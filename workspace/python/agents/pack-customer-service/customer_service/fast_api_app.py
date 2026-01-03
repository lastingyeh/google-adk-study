import os

import google.auth
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
from google.cloud import logging as google_cloud_logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, export
from vertexai import agent_engines

from customer_service.app_utils.gcs import create_bucket_if_not_exists
from customer_service.app_utils.tracing import CloudTraceLoggingSpanExporter
from customer_service.app_utils.typing import Feedback

# 獲取預設認證與專案 ID
_, project_id = google.auth.default()
# 初始化 Google Cloud 日誌客戶端
logging_client = google_cloud_logging.Client()
logger = logging_client.logger(__name__)

# 從環境變數獲取允許的來源（CORS）
allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else None
)

# 設定 GCS 儲存桶名稱，用於存放日誌
bucket_name = f"gs://{project_id}-pack-customer-service-logs"
# 如果儲存桶不存在則建立
create_bucket_if_not_exists(
    bucket_name=bucket_name, project=project_id, location="us-central1"
)

# 配置 OpenTelemetry 追蹤（Tracing）
provider = TracerProvider()
# 使用自定義的 CloudTraceLoggingSpanExporter 將追蹤資訊輸出到日誌
processor = export.BatchSpanProcessor(CloudTraceLoggingSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# 獲取代理目錄路徑
AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 代理引擎（Agent Engine）會話配置
# 使用環境變數設定代理名稱，預設為 "pack-customer-service"
agent_name = os.environ.get("AGENT_ENGINE_SESSION_NAME", "pack-customer-service")

# 檢查是否已存在同名的代理
existing_agents = list(agent_engines.list(filter=f"display_name={agent_name}"))

if existing_agents:
    # 使用現有的代理
    agent_engine = existing_agents[0]
else:
    # 如果不存在則建立新的代理
    agent_engine = agent_engines.create(display_name=agent_name)

# 定義會話服務的 URI
session_service_uri = f"agentengine://{agent_engine.resource_name}"

# 初始化 FastAPI 應用程式，使用 ADK 提供的 get_fast_api_app
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    artifact_service_uri=bucket_name,
    allow_origins=allow_origins,
    session_service_uri=session_service_uri,
)
app.title = "pack-customer-service"
app.description = "與 pack-customer-service 代理互動的 API"


@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    """收集並記錄使用者回饋。

    參數:
        feedback: 要記錄的回饋數據

    回傳:
        成功訊息
    """
    # 將回饋內容以結構化日誌形式記錄
    logger.log_struct(feedback.model_dump(), severity="INFO")
    return {"status": "success"}


# 主程式進入點
if __name__ == "__main__":
    import uvicorn

    # 啟動 Uvicorn 伺服器
    uvicorn.run(app, host="0.0.0.0", port=8000)

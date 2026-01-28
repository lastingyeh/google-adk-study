# 版權所有 2025 Google LLC
#
# 根據 Apache 許可證 2.0 版（「許可證」）授權；
# 除非遵守許可證，否則您不得使用此檔案。
# 您可以在以下網址獲得許可證副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據許可證分發的軟體
# 是按「原樣」分發的，不附帶任何形式的明示或暗示的保證或條件。
# 請參閱許可證以瞭解管理權限和限制的特定語言。

import os

import google.auth
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
from google.cloud import logging as google_cloud_logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, export

from app.utils.gcs import create_bucket_if_not_exists
from app.utils.tracing import CloudTraceLoggingSpanExporter
from app.utils.typing import Feedback

# 獲取預設的 Google Cloud 憑證與專案 ID
_, project_id = google.auth.default()
# 初始化 Google Cloud 日誌客戶端
logging_client = google_cloud_logging.Client()
logger = logging_client.logger(__name__)

# 設定允許的 CORS 來源
allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",")
    if os.getenv("ALLOW_ORIGINS")
    else None
)

# 定義並建立用於日誌和數據存儲的 GCS 儲存桶
bucket_name = f"gs://{project_id}-short-movie-agents-logs-data"
create_bucket_if_not_exists(
    bucket_name=bucket_name, project=project_id, location="europe-west4"
)

# 配置 OpenTelemetry 追蹤 (Tracing)
provider = TracerProvider()
processor = export.BatchSpanProcessor(CloudTraceLoggingSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# 獲取代理程式碼所在目錄
AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 記憶體內對話服務配置 - 不使用持久化存儲
session_service_uri = None

# 建立 FastAPI 應用程式
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True, # 啟用網頁介面
    artifact_service_uri=bucket_name, # 指定工件存儲位址
    allow_origins=allow_origins,
    session_service_uri=session_service_uri,
)
app.title = "短片生成代理 (short-movie-agents)"
app.description = "與短片生成代理互動的 API"


@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    """收集並記錄使用者回饋。

    Args:
        feedback: 要記錄的回饋數據對象

    Returns:
        成功訊息字典
    """
    logger.log_struct(feedback.model_dump(), severity="INFO")
    return {"status": "success"}


# 主執行入口
if __name__ == "__main__":
    import uvicorn

    # 啟動 Uvicorn 伺服器
    uvicorn.run(app, host="0.0.0.0", port=8000)

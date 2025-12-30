import os
from urllib.parse import quote

import google.auth
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
from google.cloud import logging as google_cloud_logging

from app.app_utils.telemetry import setup_telemetry
from app.app_utils.typing import Feedback

# 設定遙測 (Telemetry)
setup_telemetry()
# 進行 Google Cloud 預設身份驗證並取得專案 ID
_, project_id = google.auth.default()
# 初始化 Google Cloud Logging 客戶端
logging_client = google_cloud_logging.Client()
logger = logging_client.logger(__name__)
# 從環境變數讀取允許的 CORS 來源
allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else None
)

# ADK 的產物儲存桶 (由 Terraform 建立，透過環境變數傳入)
logs_bucket_name = os.environ.get("LOGS_BUCKET_NAME")

# Agent 的根目錄
AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Cloud SQL 會話設定
db_user = os.environ.get("DB_USER", "postgres")
db_name = os.environ.get("DB_NAME", "postgres")
db_pass = os.environ.get("DB_PASS")
instance_connection_name = os.environ.get("INSTANCE_CONNECTION_NAME")

session_service_uri = None
# 如果提供了 Cloud SQL 實例連線名稱和資料庫密碼
if instance_connection_name and db_pass:
    # 使用 Unix socket 連接到 Cloud SQL
    # 對使用者名稱和密碼進行 URL 編碼，以處理特殊字元 (例如：'[', '?', '#', '$')
    # 這些字元可能導致 URL 解析錯誤，特別是 '[' 會觸發 IPv6 驗證
    encoded_user = quote(db_user, safe="")
    encoded_pass = quote(db_pass, safe="")
    # 對連線名稱進行 URL 編碼，以防止冒號被誤解
    encoded_instance = instance_connection_name.replace(":", "%3A")

    # 組合 PostgreSQL 的非同步連線字串
    session_service_uri = (
        f"postgresql+asyncpg://{encoded_user}:{encoded_pass}@"
        f"/{db_name}"
        f"?host=/cloudsql/{encoded_instance}"
    )

# 設定產物儲存服務的 URI (Google Cloud Storage)
artifact_service_uri = f"gs://{logs_bucket_name}" if logs_bucket_name else None

# 使用 ADK 的輔助函式建立 FastAPI 應用程式
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,  # 啟用 Web 介面
    artifact_service_uri=artifact_service_uri,  # 設定產物儲存服務
    allow_origins=allow_origins,  # 設定允許的 CORS 來源
    session_service_uri=session_service_uri,  # 設定會話儲存服務 (對話歷史)
    otel_to_cloud=True,  # 將 OpenTelemetry 資料傳送到 Cloud Trace
)
app.title = "rag-km-agents"
app.description = "用於與 Agent rag-km-agents 互動的 API"


@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    """收集並記錄回饋。

    Args:
        feedback: 要記錄的回饋資料

    Returns:
        表示成功的訊息
    """
    logger.log_struct(feedback.model_dump(), severity="INFO")
    return {"status": "success"}


# 主程式執行入口
if __name__ == "__main__":
    import uvicorn

    # 在本機端執行 FastAPI 應用程式
    uvicorn.run(app, host="0.0.0.0", port=8000)

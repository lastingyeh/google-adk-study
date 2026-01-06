# 匯入必要的模組
import os  # 用於與作業系統互動，例如讀取環境變數
from urllib.parse import quote  # 用於 URL 編碼

import google.auth  # Google 認證函式庫
from fastapi import FastAPI  # FastAPI 框架，用於建立 API
from google.adk.cli.fast_api import (
    get_fast_api_app,
)  # 從 ADK CLI 匯入 FastAPI 應用程式產生器
from google.cloud import logging as google_cloud_logging  # Google Cloud Logging 用戶端

from policy_as_code_agent.app_utils.telemetry import setup_telemetry  # 設定遙測
from policy_as_code_agent.app_utils.typing import Feedback  # 匯入 Feedback 資料模型

# 設定遙測
setup_telemetry()
# 取得預設的 Google Cloud 憑證和專案 ID
_, project_id = google.auth.default()
# 建立 Cloud Logging 用戶端
logging_client = google_cloud_logging.Client()
# 建立一個 logger
logger = logging_client.logger(__name__)
# 從環境變數讀取允許的來源網域，用於 CORS 設定
allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else None
)

# ADK 的產物儲存桶 (由 Terraform 建立，透過環境變數傳入)
logs_bucket_name = os.environ.get("LOGS_BUCKET_NAME")

# 取得代理程式的根目錄
AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Cloud SQL session 設定
db_user = os.environ.get("DB_USER", "postgres")  # 資料庫使用者名稱
db_name = os.environ.get("DB_NAME", "postgres")  # 資料庫名稱
db_pass = os.environ.get("DB_PASS")  # 資料庫密碼
instance_connection_name = os.environ.get(
    "INSTANCE_CONNECTION_NAME"
)  # Cloud SQL 執行個體連線名稱

# 初始化 session_service_uri
session_service_uri = None
# 如果提供了 Cloud SQL 執行個體連線名稱和資料庫密碼
if instance_connection_name and db_pass:
    # 使用 Unix socket 連線 Cloud SQL
    # 對使用者名稱和密碼進行 URL 編碼，以處理特殊字元 (例如：'[', '?', '#', '$')
    # 這些字元可能會導致 URL 解析錯誤，特別是 '[' 會觸發 IPv6 驗證
    encoded_user = quote(db_user, safe="")
    encoded_pass = quote(db_pass, safe="")
    # 對連線名稱進行 URL 編碼，以防止冒號被誤解
    encoded_instance = instance_connection_name.replace(":", "%3A")

    # 建立 PostgreSQL 連線字串
    session_service_uri = (
        f"postgresql+asyncpg://{encoded_user}:{encoded_pass}@"
        f"/{db_name}"
        f"?host=/cloudsql/{encoded_instance}"
    )

# 設定產物服務 URI (Google Cloud Storage)
artifact_service_uri = f"gs://{logs_bucket_name}" if logs_bucket_name else None

# 使用 get_fast_api_app 建立 FastAPI 應用程式實例
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,  # 代理程式目錄
    web=True,  # 啟用 Web 介面
    artifact_service_uri=artifact_service_uri,  # 產物服務 URI
    allow_origins=allow_origins,  # 允許的來源網域
    session_service_uri=session_service_uri,  # session 服務 URI
    otel_to_cloud=True,  # 將 OpenTelemetry 資料傳送到 Cloud
)
# 設定應用程式標題
app.title = "pack-policy-as-code"
# 設定應用程式描述
app.description = "API for interacting with the Agent pack-policy-as-code"


# 定義一個 POST 路由來收集回饋
@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    """收集並記錄回饋。

    Args:
        feedback: 要記錄的回饋資料

    Returns:
        成功訊息
    """
    # 將回饋資料以結構化日誌的形式記錄下來
    logger.log_struct(feedback.model_dump(), severity="INFO")
    # 回傳成功狀態
    return {"status": "success"}


# 主程式執行入口
if __name__ == "__main__":
    import uvicorn  # 匯入 uvicorn，一個 ASGI 伺服器

    # 執行 FastAPI 應用程式
    uvicorn.run(app, host="0.0.0.0", port=8000)

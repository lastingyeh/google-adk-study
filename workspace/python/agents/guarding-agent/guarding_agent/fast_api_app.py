# 版權所有 2026 Google LLC
#
# 根據 Apache License 2.0 版本（「授權」）授權；
# 除非遵守授權，否則您不得使用此檔案。
# 您可以在以下網址取得授權副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據授權散佈的軟體
# 是按「原樣」散佈的，不附任何明示或暗示的保證或條件。
# 請參閱授權以了解管理授權下權限和限制的特定語言。

"""
### 翻譯內容
此檔案實作了基於 FastAPI 的 Web 伺服器，用於與 Guarding Agent 進行互動。
它整合了 Google Cloud Logging、遙測系統 (Telemetry) 以及資料庫連線 (Cloud SQL)，並透過 Google ADK 的 `get_fast_api_app` 自動生成 API 路由。

### 重點摘要
- **核心概念**：提供 AI 代理的生產級 API 介面。
- **關鍵技術**：FastAPI, Google ADK `get_fast_api_app`, Google Cloud Logging, Cloud SQL (PostgreSQL), OpenTelemetry。
- **重要結論**：透過自動化的應用程式生成工具，可以快速將 AI 代理部署為可擴展的 Web 服務，同時保有完善的日誌與監控能力。
- **行動項目**：設定環境變數（如 `DB_PASS`, `INSTANCE_CONNECTION_NAME`）以啟用完整功能。
"""

import os
from urllib.parse import quote

import google.auth
from fastapi import FastAPI
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
from google.adk.sessions import DatabaseSessionService
# from google.adk.cli.fast_api import get_fast_api_app
from google.cloud import logging as google_cloud_logging

# 匯入內部工具
from guarding_agent.app_utils.telemetry import setup_telemetry
from guarding_agent.app_utils.typing import Feedback

# 匯入 root_agent 模組以確保其在應用程式啟動時被正確載入
from .agent import adk_app

# 初始化遙測系統
setup_telemetry()

# 取得預設的 Google 認證資訊與專案 ID
_, project_id = google.auth.default()

# 初始化 Google Cloud Logging 客戶端
logging_client = google_cloud_logging.Client()
logger = logging_client.logger(__name__)

# 設定允許的 CORS 來源
allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else None
)

# ADK 的 Artifact 儲存桶名稱（透過環境變數傳遞）
logs_bucket_name = os.environ.get("LOGS_BUCKET_NAME")


# 取得代理目錄的路徑
AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Cloud SQL 會話 (Session) 設定
db_user = os.environ.get("DB_USER", "postgres")
db_name = os.environ.get("DB_NAME", "postgres")
db_pass = os.environ.get("DB_PASS")
instance_connection_name = os.environ.get("INSTANCE_CONNECTION_NAME")

session_service = None

# 建立資料庫連線字串
# session_service_uri = None
if instance_connection_name and db_pass:
    # 使用 Unix Socket 連接 Cloud SQL
    # 對使用者名稱和密碼進行 URL 編碼以處理特殊字元
    encoded_user = quote(db_user, safe="")
    encoded_pass = quote(db_pass, safe="")
    # 編碼連線名稱以防止冒號被誤解
    encoded_instance = instance_connection_name.replace(":", "%3A")

    session_service_uri = (
        f"postgresql+asyncpg://{encoded_user}:{encoded_pass}@"
        f"/{db_name}"
        f"?host=/cloudsql/{encoded_instance}"
    )
    session_service = DatabaseSessionService(db_url=session_service_uri)

# 設定 Artifact 服務 URI (Google Cloud Storage)
artifact_service_uri = f"gs://{logs_bucket_name}" if logs_bucket_name else None

adk_agent = ADKAgent.from_app(
    app=adk_app,
    user_id="default_user",
    session_service=session_service,
    use_in_memory_services=True,
    session_timeout_seconds=3600,
)

app = FastAPI(title="guarding-agent", description="與 guarding-agent 代理互動的 API")

add_adk_fastapi_endpoint(app, adk_agent, path="/")

# 使用 Google ADK 建立 FastAPI 應用程式
# app: FastAPI = get_fast_api_app(
#     agents_dir=AGENT_DIR,
#     web=True,
#     artifact_service_uri=artifact_service_uri,
#     allow_origins=allow_origins,
#     session_service_uri=session_service_uri,
#     otel_to_cloud=True,
# )


@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    """收集並記錄使用者回饋。

    參數:
        feedback: 要記錄的回饋數據

    回傳:
        成功訊息
    """
    # 將回饋資料以結構化日誌形式記錄到 Google Cloud
    logger.log_struct(feedback.model_dump(), severity="INFO")
    return {"status": "success"}


# 程式進入點
if __name__ == "__main__":
    import uvicorn

    # 啟動 Uvicorn 伺服器
    uvicorn.run(app, host="0.0.0.0", port=8000)

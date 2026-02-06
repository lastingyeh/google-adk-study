# 版權所有 2025 Google LLC
#
# 根據 Apache 許可證 2.0 版（「許可證」）授權；
# 除非遵守許可證，否則您不得使用此檔案。
# 您可以在以下網址獲得許可證副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據許可證分發的軟體
# 是按「原樣」分發的，無任何明示或暗示的保證或條件。
# 請參閱許可證以了解管理權限和許可證下的限制。

"""
### 摘要
本檔案建構了一個基於 FastAPI 的 Web 服務，用於公開 RAG 代理人的 API 介面。它整合了 Google Cloud Logging、遙測（Telemetry）、以及 Cloud SQL 會話存儲。

### 核心重點
- **核心概念**：將 RAG Agent 封裝成可對外提供服務的 API。
- **關鍵技術**：FastAPI、Google Cloud Logging、Cloud SQL (PostgreSQL)、OpenTelemetry (OTEL)。
- **重要結論**：此應用程式支援持久化會話與遙測追蹤，適合生產環境部署。
"""

import os
from urllib.parse import quote

import google.auth
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
from google.cloud import logging as google_cloud_logging

from rag.app_utils.telemetry import setup_telemetry
from rag.app_utils.typing import Feedback

# 初始化遙測追蹤
setup_telemetry()

# 初始化 Google Cloud 認證與日誌用戶端
_, project_id = google.auth.default()
logging_client = google_cloud_logging.Client()
logger = logging_client.logger(__name__)

# 設定允許的 CORS 來源
allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else None
)

# ADK 構件存儲桶（由 Terraform 建立，透過環境變數傳入）
logs_bucket_name = os.environ.get("LOGS_BUCKET_NAME")

# 獲取代理人目錄路徑
AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Cloud SQL 會話連線配置
db_user = os.environ.get("DB_USER", "postgres")
db_name = os.environ.get("DB_NAME", "postgres")
db_pass = os.environ.get("DB_PASS")
instance_connection_name = os.environ.get("INSTANCE_CONNECTION_NAME")

session_service_uri = None
if instance_connection_name and db_pass:
    # 使用 Unix Socket 連接 Cloud SQL
    # 對使用者名稱和密碼進行 URL 編碼以處理特殊字元
    encoded_user = quote(db_user, safe="")
    encoded_pass = quote(db_pass, safe="")
    # 對連線名稱進行編碼，防止冒號被誤解
    encoded_instance = instance_connection_name.replace(":", "%3A")

    # 構建 PostgreSQL 非同步連線字串
    session_service_uri = (
        f"postgresql+asyncpg://{encoded_user}:{encoded_pass}@"
        f"/{db_name}"
        f"?host=/cloudsql/{encoded_instance}"
    )

# 構建構件服務 URI (GCS)
artifact_service_uri = f"gs://{logs_bucket_name}" if logs_bucket_name else None

# 建立 FastAPI 應用程式實例，整合 ADK 功能
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    artifact_service_uri=artifact_service_uri,
    allow_origins=allow_origins,
    session_service_uri=session_service_uri,
    otel_to_cloud=True,  # 將 OpenTelemetry 資料發送到 Google Cloud
)
app.title = "pack-rag"
app.description = "與 pack-rag 代理人互動的 API"


@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    """收集並記錄使用者回饋。

    參數:
        feedback: 要記錄的回饋資料內容

    傳回:
        成功狀態訊息
    """
    # 將回饋資料以結構化日誌形式記錄到 Google Cloud Logging
    logger.log_struct(feedback.model_dump(), severity="INFO")
    return {"status": "success"}


# 程式進入點
if __name__ == "__main__":
    import uvicorn

    # 啟動 Uvicorn 伺服器
    uvicorn.run(app, host="0.0.0.0", port=8000)

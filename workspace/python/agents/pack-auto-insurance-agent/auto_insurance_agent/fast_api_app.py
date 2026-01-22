# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
汽車保險代理人 FastAPI 應用程式
本程式負責初始化並執行基於 Google ADK 的 FastAPI 應用程式，
提供代理人互動接口與回饋收集功能。
"""


## 重點摘要

# - **核心概念**：
#   - 建立一個整合 Google ADK (Agent Development Kit) 的 FastAPI 應用程式，專門用於處理汽車保險代理人服務。
#   - 透過標準化的 API 接口提供代理人互動、回饋收集與背景服務。

# - **關鍵技術**：
#   - **FastAPI**: 用於建立高效能的 Web API。
#   - **Google ADK**: 核心代理人開發框架，簡化代理人管理與部署。
#   - **Google Cloud Logging**: 整合雲端日誌服務，記錄結構化回饋資料。
#   - **Cloud SQL (PostgreSQL)**: 使用異步驅動 `asyncpg` 進行資料庫操作，支援 Unix socket 連線。
#   - **OpenTelemetry (OTEL)**: 整合分散式追蹤與遙測，並將數據傳送至雲端。

# - **重要結論**：
#   - 程式碼展示了生產環境中處理資料庫安全連線（如 URL 編碼）與雲端資源整合的最佳實踐。
#   - 透過 `get_fast_api_app` 函數，可以快速將開發好的代理人邏輯封裝成 Web 服務。

# - **行動項目**：
#   - 部署前需確保環境變數 `INSTANCE_CONNECTION_NAME`、`DB_PASS` 與 `LOGS_BUCKET_NAME` 已正確配置。
#   - 檢查 GCP 服務帳戶是否具備存取 Cloud SQL、Logging 與 Storage 的權限。

import os
from urllib.parse import quote

import google.auth
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
from google.cloud import logging as google_cloud_logging

from auto_insurance_agent.app_utils.telemetry import setup_telemetry
from auto_insurance_agent.app_utils.typing import Feedback

# 1. 初始化遙測 (Telemetry) 設定
setup_telemetry()

# 2. 取得 Google Cloud 認證與專案 ID
_, project_id = google.auth.default()

# 3. 初始化 Google Cloud Logging 客戶端
logging_client = google_cloud_logging.Client()
logger = logging_client.logger(__name__)

# 4. 解析跨來源資源共用 (CORS) 的允許來源
allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else None
)

# 5. 取得 ADK 的構件桶 (Artifact bucket) 名稱（由 Terraform 建立並透過環境變數傳遞）
logs_bucket_name = os.environ.get("LOGS_BUCKET_NAME")

# 6. 定義代理人根目錄
AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 7. Cloud SQL 會話 (Session) 配置
db_user = os.environ.get("DB_USER", "postgres")
db_name = os.environ.get("DB_NAME", "postgres")
db_pass = os.environ.get("DB_PASS")
instance_connection_name = os.environ.get("INSTANCE_CONNECTION_NAME")

session_service_uri = None
# 如果提供了執行個體連線名稱與密碼，則配置 PostgreSQL 連線字串
if instance_connection_name and db_pass:
    # 針對 Cloud SQL 使用 Unix socket
    # 對使用者名稱和密碼進行 URL 編碼，以處理特殊字元（例如 '[', '?', '#', '$'）
    # 這些字元可能會導致 URL 解析錯誤，特別是 '[' 會觸發 IPv6 驗證
    encoded_user = quote(db_user, safe="")
    encoded_pass = quote(db_pass, safe="")
    # 對連線名稱進行編碼，防止冒號被誤解
    encoded_instance = instance_connection_name.replace(":", "%3A")

    # 建構異步 PostgreSQL 連線 URI
    session_service_uri = (
        f"postgresql+asyncpg://{encoded_user}:{encoded_pass}@"
        f"/{db_name}"
        f"?host=/cloudsql/{encoded_instance}"
    )

# 8. 設定構件服務 URI (Google Cloud Storage)
artifact_service_uri = f"gs://{logs_bucket_name}" if logs_bucket_name else None

# 9. 建立並配置 FastAPI 應用程式執行個體
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    artifact_service_uri=artifact_service_uri,
    allow_origins=allow_origins,
    session_service_uri=session_service_uri,
    otel_to_cloud=True,
)
app.title = "pack-auto-insurance-agent"
app.description = "API for interacting with the Agent pack-auto-insurance-agent"


@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    """收集並記錄意見回饋。

    參數:
        feedback: 要記錄的回饋資料 (Feedback 類型)

    回傳:
        成功訊息 (dict)
    """
    # 將回饋資料轉換為模型字典並記錄至 Google Cloud Logging
    logger.log_struct(feedback.model_dump(), severity="INFO")
    return {"status": "success"}


# 10. 主程式執行入口
if __name__ == "__main__":
    import uvicorn

    # 啟動 Uvicorn 伺服器，監聽 0.0.0.0:8000
    uvicorn.run(app, host="0.0.0.0", port=8000)

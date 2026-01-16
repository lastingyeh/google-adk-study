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

import os

import google.auth
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
from google.cloud import logging as google_cloud_logging

from app.app_utils.telemetry import setup_telemetry
from app.app_utils.typing import Feedback

# 設定遙測 (Telemetry)
setup_telemetry()

# 取得預設的 Google Cloud 專案 ID
_, project_id = google.auth.default()

# 初始化 Google Cloud 記錄客戶端
logging_client = google_cloud_logging.Client()
logger = logging_client.logger(__name__)

# 設定允許的來源 (CORS)
allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else None
)

# ADK 的產出物存儲桶 (由 Terraform 建立，透過環境變數傳遞)
logs_bucket_name = os.environ.get("LOGS_BUCKET_NAME")

# 代理程式目錄路徑
AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 記憶體內工作階段設定 - 無持久存儲
session_service_uri = None

# 產出物服務 URI (GCS 存儲桶)
artifact_service_uri = f"gs://{logs_bucket_name}" if logs_bucket_name else None

# 初始化 FastAPI 應用程式
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    artifact_service_uri=artifact_service_uri,
    allow_origins=allow_origins,
    session_service_uri=session_service_uri,
    otel_to_cloud=True,
)
app.title = "pack-deep-search"
app.description = "與代理程式 pack-deep-search 互動的 API"


@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    """收集並記錄回饋。

    參數:
        feedback: 要記錄的回饋資料

    傳回:
        成功訊息
    """
    # 將回饋記錄為結構化日誌
    logger.log_struct(feedback.model_dump(), severity="INFO")
    return {"status": "success"}


# 主執行進入點
if __name__ == "__main__":
    import uvicorn

    # 啟動 uvicorn 伺服器
    uvicorn.run(app, host="0.0.0.0", port=8000)
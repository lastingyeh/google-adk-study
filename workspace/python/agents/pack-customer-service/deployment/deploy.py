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
Agent 部署指令碼
本程式使用 Vertex AI Agent Engine 將 Google ADK 開發的 Agent 部署到雲端。
"""

import argparse
import logging
import sys

import vertexai
from customer_service.agent import root_agent
from customer_service.config import Config
from google.api_core.exceptions import NotFound
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

# 設定日誌層級為 DEBUG 以便觀察部署過程
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

configs = Config()

# 定義預備存儲桶 (Staging Bucket)，用於上傳部署所需的程式碼與相依套件
STAGING_BUCKET = f"gs://{configs.CLOUD_PROJECT}-adk-customer-service-staging"

# 指定 Agent 的打包檔案 (.whl)
AGENT_WHL_FILE = "./customer_service-0.1.0-py3-none-any.whl"

# 初始化 Vertex AI 環境
vertexai.init(
    project=configs.CLOUD_PROJECT,
    location=configs.CLOUD_LOCATION,
    staging_bucket=STAGING_BUCKET,
)

parser = argparse.ArgumentParser(description="Agent 部署與管理工具")

# --- 參數設定重點說明 ---
# --delete: 若指定此參數，則會執行刪除已部署 Agent 的操作。
parser.add_argument(
    "--delete",
    action="store_true",
    dest="delete",
    required=False,
    help="刪除已部署的 Agent",
)
# --resource_id: 刪除操作時必須提供的資源 ID。
parser.add_argument(
    "--resource_id",
    required="--delete" in sys.argv,
    action="store",
    dest="resource_id",
    help="要刪除的 Agent 資源 ID，格式：projects/PROJECT_ID/locations/LOCATION/reasoningEngines/REASONING_ENGINE_ID",
)


args = parser.parse_args()

if args.delete:
    # --- 刪除邏輯 ---
    try:
        agent_engines.get(resource_name=args.resource_id)
        agent_engines.delete(resource_name=args.resource_id)
        print(f"Agent {args.resource_id} 已成功刪除")
    except NotFound as e:
        print(e)
        print(f"找不到 Agent 資源： {args.resource_id}")

else:
    # --- 部署邏輯 ---
    logger.info("正在準備部署應用程式...")

    # 使用 AdkApp 封裝 root_agent，以便在 Vertex AI Reasoning Engine 上執行
    app = AdkApp(agent=root_agent, enable_tracing=False)

    logging.debug("正在將 Agent 部署至 Agent Engine:")
    # agent_engines.create 會處理套件上傳、環境構建與 API 端點建立
    remote_app = agent_engines.create(
        app,
        requirements=[
            AGENT_WHL_FILE,
        ],
        extra_packages=[AGENT_WHL_FILE],
    )

    # --- 驗證部署 ---
    logging.debug("正在測試部署結果：")
    # 建立一個測試 Session 並發送問候語，確保雲端端點運作正常
    session = remote_app.create_session(user_id="123")
    for event in remote_app.stream_query(
        user_id="123",
        session_id=session["id"],
        message="hello!",
    ):
        if event.get("content", None):
            print(
                f"Agent 部署成功！資源名稱為： {remote_app.resource_name}"
            )

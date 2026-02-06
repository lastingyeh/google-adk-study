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

import logging
import os

import vertexai
from dotenv import set_key
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

from rag.agent import root_agent

# 設定日誌記錄層級為 DEBUG
# Set logging level to DEBUG
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 從環境變數中讀取 Google Cloud 專案設定
# Read Google Cloud project settings from environment variables
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
STAGING_BUCKET = os.getenv("STAGING_BUCKET")
# 定義相對於此腳本的 .env 檔案路徑
# Define the path to the .env file relative to this script
ENV_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))

# 初始化 Vertex AI SDK
# Initialize Vertex AI SDK
vertexai.init(
    project=GOOGLE_CLOUD_PROJECT,
    location=GOOGLE_CLOUD_LOCATION,
    staging_bucket=STAGING_BUCKET,
)


# 更新 .env 檔案的函式
# Function to update the .env file
def update_env_file(agent_engine_id, env_file_path):
    """
    更新 .env 檔案中的 Agent Engine ID。
    Updates the .env file with the agent engine ID.
    """
    try:
        # 使用 dotenv 更新環境變數檔案
        # Update environment variable file using dotenv
        set_key(env_file_path, "AGENT_ENGINE_ID", agent_engine_id)
        print(f"Updated AGENT_ENGINE_ID in {env_file_path} to {agent_engine_id}")
    except Exception as e:
        print(f"Error updating .env file: {e}")


logger.info("deploying app...")
# 建立 AdkApp 實例，啟用追蹤
# Create AdkApp instance, enable tracing
app = AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

logging.debug("deploying agent to agent engine:")

# 部署 Agent 到 Vertex AI Agent Engine
# Deploy Agent to Vertex AI Agent Engine
remote_app = agent_engines.create(
    app,  # type: ignore[arg-type]
    requirements=[
        "google-cloud-aiplatform[adk,agent-engines]==1.108.0",
        "google-adk==1.10.0",
        "python-dotenv",
        "google-auth",
        "tqdm",
        "requests",
        "llama-index",
    ],
    extra_packages=[
        "./rag",
    ],
)

# 記錄部署成功的 remote_app 資訊
# log remote_app
logging.info(
    f"Deployed agent to Vertex AI Agent Engine successfully, resource name: {remote_app.resource_name}"
)

# 使用新的 Agent Engine ID 更新 .env 檔案
# Update the .env file with the new Agent Engine ID
update_env_file(remote_app.resource_name, ENV_FILE_PATH)

"""
## 重點摘要

- **核心概念**：自動化部署 Agent 至 Vertex AI Agent Engine
- **關鍵技術**：Vertex AI SDK, Agent Engine, python-dotenv
- **重要結論**：此腳本負責初始化 Vertex AI 環境，將定義好的 `root_agent` 應用程式封裝並部署至雲端，最後將生成的 Agent Engine ID 回寫至 `.env` 設定檔以便後續使用。
- **行動項目**：執行此腳本以進行部署。
"""

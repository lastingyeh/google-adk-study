# Copyright 2025 Google LLC
#
# 根據 Apache License 2.0 版本（「本授權」）授權；
# 除非遵守本授權，否則您不得使用此檔案。
# 您可以在以下網址獲得本授權的副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據本授權分發的軟體
# 是按「現狀」基礎分發的，無任何明示或暗示的保證或條件。
# 請參閱本授權以了解管理權限和限制的特定語言。


"""
## 重點摘要
- **核心概念**：自動化部署 Agent 到 Vertex AI Agent Engine。
- **關鍵技術**：Vertex AI, Python, AdkApp, Agent Engine。
- **重要結論**：腳本會自動建立雲端資源並將資源 ID 回填至本地環境變數檔案。
- **行動項目**：執行此腳本前需確保已設定正確的 GCP 環境變數。
"""

import logging
import os
import sys

import vertexai
from dotenv import load_dotenv, set_key
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

from auto_insurance_agent.agent import root_agent

# 將專案根目錄添加到 sys.path，以便導入自定義模組
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 載入 .env 檔案中的環境變數
load_dotenv()

# 設定日誌記錄
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 從環境變數獲取 GCP 相關配置
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
STAGING_BUCKET = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")

# .env 檔案的路徑
ENV_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))

# 初始化 Vertex AI SDK
vertexai.init(
    project=GOOGLE_CLOUD_PROJECT,
    location=GOOGLE_CLOUD_LOCATION,
    staging_bucket=STAGING_BUCKET,
)


# 更新 .env 檔案的函式
def update_env_file(agent_engine_id, env_file_path):
    """使用代理引擎 ID (Agent Engine ID) 更新 .env 檔案。"""
    try:
        set_key(env_file_path, "AGENT_ENGINE_ID", agent_engine_id)
        print(f"已更新 {env_file_path} 中的 AGENT_ENGINE_ID 為 {agent_engine_id}")
    except Exception as e:
        print(f"更新 .env 檔案時發生錯誤: {e}")


logger.info("正在部署應用程式...")

# 建立 AdkApp 實例，包裝 root_agent
app = AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

logging.debug("正在將代理部署到代理引擎：")

# 在 Vertex AI Agent Engine 上建立遠端代理
remote_app = agent_engines.create(
    app,
    display_name="auto_insurance_agent",
    requirements=[
        "google-cloud-aiplatform[adk,agent-engines]>=1.100.0,<2.0.0",
        "google-adk>=1.5.0,<2.0.0",
        "python-dotenv",
        "google-cloud-secret-manager",
    ],
    extra_packages=[
        "./auto_insurance_agent",
    ],
)

# 記錄部署成功的訊息與資源名稱
logging.info(
    f"成功將代理部署到 Vertex AI Agent Engine，資源名稱: {remote_app.resource_name}"
)

# 使用新的代理引擎 ID 更新 .env 檔案
update_env_file(remote_app.resource_name, ENV_FILE_PATH)

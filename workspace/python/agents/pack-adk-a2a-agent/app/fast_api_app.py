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
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import google.auth
from a2a.server.apps import A2AFastAPIApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard
from a2a.utils.constants import (
    AGENT_CARD_WELL_KNOWN_PATH,
    EXTENDED_AGENT_CARD_PATH,
)
from fastapi import FastAPI
from google.adk.a2a.executor.a2a_agent_executor import A2aAgentExecutor
from google.adk.a2a.utils.agent_card_builder import AgentCardBuilder
from google.adk.artifacts import GcsArtifactService, InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.cloud import logging as google_cloud_logging

from app.agent import app as adk_app
from app.app_utils.telemetry import setup_telemetry
from app.app_utils.typing import Feedback

# 初始化遙測 (Telemetry)
setup_telemetry()
# 自動獲取 Google Cloud 的預設憑證和專案 ID
_, project_id = google.auth.default()
# 初始化 Google Cloud Logging 客戶端
logging_client = google_cloud_logging.Client()
# 為此模組建立一個專用的 logger
logger = logging_client.logger(__name__)

# 從環境變數讀取 ADK 的 Artifact bucket 名稱 (通常由 Terraform 建立)
logs_bucket_name = os.environ.get("LOGS_BUCKET_NAME")
# 根據是否存在 bucket 名稱，決定使用 GCS 或記憶體作為 Artifact 儲存服務
# 若在雲端環境，使用 GcsArtifactService 將產物 (如日誌) 存到 GCS
# 若在本地開發，則使用 InMemoryArtifactService，產物僅存於記憶體中
artifact_service = (
    GcsArtifactService(bucket_name=logs_bucket_name)
    if logs_bucket_name
    else InMemoryArtifactService()
)

# 建立 ADK Runner，這是執行 Agent 核心邏輯的引擎
runner = Runner(
    app=adk_app,  # 核心 Agent 應用程式
    artifact_service=artifact_service,  # 指定產物儲存服務
    session_service=InMemorySessionService(),  # 使用記憶體來管理對話 Session，服務重啟後 Session 會遺失
)

# 建立 A2A (Agent-to-Agent) 請求處理器
request_handler = DefaultRequestHandler(
    # 使用 A2A Agent 執行器，它將 A2A 請求轉發給 ADK Runner
    agent_executor=A2aAgentExecutor(runner=runner),
    # 使用記憶體來管理非同步任務
    task_store=InMemoryTaskStore(),
)

# 定義此 Agent 的 A2A RPC (遠端程序呼叫) 路由路徑
A2A_RPC_PATH = f"/a2a/{adk_app.name}"


async def build_dynamic_agent_card() -> AgentCard:
    """從 root_agent 動態建立代理程式卡片 (Agent Card)。

    Agent Card 如同代理程式的名片，定義了其能力、如何與之通訊等資訊。
    動態建立是為了在不同環境（如本地、雲端）中能正確設定 RPC 的 URL。
    """
    agent_card_builder = AgentCardBuilder(
        agent=adk_app.root_agent,  # 從 ADK 應用程式取得根代理程式的定義
        capabilities=AgentCapabilities(streaming=True),  # 宣告此代理程式支援串流回應
        # 從環境變數取得應用程式的公開 URL，並組合出完整的 RPC 路徑
        rpc_url=f"{os.getenv('APP_URL', 'http://0.0.0.0:8000')}{A2A_RPC_PATH}",
        agent_version=os.getenv("AGENT_VERSION", "0.1.0"),  # 設定代理程式版本
    )
    agent_card = await agent_card_builder.build()
    return agent_card


@asynccontextmanager
async def lifespan(app_instance: FastAPI) -> AsyncIterator[None]:
    """FastAPI 的生命週期管理器，在應用程式啟動和關閉時執行。"""
    # 在應用程式啟動時，動態建立 Agent Card
    agent_card = await build_dynamic_agent_card()
    # 建立 A2A FastAPI 應用程式實例，並傳入 Agent Card 和請求處理器
    a2a_app = A2AFastAPIApplication(agent_card=agent_card, http_handler=request_handler)
    # 將 A2A 所需的路由 (如 Agent Card 的 well-known 路徑、RPC 端點) 新增到主 FastAPI 應用程式中
    a2a_app.add_routes_to_app(
        app_instance,
        agent_card_url=f"{A2A_RPC_PATH}{AGENT_CARD_WELL_KNOWN_PATH}",
        rpc_url=A2A_RPC_PATH,
        extended_agent_card_url=f"{A2A_RPC_PATH}{EXTENDED_AGENT_CARD_PATH}",
    )
    # lifespan 函式在此暫停，直到應用程式準備關閉
    yield
    # 應用程式關閉時可以在此處執行清理程式碼 (此處無)


# 建立 FastAPI 主應用程式實例
app = FastAPI(
    title="pack-adk-a2a-agent",
    description="用於與 Agent pack-adk-a2a-agent 互動的 API",
    lifespan=lifespan,  # 註冊生命週期管理器
)


@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    """收集並記錄使用者回饋。

    Args:
        feedback: 要記錄的回饋資料 (Pydantic 模型)

    Returns:
        一個表示成功的字典
    """
    # 將回饋資料轉換為字典格式，並透過 Google Cloud Logging 記錄下來
    logger.log_struct(feedback.model_dump(), severity="INFO")
    return {"status": "success"}


# 如果此檔案作為主程式執行
if __name__ == "__main__":
    import uvicorn

    # 啟動 uvicorn 伺服器來運行 FastAPI 應用程式
    uvicorn.run(app, host="0.0.0.0", port=8000)

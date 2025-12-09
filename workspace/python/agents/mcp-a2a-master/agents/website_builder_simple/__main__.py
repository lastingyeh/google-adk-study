"""
重點摘要:
- **核心概念**: Website Builder Simple Agent 的啟動腳本。
- **關鍵技術**: `uvicorn` (ASGI Server), `click` (CLI), `A2A Framework`。
- **重要結論**: 設定並啟動網站建構代理伺服器。
- **行動項目**: 透過 `python -m agents.website_builder_simple` 執行此腳本。
"""

import uvicorn

from a2a.types import AgentSkill, AgentCard, AgentCapabilities
import click
from a2a.server.request_handlers import DefaultRequestHandler

from agents.website_builder_simple.agent_executor import (
    WebsiteBuilderSimpleAgentExecutor,
)
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.apps import A2AStarletteApplication


@click.command()
@click.option("--host", default="localhost", help="Host for the agent server")
@click.option("--port", default=10000, help="Port for the agent server")
def main(host: str, port: int):
    """
    建立並執行網站建構代理的主函式。
    Main function to create and run the website builder agent.

    執行流程：
    1. 定義 Agent 技能 (Skill) - 描述 Agent 的能力範圍
    2. 建立 Agent 卡片 (AgentCard) - Agent 的識別和能力聲明
    3. 初始化請求處理器 (RequestHandler) - 處理來自客戶端的請求
    4. 啟動 A2A 伺服器 - 透過 ASGI/Uvicorn 提供 HTTP 服務

    技術要點：
    - 使用 Click 提供 CLI 介面，支援動態配置 host/port
    - 遵循 A2A Protocol，提供標準化的 Agent 介面
    - 支援串流回應 (streaming=True)，提升用戶體驗
    - 使用 InMemoryTaskStore 儲存任務狀態（適合單機部署）
    """
    # ========== 步驟 1: 定義 Agent 技能 ==========
    # AgentSkill 描述了這個 Agent 具體能做什麼
    # 其他 Agent 或客戶端可透過 skill 判斷是否適合委派任務
    skill = AgentSkill(
        id="website_builder_simple_skill",  # 唯一識別碼
        name="website_builder_simple_skill",  # 技能名稱
        description="一個簡易的網站建構代理，可以建立基本的網頁。",
        tags=["website", "builder", "html", "css", "javascript"],  # 標籤用於搜尋和分類
        examples=[  # 範例幫助用戶理解 Agent 的使用方式
            """建立一個包含頁首和頁尾的簡單網頁。""",
            """為產品建立一個帶有行動呼籲按鈕的登陸頁面。""",
        ],
    )

    # ========== 步驟 2: 建立 Agent 卡片 ==========
    # AgentCard 是 Agent 的「名片」，包含所有必要的元資料
    # 會自動暴露在 /.well-known/agent.json 端點，供其他 Agent 發現
    agent_card = AgentCard(
        name="website_builder_simple",
        description="一個簡易的網站建構代理，可以建立基本的網頁，並使用 Google 的代理開發框架構建。",
        url=f"http://{host}:{port}/",  # Agent 的公開 URL（用於 Agent-to-Agent 通訊）
        version="1.0.0",  # 版本號（遵循語意化版本）
        defaultInputModes=["text"],  # 支援的輸入模式（文字、圖片、音訊等）
        defaultOutputModes=["text"],  # 支援的輸出模式
        skills=[skill],  # 此 Agent 提供的技能列表
        capabilities=AgentCapabilities(streaming=True),  # 支援串流回應（SSE）
    )

    # ========== 步驟 3: 初始化請求處理器 ==========
    # DefaultRequestHandler 負責：
    # 1. 接收來自客戶端的 HTTP 請求
    # 2. 調用 AgentExecutor 執行任務
    # 3. 管理任務狀態（透過 TaskStore）
    # 4. 回傳回應給客戶端
    request_handler = DefaultRequestHandler(
        agent_executor=WebsiteBuilderSimpleAgentExecutor(),  # 實際執行業務邏輯的執行器
        task_store=InMemoryTaskStore(),  # 任務狀態儲存（記憶體中，重啟會遺失）
    )

    # ========== 步驟 4: 建立 ASGI 應用 ==========
    # A2AStarletteApplication 是基於 Starlette 的 ASGI 應用
    # 自動註冊以下端點：
    # - GET  /.well-known/agent.json  (Agent 發現)
    # - POST /tasks                    (建立任務)
    # - GET  /tasks/{task_id}          (查詢任務狀態)
    # - POST /tasks/{task_id}/cancel   (取消任務)
    server = A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )

    # ========== 步驟 5: 啟動 Uvicorn 伺服器 ==========
    # Uvicorn 是高效能的 ASGI 伺服器（基於 uvloop）
    # 支援：
    # - 非同步 I/O（asyncio）
    # - WebSocket
    # - Server-Sent Events (SSE)
    uvicorn.run(server.build(), host=host, port=port)


if __name__ == "__main__":
    main()

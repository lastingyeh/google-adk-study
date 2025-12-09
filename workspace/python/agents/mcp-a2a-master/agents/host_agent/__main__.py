"""
重點摘要:
- **核心概念**: Host Agent 的啟動腳本。
- **關鍵技術**: `uvicorn` (ASGI Server), `asyncclick` (CLI), `A2A Framework`。
- **重要結論**: 設定並啟動 Host Agent 伺服器，使其能夠被發現並處理請求。
- **行動項目**: 透過 `python -m agents.host_agent` 執行此腳本。
"""

import asyncio
import uvicorn

from a2a.types import AgentSkill, AgentCard, AgentCapabilities
import asyncclick as click
from a2a.server.request_handlers import DefaultRequestHandler

from agents.host_agent.agent_executor import HostAgentExecutor
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.apps import A2AStarletteApplication


@click.command()
@click.option("--host", default="localhost", help="Host for the agent server")
@click.option("--port", default=10001, help="Port for the agent server")
async def main(host: str, port: int):
    """
    建立並執行主機代理 (Host Agent) 的主函式。
    """
    skill = AgentSkill(
        id="host_agent_skill",
        name="host_agent_skill",
        description="一個簡單的協調者，用於使用 A2A 代理和 MCP 工具來編排任務",
        tags=["host", "orchestrator"],
        examples=[
            """使用其他代理/工具建立一個包含頁首和頁尾的簡單網頁。""",
        ],
    )

    agent_card = AgentCard(
        name="host_agent",
        description="一個簡單的協調者，用於編排任務",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        capabilities=AgentCapabilities(streaming=True),
    )

    # 建立代理執行器 (Create agent executor)
    agent_executor = HostAgentExecutor()
    await agent_executor.create()

    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor, task_store=InMemoryTaskStore()
    )

    server = A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )

    # 修正: 使用 uvicorn.Config 和 Server 代替 uvicorn.run() 以避免
    # "asyncio.run() cannot be called from a running event loop" 錯誤
    config = uvicorn.Config(server.build(), host=host, port=port)
    server_instance = uvicorn.Server(config)

    await server_instance.serve()


if __name__ == "__main__":
    asyncio.run(main())

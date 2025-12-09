"""
重點摘要:
- **核心概念**: 互動式 CLI 客戶端。
- **關鍵技術**: `asyncclick` (CLI), `httpx` (HTTP Client), A2A SDK (`A2ACardResolver`, `AgentConnector`)。
- **重要結論**: 實作了一個 REPL (Read-Eval-Print Loop) 介面來與 Agent 進行持續對話。
"""

import asyncio
from uuid import uuid4
from a2a.client import A2ACardResolver
from a2a.types import (
    AgentCard,
)
import asyncclick as click
import httpx

from utilities.a2a.agent_connect import AgentConnector


@click.command()
@click.option(
    "--agent",
    default="http://127.0.0.1:10001",
    help="A2A 代理伺服器的基本 URL (Base URL of the A2A agent server)",
)
@click.option(
    "--session",
    default=0,
    help="工作階段 ID (使用 0 產生新的) (Session ID (use 0 to generate a new one))",
)
async def cli(agent: str, session: str):
    """
    使用 A2A 客戶端傳送使用者訊息至 A2A 代理並顯示回應的 CLI。
    """

    # 如果 session 為 0，則生成新的 UUID，否則使用提供的 session
    session_id = uuid4().hex if str(session) == "0" else session

    while True:
        prompt = await click.prompt(
            "\n您想傳送什麼給代理？輸入 ':q' 或 'quit' 離開 (What do you want to send to the agent. Type ':q' or 'quit' to exit)"
        )

        if prompt.strip().lower() in ["quit", ":q"]:
            break

        card: AgentCard = None

        async with httpx.AsyncClient(timeout=300.0) as httpx_client:
            resolver = A2ACardResolver(
                base_url=agent.rstrip("/"), httpx_client=httpx_client
            )

            card = await resolver.get_agent_card()

        connector = AgentConnector(card)

        response = await connector.send_task(message=prompt, session_id=session_id)
        print("\n代理回應 (Agent says):", response)


if __name__ == "__main__":
    asyncio.run(cli())

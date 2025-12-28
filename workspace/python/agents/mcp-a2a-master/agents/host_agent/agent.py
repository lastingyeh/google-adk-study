"""
重點摘要:
- **核心概念**: HostAgent 類別實作。
- **關鍵技術**: Google ADK (`LlmAgent`, `Runner`), MCP Connector, A2A Discovery。
- **重要結論**: 整合了工具發現、任務委派和 LLM 處理邏輯，是系統的核心智慧部分。
"""

from collections.abc import AsyncIterable
import json
from typing import Any
from uuid import uuid4
from utilities.a2a.agent_connect import AgentConnector
from utilities.a2a.agent_discovery import AgentDiscovery
from utilities.common.file_loader import load_instructions_file
from google.adk.agents import LlmAgent
from google.adk import Runner

from google.adk.artifacts import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.tools.function_tool import FunctionTool

from google.genai import types
from rich import print as rprint
from rich.syntax import Syntax

from utilities.mcp.mcp_connect import MCPConnector

from a2a.types import AgentCard

from dotenv import load_dotenv

load_dotenv()


class HostAgent:
    """
    協調者代理 (Orchestrator agent)
    - 透過代理發現機制尋找 A2A 代理 (Discover A2A agents via agent discovery)
    - 透過 MCP 連接器發現 MCP 伺服器並載入 MCP 工具 (Discover the MCP servers via MCP connectors and load the MCP tools)
    - 透過選擇正確的代理/工具來路由使用者查詢 (Routes the user query by picking the correct agent/tool)
    """

    def __init__(self):
        self.system_instruction = load_instructions_file(
            "agents/host_agent/instructions.txt"
        )
        self.description = load_instructions_file("agents/host_agent/description.txt")

        self.MCPConnector = MCPConnector()
        self.AgentDiscovery = AgentDiscovery()

        self._agent = None
        self._user_id = "host_agent_user"
        self._runner = None

    async def create(self):
        self._agent = await self._build_agent()
        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

    async def _list_agents(self) -> list[dict]:
        """
        A2A 工具：回傳已註冊的 A2A 子代理的代理卡片物件字典列表。
        A2A tool: returns the list of dictionaries with agent card
        objects of registered A2A child agents

        Returns:
            list[dict]: 代理卡片物件字典列表 (List of agent card object dictionaries)
        """
        cards = await self.AgentDiscovery.list_agent_cards()

        return [card.model_dump(exclude_none=True) for card in cards]

    async def _delegate_task(self, agent_name: str, message: str) -> str:
        """
        將任務委派給指定的代理。
        Delegate task to the specified agent.
        """
        cards = await self.AgentDiscovery.list_agent_cards()

        matched_card = None
        for card in cards:
            if card.name.lower() == agent_name.lower():
                matched_card = card
            elif getattr(card, "id", "").lower() == agent_name.lower():
                matched_card = card

        if matched_card is None:
            return "找不到代理 (Agent not found)"

        connector = AgentConnector(agent_card=matched_card)

        return await connector.send_task(message=message, session_id=str(uuid4()))

    async def _build_agent(self) -> LlmAgent:
        """
        建構並設定 LlmAgent。
        Build and configure the LlmAgent.
        """
        mcp_tools = await self.MCPConnector.get_tools()

        return LlmAgent(
            name="host_agent",
            model="gemini-2.5-flash",
            instruction=self.system_instruction,
            description=self.description,
            tools=[
                FunctionTool(self._delegate_task),
                FunctionTool(self._list_agents),
                *mcp_tools,
            ],
        )

    async def invoke(self, query: str, session_id: str) -> AsyncIterable[dict]:
        """
        調用代理。
        隨著代理處理查詢，回傳更新串流給呼叫者。
        Invoke the agent.
        Return a stream of updates back to the caller as the agent processes the query.

        {
            'is_task_complete': bool,  # 指示任務是否完成 (Indicates if the task is complete)
            'updates': str,  # 任務進度更新 (Updates on the task progress)
            'content': str  # 如果完成，任務的最終結果 (Final result of the task if complete)
        }

        """

        session = await self._runner.session_service.get_session(
            app_name=self._agent.name,
            session_id=session_id,
            user_id=self._user_id,
        )

        if not session:
            session = await self._runner.session_service.create_session(
                app_name=self._agent.name,
                session_id=session_id,
                user_id=self._user_id,
            )

        user_content = types.Content(
            role="user", parts=[types.Part.from_text(text=query)]
        )

        async for event in self._runner.run_async(
            user_id=self._user_id, session_id=session_id, new_message=user_content
        ):
            print_json_response(event, "================ NEW EVENT ================")

            print(f"is_final_response: {event.is_final_response()}")

            if event.is_final_response():

                final_response = ""
                if (
                    event.content
                    and event.content.parts
                    and event.content.parts[-1].text
                ):
                    final_response = event.content.parts[-1].text

                yield {"is_task_complete": True, "content": final_response}
            else:
                yield {
                    "is_task_complete": False,
                    "updates": "代理正在處理您的請求... (Agent is processing your request...)",
                }


def print_json_response(response: Any, title: str) -> None:
    # 顯示回應的格式化和顏色高亮視圖
    # Displays a formatted and color-highlighted view of the response
    print(f"\n=== {title} ===")  # 章節標題以便清晰 (Section title for clarity)
    try:
        if hasattr(
            response, "root"
        ):  # 檢查回應是否被 SDK 包裝 (Check if response is wrapped by SDK)
            data = response.root.model_dump(mode="json", exclude_none=True)
        else:
            data = response.model_dump(mode="json", exclude_none=True)

        json_str = json.dumps(
            data, indent=2, ensure_ascii=False
        )  # 將 dict 轉換為漂亮的 JSON 字串 (Convert dict to pretty JSON string)
        syntax = Syntax(
            json_str, "json", theme="monokai", line_numbers=False
        )  # 應用語法高亮 (Apply syntax highlighting)
        rprint(syntax)  # 帶顏色列印 (Print it with color)
    except Exception as e:
        # 如果失敗則列印後備文字 (Print fallback text if something fails)
        rprint(f"[red bold]Error printing JSON:[/red bold] {e}")
        rprint(repr(response))

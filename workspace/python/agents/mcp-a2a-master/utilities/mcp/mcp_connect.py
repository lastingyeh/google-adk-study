"""
重點摘要:
- **核心概念**: MCP 連接器 (Connector)。
- **關鍵技術**: Google ADK MCP Toolset, `asyncio` (Timeout, Error Handling)。
- **重要結論**: 負責連線到 MCP Server 並載入其提供的工具，轉換為 Agent 可使用的格式。
"""

import asyncio
import logging

# 新增: 匯入 signal 和 sys 以處理優雅關閉
# ADDED: Import signal and sys for graceful shutdown handling
import signal
import sys
from contextlib import asynccontextmanager
from utilities.mcp.mcp_discovery import MCPDiscovery
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

from mcp import StdioServerParameters
from rich import print


# 新增: 設定 MCP 清理問題的日誌記錄，以減少關閉期間的干擾
# ADDED: Configure logging for MCP cleanup issues to reduce noise during shutdown
logging.getLogger("mcp").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)


class MCPConnector:
    """
    從設定檔中發現 MCP 伺服器。
    設定檔將由 MCP 發現類別載入。
    然後它列出每個伺服器的工具，
    並將它們快取為與 Google Agent Development Kit 相容的 MCPToolsets。
    """

    def __init__(self, config_file: str = None):
        self.discovery = MCPDiscovery(config_file=config_file)
        self.tools: list[MCPToolset] = []

    async def _load_all_tools(self):
        """
        從發現的 MCP 伺服器載入所有工具，並將它們快取為 MCPToolsets。
        Loads all tools from the discovered MCP servers
        and caches them as MCPToolsets.
        """

        tools = []

        for name, server in self.discovery.list_servers().items():
            try:
                if server.get("command") == "streamable_http":
                    conn = StreamableHTTPServerParams(url=server["args"][0])
                else:
                    conn = StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command=server["command"], args=server["args"]
                        ),
                        timeout=5,
                    )

                # 新增: 使用 timeout 和錯誤處理包裝 toolset 建立過程
                # 這可以防止在無回應的 MCP 伺服器上卡住
                # ADDED: Wrap toolset creation with timeout and error handling
                # This prevents hanging on unresponsive MCP servers
                mcp_toolset = MCPToolset(connection_params=conn)
                toolset = await asyncio.wait_for(mcp_toolset.get_tools(), timeout=10.0)

                if toolset:
                    # 建立實際的 toolset 物件進行快取 (Create the actual toolset object for caching)
                    tool_names = [tool.name for tool in toolset]
                    print(
                        f"[bold green]已從伺服器 [cyan]'{name}'[/cyan] 載入工具:[/bold green] {', '.join(tool_names)}"
                    )
                    tools.append(mcp_toolset)

            # 新增: 針對不同類型的連接失敗進行特定錯誤處理
            # ADDED: Specific error handling for different types of connection failures
            except asyncio.TimeoutError:
                print(
                    f"[bold red]載入伺服器 '{name}' 的工具逾時 (跳過) (Timeout loading tools from server '{name}' (skipping))[/bold red]"
                )
            except ConnectionError as e:
                print(
                    f"[bold red]載入伺服器 '{name}' 的工具時發生連接錯誤: {e} (跳過) (Connection error loading tools from server '{name}': {e} (skipping))[/bold red]"
                )
            except Exception as e:
                print(
                    f"[bold red]載入伺服器 '{name}' 的工具時發生錯誤: {e} (跳過) (Error loading tools from server '{name}': {e} (skipping))[/bold red]"
                )

        self.tools = tools

    async def get_tools(self) -> list[MCPToolset]:
        """
        回傳快取的 MCPToolsets 列表。
        Returns the cached list of MCPToolsets.
        """

        await self._load_all_tools()
        return self.tools.copy()

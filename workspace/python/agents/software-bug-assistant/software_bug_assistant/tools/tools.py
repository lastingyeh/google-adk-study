import os
from datetime import datetime

# env file loading
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.langchain_tool import LangchainTool
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
from langchain_community.tools import StackExchangeTool
from langchain_community.utilities import StackExchangeAPIWrapper
from toolbox_core import ToolboxSyncClient

load_dotenv()


# --Example of a Function Tool--
def get_current_date() -> dict:
    """Get the current date in YYYY-MM-DD format."""
    return {"current_date": datetime.now().strftime("%Y-%m-%d")}


# -- Example of a Built-in Tool --
search_agent = Agent(
    model="gemini-2.5-flash",
    name="search_agent",
    instruction="""
  你是一個使用Google Search的專家
  """,
    tools=[google_search],
)

search_tool = AgentTool(search_agent)

# -- Example of a Third Party Tool (LangChainTool) --
stack_exchange_tool = StackExchangeTool(api_wrapper=StackExchangeAPIWrapper())
# -- Convert LangChain tool to ADK tool using LangchainTool
langchain_tool = LangchainTool(stack_exchange_tool)

# -- Example of a Google Cloud Tool (MCP Toolbox for database) --
TOOLBOX_URL = os.getenv("MCP_TOOLBOX_URL", "http://127.0.0.1:5000")


# Initialize Toolbox client and load tools
# If the toolbox server is not available (e.g., in CI), set to empty list
try:
    toolbox = ToolboxSyncClient(TOOLBOX_URL)
    toolbox_tools = toolbox.load_toolset("tickets_toolset")
except Exception:
    # Toolbox server not available, set to empty list
    toolbox_tools = []

# ----- Example of an MCP Tool (streamable-http) -----
# If GitHub token is not available (e.g., in CI), set to None
try:
    mcp_tools = MCPToolset(
        connection_param=StreamableHTTPConnectionParams(
            url="https://api.githubcopilot.com/mcp/",
            headers={
                "Authorization": "Bearer " + os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
            },
        ),
        tool_filter=[
            "search_repositories",
            "search_issues",
            "list_issues",
            "get_issue",
            "list_pull_requests",
            "get_pull_request",
        ],
    )
except Exception:
    # MCP Tool not available, set to empty list
    mcp_tools = None

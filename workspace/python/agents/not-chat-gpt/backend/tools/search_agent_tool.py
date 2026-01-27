from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool


search_agent = Agent(
    name="search_agent",  # 代理名稱
    model="gemini-3-flash-preview",
    instruction=f"""
    You're a specialist in Google Search
    """,
    tools=[google_search]
)

SEARCH_AGENT_TOOL = AgentTool(search_agent)

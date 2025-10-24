from google.adk.agents import LoopAgent
from google.adk.tools.agent_tool import AgentTool


from .sub_agents import scriptwriter_agent
from .sub_agents import visualizer_agent
from .sub_agents import formatter_agent

# --- Llm Agent Workflow ---
youtube_shorts_agent = LoopAgent(
    name="youtube_shorts_agent",
    max_iterations=3,
    sub_agents=[
        scriptwriter_agent,
        visualizer_agent,
        formatter_agent,
    ],
)

# --- Root Agent for the Runner ---
# The runner will now execute the workflow
root_agent = youtube_shorts_agent

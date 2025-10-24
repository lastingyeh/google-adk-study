from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from .util import load_instructions_from_file

from .sub_agents import scriptwriter_agent
from .sub_agents import visualizer_agent
from .sub_agents import formatter_agent

# --- Llm Agent Workflow ---
youtube_shorts_agent = LlmAgent(
    name="youtube_shorts_agent",
    model="gemini-2.0-flash-001",
    instruction=load_instructions_from_file("shorts_agent_instruction.txt"),
    description="You are an agent that can write scripts, visuals and format youtube short videos. You have subagents that can do this",
    tools=[
        AgentTool(scriptwriter_agent),
        AgentTool(visualizer_agent),
        AgentTool(formatter_agent),
    ],
)

# --- Root Agent for the Runner ---
# The runner will now execute the workflow
root_agent = youtube_shorts_agent

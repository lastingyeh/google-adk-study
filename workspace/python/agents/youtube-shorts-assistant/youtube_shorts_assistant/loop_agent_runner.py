from google.adk.agents import LoopAgent
from google.adk.tools.agent_tool import AgentTool


from .sub_agents import scriptwriter_agent
from .sub_agents import visualizer_agent
from .sub_agents import formatter_agent

# --- Llm Agent Workflow ---
youtube_shorts_agent = LoopAgent(
    name="youtube_shorts_agent",
    sub_agents=[
        scriptwriter_agent,
        visualizer_agent,
        formatter_agent,
    ],
)

# --- Root Agent for the Runner ---
# The runner will now execute the workflow
root_agent = youtube_shorts_agent

# Code required to make the agent programmatically runnable.
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from util import load_instruction_from_file

# Load .env
# Replace the API_KEY in .env file.
from dotenv import load_dotenv

load_dotenv()

# Instantiate constants
APP_NAME = "youtube_shorts_app"
USER_ID = "12345"
SESSION_ID = "123344"


# Session and Runner
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    runner = Runner(agent=youtube_shorts_agent, session_service=session_service)
    return session, runner


# Agent Interaction Example
async def call_agent_async(query: str):
    content = types.Content(role="user", parts=[types.TextPart(text=query)])
    session, runner = await setup_session_and_runner()

    events = runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=content
    )

    async for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)


call_agent_async("I want to write a short on how to build AI Agents")

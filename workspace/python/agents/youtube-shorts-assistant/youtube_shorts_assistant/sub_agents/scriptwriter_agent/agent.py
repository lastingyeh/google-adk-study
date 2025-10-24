from google.adk.agents import LlmAgent
from google.adk.tools import google_search

from prompt import script_writer_instruction

# --- input state keys ---
# 'raw_idea' : Original product idea or feature description

# --- Sub Agent 1: Scriptwriter ---
scriptwriter_agent = LlmAgent(
    name="ShortsScriptwriter",
    model="gemini-2.0-flash-001",
    instruction=script_writer_instruction,
    tools=[google_search],
    output_key="generated_script",  # Save result to state
)

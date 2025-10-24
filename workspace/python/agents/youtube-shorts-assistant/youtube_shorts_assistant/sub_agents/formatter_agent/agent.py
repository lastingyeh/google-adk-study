from google.adk.agents import LlmAgent
from google.adk.tools import google_search

from prompt import formatter_instruction

# --- input state keys ---
# 'generated_script' : Original product idea or feature description
# 'visual_concepts' : Visual concepts generated from the script

# --- Sub Agent 3: Formatter ---
# This agent would read both state keys and combine into the final Markdown
formatter_agent = LlmAgent(
    name="ConceptFormatter",
    model="gemini-2.0-flash-001",
    instruction=formatter_instruction,
    description="Formats the final Short concept.",
    output_key="final_short_concept",
)

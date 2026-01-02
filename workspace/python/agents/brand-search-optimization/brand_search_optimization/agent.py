from google.adk.agents.llm_agent import Agent

from .shared_libraries.constants import DESCRIPTION, AGENT_NAME, MODEL

from .sub_agents.comparison.agent import comparison_root_agent
from .sub_agents.search_results.agent import search_results_agent
from .sub_agents.keyword_finding.agent import keyword_finding_agent

from .prompt import ROOT_PROMPT


root_agent = Agent(
    model=MODEL,
    name=AGENT_NAME,
    description=DESCRIPTION,
    instruction=ROOT_PROMPT,
    sub_agents=[
        keyword_finding_agent,
        search_results_agent,
        comparison_root_agent,
    ],
)

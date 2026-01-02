from google.adk.agents.llm_agent import Agent

from ...shared_libraries.constants import MODEL
from .prompt import (
    COMPARISON_AGENT_PROMPT,
    COMPARISON_CRITIC_AGENT_PROMPT,
    COMPARISON_ROOT_AGENT_PROMPT,
)

comparison_agent = Agent(
    model=MODEL,
    name="comparison_generator_agent",
    description="生成產品標題之間的比較報告",
    instruction=COMPARISON_AGENT_PROMPT,
)

comparsion_critic_agent = Agent(
    model=MODEL,
    name="comparison_critic_agent",
    description="評論比較並提供有用的建議",
    instruction=COMPARISON_CRITIC_AGENT_PROMPT,
)


comparison_root_agent = Agent(
    model=MODEL,
    name="comparison_root_agent",
    description="路由代理以生成和評論比較",
    instruction=COMPARISON_ROOT_AGENT_PROMPT,
    sub_agents=[comparison_agent, comparsion_critic_agent],
)

from google.adk.agents.llm_agent import Agent

from ...shared_libraries.constants import MODEL
from ...tools.bq_connector import get_product_details_for_brand
from .prompt import KEYWORD_FINDING_PROMPT

keyword_finding_agent = Agent(
    model=MODEL,
    name="keyword_finding_agent",
    description="協助關鍵字搜尋優化的子代理。",
    instruction=KEYWORD_FINDING_PROMPT,
    tools=[get_product_details_for_brand],
)

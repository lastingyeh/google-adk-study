
"""商務代理人 - 簡化且乾淨的架構

此代理人協助使用者透過 Google Search 接地來尋找運動產品。
遵循官方 ADK 範例模式以求簡單與易於維護。

注意：接地回呼 (create_grounding_callback) 應傳遞給 Runner，
而非直接傳遞給 Agent。請參閱 README 以了解使用範例。
"""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from .config import MODEL_NAME, AGENT_NAME
from .tools.search import search_products
from .tools.preferences import save_preferences, get_preferences
from .prompt import commerce_agent_instruction
# 匯出回調以供 Runner 使用
from .callbacks import create_grounding_callback

root_agent = Agent(
    model=MODEL_NAME,
    name=AGENT_NAME,
    description="一位個人運動購物禮賓，使用 Google Search 接地與儲存的使用者偏好來提供專家級產品推薦。",
    instruction=commerce_agent_instruction,
    tools=[
        search_products,  # 包裝 Google Search 的 AgentTool
        FunctionTool(func=save_preferences),
        FunctionTool(func=get_preferences),
    ],
)

# 匯出回調以供 Runner 使用：
# runner = Runner(
#     agent=root_agent,
#     after_model_callbacks=[create_grounding_callback(verbose=True)]
# )
__all__ = ["root_agent", "create_grounding_callback"]


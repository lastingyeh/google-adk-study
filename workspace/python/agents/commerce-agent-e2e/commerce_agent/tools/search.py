
"""用於體育產品搜尋的 Google Search 包裝器。"""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.google_search_tool import google_search

# 使用 Google Search 接地的搜尋代理人
_search_agent = Agent(
    model="gemini-2.5-flash",
    name="sports_product_search",
    description="使用帶有 Grounding 的 Google Search 搜尋體育產品",
    instruction="""搜尋體育產品並提供詳細資訊與購買連結。

    搜尋時：
    1. 使用綜合查詢，例如 "2025 年 100 歐元以下最佳越野跑鞋"
    2. 提取關鍵產品資訊：名稱、品牌、價格、功能
    3. **關鍵**：顯示來自搜尋結果的 URL，並清楚註明零售商歸屬
    4. 提供 3-5 個帶有可點擊連結的產品

    回應格式：
    - 產品名稱與品牌
    - 價格 (歐元)
    - 關鍵功能 (2-3 個要點)
    - **購買連結**：顯示可見的零售商網域
    - 簡要說明為何符合使用者需求

    重要：Google Search 在 grounding_chunks 中提供 web.uri 和 web.domain 欄位。
    提取這些欄位並格式化 URL 以清楚顯示零售商網域：
    - 格式：🔗 **在 [domain] 購買**：[full_url]
    - 範例：🔗 **在 alltricks.com 購買**：https://www.alltricks.com/...

    範例回應格式：
    "Brooks Divide 5 - €95
    - 適合初學者的舒適緩衝
    - 適合混合地形
    - 🔗 **在 decathlon.com.hk 購買**：https://decathlon.com.hk/brooks-divide-5"
    """,
    tools=[google_search],
)

# 匯出為 AgentTool 以供主代理人使用
search_products = AgentTool(agent=_search_agent)

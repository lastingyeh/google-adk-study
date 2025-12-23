"""
整合 Interactions API 的 ADK 代理

本模組展示如何將 Google 的 Interactions API 與 Agent Development Kit (ADK) 整合，
以實現增強的代理工作流程 (agentic workflows)。

主要功能：
- 透過 Interactions API 進行伺服器端狀態管理
- 支援長時間執行任務的背景執行 (Background execution)
- 原生思維處理 (Native thought handling)
- 無縫的工具協調 (Seamless tool orchestration)

需求：
- google-adk >= 1.18.0
- google-genai >= 1.55.0
- GOOGLE_API_KEY 環境變數
"""

import os
from typing import Dict, Any

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini

from dotenv import load_dotenv

from .tools import (
    get_current_weather,
    calculate_expression,
    search_knowledge_base,
)

load_dotenv()

# 代理指令範本 (Agent instruction template)
# 定義代理的角色、可用工具及行為準則
AGENT_INSTRUCTION = """你是使用 Gemini Interactions API 驅動的實用 AI 助理。

你可以使用以下工具：

1. **get_current_weather**: 取得任何地點的天氣資訊
   - 當使用者詢問天氣狀況時使用
   - 提供地點格式為 "City, Country" (城市, 國家)

2. **calculate_expression**: 執行數學運算
   - 用於算術、百分比和方程式
   - 可處理複雜的表達式

3. **search_knowledge_base**: 搜尋資訊
   - 用於事實性查詢
   - 返回相關文件和摘要片段

## 準則 (Guidelines)

- 總是使用適合該任務的工具
- 提供清晰、有幫助的回覆
- 如果工具失敗，解釋問題並提供替代方案
- 對於複雜的研究問題，承認其限制

## 互動範例 (Example Interactions)

使用者: "東京的天氣如何？"
→ 使用 get_current_weather，參數 location="Tokyo, Japan"

使用者: "計算 250 的 15%"
→ 使用 calculate_expression，參數 expression="15% of 250"

使用者: "告訴我關於量子運算的資訊"
→ 使用 search_knowledge_base，參數 query="quantum computing fundamentals"
"""


def create_interactions_enabled_agent(
    model: str = "gemini-2.5-flash",
    use_interactions_api: bool = True,
) -> Agent:
    """
    建立一個具備 Interactions API 後端的 ADK 代理。

    Args:
        model: 要使用的 Gemini 模型。
        use_interactions_api: 是否啟用 Interactions API。

    Returns:
        設定完成的 Agent 實例。

    Example:
        >>> agent = create_interactions_enabled_agent()
        >>> # 可配合 adk web 或以程式方式使用
    """
    # 初始化 Agent，並設定 Gemini 模型參數
    return Agent(
        model=Gemini(
            model=model,
            # 為此代理啟用 Interactions API
            # 這提供了：
            # - 伺服器端狀態管理 (Server-side state management)
            # - 背景執行支援 (Background execution support)
            # - 原生思維處理 (Native thought handling)
            use_interactions_api=use_interactions_api,
        ),
        name="adk_interactions_agent",
        description="一個展示 Interactions API 整合的 ADK 代理，具備天氣、計算和搜尋工具。",
        instruction=AGENT_INSTRUCTION,
        tools=[
            get_current_weather,
            calculate_expression,
            search_knowledge_base,
        ],
    )


def create_standard_agent(model: str = "gemini-2.5-flash") -> Agent:
    """
    建立一個不使用 Interactions API 的標準 ADK 代理。

    這對於比較差異或當你不需要 Interactions API 功能時很有用。

    Args:
        model: 要使用的 Gemini 模型。

    Returns:
        設定完成的 Agent 實例。
    """
    return Agent(
        model=model,
        name="standard_agent",
        description="用於比較的標準 ADK 代理。",
        instruction=AGENT_INSTRUCTION,
        tools=[
            get_current_weather,
            calculate_expression,
            search_knowledge_base,
        ],
    )


# 匯出 root_agent 以供 ADK 探索使用
# 這是 `adk web` 找到代理所必需的
root_agent = create_interactions_enabled_agent()


# 用於不同配置的替代代理工廠類別
class AgentFactory:
    """用於建立不同代理配置的工廠類別。"""

    @staticmethod
    def interactions_agent() -> Agent:
        """建立已啟用 Interactions API 的代理。"""
        return create_interactions_enabled_agent(use_interactions_api=True)

    @staticmethod
    def standard_agent() -> Agent:
        """建立不使用 Interactions API 的標準代理。"""
        return create_standard_agent()

    @staticmethod
    def pro_agent() -> Agent:
        """建立使用 Gemini Pro 模型的代理。"""
        return create_interactions_enabled_agent(
            model="gemini-2.5-pro",
            use_interactions_api=True
        )

# 重點摘要
#
# - **核心概念**：展示如何透過 ADK 使用 Gemini Interactions API。
# - **關鍵技術**：Interactions API, ADK Agent, Server-side State。
# - **重要結論**：透過 `use_interactions_api=True` 參數，即可將標準 ADK 代理升級為具備 Interactions API 能力的代理。
# - **行動項目**：使用 `root_agent` 作為主要入口點，或使用 `AgentFactory` 建立特定配置的代理。
#
# 類別/函式結構圖
# ```mermaid
# classDiagram
#     class AgentFactory {
#         +interactions_agent() Agent
#         +standard_agent() Agent
#         +pro_agent() Agent
#     }
#     class create_interactions_enabled_agent {
#         <<function>>
#     }
#     class create_standard_agent {
#         <<function>>
#     }
#
#     AgentFactory ..> create_interactions_enabled_agent : uses
#     AgentFactory ..> create_standard_agent : uses
# ```

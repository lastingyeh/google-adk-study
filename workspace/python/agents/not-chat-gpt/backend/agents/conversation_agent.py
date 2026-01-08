"""Conversation Agent 範例代理

這是你的第一個 ADK 代理（Agent）。功能：提供友善的對話體驗。

核心概念說明：
- ADK (Agent Development Kit)：用於快速建立具備指令 (instruction) 與模型 (model) 的 AI 代理。
- Agent：包裝模型、名稱、描述與指令的物件，啟動後可在 Web UI 中被選取進行互動。

此檔案主要定義一個名為 `root_agent` 的代理，為 ADK 啟動時的入口。依框架需求，若要在 Web 介面中自動列出該代理，必須使用名稱 `root_agent` 做為變數。

v2 更新：
- 參考 personal-tutor 範例，導入狀態管理機制。
- 設計三種狀態層級，以模仿 GPT 的記憶與上下文能力：
  1. `user:` 前綴：永久儲存使用者偏好。
  2. Session 狀態：記錄當前對話歷史。
  3. `temp:` 前綴：單次呼叫的暫存分析資料。
"""

from __future__ import annotations
from typing import Dict, Any, List

from google.adk.agents import Agent  # 匯入 ADK 提供的 Agent 類別，用來建立代理核心物件
from google.adk.tools.tool_context import ToolContext


# ============================================================================
# TOOLS: State Management
# ============================================================================


def remember_user_info(
    key: str, value: str, tool_context: ToolContext
) -> Dict[str, Any]:
    """儲存關於使用者的長期資訊（例如姓名、偏好）。

    說明：
    - 使用 `user:` 前綴，代表此資訊將跨工作階段永久保存。
    - 用於建立個人化體驗。
    """
    tool_context.state[f"user:{key}"] = value
    return {"status": "success", "message": f"已記住 {key} 為 {value}"}


def get_user_info(key: str, tool_context: ToolContext) -> Dict[str, Any]:
    """讀取先前儲存的使用者長期資訊。"""
    value = tool_context.state.get(f"user:{key}")
    if value:
        return {"status": "found", "key": key, "value": value}
    return {"status": "not_found", "key": key}


def add_message_to_history(
    role: str, content: str, tool_context: ToolContext
) -> Dict[str, Any]:
    """將一則訊息加入當前對話歷史（Session 狀態）。

    說明：
    - 不使用前綴，代表此狀態僅存於當前工作階段。
    - `role` 應為 'user' 或 'assistant'。
    """
    history = tool_context.state.get("conversation_history", [])
    history.append({"role": role, "content": content})
    tool_context.state["conversation_history"] = history
    return {"status": "success", "history_length": len(history)}


def analyze_intent(intent: str, tool_context: ToolContext) -> Dict[str, Any]:
    """分析使用者最新訊息的意圖，並暫存結果。

    說明：
    - 使用 `temp:` 前綴，代表此狀態為單次呼叫的暫存資料，呼叫結束後即丟棄。
    - 用於在生成回應前，進行中間步驟的思考或標記。
    """
    tool_context.state["temp:last_message_intent"] = intent
    return {"status": "success", "analyzed_intent": intent}


# ============================================================================
# AGENT DEFINITION
# ============================================================================

# 定義代理：按照框架規則，變數必須命名為 'root_agent' 才會被自動載入。
# 參數說明：
# - name: 顯示於介面或識別此代理的名稱。
# - model: 使用的基礎模型（此處為 Gemini 2.0 Flash，追求快速回應）。
# - description: 對此代理的簡短描述，通常會顯示在 UI 或紀錄中。
# - instruction: 系統指令，提供模型角色定位與語氣要求，影響生成內容的風格與限制。
#
# 設計考量：
# 1. 指令保持簡潔，避免過度冗長導致回應延遲。
# 2. 使用正向明確語氣（warm, helpful, friendly），提升使用者互動體驗。
# 3. 後續可擴充：加入工具能力、上下文記憶、使用者偏好設定等。
#
# 若要調整模型，可將 model 參數修改為其他可用標籤；需確保相依平台已支援。

root_agent = Agent(
    name="ConversationAgent",  # 代理名稱，可於 UI 下拉選單看到
    model="gemini-2.0-flash",  # 使用的模型：高速度、適合互動式對話
    description="一個具備狀態管理能力的友善 AI 助理，能記住使用者資訊與對話歷史。",  # 簡述用途
    instruction=(  # 系統指令：影響基礎回應行為
        """
        你是一個溫暖且樂於助人的助理，具備模仿 GPT 的記憶能力。

        核心能力:
        1.  **對話歷史**: 使用 `add_message_to_history` 工具記錄每一輪對話 (使用者與你自己的回應)，以維持上下文的連貫性。
        2.  **使用者記憶**: 如果使用者提到個人資訊 (例如名字)，使用 `remember_user_info` 工具將其永久記住。在後續對話中，可使用 `get_user_info` 來回憶這些資訊，並稱呼使用者。
        3.  **意圖分析**: 在回應前，可選擇性使用 `analyze_intent` 工具對使用者的問題進行分類或標記，此為暫存資訊。

        互動流程:
        - 熱情地問候使用者。
        - 在每次互動中，先將使用者的話加入歷史紀錄，然後再生成你的回應，並將你的回應也加入歷史紀錄。
        - 如果偵測到可記憶的資訊，就呼叫工具儲存起來。
        - 保持對話性和友善！
        """
    ),
    tools=[
        remember_user_info,
        get_user_info,
        add_message_to_history,
        analyze_intent,
    ],
    output_key="last_response",  # 最後回應會存放在 state['last_response']
)

# 擴充建議：
# - 可以新增工具 (tools) 參數：整合計算、查詢或外部 API。
# - 可以加入記憶模組：讓代理根據歷史對話調整回應。
# - 可以針對 domain 調整 instruction，例如客服、教學、旅遊規劃等場景。
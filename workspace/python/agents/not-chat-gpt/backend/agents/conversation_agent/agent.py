"""Conversation Agent 範例代理

這是你的第一個 ADK 代理（Agent）。功能：提供友善的對話體驗。

核心概念說明：
- ADK (Agent Development Kit)：用於快速建立具備指令 (instruction) 與模型 (model) 的 AI 代理。
- Agent：包裝模型、名稱、描述與指令的物件，啟動後可在 Web UI 中被選取進行互動。

此檔案主要定義一個名為 `root_agent` 的代理，為 ADK 啟動時的入口。依框架需求，若要在 Web 介面中自動列出該代理，必須使用名稱 `root_agent` 做為變數。
"""

from __future__ import annotations
from typing import Dict, Any

from google.adk.agents import Agent  # 匯入 ADK 提供的 Agent 類別，用來建立代理核心物件
from google.adk.tools.tool_context import ToolContext
from guardrails.guardrails import before_model_callback  # 匯入安全防護回調函數


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


def get_user_info(tool_context: ToolContext) -> Dict[str, Any]:
    """載入使用者的完整上下文資訊，在對話開始時使用。"""
    user_data = {}
    
    # 載入所有以 user: 開頭的狀態
    for key, value in tool_context.state.to_dict().items():
        if key.startswith("user:"):
            clean_key = key.replace("user:", "")
            user_data[clean_key] = value
    
    return {
        "status": "success",
        "user_context": user_data,
        "total_items": len(user_data),
        "message": "已載入完整使用者上下文" if user_data else "尚無使用者資訊"
    }


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

conversation_agent = Agent(
    name="ConversationAgent",  # 代理名稱，可於 UI 下拉選單看到
    model="gemini-2.0-flash",  # 使用的模型：高速度、適合互動式對話
    description="一個具備狀態管理能力的友善 AI 助理，能記住使用者資訊與對話歷史。",  # 簡述用途
    instruction=(  # 系統指令：影響基礎回應行為
        """
        你是一個溫暖且樂於助人的助理，具備持久記憶能力，能記住用戶的個人資訊和偏好。

        **工具使用策略**:

        1. **記憶查詢 (`get_user_info`)**:
           - 當 session 剛啟動且缺乏用戶 context 時，調用此工具載入已知的用戶資訊
           - 當用戶提到「我之前說過」、「你還記得我嗎」等暗示有歷史記錄的話語時
           - 當需要個人化回應但不確定用戶背景時
           - **不需要每次對話都調用，只在需要 context 時使用**

        2. **資訊儲存 (`remember_user_info`)**:
           - 用戶主動分享個人資訊時立即儲存（姓名、工作、興趣、偏好等）
           - 用戶提到重要的個人狀況或需求時
           - 任何值得記住以改善未來互動的資訊

        **互動準則**:
        - 在對話初期，如果缺乏用戶背景且對話需要個人化，先使用 `get_user_info` 了解用戶
        - 根據已知資訊提供個人化回應（如稱呼姓名、回憶偏好）
        - 主動但自然地詢問並記住用戶資訊
        - 保持溫暖友善的對話風格

        **範例時機**:
        - 用戶說「嗨」→ 先查看是否認識這個用戶
        - 用戶問「你還記得我的名字嗎？」→ 調用 `get_user_info`
        - 用戶說「我叫小明」→ 調用 `remember_user_info`
        """
    ),
    tools=[
        remember_user_info,
        get_user_info,
    ],
    before_model_callback=before_model_callback,
)

# 擴充建議：
# - 可以新增工具 (tools) 參數：整合計算、查詢或外部 API。
# - 可以加入記憶模組：讓代理根據歷史對話調整回應。
# - 可以針對 domain 調整 instruction，例如客服、教學、旅遊規劃等場景。
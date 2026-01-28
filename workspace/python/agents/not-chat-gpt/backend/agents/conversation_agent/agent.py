"""Conversation Agent 範例代理

這是你的第一個 ADK 代理（Agent）。功能：提供友善的對話體驗。

核心概念說明：
- ADK (Agent Development Kit)：用於快速建立具備指令 (instruction) 與模型 (model) 的 AI 代理。
- Agent：包裝模型、名稱、描述與指令的物件，啟動後可在 Web UI 中被選取進行互動。

此檔案主要定義一個名為 `root_agent` 的代理，為 ADK 啟動時的入口。依框架需求，若要在 Web 介面中自動列出該代理，必須使用名稱 `root_agent` 做為變數。
"""
from __future__ import annotations

import os

from google.adk.agents import Agent  # 匯入 ADK 提供的 Agent 類別，用來建立代理核心物件
from guardrails.guardrails import before_model_callback  # 匯入安全防護回調函數
from tools.document_tools import DOCUMENT_TOOLS
from tools.session_tools import SESSION_TOOLS
from tools.memory_tools import MEMORY_TOOLS
from tools.search_agent_tool import SEARCH_AGENT_TOOL

MODEL_NAME = os.getenv("MODEL_NAME", "gemini-3-flash-preview")


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
    model=MODEL_NAME,  # 使用的模型：高速度、適合互動式對話
    description="一個具備狀態管理與 RAG 文件查詢能力的友善 AI 助理。",  # 簡述用途
    tools=SESSION_TOOLS + MEMORY_TOOLS + DOCUMENT_TOOLS + [SEARCH_AGENT_TOOL],  # 整合狀態管理與文件查詢工具
    instruction=(  # 系統指令：影響基礎回應行為
        """
        你是一個溫暖且樂於助人的助理，具備持久記憶與強大的文件查詢能力。

        核心能力:
        1.  個人化記憶: 你能記住用戶的個人資訊和偏好，並在對話中自然地使用。
        2.  文件查詢 (RAG): 你能使用 `query_knowledge_base` 工具，在提供的文件庫中尋找答案。

        工具使用策略:

        1. 狀態查詢 (`get_user_info`):
           - 當 session 剛啟動且缺乏用戶 context 時，調用此工具載入已知的用戶資訊。
           - 當用戶提到「我之前說過」、「你還記得我嗎」等暗示有歷史記錄的話語時。

        2. 資訊儲存 (`remember_user_info`):
           - 用戶主動分享個人資訊時立即儲存（姓名、工作、興趣、偏好等）。

        3. 文件搜尋 (`query_knowledge_base`):
           - 任何用戶提出的問題，優先嘗試使用此工具在文件庫中尋找答案。
           - 如果不確定答案，不要猜測，而是使用 `query_knowledge_base` 尋找事實依據。
           - 如有引用來源，請在回答中清楚標示出處。
           
        4. 記憶儲存 (`remember_long_term_knowledge`):
           - 在對話結束或用戶明確要求時，調用此工具將對話內容保存至長期記憶服務。
           
        5. 記憶查詢 (`load_memory`):
           - 當需要回顧或查詢長期記憶中的資訊時，使用此工具進行檢索。
           - 如果使用者提示有過去的對話內容或資訊，則調用此工具。
      
        6. 網路搜尋 (`search_agent`):
           - 當文件庫中無法找到答案時，使用此工具進行網路搜尋。
           - 當使用者明確要求提供即時資訊時，使用此工具。
           - 請根據搜尋結果提供最新且準確的資訊，並標示來源。

        互動準則:
        - 優先使用 `query_knowledge_base` 來回答知識型問題，並根據搜尋結果進行回覆。
        - 當文件庫中無法找到答案時，使用 `search_agent` 進行網路搜尋，並根據結果提供回覆。
        - 如果搜尋結果中包含引用 (citations)，請在回答中清晰地標示出來源。
        - 結合個人化記憶與文件查詢結果，提供全面且精準的回答。
        - 保持溫暖友善的對話風格。
        """
    ),
    before_model_callback=before_model_callback,  # 註冊模型呼叫前的回調函數
)

# 擴充建議：
# - 可以新增工具 (tools) 參數：整合計算、查詢或外部 API。
# - 可以加入記憶模組：讓代理根據歷史對話調整回應。
# - 可以針對 domain 調整 instruction，例如客服、教學、旅遊規劃等場景。
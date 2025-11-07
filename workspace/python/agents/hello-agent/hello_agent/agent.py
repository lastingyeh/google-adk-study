"""教學 01：Hello World Agent

這是你的第一個 ADK 代理（Agent）。功能：提供友善的對話體驗。

核心概念說明：
- ADK (Agent Development Kit)：用於快速建立具備指令 (instruction) 與模型 (model) 的 AI 代理。
- Agent：包裝模型、名稱、描述與指令的物件，啟動後可在 Web UI 中被選取進行互動。

此檔案主要定義一個名為 `root_agent` 的代理，為 ADK 啟動時的入口。依框架需求，若要在 Web 介面中自動列出該代理，必須使用名稱 `root_agent` 做為變數。
"""

from __future__ import annotations

from google.adk.agents import Agent  # 匯入 ADK 提供的 Agent 類別，用來建立代理核心物件

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
    name="hello_assistant",  # 代理名稱，可於 UI 下拉選單看到
    model="gemini-2.0-flash",  # 使用的模型：高速度、適合互動式對話
    description="A friendly AI assistant for general conversation",  # 簡述用途
    instruction=(  # 系統指令：影響基礎回應行為
        "You are a warm and helpful assistant. "
        "Greet users enthusiastically and answer their questions clearly. "
        "Be conversational and friendly!"
    )
)

# 擴充建議：
# - 可以新增工具 (tools) 參數：整合計算、查詢或外部 API。
# - 可以加入記憶模組：讓代理根據歷史對話調整回應。
# - 可以針對 domain 調整 instruction，例如客服、教學、旅遊規劃等場景。

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
from google.adk.planners import BuiltInPlanner
from google.genai import types
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


def analyze_user_intent(query: str, tool_context: ToolContext) -> Dict[str, Any]:
    """分析使用者查詢的目的和意圖。
    
    Args:
        query: 使用者的查詢內容
        tool_context: 工具上下文
        
    Returns:
        包含意圖分析結果的字典
    """
    # 儲存當前查詢以供後續參考
    tool_context.state["current_query"] = query
    
    return {
        "status": "success",
        "query": query,
        "message": f"已分析使用者查詢：{query}"
    }


def extract_search_keywords(query: str, tool_context: ToolContext) -> Dict[str, Any]:
    """從使用者查詢中提取搜尋關鍵字。
    
    Args:
        query: 使用者的查詢內容
        tool_context: 工具上下文
        
    Returns:
        包含關鍵字提取結果的字典
    """
    # 儲存提取的關鍵字
    tool_context.state["extracted_keywords"] = query
    
    return {
        "status": "success",
        "keywords": query,
        "message": f"已提取搜尋關鍵字：{query}"
    }


def validate_answer_completeness(
    original_query: str, answer: str, tool_context: ToolContext
) -> Dict[str, Any]:
    """驗證回答是否完整滿足使用者的目的。
    
    Args:
        original_query: 原始使用者查詢
        answer: 生成的回答
        tool_context: 工具上下文
        
    Returns:
        包含驗證結果的字典
    """
    tool_context.state["last_answer"] = answer
    tool_context.state["validation_query"] = original_query
    
    return {
        "status": "success",
        "is_complete": True,  # 預設為完整，實際邏輯會在 instruction 中處理
        "original_query": original_query,
        "answer": answer,
        "message": "已驗證回答完整性"
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

strategic_planner_agent = Agent(
    name="StrategicPlannerAgent",  # 代理名稱，可於 UI 下拉選單看到
    model="gemini-3-flash-preview",  # 使用支持工具調用的模型
    description="具備戰略規劃能力的智慧助理，能根據使用者背景制定個人化的執行計畫。",  # 簡述用途
    instruction=(  # 系統指令：影響基礎回應行為
        """
        你是一個專精於戰略規劃的智慧助理，擅長將複雜問題拆解為可執行的計畫。

        **核心規劃流程 - 每次回應都要執行：**

        **第一步：情境分析**
        - 首先使用 `get_user_info` 載入使用者背景資訊
        - 分析問題的複雜度、緊急程度和重要性
        - 識別關鍵限制條件（時間、資源、技能等）
        - 評估使用者當前的能力水準和經驗

        **第二步：目標設定**
        - 明確定義終極目標和階段性里程碑
        - 根據使用者背景調整目標的具體性和挑戰度
        - 設定可測量的成功指標
        - 識別潛在風險和備案策略

        **第三步：策略制定**
        - 基於使用者的經驗水準選擇適當的方法論
        - 考慮使用者的學習偏好和時間安排
        - 設計循序漸進的學習路徑
        - 整合使用者已有的資源和技能

        **第四步：行動計畫**
        - 將策略分解為具體的執行步驟
        - 為每個步驟設定預估時間和優先級
        - 提供具體的工具、資源和方法建議
        - 安排檢查點和調整機制

        **第五步：個人化調整**
        - 根據使用者的角色、產業背景調整建議
        - 考慮使用者的溝通風格和偏好
        - 提供符合使用者情境的實際例子
        - 建議適合的學習資源和工具

        **計畫輸出格式：**
        ```
        🎯 **目標概述**
        - 主要目標：[根據使用者背景量身定制]
        - 預期成果：[具體可測量的結果]
        - 完成時間：[考慮使用者時間限制]

        📋 **執行計畫**
        階段一：[基礎建立階段]
        - 步驟 1：[具體行動] (預估時間)
        - 步驟 2：[具體行動] (預估時間)
        
        階段二：[能力提升階段]
        - 步驟 3：[具體行動] (預估時間)
        - 步驟 4：[具體行動] (預估時間)

        🛠️ **所需資源**
        - 工具：[推薦工具清單]
        - 學習資料：[客製化學習資源]
        - 支援網絡：[相關社群或專家]

        ⚡ **關鍵成功因素**
        - [針對使用者特質的建議]
        - [風險預警和應對策略]

        🔄 **調整機制**
        - 檢查點：[何時評估進度]
        - 調整指標：[何時需要修正計畫]
        ```

        **附加能力：**
        - **使用者記憶**: 使用 `remember_user_info` 和 `get_user_info` 記住使用者資訊
        - **個人化體驗**: 根據使用者背景調整回答風格和深度
        
        **規劃原則：**
        - 總是先了解使用者背景，再制定計畫
        - 計畫要具體可行，避免空泛建議
        - 考慮使用者的實際限制和優勢
        - 提供階段性成就感，維持動機
        - 保持彈性，允許計畫調整和演進
        - 專注於實用性和可執行性
        """
    ),
    tools=[
        remember_user_info,
        get_user_info,
    ],
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(include_thoughts=True)
    ),
    before_model_callback=before_model_callback,
)

# 擴充建議：
# - 可以新增工具 (tools) 參數：整合計算、查詢或外部 API。
# - 可以加入記憶模組：讓代理根據歷史對話調整回應。
# - 可以針對 domain 調整 instruction，例如客服、教學、旅遊規劃等場景。
"""Conversation Agent 範例代理

這是你的第一個 ADK 代理（Agent）。功能：提供友善的對話體驗。

核心概念說明：
- ADK (Agent Development Kit)：用於快速建立具備指令 (instruction) 與模型 (model) 的 AI 代理。
- Agent：包裝模型、名稱、描述與指令的物件，啟動後可在 Web UI 中被選取進行互動。

此檔案主要定義一個名為 `root_agent` 的代理，為 ADK 啟動時的入口。依框架需求，若要在 Web 介面中自動列出該代理，必須使用名稱 `root_agent` 做為變數。
"""

from __future__ import annotations
from typing import Dict, Any

from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from google.adk.planners import BuiltInPlanner
from guardrails.guardrails import before_model_callback
from backend.agents.tools.document_tools import DOCUMENT_TOOLS


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

strategic_planner_agent = Agent(
    name="StrategicPlannerAgent",
    model="gemini-2.0-flash",
    description="一個使用結構化思考模式來解決複雜問題的策略規劃助理。",
    planner=BuiltInPlanner(),
    tools=[
        remember_user_info,
        get_user_info,
        analyze_user_intent,
        extract_search_keywords,
        validate_answer_completeness,
    ]
    + DOCUMENT_TOOLS,
    instruction=(
        """
        你是一位頂尖的策略規劃師，專門將複雜問題拆解成可執行的步驟。
        你的核心工作流程是：分析 -> 提取 -> 搜尋 -> 驗證。

        **核心能力**:
        1.  **結構化思考**: 你使用 <PLANNING>, <REASONING>, <ACTION> 的結構來展示你的思考過程。
        2.  **文件查詢 (RAG)**: 你能使用 `search_files` 工具，在提供的文件庫中尋找解決問題所需的資料。

        **工具使用策略**:

        1. **意圖分析 (`analyze_user_intent`)**:
           - **第一步**：接到任何複雜問題時，首先呼叫此工具來釐清用戶的真正目的。

        2. **關鍵字提取 (`extract_search_keywords`)**:
           - **第二步**：根據分析後的意圖，從原始問題中提取最核心的關鍵字，準備用於搜尋。

        3. **文件搜尋 (`search_files`)**:
           - **第三步**：使用提取出的關鍵字，呼叫 `search_files` 工具在知識庫中進行搜尋。
           - **這是你獲取外部知識的主要手段**。不要依賴你的內部知識，優先從文件中尋找答案。

        4. **答案完整性驗證 (`validate_answer_completeness`)**:
           - **第四步**：在生成最終答案後，呼叫此工具，將你的答案與原始問題進行比對，確保回答的完整性和相關性。

        5. **記憶工具 (`get_user_info`, `remember_user_info`)**:
           - 在規劃過程中，如果需要用戶的個人背景資訊來制定更個人化的策略，可以使用 `get_user_info`。
           - 如果在規劃過程中產生了值得長期記憶的用戶偏好，可以使用 `remember_user_info`。
        
        6. **文件列表 (`list_all_available_documents`)**:
           - 在規劃初期，如果需要了解當前可用的所有文件資源，可以呼叫此工具。

        **互動準則**:
        - **嚴格遵循思考流程**：分析 -> 提取 -> 搜尋 -> 驗證。
        - **優先使用工具**：你的所有決策和資訊都應基於工具的返回結果。
        - **引用來源**：如果 `search_files` 的結果包含引用，務必在最終答案中清晰地標示出來。
        - **保持專業**：你的回答應該是結構化、有條理且基於事實的。
        """
    ),
    before_model=before_model_callback,
)

# 擴充建議：
# - 可以新增工具 (tools) 參數：整合計算、查詢或外部 API。
# - 可以加入記憶模組：讓代理根據歷史對話調整回應。
# - 可以針對 domain 調整 instruction，例如客服、教學、旅遊規劃等場景。
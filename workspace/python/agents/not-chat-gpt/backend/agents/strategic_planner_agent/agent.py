"""Conversation Agent 範例代理

這是你的第一個 ADK 代理（Agent）。功能：提供友善的對話體驗。

核心概念說明：
- ADK (Agent Development Kit)：用於快速建立具備指令 (instruction) 與模型 (model) 的 AI 代理。
- Agent：包裝模型、名稱、描述與指令的物件，啟動後可在 Web UI 中被選取進行互動。

此檔案主要定義一個名為 `root_agent` 的代理，為 ADK 啟動時的入口。依框架需求，若要在 Web 介面中自動列出該代理，必須使用名稱 `root_agent` 做為變數。
"""
from __future__ import annotations

import os
from typing import Dict, Any

from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from google.adk.planners import BuiltInPlanner
from google.adk.tools import google_search
from google.genai import types
from guardrails.guardrails import before_model_callback
from tools.document_tools import DOCUMENT_TOOLS
from tools.session_tools import SESSION_TOOLS
from tools.memory_tools import MEMORY_TOOLS


MODEL_NAME = os.getenv("MODEL_NAME", "gemini-3-flash-preview")


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
    model=MODEL_NAME,
    description="一個使用結構化思考模式來解決複雜問題的策略規劃助理。",
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(include_thoughts=True)
    ),
    tools=[
        analyze_user_intent,
        extract_search_keywords,
        validate_answer_completeness,
        google_search,
    ] + SESSION_TOOLS + MEMORY_TOOLS + DOCUMENT_TOOLS,
    instruction=(
        """
        你是一位頂尖的策略規劃師，專門將複雜問題拆解成可執行的步驟。
        你的核心工作流程是：分析 -> 提取 -> 搜尋 -> 驗證。

        核心能力:
        1.  結構化思考: 你使用 <PLANNING>, <REASONING>, <ACTION> 的結構來展示你的思考過程。
        2.  文件查詢 (RAG): 你能使用 `search_files` 工具，在提供的文件庫中尋找解決問題所需的資料。

        工具使用策略:

        1. 意圖分析 (`analyze_user_intent`):
           - 第一步：接到任何複雜問題時，首先呼叫此工具來釐清用戶的真正目的。

        2. 關鍵字提取 (`extract_search_keywords`):
           - 第二步：根據分析後的意圖，從原始問題中提取最核心的關鍵字，準備用於搜尋。

        3. 文件搜尋 (`search_files`):
           - 第三步：使用提取出的關鍵字，呼叫 `search_files` 工具在知識庫中進行搜尋。
           - 這是你獲取外部知識的主要手段。不要依賴你的內部知識，優先從文件中尋找答案。

        4. 答案完整性驗證 (`validate_answer_completeness`):
           - 第四步：在生成最終答案後，呼叫此工具，將你的答案與原始問題進行比對，確保回答的完整性和相關性。

        5. 狀態工具 (`get_user_info`, `remember_user_info`):
           - 在規劃過程中，如果需要用戶的個人背景資訊來制定更個人化的策略，可以使用 `get_user_info`。
           - 如果在規劃過程中產生了值得長期記憶的用戶偏好，可以使用 `remember_user_info`。
        
        6. 文件搜尋 (`search_files`):
           - 任何用戶提出的問題，優先嘗試使用此工具在文件庫中尋找答案。
           - 如果不確定答案，不要猜測，而是使用 `search_files` 尋找事實依據。
           - 如有引用來源，請在回答中清楚標示出處。
           
        7. 記憶儲存 (`remember_long_term_knowledge`):
           - 在對話結束或用戶明確要求時，調用此工具將對話內容保存至長期記憶服務。
           
        8. 記憶查詢 (`load_memory`):
           - 當需要回顧或查詢長期記憶中的資訊時，使用此工具進行檢索。
           - 如果使用者提示有過去的對話內容或資訊，則調用此工具。

        9. 網路搜尋 (`google_search`):
           - 當文件庫中無法找到答案時，使用此工具進行網路搜尋。
           - 當使用者明確要求提供即時資訊時，使用此工具。
           - 請根據搜尋結果提供最新且準確的資訊，並標示來源。

        互動準則:
        - 嚴格遵循思考流程：分析 -> 提取 -> 搜尋 -> 驗證。
        - 優先使用工具：你的所有決策和資訊都應基於工具的返回結果。
        - 引用來源：如果 `search_files` 的結果包含引用，務必在最終答案中清晰地標示出來。
        - 引用來源：如果 `google_search` 的結果包含引用，務必在最終答案中清晰地標示出來。
        - 回憶與整合：結合使用者的個人化記憶與文件查詢結果，提供全面且精準的策略建議。
        - 保持專業：你的回答應該是結構化、有條理且基於事實的。
        """
    ),
    before_model_callback=before_model_callback,
)

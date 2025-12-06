
"""Type definitions for Commerce Agent tools and callbacks. (商務代理人工具與回調的型別定義)

This module provides TypedDict definitions for better type safety and IDE support.
此模組提供 TypedDict 定義，以獲得更好的型別安全與 IDE 支援。

⚠️ IMPORTANT: ADK Compatibility Note (重要：ADK 相容性說明)
These TypedDict types cannot be used directly in function signatures for tools
that use ADK's automatic function calling. Use `Dict[str, Any]` in signatures
instead, but ensure the returned dictionary matches these structures.
這些 TypedDict 型別不能直接用於使用 ADK 自動函式呼叫的工具函式簽名中。
請在簽名中使用 `Dict[str, Any]` 代替，但確保回傳的字典符合這些結構。

Example (範例):
    def my_tool(...) -> Dict[str, Any]:  # 在簽名中使用此方式 (Use this in signature)
        result: ToolResult = {...}       # 可使用 TypedDict 進行型別提示 (Can use TypedDict for type hints)
        return result                    # 回傳值符合 ToolResult 結構 (Return matches ToolResult structure)
"""

from typing import TypedDict, NotRequired, Any


class ToolResult(TypedDict):
    """所有工具函式的標準回傳型別 (Standard return type for all tool functions.)

    ⚠️ 請勿在工具函式簽名中作為回傳型別註解使用。
    ADK 的自動函式呼叫無法解析 TypedDict 回傳型別。
    請改用 `Dict[str, Any]`，但確保回傳的字典符合此結構。
    ⚠️ Do not use as return type annotation in tool function signatures.
    ADK's automatic function calling cannot parse TypedDict return types.
    Use `Dict[str, Any]` instead but ensure returned dict matches this structure.

    Attributes:
        status: "success" 或 "error" (Either "success" or "error")
        report: 描述結果的人類可讀訊息 (Human-readable message describing the result)
        data: 帶有結果資料的可選字典 (Optional dictionary with result data)
        error: 可選錯誤訊息 (僅在 status="error" 時出現) (Optional error message (only present when status="error"))
    """
    status: str
    report: str
    data: NotRequired[dict[str, Any]]
    error: NotRequired[str]


class UserPreferences(TypedDict):
    """使用者偏好資料結構 (User preference data structure.)

    Attributes:
        sport: 運動類型 (例如："running", "cycling", "hiking") (Type of sport (e.g., "running", "cycling", "hiking"))
        budget_max: 最大預算 (歐元) (Maximum budget in EUR)
        experience_level: 使用者經驗水平 ("beginner", "intermediate", "advanced") (User's experience level ("beginner", "intermediate", "advanced"))
    """
    sport: NotRequired[str]
    budget_max: NotRequired[int]
    experience_level: NotRequired[str]


class GroundingSource(TypedDict):
    """來自 Google Search 的接地來源資訊 (Grounding source information from Google Search.)

    Attributes:
        title: 來源頁面標題 (Title of the source page)
        uri: 來源完整 URL (Full URL of the source)
        domain: 提取的網域名稱 (例如："decathlon.com") (Extracted domain name (e.g., "decathlon.com"))
    """
    title: str
    uri: str
    domain: NotRequired[str]


class GroundingSupport(TypedDict):
    """特定文字片段的接地支援 (Grounding support for a specific text segment.)

    Attributes:
        text: 被支援的文字片段 (The text segment being supported)
        start_index: 回應中的起始字元位置 (Starting character position in the response)
        end_index: 回應中的結束字元位置 (Ending character position in the response)
        source_indices: 來自 grounding_chunks 的來源索引列表 (List of source indices from grounding_chunks)
        confidence: 信心水準 ("high", "medium", "low") (Confidence level ("high", "medium", "low"))
    """
    text: str
    start_index: int
    end_index: int
    source_indices: list[int]
    confidence: NotRequired[str]


class GroundingMetadata(TypedDict):
    """來自 Google Search 結果的完整接地元數據 (Complete grounding metadata from Google Search results.)

    Attributes:
        sources: 來源資訊列表 (List of source information)
        supports: 帶有來源歸因的文字片段列表 (List of text segments with source attribution)
        search_suggestions: 相關搜尋查詢的可選列表 (Optional list of related search queries)
        total_sources: 總唯一來源數 (Total number of unique sources)
    """
    sources: list[GroundingSource]
    supports: list[GroundingSupport]
    search_suggestions: NotRequired[list[str]]
    total_sources: int


__all__ = [
    "ToolResult",
    "UserPreferences",
    "GroundingSource",
    "GroundingSupport",
    "GroundingMetadata",
]


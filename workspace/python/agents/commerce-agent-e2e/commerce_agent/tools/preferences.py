
"""簡單的使用者偏好管理。"""

from typing import Dict, Any
from google.adk.tools import ToolContext
# 為了與 ADK 自動函式呼叫保持相容性
# 注意：ToolResult TypedDict 可供參考，但為了維持與 ADK 自動函式呼叫的相容性，未在簽名中使用
from ..types import ToolResult


def save_preferences(
    sport: str,
    budget_max: int,
    experience_level: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """為個人化推薦儲存使用者偏好。

    Args:
        sport: 運動類型 (例如："running", "cycling", "hiking")
        budget_max: 最高預算 (歐元)
        experience_level: 使用者的經驗水平 ("beginner", "intermediate", "advanced")
        tool_context: ADK 工具上下文

    Returns:
        包含狀態和報告的字典。
    """
    try:
        # 儲存至使用者狀態 (可跨對話持久化)
        # ADK v1.17+ 直接使用 tool_context.state，而非 invocation_context
        tool_context.state["user:pref_sport"] = sport
        tool_context.state["user:pref_budget"] = budget_max
        tool_context.state["user:pref_experience"] = experience_level

        return {
            "status": "success",
            "report": f"✓ 偏好已儲存：{sport}，最高預算 €{budget_max}，經驗水平 {experience_level}",
            "data": {
                "sport": sport,
                "budget_max": budget_max,
                "experience_level": experience_level
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "report": f"儲存偏好失敗：{str(e)}",
            "error": str(e)
        }


def get_preferences(tool_context: ToolContext) -> Dict[str, Any]:
    """檢索已儲存的使用者偏好。

    Args:
        tool_context: ADK 工具上下文

    Returns:
        包含狀態、報告和偏好資料的字典。
    """
    try:
        # ADK v1.17+ 直接使用 tool_context.state，而非 invocation_context
        state = tool_context.state

        prefs = {
            "sport": state.get("user:pref_sport"),
            "budget_max": state.get("user:pref_budget"),
            "experience_level": state.get("user:pref_experience")
        }

        # 過濾掉值為 None 的項目
        prefs = {k: v for k, v in prefs.items() if v is not None}

        if not prefs:
            return {
                "status": "success",
                "report": "尚未儲存任何偏好",
                "data": {}
            }

        return {
            "status": "success",
            "report": f"已檢索偏好：{', '.join(f'{k}={v}' for k, v in prefs.items())}",
            "data": prefs
        }
    except Exception as e:
        return {
            "status": "error",
            "report": f"檢索偏好失敗：{str(e)}",
            "error": str(e),
            "data": {}
        }


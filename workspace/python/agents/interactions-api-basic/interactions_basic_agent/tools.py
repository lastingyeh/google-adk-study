"""
Interactions API 範例的工具定義 (Tool definitions)。

本模組提供與 Interactions API 函數呼叫功能相容的工具架構 (schemas)。
"""

from typing import Dict, Any, List


def get_weather_tool() -> Dict[str, Any]:
    """
    取得天氣工具定義。

    Returns:
        Interactions API 格式的工具定義字典。
    """
    return {
        "type": "function",
        "name": "get_weather",
        "description": "取得指定地點的當前天氣。",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "城市與州/國家，例如 'San Francisco, CA' 或 'Paris, France'"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "溫度單位偏好"
                }
            },
            "required": ["location"]
        }
    }


def calculate_tool() -> Dict[str, Any]:
    """
    取得計算機工具定義。

    Returns:
        數學運算的工具定義字典。
    """
    return {
        "type": "function",
        "name": "calculate",
        "description": "執行數學運算。用於算術、百分比和基礎數學。",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "要評估的數學表達式，例如 '2 + 2' 或 '15% of 200'"
                }
            },
            "required": ["expression"]
        }
    }


def search_database_tool() -> Dict[str, Any]:
    """
    取得資料庫搜尋工具定義。

    Returns:
        搜尋資料庫的工具定義。
    """
    return {
        "type": "function",
        "name": "search_database",
        "description": "在資料庫中搜尋符合查詢的記錄。",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜尋查詢字串"
                },
                "table": {
                    "type": "string",
                    "description": "要搜尋的資料表",
                    "enum": ["users", "products", "orders"]
                },
                "limit": {
                    "type": "integer",
                    "description": "回傳的最大結果數量",
                    "default": 10
                }
            },
            "required": ["query", "table"]
        }
    }


def schedule_meeting_tool() -> Dict[str, Any]:
    """
    取得會議安排工具定義。

    Returns:
        安排會議的工具定義。
    """
    return {
        "type": "function",
        "name": "schedule_meeting",
        "description": "在指定的時間和日期安排與特定與會者的會議。",
        "parameters": {
            "type": "object",
            "properties": {
                "attendees": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "與會者電子郵件列表"
                },
                "date": {
                    "type": "string",
                    "description": "會議日期 (YYYY-MM-DD 格式)"
                },
                "time": {
                    "type": "string",
                    "description": "會議時間 (HH:MM 格式，24小時制)"
                },
                "topic": {
                    "type": "string",
                    "description": "會議主題"
                },
                "duration_minutes": {
                    "type": "integer",
                    "description": "會議持續時間 (分鐘)",
                    "default": 60
                }
            },
            "required": ["attendees", "date", "time", "topic"]
        }
    }


# Collection of all available tools
AVAILABLE_TOOLS: List[Dict[str, Any]] = [
    get_weather_tool(),
    calculate_tool(),
    search_database_tool(),
    schedule_meeting_tool(),
]


# Mock implementations for demo purposes
def execute_tool(name: str, arguments: Dict[str, Any]) -> str:
    """
    使用給定的參數執行工具。

    這是用於展示目的的模擬實作 (Mock implementation)。
    在生產環境中，您將連接到真實的服務。

    Args:
        name: 工具名稱。
        arguments: 工具參數。

    Returns:
        工具執行的字串結果。
    """
    if name == "get_weather":
        location = arguments.get("location", "Unknown")
        unit = arguments.get("unit", "celsius")
        temp = "22°C" if unit == "celsius" else "72°F"
        return f"{location} 的天氣晴朗，氣溫為 {temp}。"

    elif name == "calculate":
        expression = arguments.get("expression", "0")
        # Simple evaluation for demo - in production, use a proper parser
        try:
            # Handle percentages
            if "%" in expression and "of" in expression.lower():
                parts = expression.lower().replace("%", "").split("of")
                percent = float(parts[0].strip())
                value = float(parts[1].strip())
                result = (percent / 100) * value
            else:
                # WARNING: eval is unsafe for production!
                result = eval(expression)
            return f"計算結果： {result}"
        except Exception as e:
            return f"計算錯誤： {e}"

    elif name == "search_database":
        query = arguments.get("query", "")
        table = arguments.get("table", "")
        limit = arguments.get("limit", 10)
        return f"在 '{table}' 中找到 3 筆符合 '{query}' 的結果 (上限： {limit})"

    elif name == "schedule_meeting":
        topic = arguments.get("topic", "Meeting")
        date = arguments.get("date", "TBD")
        time = arguments.get("time", "TBD")
        attendees = arguments.get("attendees", [])
        return f"會議 '{topic}' 已安排於 {date} {time}，共有 {len(attendees)} 位與會者。"

    else:
        return f"未知工具： {name}"

"""
=== 重點摘要 ===
- **核心概念**：定義與 OpenAI/Gemini Function Calling 相容的 JSON Schema 工具描述。
- **關鍵技術**：
  - **JSON Schema**：標準化的數據交換格式，用於描述函數參數。
  - **模擬實作 (Mocking)**：在不依賴外部服務的情況下驗證工具邏輯。
- **重要結論**：清晰的工具描述對於模型正確理解與使用工具至關重要。
- **行動項目**：
  - 根據實際業務需求擴充更多工具定義。
  - 將模擬的 `execute_tool` 替換為實際的 API 呼叫。
"""

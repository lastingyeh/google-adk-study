"""
ADK Interactions Agent 的工具定義

本模組包含 ADK 代理使用的工具函式。
工具遵循 ADK 慣例，回傳包含 status (狀態)、report (報告) 和 data (資料) 欄位的結構化字典。
"""

import random
from typing import Dict, Any


def get_current_weather(location: str, units: str = "celsius") -> Dict[str, Any]:
    """
    取得特定地點的目前天氣。

    這是一個模擬的天氣工具，回傳看似真實的天氣資料。
    在正式環境中，你應該整合真實的天氣 API，如 OpenWeatherMap 或 WeatherAPI。

    Args:
        location: 要查詢天氣的地點 (例如："Tokyo, Japan")。
        units: 溫度單位 - "celsius" (攝氏) 或 "fahrenheit" (華氏)。

    Returns:
        包含天氣資訊的字典：
        - status: "success" 或 "error"
        - report: 人類可讀的摘要
        - temperature: 目前溫度
        - humidity: 濕度百分比
        - conditions: 天氣狀況
        - wind_speed: 風速
        - location: 解析後的地點名稱

    Example:
        >>> result = get_current_weather("Tokyo, Japan")
        >>> print(result["report"])
        "Weather in Tokyo, Japan: 22°C, Partly Cloudy, Humidity: 65%"
    """
    try:
        # 模擬天氣資料 (正式環境請替換為真實 API)
        temperature_c = random.randint(5, 35)
        humidity = random.randint(30, 90)

        conditions_list = [
            "Sunny",
            "Partly Cloudy",
            "Cloudy",
            "Light Rain",
            "Clear",
            "Overcast",
            "Scattered Clouds",
        ]
        conditions = random.choice(conditions_list)
        wind_speed = random.randint(5, 30)

        # 轉換溫度單位
        if units.lower() == "fahrenheit":
            temperature = int(temperature_c * 9 / 5 + 32)
            temp_unit = "°F"
        else:
            temperature = temperature_c
            temp_unit = "°C"

        return {
            "status": "success",
            "report": f"Weather in {location}: {temperature}{temp_unit}, {conditions}, Humidity: {humidity}%",
            "temperature": temperature,
            "temperature_unit": temp_unit,
            "humidity": humidity,
            "conditions": conditions,
            "wind_speed": wind_speed,
            "wind_unit": "km/h",
            "location": location,
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "report": f"Failed to get weather for {location}: {str(e)}",
        }


def calculate_expression(expression: str) -> Dict[str, Any]:
    """
    安全地計算數學表達式。

    支援：
    - 基本運算：+, -, *, /, **, //
    - 括號分組
    - 百分比計算 ("15% of 250")
    - 常見數學操作

    Args:
        expression: 要評估的數學表達式。

    Returns:
        包含計算結果的字典：
        - status: "success" 或 "error"
        - report: 人類可讀的結果
        - result: 數值結果
        - expression: 原始表達式

    Example:
        >>> result = calculate_expression("15% of 250")
        >>> print(result["result"])
        37.5
    """
    try:
        # 處理百分比表示法
        expr = expression.lower().strip()

        # 解析 "X% of Y" 格式
        if "% of" in expr:
            parts = expr.split("% of")
            if len(parts) == 2:
                percent = float(parts[0].strip())
                value = float(parts[1].strip())
                result = (percent / 100) * value
                return {
                    "status": "success",
                    "report": f"{expression} = {result}",
                    "result": result,
                    "expression": expression,
                }

        # 處理簡單百分比
        if expr.endswith("%"):
            number = float(expr[:-1].strip())
            result = number / 100
            return {
                "status": "success",
                "report": f"{expression} = {result}",
                "result": result,
                "expression": expression,
            }

        # 安全評估：僅允許特定字元
        allowed_chars = set("0123456789+-*/(). ")
        sanitized = "".join(c for c in expression if c in allowed_chars)

        if not sanitized:
            return {
                "status": "error",
                "error": "Invalid expression",
                "report": f"Could not parse expression: {expression}",
            }

        # 安全地評估表達式
        result = eval(sanitized, {"__builtins__": {}}, {})

        return {
            "status": "success",
            "report": f"{expression} = {result}",
            "result": result,
            "expression": expression,
        }

    except ZeroDivisionError:
        return {
            "status": "error",
            "error": "Division by zero",
            "report": "Cannot divide by zero",
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "report": f"Failed to calculate: {str(e)}",
        }


def search_knowledge_base(query: str, max_results: int = 3) -> Dict[str, Any]:
    """
    在知識庫中搜尋資訊。

    這是一個模擬的知識庫搜尋。在正式環境中，你應該整合真實的搜尋後端，
    如 Elasticsearch, Pinecone, 或自訂向量資料庫。

    Args:
        query: 搜尋查詢字串。
        max_results: 要返回的最大結果數量。

    Returns:
        包含搜尋結果的字典：
        - status: "success" 或 "error"
        - report: 人類可讀的摘要
        - results: 匹配的文件列表
        - query: 原始查詢
        - total_results: 找到的結果數量

    Example:
        >>> result = search_knowledge_base("quantum computing")
        >>> for doc in result["results"]:
        ...     print(doc["title"])
    """
    try:
        # 模擬知識庫條目
        knowledge_base = [
            {
                "id": "kb001",
                "title": "Introduction to Quantum Computing",
                "snippet": "Quantum computing harnesses quantum mechanics to process information in fundamentally new ways, using qubits instead of classical bits.",
                "relevance": 0.95,
            },
            {
                "id": "kb002",
                "title": "Machine Learning Fundamentals",
                "snippet": "Machine learning is a subset of AI that enables systems to learn and improve from experience without being explicitly programmed.",
                "relevance": 0.88,
            },
            {
                "id": "kb003",
                "title": "Cloud Computing Architecture",
                "snippet": "Cloud computing delivers computing services over the internet, offering scalable resources on demand.",
                "relevance": 0.82,
            },
            {
                "id": "kb004",
                "title": "Natural Language Processing",
                "snippet": "NLP enables computers to understand, interpret, and generate human language, powering applications from chatbots to translation.",
                "relevance": 0.85,
            },
            {
                "id": "kb005",
                "title": "Deep Learning and Neural Networks",
                "snippet": "Deep learning uses multi-layer neural networks to learn complex patterns in data, enabling breakthroughs in image and speech recognition.",
                "relevance": 0.91,
            },
            {
                "id": "kb006",
                "title": "Agent-Based AI Systems",
                "snippet": "AI agents are autonomous systems that perceive their environment and take actions to achieve specific goals using reasoning and tools.",
                "relevance": 0.87,
            },
        ]

        # 簡單關鍵字匹配 (正式環境請使用向量搜尋)
        query_terms = set(query.lower().split())
        scored_results = []

        for entry in knowledge_base:
            title_terms = set(entry["title"].lower().split())
            snippet_terms = set(entry["snippet"].lower().split())
            all_terms = title_terms | snippet_terms

            # 根據詞彙重疊計算關聯性
            overlap = len(query_terms & all_terms)
            if overlap > 0:
                score = overlap * entry["relevance"]
                scored_results.append((score, entry))

        # 依分數排序並取前幾名
        scored_results.sort(key=lambda x: x[0], reverse=True)
        top_results = [entry for _, entry in scored_results[:max_results]]

        # 如果沒有直接匹配，返回一些預設結果 (模擬行為)
        if not top_results:
            top_results = knowledge_base[:max_results]

        return {
            "status": "success",
            "report": f"Found {len(top_results)} results for '{query}'",
            "results": top_results,
            "query": query,
            "total_results": len(top_results),
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "report": f"Search failed: {str(e)}",
        }


# 額外的實用工具

def format_response(data: Dict[str, Any], style: str = "markdown") -> str:
    """
    格式化工具回傳資料以供顯示。

    Args:
        data: 工具回傳的字典。
        style: 輸出格式 - "markdown", "plain", 或 "json"。

    Returns:
        格式化後的字串表示。
    """
    if style == "json":
        import json
        return json.dumps(data, indent=2)

    if style == "markdown":
        lines = []
        if "report" in data:
            lines.append(f"**{data['report']}**\n")
        for key, value in data.items():
            if key not in ("status", "report", "error"):
                if isinstance(value, list):
                    lines.append(f"- **{key}**: {len(value)} items")
                else:
                    lines.append(f"- **{key}**: {value}")
        return "\n".join(lines)

    # 純文字
    return data.get("report", str(data))

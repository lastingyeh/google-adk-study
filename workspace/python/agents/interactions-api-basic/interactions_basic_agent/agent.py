"""
Interactions API 基礎代理 (Basic Agent) 實作

本模組展示 Google Interactions API 的核心功能：
- 基礎文字互動 (Basic text interactions)
- 伺服器端狀態管理 (Server-side state management)
- 串流回應 (Streaming responses)
- 函數呼叫 (Function calling)

需求：
- google-genai >= 1.55.0
- 已設定 GOOGLE_API_KEY 環境變數
"""

import os
from typing import Optional, Generator, Any, Dict, List

# 匯入 google.genai - Interactions API 於 1.55.0+ 版本提供
try:
    from google import genai
    from google.genai import types
except ImportError:
    raise ImportError(
        "Interactions API 需要 google-genai >= 1.55.0。"
        "安裝指令：pip install 'google-genai>=1.55.0'"
    )

from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# Interactions API 支援的模型
SUPPORTED_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-pro",
    "gemini-3-pro-preview",
]

# 預設模型
DEFAULT_MODEL = "gemini-2.5-flash"


def get_client(api_key: Optional[str] = None) -> genai.Client:
    """
    建立 Interactions API 的 Google GenAI 客戶端。

    Args:
        api_key: 可選的 API 金鑰。若未提供，則使用 GOOGLE_API_KEY 環境變數。

    Returns:
        設定完成的 genai.Client 實例。

    Raises:
        ValueError: 若未提供 API 金鑰。
    """
    key = api_key or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise ValueError(
            "必須設定 GOOGLE_API_KEY 環境變數。"
            "請至此處取得您的金鑰： https://aistudio.google.com/apikey"
        )
    return genai.Client(api_key=key)


def create_basic_interaction(
    prompt: str,
    model: str = DEFAULT_MODEL,
    client: Optional[genai.Client] = None,
) -> Dict[str, Any]:
    """
    與 Gemini 模型建立基礎互動。

    這是使用 Interactions API 最簡單的形式 -
    單次的請求-回應互動。

    Args:
        prompt: 發送給模型的文字提示 (prompt)。
        model: 模型識別碼 (預設：gemini-2.5-flash)。
        client: 可選的預先設定客戶端。

    Returns:
        包含互動詳細資訊的字典：
        - id: 唯一的互動識別碼
        - text: 模型的回應文字
        - status: 互動狀態
        - usage: Token 使用量資訊

    Example:
        >>> result = create_basic_interaction("說個笑話")
        >>> print(result["text"])
    """
    if client is None:
        client = get_client()

    # 建立互動請求
    interaction = client.interactions.create(
        model=model,
        input=prompt
    )

    return {
        "id": interaction.id,
        "text": interaction.outputs[-1].text if interaction.outputs else "",
        "status": interaction.status,
        "usage": interaction.usage if hasattr(interaction, "usage") else None,
    }


def create_stateful_conversation(
    messages: List[str],
    model: str = DEFAULT_MODEL,
    client: Optional[genai.Client] = None,
) -> List[Dict[str, Any]]:
    """
    建立具備伺服器端狀態管理的多輪對話。

    這展示了 Interactions API 的關鍵優勢 -
    伺服器管理對話歷史記錄，減少 Token 成本
    並降低客戶端複雜度。

    Args:
        messages: 依序發送的使用者訊息列表。
        model: 模型識別碼。
        client: 可選的預先設定客戶端。

    Returns:
        互動結果列表，每個包含：
        - id: 互動 ID
        - text: 模型回應
        - previous_id: 前次互動的 ID (若有)

    Example:
        >>> results = create_stateful_conversation([
        ...     "我叫 Alex",
        ...     "我的名字是什麼？"
        ... ])
        >>> print(results[-1]["text"])  # "你的名字是 Alex"
    """
    if client is None:
        client = get_client()

    results = []
    previous_id = None

    for message in messages:
        kwargs = {
            "model": model,
            "input": message,
        }

        # 加入前次互動 ID 以延續上下文
        # 這是狀態管理的關鍵：只需傳遞 ID，無需傳遞完整歷史
        if previous_id:
            kwargs["previous_interaction_id"] = previous_id

        interaction = client.interactions.create(**kwargs)

        result = {
            "id": interaction.id,
            "text": interaction.outputs[-1].text if interaction.outputs else "",
            "previous_id": previous_id,
        }
        results.append(result)

        # 更新 ID 供下一次迭代使用
        previous_id = interaction.id

    return results


def create_streaming_interaction(
    prompt: str,
    model: str = DEFAULT_MODEL,
    client: Optional[genai.Client] = None,
) -> Generator[str, None, None]:
    """
    建立即時回應輸出的串流互動。

    串流適用於：
    - 向使用者顯示進度
    - 減少感知的延遲
    - 逐步處理長回應

    Args:
        prompt: 文字提示。
        model: 模型識別碼。
        client: 可選的預先設定客戶端。

    Yields:
        從模型接收到的文字片段 (chunks)。

    Example:
        >>> for chunk in create_streaming_interaction("解釋 AI"):
        ...     print(chunk, end="", flush=True)
    """
    if client is None:
        client = get_client()

    # 開啟 stream=True 進行串流
    stream = client.interactions.create(
        model=model,
        input=prompt,
        stream=True
    )

    for chunk in stream:
        if chunk.event_type == "content.delta":
            if hasattr(chunk.delta, "text") and chunk.delta.text:
                yield chunk.delta.text


def create_function_calling_interaction(
    prompt: str,
    tools: List[Dict[str, Any]],
    model: str = DEFAULT_MODEL,
    client: Optional[genai.Client] = None,
    tool_executor: Optional[callable] = None,
) -> Dict[str, Any]:
    """
    建立具備函數呼叫 (Function Calling) 能力的互動。

    Interactions API 支援精密的工具使用：
    - 自定義函數定義
    - 內建工具 (google_search, code_execution)
    - 遠端 MCP 伺服器

    Args:
        prompt: 使用者的請求。
        tools: 工具定義列表。
        model: 模型識別碼。
        client: 可選的預先設定客戶端。
        tool_executor: 可選的工具執行函數。
                      應接受 (name, arguments) 並回傳結果。

    Returns:
        包含以下內容的字典：
        - id: 互動 ID
        - text: 最終回應文字
        - tool_calls: 已執行的工具呼叫列表
        - tool_results: 工具執行結果 (若有提供執行器)

    Example:
        >>> tools = [get_weather_tool()]
        >>> result = create_function_calling_interaction(
        ...     "巴黎的天氣如何？",
        ...     tools=tools,
        ...     tool_executor=my_weather_function
        ... )
    """
    if client is None:
        client = get_client()

    # 帶有工具的初始互動
    interaction = client.interactions.create(
        model=model,
        input=prompt,
        tools=tools
    )

    result = {
        "id": interaction.id,
        "text": "",
        "tool_calls": [],
        "tool_results": [],
    }

    # 處理輸出
    for output in interaction.outputs:
        if output.type == "function_call":
            tool_call = {
                "name": output.name,
                "arguments": output.arguments,
                "call_id": output.id,
            }
            result["tool_calls"].append(tool_call)

            # 若有提供執行器，則執行工具
            if tool_executor:
                tool_result = tool_executor(output.name, output.arguments)
                result["tool_results"].append(tool_result)

                # 將結果送回模型
                follow_up = client.interactions.create(
                    model=model,
                    previous_interaction_id=interaction.id,
                    input=[{
                        "type": "function_result",
                        "name": output.name,
                        "call_id": output.id,
                        "result": str(tool_result)
                    }]
                )

                # 更新為最終回應
                if follow_up.outputs:
                    result["text"] = follow_up.outputs[-1].text
                    result["id"] = follow_up.id

        elif output.type == "text":
            result["text"] = output.text

    return result


def create_interaction_with_builtin_tools(
    prompt: str,
    tool_type: str = "google_search",
    model: str = DEFAULT_MODEL,
    client: Optional[genai.Client] = None,
) -> Dict[str, Any]:
    """
    使用內建工具建立互動。

    可用的內建工具：
    - google_search: 搜尋網路獲取最新資訊
    - code_execution: 執行 Python 程式碼
    - url_context: 讀取並摘要網頁

    Args:
        prompt: 使用者的請求。
        tool_type: "google_search", "code_execution", "url_context" 其中之一。
        model: 模型識別碼。
        client: 可選的預先設定客戶端。

    Returns:
        互動結果字典。

    Example:
        >>> result = create_interaction_with_builtin_tools(
        ...     "誰贏得了 2024 年超級盃？",
        ...     tool_type="google_search"
        ... )
    """
    if client is None:
        client = get_client()

    valid_tools = ["google_search", "code_execution", "url_context"]
    if tool_type not in valid_tools:
        raise ValueError(f"tool_type 必須是 {valid_tools} 其中之一")

    interaction = client.interactions.create(
        model=model,
        input=prompt,
        tools=[{"type": tool_type}]
    )

    # 提取文字輸出 (過濾掉特定於工具的輸出)
    text_output = next(
        (o for o in interaction.outputs if o.type == "text"),
        None
    )

    return {
        "id": interaction.id,
        "text": text_output.text if text_output else "",
        "status": interaction.status,
        "outputs": [
            {"type": o.type, "content": getattr(o, "text", str(o))}
            for o in interaction.outputs
        ],
    }

"""
=== 重點摘要 ===
- **核心概念**：Interactions API 提供了一種簡化、以互動為中心的開發模式。
- **關鍵技術**：
  - **狀態管理**：透過 `previous_interaction_id` 在伺服器端維護上下文，無需客戶端傳遞完整歷史。
  - **串流回應**：支援即時輸出，提升使用者體驗。
  - **函數呼叫**：整合外部工具與函數，擴展模型能力。
  - **內建工具**：直接支援 Google Search 與 Code Execution。
- **重要結論**：Interactions API 顯著降低了開發對話式 AI 應用的複雜度，特別是在狀態管理與工具整合方面。
- **行動項目**：
  - 確保安裝正確版本的 `google-genai` 套件。
  - 在實際應用中實作具體的 `tool_executor` 邏輯。
"""

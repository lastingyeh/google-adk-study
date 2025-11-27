# 教學 28: 透過 LiteLLM 使用其他 LLM
# Multi-LLM Agent，支援 OpenAI, Claude, Ollama 等多種模型

from __future__ import annotations

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import FunctionTool


def calculate_square(number: int) -> int:
    """
    計算一個數字的平方。

    Args:
        number: 要計算平方的數字

    Returns:
        輸入數字的平方值
    """
    return number ** 2


def get_weather(city: str) -> dict:
    """
    取得指定城市目前的天氣 (模擬實作)。

    Args:
        city: 城市名稱

    Returns:
        包含天氣資訊的字典
    """
    # 在實際應用中，這裡會呼叫一個真正的天氣 API
    return {
        'city': city,
        'temperature': 22,  # 溫度 (攝氏)
        'condition': '晴天',
        'humidity': 45  # 濕度 (%)
    }


def analyze_sentiment(text: str) -> dict:
    """
    分析文字的情緒 (模擬實作)。

    Args:
        text: 要分析的文字

    Returns:
        包含情緒分析結果的字典
    """
    # 在實際應用中，應使用實際的情緒分析服務
    return {
        'sentiment': 'positive',  # 情緒 (正面)
        'confidence': 0.85,  # 信賴度
        'key_phrases': ['exciting', 'innovative', 'breakthrough']  # 關鍵詞
    }


# 預設 agent：透過 LiteLLM 使用 OpenAI GPT-4o-mini
# 對於大多數任務來說，這是一個具成本效益的選擇
# 注意：使用者可以透過更改 model 參數輕鬆切換到其他模型

root_agent = Agent(
    name="multi_llm_agent",
    model=LiteLlm(model='openai/gpt-4o-mini'),  # 透過 LiteLLM 使用 OpenAI GPT-4o-mini
    description=(
        "支援 OpenAI, Claude, Ollama 等多種模型的 Multi-LLM agent，透過 LiteLLM 實現。"
        "此 agent 可以針對不同任務使用不同的 LLM 供應商。"
    ),
    instruction="""
    你是一個透過 LiteLLM 由多個 LLM 供應商驅動的多功能 AI 助理。
    你可以存取多種工具，並能協助處理以下任務：
    - 數學計算 (calculate_square)
    - 天氣資訊 (get_weather)
    - 情緒分析 (analyze_sentiment)

    請保持樂於助人、準確的態度，並在需要時使用適當的工具。
    請清楚地解釋你的推理過程並提供詳細的回應。
    """.strip(),
    tools=[
        FunctionTool(calculate_square),
        FunctionTool(get_weather),
        FunctionTool(analyze_sentiment)
    ]
)


# 其他 agent 設定 (可以單獨匯入並使用)：

# OpenAI GPT-4o-mini (具成本效益的版本) - 用於一般任務
gpt4o_agent = Agent(
    name="gpt4o_mini_agent",
    model=LiteLlm(model='openai/gpt-4o-mini'),
    description="由 OpenAI GPT-4o-mini 驅動的 agent，用於高效處理一般任務",
    instruction="你是一個使用 GPT-4o-mini 的高效助理，專為具成本效益的 AI 互動而設計。",
    tools=[
        FunctionTool(calculate_square),
        FunctionTool(get_weather),
        FunctionTool(analyze_sentiment)
    ]
)


# Anthropic Claude 3.7 Sonnet - 用於長篇內容與分析
claude_agent = Agent(
    name="claude_agent",
    model=LiteLlm(model='anthropic/claude-3-7-sonnet-20250219'),
    description="由 Claude 3.7 Sonnet 驅動的 agent，用於詳細分析",
    instruction="""
    你是一個由 Claude 3.7 Sonnet 驅動，深思熟慮的分析師。
    你擅長：
    - 複雜推理
    - 長篇內容
    - 倫理考量
    - 遵循詳細指令
    """.strip(),
    tools=[
        FunctionTool(calculate_square),
        FunctionTool(get_weather),
        FunctionTool(analyze_sentiment)
    ]
)


# Ollama Granite 4 - 使用 IBM Granite 模型進行本地、注重隱私的操作
# 注意：需要先在本地安裝並執行 Ollama
# 請使用 'ollama_chat' 前綴，而不是 'ollama'，以確保函式呼叫的正常支援
ollama_agent = Agent(
    name="ollama_agent",
    model=LiteLlm(model='ollama_chat/granite4:latest'),  # 更新為使用 Granite 4 模型
    description="透過 Ollama 在本地端執行 Granite 4 的 agent，以保護隱私",
    instruction="你是一個由 IBM Granite 4 驅動的本地助理。所有處理都在本機裝置上進行。",
    tools=[
        FunctionTool(calculate_square),
        FunctionTool(get_weather),
        FunctionTool(analyze_sentiment)
    ]
)

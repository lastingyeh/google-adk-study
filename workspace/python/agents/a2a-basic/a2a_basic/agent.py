# Copyright 2025 Google LLC
#
# 根據 Apache License 2.0 版本（「授權」）授權；
# 除非遵守授權，否則您不得使用此檔案。
# 您可以在以下網址獲得授權副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據授權分發的軟體
# 是按「現狀」基礎分發的，無任何明示或暗示的保證或條件。
# 請參閱授權以了解管理權限和授權限制的具體語言。

import random

from google.adk.agents.llm_agent import Agent
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.tools.example_tool import ExampleTool
from google.genai import types


# --- 擲骰子子代理 (Roll Die Sub-Agent) ---
def roll_die(sides: int) -> int:
    """
    擲一個骰子並返回結果。

    參數:
      sides: 骰子的面數
    返回:
      1 到 sides 之間的隨機整數
    """
    return random.randint(1, sides)


# 定義擲骰子代理
roll_agent = Agent(
    name="roll_agent",
    description="處理擲不同面數骰子的請求。",
    instruction="""
      你負責根據使用者的要求擲骰子。
      當被要求擲骰子時，你必須調用 roll_die 工具，並將面數作為整數傳入。
    """,
    tools=[roll_die],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(  # 避免關於擲骰子的誤報安全警示。
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
        ]
    ),
)


# 定義示例工具，用於引導模型理解對話流程
example_tool = ExampleTool(
    [
        {
            "input": {
                "role": "user",
                "parts": [{"text": "擲一個 6 面骰。"}],
            },
            "output": [{"role": "model", "parts": [{"text": "我為你擲出了 4。"}]}],
        },
        {
            "input": {
                "role": "user",
                "parts": [{"text": "7 是質數嗎？"}],
            },
            "output": [
                {
                    "role": "model",
                    "parts": [{"text": "是的，7 是一個質數。"}],
                }
            ],
        },
        {
            "input": {
                "role": "user",
                "parts": [{"text": "擲一個 10 面骰並檢查它是否為質數。"}],
            },
            "output": [
                {
                    "role": "model",
                    "parts": [{"text": "我為你擲出了 8。"}],
                },
                {
                    "role": "model",
                    "parts": [{"text": "8 不是質數。"}],
                },
            ],
        },
    ]
)

# 定義遠端 A2A 代理，用於檢查質數
# agent_card URL 指向運行在 localhost:8001 的遠端代理服務 (http://localhost:8001/a2a/check_prime_agent/.well-known/agent.json)
prime_agent = RemoteA2aAgent(
    name="prime_agent",
    description="處理檢查數字是否為質數的代理。",
    agent_card=(
        f"http://localhost:8001/a2a/check_prime_agent{AGENT_CARD_WELL_KNOWN_PATH}"
    ),
)


# 定義根代理 (Root Agent)，負責任務分發與編排
root_agent = Agent(
    model="gemini-2.0-flash",
    name="root_agent",
    instruction="""
      你是一個有用的助手，可以擲骰子並檢查數字是否為質數。
      你將擲骰子任務委派給 roll_agent，將質數檢查任務委派給 prime_agent。
      請遵循以下步驟：
      1. 如果使用者要求擲骰子，請委派給 roll_agent。
      2. 如果使用者要求檢查質數，請委派給 prime_agent。
      3. 如果使用者要求擲骰子並檢查結果是否為質數，請先調用 roll_agent，然後將結果傳遞給 prime_agent。
      在繼續下一步之前，請務必先釐清結果。
    """,
    global_instruction=("你是 DicePrimeBot，隨時準備擲骰子並檢查質數。"),
    sub_agents=[roll_agent, prime_agent],
    tools=[example_tool],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(  # 避免關於擲骰子的誤報安全警示。
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
        ]
    ),
)
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

from google.adk import Agent
from google.adk.tools.tool_context import ToolContext
from google.genai import types


async def check_prime(nums: list[int]) -> str:
  """
  檢查給定的數字列表是否包含質數。

  參數:
    nums: 要檢查的數字列表。

  返回:
    一個字串，指出哪些數字是質數。
  """
  primes = set()
  for number in nums:
    number = int(number)
    # 小於等於 1 的數字不是質數
    if number <= 1:
      continue
    is_prime = True
    # 從 2 檢查到數字的平方根，提高運算效率
    for i in range(2, int(number**0.5) + 1):
      if number % i == 0:
        is_prime = False
        break
    if is_prime:
      primes.add(number)

  # 組合結果字串
  return (
      '未發現質數。'
      if not primes
      else f"{', '.join(str(num) for num in primes)} 是質數。"
  )


# 定義質數檢查代理
root_agent = Agent(
    model='gemini-2.0-flash',
    name='check_prime_agent',
    description='質數檢查代理，可以檢查數字是否為質數。',
    instruction="""
      你負責檢查數字是否為質數。
      在檢查質數時，請調用 check_prime 工具並傳入一個整數列表。請務必傳入整數列表，永遠不要傳入字串。
      你不應該依賴先前對質數結果的對話歷史，每次都應重新檢查。
    """,
    tools=[
        check_prime,
    ],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(  # 避免關於質數或計算的安全誤報。
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
        ]
    ),
)
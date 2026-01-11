# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import random

from google.adk import Agent
from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.apps.app import EventsCompactionConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
from google.adk.models.llm_request import LlmRequest
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.plugins.context_filter_plugin import ContextFilterPlugin
from google.adk.plugins.save_files_as_artifacts_plugin import SaveFilesAsArtifactsPlugin
from google.adk.tools import load_artifacts
from google.adk.tools.tool_context import ToolContext
from google.genai import types


def roll_die(sides: int, tool_context: ToolContext) -> int:
  """擲骰子並回傳結果。

  參數:
    sides: 骰子的面數。
    tool_context: 工具上下文，用於存取會話狀態。

  回傳:
    擲出的整數結果。
  """
  result = random.randint(1, sides)
  # 如果狀態中尚未有 'rolls' 紀錄，則初始化為空列表
  if not 'rolls' in tool_context.state:
    tool_context.state['rolls'] = []

  # 將本次結果存入會話狀態中
  tool_context.state['rolls'] = tool_context.state['rolls'] + [result]
  return result


async def check_prime(nums: list[int]) -> str:
  """檢查給定的數字列表是否為質數。

  參數:
    nums: 待檢查的數字列表。

  回傳:
    表示哪些數字是質數的字串。
  """
  primes = set()
  for number in nums:
    number = int(number)
    if number <= 1:
      continue
    is_prime = True
    for i in range(2, int(number**0.5) + 1):
      if number % i == 0:
        is_prime = False
        break
    if is_prime:
      primes.add(number)
  return (
      'No prime numbers found.'
      if not primes
      else f"{', '.join(str(num) for num in primes)} are prime numbers."
  )


root_agent = Agent(
    model='gemini-2.0-flash',
    name='hello_world_agent',
    description=(
        'hello world agent that can roll a dice of 8 sides and check prime'
        ' numbers.'
    ),
    instruction="""
      你負責擲骰子並回答有關擲骰結果的問題。
      你可以擲不同面數的骰子。
      你可以透過並行調用函式來同時使用多個工具。
      你可以討論之前的擲骰紀錄並進行評論。
      當被要求擲骰子時，你必須呼叫 roll_die 工具並傳入面數（整數）。請確保傳入的是整數而非字串。
      你絕對不應該自己猜測或偽造擲骰結果。
      檢查質數時，呼叫 check_prime 工具並傳入整數列表。請確保傳入的是整數列表而非字串。
      在呼叫工具之前，你不應該自行判斷質數。
      當被要求同時擲骰子與檢查質數時，你應遵循以下步驟：
      1. 先呼叫 roll_die 工具。在獲得回傳結果前，不要呼叫 check_prime。
      2. 獲得 roll_die 結果後，呼叫 check_prime 工具並將該結果包含在內。
        2.1 如果使用者要求根據之前的紀錄檢查質數，請確保包含之前的擲骰結果。
      3. 回覆時，必須包含步驟 1 的擲骰結果。
      你應始終執行上述三個步驟。
      不應依賴之前的質數檢查歷史紀錄。
    """,
    tools=[
        roll_die,
        check_prime,
        load_artifacts,
    ],
    # planner=BuiltInPlanner(
    #     thinking_config=types.ThinkingConfig(
    #         include_thoughts=True,
    #     ),
    # ),
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(  # avoid false alarm about rolling dice.
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
        ]
    ),
)


class CountInvocationPlugin(BasePlugin):
  """自定義插件，用於統計代理人與工具的調用次數。"""

  def __init__(self) -> None:
    """初始化計數器。"""
    super().__init__(name='count_invocation')
    self.agent_count: int = 0
    self.tool_count: int = 0
    self.llm_request_count: int = 0

  async def before_agent_callback(
      self, *, agent: BaseAgent, callback_context: CallbackContext
  ) -> None:
    """在代理人運行前計數。"""
    self.agent_count += 1
    print(f'[Plugin] Agent run count: {self.agent_count}')

  async def before_model_callback(
      self, *, callback_context: CallbackContext, llm_request: LlmRequest
  ) -> None:
    """在 LLM 請求前計數。"""
    self.llm_request_count += 1
    print(f'[Plugin] LLM request count: {self.llm_request_count}')


app = App(
    name='hello_world_app',
    root_agent=root_agent,
    plugins=[
        CountInvocationPlugin(),
        # ContextFilterPlugin(num_invocations_to_keep=3),
        SaveFilesAsArtifactsPlugin(),
    ],
    # 啟用事件壓縮功能 (Event Compaction)，優化歷史對話。
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=2, # 每 2 個事件觸發一次壓縮
        overlap_size=1,       # 壓縮時保留 1 個事件作為重疊上下文
    ),
)

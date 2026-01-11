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

"""Bingo 數位寵物主腳本。

此腳本展示了靜態指令 (Static Instruction) 的功能，透過一個根據
存儲在會話狀態 (Session State) 中的餵食時間而展現不同情緒的數位寵物來呈現。
"""

import asyncio
import logging
import time

from dotenv import load_dotenv
from google.adk.cli.utils import logs
from google.adk.runners import InMemoryRunner

from .static_instruction import agent

# 定義應用程式名稱與使用者 ID
APP_NAME = "bingo_digital_pet_app"
USER_ID = "pet_owner"

# 設定 ADK 日誌級別為 DEBUG
logs.setup_adk_logger(level=logging.DEBUG)


async def call_agent_async(
    runner, user_id, session_id, prompt, state_delta=None
):
  """以非同步方式呼叫代理程式，並支援狀態增量 (State Delta) 更新。"""
  from google.adk.agents.run_config import RunConfig
  from google.genai import types

  # 建立使用者輸入內容
  content = types.Content(
      role="user", parts=[types.Part.from_text(text=prompt)]
  )

  final_response_text = ""
  # 執行代理程式並處理串流回應
  async for event in runner.run_async(
      user_id=user_id,
      session_id=session_id,
      new_message=content,
      state_delta=state_delta,
      run_config=RunConfig(save_input_blobs_as_artifacts=False),
  ):
    # 提取非使用者（即代理程式）的回應文字
    if event.content and event.content.parts:
      if text := "".join(part.text or "" for part in event.content.parts):
        if event.author != "user":
          final_response_text += text

  return final_response_text


async def test_hunger_states(runner):
  """透過模擬餵食時間來測試不同的飢餓狀態。"""
  print("正在測試 Bingo 的不同飢餓狀態...\n")

  # 建立新的會話
  session = await runner.session_service.create_session(
      app_name=APP_NAME, user_id=USER_ID
  )

  # 模擬不同的飢餓情境
  current_time = time.time()
  hunger_scenarios = [
      {
          "description": "剛建立的寵物 (飢餓)",
          "last_fed": None,
          "prompt": "嗨 Bingo！我剛把你帶回家當我的數位寵物！",
      },
      {
          "description": "剛餵過 (飽足且滿足)",
          "last_fed": current_time,  # 就在剛才
          "prompt": "吃完這餐後感覺如何，Bingo？",
      },
      {
          "description": "4 秒前餵過 (滿足)",
          "last_fed": current_time - 4,  # 4 秒前
          "prompt": "想跟我玩遊戲嗎？",
      },
      {
          "description": "10 秒前餵過 (有點餓)",
          "last_fed": current_time - 10,  # 10 秒前
          "prompt": "你還好嗎，夥伴？",
      },
      {
          "description": "20 秒前餵過 (飢餓)",
          "last_fed": current_time - 20,  # 20 秒前
          "prompt": "Bingo，你在想什麼？",
      },
      {
          "description": "30 秒前餵過 (非常餓)",
          "last_fed": current_time - 30,  # 30 秒前
          "prompt": "嘿 Bingo，你感覺怎麼樣？",
      },
      {
          "description": "60 秒前餵過 (餓扁了)",
          "last_fed": current_time - 60,  # 60 秒前
          "prompt": "Bingo？你還在嗎？",
      },
  ]

  # 遍歷各個情境並執行
  for i, scenario in enumerate(hunger_scenarios, 1):
    print(f"{'='*80}")
    print(f"情境 #{i}: {scenario['description']}")
    print(f"{'='*80}")

    # 設定包含模擬餵食時間的狀態增量
    state_delta = {}
    if scenario["last_fed"] is not None:
      state_delta["last_fed_timestamp"] = scenario["last_fed"]

    print(f"你: {scenario['prompt']}")

    # 呼叫代理程式並獲取回應
    response = await call_agent_async(
        runner,
        USER_ID,
        session.id,
        scenario["prompt"],
        state_delta if state_delta else None,
    )
    print(f"Bingo: {response}\n")

    # 情境之間的短暫延遲
    if i < len(hunger_scenarios):
      await asyncio.sleep(1)


async def main():
  """執行數位寵物 Bingo 的主函數。"""
  # 從 .env 檔案載入環境變數
  load_dotenv()

  print("🐕 正在初始化數位寵物 Bingo...")
  print(f"寵物名稱: {agent.root_agent.name}")
  print(f"模型: {agent.root_agent.model}")
  print(
      "靜態個性已配置:"
      f" {agent.root_agent.static_instruction is not None}"
  )
  print(
      "動態情緒系統已配置:"
      f" {agent.root_agent.instruction is not None}"
  )
  print()

  # 建立記憶體內執行器 (InMemoryRunner)
  runner = InMemoryRunner(
      agent=agent.root_agent,
      app_name=APP_NAME,
  )

  # 執行飢餓狀態展示
  await test_hunger_states(runner)


if __name__ == "__main__":
  start_time = time.time()
  print(
      "🐕 Bingo 數位寵物會話開始於"
      f" {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(start_time))}"
  )
  print("-" * 80)

  # 啟動非同步主迴圈
  asyncio.run(main())

  print("-" * 80)
  end_time = time.time()
  print(
      "🐕 寵物會話結束於"
      f" {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(end_time))}"
  )
  print(f"總遊玩時間: {end_time - start_time:.2f} 秒")
  print("謝謝你陪伴 Bingo！ 🐾")

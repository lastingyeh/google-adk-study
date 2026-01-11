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

import asyncio
import time

from .hello_world_app import agent
from dotenv import load_dotenv
from google.adk.agents.run_config import RunConfig
from google.adk.cli.utils import logs
from google.adk.runners import InMemoryRunner
from google.adk.sessions.session import Session
from google.genai import types

# 載入環境變數（主要用於 API 金鑰）
load_dotenv(override=True)
# 將日誌（Logs）記錄到暫存資料夾
logs.log_to_tmp_folder()


async def main():
  """
  主程式流程：
  1. 初始化 InMemoryRunner 並綁定代理人 (Agent)。
  2. 建立會話 (Session)。
  3. 執行多次對話測試，包括擲骰子與狀態檢查。
  4. 測試傳送位元組 (Bytes) 格式的訊息。
  5. 查詢產出的成品 (Artifacts)。
  """
  app_name = 'my_app'
  user_id_1 = 'user1'

  # 初始化執行器 (Runner)，使用記憶體模式 (InMemoryRunner)
  runner = InMemoryRunner(
      agent=agent.root_agent,
      app_name=app_name,
  )

  # 建立新的會話 (Session)
  session_11 = await runner.session_service.create_session(
      app_name=app_name, user_id=user_id_1
  )

  async def run_prompt(session: Session, new_message: str):
    """傳送純文字訊息並打印代理人的回應。"""
    content = types.Content(
        role='user', parts=[types.Part.from_text(text=new_message)]
    )
    print('** User says:', content.model_dump(exclude_none=True))

    # 非同步執行代理人任務
    async for event in runner.run_async(
        user_id=user_id_1,
        session_id=session.id,
        new_message=content,
    ):
      # 打印代理人的回覆內容
      if event.content.parts and event.content.parts[0].text:
        print(f'** {event.author}: {event.content.parts[0].text}')

  async def run_prompt_bytes(session: Session, new_message: str):
    """傳送位元組 (Bytes) 格式的訊息。"""
    content = types.Content(
        role='user',
        parts=[
            types.Part.from_bytes(
                data=str.encode(new_message), mime_type='text/plain'
            )
        ],
    )
    print('** User says:', content.model_dump(exclude_none=True))

    async for event in runner.run_async(
        user_id=user_id_1,
        session_id=session.id,
        new_message=content,
        # 設定不將輸入的 Blob 儲存為 Artifacts
        run_config=RunConfig(save_input_blobs_as_artifacts=False),
    ):
      if event.content.parts and event.content.parts[0].text:
        print(f'** {event.author}: {event.content.parts[0].text}')

  async def check_rolls_in_state(rolls_size: int):
    """檢查會話狀態 (Session State) 中的擲骰子紀錄。"""
    session = await runner.session_service.get_session(
        app_name=app_name, user_id=user_id_1, session_id=session_11.id
    )
    # 驗證擲骰子的次數是否正確
    assert len(session.state['rolls']) == rolls_size
    # 驗證骰子點數是否在合理範圍內 (1-100)
    for roll in session.state['rolls']:
      assert roll > 0 and roll <= 100

  # 開始執行測試流程
  start_time = time.time()
  print('Start time:', start_time)
  print('------------------------------------')

  # 第一輪對話：打招呼
  await run_prompt(session_11, 'Hi')

  # 第二輪對話：請求擲 100 面的骰子
  await run_prompt(session_11, 'Roll a die with 100 sides')
  await check_rolls_in_state(1)

  # 第三輪對話：再次擲骰子
  await run_prompt(session_11, 'Roll a die again with 100 sides.')
  await check_rolls_in_state(2)

  # 第四輪對話：詢問剛才擲出的點數（測試記憶功能）
  await run_prompt(session_11, 'What numbers did I got?')

  # 第五輪對話：測試位元組輸入
  await run_prompt_bytes(session_11, 'Hi bytes')

  # 列出此會話產生的所有成品 (Artifacts)
  print(
      await runner.artifact_service.list_artifact_keys(
          app_name=app_name, user_id=user_id_1, session_id=session_11.id
      )
  )

  end_time = time.time()
  print('------------------------------------')
  print('End time:', end_time)
  print('Total time:', end_time - start_time)


if __name__ == '__main__':
  # 執行主異步函式
  asyncio.run(main())

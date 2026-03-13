# Copyright 2026 Google LLC
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

from google.adk.agents.llm_agent import Agent
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.genai import types

def reimburse(purpose: str, amount: float) -> str:
  """將款項報支（Reimburse）給員工。"""
  # 模擬報支流程，回傳成功狀態
  return {
      'status': 'ok',
  }

# 定義審批代理人 (Approval Agent)，負責處理超過 100 元的報支請求
approval_agent = RemoteA2aAgent(
    name='approval_agent',
    description='如果金額大於 100，協助審核報支。',
    agent_card=(
        f'http://localhost:8001/a2a/human_in_loop{AGENT_CARD_WELL_KNOWN_PATH}'
    ),
)


# 定義根代理人 (Root Agent)，作為報支流程的入口
root_agent = Agent(
    model='gemini-2.0-flash',
    name='reimbursement_agent',
    instruction="""
      你是一個負責處理員工報支流程的代理人。
      如果金額小於 $100，你會自動核准報銷。並呼叫 reimburse() 將款項報支給員工。

      如果金額大於 $100，你會將請求移交給審批代理人 (approval_agent) 來處理報支。
    """,
    tools=[reimburse],
    sub_agents=[approval_agent],
    generate_content_config=types.GenerateContentConfig(temperature=0.1),
)

from google.adk.apps import App

app = App(root_agent=root_agent, name="a2a_human_in_loop")

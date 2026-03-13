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

from typing import Any

from google.adk import Agent
from google.adk.tools.long_running_tool import LongRunningFunctionTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types


def reimburse(purpose: str, amount: float) -> str:
  """將款項報支（Reimburse）給員工。"""
  # 模擬報支成功回傳
  return {
      'status': 'ok',
  }


def ask_for_approval(
    purpose: str, amount: float, tool_context: ToolContext
) -> dict[str, Any]:
  """請求對報支申請進行審批（Approval）。"""
  # 此函數被封裝為 LongRunningFunctionTool，用於模擬需要人工介入的流程
  return {
      'status': 'pending',
      'amount': amount,
      'ticketId': 'reimbursement-ticket-001',
  }


# 定義負責處理報支邏輯的代理人
root_agent = Agent(
    model='gemini-2.0-flash',
    name='reimbursement_agent',
    instruction="""
      你是一個負責處理員工報支流程的代理人。
      如果金額小於 $100，你會自動核准報銷。

      如果金額大於 $100，你會向經理請求核准。
      如果經理核准，你將呼叫 reimburse() 將款項報支給員工。
      如果經理拒絕，你將告知員工拒絕的結果。
""",
    # 使用 LongRunningFunctionTool 封裝需要等待的審批函數
    tools=[reimburse, LongRunningFunctionTool(func=ask_for_approval)],
    generate_content_config=types.GenerateContentConfig(temperature=0.1),
)
# Copyright 2025 Google LLC
#
# 根據 Apache License, Version 2.0 授權
# 詳細授權條款請參閱 http://www.apache.org/licenses/LICENSE-2.0

from google.adk import Agent
from google.adk.apps import App
from google.adk.apps import ResumabilityConfig
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.tool_confirmation import ToolConfirmation
from google.adk.tools.tool_context import ToolContext
from google.genai import types

def reimburse(amount: int, tool_context: ToolContext) -> str:
  """根據金額為員工報銷。"""
  return {'status': 'ok'}

async def confirmation_threshold(
    amount: int, tool_context: ToolContext
) -> bool:
  """若金額大於 1000，則需經過確認。"""
  return amount > 1000

def request_time_off(days: int, tool_context: ToolContext):
  """員工請假申請。"""
  if days <= 0:
    return {'status': '請假天數無效。'}

  if days <= 2:
    # 2 天以內自動核准
    return {
        'status': 'ok',
        'approved_days': days,
    }

  # 超過 2 天需主管確認
  tool_confirmation = tool_context.tool_confirmation
  if not tool_confirmation:
    # 請求主管確認
    tool_context.request_confirmation(
        hint=(
            '請主管核准或拒絕 request_time_off() 工具呼叫，'
            '並以 FunctionResponse 回覆，內容需包含 ToolConfirmation payload。'
        ),
        payload={
            'approved_days': 0,
        },
    )
    return {'status': '需主管核准。'}

  approved_days = tool_confirmation.payload['approved_days']
  approved_days = min(approved_days, days)
  if approved_days == 0:
    return {'status': '請假申請被拒絕。', 'approved_days': 0}
  return {
      'status': 'ok',
      'approved_days': approved_days,
  }

# 建立主要代理人
root_agent = Agent(
    model='gemini-2.5-flash',
    name='time_off_agent',
    instruction="""
    你是一位能協助員工報銷及請假申請的助理。
    - 報銷請使用 `reimburse` 工具。
    - 請假申請請使用 `request_time_off` 工具。
    - 優先使用工具來完成使用者需求。
    - 回覆時請務必提供工具執行結果。
    """,
    tools=[
        # 設定 require_confirmation 為 True 或 callable，決定是否需使用者確認工具呼叫
        FunctionTool(
            reimburse,
            require_confirmation=confirmation_threshold,
        ),
        request_time_off,
    ],
    generate_content_config=types.GenerateContentConfig(temperature=0.1),
)

# 建立應用程式
app = App(
    name='human_tool_confirmation',
    root_agent=root_agent,
    # 啟用可恢復性設定
    resumability_config=ResumabilityConfig(
        is_resumable=True,
    ),
)

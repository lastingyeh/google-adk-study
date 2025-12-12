# ruff: noqa
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

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps.app import App

import os
import google.auth

_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"


def get_weather(query: str) -> str:
    """模擬網路搜尋。使用它來獲取天氣資訊。

    Args:
        query: 包含要獲取天氣資訊的地點的字串。

    Returns:
        包含查詢地點的模擬天氣資訊的字串。
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "現在 60 度，有霧。"
    return "現在 90 度，晴朗。"


def get_current_time(query: str) -> str:
    """模擬獲取城市的當前時間。

    Args:
        city: 要獲取當前時間的城市名稱。

    Returns:
        包含當前時間資訊的字串。
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"抱歉，我沒有關於查詢的時區資訊：{query}。"

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"查詢 {query} 的當前時間是 {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


root_agent = Agent(
    name="root_agent",
    model="gemini-3-pro-preview",
    description="一個可以提供有關天氣和時間資訊的代理程式。",
    instruction="您是一個有用的 AI 助手，旨在提供準確和有用的資訊。",
    tools=[get_weather, get_current_time],
)

app = App(root_agent=root_agent, name="app")

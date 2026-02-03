# ruff: noqa
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

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.tools import google_search
from google.genai import types

import os
import google.auth

# 獲取預設的 Google Cloud 憑證與專案 ID
_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"


def get_weather(query: str) -> str:
    """模擬網路搜尋以獲取天氣資訊。

    參數:
        query: 包含要獲取天氣資訊的地區名稱的字串。

    傳回值:
        包含查詢地區模擬天氣資訊的字串。
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "舊金山氣溫 60 度，有霧。"
    return "天氣晴朗，氣溫 90 度。"


def get_current_time(query: str) -> str:
    """模擬獲取城市的當前時間。

    參數:
        query: 要獲取當前時間的地區或查詢內容。

    傳回值:
        包含當前時間資訊的字串。
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"抱歉，我沒有此查詢的時區資訊： {query}。"

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"查詢內容 {query} 的目前時間為 {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


# 定義根代理 (Root Agent)
root_agent = Agent(
    name="root_agent",
    model=os.getenv("DEMO_AGENT_MODEL", "gemini-live-2.5-flash"),
    instruction="你是一個可以搜尋網路的得力助手，旨在提供準確且有用的資訊。",
    tools=[
        get_weather,
        get_current_time,
        google_search,
    ],  # 註冊天氣、時間與 Google 搜尋查詢工具
)

# 建立應用程式實例
app = App(root_agent=root_agent, name="bidi_demo")

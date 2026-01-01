from google.adk.agents import Agent
from google.adk.apps.app import App
from google.adk.models import Gemini
from google.genai import types

import os
import google.auth
import vertexai

# 獲取預設的 Google Cloud 憑證和專案 ID
_, project_id = google.auth.default()

# 設定環境變數，指定 Google Cloud 專案和區域
# 這些變數將被後續的 SDK 調用使用
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
# 強制使用 Vertex AI 而非預設的 GenAI API
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

# 初始化 Vertex AI SDK
vertexai.init(project=project_id, location="us-central1")


def get_weather(query: str) -> str:
    """模擬網路搜尋功能。用於獲取天氣資訊。

    Args:
        query: 包含要查詢天氣資訊的地點字串。

    Returns:
        包含查詢地點模擬天氣資訊的字串。
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


# 建立根代理 (Root Agent)
# 這是應用程式的主要進入點
root_agent = Agent(
    name="root_agent",
    # 設定使用的 Gemini 模型配置
    model=Gemini(
        model="gemini-live-2.5-flash-native-audio",
        # 設定 HTTP 重試選項，最多重試 3 次
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    # 設定代理的系統指令
    instruction="你是一個樂於助人的人工智慧助理，旨在提供準確且有用的資訊。",
    # 註冊可用的工具函式
    tools=[get_weather],
)

# 建立 ADK 應用程式實例
# 將根代理綁定到應用程式
app = App(root_agent=root_agent, name="app")

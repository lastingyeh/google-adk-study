# Copyright 2025 Google LLC
#
# 根據 Apache License 2.0 版本（「本授權」）授權；
# 除非遵守本授權，否則您不得使用此檔案。
# 您可以在以下網址獲得本授權的副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據本授權分發的軟體
# 是按「現狀」基礎分發的，無任何明示或暗示的保證或條件。
# 請參閱本授權以了解管理權限和限制的特定語言。

"""
## 重點摘要
- **核心概念**：測試已部署到 Vertex AI Agent Engine 的代理功能。
- **關鍵技術**：VertexAiSessionService, stream_query, 異步 (asyncio)。
- **重要結論**：此腳本模擬使用者與代理的對話，並能展示函式呼叫與回應的詳細流程。
- **行動項目**：執行前確保 `AGENT_ENGINE_ID` 已在 `.env` 中正確設定。
"""

import asyncio
import json
import os
import sys

import vertexai
from dotenv import load_dotenv
from google.adk.sessions import VertexAiSessionService
from vertexai import agent_engines

# 將專案根目錄添加到 sys.path，以便導入自定義模組
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def pretty_print_event(event):
    """漂亮地打印事件內容，並對過長的內容進行截斷。"""
    if "content" not in event:
        print(f"[{event.get('author', 'unknown')}]: {event}")
        return

    author = event.get("author", "unknown")
    parts = event["content"].get("parts", [])

    for part in parts:
        if "text" in part:
            text = part["text"]
            print(f"[{author}]: {text}")
        elif "functionCall" in part:
            func_call = part["functionCall"]
            print(
                f"[{author}]: 函式呼叫 (Function call): {func_call.get('name', 'unknown')}"
            )
            # 如果引數太長則截斷
            args = json.dumps(func_call.get("args", {}))
            if len(args) > 100:
                args = args[:97] + "..."
            print(f"  引數 (Args): {args}")
        elif "functionResponse" in part:
            func_response = part["functionResponse"]
            print(
                f"[{author}]: 函式回應 (Function response): {func_response.get('name', 'unknown')}"
            )
            # 如果回應太長則截斷
            response = json.dumps(func_response.get("response", {}))
            if len(response) > 100:
                response = response[:97] + "..."
            print(f"  回應 (Response): {response}")


# 載入環境變數
load_dotenv()

# 初始化 Vertex AI
vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
)

# 初始化會話服務 (Session Service)
session_service = VertexAiSessionService(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
)
AGENT_ENGINE_ID = os.getenv("AGENT_ENGINE_ID")

# 建立新會話
session = asyncio.run(
    session_service.create_session(
        app_name=AGENT_ENGINE_ID,
        user_id="123",
    )
)

# 獲取代理引擎實例
agent_engine = agent_engines.get(AGENT_ENGINE_ID)

print("輸入 'quit' 以退出。")
while True:
    user_input = input("輸入: ")
    if user_input == "quit":
        break

    # 串流查詢代理
    for event in agent_engine.stream_query(
        user_id="123", session_id=session.id, message=user_input
    ):
        pretty_print_event(event)

# 刪除會話以清理資源
asyncio.run(
    session_service.delete_session(
        app_name="auto_insurance_agent", user_id="123", session_id=session.id
    )
)

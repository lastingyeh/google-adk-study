import asyncio
import json
import os

import vertexai
from dotenv import load_dotenv
from google.adk.sessions import VertexAiSessionService
from vertexai import agent_engines


def pretty_print_event(event):
    """
    格式化並列印事件內容，對於過長的內容進行截斷。
    Pretty prints an event with truncation for long content.
    """
    max_args = 100
    max_part_length = 200
    max_response_length = 100

    if "content" not in event:
        print(f"[{event.get('author', 'unknown')}]: {event}")
        return

    author = event.get("author", "unknown")
    parts = event["content"].get("parts", [])

    for part in parts:
        if "text" in part:
            text = part["text"]
            # 截斷過長的文字至 200 字元
            # Truncate long text to 200 characters
            if len(text) > max_part_length:
                text = text[: max_part_length - 3] + "..."
            print(f"[{author}]: {text}")
        elif "functionCall" in part:
            func_call = part["functionCall"]
            print(f"[{author}]: Function call: {func_call.get('name', 'unknown')}")
            # 截斷過長的參數
            # Truncate args if too long
            args = json.dumps(func_call.get("args", {}))
            if len(args) > max_args:
                args = args[: max_args - 3] + "..."
            print(f"  Args: {args}")
        elif "functionResponse" in part:
            func_response = part["functionResponse"]
            print(
                f"[{author}]: Function response: {func_response.get('name', 'unknown')}"
            )
            # 截斷過長的回應
            # Truncate response if too long
            response = json.dumps(func_response.get("response", {}))
            if len(response) > max_response_length:
                response = response[: max_response_length - 3] + "..."
            print(f"  Response: {response}")


load_dotenv()

# 初始化 Vertex AI
vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
)

# 初始化 Vertex AI Session 服務
session_service = VertexAiSessionService(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
)
AGENT_ENGINE_ID = os.getenv("AGENT_ENGINE_ID")
assert AGENT_ENGINE_ID is not None, "AGENT_ENGINE_ID 環境變數必須設定"

# 建立對話 Session
session = asyncio.run(
    session_service.create_session(
        app_name=AGENT_ENGINE_ID,
        user_id="123",
    )
)

# 獲取 Agent Engine 實例
agent_engine = agent_engines.get(AGENT_ENGINE_ID)

# 測試查詢列表
queries = [
    "Hi, how are you?",
    "According to the MD&A, how might the increasing proportion of revenues derived from non-advertising sources like Google Cloud and devices potentially impact Alphabet's overall operating margin, and why?",
    "The report mentions significant investments in AI. What specific connection is drawn between these AI investments and the company's expectations regarding future capital expenditures?",
    "Thanks, I got all the information I need. Goodbye!",
]

for query in queries:
    print(f"\n[user]: {query}")
    # 串流查詢回應
    for event in agent_engine.stream_query(  # type: ignore[attr-defined]
        user_id="123",
        session_id=session.id,
        message=query,
    ):
        pretty_print_event(event)

"""
## 重點摘要

- **核心概念**：與部署的 Agent 進行互動
- **關鍵技術**：Vertex AI Session Service, Agent Engine Streaming Query
- **重要結論**：此腳本示範如何建立會話 (Session) 並透過串流方式 (Stream Query) 與已部署在 Vertex AI 的 Agent 進行多輪對話。
- **行動項目**：確認 `.env` 中已設定正確的 `AGENT_ENGINE_ID` 後執行此腳本進行測試。
"""

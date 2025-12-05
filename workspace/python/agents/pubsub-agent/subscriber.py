import os
import sys
import json
import asyncio
import logging
from google.cloud import pubsub_v1
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pubsub_agent.agent import root_agent

# 抑制來自函式庫的吵雜除錯訊息
logging.getLogger('google.auth').setLevel(logging.WARNING)
logging.getLogger('google.cloud').setLevel(logging.WARNING)
logging.getLogger('google.genai').setLevel(logging.WARNING)
logging.getLogger('absl').setLevel(logging.ERROR)

# 從環境變數中取得 GCP 專案 ID
project_id = os.environ.get("GCP_PROJECT")
# 定義 Pub/Sub 訂閱 ID
subscription_id = "document-processor"

# 初始化 Pub/Sub 訂閱者客戶端
subscriber = pubsub_v1.SubscriberClient()
# 建立完整的訂閱路徑: projects/{project_id}/subscriptions/{subscription_id}
subscription_path = subscriber.subscription_path(project_id, subscription_id)

async def process_document_with_agent(document_id: str, content: str):
    """
    使用 ADK root_agent 協調者處理文件。

    Args:
        document_id (str): 文件的唯一識別碼
        content (str): 文件的文字內容

    Returns:
        代理執行的最終結果
    """
    try:
        # 使用所需的會話服務建立代理執行器 (Runner)
        session_service = InMemorySessionService()
        runner = Runner(
            app_name="pubsub_processor",
            agent=root_agent,
            session_service=session_service
        )

        # 為此文件處理建立一個工作階段 (Session)
        session = await session_service.create_session(
            app_name="pubsub_processor",
            user_id="pubsub_subscriber"
        )

        # 準備給代理的提示訊息
        prompt_text = f"""分析此文件並將其路由到適當的分析器：

        文件 ID: {document_id}

        內容:
        {content}

        分析文件類型並提取相關資訊。"""

        # 建立正確的 Content 物件
        prompt = types.Content(
            role="user",
            parts=[types.Part(text=prompt_text)]
        )

        # 執行代理並收集結果
        final_result = None
        # run_async 回傳一個非同步產生器，我們會迭代它直到最後一個事件
        async for event in runner.run_async(
            user_id="pubsub_subscriber",
            session_id=session.id,
            new_message=prompt
        ):
            # 事件是串流的，捕捉最後一個
            final_result = event

        return final_result

    except Exception as e:
        print(f"❌ 代理處理錯誤: {e}")
        raise

def process_message(message):
    """
    處理 Pub/Sub 訊息，並進行非同步代理處理。

    Args:
        message: Pub/Sub 訊息物件
    """
    try:
        # 解碼訊息資料
        data = json.loads(message.data.decode("utf-8"))
        document_id = data.get("document_id")
        content = data.get("content")

        print(f"\n📨 正在處理: {document_id}")

        # 執行非同步代理處理
        result = asyncio.run(process_document_with_agent(document_id, content))

        if result:
            # 從事件內容中提取文字
            response_text = ""
            if hasattr(result, 'content') and result.content and result.content.parts:
                for part in result.content.parts:
                    if part.text:
                        response_text += part.text

            if response_text:
                # 清理回應文字以進行顯示 (取前 200 個字元)
                display_text = response_text.strip()[:200]
                print(f"✅ 成功: {document_id}")
                print(f"   └─ {display_text}...")
            else:
                print(f"✅ 完成 {document_id} (無文字回應)")
        else:
            print(f"✅ 完成 {document_id}")

        # 確認訊息 (從佇列中移除)
        message.ack()

    except Exception as e:
        print(f"❌ 錯誤: {document_id} - {str(e)[:100]}")
        # 否定確認訊息 (讓 Pub/Sub 稍後重試)
        message.nack()

# 訂閱並開始處理
print("\n" + "="*70)
print("🚀 文件處理協調者")
print("="*70)
print(f"訂閱: {subscription_id}")
print(f"專案: {project_id or '(未設定 - 本地模式)'}")
print(f"代理: root_agent (多重分析協調者)")
print("="*70)
print("等待訊息中...\n")

# 開啟串流拉取 (Streaming Pull)
streaming_pull_future = subscriber.subscribe(
    subscription_path,
    callback=process_message
)

try:
    # 保持主執行緒運行，直到收到取消訊號或發生錯誤
    streaming_pull_future.result()
except KeyboardInterrupt:
    # 處理 Ctrl+C 中斷
    streaming_pull_future.cancel()
    print("\n" + "="*70)
    print("✋ 處理器已停止")
    print("="*70)

### 重點摘要
# - **核心概念**：Pub/Sub 訂閱者 (Subscriber) 實作，整合 ADK 代理進行文件處理。
# - **關鍵技術**：Pub/Sub Streaming Pull, Python Asyncio, Google ADK Runner, InMemorySessionService。
# - **重要結論**：
#   - 使用 `subscriber.subscribe(callback=process_message)` 建立持續的訊息監聽。
#   - `process_message` 回呼函式在獨立的執行緒中執行，因此需要使用 `asyncio.run()` 來呼叫非同步的代理邏輯。
#   - 訊息必須被明確地 `ack()` (確認成功) 或 `nack()` (處理失敗，要求重試)。
# - **行動項目**：
#   - 確保訂閱 `document-processor` 已在 GCP 中建立。
#   - 監控處理錯誤並根據需要調整重試策略。

import os
import json
from google.cloud import pubsub_v1
from datetime import datetime

# 從環境變數中取得 GCP 專案 ID
# Get GCP project ID from environment variables
project_id = os.environ.get("GCP_PROJECT")
# 定義 Pub/Sub 主題 ID
# Define Pub/Sub topic ID
topic_id = "document-uploads"

# 初始化 Pub/Sub 發布者客戶端
# Initialize Pub/Sub publisher client
publisher = pubsub_v1.PublisherClient()
# 建立完整的主題路徑: projects/{project_id}/topics/{topic_id}
# Create full topic path: projects/{project_id}/topics/{topic_id}
topic_path = publisher.topic_path(project_id, topic_id)

def publish_document(document_id: str, content: str):
    """
    發布文件進行處理。
    Publish a document for processing.

    Args:
        document_id (str): 文件的唯一識別碼 Unique identifier for the document
        content (str): 文件的文字內容 Text content of the document

    Returns:
        str: 已發布訊息的 ID The ID of the published message
    """
    # 建立訊息資料字典，包含文件 ID、內容和上傳時間
    # Create message data dictionary with document ID, content, and upload timestamp
    message_data = {
        "document_id": document_id,
        "content": content,
        "uploaded_at": datetime.now().isoformat(),
    }

    # 將字典序列化為 JSON 字串並編碼為 UTF-8 bytes
    # Serialize dictionary to JSON string and encode as UTF-8 bytes
    data = json.dumps(message_data).encode("utf-8")

    # 發布訊息到指定主題
    # publish() 方法是非同步的，回傳一個 Future 物件
    # Publish message to the specified topic
    # publish() method is asynchronous and returns a Future object
    future = publisher.publish(topic_path, data)

    # 等待發布完成並取得訊息 ID
    # result() 會阻塞直到訊息確認發布成功
    # Wait for publication to complete and get message ID
    # result() blocks until the message is confirmed as published
    message_id = future.result()

    print(f"✅ 已發布 (Published) {document_id} (訊息 ID: {message_id})")
    return message_id

# 範例使用方式
# Example usage
if __name__ == "__main__":
    # 發布一個財務文件範例
    # Publish a sample financial document
    publish_document(
        "DOC-001",
        "Q4 2024 Financial Report: Revenue $1.2M, Profit 33%"
    )

### 重點摘要
# - **核心概念**：Pub/Sub 發布者 (Publisher) 的實作，負責將資料發送到主題 (Topic)。
# - **關鍵技術**：`google-cloud-pubsub` 函式庫, JSON 序列化。
# - **重要結論**：發布訊息是非同步的過程，但可以透過 `.result()` 方法同步等待確認 (Ack)。
# - **行動項目**：確保環境變數 `GCP_PROJECT` 已正確設定，並且該專案中存在 `document-uploads` 主題。

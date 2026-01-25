# Copyright 2026 Google LLC
#
# 根據 Apache License 2.0 版本（「許可證」）授權；
# 除非遵守許可證，否則您不得使用此文件。
# 您可以在以下網址獲得許可證副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據許可證分發的軟體
# 是按「現狀」分發的，無任何明示或暗示的保證或條件。
# 請參閱許可證以瞭解管理權限和限制的特定語言。

"""
## 重點摘要 (程式碼邏輯)

- **核心概念**：利用 `ApiRegistry` 動態獲取 MCP 伺服器提供的工具集，並將其賦予 `LlmAgent`。
- **關鍵技術**：
    - `ApiRegistry`：連線至 Google Cloud 並獲取註冊的工具資訊。
    - `LlmAgent`：封裝了 LLM (Gemini 2.5 Flash) 的邏輯，並能執行傳入的工具。
- **重要結論**：這種架構使得工具的管理與 Agent 的開發解耦，工具可以獨立於 Agent 程式碼之外進行維護與註冊。
- **行動項目**：
    - 確保 `PROJECT_ID` 和 `MCP_SERVER_NAME` 已正確設定。
    - 確保環境中有足夠的權限存取 Google Cloud API Registry。
"""

import os

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.api_registry import ApiRegistry

# TODO: 填寫您的 Google Cloud 專案 ID 和 MCP 伺服器名稱
# 這些參數用於連接到正確的 API 註冊表和 MCP 服務
PROJECT_ID = "your-google-cloud-project-id"
MCP_SERVER_NAME = "your-mcp-server-name"

# 初始化 ApiRegistry 實例，用於發現註冊的工具
api_registry = ApiRegistry(PROJECT_ID)

# 從指定的 MCP 伺服器中獲取一組工具 (Toolset)
# 這允許 Agent 動態載入並使用該伺服器提供的功能（如 BigQuery 查詢）
registry_tools = api_registry.get_toolset(
    mcp_server_name=MCP_SERVER_NAME,
)

# 建立一個 LLM Agent (大型語言模型代理)
# 這個 Agent 將擔任數據分析師的角色，並配備了透過 API Registry 獲取的工具
root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="bigquery_assistant",
    instruction=f"""
    你是一個樂於助人的數據分析助理，擁有存取 BigQuery 的權限。專案 ID 為：{PROJECT_ID}

    當使用者詢問關於數據的問題時：
    - 在調用 BigQuery 工具時，請使用專案 ID {PROJECT_ID}。
    - 首先，探索可用的資料集 (Dataset) 和資料表 (Table)，以瞭解存在哪些數據。
    - 在進行查詢之前，檢查資料表架構 (Schema) 以瞭解其結構。
    - 編寫清晰、高效的 SQL 查詢來回答使用者的問題。
    - 用簡單、非技術性的語言解釋您的發現。

    強制性要求：
    - 務必使用 BigQuery 工具來獲取真實數據，而不是憑空假設。
    - 對於所有的 BigQuery 操作，請使用 project_id: {PROJECT_ID}。
    """,
    tools=[registry_tools],
)


# 版權所有 2025 Google LLC
#
# 根據 Apache 許可證 2.0 版（「許可證」）授權；
# 除非遵守許可證，否則您不得使用此檔案。
# 您可以在以下網址獲得許可證副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據許可證分發的軟體
# 是按「原樣」分發的，無任何明示或暗示的保證或條件。
# 請參閱許可證以了解管理權限和許可證下的限制。

"""
### 摘要
本檔案定義了 RAG 代理人（Agent）及其使用的檢索工具。它設定了一個 `VertexAiRagRetrieval` 工具，用於從 Vertex AI RAG Corpus 中檢索文件，並初始化了一個名為 `ask_rag_agent` 的根代理人。

### 核心重點
- **核心概念**：建立一個具備檢索能力的 AI 代理人。
- **關鍵技術**：Vertex AI RAG、Google ADK (Agent Development Kit)、Arize 追蹤。
"""

import os
import uuid

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import (
    VertexAiRagRetrieval,
)
from openinference.instrumentation import using_session
from vertexai.preview import rag

from rag.tracing import instrument_adk_with_arize

from .prompts import return_instructions_root

# 載入 .env 檔案中的環境變數
load_dotenv()
# 初始化 Arize 追蹤器，用於監控 ADK 效能
_ = instrument_adk_with_arize()


# 設定 Vertex AI RAG 檢索工具
ask_vertex_retrieval = VertexAiRagRetrieval(
    name="retrieve_rag_documentation",
    description=("使用此工具從 RAG 語料庫中檢索與問題相關的文件與參考資料。"),
    rag_resources=[
        rag.RagResource(
            # 請填入您自己的 RAG 語料庫 (RAG Corpus) ID
            # 範例格式：projects/123/locations/us-central1/ragCorpora/456
            rag_corpus=os.environ.get("RAG_CORPUS")
        )
    ],
    similarity_top_k=10,  # 檢索最相似的前 10 個區塊
    vector_distance_threshold=0.6,  # 向量距離閾值，過濾關聯性較低的結果
)

# 使用隨機產生的 session_id 建立代理人實例
with using_session(session_id=str(uuid.uuid4())):
    root_agent = Agent(
        model="gemini-2.0-flash-001",  # 使用的 Gemini 模型版本
        name="ask_rag_agent",
        instruction=return_instructions_root(),  # 載入代理人指令
        tools=[
            ask_vertex_retrieval,  # 註冊檢索工具
        ],
    )

# 將根代理人封裝成 ADK App
app = App(root_agent=root_agent, name="rag")

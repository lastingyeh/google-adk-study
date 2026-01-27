# ADK 的 Vertex AI RAG Engine 工具

> 🔔 `更新日期：2026-01-26`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/tools/google-cloud/vertex-ai-rag-engine/

[`ADK 支援`: `Python v0.1.0` | `Java v0.2.0`]

`vertex_ai_rag_retrieval` 工具允許代理（agent）使用 Vertex AI RAG Engine 執行私有數據檢索。

當您將 Vertex AI RAG Engine 用於 Grounding 時，您需要預先準備一個 RAG 語料庫（corpus）。
請參考 [RAG ADK 代理範例](https://github.com/google/adk-samples/blob/main/python/agents/RAG/rag/shared_libraries/prepare_corpus_and_data.py) 或 [Vertex AI RAG Engine 頁面](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-quickstart) 以了解如何設定。

> [!WARNING] 警告：每個代理執行個體僅限單一工具
此工具只能在代理執行個體中***單獨使用***。
如需更多關於此限制及解決辦法的資訊，請參閱 [ADK 工具的限制](../limitations.md)。

```py
import os

from google.adk.agents import Agent
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag

from dotenv import load_dotenv
from .prompts import return_instructions_root

# 載入環境變數
load_dotenv()

# 初始化 Vertex AI RAG 檢索工具
ask_vertex_retrieval = VertexAiRagRetrieval(
    name='retrieve_rag_documentation',
    description=(
        '使用此工具從 RAG 語料庫中檢索與問題相關的文件和參考資料。'
    ),
    rag_resources=[
        rag.RagResource(
            # 請填入您自己的 RAG 語料庫
            # 此處為測試用的範例 RAG 語料庫格式
            # 例如：projects/123/locations/us-central1/ragCorpora/456
            rag_corpus=os.environ.get("RAG_CORPUS")
        )
    ],
    similarity_top_k=10,
    vector_distance_threshold=0.6,
)

# 定義根代理（Root Agent）
root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='ask_rag_agent',
    instruction=return_instructions_root(),
    tools=[
        ask_vertex_retrieval,
    ]
)
```

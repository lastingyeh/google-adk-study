# 向量數據庫選擇

在 RAG 架構中，向量數據庫（Vector Store）是知識檢索的核心。身為架構師，在面對「自建 DIY（如 PostgreSQL + pgvector）」與「託管服務（如 Vertex AI Search）」的選擇時，我們必須跳脫單純的存儲視角，轉而評估整個**數據生命週期（Pipeline）** 的維運成本與系統脆性。選擇錯誤的存儲方案往往導致開發團隊陷入無止盡的索引維護與模型版本同步地獄。

---

### 情境 1：優先使用託管檢索服務（Vertex AI Search）而非原始向量存儲
**核心概念簡述**：
許多開發者直覺地認為 RAG = 「Embedding 模型 + 向量資料庫」。然而，這忽略了文檔解析（Parsing）、切片（Chunking）、元數據提取（Metadata Extraction）以及索引更新（Indexing）的複雜性。對於大多數企業級應用，應優先選擇「檢索即服務（Retrieval-as-a-Service）」，將這些非核心業務邏輯外包給平台。

**程式碼範例（Bad vs. Better）**：

*   **❌ Bad：手動維護 Embedding Pipeline**
    > **Rationale**: 這種做法將 ETL 邏輯與應用程式碼耦合。當 Embedding 模型需要升級（例如從 text-embedding-004 升級到 005），你需要手動重新處理所有舊數據，且容易發生「查詢時模型」與「索引時模型」不一致的災難。

    ```python
    # ❌ Bad: 手動處理 Embeddings 與向量存儲
    from langchain_google_vertexai import VertexAIEmbeddings
    from some_vector_db import VectorDBClient

    def add_document(text):
        # 開發者需自行負責 Chunking 策略
        chunks = manual_chunking(text)
        embeddings = VertexAIEmbeddings(model="text-embedding-004")
        vectors = embeddings.embed_documents(chunks)

        # 開發者需自行管理 ID 與重試邏輯
        client = VectorDBClient(host="...")
        client.upsert(vectors)
    ```

*   **✅ Better：使用 ADK 整合的託管檢索工具**
    > **Rationale**: 使用託管服務（如 Vertex AI Search），你只需關注「數據源」配置。平台會自動處理文檔解析、切片優化與索引更新。ADK 的工具層封裝了這些調用，確保代理（Agent）能以最穩定的方式獲取知識，並自動處理引用來源（grounding metadata）。

    ```python
    # ✅ Better: 利用 ADK 整合完整的檢索 Agent
    import asyncio
    from google.adk.agents import LlmAgent
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.adk.tools import VertexAiSearchTool
    from google.genai import types

    # 1. 定義託管檢索工具（指向已配置的 Data Store）
    search_tool = VertexAiSearchTool(
        data_store_id="projects/my-project/locations/global/collections/default_collection/dataStores/enterprise-docs",
        max_results=5,  # 可選，限制檢索結果數量
    )

    # 2. 建立具備檢索能力的 Agent
    doc_agent = LlmAgent(
        name="doc_qa_agent",
        model="gemini-2.0-flash",  # 必須使用 Gemini 模型
        tools=[search_tool],
        instruction="""你是基於文檔庫回答問題的助理。
        在回答前，務必使用搜尋工具查找相關資訊。
        若文檔中找不到答案，請明確告知。""",
    )

    # 3. 執行查詢並取得帶引用的回應
    async def query_with_sources(question: str):
        runner = Runner(agent=doc_agent, app_name="rag_app")
        content = types.Content(role='user', parts=[types.Part(text=question)])

        async for event in runner.run_async(user_id="user_1",
                                            session_id="session_1",
                                            new_message=content):
            if event.is_final_response() and event.content:
                # 取得模型回應
                response_text = event.content.parts[0].text

                # 取得引用來源（自動處理）
                if event.grounding_metadata:
                    sources = event.grounding_metadata.grounding_attributions
                    print(f"回應：{response_text}")
                    print(f"引用來源數量：{len(sources)}")
                    # 每個 attribution 包含：segment (文本片段), source_url (來源)

    # 執行查詢
    asyncio.run(query_with_sources("ADK 的安裝步驟是什麼？"))

    # 進階：如需根據使用者狀態動態調整 filter，可繼承並覆寫方法
    class DynamicFilterSearchTool(VertexAiSearchTool):
        def _build_vertex_ai_search_config(self, ctx):
            # 從 context 取得使用者資訊
            user_id = ctx.state.get('user_id')
            return types.VertexAISearch(
                datastore=self.data_store_id,
                filter=f"user_id = '{user_id}'",  # 動態過濾
                max_results=self.max_results,
            )
    ```

**底層原理探討與權衡**：
*   **維運成本（OpEx）**：DIY 方案要求團隊維護索引的一致性（Re-indexing）。當知識庫更新時，若沒有穩健的 CDC（Change Data Capture）機制，向量庫與原始文檔極易脫鉤。託管服務通常內建了與 Google Drive / Cloud Storage 的自動同步機制。
*   **檢索品質**：託管服務通常包含「語義重排序（Semantic Reranking）」與「混合搜尋（Hybrid Search）」邏輯，這些若要自建，需要極高的演算法專業知識。

---

### 情境 2：在大規模或特定領域查詢使用 Vector Search 2.0 (Hybrid Search)
**核心概念簡述**：
當你的應用場景需要「精確關鍵字匹配」（如：產品型號、錯誤代碼）與「語義理解」並存時，單純的 Dense Vector Search 往往效果不佳。此時應明確選用支援稀疏向量（Sparse Vectors）或混合搜尋（Hybrid Search）的現代向量引擎，而非試圖通過 Prompt Engineering 來修補檢索缺陷。

**程式碼範例（Bad vs. Better）**：

*   **❌ Bad：僅依賴語義相似度進行精確查找**
    > **Rationale**: 向量空間對於「SKU-12345」與「SKU-12346」可能判定極為相似，導致模型在查詢特定型號時產生幻覺。

    ```python
    # ❌ Bad: 僅使用 Dense Vector
    # 當用戶搜尋 "錯誤代碼 E-502" 時，可能返回 "錯誤代碼 E-503" 的解決方案
    # 因為兩者在語義上非常接近（都是錯誤代碼）
    results = vector_store.similarity_search("錯誤代碼 E-502", k=3)
    ```

*   **✅ Better：啟用混合搜尋與過濾器**
    > **Rationale**: 結合倒排索引（Inverted Index）與向量索引。先通過關鍵字鎖定範圍，再通過向量尋找語義相關性。ADK 的配置允許在定義工具時指定這種行為。

    ```python
    # ✅ Better: 混合搜尋配置
    from google.cloud import aiplatform

    # 使用 Vector Search 2.0 的混合檢索能力
    my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(...)

    response = my_index_endpoint.find_neighbors(
        queries=[embedding_vector],
        # 結合關鍵字過濾 (Filtering)
        filter=[{"namespace": "error_codes", "allow_list": ["E-502"]}],
        # 開啟混合搜尋模式 (若底層支援)
        algorithm_config="hybrid"
    )
    ```

**更多說明：檢索技術堆疊決策**

| 特性         | 原始向量存儲 (Raw Vector Store)                   | 託管檢索服務 (Managed Retrieval / Vertex AI Search) |
| :----------- | :------------------------------------------------ | :-------------------------------------------------- |
| **核心抽象** | 向量 (Embeddings)                                 | 文檔 (Documents)                                    |
| **適用場景** | 需要極致的延遲控制 (<10ms)、自定義 Embedding 模型 | 企業知識庫、RAG 標準應用、多模態搜尋                |
| **混合搜尋** | 需手動實作 (結合 Elasticsearch 或 Postgres)       | 內建 (Keyword + Semantic)                           |
| **Chunking** | 需自定義邏輯                                      | 自動化 / 可配置                                     |
| **維運負擔** | 高 (需處理分片、副本、索引重建)                   | 低 (Serverless)                                     |

```mermaid
graph TD
    UserQuery[用戶查詢] --> Intent{意圖識別}

    Intent -- "特定實體/ID" --> Hybrid[混合搜尋 (Vector + Keyword)]
    Intent -- "廣泛概念" --> Semantic[純語義搜尋 (Vertex AI Search)]

    subgraph "Managed Retrieval Pipeline"
        Semantic --> Rerank[語義重排序 (Reranking)]
        Rerank --> Snippet[摘要生成]
    end

    subgraph "Raw Vector Pipeline"
        Hybrid --> Sparse[關鍵字索引 (Sparse)]
        Hybrid --> Dense[向量索引 (Dense)]
        Sparse & Dense --> Merge[結果合併]
    end

    Snippet --> Context
    Merge --> Context[上下文組裝]
```

---

### 適用場景與拇指法則

*   **Rule of Thumb**：**除非你有特殊的「非文本」需求（如生技分子結構搜尋）或極端的成本/延遲限制，否則 RAG 應用應始終從「託管檢索服務（Vertex AI Search）」開始。**
*   **例外情況**：
    1.  **超低延遲推薦系統**：需要毫秒級回應，且數據結構單一（如電商向量召回），此時直接使用 `Vertex AI Vector Search` (Raw Index) 效能更佳。
    2.  **數據主權極其敏感**：數據完全無法離開本地 VPC，甚至無法接觸 Google 託管的 Public API 端點，此時可能需要自建開源向量庫（如 Weaviate, Milvus）於 GKE 上。

---

### 延伸思考

**1️⃣ 問題一**：為什麼說「Re-indexing」是向量資料庫維運中最大的隱形炸彈？

**👆 回答**：Embedding 模型是會迭代的（如 text-embedding-004 -> 005）。當你決定升級模型以獲得更好的語義理解時，你必須對**所有歷史數據**重新進行 Inference。在 TB 級別的數據規模下，這不僅是巨大的計算成本，更涉及如何在「不亦停機」的情況下平滑切換索引。託管服務通常提供版本控制或後台升級機制，大幅降低了此風險。

---

**2️⃣ 問題二**：在多租戶（Multi-tenant）SaaS 應用中，如何設計向量隔離？

**👆 回答**：絕對不要為每個租戶建立獨立的 Index（成本過高）。正確做法是使用**命名空間（Namespacing）**或**元數據過濾（Metadata Filtering）**。在查詢時，強制附加 `tenant_id` 作為過濾條件。注意，這要求向量資料庫支援「預過濾（Pre-filtering）」（如 Vertex AI Vector Search 的 `allow_list`），否則先檢索後過濾（Post-filtering）會導致召回率嚴重下降（即檢索出的 Top-K 結果可能全屬於其他租戶，被過濾後結果為空）。

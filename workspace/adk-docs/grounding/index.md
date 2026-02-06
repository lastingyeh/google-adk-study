# 使用數據 Grounding 代理

> 🔔 `更新日期：2026-02-05`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/grounding/

Grounding 是將您的 AI 代理連接到外部資訊源的過程，使它們能夠生成更準確、即時且可驗證的回答。透過將代理的回應建立在權威數據之上，您可以減少幻覺，並為使用者提供由可靠來源支持的答案。

ADK 支援多種 Grounding 方法：

- **Google 搜尋 Grounding**：將代理連接到即時網路資訊，用於需要最新數據（如新聞、天氣或自模型訓練以來可能已更改的事實）的查詢。

- **Vertex AI 搜尋 Grounding**：將代理連接到您組織的私人文件和企業數據，用於需要專有資訊的查詢。

- **代理式 RAG (Agentic RAG)**：構建能夠推理如何搜尋的代理，使用 Vector Search 2.0、Vertex AI RAG Engine 或其他檢索系統動態構建查詢和過濾器。

### 學習資源
|名稱 | 說明 | 相關連結 |
|---|---|---|
| **Google 搜尋 Grounding** | 讓代理存取即時、權威的網路資訊。設置流程、數據流解釋、回應引用顯示。 | [理解 Google 搜尋 Grounding](google_search_grounding.md) |
| **Vertex AI 搜尋 Grounding** | 連接企業文件和私人數據庫，配置數據存儲、回應 Grounding、來源歸屬。 | [理解 Vertex AI 搜尋 Grounding](vertex_ai_search_grounding.md) |
| **部落格文章：代理式 RAG 實作** | 介紹如何用 Vector Search 2.0 和 ADK 建立能解析意圖、構建過濾器的旅遊代理。 | [部落格文章](https://medium.com/google-cloud/10-minute-agentic-rag-with-the-new-vector-search-2-0-and-adk-655fff0bacac) |
| **Vector Search 2.0 旅遊代理筆記本** | Jupyter 筆記本範例，使用真實 Airbnb 數據、混合搜尋與 ADK 工具整合。 | [旅遊代理筆記本](https://github.com/google/adk-samples/blob/main/python/notebooks/grounding/vectorsearch2_travel_agent.ipynb) |
| **深度搜尋代理 (Deep Search Agent)** | 生產就緒的研究代理，兩階段工作流、多代理架構，生成帶引用的報告。 | [深度搜尋代理](../../python/agents/pack-deep-search/) |
| **RAG 代理** | 文件問答代理，支援文件上傳與引用格式答案，由 Vertex AI RAG Engine 驅動。 | [RAG 代理](../../python/agents/pack-rag/) |

# Google Cloud 工具

> 🔔 `更新日期：2026-01-25`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/tools/google-cloud/

Google Cloud 工具讓您的代理程式（agents）更輕鬆地連接到 Google Cloud 的產品與服務。只需幾行程式碼，您就可以使用這些工具將您的代理程式連接到：

* **任何自訂 API**：開發者託管在 Apigee 中的 API。
* **數百個預建連接器**：連接到 Salesforce、Workday 和 SAP 等企業系統。
* **自動化工作流**：使用應用程式整合（Application Integration）構建。
* **資料庫**：例如 Spanner、AlloyDB、Postgres 等，使用 MCP 資料庫工具箱（MCP Toolbox for databases）。

|                                                                                                               | 名稱                                              | 說明                                                                     | 連結                                   |
| ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------ | -------------------------------------- |
| <img src="https://google.github.io/adk-docs/assets/tools-apigee.png" style="width:32px;"/>                    | Apigee API Hub                                    | 將來自 Apigee API hub 的任何已編寫文件的 API 轉換為工具                  | [連結](./apigee-api-hub.md)            |
| <img src="https://google.github.io/adk-docs/assets/developer-tools-color.svg" style="width:32px;"/>           | API Registry                                      | 動態地將 Google Cloud 服務連接為 MCP 工具                                | [連結](./api-registry.md)              |
| <img src="https://google.github.io/adk-docs/assets/tools-apigee-integration.png" style="width:32px;"/>        | Application Integration (應用程式整合)            | 使用整合連接器（Integration Connectors）將您的代理程式連結到企業應用程式 | [連結](./application-integration.md)   |
| <img src="https://google.github.io/adk-docs/assets/tools-bigquery.png" style="width:32px;"/>                  | BigQuery 代理程式分析 (BigQuery Agent Analytics)  | 大規模分析和調試代理程式行為                                             | [連結](https://google.github.io/adk-docs/observability/bigquery-agent-analytics/)  |
| <img src="https://google.github.io/adk-docs/assets/tools-bigquery.png" style="width:32px;"/>                  | BigQuery 工具                                     | 連接 BigQuery 以檢索數據並進行分析                                       | [連結](./bigquery.md)                  |
| <img src="https://google.github.io/adk-docs/assets/tools-bigtable.png" style="width:32px;"/>                  | Bigtable 工具                                     | 與 Bigtable 交互以檢索數據並執行 SQL                                     | [連結](./bigtable.md)                  |
| <img src="https://google.github.io/adk-docs/assets/tools-gke.png" style="width:32px;"/>                       | GKE 程式碼執行器 (GKE Code Executor)              | 在安全且可擴展的 GKE 環境中運行 AI 生成的程式碼                          | [連結](./gke-code-executor.md)         |
| <img src="https://google.github.io/adk-docs/assets/tools-spanner.png" style="width:32px;"/>                   | Spanner 工具                                      | 與 Spanner 交互以檢索數據、搜索並執行 SQL                                | [連結](./spanner.md)                   |
| <img src="https://google.github.io/adk-docs/assets/tools-mcp-toolbox-for-databases.png" style="width:32px;"/> | 資料庫專用 MCP 工具箱 (MCP Toolbox for Databases) | 為您的代理程式連接超過 30 種不同的數據源                                 | [連結](./mcp-toolbox-for-databases.md) |
| <img src="https://google.github.io/adk-docs/assets/tools-vertex-ai.png" style="width:32px;"/>                 | Vertex AI RAG 引擎                                | 使用 Vertex AI RAG 引擎執行私有數據檢索                                  | [連結](./vertex-ai-rag-engine.md)      |
| <img src="https://google.github.io/adk-docs/assets/tools-vertex-ai.png" style="width:32px;"/>                 | Vertex AI 搜尋 (Vertex AI Search)                 | 在 Vertex AI Search 中搜索您私有的、配置好的數據存儲                     | [連結](./vertex-ai-search.md)          |
| <img src="https://google.github.io/adk-docs/assets/tools-pubsub.png" style="width:32px;"/>                    | Pub/Sub 工具                                      | 從 Google Cloud Pub/Sub 發佈、提取並確認消息                             | [連結](./pubsub.md)                    |

## 應用場景整理

| 工具名稱 | 關鍵程式碼 | 描述 | 應用場景 | 工具組合 |
| :--- | :--- | :--- | :--- | :--- |
| **API Registry** | `ApiRegistry(...)` | 將 Google Cloud 服務動態轉換為 MCP 工具。 | 動態存取專案中啟用的多種 Cloud 服務。 | Google Cloud APIs, MCP |
| **Apigee API Hub** | `APIHubToolset(...)` | 將 Apigee API Hub 中的 API 轉換為工具。 | 企業 API 管理、利用現有 OpenAPI 規範生成工具。 | Apigee API Hub |
| **Application Integration** | `ApplicationIntegrationToolset(...)` | 連接企業應用程式 (Salesforce, SAP 等) 與自動化工作流。 | 存取 SaaS/地端應用、執行複雜業務流程、聯合搜尋。 | Integration Connectors, Application Integration |
| **BigQuery Tools** | `BigQueryToolset(...)` | 提供 BigQuery 資料集、資料表資訊查詢與 SQL 執行。 | 數據分析、資料倉儲查詢、獲取資料結構。 | BigQuery |
| **Bigtable Tools** | `BigtableToolset(...)` | 存取 Bigtable 執行個體、資料表與執行 SQL。 | 大規模 NoSQL 數據存取、時間序列數據查詢。 | Bigtable |
| **Agent Engine Code Executor** | `AgentEngineSandboxCodeExecutor(...)` | 使用 Agent Engine 服務在沙箱中執行程式碼。 | 低延遲、狀態持久化的多步驟程式碼執行任務。 | Agent Engine |
| **Data Agents** | `DataAgentToolset(...)` | 與 Conversational Analytics API 驅動的數據代理互動。 | 使用自然語言進行數據分析與問答。 | BigQuery, Looker |
| **Vertex AI Express Mode** | `VertexAiSessionService`, `VertexAiMemoryBankService` | 提供免費層級的 Vertex AI 服務 (Session, Memory) 存取。 | 原型設計、快速開發與測試 Agent 功能。 | Vertex AI SDK |
| **GKE Code Executor** | `GkeCodeExecutor(...)` | 在 GKE gVisor 沙箱中執行程式碼。 | 生產環境、高安全性隔離需求的程式碼執行。 | GKE, gVisor |
| **MCP Toolbox for Databases** | `ToolboxToolset(...)` | 連接多種資料庫 (SQL, NoSQL, Graph) 的 MCP 伺服器客戶端。 | 需連接多樣化資料庫且需處理連接池與驗證的場景。 | PostgreSQL, MySQL, Neo4j 等 |
| **Pub/Sub Tools** | `PubSubToolset(...)` | 發布、提取和確認 Pub/Sub 訊息。 | 事件驅動架構、異步訊息傳遞與處理。 | Cloud Pub/Sub |
| **Spanner Tools** | `SpannerToolset(...)` | 存取 Spanner 資料庫、執行 SQL 與相似性搜尋。 | 全球分佈式資料庫存取、關鍵業務數據查詢。 | Spanner |
| **Vertex AI RAG Engine** | `VertexAiRagRetrieval(...)` | 使用 Vertex AI RAG Engine 進行私有數據檢索。 | 建立基於私有知識庫的 RAG 應用。 | Vertex AI RAG Corpus |
| **Vertex AI Search** | `VertexAiSearchTool(...)` | 在 Vertex AI Search 資料儲存庫中進行搜尋。 | 企業知識庫搜尋、文件檢索與 Grounding。 | Vertex AI Search Data Store |

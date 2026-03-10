# 模型上下文協定 (Model Context Protocol, MCP)

> 🔔 `更新日期：2026-01-30`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/mcp/

[`ADK 支援`: `Python` | `TypeScript` | `Go` | `Java`]

[模型上下文協定 (Model Context Protocol, MCP)](https://modelcontextprotocol.io/introduction) 是一個開放標準，旨在標準化 Gemini 和 Claude 等大型語言模型 (LLM) 與外部應用程式、資料來源及工具之間的通訊方式。您可以將其視為一種通用的連接機制，簡化了 LLM 獲取上下文、執行操作以及與各種系統互動的方式。

## MCP 如何運作？

MCP 遵循用戶端-伺服器架構，定義了 MCP 伺服器如何公開資料 (資源)、互動式範本 (提示) 和可執行功能 (工具)，並由 MCP 用戶端 (可能是 LLM 託管應用程式或 AI 代理) 使用。

## ADK 中的 MCP 工具

ADK 可協助您在代理中同時使用和提供 MCP 工具，無論您是嘗試建立呼叫 MCP 服務的工具，還是公開 MCP 伺服器以便其他開發人員或代理與您的工具互動。

請參考 [MCP 工具文件](../custom-tools/mcp-tools.md) 以取得程式碼範例和設計模式，協助您將 ADK 與 MCP 伺服器結合使用，包括：

- **在 ADK 中使用現有的 MCP 伺服器**：ADK 代理可以充當 MCP 用戶端，並使用外部 MCP 伺服器提供的工具。
- **透過 MCP 伺服器公開 ADK 工具**：如何建立一個包裝 ADK 工具的 MCP 伺服器，使任何 MCP 用戶端都能存取這些工具。

## 用於資料庫的 MCP 工具箱 (MCP Toolbox for Databases)

[用於資料庫的 MCP 工具箱 (MCP Toolbox for Databases)](https://github.com/googleapis/genai-toolbox) 是一個開源的 MCP 伺服器，它將您的後端資料來源安全地公開為一組預先建立、可用於生產環境的工具，供生成式 AI 代理使用。它作為一個通用的抽象層，允許您的 ADK 代理在內建支援下，安全地查詢、分析和檢索來自各種資料庫的資訊。

MCP 工具箱伺服器包含一個全面的連接器函式庫，確保代理可以安全地與您複雜的資料資產進行互動。

### 支援的資料來源

MCP 工具箱為以下資料庫和資料平台提供現成的工具集：

#### Google Cloud

*   [BigQuery](https://googleapis.github.io/genai-toolbox/resources/sources/bigquery/) (包括 SQL 執行、結構定義探索和 AI 驅動的時間序列預測工具)
*   [AlloyDB](https://googleapis.github.io/genai-toolbox/resources/sources/alloydb-pg/) (與 PostgreSQL 相容，提供標準查詢和自然語言查詢工具)
*   [AlloyDB Admin](https://googleapis.github.io/genai-toolbox/resources/sources/alloydb-admin/)
*   [Spanner](https://googleapis.github.io/genai-toolbox/resources/sources/spanner/) (支援 GoogleSQL 和 PostgreSQL 方言)
*   Cloud SQL (專門支援 [Cloud SQL for PostgreSQL](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-sql-pg/)、[Cloud SQL for MySQL](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-sql-mysql/) 和 [Cloud SQL for SQL Server](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-sql-mssql/))
*   [Cloud SQL Admin](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-sql-admin/)
*   [Firestore](https://googleapis.github.io/genai-toolbox/resources/sources/firestore/)
*   [Bigtable](https://googleapis.github.io/genai-toolbox/resources/sources/bigtable/)
*   [Dataplex](https://googleapis.github.io/genai-toolbox/resources/sources/dataplex/) (用於資料探索和元資料搜尋)
*   [Cloud Monitoring](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-monitoring/)

#### 關聯式與 SQL 資料庫

*   [PostgreSQL](https://googleapis.github.io/genai-toolbox/resources/sources/postgres/) (通用)
*   [MySQL](https://googleapis.github.io/genai-toolbox/resources/sources/mysql/) (通用)
*   [Microsoft SQL Server](https://googleapis.github.io/genai-toolbox/resources/sources/mssql/) (通用)
*   [ClickHouse](https://googleapis.github.io/genai-toolbox/resources/sources/clickhouse/)
*   [TiDB](https://googleapis.github.io/genai-toolbox/resources/sources/tidb/)
*   [OceanBase](https://googleapis.github.io/genai-toolbox/resources/sources/oceanbase/)
*   [Firebird](https://googleapis.github.io/genai-toolbox/resources/sources/firebird/)
*   [SQLite](https://googleapis.github.io/genai-toolbox/resources/sources/sqlite/)
*   [YugabyteDB](https://googleapis.github.io/genai-toolbox/resources/sources/yugabytedb/)

#### NoSQL 與 鍵值存儲 (Key-Value Stores)

*   [MongoDB](https://googleapis.github.io/genai-toolbox/resources/sources/mongodb/)
*   [Couchbase](https://googleapis.github.io/genai-toolbox/resources/sources/couchbase/)
*   [Redis](https://googleapis.github.io/genai-toolbox/resources/sources/redis/)
*   [Valkey](https://googleapis.github.io/genai-toolbox/resources/sources/valkey/)
*   [Cassandra](https://googleapis.github.io/genai-toolbox/resources/sources/cassandra/)

#### 圖形資料庫 (Graph Databases)

*   [Neo4j](https://googleapis.github.io/genai-toolbox/resources/sources/neo4j/) (提供 Cypher 查詢和結構檢查工具)
*   [Dgraph](https://googleapis.github.io/genai-toolbox/resources/sources/dgraph/)

#### 資料平台與聯邦 (Data Platforms & Federation)

*   [Looker](https://googleapis.github.io/genai-toolbox/resources/sources/looker/) (用於透過 Looker API 執行 Looks、查詢和建立儀表板)
*   [Trino](https://googleapis.github.io/genai-toolbox/resources/sources/trino/) (用於跨多個來源執行聯邦查詢)

#### 其他

*   [HTTP](https://googleapis.github.io/genai-toolbox/resources/sources/http/)

### 文件

請參考 [用於資料庫的 MCP 工具箱](../tools-and-integrations/integrations/mcp-toolbox-for-databases.md) 文件，瞭解如何將 ADK 與用於資料庫的 MCP 工具箱結合使用。若要開始使用用於資料庫的 MCP 工具箱，也可以參考部落格文章 [教學：用於資料庫的 MCP 工具箱 - 公開 Big Query 資料集](https://medium.com/google-cloud/tutorial-mcp-toolbox-for-databases-exposing-big-query-datasets-9321f0064f4e) 和 Codelab [用於資料庫的 MCP 工具箱：讓 BigQuery 資料集可供 MCP 用戶端使用](https://codelabs.developers.google.com/mcp-toolbox-bigquery-dataset?hl=en#0)。

![GenAI 工具箱](https://google.github.io/adk-docs/assets/mcp_db_toolbox.png)

## ADK 代理與 FastMCP 伺服器
[FastMCP](https://github.com/jlowin/fastmcp) 處理所有複雜的 MCP 協定細節和伺服器管理，因此您可以專注於建立出色的工具。它被設計為高階且符合 Python 習慣 (Pythonic)；在大多數情況下，只需裝飾一個函式即可。

請參考 [MCP 工具文件](../custom-tools/mcp-tools.md) 文件，瞭解如何將 ADK 與在 Cloud Run 上執行的 FastMCP 伺服器結合使用。

## Google Cloud 生成式媒體 (Genmedia) 的 MCP 伺服器

[用於生成式媒體服務的 MCP 工具 (MCP Tools for Genmedia Services)](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia) 是一組開源的 MCP 伺服器，可讓您將 Google Cloud 生成式媒體服務 (例如 Imagen、Veo、Chirp 3 HD voices 和 Lyria) 整合到您的 AI 應用程式中。

代理開發套件 (ADK) 和 [Genkit](https://genkit.dev/) 提供對這些 MCP 工具的內建支援，讓您的 AI 代理能夠有效率地編排生成式媒體工作流程。如需實作指南，請參考 [ADK 範例代理](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia/sample-agents/adk) 和 [Genkit 範例](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia/sample-agents/genkit)。

### 實作範例

-   [`Genmedia Agent`](../../python/agents/genmedia-agent/): 使用 MCP 工具與 Google Cloud 生成式媒體服務互動，以建立包含圖像和語音的多媒體內容。

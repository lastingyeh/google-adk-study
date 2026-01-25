# Agent 工具 (Tools for Agents)

> 🔔 `更新日期：2026-01-24`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/tools/

以下為可與 ADK agent 搭配使用的預建工具目錄與使用說明。

## Gemini API 工具
| 序號 | 名稱                        | 說明                                     | 連結                                             |
| ---: | --------------------------- | ---------------------------------------- | ------------------------------------------------ |
|    1 | Google 搜尋 (Google Search) | 搭配 Gemini 使用 Google 搜尋執行網頁搜尋 | [google-search](./gemini-api/google-search.md)   |
|    2 | 程式碼執行 (Code Execution) | 使用 Gemini 模型執行程式碼並進行除錯     | [code-execution](./gemini-api/code-execution.md) |
|    3 | 電腦使用 (Computer Use)     | 使用 Gemini 模型操作電腦使用者介面       | [computer-use](./gemini-api/computer-use.md)     |

## Google Cloud 工具
| 序號 | 名稱                                              | 說明                                                | 連結                                                                     |
| ---: | ------------------------------------------------- | --------------------------------------------------- | ------------------------------------------------------------------------ |
|    1 | Apigee API Hub                                    | 將 Apigee API hub 中任何已記載的 API 轉換為工具     | [apigee-api-hub](./google-cloud/apigee-api-hub.md)                       |
|    2 | API 註冊表 (API Registry)                         | 以 MCP 工具的形式動態連接 Google Cloud 服務         | [api-registry](./google-cloud/api-registry.md)                           |
|    3 | 應用程式整合 (Application Integration)            | 使用整合連接器將您的 agent 連結到企業應用程式       | [application-integration](./google-cloud/application-integration.md)     |
|    4 | BigQuery Agent 分析                               | 大規模分析及除錯 agent 行為                         | [bigquery-agent-analytics](./google-cloud/bigquery-agent-analytics.md)   |
|    5 | BigQuery 工具                                     | 連接 BigQuery 以擷取數據並進行分析                  | [bigquery](./google-cloud/bigquery.md)                                   |
|    6 | Bigtable 工具                                     | 與 Bigtable 互動以擷取數據並執行 SQL                | [bigtable](./google-cloud/bigtable.md)                                   |
|    7 | GKE 程式碼執行器 (GKE Code Executor)              | 在安全且可擴充的 GKE 環境中執行 AI 生成的程式碼     | [gke-code-executor](./google-cloud/gke-code-executor.md)                 |
|    8 | Spanner 工具                                      | 與 Spanner 互動以擷取數據、搜尋並執行 SQL           | [spanner](./google-cloud/spanner.md)                                     |
|    9 | 資料庫專用 MCP 工具箱 (MCP Toolbox for Databases) | 為您的 agent 連接超過 30 種不同的資料來源           | [mcp-toolbox-for-databases](./google-cloud/mcp-toolbox-for-databases.md) |
|   10 | Vertex AI RAG 引擎                                | 使用 Vertex AI RAG 引擎執行私有數據擷取             | [vertex-ai-rag-engine](./google-cloud/vertex-ai-rag-engine.md)           |
|   11 | Vertex AI 搜尋 (Vertex AI Search)                 | 在 Vertex AI 搜尋中搜尋您的私有、已配置的資料儲存庫 | [vertex-ai-search](./google-cloud/vertex-ai-search.md)                   |

## 第三方工具
| 序號 | 名稱         | 說明                                           | 連結                                                              |
| ---: | ------------ | ---------------------------------------------- | ----------------------------------------------------------------- |
|    1 | Asana        | 管理專案、任務和目標以進行團隊協作             | https://google.github.io/adk-docs/tools/third-party/asana/        |
|    2 | Atlassian    | 管理問題、搜尋頁面並更新團隊內容               | https://google.github.io/adk-docs/tools/third-party/atlassian/    |
|    3 | Cartesia     | 生成語音、在地化聲音並建立音訊內容             | https://google.github.io/adk-docs/tools/third-party/cartesia/     |
|    4 | ElevenLabs   | 生成語音、複製聲音、轉錄音訊並建立音效         | https://google.github.io/adk-docs/tools/third-party/elevenlabs/   |
|    5 | GitHub       | 分析程式碼、管理 Issue 和 PR，並自動化工作流程 | https://google.github.io/adk-docs/tools/third-party/github/       |
|    6 | GitLab       | 執行語義程式碼搜尋、檢查流水線、管理合併請求   | https://google.github.io/adk-docs/tools/third-party/gitlab/       |
|    7 | Hugging Face | 存取模型、資料集、研究論文和 AI 工具           | https://google.github.io/adk-docs/tools/third-party/hugging-face/ |
|    8 | Linear       | 管理問題、追蹤專案並簡化開發流程               | https://google.github.io/adk-docs/tools/third-party/linear/       |
|    9 | n8n          | 觸發自動化工作流程、連接應用程式並處理資料     | https://google.github.io/adk-docs/tools/third-party/n8n/          |
|   10 | Notion       | 搜尋工作區、建立頁面並管理任務和資料庫         | https://google.github.io/adk-docs/tools/third-party/notion/       |
|   11 | Postman      | 管理 API 集合、工作區並生成客戶端程式碼        | https://google.github.io/adk-docs/tools/third-party/postman/      |
|   12 | Paypal       | 管理付款、發送發票並處理訂閱                   | https://google.github.io/adk-docs/tools/third-party/paypal/       |
|   13 | Qdrant       | 使用語義向量搜尋儲存和擷取資訊                 | https://google.github.io/adk-docs/tools/third-party/qdrant/       |
|   14 | Stripe       | 管理付款、客戶、訂閱和發票                     | https://google.github.io/adk-docs/tools/third-party/stripe/       |

---

## 在 ADK agent 中使用預建工具(pre-built tools with ADK Agents)
1. 匯入 (Import)：從工具模組匯入所需工具。
     - Python: `agents.tools`
     - TypeScript: `@google/adk`
     - Go: `google.golang.org/adk/tool`
     - Java: `com.google.adk.tools`
2. 配置 (Configure)：初始化工具並提供必要參數。
3. 註冊 (Register)：將初始化的工具加入 Agent 的 tools 列表。

  Agent 會在需要時根據提示呼叫已註冊的工具，框架負責執行與回傳。

> [!NOTE] 注意：使用多種工具的限制
注意：某些工具無法與同一 agent 中的其他工具同時使用。請參閱 ADK 工具的限制以取得詳細資訊 [limitations](./limitations.md)。

## 為 agent 建立工具（擴充指南）
- 函式工具 [Function Tools](../custom-tools/function-tools/overview.md)：為特定 agent 行為建立自定義函式工具。
- MCP 工具 [MCP Tools](../custom-tools/mcp-tools.md)：將 MCP 伺服器連接為 agent 可呼叫的工具。
- OpenAPI 整合 [Openapi Tools](../custom-tools/openapi-tools.md)：從 OpenAPI 規格生成可呼叫的工具介面。

---
若需更詳細範例或程式碼片段，請參考各工具對應的連結頁面。
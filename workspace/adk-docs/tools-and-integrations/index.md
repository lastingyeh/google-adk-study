# Agents 工具與整合

查看以下預先建置的工具與整合，您可以搭配 ADK agents 使用。如需建置自訂工具的相關資訊,請參閱[自訂工具](../custom-tools/index.md)。如需提交整合到目錄的相關資訊，請參閱[整合貢獻指南](https://github.com/google/adk-docs/blob/main/CONTRIBUTING.md#integrations)。

**篩選**：[所有項目](#所有項目) [程式碼](#程式碼) • [連接器](#連接器) • [資料](#資料) • [Google](#google) • [MCP](#mcp) • [可觀測性](#可觀測性) • [搜尋](#搜尋)

## 所有項目

| 工具名稱 | 說明 |
|---------|------|
| [AG-UI](integrations/ag-ui.md) | 使用串流、狀態同步及 agentic 動作建置互動式聊天 UI |
| [AgentMail](integrations/agentmail.md) | 為 AI agents 建立電子郵件收件匣以傳送、接收及管理訊息 |
| [AgentOps](integrations/agentops.md) | ADK agents 的工作階段重播、指標及監控 |
| [Google Cloud API Registry](integrations/api-registry.md) | 以 MCP 工具形式連接 Google Cloud 服務 |
| [Apigee API Hub](integrations/apigee-api-hub.md) | 將 Apigee API Hub 中任何已記錄的 API 轉換為工具 |
| [Application Integration](integrations/application-integration.md) | 使用整合連接器將 agents 連結至企業應用程式 |
| [Arize AX](integrations/arize-ax.md) | LLM 應用程式的生產級可觀測性、偵錯及改進 |
| [Asana](integrations/asana.md) | 管理專案、工作及目標以進行團隊協作 |
| [Atlassian](integrations/atlassian.md) | 管理問題、搜尋頁面並更新團隊內容 |
| [BigQuery Agent Analytics Plugin](integrations/bigquery-agent-analytics.md) | 針對行為分析和記錄的深入 agent 分析 |
| [BigQuery Tools](https://google.github.io/adk-docs/integrations/bigquery/) | 連接 BigQuery 以擷取資料並執行分析 |
| [Bigtable Tools](https://google.github.io/adk-docs/integrations/bigtable/) | 與 Bigtable 互動以擷取資料並執行 SQL |
| [Cartesia](https://google.github.io/adk-docs/integrations/cartesia/) | 產生語音、本地化語音並建立音訊內容 |
| [Chroma](https://google.github.io/adk-docs/integrations/chroma/) | 使用語義向量搜尋儲存和擷取資訊 |
| [Google Cloud Trace](https://google.github.io/adk-docs/integrations/cloud-trace/) | 監控、偵錯及追蹤 ADK agent 互動 |
| [Code Execution Tool with Agent Engine](https://google.github.io/adk-docs/integrations/code-exec-agent-engine/) | 在安全且可擴展的 GKE 環境中執行 AI 生成的程式碼 |
| [Code Execution](https://google.github.io/adk-docs/integrations/code-execution/) | 使用 Gemini 模型執行程式碼並進行偵錯 |
| [Computer Use](https://google.github.io/adk-docs/integrations/computer-use/) | 使用 Gemini 模型操作電腦使用者介面 |
| [Data Agents](https://google.github.io/adk-docs/integrations/data-agent/) | 使用 AI 驅動的 agents 進行資料分析 |
| [Daytona](https://google.github.io/adk-docs/integrations/daytona/) | 在安全沙箱中執行程式碼、執行 Shell 指令和管理檔案 |
| [ElevenLabs](https://google.github.io/adk-docs/integrations/elevenlabs/) | 產生語音、複製語音、轉錄音訊並建立音效 |
| [Vertex AI express mode](https://google.github.io/adk-docs/integrations/express-mode/) | 以零成本試用 Vertex AI 服務開發 |
| [Freeplay](https://google.github.io/adk-docs/integrations/freeplay/) | 使用 Freeplay 透過端對端可觀測性建置、最佳化及評估 AI agents |
| [GitHub](https://google.github.io/adk-docs/integrations/github/) | 分析程式碼、管理問題和 PR，以及自動化工作流程 |
| [GitLab](https://google.github.io/adk-docs/integrations/gitlab/) | 執行語義程式碼搜尋、檢查管道、管理合併請求 |
| [GKE Code Executor](https://google.github.io/adk-docs/integrations/gke-code-executor/) | 在安全且可擴展的 GKE 環境中執行 AI 生成的程式碼 |
| [GoodMem](https://google.github.io/adk-docs/integrations/goodmem/) | 在對話間為 agents 新增持久的語義記憶 |
| [Google Search](https://google.github.io/adk-docs/integrations/google-search/) | 使用 Google Search 搭配 Gemini 執行網路搜尋 |
| [Hugging Face](https://google.github.io/adk-docs/integrations/hugging-face/) | 存取模型、資料集、研究論文及 AI 工具 |
| [Linear](https://google.github.io/adk-docs/integrations/linear/) | 管理問題、追蹤專案並簡化開發 |
| [Mailgun](https://google.github.io/adk-docs/integrations/mailgun/) | 傳送電子郵件、追蹤傳遞指標並管理郵寄清單 |
| [MCP Toolbox for Databases](https://google.github.io/adk-docs/integrations/mcp-toolbox-for-databases/) | 將 30+ 個不同的資料來源連接到您的 agents |
| [MLflow](https://google.github.io/adk-docs/integrations/mlflow/) | 擷取 agent 執行、工具呼叫及模型要求的 OpenTelemetry 追蹤 |
| [MongoDB](https://google.github.io/adk-docs/integrations/mongodb/) | 查詢集合、管理資料庫及分析結構描述 |
| [Monocle](https://google.github.io/adk-docs/integrations/monocle/) | LLM 應用程式的開源可觀測性、追蹤及偵錯 |
| [n8n](https://google.github.io/adk-docs/integrations/n8n/) | 觸發自動化工作流程、連接應用程式及處理資料 |
| [Notion](https://google.github.io/adk-docs/integrations/notion/) | 搜尋工作區、建立頁面、管理工作與資料庫 |
| [Paypal](https://google.github.io/adk-docs/integrations/paypal/) | 管理付款、傳送發票並處理訂閱 |
| [Phoenix](https://google.github.io/adk-docs/integrations/phoenix/) | LLM 應用程式的開源、自我託管的可觀測性、追蹤及評估 |
| [Pinecone](https://google.github.io/adk-docs/integrations/pinecone/) | 儲存資料、執行語義搜尋及重新排名結果 |
| [Postman](https://google.github.io/adk-docs/integrations/postman/) | 管理 API 集合、工作區及產生用戶端程式碼 |
| [Pub/Sub Tools](https://google.github.io/adk-docs/integrations/pubsub/) | 發佈、提取及確認來自 Google Cloud Pub/Sub 的訊息 |
| [Qdrant](https://google.github.io/adk-docs/integrations/qdrant/) | 使用語義向量搜尋儲存和擷取資訊 |
| [Reflect and Retry Plugin](https://google.github.io/adk-docs/integrations/reflect-and-retry/) | 自動重試失敗的工具呼叫 |
| [Restate](https://google.github.io/adk-docs/integrations/restate/) | 具有耐久工作階段和人工核准功能的恢復力 agent 執行及協調 |
| [Spanner Tools](https://google.github.io/adk-docs/integrations/spanner/) | 與 Spanner 互動以擷取資料、搜尋及執行 SQL |
| [StackOne](https://google.github.io/adk-docs/integrations/stackone/) | 將 agents 連接到 200+ SaaS 提供者 |
| [Stripe](https://google.github.io/adk-docs/integrations/stripe/) | 管理付款、客戶、訂閱及發票 |
| [Supermetrics](https://google.github.io/adk-docs/integrations/supermetrics/) | 使用和分析來自 325+ 個平台的即時行銷、廣告及 CRM 資料 |
| [Vertex AI RAG Engine](https://google.github.io/adk-docs/integrations/vertex-ai-rag-engine/) | 使用 Vertex AI RAG Engine 進行私人資料擷取 |
| [Vertex AI Search](https://google.github.io/adk-docs/integrations/vertex-ai-search/) | 在 Vertex AI Search 中搜尋您的私人設定資料存放區 |
| [W&B Weave](https://google.github.io/adk-docs/integrations/weave/) | 記錄、視覺化及分析模型呼叫和 agent 效能 |
| [Windsor.ai](https://google.github.io/adk-docs/integrations/windsor-ai/) | 查詢並分析來自 325+ 個平台的行銷、銷售及客戶資料 |

---

### 程式碼

| 工具名稱 | 說明 |
|---------|------|
| [Code Execution Tool with Agent Engine](https://google.github.io/adk-docs/integrations/code-exec-agent-engine/) | 在安全且可擴展的 GKE 環境中執行 AI 生成的程式碼 |
| [Code Execution](https://google.github.io/adk-docs/integrations/code-execution/) | 使用 Gemini 模型執行程式碼並進行偵錯 |
| [Daytona](https://google.github.io/adk-docs/integrations/daytona/) | 在安全沙箱中執行程式碼、執行 Shell 指令和管理檔案 |
| [GitHub](https://google.github.io/adk-docs/integrations/github/) | 分析程式碼、管理問題和 PR，以及自動化工作流程 |
| [GitLab](https://google.github.io/adk-docs/integrations/gitlab/) | 執行語義程式碼搜尋、檢查管道、管理合併請求 |
| [GKE Code Executor](https://google.github.io/adk-docs/integrations/gke-code-executor/) | 在安全且可擴展的 GKE 環境中執行 AI 生成的程式碼 |

### 連接器

| 工具名稱 | 說明 |
|---------|------|
| [Google Cloud API Registry](integrations/api-registry.md) | 以 MCP 工具形式連接 Google Cloud 服務 |
| [Apigee API Hub](integrations/apigee-api-hub.md) | 將 Apigee API Hub 中任何已記錄的 API 轉換為工具 |
| [Application Integration](integrations/application-integration.md) | 使用整合連接器將 agents 連結至企業應用程式 |
| [n8n](https://google.github.io/adk-docs/integrations/n8n/) | 觸發自動化工作流程、連接應用程式及處理資料 |
| [StackOne](https://google.github.io/adk-docs/integrations/stackone/) | 將 agents 連接到 200+ SaaS 提供者 |

### 資料

| 工具名稱 | 說明 |
|---------|------|
| [BigQuery Tools](https://google.github.io/adk-docs/integrations/bigquery/) | 連接 BigQuery 以擷取資料並執行分析 |
| [Bigtable Tools](https://google.github.io/adk-docs/integrations/bigtable/) | 與 Bigtable 互動以擷取資料並執行 SQL |
| [Chroma](https://google.github.io/adk-docs/integrations/chroma/) | 使用語義向量搜尋儲存和擷取資訊 |
| [Data Agents](https://google.github.io/adk-docs/integrations/data-agent/) | 使用 AI 驅動的 agents 進行資料分析 |
| [GoodMem](https://google.github.io/adk-docs/integrations/goodmem/) | 在對話間為 agents 新增持久的語義記憶 |
| [MCP Toolbox for Databases](https://google.github.io/adk-docs/integrations/mcp-toolbox-for-databases/) | 將 30+ 個不同的資料來源連接到您的 agents |
| [MongoDB](https://google.github.io/adk-docs/integrations/mongodb/) | 查詢集合、管理資料庫及分析結構描述 |
| [Pinecone](https://google.github.io/adk-docs/integrations/pinecone/) | 儲存資料、執行語義搜尋及重新排名結果 |
| [Qdrant](https://google.github.io/adk-docs/integrations/qdrant/) | 使用語義向量搜尋儲存和擷取資訊 |
| [Spanner Tools](https://google.github.io/adk-docs/integrations/spanner/) | 與 Spanner 互動以擷取資料、搜尋及執行 SQL |
| [Supermetrics](https://google.github.io/adk-docs/integrations/supermetrics/) | 使用和分析來自 325+ 個平台的即時行銷、廣告及 CRM 資料 |
| [Vertex AI RAG Engine](https://google.github.io/adk-docs/integrations/vertex-ai-rag-engine/) | 使用 Vertex AI RAG Engine 進行私人資料擷取 |
| [Windsor.ai](https://google.github.io/adk-docs/integrations/windsor-ai/) | 查詢並分析來自 325+ 個平台的行銷、銷售及客戶資料 |

### Google

| 工具名稱 | 說明 |
|---------|------|
| [Google Cloud API Registry](integrations/api-registry.md) | 以 MCP 工具形式連接 Google Cloud 服務 |
| [Apigee API Hub](integrations/apigee-api-hub.md) | 將 Apigee API Hub 中任何已記錄的 API 轉換為工具 |
| [Application Integration](integrations/application-integration.md) | 使用整合連接器將 agents 連結至企業應用程式 |
| [BigQuery Agent Analytics Plugin](integrations/bigquery-agent-analytics.md) | 針對行為分析和記錄的深入 agent 分析 |
| [BigQuery Tools](https://google.github.io/adk-docs/integrations/bigquery/) | 連接 BigQuery 以擷取資料並執行分析 |
| [Bigtable Tools](https://google.github.io/adk-docs/integrations/bigtable/) | 與 Bigtable 互動以擷取資料並執行 SQL |
| [Google Cloud Trace](https://google.github.io/adk-docs/integrations/cloud-trace/) | 監控、偵錯及追蹤 ADK agent 互動 |
| [Code Execution Tool with Agent Engine](https://google.github.io/adk-docs/integrations/code-exec-agent-engine/) | 在安全且可擴展的 GKE 環境中執行 AI 生成的程式碼 |
| [Code Execution](https://google.github.io/adk-docs/integrations/code-execution/) | 使用 Gemini 模型執行程式碼並進行偵錯 |
| [Computer Use](https://google.github.io/adk-docs/integrations/computer-use/) | 使用 Gemini 模型操作電腦使用者介面 |
| [Data Agents](https://google.github.io/adk-docs/integrations/data-agent/) | 使用 AI 驅動的 agents 進行資料分析 |
| [Vertex AI express mode](https://google.github.io/adk-docs/integrations/express-mode/) | 以零成本試用 Vertex AI 服務開發 |
| [GKE Code Executor](https://google.github.io/adk-docs/integrations/gke-code-executor/) | 在安全且可擴展的 GKE 環境中執行 AI 生成的程式碼 |
| [Google Search](https://google.github.io/adk-docs/integrations/google-search/) | 使用 Google Search 搭配 Gemini 執行網路搜尋 |
| [MCP Toolbox for Databases](https://google.github.io/adk-docs/integrations/mcp-toolbox-for-databases/) | 將 30+ 個不同的資料來源連接到您的 agents |
| [Pub/Sub Tools](https://google.github.io/adk-docs/integrations/pubsub/) | 發佈、提取及確認來自 Google Cloud Pub/Sub 的訊息 |
| [Reflect and Retry Plugin](https://google.github.io/adk-docs/integrations/reflect-and-retry/) | 自動重試失敗的工具呼叫 |
| [Spanner Tools](https://google.github.io/adk-docs/integrations/spanner/) | 與 Spanner 互動以擷取資料、搜尋及執行 SQL |
| [Vertex AI RAG Engine](https://google.github.io/adk-docs/integrations/vertex-ai-rag-engine/) | 使用 Vertex AI RAG Engine 進行私人資料擷取 |
| [Vertex AI Search](https://google.github.io/adk-docs/integrations/vertex-ai-search/) | 在 Vertex AI Search 中搜尋您的私人設定資料存放區 |

### MCP

| 工具名稱 | 說明 |
|---------|------|
| [AgentMail](integrations/agentmail.md) | 為 AI agents 建立電子郵件收件匣以傳送、接收及管理訊息 |
| [Google Cloud API Registry](integrations/api-registry.md) | 以 MCP 工具形式連接 Google Cloud 服務 |
| [Asana](integrations/asana.md) | 管理專案、工作及目標以進行團隊協作 |
| [Atlassian](integrations/atlassian.md) | 管理問題、搜尋頁面並更新團隊內容 |
| [Cartesia](https://google.github.io/adk-docs/integrations/cartesia/) | 產生語音、本地化語音並建立音訊內容 |
| [Chroma](https://google.github.io/adk-docs/integrations/chroma/) | 使用語義向量搜尋儲存和擷取資訊 |
| [ElevenLabs](https://google.github.io/adk-docs/integrations/elevenlabs/) | 產生語音、複製語音、轉錄音訊並建立音效 |
| [GitHub](https://google.github.io/adk-docs/integrations/github/) | 分析程式碼、管理問題和 PR，以及自動化工作流程 |
| [GitLab](https://google.github.io/adk-docs/integrations/gitlab/) | 執行語義程式碼搜尋、檢查管道、管理合併請求 |
| [Hugging Face](https://google.github.io/adk-docs/integrations/hugging-face/) | 存取模型、資料集、研究論文及 AI 工具 |
| [Linear](https://google.github.io/adk-docs/integrations/linear/) | 管理問題、追蹤專案並簡化開發 |
| [Mailgun](https://google.github.io/adk-docs/integrations/mailgun/) | 傳送電子郵件、追蹤傳遞指標並管理郵寄清單 |
| [MCP Toolbox for Databases](https://google.github.io/adk-docs/integrations/mcp-toolbox-for-databases/) | 將 30+ 個不同的資料來源連接到您的 agents |
| [MongoDB](https://google.github.io/adk-docs/integrations/mongodb/) | 查詢集合、管理資料庫及分析結構描述 |
| [n8n](https://google.github.io/adk-docs/integrations/n8n/) | 觸發自動化工作流程、連接應用程式及處理資料 |
| [Notion](https://google.github.io/adk-docs/integrations/notion/) | 搜尋工作區、建立頁面、管理工作與資料庫 |
| [Paypal](https://google.github.io/adk-docs/integrations/paypal/) | 管理付款、傳送發票並處理訂閱 |
| [Pinecone](https://google.github.io/adk-docs/integrations/pinecone/) | 儲存資料、執行語義搜尋及重新排名結果 |
| [Postman](https://google.github.io/adk-docs/integrations/postman/) | 管理 API 集合、工作區及產生用戶端程式碼 |
| [Qdrant](https://google.github.io/adk-docs/integrations/qdrant/) | 使用語義向量搜尋儲存和擷取資訊 |
| [Stripe](https://google.github.io/adk-docs/integrations/stripe/) | 管理付款、客戶、訂閱及發票 |
| [Supermetrics](https://google.github.io/adk-docs/integrations/supermetrics/) | 使用和分析來自 325+ 個平台的即時行銷、廣告及 CRM 資料 |
| [Windsor.ai](https://google.github.io/adk-docs/integrations/windsor-ai/) | 查詢並分析來自 325+ 個平台的行銷、銷售及客戶資料 |

### 可觀測性

| 工具名稱 | 說明 |
|---------|------|
| [AgentOps](integrations/agentops.md) | ADK agents 的工作階段重播、指標及監控 |
| [Arize AX](integrations/arize-ax.md) | LLM 應用程式的生產級可觀測性、偵錯及改進 |
| [BigQuery Agent Analytics Plugin](integrations/bigquery-agent-analytics.md) | 針對行為分析和記錄的深入 agent 分析 |
| [Google Cloud Trace](https://google.github.io/adk-docs/integrations/cloud-trace/) | 監控、偵錯及追蹤 ADK agent 互動 |
| [Freeplay](https://google.github.io/adk-docs/integrations/freeplay/) | 使用 Freeplay 透過端對端可觀測性建置、最佳化及評估 AI agents |
| [MLflow](https://google.github.io/adk-docs/integrations/mlflow/) | 擷取 agent 執行、工具呼叫及模型要求的 OpenTelemetry 追蹤 |
| [Monocle](https://google.github.io/adk-docs/integrations/monocle/) | LLM 應用程式的開源可觀測性、追蹤及偵錯 |
| [Phoenix](https://google.github.io/adk-docs/integrations/phoenix/) | LLM 應用程式的開源、自我託管的可觀測性、追蹤及評估 |
| [W&B Weave](https://google.github.io/adk-docs/integrations/weave/) | 記錄、視覺化及分析模型呼叫和 agent 效能 |

### 搜尋

| 工具名稱 | 說明 |
|---------|------|
| [Google Search](https://google.github.io/adk-docs/integrations/google-search/) | 使用 Google Search 搭配 Gemini 執行網路搜尋 |
| [Vertex AI Search](https://google.github.io/adk-docs/integrations/vertex-ai-search/) | 在 Vertex AI Search 中搜尋您的私人設定資料存放區 |

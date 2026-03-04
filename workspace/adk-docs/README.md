# Google ADK 文件學習指南

🔔 `更新日期：2026 年 2 月 2 日`

---
🪧 `以官方文件 (Google ADK Docs) 為基礎的學習資源`

✍️ `作者：Lastingyeh`

歡迎來到 Google ADK 官方文件學習指南！本指南旨在協助您快速了解和掌握 Google ADK（Application Development Kit）的核心概念與功能。無論您是初學者還是經驗豐富的開發者，都能在此找到適合您的資源和建議。

### 版本發行 (Release Notes)

您可以在各支援語言的程式碼儲存庫中找到發行說明。有關 ADK 發行版本的詳細資訊，請參閱以下位置：

- [ADK Python 發行說明](https://github.com/google/adk-python/releases) (v1.23.0)
- [ADK TypeScript 發行說明](https://github.com/google/adk-js/releases) (v0.2.5)
- [ADK Go 發行說明](https://github.com/google/adk-go/releases) (v0.3.0)
- [ADK Java 發行說明](https://github.com/google/adk-java/releases) (v0.5.0)

### Agent Development Kit 簡介

Agent Development Kit (ADK) 是一個靈活且模組化的架構，用於**開發和部署 AI 代理 (AI agents)**。雖然針對 Gemini 和 Google 生態系統進行了優化，但 ADK 是**模型無關 (model-agnostic)**、**部署無關 (deployment-agnostic)**，並且是為了**與其他框架的相容性**而構建的。ADK 旨在讓代理開發感覺更像軟體開發，使開發人員更輕鬆地創建、部署和編排代理架構，涵蓋從簡單任務到複雜工作流的範圍。

[前往 Google ADK 文件](./index.md)

## 建立代理程式 (Building Agents)

### 快速入門 (Get started)

ADK 文件提供了多種程式語言的快速入門指南，可協助您在幾分鐘內建立您的第一個 ADK 代理程式。請選擇最適合您的語言：

| 語言           | 描述                                                                      | 快速入門連結                                       | 安裝指南                                             |
| :------------- | :------------------------------------------------------------------------ | :------------------------------------------------- | :--------------------------------------------------- |
| **快速入門**   | 探索 ADK 支援的各種程式語言的快速入門指南，幫助您快速建立第一個代理程式。 | [連結](./get-started/index.md)                     |                                                      |
| **Python**     | 在幾分鐘內建立您的第一個 Python ADK 代理程式。                            | [開始使用 Python](./get-started/python.md)         | [安裝說明](./get-started/Installation/python.md)     |
| **Go**         | 在幾分鐘內建立您的第一個 Go ADK 代理程式。                                | [開始使用 Go](./get-started/go.md)                 | [安裝說明](./get-started/Installation/go.md)         |
| **Java**       | 在幾分鐘內建立您的第一個 Java ADK 代理程式。                              | [開始使用 Java](./get-started/java.md)             | [安裝說明](./get-started/Installation/java.md)       |
| **TypeScript** | 在幾分鐘內建立您的第一個 TypeScript ADK 代理程式。                        | [開始使用 TypeScript](./get-started/typescript.md) | [安裝說明](./get-started/Installation/typescript.md) |

### 建立你的代理程式 (Build your Agent)

透過實踐指南系列，開始使用 ADK 構建各種類型的智慧代理。這些教學以循序漸進的方式設計，從基礎概念到進階的代理開發技術。

| 標頭                                                               | 描述                                                                                                   | 連結                                                   |
| :----------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------- | :----------------------------------------------------- |
| [教學總覽](./build-your-agent/tutorials/index.md)                  | 透過實踐指南系列學習 ADK，包含多工具代理、代理團隊、串流代理等教學內容。                               | [連結](./build-your-agent/tutorials/index.md)          |
| [代理團隊教學](./build-your-agent/tutorials/agent-team.md)         | 構建進階天氣機器人多代理系統，學習代理委派、會話管理、安全回呼等進階功能。                             | [連結](./build-your-agent/tutorials/agent-team.md)     |
| [使用 AI 進行編碼](./build-your-agent/tutorials/coding-with-ai.md) | 介紹如何使用 llms.txt 標準，在 AI 驅動的開發環境（Gemini CLI、Antigravity）中使用 ADK 文件作為上下文。 | [連結](./build-your-agent/tutorials/coding-with-ai.md) |

### 代理 (Agents)

在 ADK 中，代理 (Agent) 是一個獨立的執行單元，旨在自主行動以實現特定目標。ADK 提供不同的代理類別來建構複雜的應用程式，從智慧推理到結構化流程控制。以下整理本資料夾中與代理相關的主題與索引。

| 標頭                                                      | 描述                                                                                                                      | 連結                                                  |
| :-------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------ | :---------------------------------------------------- |
| [代理總覽](./agents/index.md)                             | 介紹 ADK 中的代理概念、核心代理類別 (LLM 代理、工作流代理、自訂代理)，以及如何選擇正確的代理類型。                        | [連結](./agents/index.md)                             |
| [LLM 代理](./agents/llm-agents.md)                        | 深入探討由大型語言模型驅動的 LlmAgent，包括定義代理身份、設定指令、配置工具與進階功能 (如規劃、程式碼執行等)。            | [連結](./agents/llm-agents.md)                        |
| [工作流代理](./agents/workflow-agents/index.md)           | 說明專門控制子代理執行流程的工作流代理，包括順序代理 (SequentialAgent)、平行代理 (ParallelAgent) 與迴圈代理 (LoopAgent)。 | [連結](./agents/workflow-agents/index.md)             |
| [順序代理](./agents/workflow-agents/sequential-agents.md) | 按照清單中指定的順序執行子代理，適合需要固定執行順序的工作流 (如程式碼開發管線)。                                         | [連結](./agents/workflow-agents/sequential-agents.md) |
| [迴圈代理](./agents/workflow-agents/loop-agents.md)       | 以迴圈方式重複執行子代理，直到達到指定迭代次數或滿足終止條件 (如迭代式文件優化)。                                         | [連結](./agents/workflow-agents/loop-agents.md)       |
| [平行代理](./agents/workflow-agents/parallel-agents.md)   | 同時執行多個子代理，適合獨立且資源密集型任務，能顯著提升處理速度 (如多源資料檢索)。                                       | [連結](./agents/workflow-agents/parallel-agents.md)   |
| [自訂代理](./agents/custom-agents.md)                     | 透過直接繼承 BaseAgent 實作自訂編排邏輯，提供極致靈活性以建構高度特定的代理工作流。                                       | [連結](./agents/custom-agents.md)                     |
| [多代理系統](./agents/multi-agents.md)                    | 說明如何將多個代理組合成多代理系統 (MAS)，包括代理層次結構、協作模式與交互機制。                                          | [連結](./agents/multi-agents.md)                      |
| [Agent Config](./agents/config.md)                        | 介紹如何使用 YAML 格式的 Agent Config 無需編寫程式碼即可構建 ADK 工作流 (實驗性功能)。                                    | [連結](./agents/config.md)                            |

### 代理模型 (Models for Agents)

ADK 允許您將各種大型語言模型 (LLM) 整合到您的代理程式中。本節介紹如何使用 Gemini 模型以及整合其他熱門模型,包括外部託管或本地運行的模型。ADK 主要使用兩種機制進行模型整合：直接字串/註冊表 (適用於 Google Cloud 模型) 和模型連接器 (適用於更廣泛的相容性)。

| 標頭                                                       | 描述                                                                                                                     | 連結                                         |
| :--------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------- | :------------------------------------------- |
| [模型總覽](./models-for-agents/index.md)                   | 介紹 ADK 支援的各種 AI 模型整合方式,包括直接字串/註冊表與模型連接器兩種整合機制,以及各模型類型的適用場景。               | [連結](./models-for-agents/index.md)         |
| [Google Gemini 模型](./models-for-agents/google-gemini.md) | 深入說明如何在 ADK 中使用 Google Gemini 系列模型,包括透過 Google AI Studio 或 Vertex AI 進行驗證,以及支援的進階功能。    | [連結](./models-for-agents/google-gemini.md) |
| [Vertex AI 託管模型](./models-for-agents/vertex.md)        | 說明如何使用部署到 Vertex AI 端點的模型,包括 Model Garden 模型、微調模型,以及透過 Vertex AI 使用的第三方模型如 Claude。  | [連結](./models-for-agents/vertex.md)        |
| [Anthropic Claude 模型](./models-for-agents/anthropic.md)  | 介紹如何在 Java ADK 中使用 Claude 包裝類別直接整合 Anthropic 的 Claude 模型,包括透過 Anthropic API 金鑰進行驗證。        | [連結](./models-for-agents/anthropic.md)     |
| [Apigee AI Gateway](./models-for-agents/apigee.md)         | 說明如何透過 Apigee AI 閘道器使用模型,提供企業級的模型安全、流量治理、效能優化與監控功能。                               | [連結](./models-for-agents/apigee.md)        |
| [LiteLLM 模型連接器](./models-for-agents/litellm.md)       | 介紹如何使用 LiteLLM 函式庫作為翻譯層,為超過 100 多個 LLM 提供標準化介面,包括 OpenAI、Anthropic、Cohere 等供應商的模型。 | [連結](./models-for-agents/litellm.md)       |
| [Ollama 模型託管](./models-for-agents/ollama.md)           | 說明如何透過 Ollama 在本地託管並運行開源模型,並透過 LiteLLM 與 ADK 整合,包括模型選擇與配置的最佳實踐。                   | [連結](./models-for-agents/ollama.md)        |
| [vLLM 模型託管](./models-for-agents/vllm.md)               | 介紹如何使用 vLLM 高效託管模型並將其作為與 OpenAI 相容的 API 端點,透過 LiteLLM 與 ADK 整合。                             | [連結](./models-for-agents/vllm.md)          |


### 代理工具與整合 (Tools and Integrations for Agents)

ADK 支援多種預建工具與整合，協助代理程式連結 Google 服務、第三方平台與資料來源。下表依功能分類整理常用工具，完整目錄與最新資訊請參閱[工具與整合目錄](./tools-and-integrations/index.md#所有項目)。

| 工具名稱 | 說明 |
|---------|------|
| [工具總覽](./tools-and-integrations/index.md) | ADK 支援的工具與整合總覽，涵蓋程式碼執行、資料連接、Google 服務等多種功能類別 |
| [AG-UI](./tools-and-integrations/integrations/ag-ui.md) | 使用串流、狀態同步及 agentic 動作建置互動式聊天 UI |
| [AgentMail](./tools-and-integrations/integrations/agentmail.md) | 為 AI agents 建立電子郵件收件匣以傳送、接收及管理訊息 |
| [AgentOps](./tools-and-integrations/integrations/agentops.md) | ADK agents 的工作階段重播、指標及監控 |
| [Google Cloud API Registry](./tools-and-integrations/integrations/api-registry.md) | 以 MCP 工具形式連接 Google Cloud 服務 |
| [Apigee API Hub](./tools-and-integrations/integrations/apigee-api-hub.md) | 將 Apigee API Hub 中任何已記錄的 API 轉換為工具 |
| [Application Integration](./tools-and-integrations/integrations/application-integration.md) | 使用整合連接器將 agents 連結至企業應用程式 |
| [Arize AX](./tools-and-integrations/integrations/arize-ax.md) | LLM 應用程式的生產級可觀測性、偵錯及改進 |
| [Asana](./tools-and-integrations/integrations/asana.md) | 管理專案、工作及目標以進行團隊協作 |
| [Atlassian](./tools-and-integrations/integrations/atlassian.md) | 管理問題、搜尋頁面並更新團隊內容 |
| [BigQuery Agent Analytics Plugin](./tools-and-integrations/integrations/bigquery-agent-analytics.md) | 針對行為分析和記錄的深入 agent 分析 |

#### 程式碼

| 工具名稱 | 說明 |
|---------|------|
| [Code Execution Tool with Agent Engine](https://google.github.io/adk-docs/integrations/code-exec-agent-engine/) | 在安全且可擴展的 GKE 環境中執行 AI 生成的程式碼 |
| [Code Execution](https://google.github.io/adk-docs/integrations/code-execution/) | 使用 Gemini 模型執行程式碼並進行偵錯 |
| [Daytona](https://google.github.io/adk-docs/integrations/daytona/) | 在安全沙箱中執行程式碼、執行 Shell 指令和管理檔案 |
| [GitHub](https://google.github.io/adk-docs/integrations/github/) | 分析程式碼、管理問題和 PR，以及自動化工作流程 |
| [GitLab](https://google.github.io/adk-docs/integrations/gitlab/) | 執行語義程式碼搜尋、檢查管道、管理合併請求 |
| [GKE Code Executor](https://google.github.io/adk-docs/integrations/gke-code-executor/) | 在安全且可擴展的 GKE 環境中執行 AI 生成的程式碼 |

#### 連接器

| 工具名稱 | 說明 |
|---------|------|
| [Google Cloud API Registry](./tools-and-integrations/integrations/api-registry.md) | 以 MCP 工具形式連接 Google Cloud 服務 |
| [Apigee API Hub](./tools-and-integrations/integrations/apigee-api-hub.md) | 將 Apigee API Hub 中任何已記錄的 API 轉換為工具 |
| [Application Integration](./tools-and-integrations/integrations/application-integration.md) | 使用整合連接器將 agents 連結至企業應用程式 |
| [n8n](https://google.github.io/adk-docs/integrations/n8n/) | 觸發自動化工作流程、連接應用程式及處理資料 |
| [StackOne](https://google.github.io/adk-docs/integrations/stackone/) | 將 agents 連接到 200+ SaaS 提供者 |

#### 資料

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

#### Google

| 工具名稱 | 說明 |
|---------|------|
| [Google Cloud API Registry](./tools-and-integrations/integrations/api-registry.md) | 以 MCP 工具形式連接 Google Cloud 服務 |
| [Apigee API Hub](./tools-and-integrations/integrations/apigee-api-hub.md) | 將 Apigee API Hub 中任何已記錄的 API 轉換為工具 |
| [Application Integration](./tools-and-integrations/integrations/application-integration.md) | 使用整合連接器將 agents 連結至企業應用程式 |
| [BigQuery Agent Analytics Plugin](./tools-and-integrations/integrations/bigquery-agent-analytics.md) | 針對行為分析和記錄的深入 agent 分析 |
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

#### MCP

| 工具名稱 | 說明 |
|---------|------|
| [AgentMail](./tools-and-integrations/integrations/agentmail.md) | 為 AI agents 建立電子郵件收件匣以傳送、接收及管理訊息 |
| [Google Cloud API Registry](./tools-and-integrations/integrations/api-registry.md) | 以 MCP 工具形式連接 Google Cloud 服務 |
| [Asana](./tools-and-integrations/integrations/asana.md) | 管理專案、工作及目標以進行團隊協作 |
| [Atlassian](./tools-and-integrations/integrations/atlassian.md) | 管理問題、搜尋頁面並更新團隊內容 |
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

#### 可觀測性

| 工具名稱 | 說明 |
|---------|------|
| [AgentOps](./tools-and-integrations/integrations/agentops.md) | ADK agents 的工作階段重播、指標及監控 |
| [Arize AX](./tools-and-integrations/integrations/arize-ax.md) | LLM 應用程式的生產級可觀測性、偵錯及改進 |
| [BigQuery Agent Analytics Plugin](./tools-and-integrations/integrations/bigquery-agent-analytics.md) | 針對行為分析和記錄的深入 agent 分析 |
| [Google Cloud Trace](https://google.github.io/adk-docs/integrations/cloud-trace/) | 監控、偵錯及追蹤 ADK agent 互動 |
| [Freeplay](https://google.github.io/adk-docs/integrations/freeplay/) | 使用 Freeplay 透過端對端可觀測性建置、最佳化及評估 AI agents |
| [MLflow](https://google.github.io/adk-docs/integrations/mlflow/) | 擷取 agent 執行、工具呼叫及模型要求的 OpenTelemetry 追蹤 |
| [Monocle](https://google.github.io/adk-docs/integrations/monocle/) | LLM 應用程式的開源可觀測性、追蹤及偵錯 |
| [Phoenix](https://google.github.io/adk-docs/integrations/phoenix/) | LLM 應用程式的開源、自我託管的可觀測性、追蹤及評估 |
| [W&B Weave](https://google.github.io/adk-docs/integrations/weave/) | 記錄、視覺化及分析模型呼叫和 agent 效能 |

#### 搜尋

| 工具名稱 | 說明 |
|---------|------|
| [Google Search](https://google.github.io/adk-docs/integrations/google-search/) | 使用 Google Search 搭配 Gemini 執行網路搜尋 |
| [Vertex AI Search](https://google.github.io/adk-docs/integrations/vertex-ai-search/) | 在 Vertex AI Search 中搜尋您的私人設定資料存放區 |



### 代理工具 (Tools for Agents)

ADK 提供多種預建工具，可讓代理程式輕鬆連結 Google 服務與第三方應用程式。

| 標頭                                                               | 描述                                                                                                   | 連結                                                  |
| :----------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------- | :---------------------------------------------------- |
| [工具總覽](./tools-for-agents/index.md)                            | 預建工具目錄，涵蓋 Gemini API、Google Cloud 與多種第三方工具（如 GitHub, Notion, Stripe 等）。         | [連結](./tools-for-agents/index.md)                   |
| [Gemini API 工具](./tools-for-agents/index.md#gemini-api-工具)     | 包含 Google 搜尋 (Google Search)、程式碼執行 (Code Execution) 與電腦使用 (Computer Use)。              | [連結](./tools-for-agents/index.md#gemini-api-工具)   |
| [Google Cloud 工具](./tools-for-agents/index.md#google-cloud-工具) | 整合 BigQuery, Spanner, Vertex AI RAG 引擎等 Google Cloud 服務。                                       | [連結](./tools-for-agents/index.md#google-cloud-工具) |
| [第三方工具](./tools-for-agents/index.md#第三方工具)               | 連結 Asana, Atlassian, GitHub, GitLab, Notion, Slack, Stripe, Agent UI 等外部平台。                    | [連結](./tools-for-agents/index.md#第三方工具)        |
| [工具限制 (Limitations)](./tools-for-agents/limitations.md)        | 了解特定內建工具（如 Google Search 或程式碼執行）的使用限制及其解決方案（如 `AgentTool` 或繞過參數）。 | [連結](./tools-for-agents/limitations.md)             |


### 自訂工具 (Custom Tools)

ADK 的「工具 (Tools)」是具備結構化輸入/輸出的程式化函數（或工具集），可由代理在推理過程中呼叫，以完成搜尋、資料查詢、API 呼叫、RAG、跨系統整合等工作。以下整理本資料夾中與自訂工具相關的主題與索引，方便依需求快速查找。

| 標頭                                                                              | 描述                                                                                                                  | 連結                                                  |
| :-------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------- |
| [自訂工具總覽](./custom-tools/index.md)                                           | 工具概念、代理如何挑選/呼叫工具，以及 ADK 工具類型（函數工具、內建工具、第三方整合）。                                | [連結](./custom-tools/index.md)                       |
| [功能工具 (Function Tools)](./custom-tools/function-tools/overview.md)            | 定義函數/方法工具、長時間運行工具、代理即工具；說明簽章、docstring、回傳格式與工具間資料傳遞。                        | [連結](./custom-tools/function-tools/overview.md)     |
| [並行執行提升效能](./custom-tools/function-tools/performance.md)                  | ADK Python v1.10.0+ 的函式工具並行執行概念；如何用 async/await、yielding、thread pool 避免阻塞。                      | [連結](./custom-tools/function-tools/performance.md)  |
| [工具操作確認 (Tool Confirmation)](./custom-tools/function-tools/confirmation.md) | 讓工具在執行前暫停並向人類/系統請求確認（布林確認、進階結構化確認），也支援透過 REST API 回覆。                       | [連結](./custom-tools/function-tools/confirmation.md) |
| [MCP 工具](./custom-tools/mcp-tools.md)                                           | 以 MCP 伺服器擴充 ADK 工具：ADK 作為 MCP client 使用既有伺服器工具，或將 ADK 工具封裝成 MCP server 提供給外部客戶端。 | [連結](./custom-tools/mcp-tools.md)                   |
| [OpenAPI 工具](./custom-tools/openapi-tools.md)                                   | 透過 OpenAPI 3.x 規範自動產生 REST API 工具（RestApiTool/OpenAPIToolset），免手寫每個端點函數工具。                   | [連結](./custom-tools/openapi-tools.md)               |
| [工具身份驗證](./custom-tools/authentication.md)                                  | 工具存取受保護資源的驗證機制（API Key、OAuth2、OIDC、Service Account…），以及安全儲存憑證的建議。                     | [連結](./custom-tools/authentication.md)              |


## 執行代理程式 (Run Agents)

### 代理執行 (Agent Runtime)

| 標頭                                                   | 描述                                                                                   | 連結                                     |
| :----------------------------------------------------- | :------------------------------------------------------------------------------------- | :--------------------------------------- |
| [Runtime 總覽](./agent-runtime/index.md)               | 介紹 ADK 提供多種在開發期間運行和測試代理的方法。                                      | [連結](./agent-runtime/index.md)         |
| [事件迴圈 (Event Loop)](./agent-runtime/event-loop.md) | 深入了解驅動 ADK 的核心事件迴圈，包括 yield/pause/resume 週期與元件協同運作。          | [連結](./agent-runtime/event-loop.md)    |
| [執行設定 (RunConfig)](./agent-runtime/runconfig.md)   | 解釋如何使用 RunConfig 來定義代理的執行時行為，例如串流模式、語音設定和 LLM 呼叫限制。 | [連結](./agent-runtime/runconfig.md)     |
| [網頁介面](./agent-runtime/web-interface.md)           | 使用 `adk web` 啟動基於瀏覽器的介面，以便互動式地測試與偵錯您的代理。                  | [連結](./agent-runtime/web-interface.md) |
| [命令列 (CLI)](./agent-runtime/command-line.md)        | 使用 `adk run` 直接在終端機中與您的代理進行互動、儲存與重播工作階段。                  | [連結](./agent-runtime/command-line.md)  |
| [API 伺服器](./agent-runtime/api-server.md)            | 說明如何透過 RESTful API 公開您的代理，提供詳細的 API 端點參考以供整合。               | [連結](./agent-runtime/api-server.md)    |
| [恢復中斷的代理](./agent-runtime/resume.md)            | 指導如何設定與使用恢復功能，讓因故中斷的代理工作流能從上次中斷的地方繼續執行。         | [連結](./agent-runtime/resume.md)        |

### 部署 (Deployment)

| 標頭                                                      | 描述                                                                              | 連結                                       |
| :-------------------------------------------------------- | :-------------------------------------------------------------------------------- | :----------------------------------------- |
| [部署總覽](./deployment/index.md)                         | 介紹如何將您的代理部署到各種環境，例如 Vertex AI Agent Engine、Cloud Run 或 GKE。 | [連結](./deployment/index.md)              |
| [部署至 Agent Engine](./deployment/agent-engine/index.md) | 說明如何將代理部署到 Google Cloud 上全託管、可自動擴展的 Agent Engine。           | [連結](./deployment/agent-engine/index.md) |
| [部署至 Cloud Run](./deployment/cloud-run.md)             | 指導您如何將代理以容器化應用程式的形式部署到 Cloud Run。                          | [連結](./deployment/cloud-run.md)          |
| [部署至 GKE](./deployment/gke.md)                         | 提供在 GKE 上部署代理的詳細步驟，適合需要更多控制權的場景。                       | [連結](./deployment/gke.md)                |

### 觀測性 (Observability)

| 標頭                                                                    | 描述                                                                                                                         | 連結                                                |
| :---------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------- |
| [觀測性總覽](./observability/index.md)                                  | 介紹 ADK 支援的多種可觀測性解決方案技術選型指南，協助您根據專案需求選擇最合適的整合方案。                                    | [連結](./observability/index.md)                    |
| [記錄 (Logging)](./observability/logging.md)                            | 說明 ADK 使用 Python 標準 logging 模組的記錄機制，包括階層式記錄器配置與日誌層級設定，適合基礎除錯需求。                     | [連結](./observability/logging.md)                  |
| [Cloud Trace](./observability/cloud-trace.md)                           | 介紹如何使用 Google Cloud Trace 進行分散式追蹤，監控 Agent 執行流程、識別延遲瓶頸與錯誤，並透過 OpenTelemetry 收集追蹤數據。 | [連結](./observability/cloud-trace.md)              |
| [AgentOps](./observability/agentops.md)                                 | 只需兩行程式碼即可整合的 SaaS 平台，提供會話重播、指標監控、LLM 成本追蹤與直觀的視覺化儀表板。                               | [連結](./observability/agentops.md)                 |
| [Arize AX](./observability/arize-ax.md)                                 | 企業級可觀測性平台，透過 OpenInference 自動收集追蹤數據，提供全面的評估、生產環境監控與詳細的偵錯分析。                      | [連結](./observability/arize-ax.md)                 |
| [BigQuery Agent Analytics](./observability/bigquery-agent-analytics.md) | ADK 官方外掛，將所有事件（含多模態數據）結構化存入 BigQuery，支援 SQL 深度分析與大規模數據處理，適合客製化報表需求。         | [連結](./observability/bigquery-agent-analytics.md) |
| [Freeplay](./observability/freeplay.md)                                 | 提供端對端的 Agent 開發流程，整合提示詞管理、線上/離線評估、人工審閱工作流與實驗比較功能。                                   | [連結](./observability/freeplay.md)                 |
| [MLflow](./observability/mlflow.md)                                     | 機器學習領域的標準實驗追蹤工具，透過 OpenTelemetry 支援 LLM 追蹤，適合已有 MLflow 基礎設施的團隊。                           | [連結](./observability/mlflow.md)                   |
| [Monocle](./observability/monocle.md)                                   | 開源的本地追蹤工具，自動儀表化 ADK 組件，產生符合 OpenTelemetry 標準的追蹤，支援匯出至本地檔案或控制台。                     | [連結](./observability/monocle.md)                  |
| [Phoenix](./observability/phoenix.md)                                   | Arize 的開源自我託管版本，提供全面的追蹤與評估能力，支援將數據保留在自有基礎設施中。                                         | [連結](./observability/phoenix.md)                  |
| [Weave (by WandB)](./observability/weave.md)                            | Weights & Biases 提供的可觀測性平台，透過 OpenTelemetry 追蹤記錄並視覺化模型調用，提供強大的時間軸檢視。                     | [連結](./observability/weave.md)                    |

### 評估代理程式 (Evaluation)

| 標頭                                                       | 描述                                                                                                         | 連結                             |
| :--------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------- | :------------------------------- |
| [為什麼要評估代理 (Agents)](./evaluation/index.md)         | 說明代理評估的必要性、評估目標與成功標準，以及如何用測試檔/評估集 (EvalSet) 建立自動化評估流程。             | [連結](./evaluation/index.md)    |
| [評估標準 (Evaluation Criteria)](./evaluation/criteria.md) | 彙整 ADK 提供的評估準則（工具軌跡、最終回應品質、幻覺、Safety、量表 Rubrics、LLM-as-a-Judge 等）與使用時機。 | [連結](./evaluation/criteria.md) |
| [使用者模擬 (User Simulation)](./evaluation/user-sim.md)   | 介紹以 ConversationScenario 動態產生使用者回合進行對話式評估，以及相關 EvalConfig / user simulator 設定。    | [連結](./evaluation/user-sim.md) |

### 安全性 (Safety and Security)
| 標頭                                         | 描述                                                                              | 連結                                   |
| :------------------------------------------- | :-------------------------------------------------------------------------------- | :------------------------------------- |
| [安全性總覽](./safety-and-security/index.md) | 介紹 ADK 中的安全性概念與功能，涵蓋輸入驗證、輸出過濾、原則強制執行與監控等方面。 | [連結](./safety-and-security/index.md) |

## Components (元件)

### 技術總覽 (Technical Overview)

| 標頭                               | 描述                                                                                                         | 連結                           |
| :--------------------------------- | :----------------------------------------------------------------------------------------------------------- | :----------------------------- |
| [技術總覽](./get-started/about.md) | 提供 ADK 核心元件的技術總覽，包括代理、模型、工具、上下文管理 與回呼等，說明它們如何協同工作以構建智能代理。 | [連結](./get-started/about.md) |

### 上下文 (Context)

| 標頭                                         | 描述                                                                                                    | 連結                            |
| :------------------------------------------- | :------------------------------------------------------------------------------------------------------ | :------------------------------ |
| [上下文 (Context) 總覽](./context/index.md)  | 說明 ADK 中 `context` 的概念、用途，以及不同類型的 Context（如 `InvocationContext` 等）。               | [連結](./context/index.md)      |
| [使用 Gemini 進行快取](./context/caching.md) | 介紹 Context Caching：用 `ContextCacheConfig` 快取大型指令/資料以降低 token 與延遲。                    | [連結](./context/caching.md)    |
| [壓縮 Agent 上下文](./context/compaction.md) | 說明 Context Compaction：以滑動視窗摘要較舊事件，透過 `EventsCompactionConfig` 控制壓縮頻率與重疊大小。 | [連結](./context/compaction.md) |

### 會話與記憶 (Sessions & Memory)

| 標頭                                                       | 描述                                                     | 連結                                         |
| :--------------------------------------------------------- | :------------------------------------------------------- | :------------------------------------------- |
| [對話上下文簡介](./sessions&memory/index.md)               | 簡介 `Session`、`State` 與 `Memory` 如何管理對話上下文。 | [連結](./sessions&memory/index.md)           |
| [會話 (Session) 概觀](./sessions&memory/session/index.md)  | 深入探討 `Session` 如何追蹤個別對話。                    | [連結](./sessions&memory/session/index.md)   |
| [會話遷移 (Migrate)](./sessions&memory/session/migrate.md) | 說明如何在會話模型或儲存後端間進行遷移與相容性處理。     | [連結](./sessions&memory/session/migrate.md) |
| [會話倒回 (Rewind)](./sessions&memory/session/rewind.md)   | 說明如何將會話還原到之前的狀態。                         | [連結](./sessions&memory/session/rewind.md)  |
| [State](./sessions&memory/state.md)                        | 解釋 `State` 如何作為 `Session` 的暫存記事本。           | [連結](./sessions&memory/state.md)           |
| [記憶 (Memory)](./sessions&memory/memory.md)               | 介紹如何利用 `MemoryService` 實現長期知識。              | [連結](./sessions&memory/memory.md)          |


### 回呼 (Callbacks)

| 標頭                                                                    | 描述                                                                                                                    | 連結                                                      |
| :---------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------- |
| [回呼總覽](./callbacks/index.md)                                        | 介紹 Callbacks 如何掛鉤到代理執行過程，提供觀察、自訂與控制代理行為的機制，包括代理前後、LLM 前後與工具執行前後的回呼。 | [連結](./callbacks/index.md)                              |
| [回呼類型](./callbacks/types-of-callbacks.md)                           | 詳細說明不同類型的回呼（代理生命週期回呼、LLM 交互回呼、工具執行回呼），包括觸發時機、用途與實作範例。                  | [連結](./callbacks/types-of-callbacks.md)                 |
| [設計模式與最佳實踐](./callbacks/design-patterns-and-best-practices.md) | 彙整 Callbacks 的常見設計模式（護欄策略、狀態管理、日誌記錄、快取、請求修改等）與實施最佳實踐，協助有效利用回呼功能。   | [連結](./callbacks/design-patterns-and-best-practices.md) |


### Artifacts (工件)

| 標頭                                   | 描述                                                                                                                      | 連結                         |
| :------------------------------------- | :------------------------------------------------------------------------------------------------------------------------ | :--------------------------- |
| [Artifacts 總覽](./artifacts/index.md) | 介紹 Artifacts 如何管理與工作階段或使用者相關的具名、版本化二進位資料 (如檔案、圖片)，並說明其在 ADK 中的表示與操作方式。 | [連結](./artifacts/index.md) |

### Events (事件)
| 標頭                          | 描述                                                                                    | 連結                      |
| :---------------------------- | :-------------------------------------------------------------------------------------- | :------------------------ |
| [事件總覽](./events/index.md) | 介紹 ADK 中事件 (Events) 的概念、用途，以及如何使用事件來追蹤代理的執行歷程與狀態變化。 | [連結](./events/index.md) |


### Apps (應用程式)

| 標頭                            | 描述                                                                                                                            | 連結                    |
| :------------------------------ | :------------------------------------------------------------------------------------------------------------------------------ | :---------------------- |
| [App 類別總覽](./apps/index.md) | 介紹 App 類別作為代理工作流程的頂層容器，用於管理代理集合的生命週期、配置和狀態，並簡化如情境快取、恢復和外掛程式等功能的設定。 | [連結](./apps/index.md) |


### Plugins (外掛程式)

| 標頭                                             | 描述                                                                                                                                    | 連結                                   |
| :----------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------- |
| [外掛程式總覽](./plugins/index.md)               | 介紹 ADK 外掛程式 (Plugin) 的概念，它如何使用回呼掛鉤在代理工作流的生命週期中執行，以及其常見應用，如日誌記錄、原則強制執行和回應快取。 | [連結](./plugins/index.md)             |
| [反思與重試工具](./plugins/reflect-and-retry.md) | 說明如何使用 `Reflect and Retry` 外掛程式來追蹤工具故障、引導 AI 模型進行反思與修正，並智慧地重試失敗的工具請求，以增強代理的韌性。     | [連結](./plugins/reflect-and-retry.md) |

### MCP 協議 (MCP Protocol)
| 標頭                       | 描述 | 連結                                                                                                                                                                                                                                           |
| :------------------------- | :--- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [MCP 總覽](./mcp/index.md) |      | 模型上下文協定 (MCP) 是開放標準，標準化 LLM 與外部系統的通訊。ADK 支援使用與提供 MCP 工具，包含用於資料庫的 MCP 工具箱（支援 BigQuery、PostgreSQL、MongoDB 等多種資料來源）、FastMCP 伺服器整合，以及 Google Cloud 生成式媒體服務的 MCP 工具。 | [連結](./mcp-protocol/index.md) |


### A2A 協議 (A2A Protocol)

| 標頭                                                                                               | 描述                                                                                             | 連結                                                                           |
| :------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------- |
| [A2A 總覽](./a2a-protocol/index.md)                                                                | 提供 ADK 中 A2A 功能的全面指南，說明如何建構可安全高效溝通的多代理系統。                         | [連結](./a2a-protocol/index.md)                                                |
| [A2A 簡介](./a2a-protocol/intro.md)                                                                | 介紹 Agent2Agent (A2A) 協定的基礎知識，並說明何時該使用遠端 A2A 代理，以及何時該選擇本地子代理。 | [連結](./a2a-protocol/intro.md)                                                |
| [快速入門：公開代理 (Python)](./a2a-protocol/a2a-quickstart%20(exposing)/quickstart-exposing.md)   | 指導如何使用 Python ADK 將您的代理公開為 A2A 服務，使其能被其他遠端代理調用。                    | [連結](./a2a-protocol/a2a-quickstart%20(exposing)/quickstart-exposing.md)      |
| [快速入門：公開代理 (Go)](./a2a-protocol/a2a-quickstart%20(exposing)/quickstart-exposing-go.md)    | 指導如何使用 Go ADK 將您的代理公開為 A2A 服務。                                                  | [連結](./a2a-protocol/a2a-quickstart%20(exposing)/quickstart-exposing-go.md)   |
| [快速入門：使用代理 (Python)](./a2a-protocol/a2a-quickstart%20(consuming)/quickstart-consuming.md) | 說明如何讓您的 Python 代理使用 A2A 協定來調用另一個遠端代理。                                    | [連結](./a2a-protocol/a2a-quickstart%20(consuming)/quickstart-consuming.md)    |
| [快速入門：使用代理 (Go)](./a2a-protocol/a2a-quickstart%20(consuming)/quickstart-consuming-go.md)  | 說明如何讓您的 Go 代理使用 A2A 協定來調用另一個遠端代理。                                        | [連結](./a2a-protocol/a2a-quickstart%20(consuming)/quickstart-consuming-go.md) |

### 雙向串流 (Bidirectional Streaming)

ADK 中的雙向 (Bidi) 串流 (Live) 為 AI 代理增加了 Gemini Live API 的低延遲雙向語音和視訊互動能力。這使得代理能夠處理即時的音訊與視訊輸入，並提供類人的對話體驗。

| 標頭                                                                   | 描述                                                                                        | 連結                                             |
| :--------------------------------------------------------------------- | :------------------------------------------------------------------------------------------ | :----------------------------------------------- |
| [雙向串流總覽](./bidi-streaming-live/index.md)                         | 介紹 ADK 中的雙向串流概念、Gemini Live API 的整合、開發指南系列以及快速上手資源。           | [連結](./bidi-streaming-live/index.md)           |
| [設定串流行為](./bidi-streaming-live/configuration.md)                 | 說明如何透過 RunConfig 設定即時（串流）代理程式的配置，例如語音配置 (speech_config)。       | [連結](./bidi-streaming-live/configuration.md)   |
| [串流工具 (Streaming Tools)](./bidi-streaming-live/streaming-tools.md) | 介紹如何定義串流工具，允許工具將中間結果串流傳回給代理，以實現如監控股價或影片串流的反應。  | [連結](./bidi-streaming-live/streaming-tools.md) |
| [開發指南：第 1 部分](./bidi-streaming-live/dev-guide/part1.md)        | 介紹雙向串流基礎、底層 Live API 技術（Gemini/Vertex AI）、ADK 架構組件及 FastAPI 實作範例。 | [連結](./bidi-streaming-live/dev-guide/part1.md) |
| [開發指南：第 2 部分](./bidi-streaming-live/dev-guide/part2.md)        | 深入探討如何使用 LiveRequestQueue 發送訊息，包括文字、音訊/影片串流、活動訊號與控制訊號。   | [連結](./bidi-streaming-live/dev-guide/part2.md) |
| [開發指南：第 3 部分](./bidi-streaming-live/dev-guide/part3.md)        | 掌握 run_live() 事件處理，包括文字/音訊事件、逐字稿、自動工具執行與多代理程式工作流。       | [連結](./bidi-streaming-live/dev-guide/part3.md) |
| [開發指南：第 4 部分](./bidi-streaming-live/dev-guide/part4.md)        | 詳解 RunConfig 配置，涵蓋回應型態、串流模式、會話恢復、上下文視窗壓縮與配額管理。           | [連結](./bidi-streaming-live/dev-guide/part4.md) |
| [開發指南：第 5 部分](./bidi-streaming-live/dev-guide/part5.md)        | 說明如何處理音訊、圖片與影片，包含 VAD、語音配置、音訊逐字稿與主動/情感對話功能。           | [連結](./bidi-streaming-live/dev-guide/part5.md) |

### Grounding

Grounding 是將代理的回應建立在外部權威資料之上的流程，用於降低幻覺、提高即時性，並讓答案可被來源驗證。以下整理本資料夾中與 Grounding 相關的主題與延伸資源。

| 標頭                                                                    | 描述                                                                                                 | 連結                                              |
| :---------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------- | :------------------------------------------------ |
| [Grounding 總覽](./grounding/index.md)                                  | 說明 Grounding 概念與 ADK 支援方式（Google 搜尋 / Vertex AI Search / Agentic RAG），並整理延伸資源。 | [連結](./grounding/index.md)                      |
| [Google 搜尋 Grounding](./grounding/google_search_grounding.md)         | 讓代理存取即時、權威的網路資訊；包含設定流程、資料流解釋與回應引用顯示。                             | [連結](./grounding/google_search_grounding.md)    |
| [Vertex AI Search Grounding](./grounding/vertex_ai_search_grounding.md) | 連接企業文件與私人資料庫；包含資料儲存設定、回應 Grounding 與來源歸屬。                              | [連結](./grounding/vertex_ai_search_grounding.md) |

## 參考資源

- [Google ADK Docs](https://google.github.io/adk-docs/)
- [[code wiki] adk-python](https://codewiki.google/github.com/google/adk-python)
- [[code wiki] agent-starter-pack](https://codewiki.google/github.com/googlecloudplatform/agent-starter-pack)
- [Google AI Studio](https://aistudio.google.com/)
- [Gemini Live API](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/live-api)

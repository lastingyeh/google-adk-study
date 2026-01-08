# 部署到 Vertex AI Agent Engine

Google Cloud Vertex AI
[Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
是一套模組化服務，可幫助開發人員在生產環境中擴展和治理 Agent。Agent Engine 執行階段使您能夠在生產環境中使用端到端託管基礎設施部署 Agent，以便您可以專注於創建智慧且具影響力的 Agent。當您將 ADK Agent 部署到 Agent Engine 時，您的程式碼會在 *Agent Engine 執行階段 (runtime)* 環境中運行，這是 Agent Engine 產品提供的更大規模 Agent 服務集的一部分。

本指南包含以下具有不同用途的部署路徑：

*   **[標準部署 (Standard deployment)](./deploy.md)**：如果您已有現有的 Google Cloud 專案，並且希望仔細管理將 ADK Agent 部署到 Agent Engine 執行階段，請遵循此標準部署路徑。此部署路徑使用 Cloud Console、ADK 命令列介面，並提供逐步指示。建議已經熟悉配置 Google Cloud 專案的使用者以及正在準備生產部署的使用者使用此路徑。

*   **[Agent Starter Pack 部署](./asp.md)**：如果您沒有現有的 Google Cloud 專案，並且是專門為開發和測試而創建專案，請遵循此加速部署路徑。Agent Starter Pack (ASP) 可幫助您快速部署 ADK 專案，並配置運行帶有 Agent Engine 執行階段的 ADK Agent 並非嚴格必需的 Google Cloud 服務。

> [!NOTE] "Google Cloud 上的 Agent Engine 服務"
    Agent Engine 是一項付費服務，如果您超過免費存取層級，可能會產生費用。更多資訊可以在 [Agent Engine 定價頁面](https://cloud.google.com/vertex-ai/pricing#vertex-ai-agent-engine) 中找到。

## 部署酬載 (Deployment payload)

當您將 ADK Agent 專案部署到 Agent Engine 時，以下內容將上傳到該服務：

- 您的 ADK Agent 程式碼
- 您的 ADK Agent 程式碼中宣告的任何依賴項

部署 *不包括* ADK API 伺服器或 ADK 網頁使用者介面函式庫。Agent Engine 服務提供 ADK API 伺服器功能的函式庫。

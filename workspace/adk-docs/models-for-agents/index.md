# 適用於 ADK Agent 的 AI 模型

> 🔔 `更新日期：2026-01-23`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/agents/models/

[`ADK 支援`: `Python` | `Typescript` | `Go` | `Java`]

Agent Development Kit (ADK) 的設計具有靈活性，允許您將各種大型語言模型 (LLM) 整合到您的 Agent 中。本節詳細介紹了如何有效地利用 Gemini 並整合其他熱門模型，包括外部託管或在本機運行的模型。

ADK 主要使用兩種機制進行模型整合：

1. **直接字串 / 註冊表 (Registry)：** 適用於與 Google Cloud 緊密整合的模型，例如透過 Google AI Studio 或 Vertex AI 存取的 Gemini 模型，或是託管在 Vertex AI 端點上的模型。您可以透過提供模型名稱或端點資源字串來存取這些模型，ADK 的內部註冊表會將此字串解析為相應的後端客戶端。

      *  [Gemini 模型](./gemini.md)
      *  [Claude 模型](./anthropic.md)
      *  [Vertex AI 託管模型](./vertex.md)

2. **模型連接器 (Model connectors)：** 為了實現更廣泛的相容性，特別是 Google 生態系統之外的模型，或那些需要特定客戶端配置的模型，例如透過 Apigee 或 LiteLLM 存取的模型。您可以實例化一個特定的包裝類別 (wrapper class)，例如 `ApigeeLlm` 或 `LiteLlm`，並將此物件作為 `model` 參數傳遞給您的 `LlmAgent`。

      *  [Apigee 模型](./apigee.md)
      *  [LiteLLM 模型](./litellm.md)
      *  [Ollama 模型託管](./ollama.md)
      *  [vLLM 模型託管](./vllm.md)

## 模型整合說明

下表總結了 ADK 支援的各種模型整合方式及其適用場景：

| 模型類型 | 用法 | 注意事項 | 連結 |
| :--- | :--- | :--- | :--- |
| **Google Gemini** | 直接在 `LlmAgent` 中指定模型名稱 (如 `gemini-2.5-flash`) | 支援程式碼執行、Google 搜尋等功能。可透過 AI Studio 或 Vertex AI 驗證。 | [Gemini 模型](./google-gemini.md) |
| **Anthropic Claude** | 使用 `Claude` 包裝類別，或透過 Vertex AI | 需使用 Anthropic API Key 或透過 Vertex AI 整合。Java 支援直接包裝器，Python 可透過 LiteLLM 或 Vertex AI 使用。 | [Claude 模型](./anthropic.md) |
| **Vertex AI** | 使用完整 Endpoint 資源字串 (`projects/...`) | 適用於 Model Garden 模型、微調模型及企業級部署。提供高可靠性與整合性。 | [Vertex AI 託管模型](./vertex.md) |
| **Apigee AI Gateway** | 使用 `ApigeeLlm` 包裝類別 | 提供模型安全性、流量治理、快取與監控。目前主要支援 Vertex AI 與 Gemini。 | [Apigee 模型](./apigee.md) |
| **LiteLLM** | 使用 `LiteLlm` 包裝類別 (如 `openai/gpt-4o`) | 作為連接器存取 100+ 種模型 (OpenAI, Anthropic 等)。提供標準化介面。 | [LiteLLM 模型](./litellm.md) |
| **Ollama** | 透過 `LiteLlm` 連接，使用 `ollama_chat` 提供者 | 用於本地託管開源模型。需設定 `OLLAMA_API_BASE`。建議使用支援工具的模型。 | [Ollama 模型託管](./ollama.md) |
| **vLLM** | 透過 `LiteLlm` 連接，指向 vLLM 端點 | 用於高效能自託管模型。需確保端點支援 OpenAI 相容的工具呼叫。 | [vLLM 模型託管](./vllm.md) |

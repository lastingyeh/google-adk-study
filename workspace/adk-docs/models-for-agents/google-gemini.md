# ADK Agent 的 Google Gemini 模型
🔔 `更新日期：2026-01-21`

[`ADK 支援`: `Python v0.1.0` | `Typescript v0.2.0` | `Go v0.1.0` | `Java v0.2.0`]

ADK 支援 Google Gemini 系列的生成式 AI 模型，這組強大的模型提供了廣泛的功能。ADK 支援許多 Gemini 的特性，包括 [程式碼執行 (Code Execution)](https://google.github.io/adk-docs/tools/gemini-api/code-execution/)、[Google 搜尋 (Google Search)](https://google.github.io/adk-docs/tools/gemini-api/google-search/)、[內容快取 (Context caching)](../context/caching.md)、[電腦使用 (Computer use)](https://google.github.io/adk-docs/tools/gemini-api/computer-use/) 以及 [Interactions API](#gemini-interactions-api)。

## 開始使用

以下程式碼範例展示了在 Agent 中使用 Gemini 模型的基本實作：

<details>
<summary>範例說明</summary>

> Python

```python
from google.adk.agents import LlmAgent

# --- 使用穩定版 Gemini Flash 模型的範例 ---
agent_gemini_flash = LlmAgent(
    # 使用最新的穩定版 Flash 模型識別碼
    model="gemini-2.5-flash",
    name="gemini_flash_agent",
    instruction="你是一個快速且樂於助人的 Gemini 助手。",
    # ... 其他 Agent 參數
)
```

> TypeScript

```typescript
import {LlmAgent} from '@google.adk';

// --- 範例 #2：在模型中搭配 API Key 使用強大的 Gemini Pro 模型 ---
export const rootAgent = new LlmAgent({
  name: 'hello_time_agent',
  model: 'gemini-2.5-flash',
  description: 'Gemini flash agent',
  instruction: `你是一個快速且樂於助人的 Gemini 助手。`,
});
```

> Go

```go
import (
    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/model/gemini"
    "google.golang.org/genai"
)

// --- 使用穩定版 Flash 模型 ---
modelFlash, err := gemini.NewModel(ctx, "gemini-2.0-flash", &genai.ClientConfig{})
if err != nil {
    log.Fatalf("failed to create model: %v", err)
}
agentGeminiFlash, err := llmagent.New(llmagent.Config{
    // 使用最新的穩定版 Flash 模型識別碼
    Model:       modelFlash,
    Name:        "gemini_flash_agent",
    Instruction: "You are a fast and helpful Gemini assistant.",
    // ... 其他 Agent 參數
if err != nil {
    log.Fatalf("failed to create agent: %v", err)
}
```

> Java

```java
// --- 範例 #1：搭配環境變數使用穩定版 Gemini Flash 模型 ---
LlmAgent agentGeminiFlash =
    LlmAgent.builder()
        // 使用最新的穩定版 Flash 模型識別碼
        .model("gemini-2.5-flash") // 設定環境變數以使用此模型
        .name("gemini_flash_agent")
        .instruction("你是一個快速且樂於助人的 Gemini 助手。")
        // ... 其他 Agent 參數
        .build();
```

</details>


## Gemini 模型驗證

本節介紹如何驗證 Google Gemini 模型，可以透過適合快速開發的 Google AI Studio，或是適合企業應用的 Google Cloud Vertex AI。這是在 ADK 中使用 Google 旗艦模型最直接的方式。

**整合方法**：一旦您使用以下任一方法完成驗證，即可將模型的識別碼字串直接傳遞給 `LlmAgent` 的 `model` 參數。

> [!TIP]
ADK 內部為 Gemini 模型使用的 `google-genai` 程式庫可以透過 Google AI Studio 或 Vertex AI 進行連線。
> **支援語音/影片串流的模型**
> 為了在 ADK 中使用語音/影片串流，您需要使用支援 Live API 的 Gemini 模型。您可以在文件中找到支援 Gemini Live API 的模型 ID：
> - [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
> - [Vertex AI: Gemini Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

### Google AI Studio

這是最簡單的方法，建議用於快速開始。

*   **驗證方法：** API Key
*   **設定：**
    1.  **獲取 API key：** 從 [Google AI Studio](https://aistudio.google.com/apikey) 獲取您的金鑰。
    2.  **設定環境變數：** 在專案根目錄下建立 `.env` 檔案 (Python) 或 `.properties` (Java)，並加入以下內容。ADK 會自動載入此檔案。

        ```shell
        export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
        export GOOGLE_GENAI_USE_VERTEXAI=FALSE
        ```

        (或)

        在模型初始化期間透過 `Client` 傳遞這些變數（請參見下方範例）。

* **模型：** 在 [Google AI for Developers 網站](https://ai.google.dev/gemini-api/docs/models)上尋找所有可用模型。

### Google Cloud Vertex AI

對於可擴展且面向生產的使用場景，Vertex AI 是推薦的平台。Vertex AI 上的 Gemini 支援企業級功能、安全性和合規性控制。根據您的開發環境和使用場景，*選擇以下任一方法進行驗證*。

**先決條件：** 一個已[啟用 Vertex AI](https://console.cloud.google.com/apis/enableflow;apiid=aiplatform.googleapis.com) 的 Google Cloud 專案。

### **方法 A：使用者憑證（用於本地開發）**

1.  **安裝 gcloud CLI：** 按照官方[安裝說明](https://cloud.google.com/sdk/docs/install)進行操作。
2.  **使用 ADC 登入：** 此指令會開啟瀏覽器以驗證您的使用者帳戶，用於本地開發。
    ```bash
    gcloud auth application-default login
    ```
3.  **設定環境變數：**
    ```shell
    export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    export GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION" # 例如：us-central1
    ```

    明確告知程式庫使用 Vertex AI：

    ```shell
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

4. **模型：** 在 [Vertex AI 文件](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models)中尋找可用的模型 ID。

### **方法 B：Vertex AI Express Mode**
[Vertex AI Express Mode](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview) 提供了一種簡化的、基於 API 金鑰的設定方式，用於快速原型設計。

1.  **註冊 Express Mode** 以獲取您的 API 金鑰。
2.  **設定環境變數：**
    ```shell
    export GOOGLE_API_KEY="PASTE_YOUR_EXPRESS_MODE_API_KEY_HERE"
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

### **方法 C：服務帳戶（用於生產與自動化）**

對於已部署的應用程式，服務帳戶是標準方法。

1.  [**建立服務帳戶**](https://cloud.google.com/iam/docs/service-accounts-create#console) 並授予其 `Vertex AI User` 角色。
2.  **為您的應用程式提供憑證：**
    *   **在 Google Cloud 上：** 如果您在 Cloud Run、GKE、VM 或其他 Google Cloud 服務中運行 Agent，環境可以自動提供服務帳戶憑證。您無需建立金鑰檔案。
    *   **在其他地方：** 建立[服務帳戶金鑰檔案](https://cloud.google.com/iam/docs/keys-create-delete#console)，並使用環境變數指向它：
        ```bash
        export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/keyfile.json"
        ```
    除了金鑰檔案外，您也可以使用 Workload Identity 來驗證服務帳戶。但這超出了本指南的範圍。

> [!WARNING] 保護您的憑證
服務帳戶憑證或 API 金鑰是強大的憑證。切勿公開。在生產環境中，請使用秘密管理器（例如 [Google Cloud Secret Manager](https://cloud.google.com/security/products/secret-manager)）來安全地儲存和存取它們。

> [!NOTE] Gemini 模型版本
請務必查看官方 Gemini 文件以獲取最新的模型名稱，包括視需要選用的特定預覽版本。預覽模型可能具有不同的可用性或配額限制。

### 驗證模型整理

| 驗證平台 / 方法 | 適用場景 | 驗證方式 | 主要環境變數設定 |
| :--- | :--- | :--- | :--- |
| **Google AI Studio** | 快速開發、個人原型 | API Key | `GOOGLE_API_KEY`, `GOOGLE_GENAI_USE_VERTEXAI=FALSE` |
| **Vertex AI (方法 A)** | 本地開發 | 使用者憑證 (ADC) | `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `GOOGLE_GENAI_USE_VERTEXAI=TRUE` |
| **Vertex AI (方法 B)** | 快速原型 (Express Mode) | API Key | `GOOGLE_API_KEY`, `GOOGLE_GENAI_USE_VERTEXAI=TRUE` |
| **Vertex AI (方法 C)** | 生產環境、自動化 | 服務帳戶 (SA) | `GOOGLE_APPLICATION_CREDENTIALS` (或 Workload Identity) |

## 疑難排解

### 錯誤代碼 429 - RESOURCE_EXHAUSTED

此錯誤通常發生在您的請求數量超過處理請求所分配的容量時。

為了緩解此問題，您可以執行以下操作之一：

1.  為您嘗試使用的模型申請更高的配額限制。

2.  啟用用戶端重試。重試允許用戶端在延遲後自動重試請求，這在配額問題是暫時的情況下很有幫助。

    有兩種方法可以設定重試選項：

    **方法 1：** 在 Agent 上將重試選項設定為 `generate_content_config` 的一部分。

    如果您是自行實例化此模型適配器，則可以使用此選項。

    ```python
    root_agent = Agent(
        model='gemini-2.5-flash',
        ...
        generate_content_config=types.GenerateContentConfig(
            ...
            http_options=types.HttpOptions(
                ...
                retry_options=types.HttpRetryOptions(initial_delay=1, attempts=2),
                ...
            ),
            ...
        )
    ```

    **方法 2：** 在模型適配器上設定重試選項。

    如果您是自行實例化適配器的實例，則可以使用此選項。

    ```python
    from google.genai import types

    # ...

    agent = Agent(
        model=Gemini(
        retry_options=types.HttpRetryOptions(initial_delay=1, attempts=2),
        )
    )
    ```

## Gemini Interactions API

[`ADK 支援`: `Python v1.21.0`]

Gemini [Interactions API](https://ai.google.dev/gemini-api/docs/interactions) 是 ***generateContent*** 推論 API 的替代方案，它提供了具狀態的對話功能，允許您使用 `previous_interaction_id` 鏈接互動，而無需在每次請求時發送完整的對話歷史記錄。對於長時間的對話，使用此功能可能會更有效率。

您可以透過在 Gemini 模型配置中設置 `use_interactions_api=True` 參數來啟用 Interactions API，如以下程式碼片段所示：

```python
from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools.google_search_tool import GoogleSearchTool

root_agent = Agent(
    model=Gemini(
        model="gemini-2.5-flash",
        use_interactions_api=True,  # 啟用 Interactions API
    ),
    name="interactions_test_agent",
    tools=[
        GoogleSearchTool(bypass_multi_tools_limit=True),  # 轉換為函式工具
        get_current_weather,  # 自定義函式工具
    ],
)
```

如需完整的程式碼範例，請參閱 [Interactions API 範例](https://github.com/google/adk-python/tree/main/contributing/samples/interactions_api)。

### 已知限制

Interactions API **不支援**在同一個 Agent 中將自定義函式呼叫工具與內建工具（如 [Google 搜尋 (Google Search)](https://google.github.io/adk-docs/tools/#google-search) 工具）混合使用。您可以透過使用 `bypass_multi_tools_limit` 參數將內建工具配置為作為自定義工具運作來繞過此限制：

```python
# 使用 bypass_multi_tools_limit=True 將 google_search 轉換為函式工具
GoogleSearchTool(bypass_multi_tools_limit=True)
```

在此範例中，此選項將內建的 google_search 轉換為函式呼叫工具（透過 GoogleSearchAgentTool），使其能夠與自定義函式工具並行運作。

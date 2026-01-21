# 為 ADK 代理託管的 Vertex AI 模型
🔔 `更新日期：2026-01-21`

為了實現企業級的可擴展性、可靠性以及與 Google Cloud MLOps 生態系統的整合，您可以使用部署到 Vertex AI 端點（Endpoints）的模型。這包括來自 Model Garden 的模型或您自己微調的模型。

**整合方法：** 將完整的 Vertex AI 端點資源字串 (`projects/PROJECT_ID/locations/LOCATION/endpoints/ENDPOINT_ID`) 直接傳遞給 `LlmAgent` 的 `model` 參數。

## Vertex AI 設定

確保您的環境已針對 Vertex AI 進行配置：

1. **身分驗證：** 使用應用程式預設認證 (ADC)：

    ```shell
    # 登入以設定應用程式預設認證
    gcloud auth application-default login
    ```

2. **環境變數：** 設定您的專案和位置：

    ```shell
    # 設定 Google Cloud 專案 ID
    export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    # 設定 Vertex AI 區域，例如 us-central1
    export GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION"
    ```

3. **啟用 Vertex 後端：** 至關重要的是，確保 `google-genai` 函式庫以 Vertex AI 為目標：

    ```shell
    # 強制 google-genai 使用 Vertex AI 後端
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

## Model Garden 部署 (Model Garden Deployments)

[`ADK 支援`: `Python v0.2.0`]

您可以將來自 [Vertex AI Model Garden](https://console.cloud.google.com/vertex-ai/model-garden) 的各種開源和專有模型部署到端點。

**範例：**

```python
from google.adk.agents import LlmAgent
from google.genai import types # 用於配置物件

# --- 使用從 Model Garden 部署的 Llama 3 模型的代理範例 ---

# 替換為您實際的 Vertex AI 端點資源名稱
llama3_endpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_LLAMA3_ENDPOINT_ID"

agent_llama3_vertex = LlmAgent(
    model=llama3_endpoint,
    name="llama3_vertex_agent",
    instruction="您是一個基於 Llama 3 的得力助手，託管在 Vertex AI 上。",
    generate_content_config=types.GenerateContentConfig(max_output_tokens=2048),
    # ... 其他代理參數
)
```

## 微調模型端點 (Fine-tuned Model Endpoints)

[`ADK 支援`: `Python v0.2.0`]

部署您的微調模型（無論是基於 Gemini 還是 Vertex AI 支援的其他架構）會產生一個可以直接使用的端點。

**範例：**

```python
from google.adk.agents import LlmAgent

# --- 使用微調後的 Gemini 模型端點的代理範例 ---

# 替換為您微調模型的端點資源名稱
finetuned_gemini_endpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_FINETUNED_ENDPOINT_ID"

agent_finetuned_gemini = LlmAgent(
    model=finetuned_gemini_endpoint,
    name="finetuned_gemini_agent",
    instruction="您是一個在特定數據上訓練過的專業助手。",
    # ... 其他代理參數
)
```

## Vertex AI 上的 Anthropic Claude

[`ADK 支援`: `Python v0.2.0` | `Java v0.1.0`]

某些提供商（如 Anthropic）直接透過 Vertex AI 提供其模型。

<details>
<summary>範例說明</summary>

> Python

**整合方法：** 使用直接的模型字串（例如 `"claude-3-sonnet@20240229"`），*但需要在 ADK 中手動註冊*。

**為什麼要註冊？** ADK 的註冊表會自動辨識 `gemini-*` 字串和標準 Vertex AI 端點字串 (`projects/.../endpoints/...`)，並透過 `google-genai` 函式庫進行路由。對於直接透過 Vertex AI 使用的其他模型類型（如 Claude），您必須明確告知 ADK 註冊表哪個特定的封裝類別（在本例中為 `Claude`）知道如何處理該模型識別字串與 Vertex AI 後端。

**設定：**

1. **Vertex AI 環境：** 確保已完成統一的 Vertex AI 設定（ADC、環境變數、`GOOGLE_GENAI_USE_VERTEXAI=TRUE`）。

2. **安裝提供商函式庫：** 安裝針對 Vertex AI 配置的必要客戶端函式庫。

    ```shell
    # 安裝支援 Vertex AI 的 Anthropic 函式庫
    pip install "anthropic[vertex]"
    ```

3. **註冊模型類別：** 在應用程式開始處，建立使用 Claude 模型字串的代理 *之前*，加入此程式碼：

    ```python
    # 透過 LlmAgent 直接使用 Claude 模型字串與 Vertex AI 時所需
    from google.adk.models.anthropic_llm import Claude
    from google.adk.models.registry import LLMRegistry

    # 註冊 Claude 模型類別
    LLMRegistry.register(Claude)
    ```

**範例：**

```python
from google.adk.agents import LlmAgent
from google.adk.models.anthropic_llm import Claude # 註冊所需
from google.adk.models.registry import LLMRegistry # 註冊所需
from google.genai import types

# --- 註冊 Claude 類別（在啟動時執行一次） ---
LLMRegistry.register(Claude)

# --- 在 Vertex AI 上使用 Claude 3 Sonnet 的代理範例 ---

# Vertex AI 上 Claude 3 Sonnet 的標準模型名稱
claude_model_vertexai = "claude-3-sonnet@20240229"

agent_claude_vertexai = LlmAgent(
    model=claude_model_vertexai, # 註冊後傳遞直接字串
    name="claude_vertexai_agent",
    instruction="您是一個由 Vertex AI 上的 Claude 3 Sonnet 提供支援的助手。",
    generate_content_config=types.GenerateContentConfig(max_output_tokens=4096),
    # ... 其他代理參數
)
```

> Java

**整合方法：** 直接實例化提供商特定的模型類別（例如 `com.google.adk.models.Claude`），並使用 Vertex AI 後端對其進行配置。

**為什麼要直接實例化？** Java ADK 的 `LlmRegistry` 預設主要處理 Gemini 模型。對於 Vertex AI 上的 Claude 等第三方模型，您直接向 `LlmAgent` 提供 ADK 封裝類別（例如 `Claude`）的實例。此封裝類別負責透過其特定的客戶端函式庫（已針對 Vertex AI 配置）與模型互動。

**設定：**

1.  **Vertex AI 環境：**
    *   確保您的 Google Cloud 專案和區域已正確設定。
    *   **應用程式預設認證 (ADC)：** 確保您的環境中正確配置了 ADC。這通常透過執行 `gcloud auth application-default login` 來完成。Java 客戶端函式庫使用這些認證向 Vertex AI 進行身分驗證。有關詳細設定，請參閱 [ADC 上的 Google Cloud Java 文件](https://cloud.google.com/java/docs/reference/google-auth-library/latest/com.google.auth.oauth2.GoogleCredentials#com_google_auth_oauth2_GoogleCredentials_getApplicationDefault__)。

2.  **提供商函式庫依賴項：**
    *   **第三方客戶端函式庫（通常是傳遞性的）：** ADK 核心函式庫通常將 Vertex AI 上常見第三方模型所需的客戶端函式庫（如 Anthropic 所需的類別）作為 **傳遞依賴項** 包含在內。這意味著您可能不需要在 `pom.xml` 或 `build.gradle` 中顯式添加 Anthropic Vertex SDK 的單獨依賴項。

3.  **實例化並配置模型：**
    建立 `LlmAgent` 時，實例化 `Claude` 類別（或另一個提供商的等效類別）並配置其 `VertexBackend`。

**範例：**

```java
import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.vertex.backends.VertexBackend;
import com.google.adk.agents.LlmAgent;
import com.google.adk.models.Claude; // ADK 的 Claude 封裝類別
import com.google.auth.oauth2.GoogleCredentials;
import java.io.IOException;

// ... 其他匯入

public class ClaudeVertexAiAgent {

    public static LlmAgent createAgent() throws IOException {
        // Vertex AI 上 Claude 3 Sonnet 的模型名稱（或其他版本）
        String claudeModelVertexAi = "claude-3-7-sonnet"; // 或任何其他 Claude 模型

        // 使用 VertexBackend 配置 AnthropicOkHttpClient
        AnthropicClient anthropicClient = AnthropicOkHttpClient.builder()
            .backend(
                VertexBackend.builder()
                    .region("us-east5") // 指定您的 Vertex AI 區域
                    .project("your-gcp-project-id") // 指定您的 GCP 專案 ID
                    .googleCredentials(GoogleCredentials.getApplicationDefault())
                    .build())
            .build();

        // 使用 ADK Claude 封裝類別實例化 LlmAgent
        LlmAgent agentClaudeVertexAi = LlmAgent.builder()
            .model(new Claude(claudeModelVertexAi, anthropicClient)) // 傳遞 Claude 實例
            .name("claude_vertexai_agent")
            .instruction("您是一個由 Vertex AI 上的 Claude 3 Sonnet 提供支援的助手。")
            // .generateContentConfig(...) // 選填：如果需要，加入生成配置
            // ... 其他代理參數
            .build();

        return agentClaudeVertexAi;
    }

    public static void main(String[] args) {
        try {
            LlmAgent agent = createAgent();
            System.out.println("成功建立代理：" + agent.name());
            // 這裡您通常會設定 Runner 和 Session 來與代理互動
        } catch (IOException e) {
            System.err.println("建立代理失敗：" + e.getMessage());
            e.printStackTrace();
        }
    }
}
```

</details>

## Vertex AI 上的開放模型

[`ADK 支援`: `Python v0.1.0`]

Vertex AI 透過模型即服務 (MaaS) 提供精選的開源模型，例如 Meta Llama。這些模型可透過託管 API 存取，讓您無需管理底層基礎架構即可進行部署和擴展。如需可用選項的完整清單，請參閱 [Vertex AI 上的 MaaS 開放模型](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/maas/use-open-models#open-models) 文件。

<details>
<summary>範例說明</summary>

> Python

您可以使用 [LiteLLM](https://docs.litellm.ai/) 函式庫來存取 VertexAI MaaS 上的 Meta Llama 等開放模型。

**整合方法：** 使用 `LiteLlm` 封裝類別，並將其設定為 `LlmAgent` 的 `model` 參數。請務必參閱 [ADK 代理的 LiteLLM 模型連接器](./litellm.md#adk-代理的-litellm-模型連接器) 文件，了解如何在 ADK 中使用 LiteLLM。

**設定：**

1. **Vertex AI 環境：** 確保已完成統一的 Vertex AI 設定（ADC、環境變數、`GOOGLE_GENAI_USE_VERTEXAI=TRUE`）。

2. **安裝 LiteLLM：**
        ```shell
        # 安裝 LiteLLM 函式庫
        pip install litellm
        ```

**範例：**

```python
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# --- 使用 Meta Llama 4 Scout 的代理範例 ---
agent_llama_vertexai = LlmAgent(
    model=LiteLlm(model="vertex_ai/meta/llama-4-scout-17b-16e-instruct-maas"), # LiteLLM 模型字串格式
    name="llama4_agent",
    instruction="您是一個由 Llama 4 Scout 提供支援的得力助手。",
    # ... 其他代理參數
)
```

</details>

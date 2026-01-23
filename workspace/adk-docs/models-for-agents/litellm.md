# ADK 代理的 LiteLLM 模型連接器

> 🔔 `更新日期：2026-01-23`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/agents/models/litellm/

[`ADK 支援`: `Python v0.1.0`]

[LiteLLM](https://docs.litellm.ai/) 是一個 Python 函式庫，充當模型和模型託管服務的翻譯層，為超過 100 多個 LLM 提供標準化的、與 OpenAI 相容的介面。ADK 通過 LiteLLM 函式庫提供整合，讓您能夠存取來自 OpenAI、Anthropic (非 Vertex AI)、Cohere 等許多供應商的廣泛 LLM。您可以本地運行開源模型或自行託管，並使用 LiteLLM 進行整合，以實現操作控制、節省成本、保護隱私或離線使用案例。

您可以使用 LiteLLM 函式庫存取遠端或本地託管的 AI 模型：

*   **遠端模型主機：** 使用 `LiteLlm` 包裝類別並將其設置為 `LlmAgent` 的 `model` 參數。
*   **本地模型主機：** 使用配置為指向本地模型伺服器的 `LiteLlm` 包裝類別。有關本地模型託管解決方案的範例，請參閱 [Ollama](./ollama.md) 或 [vLLM](./vllm.md) 文件。

> [!WARNING] Windows 上的 LiteLLM 編碼問題
>在 Windows 上將 ADK 代理與 LiteLLM 一起使用時，您可能會遇到 `UnicodeDecodeError`。發生此錯誤的原因是 LiteLLM 可能會嘗試使用預設的 Windows 編碼 (`cp1252`) 而不是 UTF-8 來讀取快取檔案。通過將 `PYTHONUTF8` 環境變數設置為 `1` 來防止此錯誤。這會強制 Python 對所有檔案 I/O 使用 UTF-8。
>
> **範例 (PowerShell)：**
>```powershell
> # 為當前工作階段設置
>$env:PYTHONUTF8 = "1"
>
> # 為使用者持久設置
> [System.Environment]::SetEnvironmentVariable('PYTHONUTF8', '1', [System.> EnvironmentVariableTarget]::User)
> ```

## 設定

1. **安裝 LiteLLM：**
        ```shell
        pip install litellm
        ```
2. **設置供應商 API 金鑰：** 為您打算使用的特定供應商配置 API 金鑰作為環境變數。

    * *OpenAI 範例：*

        ```shell
        export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
        ```

    * *Anthropic (非 Vertex AI) 範例：*

        ```shell
        export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
        ```

    * *有關其他供應商的正確環境變數名稱，請參閱 [LiteLLM 供應商文件](https://docs.litellm.ai/docs/providers)。*

## 實作範例

```python
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# --- 使用 OpenAI 的 GPT-4o 的代理範例 ---
# (需要 OPENAI_API_KEY)
agent_openai = LlmAgent(
    model=LiteLlm(model="openai/gpt-4o"), # LiteLLM 模型字串格式
    name="openai_agent",
    instruction="您是一個由 GPT-4o 驅動的得力助手。",
    # ... 其他代理參數
)

# --- 使用 Anthropic 的 Claude Haiku (非 Vertex) 的代理範例 ---
# (需要 ANTHROPIC_API_KEY)
agent_claude_direct = LlmAgent(
    model=LiteLlm(model="anthropic/claude-3-haiku-20240307"),
    name="claude_direct_agent",
    instruction="您是一個由 Claude Haiku 驅動的助手。",
    # ... 其他代理參數
)
```
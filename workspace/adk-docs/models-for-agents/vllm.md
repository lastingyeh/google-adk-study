# 為 ADK 代理程式託管 vLLM 模型

> 🔔 `更新日期：2026-01-23`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/agents/models/vllm/

[`ADK 支援`: `Python v0.1.0`]

[vLLM](https://github.com/vllm-project/vllm) 等工具可讓您高效地託管模型，並將其作為與 OpenAI 相容的 API 端點。您可以透過 Python 的 [LiteLLM](./litellm.md) 函式庫使用 vLLM 模型。

## 設定

1. **部署模型：** 使用 vLLM（或類似工具）部署您選擇的模型。請記下 API 基礎 URL（例如：`https://your-vllm-endpoint.run.app/v1`）。
    * *對 ADK 工具的重要性：* 部署時，請確保服務工具支援並啟用與 OpenAI 相容的工具/函式呼叫。對於 vLLM，這可能涉及 `--enable-auto-tool-choice` 等標記，以及根據模型可能需要的特定 `--tool-call-parser`。請參閱 vLLM 關於工具使用的文件。
2. **身份驗證：** 確定您的端點如何處理身份驗證（例如：API 金鑰、載體令牌 (bearer token)）。

## 整合範例

以下範例展示了如何將 vLLM 端點與 ADK 代理程式配合使用。

```python
import subprocess
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# --- 使用託管在 vLLM 端點上的模型的代理程式範例 ---

# 由您的 vLLM 部署提供的端點 URL
api_base_url = "https://your-vllm-endpoint.run.app/v1"

# 您的 vLLM 端點配置所辨識的模型名稱
model_name_at_endpoint = "hosted_vllm/google/gemma-3-4b-it" # 來自 vllm_test.py 的範例

# 身份驗證（範例：針對 Cloud Run 部署使用 gcloud 身份令牌）
# 請根據您的端點安全性進行調整
try:
    # 取得 gcloud 身份令牌
    gcloud_token = subprocess.check_output(
        ["gcloud", "auth", "print-identity-token", "-q"]
    ).decode().strip()
    auth_headers = {"Authorization": f"Bearer {gcloud_token}"}
except Exception as e:
    # 如果無法取得權限，輸出警告
    print(f"警告：無法取得 gcloud 令牌 - {e}。端點可能未受保護或需要不同的驗證方式。")
    auth_headers = None # 或進行適當的錯誤處理

# 初始化 LlmAgent
agent_vllm = LlmAgent(
    model=LiteLlm(
        model=model_name_at_endpoint,
        api_base=api_base_url,
        # 如果需要，傳遞身份驗證標頭
        extra_headers=auth_headers
        # 或者，如果端點使用 API 金鑰：
        # api_key="YOUR_ENDPOINT_API_KEY"
    ),
    name="vllm_agent",
    instruction="您是運行在自行託管的 vLLM 端點上的樂於助人的助理。",
    # ... 其他代理程式參數
)
```
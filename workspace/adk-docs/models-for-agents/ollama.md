# 為 ADK 代理程式託管 Ollama 模型

> 🔔 `更新日期：2026-01-23`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/agents/models/ollama/

[`ADK 支援`: `Python v0.1.0`]

[Ollama](https://ollama.com/) 是一個讓您可以在本地託管並運行開源模型的工具。ADK 透過 [LiteLLM](./litellm.md) 模型連接器函式庫與 Ollama 託管的模型整合。

## 開始使用

使用 LiteLLM 包裝器來建立使用 Ollama 託管模型的代理程式。以下程式碼範例展示了在您的代理程式中使用 Gemma 開源模型的基礎實作：

```py
# 建立一個使用 Ollama 託管的 Gemma3 模型代理程式
root_agent = Agent(
    # 指定使用 LiteLlm 模型連接器，provider 設為 ollama_chat
    model=LiteLlm(model="ollama_chat/gemma3:latest"),
    name="dice_agent",
    description=(
        "這是一個 hello world 代理程式，可以擲 8 面骰並檢查質數。"
    ),
    instruction="""
      您負責擲骰子並回答有關擲骰結果的問題。
    """,
    # 代理程式可使用的工具列表
    tools=[
        roll_die,
        check_prime,
    ],
)
```

> [!WARNING] 使用 ollama_chat 介面
請務必將提供者設置為 `ollama_chat` 而不是 `ollama`。使用 `ollama` 可能會導致非預期的行為，例如無限工具調用循環以及忽略先前的上下文。

> [!TIP] 使用 OLLAMA_API_BASE 環境變數
雖然您可以在 LiteLLM 中指定 `api_base` 參數進行生成，但截至 v1.65.5，該函式庫的其他 API 調用仍依賴於環境變數。因此，您應該為您的 Ollama 伺服器 URL 設置 `OLLAMA_API_BASE` 環境變數，以確保所有請求都能正確路由。

```bash
# 設置 Ollama API 基礎 URL
export OLLAMA_API_BASE="http://localhost:11434"
# 啟動 ADK web 介面
adk web
```

## 模型選擇

如果您的代理程式依賴工具，請務必從 [Ollama 網站](https://ollama.com/search?c=tools)選擇具有工具支援的模型。為了獲得可靠的結果，請使用支援工具的模型。您可以使用以下命令檢查模型的工具支援情況：

```bash
# 檢查 mistral-small3.1 模型的詳細資訊
ollama show mistral-small3.1
  Model
    architecture        mistral3
    parameters          24.0B
    context length      131072
    embedding length    5120
    quantization        Q4_K_M

  Capabilities
    completion
    vision
    tools
```

您應該會在 capabilities 下看到 **tools**。您也可以查看模型正在使用的模板，並根據您的需求進行調整。

```bash
# 將 llama3.2 的模型文件匯出到檔案以便修改
ollama show --modelfile llama3.2 > model_file_to_modify
```

例如，上述模型的預設模板固有的建議模型應始終調用函數。這可能會導致函數調用的無限循環。

```
給定以下函數，請回覆一個包含正確參數的函數調用 JSON，以最好地回答給定的提示。

請以 {"name": 函數名稱, "parameters": 參數名稱與其值的字典} 的格式回覆。不要使用變數。
```

您可以用更具描述性的提示替換此類提示，以防止無限工具調用循環，例如：

```
審查使用者的提示和下面列出的可用函數。

首先，確定調用其中一個函數是否是回應的最合適方式。如果提示要求特定操作、需要外部數據查詢或涉及由函數處理的計算，則可能需要函數調用。如果提示是通用問題或可以直接回答，則可能不需要函數調用。

如果您確定需要函數調用：僅以 {"name": "function_name", "parameters": {"argument_name": "value"}} 格式的回覆 JSON 物件。確保參數值是具體的，而不是變數。

如果您確定不需要函數調用：以純文字直接回覆使用者的提示，提供要求的答案或資訊。不要輸出任何 JSON。
```

然後您可以使用以下命令建立一個新模型：

```bash
# 使用修改後的模型文件建立新模型
ollama create llama3.2-modified -f model_file_to_modify
```

## 使用 OpenAI 提供者

或者，您可以使用 `openai` 作為提供者名稱。這種方法需要設置 `OPENAI_API_BASE=http://localhost:11434/v1` 和 `OPENAI_API_KEY=anything` 環境變數，而不是 `OLLAMA_API_BASE`。請注意，`API_BASE` 值末尾有 *`/v1`*。

```py
# 使用 OpenAI 相容介面建立代理程式
root_agent = Agent(
    # 指定使用 LiteLlm 模型連接器，透過 openai provider 訪問 Ollama
    model=LiteLlm(model="openai/mistral-small3.1"),
    name="dice_agent",
    description=(
        "這是一個 hello world 代理程式，可以擲 8 面骰並檢查質數。"
    ),
    instruction="""
      您負責擲骰子並回答有關擲骰結果的問題。
    """,
    tools=[
        roll_die,
        check_prime,
    ],
)
```

```bash
# 設置 OpenAI 相容的 API 基礎 URL 與金鑰
export OPENAI_API_BASE=http://localhost:11434/v1
export OPENAI_API_KEY=anything
# 啟動 ADK web 介面
adk web
```

### 偵錯

您可以透過在代理程式程式碼中的匯入語句後加入以下內容，查看發送到 Ollama 伺服器的請求。

```py
import litellm
# 開啟 LiteLLM 的偵錯模式以查看詳細請求
litellm._turn_on_debug()
```

尋找類似以下的行：
```bash
# 從 LiteLLM 發送的請求範例
Request Sent from LiteLLM:
curl -X POST \
http://localhost:11434/api/chat \
-d '{'model': 'mistral-small3.1', 'messages': [{'role': 'system', 'content': ...
```

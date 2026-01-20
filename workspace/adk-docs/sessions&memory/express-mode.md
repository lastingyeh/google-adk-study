# Vertex AI 快速模式：使用 Vertex AI 會話 (Sessions) 與記憶 (Memory)

🔔 `更新日期：2026 年 1 月 5 日`

如果您有興趣使用 `VertexAiSessionService` 或 `VertexAiMemoryBankService` 但沒有 Google Cloud 專案，您可以註冊 Vertex AI 快速模式 (Express Mode) 以免費獲取存取權限並試用這些服務！您可以使用合格的 **_gmail_** 帳號在[此處](https://console.cloud.google.com/expressmode)註冊。有關 Vertex AI 快速模式的更多細節，請參閱[概覽頁面](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview)。
註冊後，獲取 [API 金鑰](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview#api-keys)，即可開始在您的本地 ADK 代理 (Agent) 中使用 Vertex AI 會話與記憶服務！

> [!NOTE] info Vertex AI 快速模式限制
> Vertex AI 快速模式在免費層級中有某些限制。免費快速模式專案有效期僅為 90 天，且僅提供部分服務，配額有限。例如，代理引擎 (Agent Engines) 的數量限制為 10 個，且部署到代理引擎的功能僅限於付費層級。要移除配額限制並使用所有 Vertex AI 服務，請為您的快速模式專案添加付款帳戶。

## 內容摘要

| 主題                                   | 說明                                  | 相關連結                                                                 |
| -------------------------------------- | ------------------------------------- | ------------------------------------------------------------------------ |
| 建立代理引擎 (Agent Engine)            | 如何建立與設定 Vertex AI 代理引擎     | [建立代理引擎](#建立代理引擎-agent-engine)                               |
| 會話管理 (`VertexAiSessionService`)    | 使用 Session Service 管理對話會話     | [會話管理](#使用-vertexaisessionservice-管理會話)                        |
| 記憶管理 (`VertexAiMemoryBankService`) | 使用 Memory Bank Service 管理代理記憶 | [記憶管理](#使用-vertexaimemorybankservice-管理記憶)                     |
| 程式碼範例                             | 天氣代理整合 Session 與 Memory 的範例 | [程式碼範例](#程式碼範例使用-vertex-ai-快速模式搭配會話與記憶的天氣代理) |

---

## 建立代理引擎 (Agent Engine)

`Session` 物件是 `AgentEngine` 的子物件。使用 Vertex AI 快速模式時，我們可以建立一個空的 `AgentEngine` 父物件來管理所有的 `Session` 和 `Memory` 物件。
首先，確保您的環境變數設定正確。例如，在 Python 中：

`agent/.env`

```env title="agent/.env"
# 設定使用 Vertex AI
GOOGLE_GENAI_USE_VERTEXAI=TRUE
# 在此處貼上您的實際快速模式 API 金鑰
GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_EXPRESS_MODE_API_KEY_HERE
```

接下來，我們可以建立代理引擎實例。您可以使用 Vertex AI SDK。

1. 匯入 Vertex AI SDK。

   > python

   ```py
   # 匯入 vertexai 模組
   import vertexai
   # 從 vertexai 匯入 agent_engines
   from vertexai import agent_engines
   ```

2. 使用您的 API 金鑰初始化 Vertex AI 用戶端並建立代理引擎實例。

   > python

   ```py
   # 使用 Gen AI SDK 建立代理引擎用戶端
   client = vertexai.Client(
     api_key="YOUR_API_KEY", # 替換為您的 API 金鑰
   )

   # 建立代理引擎實例
   agent_engine = client.agent_engines.create(
     config={
       "display_name": "Demo Agent Engine", # 顯示名稱
       "description": "Agent Engine for Session and Memory", # 描述
     })
   ```

3. 將 `YOUR_AGENT_ENGINE_DISPLAY_NAME` 和 `YOUR_AGENT_ENGINE_DESCRIPTION` 替換為您的使用案例。
4. 從回應中獲取代理引擎的名稱和 ID，以便與記憶 (Memories) 和會話 (Sessions) 一起使用。

   > python

   ```py
   # 從回應資源名稱中解析出 APP_ID
   APP_ID = agent_engine.api_resource.name.split('/')[-1]
   ```

## 使用 `VertexAiSessionService` 管理會話

[`VertexAiSessionService`](../sessions&memory/session/overview.md#sessionservice-實作方式) 與 Vertex AI 快速模式 API 金鑰相容。我們可以改為初始化會話物件，而無需任何專案 (project) 或位置 (location)。

> python

```py
# 需求：pip install google-adk[vertexai]
# 加上環境變數設定：
# GOOGLE_GENAI_USE_VERTEXAI=TRUE
# GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_EXPRESS_MODE_API_KEY_HERE

# 匯入 VertexAiSessionService
from google.adk.sessions import VertexAiSessionService

# 與此服務一起使用的 app_name 應為推理引擎 ID (Reasoning Engine ID) 或名稱
APP_ID = "your-reasoning-engine-id"

# 使用 Vertex 快速模式初始化時，不需要專案和位置資訊
session_service = VertexAiSessionService(agent_engine_id=APP_ID)

# 呼叫服務方法時使用 REASONING_ENGINE_APP_ID，例如：
# session = await session_service.create_session(app_name=APP_ID, user_id= ...)
```

> [!NOTE] 會話服務配額 (Session Service Quotas)
> 對於免費快速模式專案，`VertexAiSessionService` 具有以下配額：
>
> - 每分鐘可建立、刪除或更新 10 個 Vertex AI 代理引擎會話
> - 每分鐘可將 30 個事件附加到 Vertex AI 代理引擎會話

## 使用 `VertexAiMemoryBankService` 管理記憶

[`VertexAiMemoryBankService`](../sessions&memory/memory.md#vertex-ai-memory-bank) 與 Vertex AI 快速模式 API 金鑰相容。我們可以改為初始化記憶物件，而無需任何專案或位置。

> python

```py
# 需求：pip install google-adk[vertexai]
# 加上環境變數設定：
# GOOGLE_GENAI_USE_VERTEXAI=TRUE
# GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_EXPRESS_MODE_API_KEY_HERE

# 匯入 VertexAiMemoryBankService
from google.adk.memory import VertexAiMemoryBankService

# 與此服務一起使用的 app_name 應為推理引擎 ID 或名稱
APP_ID = "your-reasoning-engine-id"

# 使用 Vertex 快速模式初始化時，不需要專案和位置資訊
memory_service = VertexAiMemoryBankService(agent_engine_id=APP_ID)

# 從該會話生成記憶，以便代理可以記住關於使用者的相關細節
# memory = await memory_service.add_session_to_memory(session)
```

> [!NOTE] info 記憶服務配額 (Memory Service Quotas)
> 對於免費快速模式專案，`VertexAiMemoryBankService` 具有以下配額：
>
> - 每分鐘可建立、刪除或更新 10 個 Vertex AI 代理引擎記憶資源
> - 每分鐘可從 Vertex AI 代理引擎記憶庫獲取、列出或擷取 10 次

## 程式碼範例：使用 Vertex AI 快速模式搭配會話與記憶的天氣代理

在此範例中，我們建立了一個天氣代理，它同時利用 `VertexAiSessionService` 和 `VertexAiMemoryBankService` 進行內容管理，讓我們的代理能夠回想起使用者的偏好和對話內容！

**[使用 Vertex AI 快速模式搭配會話與記憶的天氣代理](https://github.com/google/adk-docs/blob/main/examples/python/notebooks/express-mode-weather-agent.ipynb)**

## 參考資源

*   [概覽頁面](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview)
*   [API 金鑰](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview#api-keys)
*   [VertexAiSessionService](https://google.github.io/adk-docs/sessions/session/#sessionservice-implementations)
*   [VertexAiMemoryBankService](https://google.github.io/adk-docs/sessions/memory/#vertex-ai-memory-bank)
*   [使用 Vertex AI 快速模式搭配會話與記憶的天氣代理](https://github.com/google/adk-docs/blob/main/examples/python/notebooks/express-mode-weather-agent.ipynb)
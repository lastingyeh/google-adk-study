# Vertex AI 快速模式

> 🔔 `更新日期：2026-01-26`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/tools/google-cloud/express-mode/

[`ADK 支援`: `Python v0.1.0` | `Java v0.1.0` | `預覽版`]

Google Cloud Vertex AI 快速模式提供免費存取層級，用於原型設計和開發，讓您無需建立完整的 Google Cloud 專案即可使用 Vertex AI 服務。此服務包含對許多強大的 Vertex AI 服務的存取，包括：
- [Vertex AI 快速模式](#vertex-ai-快速模式)
  - [配置 Agent Engine 容器](#配置-agent-engine-容器)
  - [使用 `VertexAiSessionService` 管理 Session](#使用-vertexaisessionservice-管理-session)
  - [使用 `VertexAiMemoryBankService` 管理 Memory](#使用-vertexaimemorybankservice-管理-memory)
    - [程式碼範例：具有 Session 和 Memory 的天氣代理程式](#程式碼範例具有-session-和-memory-的天氣代理程式)

您可以使用 Gmail 帳號註冊快速模式帳號，並取得 API 金鑰以搭配 ADK 使用。透過 [Google Cloud 控制台](https://console.cloud.google.com/expressmode)取得 API 金鑰。如需詳細資訊，請參閱 [Vertex AI 快速模式](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview)。

> [!NOTE] 預覽版發布
Vertex AI 快速模式功能為預覽版。如需詳細資訊，請參閱[發布階段說明](https://cloud.google.com/products#product-launch-stages)。

> [!TIP] Vertex AI 快速模式限制
Vertex AI 快速模式專案僅在 90 天內有效，且僅提供部分服務供有限配額使用。例如，Agent Engine 的數量限制為 10 個，且部署到 Agent Engine 需要付費存取。若要解除配額限制並使用所有 Vertex AI 服務，請將付款帳戶新增至您的快速模式專案。

## 配置 Agent Engine 容器

使用 Vertex AI 快速模式時，請建立 `AgentEngine` 物件，以啟用對 `Session` 和 `Memory` 等代理程式元件的 Vertex AI 管理。透過此方法，`Session` 物件將作為 `AgentEngine` 物件的子項目進行處理。在執行您的代理程式之前，請確保您的環境變數已正確設定，如下所示：

`agent/.env`
```env title="agent/.env"
# 設定使用 Vertex AI
GOOGLE_GENAI_USE_VERTEXAI=TRUE
# 在此貼上您的快速模式 API 金鑰
GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_EXPRESS_MODE_API_KEY_HERE
```

接下來，使用 Vertex AI SDK 建立您的 Agent Engine 執行個體。

1. 匯入 Vertex AI SDK。

    ```py
    import vertexai
    from vertexai import agent_engines
    ```

2. 使用您的 API 金鑰初始化 Vertex AI 用戶端，並建立代理程式引擎執行個體。

    ```py
    # 使用 Gen AI SDK 建立 Agent Engine
    client = vertexai.Client(
      api_key="YOUR_API_KEY", # 您的 API 金鑰
    )

    # 建立 Agent Engine 執行個體
    agent_engine = client.agent_engines.create(
      config={
        "display_name": "Demo Agent Engine",
        "description": "Agent Engine for Session and Memory",
      })
    ```

3. 從回應中獲取 Agent Engine 名稱和 ID，以便與 Memory 和 Session 一起使用。

    ```py
    # 從資源名稱中解析出 APP_ID
    APP_ID = agent_engine.api_resource.name.split('/')[-1]
    ```

## 使用 `VertexAiSessionService` 管理 Session

[`VertexAiSessionService`](#使用-vertexaisessionservice-管理-session) 與 Vertex AI 快速模式 API 金鑰相容。您可以改為在不指定任何專案或位置的情況下初始化會話物件。

```py
# 需要：pip install google-adk[vertexai]
# 加上環境變數設定：
# GOOGLE_GENAI_USE_VERTEXAI=TRUE
# GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_EXPRESS_MODE_API_KEY_HERE
from google.adk.sessions import VertexAiSessionService

# 搭配此服務使用的 app_name 應為推理引擎 (Reasoning Engine) ID 或名稱
APP_ID = "your-reasoning-engine-id"

# 使用 Vertex 快速模式初始化時，不需要專案和位置
session_service = VertexAiSessionService(agent_engine_id=APP_ID)
# 在呼叫服務方法時使用 REASONING_ENGINE_APP_ID，例如：
# session = await session_service.create_session(app_name=APP_ID, user_id= ...)
```

> [!NOTE] Session 服務配額
> 對於免費的快速模式專案，`VertexAiSessionService` 具有以下配額：
> - 每分鐘 10 次建立、刪除或更新 Vertex AI Agent Engine 會話
> - 每分鐘 30 次附加事件至 Vertex AI Agent Engine 會話

## 使用 `VertexAiMemoryBankService` 管理 Memory

[`VertexAiMemoryBankService`](#使用-vertexaimemorybankservice-管理-memory) 與 Vertex AI 快速模式 API 金鑰相容。您可以改為在不指定任何專案或位置的情況下初始化記憶體物件。

```py
# 需要：pip install google-adk[vertexai]
# 加上環境變數設定：
# GOOGLE_GENAI_USE_VERTEXAI=TRUE
# GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_EXPRESS_MODE_API_KEY_HERE
from google.adk.memory import VertexAiMemoryBankService

# 搭配此服務使用的 app_name 應為推理引擎 (Reasoning Engine) ID 或名稱
APP_ID = "your-reasoning-engine-id"

# 使用快速模式初始化時，不需要專案和位置
memory_service = VertexAiMemoryBankService(agent_engine_id=APP_ID)
# 從該會話生成記憶，以便代理程式可以記住有關使用者的相關細節
# memory = await memory_service.add_session_to_memory(session)
```

> [!TIP] Memory 服務配額
> 對於免費的快速模式專案，`VertexAiMemoryBankService` 具有以下配額：
> - 每分鐘 10 次建立、刪除或更新 Vertex AI Agent Engine 記憶體資源
> - 每分鐘 10 次從 Vertex AI Agent Engine 記憶庫獲取、列出或檢索

### 程式碼範例：具有 Session 和 Memory 的天氣代理程式

此程式碼範例展示了一個利用 `VertexAiSessionService` 和 `VertexAiMemoryBankService` 進行內容管理的氣象代理程式，讓您的代理程式能夠回想起使用者的偏好和對話。

*   [具有 Session 和 Memory 的天氣代理程式](https://github.com/google/adk-docs/blob/main/examples/python/notebooks/express-mode-weather-agent.ipynb)（使用 Vertex AI 快速模式）

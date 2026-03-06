# 適用於 ADK 的 Google Cloud Vertex AI express mode (快速模式)

> 🔔 `更新日期：2026-03-06`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/express-mode/

[`ADK 支援`: `Python v0.1.0` | `Java v0.1.0`] Preview

Google Cloud Vertex AI express mode 提供了一個免費的存取層級，用於原型設計和開發，讓您無需建立完整的 Google Cloud 專案即可使用 Vertex AI 服務。此服務包含對許多強大 Vertex AI 服務的存取，包括：

- [適用於 ADK 的 Google Cloud Vertex AI express mode (快速模式)](#適用於-adk-的-google-cloud-vertex-ai-express-mode-快速模式)
  - [配置 Agent Engine 容器](#配置-agent-engine-容器)
  - [使用 `VertexAiSessionService` 管理對話 (Sessions)](#使用-vertexaisessionservice-管理對話-sessions)
  - [使用 `VertexAiMemoryBankService` 管理記憶 (Memory)](#使用-vertexaimemorybankservice-管理記憶-memory)
    - [程式碼範例：具有對話與記憶功能的天氣 Agent](#程式碼範例具有對話與記憶功能的天氣-agent)

您可以使用 Gmail 帳號註冊 express mode 帳號，並獲得一個與 ADK 搭配使用的 API 金鑰。透過 [Google Cloud 控制台](https://console.cloud.google.com/expressmode) 取得 API 金鑰。欲了解更多資訊，請參閱 [Vertex AI express mode](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview)。

> [!TIP] 預覽版本 (Preview release)
Vertex AI express mode 功能目前為預覽版本。欲了解更多資訊，請參閱 [產品發布階段說明](https://cloud.google.com/products#product-launch-stages)。

> [!WARNING] Vertex AI express mode 限制
Vertex AI express mode 專案僅在 90 天內有效，且僅有部分服務可在限制配額下使用。例如，Agent Engine 的數量限制為 10 個，且部署到 Agent Engine 需要付費存取。若要移除配額限制並使用所有 Vertex AI 服務，請為您的 express mode 專案新增帳單帳戶。

## 配置 Agent Engine 容器

使用 Vertex AI express mode 時，請建立 `AgentEngine` 物件，以啟用對 agent 元件（如 `Session` 和 `Memory` 物件）的 Vertex AI 管理。透過此方法，`Session` 物件將作為 `AgentEngine` 物件的子項進行處理。在執行您的 agent 之前，請確保已正確設定環境變數，如下所示：

`agent/.env`
```text
# 設定使用 Vertex AI
GOOGLE_GENAI_USE_VERTEXAI=TRUE
# 在此處貼上您的實際 Express Mode API 金鑰
GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_EXPRESS_MODE_API_KEY_HERE
```

接著，使用 Vertex AI SDK 建立您的 Agent Engine 執行個體。

1. 匯入 Vertex AI SDK。
   ```python
   # 匯入必要的 Vertex AI 模組
   import vertexai
   from vertexai import agent_engines
   ```

2. 使用您的 API 金鑰初始化 Vertex AI 用戶端，並建立一個 agent engine 執行個體。
   ```python
   # 使用 Gen AI SDK 建立 Agent Engine
   # 使用您的 API 金鑰建立 Vertex AI 用戶端
   client = vertexai.Client(
     api_key="YOUR_API_KEY",
   )

   # 建立 Agent Engine 執行個體並配置顯示名稱與說明
   agent_engine = client.agent_engines.create(
     config={
       "display_name": "Demo Agent Engine",
       "description": "Agent Engine for Session and Memory",
     })
   ```

3. 從回應中取得 Agent Engine 的名稱和 ID，以便與 Memories 和 Sessions 搭配使用。
   ```python
   # 從資源名稱中解析出 APP_ID
   APP_ID = agent_engine.api_resource.name.split('/')[-1]
   ```

## 使用 `VertexAiSessionService` 管理對話 (Sessions)

[`VertexAiSessionService`](../../sessions&memory/session/index.md#使用-sessionservice-管理會話) 與 Vertex AI express mode API 金鑰相容。您可以初始化 session 物件而無需指定任何專案或位置。

```python
# 需要執行：pip install google-adk[vertexai]
# 加上環境變數設定：
# GOOGLE_GENAI_USE_VERTEXAI=TRUE
# GOOGLE_API_KEY=在此處貼上您的實際 EXPRESS MODE API 金鑰
from google.adk.sessions import VertexAiSessionService

# 與此服務搭配使用的 app_name 應為 Reasoning Engine ID 或名稱
APP_ID = "your-reasoning-engine-id"

# 使用 Vertex express mode 初始化時不需要專案 (Project) 和位置 (Location)
session_service = VertexAiSessionService(agent_engine_id=APP_ID)
# 在呼叫服務方法時使用 REASONING_ENGINE_APP_ID，例如：
# session = await session_service.create_session(app_name=APP_ID, user_id= ...)
```

> [!TIP] 對話服務配額 (Session Service Quotas)
對於免費的 express mode 專案，`VertexAiSessionService` 具有以下配額：
> - 每分鐘可建立、刪除或更新 10 個 Vertex AI Agent Engine 對話
> - 每分鐘可附加 30 個事件至 Vertex AI Agent Engine 對話

## 使用 `VertexAiMemoryBankService` 管理記憶 (Memory)

[`VertexAiMemoryBankService`](../../sessions&memory/memory.md#vertex-ai-記憶銀行-memory-bank) 與 Vertex AI express mode API 金鑰相容。您可以初始化 memory 物件而無需指定任何專案或位置。

```python
# 需要執行：pip install google-adk[vertexai]
# 加上環境變數設定：
# GOOGLE_GENAI_USE_VERTEXAI=TRUE
# GOOGLE_API_KEY=在此處貼上您的實際 EXPRESS MODE API 金鑰
from google.adk.memory import VertexAiMemoryBankService

# 與此服務搭配使用的 app_name 應為 Reasoning Engine ID 或名稱
APP_ID = "your-reasoning-engine-id"

# 使用 express mode 初始化時不需要專案和位置
memory_service = VertexAiMemoryBankService(agent_engine_id=APP_ID)
# 從該對話生成記憶，以便 Agent 能夠記住關於使用者的相關詳細資訊
# memory = await memory_service.add_session_to_memory(session)
```

記憶服務配額 (Memory Service Quotas)

對於免費的 express mode 專案，`VertexAiMemoryBankService` 具有以下配額：

- 每分鐘可建立、刪除或更新 10 個 Vertex AI Agent Engine 記憶資源
- 每分鐘可從 Vertex AI Agent Engine 記憶庫 (Memory Bank) 進行 10 次獲取、列出或檢索操作

### 程式碼範例：具有對話與記憶功能的天氣 Agent

此程式碼範例展示了一個利用 `VertexAiSessionService` 和 `VertexAiMemoryBankService` 進行上下文管理的天氣 agent，讓您的 agent 能夠回想使用者的偏好和對話內容。

- [使用 Vertex AI express mode 且具備對話與記憶功能的天氣 Agent](https://github.com/google/adk-docs/blob/main/examples/python/notebooks/express-mode-weather-agent.ipynb)

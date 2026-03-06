# ADK 的 GoodMem 插件

> 🔔 `更新日期：2026-03-06`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/goodmem/

[`ADK 支援`: `Python`]

[GoodMem ADK 插件](https://github.com/PAIR-Systems-Inc/goodmem-adk) 將您的 ADK 代理程式連接到 [GoodMem](https://goodmem.ai)，這是一個基於向量的語意記憶服務。此整合為您的代理程式提供跨對話的持久且可搜尋的記憶，使其能夠回想過去的互動、使用者偏好和上傳的文件。

有兩種整合方式：

| 方式                                          | 描述                                                                                                                      |
| ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **插件 (Plugin)** (`GoodmemPlugin`)                      | 透過 ADK 回呼在每回合提供隱含、確定的記憶。自動儲存所有對話回合和檔案附件。 |
| **工具 (Tools)** (`GoodmemSaveTool`, `GoodmemFetchTool`) | 顯式、由代理程式控制的記憶。代理程式決定何時儲存和檢索資訊。                                      |

## 使用案例

- **為代理程式提供持久記憶**：讓您的代理程式擁有在不同對話中都能依賴的長期記憶。
- **免動手、多模態記憶管理**：自動儲存和檢索對話中的資訊，包括使用者訊息、代理程式回應和檔案附件（PDF、DOCX 等）。
- **從不從零開始**：代理程式可以回想您是誰、討論過什麼內容以及已經處理過的解決方案 —— 節省 Token 並避免重複工作。

## 前提條件

- 一個 [GoodMem](https://goodmem.ai/quick-start) 實例（自行託管或雲端）
- GoodMem API 金鑰
- [Gemini API 金鑰](https://aistudio.google.com/app/api-keys)（用於透過 Gemini 自動建立嵌入 (embeddings)）

## 安裝

```bash
pip install goodmem-adk
```

## 在代理程式中使用

### Plugin 方式 (自動化記憶)
```python
import os
from google.adk.agents import LlmAgent
from google.adk.apps import App
from goodmem_adk import GoodmemPlugin

# 初始化 Goodmem 插件
plugin = GoodmemPlugin(
    base_url=os.getenv("GOODMEM_BASE_URL"),  # 例如 "http://localhost:8080"
    api_key=os.getenv("GOODMEM_API_KEY"),
    top_k=5,  # 每回合檢索的記憶數量
)

# 建立具有持久記憶的代理程式
agent = LlmAgent(
    name="memory_agent",
    model="gemini-2.5-flash",
    instruction="你是一個具有持久記憶的得力助手。",
)

# 將插件加入應用程式
app = App(name="GoodmemPluginDemo", root_agent=agent, plugins=[plugin])
```
---
### Tools 方式 (代理程式控制的記憶)
```python
import os
from google.adk.agents import LlmAgent
from google.adk.apps import App
from goodmem_adk import GoodmemSaveTool, GoodmemFetchTool

# 初始化儲存與檢索工具
save_tool = GoodmemSaveTool(
    base_url=os.getenv("GOODMEM_BASE_URL"),  # 例如 "http://localhost:8080"
    api_key=os.getenv("GOODMEM_API_KEY"),
)
fetch_tool = GoodmemFetchTool(
    base_url=os.getenv("GOODMEM_BASE_URL"),
    api_key=os.getenv("GOODMEM_API_KEY"),
    top_k=5,
)

# 建立代理程式並配置工具
agent = LlmAgent(
    name="memory_agent",
    model="gemini-2.5-flash",
    instruction="你是一個具有持久記憶的得力助手。",
    tools=[save_tool, fetch_tool],
)

# 建立應用程式
app = App(name="GoodmemToolsDemo", root_agent=agent)
```

## 可用工具

### 插件回呼 (Plugin callbacks)

`GoodmemPlugin` 使用 ADK 回呼來自動管理記憶：

| 回呼                       | 描述                                                  |
| -------------------------- | ------------------------------------------------------------ |
| `on_user_message_callback` | 將使用者訊息和檔案附件儲存到記憶中           |
| `before_model_callback`    | 檢索相關記憶並將其注入到提示 (prompt) 中 |
| `after_model_callback`     | 將代理程式的回應儲存到記憶中                         |

這些回呼是確定的，並在每次代理程式互動期間執行，將通過代理程式的所有資訊儲存到記憶中。代理程式不需要決定何時儲存或檢索資訊。

### 工具

使用工具方式時，代理程式可以訪問：

| 工具            | 描述                                                 |
| --------------- | ----------------------------------------------------------- |
| `goodmem_save`  | 將文字內容和檔案附件儲存到持久記憶中 |
| `goodmem_fetch` | 使用語意相似性查詢搜尋記憶           |

這些工具由代理程式根據需求調用，代理程式可以根據對話上下文選擇何時儲存（可能經過改寫）或檢索資訊。

## 配置

### 環境變數

| 變數              | 必填 | 描述                                           |
| --------------------- | -------- | ----------------------------------------------------- |
| `GOODMEM_BASE_URL`    | 是      | GoodMem 伺服器 URL（不含 `/v1` 後綴）             |
| `GOODMEM_API_KEY`     | 是      | GoodMem 的 API 金鑰                                   |
| `GOOGLE_API_KEY`      | 是      | 用於自動建立 Gemini 嵌入器的 Gemini API 金鑰      |
| `GOODMEM_EMBEDDER_ID` | 否       | 固定特定的嵌入器（必須存在）                  |
| `GOODMEM_SPACE_ID`    | 否       | 固定特定的記憶空間（必須存在）              |
| `GOODMEM_SPACE_NAME`  | 否       | 覆蓋預設空間名稱（如果缺少則自動建立） |

### 空間解析 (Space resolution)

如果未配置空間，系統會為每個使用者自動建立一個：

- 插件：`adk_chat_{user_id}`
- 工具：`adk_tool_{user_id}`

## 額外資源

- [GitHub 上的 GoodMem ADK](https://github.com/PAIR-Systems-Inc/goodmem-adk)
- [GoodMem 文件](https://goodmem.ai)
- [PyPI 上的 GoodMem ADK](https://pypi.org/project/goodmem-adk/)

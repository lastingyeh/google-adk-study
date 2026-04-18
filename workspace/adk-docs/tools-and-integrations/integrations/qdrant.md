# Qdrant MCP tool for ADK

> 🔔 `更新日期：2026-03-09`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/qdrant/

[`ADK 支援`: `Python` | `TypeScript`]

[Qdrant MCP 伺服器](https://github.com/qdrant/mcp-server-qdrant) 將您的 ADK 代理程式連接到 [Qdrant](https://qdrant.tech/)，這是一個開源的向量搜尋引擎。此整合讓您的代理程式具備使用語意搜尋來儲存和檢索資訊的能力。

## 使用案例

- **代理程式的語意記憶**：儲存對話上下文、事實或學習到的資訊，代理程式稍後可以使用自然語言查詢進行檢索。
- **程式碼儲存庫搜尋**：建立程式碼片段、文件和實作模式的可搜尋索引，並可以進行語意查詢。
- **知識庫檢索**：透過儲存文件並為回應檢索相關上下文，建立一個檢索增強生成 (RAG) 系統。

## 先決條件

- 一個執行中的 Qdrant 實體。您可以：
  - 使用 [Qdrant Cloud](https://cloud.qdrant.io/)（託管服務）
  - 使用 Docker 在本地端執行：`docker run -p 6333:6333 qdrant/qdrant`
- （選用）用於驗證的 Qdrant API 金鑰

## 在代理程式中使用

<details>
<summary>範例說明</summary>

> Python

**Local MCP Server**
```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# 設定 Qdrant URL (本地端或雲端)
QDRANT_URL = "http://localhost:6333"  # 或您的 Qdrant Cloud URL
# 設定集合名稱
COLLECTION_NAME = "my_collection"
# QDRANT_API_KEY = "YOUR_QDRANT_API_KEY"

# 建立根代理程式
root_agent = Agent(
    model="gemini-2.5-pro",
    name="qdrant_agent",
    instruction="幫助使用者使用語意搜尋儲存和檢索資訊",
    tools=[
        # 設定 MCP 工具集以連接 Qdrant
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="uvx",
                    args=["mcp-server-qdrant"],
                    env={
                        "QDRANT_URL": QDRANT_URL,
                        "COLLECTION_NAME": COLLECTION_NAME,
                        # "QDRANT_API_KEY": QDRANT_API_KEY,
                    }
                ),
                timeout=30,
            ),
        )
    ],
)
```

> TypeScript

**Local MCP Server**
```typescript
import { LlmAgent, MCPToolset } from "@google.adk";

// 設定 Qdrant URL
const QDRANT_URL = "http://localhost:6333"; // 或您的 Qdrant Cloud URL
// 設定集合名稱
const COLLECTION_NAME = "my_collection";
// const QDRANT_API_KEY = "YOUR_QDRANT_API_KEY";

// 初始化代理程式
const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "qdrant_agent",
    instruction: "幫助使用者使用語意搜尋儲存和檢索資訊",
    tools: [
        // 使用 Stdio 連接參數配置 MCP 工具集
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "uvx",
                args: ["mcp-server-qdrant"],
                env: {
                    QDRANT_URL: QDRANT_URL,
                    COLLECTION_NAME: COLLECTION_NAME,
                    // QDRANT_API_KEY: QDRANT_API_KEY,
                },
            },
        }),
    ],
});

export { rootAgent };
```

</details>

## 可用工具

| 工具           | 描述                                           |
| -------------- | ---------------------------------------------- |
| `qdrant-store` | 在 Qdrant 中儲存資訊，可包含選用的詮釋資料 (metadata) |
| `qdrant-find`  | 使用自然語言查詢搜尋相關資訊                   |

## 配置

Qdrant MCP 伺服器可以使用環境變數進行配置：

| 變數                 | 描述                                            | 預設值                                   |
| -------------------- | ----------------------------------------------- | ---------------------------------------- |
| `QDRANT_URL`         | Qdrant 伺服器的 URL                             | `None` (必填)                            |
| `QDRANT_API_KEY`     | Qdrant Cloud 驗證用的 API 金鑰                  | `None`                                   |
| `COLLECTION_NAME`    | 要使用的集合名稱                                | `None`                                   |
| `QDRANT_LOCAL_PATH`  | 本地持久化儲存的路徑 (URL 的替代方案)           | `None`                                   |
| `EMBEDDING_MODEL`    | 要使用的嵌入模型 (Embedding model)              | `sentence-transformers/all-MiniLM-L6-v2` |
| `EMBEDDING_PROVIDER` | 嵌入提供者 (`fastembed` 或 `ollama`)            | `fastembed`                              |
| `TOOL_STORE_DESCRIPTION` | 儲存工具的自定義描述                        | 預設描述                                 |
| `TOOL_FIND_DESCRIPTION`  | 搜尋工具的自定義描述                        | 預設描述                                 |

### 自定義工具描述

您可以自定義工具描述來引導代理程式的行為：

```python
env={
    "QDRANT_URL": "http://localhost:6333",
    "COLLECTION_NAME": "code-snippets",
    # 自定義儲存工具描述，引導代理程式如何處理程式碼片段
    "TOOL_STORE_DESCRIPTION": "儲存帶有描述的程式碼片段。'information' 參數應包含程式碼功能的描述，而實際程式碼應放在 'metadata.code' 中。",
    # 自定義搜尋工具描述，引導代理程式如何搜尋功能
    "TOOL_FIND_DESCRIPTION": "使用自然語言搜尋相關程式碼片段。請描述您正在尋找的功能。",
}
```

## 其他資源

- [Qdrant MCP 伺服器儲存庫](https://github.com/qdrant/mcp-server-qdrant)
- [Qdrant 文件](https://qdrant.tech/documentation/)
- [Qdrant Cloud](https://cloud.qdrant.io/)

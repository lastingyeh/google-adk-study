# Qdrant

> 🔔 `更新日期：2026-01-27`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/tools/third-party/qdrant/

[Qdrant MCP 伺服器](https://github.com/qdrant/mcp-server-qdrant) 將您的 ADK 代理連接到 [Qdrant](https://qdrant.tech/)，這是一個開源的向量搜尋引擎。這種整合使您的代理能夠使用語義搜尋來儲存和檢索資訊。

## 使用案例

- **代理的語義記憶**：儲存對話上下文、事實或學到的資訊，代理稍後可以使用自然語言查詢來檢索。

- **程式碼庫搜尋**：建立程式碼片段、文件和實作模式的可搜尋索引，並可以進行語義查詢。

- **知識庫檢索**：透過儲存文件並檢索相關上下文進行回應，建立檢索增強生成 (RAG) 系統。

## 先決條件

- 一個執行中的 Qdrant 實例。您可以：
    - 使用 [Qdrant Cloud](https://cloud.qdrant.io/)（託管服務）
    - 使用 Docker 在本地執行：`docker run -p 6333:6333 qdrant/qdrant`
- （選填）用於身份驗證的 Qdrant API 金鑰

## 與代理一起使用

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# Qdrant 伺服器 URL，或您的 Qdrant Cloud URL
QDRANT_URL = "http://localhost:6333"
# 集合名稱
COLLECTION_NAME = "my_collection"
# Qdrant API 金鑰（如果需要）
# QDRANT_API_KEY = "YOUR_QDRANT_API_KEY"

# 建立根代理
root_agent = Agent(
    model="gemini-2.5-pro",
    name="qdrant_agent",
    instruction="協助使用者使用語義搜尋儲存和檢索資訊",
    tools=[
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

## 可用工具

工具 | 描述
---- | -----------
`qdrant-store` | 在 Qdrant 中儲存資訊，可包含選填的元數據
`qdrant-find` | 使用自然語言查詢搜尋相關資訊

## 配置

Qdrant MCP 伺服器可以使用環境變數進行配置：

變數 | 描述 | 預設值
-------- | ----------- | -------
`QDRANT_URL` | Qdrant 伺服器的 URL | `None` (必填)
`QDRANT_API_KEY` | 用於 Qdrant Cloud 身份驗證的 API 金鑰 | `None`
`COLLECTION_NAME` | 要使用的集合名稱 | `None`
`QDRANT_LOCAL_PATH` | 本地持久化儲存的路徑（URL 的替代方案） | `None`
`EMBEDDING_MODEL` | 要使用的嵌入模型 | `sentence-transformers/all-MiniLM-L6-v2`
`EMBEDDING_PROVIDER` | 嵌入提供者 (`fastembed` 或 `ollama`) | `fastembed`
`TOOL_STORE_DESCRIPTION` | 儲存工具的自定義描述 | 預設描述
`TOOL_FIND_DESCRIPTION` | 搜尋工具的自定義描述 | 預設描述

### 自定義工具描述

您可以自定義工具描述來引導代理的行為：

```python
env={
    "QDRANT_URL": "http://localhost:6333",
    "COLLECTION_NAME": "code-snippets",
    # 儲存包含描述的程式碼片段。'information' 參數應包含程式碼作用的描述，而實際程式碼應放在 'metadata.code' 中。
    "TOOL_STORE_DESCRIPTION": "Store code snippets with descriptions. The 'information' parameter should contain a description of what the code does, while the actual code should be in 'metadata.code'.",
    # 使用自然語言搜尋相關的程式碼片段。描述您正在尋找的功能。
    "TOOL_FIND_DESCRIPTION": "Search for relevant code snippets using natural language. Describe the functionality you're looking for.",
}
```

## 其他資源

- [Qdrant MCP 伺服器儲存庫](https://github.com/qdrant/mcp-server-qdrant)
- [Qdrant 文件](https://qdrant.tech/documentation/)
- [Qdrant Cloud](https://cloud.qdrant.io/)

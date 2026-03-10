# 用於 ADK 的 Pinecone MCP 工具

> 🔔 `更新日期：2026-03-08`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/pinecone/

[`ADK 支援`: `Python` | `TypeScript`]

[Pinecone MCP 伺服器](https://github.com/pinecone-io/pinecone-mcp) 將您的 ADK 代理程式連接到 [Pinecone](https://www.pinecone.io/)，這是一個用於 AI 應用程式的向量資料庫。此整合讓您的代理程式能夠管理索引、使用具有元數據篩選（metadata filtering）的語義搜尋（semantic search）來儲存和搜尋資料，以及透過重排序（reranking）跨多個索引進行搜尋。

## 使用案例

- **語義搜尋與檢索**：使用自然語言查詢並搭配元數據篩選與重排序來搜尋儲存的資料。
- **知識庫管理**：儲存並管理資料，以建立和維護檢索增強生成（RAG）系統。
- **跨索引搜尋**：同時搜尋多個 Pinecone 索引，並自動對結果進行去重（deduplication）與重排序。

## 前置作業

- 一個 [Pinecone](https://www.pinecone.io/) 帳戶
- 來自 [Pinecone 控制台](https://app.pinecone.io) 的 API 金鑰

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

# 您的 Pinecone API 金鑰
PINECONE_API_KEY = "YOUR_PINECONE_API_KEY"

# 初始化根代理程式
root_agent = Agent(
    model="gemini-2.5-pro",
    name="pinecone_agent",
    instruction="幫助使用者管理和搜尋他們的 Pinecone 向量索引",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@pinecone-database/mcp",
                    ],
                    env={
                        "PINECONE_API_KEY": PINECONE_API_KEY,
                    }
                ),
                timeout=30,
            ),
        )
    ],
)
```

> typescript

**Local MCP Server**
```typescript
import { LlmAgent, MCPToolset } from "@google/adk";

// 您的 Pinecone API 金鑰
const PINECONE_API_KEY = "YOUR_PINECONE_API_KEY";

// 初始化根代理程式
const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "pinecone_agent",
    instruction: "幫助使用者管理和搜尋他們的 Pinecone 向量索引",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: ["-y", "@pinecone-database/mcp"],
                env: {
                    PINECONE_API_KEY: PINECONE_API_KEY,
                },
            },
        }),
    ],
});

export { rootAgent };
```

</details>

> [!NOTE]注意
僅支援具有 [整合推理（integrated inference）](https://docs.pinecone.io/guides/inference/understanding-inference) 的索引。此 MCP 伺服器不支援不具備整合嵌入模型（embedding model）的索引。

## 可用工具

### 文件相關

| 工具          | 描述                                |
| ------------- | ----------------------------------- |
| `search-docs` | 搜尋 Pinecone 官方文件 |

### 索引管理

| 工具                     | 描述                                                                    |
| ------------------------ | ----------------------------------------------------------------------- |
| `list-indexes`           | 列出所有 Pinecone 索引                                                      |
| `describe-index`         | 描述索引的配置                                         |
| `describe-index-stats`   | 取得索引的統計資訊，包括記錄數和可用的命名空間 |
| `create-index-for-model` | 建立一個具有整合推理模型的新索引以用於嵌入            |

### 資料操作

| 工具               | 描述                                                                             |
| ------------------ | -------------------------------------------------------------------------------- |
| `upsert-records`   | 在具有整合推理的索引中插入或更新記錄                          |
| `search-records`   | 使用文字查詢搜尋記錄，並可選用元數據篩選與重排序功能 |
| `cascading-search` | 跨多個索引進行搜尋，並對結果進行去重與重排序                 |
| `rerank-documents` | 使用專門的重排序模型對記錄或文字文件集合進行重排序    |

## 其他資源

- [Pinecone MCP 伺服器儲存庫](https://github.com/pinecone-io/pinecone-mcp)
- [Pinecone MCP 文件](https://docs.pinecone.io/guides/operations/mcp-server)
- [Pinecone 文件](https://docs.pinecone.io)

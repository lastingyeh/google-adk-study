# 用於 ADK 的 MongoDB MCP 工具

> 🔔 `更新日期：2026-03-08`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/mongodb/

[`ADK 支援`: `Python` | `TypeScript`]

[MongoDB MCP 伺服器](https://github.com/mongodb-js/mongodb-mcp-server) 將您的 ADK 代理程式連接到 [MongoDB](https://www.mongodb.com/) 資料庫和 MongoDB Atlas 叢集。此整合讓您的代理程式能夠使用自然語言查詢集合、管理資料庫以及與 MongoDB Atlas 基礎設施互動。

## 使用案例

- **數據探索與分析**：使用自然語言查詢 MongoDB 集合、執行聚合，並在不手動撰寫複雜查詢的情況下分析文件架構。
- **資料庫管理**：透過對話式指令列出資料庫和集合、建立索引、管理使用者並監控資料庫統計數據。
- **Atlas 基礎設施管理**：直接從您的代理程式建立和管理 MongoDB Atlas 叢集、配置存取清單並查看效能建議。

## 前提條件

- **對於資料庫存取**：一個 MongoDB 連接字串（本機、自託管或 Atlas 叢集）
- **對於 Atlas 管理**：一個具有 API 憑證（用戶端 ID 和金鑰）的 [MongoDB Atlas](https://www.mongodb.com/atlas) 服務帳戶

## 與代理程式搭配使用

<details>
<summary>範例說明</summary>

> Python

**Local MCP Server**
```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# 對於資料庫存取，使用連接字串：
CONNECTION_STRING = "mongodb://localhost:27017/myDatabase"

# 對於 Atlas 管理，使用 API 憑證：
# ATLAS_CLIENT_ID = "YOUR_ATLAS_CLIENT_ID"
# ATLAS_CLIENT_SECRET = "YOUR_ATLAS_CLIENT_SECRET"

root_agent = Agent(
    model="gemini-2.5-pro",
    name="mongodb_agent",
    instruction="幫助使用者查詢和管理 MongoDB 資料庫",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "mongodb-mcp-server",
                        "--readOnly",  # 對於寫入操作請移除此項
                    ],
                    env={
                        # 對於資料庫存取，使用：
                        "MDB_MCP_CONNECTION_STRING": CONNECTION_STRING,
                        # 對於 Atlas 管理，使用：
                        # "MDB_MCP_API_CLIENT_ID": ATLAS_CLIENT_ID,
                        # "MDB_MCP_API_CLIENT_SECRET": ATLAS_CLIENT_SECRET,
                    },
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
import { LlmAgent, MCPToolset } from "@google/adk";

// 對於資料庫存取，使用連接字串：
const CONNECTION_STRING = "mongodb://localhost:27017/myDatabase";

// 對於 Atlas 管理，使用 API 憑證：
// const ATLAS_CLIENT_ID = "YOUR_ATLAS_CLIENT_ID";
// const ATLAS_CLIENT_SECRET = "YOUR_ATLAS_CLIENT_SECRET";

const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "mongodb_agent",
    instruction: "幫助使用者查詢和管理 MongoDB 資料庫",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: [
                    "-y",
                    "mongodb-mcp-server",
                    "--readOnly", // 對於寫入操作請移除此項
                ],
                env: {
                    // 對於資料庫存取，使用：
                    MDB_MCP_CONNECTION_STRING: CONNECTION_STRING,
                    // 對於 Atlas 管理，使用：
                    // MDB_MCP_API_CLIENT_ID: ATLAS_CLIENT_ID,
                    // MDB_MCP_API_CLIENT_SECRET: ATLAS_CLIENT_SECRET,
                },
            },
        }),
    ],
});

export { rootAgent };
```

</details>

## 可用工具

### MongoDB 資料庫工具

| 工具 | 描述 |
| -------------------- | ----------------------------------------------- |
| `find` | 對 MongoDB 集合執行尋找查詢 |
| `aggregate` | 對 MongoDB 集合執行聚合 |
| `count` | 取得集合中的文件數量 |
| `list-databases` | 列出 MongoDB 連接的所有資料庫 |
| `list-collections` | 列出指定資料庫的所有集合 |
| `collection-schema` | 描述集合的架構 |
| `collection-indexes` | 描述集合的索引 |
| `insert-many` | 將文件插入集合 |
| `update-many` | 更新符合篩選條件的文件 |
| `delete-many` | 移除符合篩選條件的文件 |
| `create-collection` | 建立新集合 |
| `drop-collection` | 從資料庫移除集合 |
| `drop-database` | 移除資料庫 |
| `create-index` | 為集合建立索引 |
| `drop-index` | 從集合中移除索引 |
| `rename-collection` | 重新命名集合 |
| `db-stats` | 取得資料庫統計數據 |
| `explain` | 取得查詢執行統計數據 |
| `export` | 以 EJSON 格式匯出查詢結果 |

### MongoDB Atlas 工具

注意

Atlas 工具需要 API 憑證。設定 `MDB_MCP_API_CLIENT_ID` 和 `MDB_MCP_API_CLIENT_SECRET` 環境變數以啟用它們。

| 工具 | 描述 |
| ------------------------------- | -------------------------------- |
| `atlas-list-orgs` | 列出 MongoDB Atlas 組織 |
| `atlas-list-projects` | 列出 MongoDB Atlas 專案 |
| `atlas-list-clusters` | 列出 MongoDB Atlas 叢集 |
| `atlas-inspect-cluster` | 檢查叢集的中繼資料 |
| `atlas-list-db-users` | 列出資料庫使用者 |
| `atlas-create-free-cluster` | 建立免費的 Atlas 叢集 |
| `atlas-create-project` | 建立 Atlas 專案 |
| `atlas-create-db-user` | 建立資料庫使用者 |
| `atlas-create-access-list` | 配置 IP 存取清單 |
| `atlas-inspect-access-list` | 查看 IP 存取清單條目 |
| `atlas-list-alerts` | 列出 Atlas 警示 |
| `atlas-get-performance-advisor` | 取得效能建議 |

## 配置

### 環境變數

| 變數 | 描述 |
| --------------------------- | --------------------------------------------- |
| `MDB_MCP_CONNECTION_STRING` | 用於資料庫存取的 MongoDB 連接字串 |
| `MDB_MCP_API_CLIENT_ID` | 用於 Atlas 工具的 Atlas API 用戶端 ID |
| `MDB_MCP_API_CLIENT_SECRET` | 用於 Atlas 工具的 Atlas API 用戶端金鑰 |
| `MDB_MCP_READ_ONLY` | 啟用唯讀模式 (`true` 或 `false`) |
| `MDB_MCP_DISABLED_TOOLS` | 以逗號分隔的停用工具清單 |
| `MDB_MCP_LOG_PATH` | 日誌檔案目錄 |

### 唯讀模式

`--readOnly` 旗標將伺服器限制為僅能執行讀取、連接和中繼資料操作。這可以防止任何建立、更新或刪除操作，使其在數據探索時是安全的，不會有意外修改的風險。

### 停用工具

您可以使用 `MDB_MCP_DISABLED_TOOLS` 停用特定工具或類別：

- 工具名稱：`find`、`aggregate`、`insert-many` 等。
- 類別：`atlas` (所有 Atlas 工具)、`mongodb` (所有資料庫工具)
- 操作類型：`create`、`update`、`delete`、`read`、`metadata`

## 其他資源

- [MongoDB MCP 伺服器儲存庫](https://github.com/mongodb-js/mongodb-mcp-server)
- [MongoDB 文件](https://www.mongodb.com/docs/)
- [MongoDB Atlas](https://www.mongodb.com/atlas)

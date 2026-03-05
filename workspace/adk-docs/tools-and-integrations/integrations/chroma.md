# ADK 的 Chroma MCP 工具

> 🔔 `更新日期：2026-03-05`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/chroma/

[`ADK 支援`: `Python` | `TypeScript`]

[Chroma MCP 伺服器](https://github.com/chroma-core/chroma-mcp) 將您的 ADK 代理程式連接到 [Chroma](https://www.trychroma.com/)，這是一個開源的向量嵌入資料庫（embedding database）。此整合使您的代理程式能夠建立集合（collections）、儲存文件，並使用語義搜尋、全文檢索和元數據（metadata）篩選來檢索資訊。

## 使用案例

- **代理程式的語義記憶**：儲存對話上下文、事實或學到的資訊，代理程式稍後可以使用自然語言查詢進行檢索。
- **知識庫檢索**：透過儲存文件並為回應檢索相關上下文，構建檢索增強生成（RAG）系統。
- **跨會話的持久化上下文**：在對話之間維持長期記憶，允許代理程式引用過去的互動和累積的知識。

## 先決條件

- **對於本地儲存**：用於持久化資料的目錄路徑。
- **對於 Chroma Cloud**：一個包含租戶 ID（tenant ID）、資料庫名稱和 API 金鑰的 [Chroma Cloud](https://www.trychroma.com/) 帳戶。

## 搭配代理程式使用

<details>
<summary>範例說明</summary>

> Python

**Local MCP Server**
```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# 對於本地儲存，使用：
DATA_DIR = "/path/to/your/data/directory"

# 對於 Chroma Cloud，使用：
# CHROMA_TENANT = "your-tenant-id"
# CHROMA_DATABASE = "your-database-name"
# CHROMA_API_KEY = "your-api-key"

root_agent = Agent(
    model="gemini-2.5-pro",
    name="chroma_agent",
    instruction="協助使用者使用語義搜尋儲存和檢索資訊",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="uvx",
                    args=[
                        "chroma-mcp",
                        # 對於本地儲存，使用：
                        "--client-type",
                        "persistent",
                        "--data-dir",
                        DATA_DIR,
                        # 對於 Chroma Cloud，使用：
                        # "--client-type",
                        # "cloud",
                        # "--tenant",
                        # CHROMA_TENANT,
                        # "--database",
                        # CHROMA_DATABASE,
                        # "--api-key",
                        # CHROMA_API_KEY,
                    ],
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

// 對於本地儲存，使用：
const DATA_DIR = "/path/to/your/data/directory";

// 對於 Chroma Cloud，使用：
// const CHROMA_TENANT = "your-tenant-id";
// const CHROMA_DATABASE = "your-database-name";
// const CHROMA_API_KEY = "your-api-key";

const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "chroma_agent",
    instruction: "協助使用者使用語義搜尋儲存和檢索資訊",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "uvx",
                args: [
                    "chroma-mcp",
                    // 對於本地儲存，使用：
                    "--client-type",
                    "persistent",
                    "--data-dir",
                    DATA_DIR,
                    // 對於 Chroma Cloud，使用：
                    // "--client-type",
                    // "cloud",
                    // "--tenant",
                    // CHROMA_TENANT,
                    // "--database",
                    // CHROMA_DATABASE,
                    // "--api-key",
                    // CHROMA_API_KEY,
                ],
            },
        }),
    ],
});

export { rootAgent };
```

</details>

## 可用的工具

### 集合管理

| 工具                          | 描述                                              |
| ----------------------------- | ------------------------------------------------- |
| `chroma_list_collections`     | 列出所有集合，支援分頁                            |
| `chroma_create_collection`    | 建立新集合，可選配 HNSW 設定                      |
| `chroma_get_collection_info`  | 獲取集合的詳細資訊                                |
| `chroma_get_collection_count` | 獲取集合中的文件數量                              |
| `chroma_modify_collection`    | 更新集合的名稱或元數據                            |
| `chroma_delete_collection`    | 刪除集合                                          |
| `chroma_peek_collection`      | 查看集合中文件的範例                              |

### 文件操作

| 工具                      | 描述                                              |
| ------------------------- | ------------------------------------------------- |
| `chroma_add_documents`    | 新增文件，可選配元數據和自定義 ID                 |
| `chroma_query_documents`  | 使用語義搜尋查詢文件，支援進階篩選                |
| `chroma_get_documents`    | 透過 ID 或篩選器檢索文件，支援分頁                |
| `chroma_update_documents` | 更新現有文件的內容、元數據或嵌入向量              |
| `chroma_delete_documents` | 從集合中刪除特定文件                              |

## 設定

Chroma MCP 伺服器支援多種客戶端類型以適應不同需求：

### 客戶端類型

| 客戶端類型  | 描述                                                | 關鍵參數                                                 |
| ----------- | --------------------------------------------------- | -------------------------------------------------------- |
| `ephemeral` | 記憶體內儲存，重新啟動後會清除。適用於測試。        | 無（預設）                                               |
| `persistent` | 您本地機器上的檔案型儲存                            | `--data-dir`                                             |
| `http`      | 連接到自行託管的 Chroma 伺服器                      | `--host`, `--port`, `--ssl`, `--custom-auth-credentials` |
| `cloud`     | 連接到 Chroma Cloud (api.trychroma.com)             | `--tenant`, `--database`, `--api-key`                    |

### 環境變數

您也可以使用環境變數來設定客戶端。命令列參數的優先級高於環境變數。

| 變數                 | 描述                                                       |
| -------------------- | ---------------------------------------------------------- |
| `CHROMA_CLIENT_TYPE` | 客戶端類型：`ephemeral`、`persistent`、`http` 或 `cloud` |
| `CHROMA_DATA_DIR`    | 本地持久化儲存的路徑                                       |
| `CHROMA_TENANT`      | Chroma Cloud 的租戶 ID                                     |
| `CHROMA_DATABASE`    | Chroma Cloud 的資料庫名稱                                  |
| `CHROMA_API_KEY`     | Chroma Cloud 的 API 金鑰                                   |
| `CHROMA_HOST`        | 自行託管 HTTP 客戶端的主機                                 |
| `CHROMA_PORT`        | 自行託管 HTTP 客戶端的連接埠                               |
| `CHROMA_SSL`         | 為 HTTP 客戶端啟用 SSL（`true` 或 `false`）                |
| `CHROMA_DOTENV_PATH` | `.env` 檔案的路徑（預設為 `.chroma_env`）                  |

## 其他資源

- [Chroma MCP 伺服器儲存庫](https://github.com/chroma-core/chroma-mcp)
- [Chroma 文件](https://docs.trychroma.com/)
- [Chroma Cloud](https://www.trychroma.com/)

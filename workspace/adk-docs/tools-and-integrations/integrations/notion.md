# ADK 的 Notion MCP 工具

> 🔔 `更新日期：2026-03-08`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/notion/

[`ADK 支援`: `Python` | `TypeScript`]

[Notion MCP 伺服器](https://github.com/makenotion/notion-mcp-server) 將您的 ADK 代理程式連接到 Notion，使其能夠在工作區中搜尋、建立和管理頁面、資料庫等。這讓您的代理程式能夠使用自然語言在 Notion 工作區中查詢、建立和組織內容。

## 使用案例

- **搜尋您的工作區**：根據內容尋找專案頁面、會議記錄或文件。
- **建立新內容**：為會議記錄、專案計畫或任務產生新頁面。
- **管理任務和資料庫**：更新任務狀態、向資料庫新增項目或更改屬性。
- **組織您的工作區**：移動頁面、複製範本或向文件新增評論。

## 先決條件

- 在個人資料中前往 [Notion Integrations](https://www.notion.so/profile/integrations) 取得 Notion 整合權杖。如需更多詳細資訊，請參閱 [授權說明文件](https://developers.notion.com/docs/authorization)。
- 確保您的整合可以存取相關頁面和資料庫。請造訪 [Notion Integration](https://www.notion.so/profile/integrations) 設定中的「存取 (Access)」索引標籤，然後選取您想要使用的頁面以授予存取權限。

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

# 您的 Notion 權杖
NOTION_TOKEN = "YOUR_NOTION_TOKEN"

# 初始化根代理程式
root_agent = Agent(
    model="gemini-2.5-pro",
    name="notion_agent",
    instruction="幫助使用者從 Notion 獲取資訊",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@notionhq/notion-mcp-server",
                    ],
                    env={
                        "NOTION_TOKEN": NOTION_TOKEN,
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
import { LlmAgent, MCPToolset } from "@google/adk";

// 您的 Notion 權杖
const NOTION_TOKEN = "YOUR_NOTION_TOKEN";

// 初始化根代理程式
const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "notion_agent",
    instruction: "幫助使用者從 Notion 獲取資訊",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: ["-y", "@notionhq/notion-mcp-server"],
                env: {
                    NOTION_TOKEN: NOTION_TOKEN,
                },
            },
        }),
    ],
});

export { rootAgent };
```

</details>

## 可用工具

| 工具 | 描述 |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `notion-search` | 在您的 Notion 工作區以及連接的工具（如 Slack、Google Drive 和 Jira）中進行搜尋。如果 AI 功能不可用，則回退到基本工作區搜尋。 |
| `notion-fetch` | 透過 URL 從 Notion 頁面或資料庫檢索內容。 |
| `notion-create-pages` | 建立一個或多個具有指定屬性和內容的 Notion 頁面。 |
| `notion-update-page` | 更新 Notion 頁面的屬性或內容。 |
| `notion-move-pages` | 將一個或多個 Notion 頁面或資料庫移動到新的父級。 |
| `notion-duplicate-page` | 在您的工作區內複製 Notion 頁面。此動作是非同步完成的。 |
| `notion-create-database` | 建立新的 Notion 資料庫、初始資料來源和具有指定屬性的初始視圖。 |
| `notion-update-database` | 更新 Notion 資料來源的屬性、名稱、描述或其他屬性。 |
| `notion-create-comment` | 向頁面新增評論。 |
| `notion-get-comments` | 列出特定頁面上的所有評論，包括執行緒討論。 |
| `notion-get-teams` | 檢索目前工作區中的團隊（teamspaces）列表。 |
| `notion-get-users` | 列出工作區中的所有使用者及其詳細資訊。 |
| `notion-get-user` | 透過 ID 檢索您的使用者資訊。 |
| `notion-get-self` | 檢索有關您自己的機器人使用者以及您連接到的 Notion 工作區的資訊。 |

## 其他資源

- [Notion MCP 伺服器說明文件](https://developers.notion.com/docs/mcp)
- [Notion MCP 伺服器儲存庫](https://github.com/makenotion/notion-mcp-server)

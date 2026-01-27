# Notion

> 🔔 `更新日期：2026-01-27`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/tools/third-party/notion/

[Notion MCP 伺服器](https://github.com/makenotion/notion-mcp-server) 將您的 ADK 代理程式連接到 Notion，使其能夠在工作區內搜尋、建立和管理頁面、資料庫等。這讓您的代理程式能夠使用自然語言在您的 Notion 工作區中查詢、建立和組織內容。

## 使用案例

- **搜尋您的工作區**：根據內容尋找專案頁面、會議記錄或文件。

- **建立新內容**：為會議記錄、專案計畫或任務生成新頁面。

- **管理任務和資料庫**：更新任務狀態、向資料庫新增項目或更改屬性。

- **組織您的工作區**：移動頁面、複製模板或向文件新增評論。

## 先決條件

- 在您的個人資料中前往 [Notion 整合 (Integrations)](https://www.notion.so/profile/integrations) 以取得 Notion 整合權杖。如需更多詳細資訊，請參閱 [授權文件](https://developers.notion.com/docs/authorization)。
- 確保您的整合可以存取相關的頁面和資料庫。造訪您的 [Notion 整合 (Integration)](https://www.notion.so/profile/integrations) 設定中的「存取 (Access)」分頁，然後透過選擇您想使用的頁面來授予存取權限。

## 與代理程式搭配使用

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# 填入您的 Notion 整合權杖
NOTION_TOKEN = "YOUR_NOTION_TOKEN"

# 初始化負責處理 Notion 相關請求的代理程式
root_agent = Agent(
    model="gemini-2.5-pro",
    name="notion_agent",
    instruction="幫助使用者從 Notion 獲取資訊",
    tools=[
        # 使用 McpToolset 連接到外部的 Notion MCP 伺服器
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
                timeout=30, # 設定連接逾時時間為 30 秒
            ),
        )
    ],
)
```

## 可用工具

工具 | 描述
---- | -----------
`notion-search` | 在您的 Notion 工作區以及連接的工具（如 Slack、Google Drive 和 Jira）中進行搜尋。如果 AI 功能不可用，則退回到基本的工作區搜尋。
`notion-fetch` | 透過 URL 從 Notion 頁面或資料庫中檢索內容。
`notion-create-pages` | 使用指定的屬性和內容建立一個或多個 Notion 頁面。
`notion-update-page` | 更新 Notion 頁面的屬性或內容。
`notion-move-pages` | 將一個或多個 Notion 頁面或資料庫移動到新的父級。
`notion-duplicate-page` | 在工作區內複製 Notion 頁面。此動作是非同步完成的。
`notion-create-database` | 建立新的 Notion 資料庫、初始資料來源和具有指定屬性的初始視圖。
`notion-update-database` | 更新 Notion 資料來源的屬性、名稱、描述或其他屬性。
`notion-create-comment` | 向頁面新增評論。
`notion-get-comments` | 列出特定頁面上的所有評論，包括線程討論。
`notion-get-teams` | 檢索目前工作區中的團隊（teamspaces）列表。
`notion-get-users` | 列出工作區中的所有使用者及其詳細資訊。
`notion-get-user` | 透過 ID 檢索您的使用者資訊。
`notion-get-self` | 檢索有關您自己的機器人使用者和您連接到的 Notion 工作區的資訊。

## 其他資源

- [Notion MCP 伺服器文件](https://developers.notion.com/docs/mcp)
- [Notion MCP 伺服器儲存庫](https://github.com/makenotion/notion-mcp-server)

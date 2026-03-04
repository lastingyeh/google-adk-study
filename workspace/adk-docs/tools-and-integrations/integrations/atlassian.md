# 適用於 ADK 的 Atlassian MCP 工具

> 🔔 `更新日期：2026-03-04`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/atlassian/

[`ADK 支援`: `Python` | `TypeScript`]

[Atlassian MCP 伺服器](https://github.com/atlassian/atlassian-mcp-server) 將您的 ADK 代理程式連接到 [Atlassian](https://www.atlassian.com/) 生態系統，彌合了 Jira 中的專案追蹤與 Confluence 中的知識管理之間的差距。此整合讓您的代理程式能夠使用自然語言管理議題、搜尋及更新文件頁面，並簡化協作工作流程。

## 使用案例

- **統一知識搜尋**：同時搜尋 Jira 議題和 Confluence 頁面，以查找專案規格、決策或歷史背景。
- **自動化議題管理**：建立、編輯和轉換 Jira 議題，或為現有工單添加評論。
- **文件助手**：直接從您的代理程式檢索頁面內容、生成草稿或在 Confluence 文件中添加內嵌評論。

## 先決條件

- 註冊 [Atlassian 帳戶](https://id.atlassian.com/signup)
- 擁有包含 Jira 和/或 Confluence 的 Atlassian Cloud 網站

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


root_agent = Agent(
    model="gemini-2.5-pro",
    name="atlassian_agent",
    instruction="幫助使用者處理 Atlassian 產品中的資料",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "mcp-remote",
                        "https://mcp.atlassian.com/v1/mcp",
                    ]
                ),
                timeout=30,
            ),
        )
    ],
)
# 初始化 Atlassian 代理程式，並配置 MCP 工具集以連接遠端 Atlassian MCP 伺服器
```

> TypeScript

**Local MCP Server**
```typescript
import { LlmAgent, MCPToolset } from "@google/adk";

const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "atlassian_agent",
    instruction: "幫助使用者處理 Atlassian 產品中的資料",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: [
                    "-y",
                    "mcp-remote",
                    "https://mcp.atlassian.com/v1/mcp",
                ],
            },
        }),
    ],
});
// 建立 LlmAgent 實例，使用 MCPToolset 整合 Atlassian 遙測功能

export { rootAgent };
```

</details>

> [!NOTE] 注意
當您第一次執行此代理程式時，會自動開啟瀏覽器視窗以要求透過 OAuth 進行存取。或者，您可以使用控制台中印出的授權 URL。您必須核准此要求，以允許代理程式存取您的 Atlassian 資料。

## 可用工具

| 工具                               | 描述                                                |
| ---------------------------------- | ---------------------------------------------------------- |
| `atlassianUserInfo`                | 獲取使用者資訊                             |
| `getAccessibleAtlassianResources`  | 獲取可存取的 Atlassian 資源資訊       |
| `getJiraIssue`                     | 獲取 Jira 議題資訊                         |
| `editJiraIssue`                    | 編輯 Jira 議題                                   |
| `createJiraIssue`                  | 建立新的 Jira 議題                               |
| `getTransitionsForJiraIssue`       | 獲取 Jira 議題的狀態轉換資訊                           |
| `transitionJiraIssue`              | 轉換 Jira 議題狀態                               |
| `lookupJiraAccountId`              | 查詢 Jira 帳戶 ID                                   |
| `searchJiraIssuesUsingJql`         | 使用 JQL 搜尋 Jira 議題                               |
| `addCommentToJiraIssue`            | 為 Jira 議題添加評論                              |
| `getJiraIssueRemoteIssueLinks`     | 獲取 Jira 議題的遠端議題連結                    |
| `getVisibleJiraProjects`           | 獲取可見的 Jira 專案                           |
| `getJiraProjectIssueTypesMetadata` | 獲取 Jira 專案的議題類型元數據                |
| `getJiraIssueTypeMetaWithFields`   | 獲取帶有欄位的 Jira 議題類型元數據       |
| `getConfluenceSpaces`              | 獲取 Confluence 空間資訊                    |
| `getConfluencePage`                | 獲取 Confluence 頁面資訊                    |
| `getPagesInConfluenceSpace`        | 獲取 Confluence 空間中的頁面資訊          |
| `getConfluencePageFooterComments`  | 獲取 Confluence 頁面的頁尾評論資訊 |
| `getConfluencePageInlineComments`  | 獲取 Confluence 頁面的內嵌評論資訊 |
| `getConfluencePageDescendants`     | 獲取 Confluence 頁面的子系資訊     |
| `createConfluencePage`             | 建立新的 Confluence 頁面                               |
| `updateConfluencePage`             | 更新現有的 Confluence 頁面                         |
| `createConfluenceFooterComment`    | 在 Confluence 頁面中建立頁尾評論               |
| `createConfluenceInlineComment`    | 在 Confluence 頁面中建立內嵌評論              |
| `searchConfluenceUsingCql`         | 使用 CQL 搜尋 Confluence                                |
| `search`                           | 搜尋資訊                                     |
| `fetch`                            | 獲取資訊                                          |

## 其他資源

- [Atlassian MCP 伺服器儲存庫](https://github.com/atlassian/atlassian-mcp-server)
- [Atlassian MCP 伺服器文件](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/)

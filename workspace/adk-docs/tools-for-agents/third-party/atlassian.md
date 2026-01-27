# Atlassian

> 🔔 `更新日期：2026-01-27`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/tools/third-party/atlassian/

[Atlassian MCP 伺服器](https://github.com/atlassian/atlassian-mcp-server) 將您的 ADK 代理連結至 [Atlassian](https://www.atlassian.com/) 生態系統，縮短了 Jira 中的專案追蹤與 Confluence 中的知識管理之間的差距。此整合賦予您的代理管理議題、搜尋及更新文件頁面，以及使用自然語言簡化協作工作流程的能力。

## 使用案例

- **統一知識搜尋**：同時搜尋 Jira 議題和 Confluence 頁面，以查找專案規格、決策或歷史背景。

- **自動化議題管理**：建立、編輯和轉換 Jira 議題，或為現有票券添加評論。

- **文件助手**：直接從您的代理中檢索頁面內容、生成草稿或在 Confluence 文件中添加行內評論。

## 先決條件

- 註冊 [Atlassian 帳戶](https://id.atlassian.com/signup)
- 包含 Jira 和/或 Confluence 的 Atlassian Cloud 站點

## 與代理一起使用

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# 初始化 root_agent
root_agent = Agent(
    model="gemini-2.5-pro", # 使用的模型版本
    name="atlassian_agent", # 代理名稱
    instruction="Help users work with data in Atlassian products", # 指令說明
    tools=[
        # 設定 MCP 工具集
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "mcp-remote",
                        "https://mcp.atlassian.com/v1/sse",
                    ]
                ),
                timeout=30, # 設定逾時時間
            ),
        )
    ],
)
```

> [!NOTE]
當您第一次運行此代理時，會自動打開一個瀏覽器視窗以請求透過 OAuth 進行訪問。或者，您可以使用控制台中顯示的授權 URL。您必須批准此請求，以允許代理訪問您的 Atlassian 數據。

## 可用工具

工具 | 描述
---- | -----------
`atlassianUserInfo` | 獲取有關使用者的資訊
`getAccessibleAtlassianResources` | 獲取有關可訪問的 Atlassian 資源的資訊
`getJiraIssue` | 獲取有關 Jira 議題的資訊
`editJiraIssue` | 編輯 Jira 議題
`createJiraIssue` | 建立新的 Jira 議題
`getTransitionsForJiraIssue` | 獲取 Jira 議題的轉換狀態
`transitionJiraIssue` | 轉換 Jira 議題狀態
`lookupJiraAccountId` | 查找 Jira 帳戶 ID
`searchJiraIssuesUsingJql` | 使用 JQL 搜尋 Jira 議題
`addCommentToJiraIssue` | 為 Jira 議題添加評論
`getJiraIssueRemoteIssueLinks` | 獲取 Jira 議題的遠端議題連結
`getVisibleJiraProjects` | 獲取可見的 Jira 專案
`getJiraProjectIssueTypesMetadata` | 獲取 Jira 專案的議題類型詮釋資料
`getJiraIssueTypeMetaWithFields` | 獲取包含欄位的 Jira 議題類型詮釋資料
`getConfluenceSpaces` | 獲取有關 Confluence 空間的資訊
`getConfluencePage` | 獲取有關 Confluence 頁面的資訊
`getPagesInConfluenceSpace` | 獲取有關 Confluence 空間中頁面的資訊
`getConfluencePageFooterComments` | 獲取有關 Confluence 頁面頁尾評論的資訊
`getConfluencePageInlineComments` | 獲取有關 Confluence 頁面行內評論的資訊
`getConfluencePageDescendants` | 獲取有關 Confluence 頁面子代頁面的資訊
`createConfluencePage` | 建立新的 Confluence 頁面
`updateConfluencePage` | 更新現有的 Confluence 頁面
`createConfluenceFooterComment` | 在 Confluence 頁面中建立頁尾評論
`createConfluenceInlineComment` | 在 Confluence 頁面中建立行內評論
`searchConfluenceUsingCql` | 使用 CQL 搜尋 Confluence
`search` | 搜尋資訊
`fetch` | 獲取資訊

## 額外資源

- [Atlassian MCP 伺服器儲存庫](https://github.com/atlassian/atlassian-mcp-server)
- [Atlassian MCP 伺服器文件](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/)

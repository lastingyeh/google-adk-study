# GitHub

> 🔔 `更新日期：2026-01-27`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/tools/third-party/github/

[GitHub MCP 伺服器](https://github.com/github/github-mcp-server) 將 AI 工具直接連接到 GitHub 平台。這讓您的 ADK 代理程式能夠閱讀儲存庫和程式碼檔案、管理議題 (Issues) 和提取請求 (PRs)、分析程式碼，並使用自然語言自動化工作流程。

## 使用案例

- **儲存庫管理**：瀏覽和查詢程式碼、搜尋檔案、分析提交 (Commits)，並在您有權限存取的任何儲存庫中了解專案結構。
- **議題與提取請求自動化**：建立、更新和管理議題與提取請求。讓 AI 協助分類錯誤 (Bugs)、審閱程式碼變更並維護專案看板。
- **程式碼分析**：檢查安全性發現、審閱 Dependabot 警報、了解程式碼模式，並獲得對程式碼庫的全面洞察。

## 前置作業

- 在 GitHub 中建立 [個人存取權杖 (Personal Access Token)](https://github.com/settings/personal-access-tokens/new)。欲了解更多資訊，請參閱 [說明文件](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)。

## 與代理程式搭配使用

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

# 您的 GitHub 個人存取權杖
GITHUB_TOKEN = "YOUR_GITHUB_TOKEN"

# 初始化 GitHub 代理程式
root_agent = Agent(
    model="gemini-2.5-pro",
    name="github_agent",
    instruction="幫助使用者從 GitHub 獲取資訊",
    tools=[
        McpToolset(
            # 設定連線參數以連接到遠端 MCP 伺服器
            connection_params=StreamableHTTPServerParams(
                url="https://api.githubcopilot.com/mcp/",
                headers={
                    "Authorization": f"Bearer {GITHUB_TOKEN}",
                    "X-MCP-Toolsets": "all",
                    "X-MCP-Readonly": "true"
                },
            ),
        )
    ],
)
```

## 可用工具

工具 | 說明
---- | -----------
`context` | 提供有關當前使用者和您正在操作的 GitHub 上下文資訊的工具
`copilot` | 與 Copilot 相關的工具（例如 Copilot Coding Agent）
`copilot_spaces` | 與 Copilot Spaces 相關的工具
`actions` | GitHub Actions 工作流程和 CI/CD 操作
`code_security` | 與程式碼安全相關的工具，例如 GitHub 程式碼掃描 (Code Scanning)
`dependabot` | Dependabot 工具
`discussions` | 與 GitHub 討論 (Discussions) 相關的工具
`experiments` | 尚未被視為穩定的實驗性功能
`gists` | 與 GitHub Gist 相關的工具
`github_support_docs_search` | 搜尋文件以回答 GitHub 產品和支援問題
`issues` | 與 GitHub 議題 (Issues) 相關的工具
`labels` | 與 GitHub 標籤 (Labels) 相關的工具
`notifications` | 與 GitHub 通知 (Notifications) 相關的工具
`orgs` | 與 GitHub 組織 (Organizations) 相關的工具
`projects` | 與 GitHub 專案 (Projects) 相關的工具
`pull_requests` | 與 GitHub 提取請求 (Pull Requests) 相關的工具
`repos` | 與 GitHub 儲存庫 (Repositories) 相關的工具
`secret_protection` | 秘密保護相關工具，例如 GitHub 秘密掃描 (Secret Scanning)
`security_advisories` | 與安全性建議 (Security Advisories) 相關的工具
`stargazers` | 與 GitHub Stargazers 相關的工具
`users` | 與 GitHub 使用者 (Users) 相關的工具

## 配置

遠端 GitHub MCP 伺服器具有可用於配置可用工具集和唯讀模式的可選標頭 (Headers)：

- `X-MCP-Toolsets`：要啟用的工具集的逗號分隔列表。（例如 "repos,issues"）
    - 如果列表為空，將使用預設工具集。如果提供了錯誤的工具集，伺服器將無法啟動並發出 400 錯誤請求狀態。空格會被忽略。

- `X-MCP-Readonly`：僅啟用「讀取」工具。
    - 如果此標頭為空、"false"、"f"、"no"、"n"、"0" 或 "off"（忽略空格和大小寫），則會被解釋為 false。所有其他值都被解釋為 true。


## 額外資源

- [GitHub MCP 伺服器儲存庫](https://github.com/github/github-mcp-server)
- [遠端 GitHub MCP 伺服器說明文件](https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md)
- [GitHub MCP 伺服器的政策與治理](https://github.com/github/github-mcp-server/blob/main/docs/policies-and-governance.md)

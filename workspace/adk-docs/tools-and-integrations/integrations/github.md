# 適用於 ADK 的 GitHub MCP 工具

> 🔔 `更新日期：2026-03-06`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/github/

[`ADK 支援`: `Python` | `TypeScript`]

[GitHub MCP 伺服器](https://github.com/github/github-mcp-server) 將 AI 工具直接連接到 GitHub 平台。這讓您的 ADK 代理程式能夠讀取儲存庫和程式碼檔案、管理議題 (Issues) 和提取請求 (PRs)、分析程式碼，並使用自然語言自動化工作流程。

## 使用案例

- **儲存庫管理**：瀏覽和查詢程式碼、搜尋檔案、分析提交 (Commits)，並在您有權存取的任何儲存庫中了解專案結構。
- **議題與 PR 自動化**：建立、更新和管理議題與提取請求。讓 AI 協助分類錯誤 (Bugs)、審查程式碼變更並維護專案看板。
- **程式碼分析**：檢查安全性發現、審查 Dependabot 警報、了解程式碼模式，並獲得對程式碼庫的全面見解。

## 前提條件

- 在 GitHub 中建立 [個人存取權杖 (Personal Access Token)](https://github.com/settings/personal-access-tokens/new)。有關更多資訊，請參閱 [說明文件](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)。

## 與代理程式搭配使用

<details>
<summary>範例說明</summary>

> Python

**Remote MCP Server**
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
    instruction="協助使用者從 GitHub 獲取資訊",
    tools=[
        McpToolset(
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

> TypeScript

**Remote MCP Server**
```typescript
import { LlmAgent, MCPToolset } from "@google/adk";

// 您的 GitHub 個人存取權杖
const GITHUB_TOKEN = "YOUR_GITHUB_TOKEN";

// 初始化 GitHub 代理程式
const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "github_agent",
    instruction: "協助使用者從 GitHub 獲取資訊",
    tools: [
        new MCPToolset({
            type: "StreamableHTTPConnectionParams",
            url: "https://api.githubcopilot.com/mcp/",
            transportOptions: {
                requestInit: {
                    headers: {
                        Authorization: `Bearer ${GITHUB_TOKEN}`,
                        "X-MCP-Toolsets": "all",
                        "X-MCP-Readonly": "true",
                    },
                },
            },
        }),
    ],
});

export { rootAgent };
```

</details>

## 可用工具

| 工具                         | 描述                                                                               |
| ---------------------------- | ----------------------------------------------------------------------------------------- |
| `context`                    | 提供有關目前使用者和您正在操作的 GitHub 上下文資訊的工具                                |
| `copilot`                    | Copilot 相關工具（例如 Copilot 編碼代理程式）                                         |
| `copilot_spaces`             | Copilot Spaces 相關工具                                                              |
| `actions`                    | GitHub Actions 工作流程和 CI/CD 操作                                             |
| `code_security`              | 程式碼安全相關工具，例如 GitHub 程式碼掃描 (Code Scanning)                                 |
| `dependabot`                 | Dependabot 工具                                                                 |
| `discussions`                | GitHub 討論 (Discussions) 相關工具                                                                 |
| `experiments`                | 尚未被視為穩定的實驗性功能                                  |
| `gists`                      | GitHub Gist 相關工具                                                                 |
| `github_support_docs_search` | 搜尋文件以回答 GitHub 產品和支援問題                                |
| `issues`                     | GitHub 議題 (Issues) 相關工具                                                               |
| `labels`                     | GitHub 標籤 (Labels) 相關工具                                                               |
| `notifications`              | GitHub 通知 (Notifications) 相關工具                                                        |
| `orgs`                       | GitHub 組織 (Organization) 相關工具                                                             |
| `projects`                   | GitHub 專案 (Projects) 相關工具                                                             |
| `pull_requests`              | GitHub 提取請求 (Pull Request) 相關工具                                                         |
| `repos`                      | GitHub 儲存庫 (Repository) 相關工具                                                             |
| `secret_protection`          | 秘密保護相關工具，例如 GitHub 秘密掃描 (Secret Scanning)                           |
| `security_advisories`        | 安全通報 (Security advisories) 相關工具                                                         |
| `stargazers`                 | GitHub Stargazers 相關工具                                                         |
| `users`                      | GitHub 使用者相關工具                                                                 |

## 配置

遠端 GitHub MCP 伺服器具有可用於配置可用工具集和唯讀模式的可選標頭：

- `X-MCP-Toolsets`：要啟用的工具集清單，以逗號分隔。（例如，"repos,issues"）

  - 如果清單為空，將使用預設工具集。如果提供了錯誤的工具集，伺服器將無法啟動並發出 400 錯誤請求狀態。空白字元會被忽略。

- `X-MCP-Readonly`：僅啟用「讀取」工具。

  - 如果此標頭為空、"false"、"f"、"no"、"n"、"0" 或 "off"（忽略空白和大小寫），則會被解釋為 false。所有其他值都將被解釋為 true。

## 其他資源

- [GitHub MCP 伺服器儲存庫](https://github.com/github/github-mcp-server)
- [遠端 GitHub MCP 伺服器文件](https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md)
- [GitHub MCP 伺服器的政策與治理](https://github.com/github/github-mcp-server/blob/main/docs/policies-and-governance.md)

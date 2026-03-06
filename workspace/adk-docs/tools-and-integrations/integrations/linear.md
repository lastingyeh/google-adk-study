# ADK 的 Linear MCP 工具

> 🔔 `更新日期：2026-03-06`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/linear/

[`ADK 支援`: `Python` | `TypeScript`]

[Linear MCP 伺服器](https://linear.app/docs/mcp) 將您的 ADK 代理（Agent）連接到 [Linear](https://linear.app/)，這是一個專為規劃和構建產品而設計的工具。此整合讓您的代理能夠使用自然語言管理議題（Issues）、追蹤專案週期（Cycles）並自動化開發工作流程。

## 使用案例

- **簡化議題管理**：使用自然語言建立、更新和組織議題。讓您的代理處理記錄 Bug、分配任務和更新狀態。
- **追蹤專案和週期**：即時掌握團隊的進度。查詢活動週期的狀態、檢查專案里程碑並檢索截止日期。
- **上下文搜尋與總結**：快速跟上長篇討論串或尋找特定的專案規範。您的代理可以搜尋文件並總結複雜的議題。

## 先決條件

- [註冊](https://linear.app/signup) Linear 帳號
- 在 [Linear 設定 > 安全性與存取](https://linear.app/docs/security-and-access) 中生成 API 金鑰（如果使用 API 驗證）

## 與代理搭配使用

### Python
<details>
<summary>Local MCP Server</summary>

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# 建立根代理，負責管理 Linear 中的議題、專案和週期
root_agent = Agent(
    model="gemini-2.5-pro",
    name="linear_agent",
    instruction="幫助使用者管理 Linear 中的議題、專案和週期",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "mcp-remote",
                        "https://mcp.linear.app/mcp",
                    ]
                ),
                timeout=30,
            ),
        )
    ],
)
```

</details>

注意

當您第一次執行此代理時，系統會自動打開一個瀏覽器視窗以要求透過 OAuth 進行存取。或者，您可以使用控制台中顯示的授權 URL。您必須核准此要求以允許代理存取您的 Linear 資料。

<details>
<summary>Remote MCP Server</summary>

> Python

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

# 請替換為您的 Linear API 金鑰
LINEAR_API_KEY = "YOUR_LINEAR_API_KEY"

# 使用 API 金鑰驗證建立代理
root_agent = Agent(
    model="gemini-2.5-pro",
    name="linear_agent",
    instruction="幫助使用者管理 Linear 中的議題、專案和週期",
    tools=[
        McpToolset(
            connection_params=StreamableHTTPServerParams(
                url="https://mcp.linear.app/mcp",
                headers={
                    "Authorization": f"Bearer {LINEAR_API_KEY}",
                },
            ),
        )
    ],
)
```

</details>

注意

此程式碼範例使用 API 金鑰進行驗證。若要改用基於瀏覽器的 OAuth 驗證流程，請移除 `headers` 參數並執行代理。

### TypeScript
<details>
<summary>Local MCP Server</summary>

> TypeScript

```typescript
import { LlmAgent, MCPToolset } from "@google/adk";

// 使用 Stdio 連接參數建立 Linear 代理
const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "linear_agent",
    instruction: "幫助使用者管理 Linear 中的議題、專案和週期",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: ["-y", "mcp-remote", "https://mcp.linear.app/mcp"],
            },
        }),
    ],
});

export { rootAgent };
```

</details>

注意

當您第一次執行此代理時，系統會自動打開一個瀏覽器視窗以要求透過 OAuth 進行存取。或者，您可以使用控制台中顯示的授權 URL。您必須核准此要求以允許代理存取您的 Linear 資料。

<details>
<summary>Remote MCP Server</summary>

> TypeScript

```typescript
import { LlmAgent, MCPToolset } from "@google/adk";

// 請替換為您的 Linear API 金鑰
const LINEAR_API_KEY = "YOUR_LINEAR_API_KEY";

// 使用 HTTP 連接參數與 API 金鑰建立代理
const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "linear_agent",
    instruction: "幫助使用者管理 Linear 中的議題、專案和週期",
    tools: [
        new MCPToolset({
            type: "StreamableHTTPConnectionParams",
            url: "https://mcp.linear.app/mcp",
            transportOptions: {
                requestInit: {
                    headers: {
                        Authorization: `Bearer ${LINEAR_API_KEY}`,
                    },
                },
            },
        }),
    ],
});

export { rootAgent };
```

</details>

注意

此程式碼範例使用 API 金鑰進行驗證。若要改用基於瀏覽器的 OAuth 驗證流程，請移除 `header` 屬性並執行代理。

## 可用工具

| 工具                   | 描述                         |
| ---------------------- | ---------------------------- |
| `list_comments`        | 列出議題上的評論             |
| `create_comment`       | 在議題上建立評論             |
| `list_cycles`          | 列出專案中的週期             |
| `get_document`         | 獲取文件                     |
| `list_documents`       | 列出文件                     |
| `get_issue`            | 獲取議題                     |
| `list_issues`          | 列出議題                     |
| `create_issue`         | 建立議題                     |
| `update_issue`         | 更新議題                     |
| `list_issue_statuses`  | 列出議題狀態                 |
| `get_issue_status`     | 獲取議題狀態                 |
| `list_issue_labels`    | 列出議題標籤                 |
| `create_issue_label`   | 建立議題標籤                 |
| `list_projects`        | 列出專案                     |
| `get_project`          | 獲取專案                     |
| `create_project`       | 建立專案                     |
| `update_project`       | 更新專案                     |
| `list_project_labels`  | 列出專案標籤                 |
| `list_teams`           | 列出團隊                     |
| `get_team`             | 獲取團隊                     |
| `list_users`           | 列出使用者                   |
| `get_user`             | 獲取使用者                   |
| `search_documentation` | 搜尋文件                     |

## 其他資源

- [Linear MCP 伺服器文件](https://linear.app/docs/mcp)
- [Linear 入門指南](https://linear.app/docs/start-guide)

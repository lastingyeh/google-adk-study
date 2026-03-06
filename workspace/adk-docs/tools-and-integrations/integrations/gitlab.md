# GitLab MCP tool for ADK

> 🔔 `更新日期：2026-03-06`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/gitlab/

[`ADK 支援`: `Python` | `TypeScript`]

[GitLab MCP 伺服器](https://docs.gitlab.com/user/gitlab_duo/model_context_protocol/mcp_server/) 將您的 ADK 代理直接連接到 [GitLab.com](https://gitlab.com/) 或您的自管理 GitLab 實例。此整合賦予您的代理管理議題（issues）和合併請求（merge requests）、檢查 CI/CD 管道、執行語義程式碼搜尋以及使用自然語言自動化開發工作流程的能力。

## 使用場景

- **語義程式碼探索**：使用自然語言瀏覽您的程式碼庫。與標準文字搜尋不同，您可以查詢程式碼的邏輯和意圖，以快速理解複雜的實作。
- **加速合併請求審查**：即時掌握程式碼變更。檢索完整的合併請求上下文，分析特定的差異（diffs），並審查提交歷史，以便為您的團隊提供更快、更有意義的反饋。
- **排除 CI/CD 管道故障**：無需離開聊天介面即可診斷構建失敗。檢查管道狀態並檢索詳細的工作日誌，以準確找出特定合併請求或提交未能通過檢查的原因。

## 前置條件

- 具有 Premium 或 Ultimate 訂閱且啟用了 [GitLab Duo](https://docs.gitlab.com/user/gitlab_duo/) 的 GitLab 帳戶
- 在您的 GitLab 設定中啟用了 [Beta 和實驗性功能](https://docs.gitlab.com/user/gitlab_duo/turn_on_off/#turn-on-beta-and-experimental-features)

## 與代理搭配使用

<details>
<summary>範例說明</summary>

> Python

**Local MCP Server**
```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# 如果是自託管，請替換為您的實例 URL (例如 "gitlab.example.com")
GITLAB_INSTANCE_URL = "gitlab.com"

root_agent = Agent(
    model="gemini-2.5-pro",
    name="gitlab_agent",
    instruction="幫助使用者從 GitLab 獲取資訊",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "mcp-remote",
                        f"https://{GITLAB_INSTANCE_URL}/api/v4/mcp",
                        "--static-oauth-client-metadata",
                        "{\"scope\": \"mcp\"}",
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

// 如果是自託管，請替換為您的實例 URL (例如 "gitlab.example.com")
const GITLAB_INSTANCE_URL = "gitlab.com";

const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "gitlab_agent",
    instruction: "幫助使用者從 GitLab 獲取資訊",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: [
                    "-y",
                    "mcp-remote",
                    `https://${GITLAB_INSTANCE_URL}/api/v4/mcp`,
                    "--static-oauth-client-metadata",
                    '{"scope": "mcp"}',
                ],
            },
        }),
    ],
});

export { rootAgent };
```

</details>

註記

當您第一次執行此代理時，系統會自動打開一個瀏覽器視窗（並印出授權 URL）要求 OAuth 權限。您必須核准此請求以允許代理訪問您的 GitLab 數據。

## 可用工具

| 工具                          | 描述                                                               |
| ----------------------------- | ------------------------------------------------------------------------- |
| `get_mcp_server_version`      | 返回 GitLab MCP 伺服器的當前版本                      |
| `create_issue`                | 在 GitLab 專案中建立新議題                                   |
| `get_issue`                   | 檢索有關特定 GitLab 議題的詳細資訊              |
| `create_merge_request`        | 在專案中建立合併請求                                      |
| `get_merge_request`           | 檢索有關特定 GitLab 合併請求的詳細資訊      |
| `get_merge_request_commits`   | 檢索特定合併請求中的提交列表                 |
| `get_merge_request_diffs`     | 檢索特定合併請求的差異（diffs）                          |
| `get_merge_request_pipelines` | 檢索特定合併請求的管道                      |
| `get_pipeline_jobs`           | 檢索特定 CI/CD 管道的工作                      |
| `gitlab_search`               | 使用搜尋 API 在整個 GitLab 實例中搜尋關鍵字 |
| `semantic_code_search`        | 在專案中搜尋相關的程式碼片段                          |

## 其他資源

- [GitLab MCP 伺服器文件](https://docs.gitlab.com/user/gitlab_duo/model_context_protocol/mcp_server/)

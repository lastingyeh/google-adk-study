# ADK 的 AgentMail MCP 工具

[`ADK 支援`: `Python` | `TypeScript`]

> 🔔 `更新日期：2026-03-04`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/agentmail/

[AgentMail MCP 伺服器](https://github.com/agentmail-to/agentmail-mcp) 將您的 ADK 代理程式連接到 [AgentMail](https://agentmail.to/)，這是一個專為 AI 代理程式構建的電子郵件收件匣 API。此整合讓您的代理程式擁有自己的電子郵件收件匣，可以使用自然語言發送、接收、回覆和轉發郵件。

## 使用案例

- **賦予代理程式自己的收件匣**：為您的代理程式建立專屬電子郵件地址，以便它們可以像人類團隊成員一樣獨立發送和接收電子郵件。
- **自動化電子郵件工作流程**：讓您的代理程式端到端處理電子郵件對話，包括發送初始外聯、閱讀回覆以及跟進執行緒。
- **管理跨收件匣的對話**：列出並搜尋執行緒和郵件、轉發電子郵件並檢索附件，以保持代理程式的資訊通暢和回應迅速。

## 先決條件

- 建立 [AgentMail 帳戶](https://agentmail.to/)
- 從 [AgentMail 儀表板](https://agentmail.to/) 產生 API 金鑰

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

# 設定您的 AgentMail API 金鑰
AGENTMAIL_API_KEY = "YOUR_AGENTMAIL_API_KEY"

# 初始化根代理程式
root_agent = Agent(
    model="gemini-2.5-pro",
    name="agentmail_agent",
    instruction="協助使用者管理電子郵件收件匣並發送郵件",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "agentmail-mcp",
                    ],
                    env={
                        "AGENTMAIL_API_KEY": AGENTMAIL_API_KEY,
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

// 設定您的 AgentMail API 金鑰
const AGENTMAIL_API_KEY = "YOUR_AGENTMAIL_API_KEY";

// 初始化根代理程式
const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "agentmail_agent",
    instruction: "協助使用者管理電子郵件收件匣並發送郵件",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: ["-y", "agentmail-mcp"],
                env: {
                    AGENTMAIL_API_KEY: AGENTMAIL_API_KEY,
                },
            },
        }),
    ],
});

export { rootAgent };
```

</details>

## 可用工具

### 收件匣管理

| 工具           | 描述                                   |
| -------------- | -------------------------------------- |
| `list_inboxes` | 列出所有收件匣                         |
| `get_inbox`    | 取得特定收件匣的詳細資訊               |
| `create_inbox` | 使用使用者名稱和網域建立新的收件匣     |
| `delete_inbox` | 刪除收件匣                             |

### 執行緒管理

| 工具             | 描述                             |
| ---------------- | -------------------------------- |
| `list_threads`   | 列出收件匣中的執行緒             |
| `get_thread`     | 取得包含其郵件的特定執行緒       |
| `get_attachment` | 從郵件中下載附件                 |

### 郵件操作

| 工具               | 描述                                   |
| ------------------ | -------------------------------------- |
| `send_message`     | 從收件匣發送新電子郵件                 |
| `reply_to_message` | 回覆現有郵件                           |
| `forward_message`  | 將郵件轉發給另一個收件人               |
| `update_message`   | 更新郵件屬性，例如閱讀狀態             |

## 其他資源

- [AgentMail MCP 伺服器儲存庫](https://github.com/agentmail-to/agentmail-mcp)
- [AgentMail 文件](https://docs.agentmail.to/)
- [AgentMail 工具包](https://github.com/agentmail-to/agentmail-toolkit)

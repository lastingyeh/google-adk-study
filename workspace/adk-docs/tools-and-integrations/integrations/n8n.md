# ADK 的 n8n MCP 工具

> 🔔 `更新日期：2026-03-08`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/n8n/

[`ADK 支援`: `Python` | `TypeScript`]

[n8n MCP 伺服器](https://docs.n8n.io/advanced-ai/accessing-n8n-mcp-server/) 將您的 ADK 代理 (Agent) 連接到 [n8n](https://n8n.io/)，這是一個可擴展的工作流自動化工具。此整合允許您的代理安全地連接到 n8n 實例，直接從自然語言介面搜尋、檢查並觸發工作流。

> [!NOTE] 替代方案：工作流級別的 MCP 伺服器
本頁面的配置指南涵蓋了 **實例級別的 MCP 存取**，它將您的代理連接到啟用的工作流中心樞紐。或者，您可以使用 [MCP 伺服器觸發節點](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcptrigger/)，讓 **單個工作流** 作為其獨立的 MCP 伺服器。如果您想製作特定的伺服器行為或公開與單個工作流隔離的工具，此方法非常有用。

## 使用場景

- **執行複雜的工作流**：直接從您的代理觸發在 n8n 中定義的多步驟業務流程，利用可靠的分支邏輯、迴圈和錯誤處理來確保一致性。
- **連接到外部應用程式**：透過 n8n 存取預先建置的整合，而無需為每個服務編寫自訂工具，從而消除了管理 API 身份驗證、標頭或樣板程式碼的需要。
- **數據處理**：將複雜的數據轉換任務卸載到 n8n 工作流，例如將自然語言轉換為 API 呼叫，或者抓取並總結網頁，利用自訂的 Python 或 JavaScript 節點進行精確的數據塑形。

## 前置條件

- 一個作用中的 n8n 實例
- 在設置中啟用了 MCP 存取
- 一個有效的 MCP 存取權杖 (Access Token)

請參閱 [n8n MCP 文件](https://docs.n8n.io/advanced-ai/accessing-n8n-mcp-server/) 以獲取詳細的設置說明。

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

# 設定 n8n 實例網址與 MCP 權杖
N8N_INSTANCE_URL = "https://localhost:5678"
N8N_MCP_TOKEN = "YOUR_N8N_MCP_TOKEN"

# 建立根代理
root_agent = Agent(
    model="gemini-2.5-pro",
    name="n8n_agent",
    instruction="幫助使用者管理與執行 n8n 中的工作流",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "supergateway",
                        "--streamableHttp",
                        f"{N8N_INSTANCE_URL}/mcp-server/http",
                        "--header",
                        f"authorization:Bearer {N8N_MCP_TOKEN}"
                    ]
                ),
                timeout=300,
            ),
        )
    ],
)
```

> Python (HTTP)

**Remote MCP Server**
```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

# 設定 n8n 實例網址與 MCP 權杖
N8N_INSTANCE_URL = "https://localhost:5678"
N8N_MCP_TOKEN = "YOUR_N8N_MCP_TOKEN"

# 建立根代理，使用 Streamable HTTP 連線
root_agent = Agent(
    model="gemini-2.5-pro",
    name="n8n_agent",
    instruction="幫助使用者管理與執行 n8n 中的工作流",
    tools=[
        McpToolset(
            connection_params=StreamableHTTPServerParams(
                url=f"{N8N_INSTANCE_URL}/mcp-server/http",
                headers={
                    "Authorization": f"Bearer {N8N_MCP_TOKEN}",
                },
            ),
        )
    ],
)
```

> TypeScript (Stdio)

**Local MCP Server**
```typescript
import { LlmAgent, MCPToolset } from "@google/adk";

// 設定 n8n 實例網址與 MCP 權杖
const N8N_INSTANCE_URL = "https://localhost:5678";
const N8N_MCP_TOKEN = "YOUR_N8N_MCP_TOKEN";

// 建立根代理，使用 Stdio 連線參數
const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "n8n_agent",
    instruction: "幫助使用者管理與執行 n8n 中的工作流",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: [
                    "-y",
                    "supergateway",
                    "--streamableHttp",
                    `${N8N_INSTANCE_URL}/mcp-server/http`,
                    "--header",
                    `authorization:Bearer ${N8N_MCP_TOKEN}`,
                ],
            },
        }),
    ],
});

export { rootAgent };
```

> TypeScript (HTTP)

**Remote MCP Server**
```typescript
import { LlmAgent, MCPToolset } from "@google/adk";

// 設定 n8n 實例網址與 MCP 權杖
const N8N_INSTANCE_URL = "https://localhost:5678";
const N8N_MCP_TOKEN = "YOUR_N8N_MCP_TOKEN";

// 建立根代理，使用 Streamable HTTP 連線參數
const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "n8n_agent",
    instruction: "幫助使用者管理與執行 n8n 中的工作流",
    tools: [
        new MCPToolset({
            type: "StreamableHTTPConnectionParams",
            url: `${N8N_INSTANCE_URL}/mcp-server/http`,
            transportOptions: {
                requestInit: {
                    headers: {
                        Authorization: `Bearer ${N8N_MCP_TOKEN}`,
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

| 工具 | 描述 |
| ---------------------- | ------------------------------------------------------- |
| `search_workflows` | 搜尋可用的工作流 |
| `execute_workflow` | 執行特定的工作流 |
| `get_workflow_details` | 檢索工作流的詮釋資料 (Metadata) 和架構 (Schema) 資訊 |

## 配置

要讓您的代理可以存取工作流，工作流必須符合以下條件：

- **處於啟用狀態 (Be Active)**：工作流必須在 n8n 中被激活。
- **支援的觸發器 (Supported Trigger)**：包含 Webhook、Schedule、Chat 或 Form 觸發器節點。
- **已為 MCP 啟用 (Enabled for MCP)**：您必須在工作流設置中切換「在 MCP 中可用 (Available in MCP)」，或從工作流卡片選單中選擇「啟用 MCP 存取 (Enable MCP access)」。

## 其他資源

- [n8n MCP 伺服器文件](https://docs.n8n.io/advanced-ai/accessing-n8n-mcp-server/)

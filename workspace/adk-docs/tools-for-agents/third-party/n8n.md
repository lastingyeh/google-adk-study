# n8n

> 🔔 `更新日期：2026-01-27`
>
> 🔗 `資料來源：https://google.github.io/adk-docs/tools/third-party/n8n/`

[n8n MCP 伺服器](https://docs.n8n.io/advanced-ai/accessing-n8n-mcp-server/) 將您的 ADK 代理程式連接到 [n8n](https://n8n.io/)，這是一個可擴展的工作流自動化工具。此整合允許您的代理程式安全地連接到 n8n 實例，直接從自然語言介面搜尋、檢查和觸發工作流。

> [!NOTE] 備選方案：工作流級別的 MCP 伺服器
本頁面上的配置指南涵蓋了 **實例級別的 MCP 存取**，它將您的代理程式連接到已啟用工作流的中央樞紐。或者，您可以使用 [MCP 伺服器觸發節點 (MCP Server Trigger node)](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcptrigger/) 讓 **單個工作流** 作為其自己的獨立 MCP 伺服器運行。如果您想構建特定的伺服器行為或公開與單個工作流隔離的工具，此方法非常有用。

## 使用案例

- **執行複雜的工作流**：直接從您的代理程式觸發 n8n 中定義的多步驟業務流程，利用可靠的分支邏輯、迴圈和錯誤處理來確保一致性。

- **連接到外部應用程式**：透過 n8n 存取預建的整合功能，而無需為每個服務編寫自定義工具，從而消除了管理 API 身分驗證、標頭或樣板程式碼的需要。

- **資料處理**：將複雜的資料轉換任務交由 n8n 工作流處理，例如將自然語言轉換為 API 呼叫，或者抓取和總結網頁，利用自定義 Python 或 JavaScript 節點進行精確的資料塑形。

## 先決條件

- 一個啟用的 n8n 實例
- 在設定中啟用了 MCP 存取
- 一個有效的 MCP 存取權杖 (token)

請參閱 [n8n MCP 文件](https://docs.n8n.io/advanced-ai/accessing-n8n-mcp-server/) 以獲取詳細的設置說明。

## 搭配代理程式使用

<details>
<summary>範例程式碼</summary>

> Local MCP Server
```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# 設定 n8n 實例網址與 MCP 存取權杖
N8N_INSTANCE_URL = "https://localhost:5678"
N8N_MCP_TOKEN = "YOUR_N8N_MCP_TOKEN"

# 初始化負責管理與執行 n8n 工作流的代理程式
root_agent = Agent(
    model="gemini-2.5-pro",
    name="n8n_agent",
    instruction="協助使用者管理及執行 n8n 中的工作流",
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

> Remote MCP Server
```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

# 設定 n8n 實例網址與 MCP 存取權杖
N8N_INSTANCE_URL = "https://localhost:5678"
N8N_MCP_TOKEN = "YOUR_N8N_MCP_TOKEN"

# 初始化負責管理與執行 n8n 工作流的代理程式 (使用遠端 MCP 伺服器)
root_agent = Agent(
    model="gemini-2.5-pro",
    name="n8n_agent",
    instruction="協助使用者管理及執行 n8n 中的工作流",
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
</details>


## 可用工具

工具 | 說明
---- | -----------
`search_workflows` | 搜尋可用的工作流
`execute_workflow` | 執行特定的工作流
`get_workflow_details` | 獲取工作流的元數據 (metadata) 與架構 (schema) 資訊

## 配置

若要讓代理程式存取工作流，這些工作流必須符合以下標準：

- **已啟用 (Active)**：工作流必須在 n8n 中被激活。

- **支援的觸發器 (Supported Trigger)**：包含 Webhook、排程 (Schedule)、聊天 (Chat) 或表單 (Form) 觸發節點。

- **已為 MCP 啟用**：您必須在工作流設定中切換「在 MCP 中可用 (Available in MCP)」，或從工作流卡片選單中選擇「啟用 MCP 存取 (Enable MCP access)」。

## 額外資源

- [n8n MCP 伺服器文件](https://docs.n8n.io/advanced-ai/accessing-n8n-mcp-server/)

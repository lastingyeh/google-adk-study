# ADK 的 Asana MCP 工具

> 🔔 `更新日期：2026-03-04`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/asana/

[`ADK 支援`: `Python` | `TypeScript`]

[Asana MCP 伺服器](https://developers.asana.com/docs/using-asanas-mcp-server) 將您的 ADK 代理程式與 [Asana](https://asana.com/) 工作管理平台連接起來。這項整合讓您的代理程式能夠使用自然語言管理專案、任務、目標和團隊協作。

## 使用案例

- **追蹤專案狀態**：獲取專案進度的即時更新，查看狀態報告，並檢索有關里程碑和截止日期的資訊。
- **管理任務**：使用自然語言建立、更新和組織任務。讓您的代理程式處理任務分配、狀態變更和優先級更新。
- **監控目標**：存取並更新 Asana 目標，以追蹤整個組織的團隊目標和關鍵結果。

## 先決條件

- 一個具有工作區存取權限的 [Asana](https://asana.com/) 帳戶

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

# 初始化 Asana 代理程式
root_agent = Agent(
    model="gemini-2.5-pro",
    name="asana_agent",
    instruction="協助使用者在 Asana 中管理專案、任務和目標",
    tools=[
        # 使用 MCP 工具集連接到 Asana MCP 伺服器
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "mcp-remote",
                        "https://mcp.asana.com/sse",
                    ]
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

// 初始化 Asana 代理程式
const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "asana_agent",
    instruction: "協助使用者在 Asana 中管理專案、任務和目標",
    tools: [
        // 使用 MCP 工具集連接到 Asana MCP 伺服器
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: [
                    "-y",
                    "mcp-remote",
                    "https://mcp.asana.com/sse",
                ],
            },
        }),
    ],
});

export { rootAgent };
```

</details>

> [!NOTE]註記
當您第一次執行此代理程式時，系統會自動開啟瀏覽器視窗，以透過 OAuth 要求存取權限。或者，您可以使用控制台列印出的授權 URL。您必須核准此要求，才能允許代理程式存取您的 Asana 資料。

## 可用工具

Asana 的 MCP 伺服器包含 30 多個按類別組織的工具。當您的代理程式連線時，會自動發現工具。執行代理程式後，使用 [ADK Web UI](/adk-docs/runtime/web-interface/) 在追蹤圖中查看可用工具。

| 類別 | 說明 |
| ----------------- | ------------------------------------------- |
| 專案追蹤 | 獲取專案狀態更新和報告 |
| 任務管理 | 建立、更新和組織任務 |
| 使用者資訊 | 存取使用者詳細資訊和指派任務 |
| 目標 | 追蹤並更新 Asana 目標 |
| 團隊組織 | 管理團隊結構和成員資格 |
| 物件搜尋 | 跨 Asana 物件進行快速預測搜尋 |

## 其他資源

- [Asana MCP 伺服器說明文件](https://developers.asana.com/docs/using-asanas-mcp-server)
- [Asana MCP 整合指南](https://developers.asana.com/docs/integrating-with-asanas-mcp-server)

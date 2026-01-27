# Asana

> 🔔 `更新日期：2026-01-27`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/tools/third-party/asana/

[Asana MCP 伺服器](https://developers.asana.com/docs/using-asanas-mcp-server) 將您的 ADK 代理程式與 [Asana](https://asana.com/) 工作管理平台連接起來。此整合讓您的代理程式能夠使用自然語言管理專案、任務、目標和團隊協作。

## 使用案例

- **追蹤專案狀態**：獲取專案進度的即時更新，查看狀態報告，並檢索有關里程碑和截止日期的資訊。

- **管理任務**：使用自然語言建立、更新和組織任務。讓您的代理程式處理任務指派、狀態變更和優先順序更新。

- **監控目標**：存取並更新 Asana 目標，以追蹤整個組織的團隊目標和關鍵結果。

## 前置作業

- 一個具有工作區存取權限的 [Asana](https://asana.com/) 帳戶

## 與代理程式搭配使用

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# 建立 Asana 代理程式
root_agent = Agent(
    model="gemini-2.5-pro",
    name="asana_agent",
    instruction="協助使用者管理 Asana 中的專案、任務和目標",
    tools=[
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

> [!NOTE]
當您第一次執行此代理程式時，系統會自動開啟瀏覽器視窗，要求透過 OAuth 進行存取。或者，您可以使用控制台中顯示的授權 URL。您必須核准此要求，才能允許代理程式存取您的 Asana 資料。

## 可用工具

Asana 的 MCP 伺服器包含 30 多個按類別組織的工具。當您的代理程式連線時，系統會自動發現這些工具。在執行代理程式後，請使用 [ADK Web UI](../../agent-runtime/web-interface.md) 在追蹤圖中查看可用工具。

類別 | 描述
---- | ----
專案追蹤 | 獲取專案狀態更新和報告
任務管理 | 建立、更新和組織任務
使用者資訊 | 存取使用者詳細資訊和指派任務
目標 | 追蹤並更新 Asana 目標
團隊組織 | 管理團隊結構和成員身分
物件搜尋 | 跨 Asana 物件進行快速預測搜尋

## 其他資源

- [Asana MCP 伺服器文件](https://developers.asana.com/docs/using-asanas-mcp-server)
- [Asana MCP 整合指南](https://developers.asana.com/docs/integrating-with-asanas-mcp-server)

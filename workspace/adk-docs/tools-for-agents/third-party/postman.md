# Postman

> 🔔 `更新日期：2026-01-27`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/tools/third-party/postman/

[Postman MCP 伺服器](https://github.com/postmanlabs/postman-mcp-server) 將您的 ADK 代理程式連接到 [Postman](https://www.postman.com/) 生態系統。這種整合讓您的代理程式能夠存取工作空間、管理集合與環境、評估 API，並透過自然語言互動自動化工作流程。

## 使用案例

- **API 測試**：使用您的 Postman 集合持續測試您的 API。

- **集合管理**：建立與標記集合、更新文件、新增評論，或在不離開編輯器的情況下對多個集合執行操作。

- **工作空間與環境管理**：建立工作空間與環境，並管理您的環境變數。

- **客戶端程式碼生成**：根據最佳實踐和專案慣例，生成使用 API 的生產級客戶端程式碼。

## 前提條件

- 建立 [Postman 帳戶](https://identity.getpostman.com/signup)
- 生成 [Postman API 金鑰](https://postman.postman.co/settings/me/api-keys)

## 與代理程式搭配使用

<details>
<summary>範例說明</summary>

> Local MCP Server

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# 設定您的 Postman API 金鑰
POSTMAN_API_KEY = "YOUR_POSTMAN_API_KEY"

# 初始化根代理程式
root_agent = Agent(
    model="gemini-2.5-pro",
    name="postman_agent",
    instruction="幫助使用者管理他們的 Postman 工作空間和集合",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@postman/postman-mcp-server",
                        # "--full",  # 使用所有 100+ 個工具
                        # "--code",  # 使用程式碼生成工具
                        # "--region", "eu",  # 使用歐盟地區
                    ],
                    env={
                        "POSTMAN_API_KEY": POSTMAN_API_KEY,
                    },
                ),
                timeout=30,
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

# 設定您的 Postman API 金鑰
POSTMAN_API_KEY = "YOUR_POSTMAN_API_KEY"

# 初始化根代理程式
root_agent = Agent(
    model="gemini-2.5-pro",
    name="postman_agent",
    instruction="幫助使用者管理他們的 Postman 工作空間和集合",
    tools=[
        McpToolset(
            connection_params=StreamableHTTPServerParams(
                url="https://mcp.postman.com/mcp",
                # (選填) 使用 "/minimal" 僅包含基本工具
                # (選填) 使用 "/code" 包含程式碼生成工具
                # (選填) 使用 "https://mcp.eu.postman.com" 歐盟地區
                headers={
                    "Authorization": f"Bearer {POSTMAN_API_KEY}",
                },
            ),
        )
    ],
)
```

</details>

## 配置

Postman 提供三種工具配置：

- **Minimal** (預設)：基本 Postman 操作的必要工具。最適合對集合、工作空間或環境進行簡單修改。
- **Full**：所有可用的 Postman API 工具（100+ 個工具）。適合進階協作和企業功能。
- **Code**：用於搜尋 API 定義和生成客戶端程式碼的工具。非常適合需要使用 API 的開發人員。

選擇配置：

- **本機伺服器**：在 `args` 清單中新增 `--full` 或 `--code`。
- **遠端伺服器**：將 URL 路徑更改為 `/minimal`、`/mcp` (full) 或 `/code`。

對於歐盟地區，請使用 `--region eu` (本機) 或 `https://mcp.eu.postman.com` (遠端)。

## 其他資源

- [GitHub 上的 Postman MCP 伺服器](https://github.com/postmanlabs/postman-mcp-server)
- [Postman API 金鑰設定](https://postman.postman.co/settings/me/api-keys)
- [Postman 學習中心](https://learning.postman.com/)

# Mailgun ADK MCP 工具

> 🔔 `更新日期：2026-03-08`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/mailgun/

[`ADK 支援`: `Python` | `TypeScript`]

[Mailgun MCP 伺服器](https://github.com/mailgun/mailgun-mcp-server) 將您的 ADK 代理程式連接到 [Mailgun](https://www.mailgun.com/)，這是一項交易式電子郵件服務。此整合讓您的代理程式具備發送電子郵件、追蹤送達指標、管理網域和範本，以及使用自然語言處理郵寄清單的能力。

## 使用案例

- **發送與管理電子郵件**：撰寫並發送交易式或行銷電子郵件、擷取儲存的訊息，並透過對話指令重新發送訊息。
- **監控送達效能**：獲取送達統計數據、分析退信分類，並審查拒絕往來清單以維護寄件者聲譽。
- **管理電子郵件基礎架構**：驗證網域 DNS 配置、配置追蹤設定、建立電子郵件範本，並設定入站路由規則。

## 先決條件

- 建立 [Mailgun 帳戶](https://www.mailgun.com/)
- 從 [Mailgun 儀表板](https://app.mailgun.com/settings/api_security) 產生 API 金鑰

## 與代理程式配合使用

<details>
<summary>程式碼範例</summary>

> Python

**Local MCP Server**
```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# 您的 Mailgun API 金鑰
MAILGUN_API_KEY = "YOUR_MAILGUN_API_KEY"

# 初始化根代理程式
root_agent = Agent(
    model="gemini-2.5-pro",
    name="mailgun_agent",
    instruction="協助使用者發送電子郵件並管理其 Mailgun 帳戶",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@mailgun/mcp-server",
                    ],
                    env={
                        "MAILGUN_API_KEY": MAILGUN_API_KEY,
                        # "MAILGUN_API_REGION": "eu",  # 選填：預設為 "us"
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

// 您的 Mailgun API 金鑰
const MAILGUN_API_KEY = "YOUR_MAILGUN_API_KEY";

// 初始化根代理程式
const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "mailgun_agent",
    instruction: "協助使用者發送電子郵件並管理其 Mailgun 帳戶",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: ["-y", "@mailgun/mcp-server"],
                env: {
                    MAILGUN_API_KEY: MAILGUN_API_KEY,
                    // MAILGUN_API_REGION: "eu",  // 選填：預設為 "us"
                },
            },
        }),
    ],
});

export { rootAgent };
```

</details>

## 可用工具

### 訊息傳遞 (Messaging)

| 工具 | 說明 |
| -------------------- | ----------------------------------------------------------- |
| `send_email` | 發送支援 HTML 內容和附件的電子郵件 |
| `get_stored_message` | 擷取儲存的電子郵件訊息 |
| `resend_message` | 重新發送先前發送過的訊息 |

### 網域 (Domains)

| 工具 | 說明 |
| -------------------------- | ------------------------------------------------- |
| `get_domain` | 查看特定網域的詳細資訊 |
| `verify_domain` | 驗證網域的 DNS 配置 |
| `get_tracking_settings` | 查看追蹤設定（點擊、開啟、取消訂閱） |
| `update_tracking_settings` | 更新網域的追蹤設定 |

### Webhooks

| 工具 | 說明 |
| ---------------- | ------------------------------------ |
| `list_webhooks` | 列出網域的所有事件 Webhook |
| `create_webhook` | 建立新的事件 Webhook |
| `update_webhook` | 更新現有的 Webhook |
| `delete_webhook` | 刪除 Webhook |

### 路由 (Routes)

| 工具 | 說明 |
| -------------- | -------------------------------- |
| `list_routes` | 查看入站電子郵件路由規則 |
| `update_route` | 更新入站路由規則 |

### 郵寄清單 (Mailing lists)

| 工具 | 說明 |
| --------------------- | ------------------------------------------- |
| `create_mailing_list` | 建立新的郵寄清單 |
| `manage_list_members` | 新增、移除或更新郵寄清單成員 |

### 範本 (Templates)

| 工具 | 說明 |
| -------------------------- | ----------------------------------- |
| `create_template` | 建立新的電子郵件範本 |
| `manage_template_versions` | 建立並管理範本版本 |

### 分析與統計 (Analytics and stats)

| 工具 | 說明 |
| --------------- | ---------------------------------------------------------------------- |
| `query_metrics` | 查詢日期範圍內的發送和使用指標 |
| `get_logs` | 擷取電子郵件事件日誌 |
| `get_stats` | 按網域、標記、提供者、裝置或國家/地區查看聚合統計數據 |

### 排除項目 (Suppressions)

| 工具 | 說明 |
| ------------------ | --------------------------------- |
| `get_bounces` | 查看退信的電子郵件地址 |
| `get_unsubscribes` | 查看已取消訂閱的電子郵件地址 |
| `get_complaints` | 查看投訴記錄 |
| `get_allowlist` | 查看允許清單項目 |

### IP 地址 (IPs)

| 工具 | 說明 |
| -------------- | -------------------------------- |
| `list_ips` | 查看 IP 分配情況 |
| `get_ip_pools` | 查看專用 IP 池配置 |

### 退信分類 (Bounce classification)

| 工具 | 說明 |
| --------------------------- | ---------------------------------------- |
| `get_bounce_classification` | 分析退信類型和送達問題 |

## 配置

| 變數 | 必填 | 預設值 | 說明 |
| -------------------- | -------- | ------- | ------------------------ |
| `MAILGUN_API_KEY` | 是 | — | 您的 Mailgun API 金鑰 |
| `MAILGUN_API_REGION` | 否 | `us` | API 區域：`us` 或 `eu` |

## 其他資源

- [Mailgun MCP 伺服器儲存庫](https://github.com/mailgun/mailgun-mcp-server)
- [Mailgun MCP 整合指南](https://www.mailgun.com/resources/integrations/mcp-server/)
- [Mailgun 說明文件](https://documentation.mailgun.com/)

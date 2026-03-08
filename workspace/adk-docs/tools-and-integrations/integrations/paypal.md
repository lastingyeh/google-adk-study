# ADK 的 PayPal MCP 工具

> 🔔 `更新日期：2026-03-08`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/paypal/

[`ADK 支援`: `Python` | `TypeScript`]

[PayPal MCP 伺服器](https://github.com/paypal/paypal-mcp-server) 將您的 ADK 代理程式與 [PayPal](https://www.paypal.com/) 生態系統連接起來。此整合使您的代理程式能夠使用自然語言管理付款、發票、訂閱和爭議，實現自動化商業工作流程和業務洞察。

## 使用案例

- **簡化財務營運**：直接透過聊天建立訂單、發送發票和處理退款，無需切換上下文。您可以立即指示您的代理程式「向客戶 X 收費」或「退款訂單 Y」。
- **管理訂閱與產品**：透過自然語言建立產品、設定訂閱方案和管理訂閱者詳細資訊，處理循環計費的全生命週期。
- **解決問題與追蹤績效**：總結並接受爭議索賠、追蹤出貨狀態並擷取商家洞察，以便即時做出數據驅動的決策。

## 先決條件

- 建立 [PayPal 開發者帳戶](https://developer.paypal.com/)
- 從 [PayPal 開發者儀表板](https://developer.paypal.com/) 建立應用程式並取得您的憑據
- 根據您的憑據 [產生存取Token (Access Token)](https://developer.paypal.com/reference/get-an-access-token/)

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

# 設定 PayPal 環境與存取Token
PAYPAL_ENVIRONMENT = "SANDBOX"  # 選項："SANDBOX" 或 "PRODUCTION"
PAYPAL_ACCESS_TOKEN = "YOUR_PAYPAL_ACCESS_TOKEN"

root_agent = Agent(
    model="gemini-2.5-pro",
    name="paypal_agent",
    instruction="協助使用者管理其 PayPal 帳戶",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@paypal/mcp",
                        "--tools=all",
                        # (選填) 指定要啟用的工具
                        # "--tools=subscriptionPlans.list,subscriptionPlans.show",
                    ],
                    env={
                        "PAYPAL_ACCESS_TOKEN": PAYPAL_ACCESS_TOKEN,
                        "PAYPAL_ENVIRONMENT": PAYPAL_ENVIRONMENT,
                    }
                ),
                timeout=300,
            ),
        )
    ],
)
```

> Python

**Remote MCP Server**
```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

# 設定 PayPal MCP 端點與存取Token
PAYPAL_MCP_ENDPOINT = "https://mcp.sandbox.paypal.com/sse"  # 生產環境：https://mcp.paypal.com/sse
PAYPAL_ACCESS_TOKEN = "YOUR_PAYPAL_ACCESS_TOKEN"

root_agent = Agent(
    model="gemini-2.5-pro",
    name="paypal_agent",
    instruction="協助使用者管理其 PayPal 帳戶",
    tools=[
        McpToolset(
            connection_params=SseConnectionParams(
                url=PAYPAL_MCP_ENDPOINT,
                headers={
                    "Authorization": f"Bearer {PAYPAL_ACCESS_TOKEN}",
                },
            ),
        )
    ],
)
```

> TypeScript

**Local MCP Server**
```typescript
import { LlmAgent, MCPToolset } from "@google/adk";

// 設定 PayPal 環境與存取Token
const PAYPAL_ENVIRONMENT = "SANDBOX"; // 選項："SANDBOX" 或 "PRODUCTION"
const PAYPAL_ACCESS_TOKEN = "YOUR_PAYPAL_ACCESS_TOKEN";

const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "paypal_agent",
    instruction: "協助使用者管理其 PayPal 帳戶",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: [
                    "-y",
                    "@paypal/mcp",
                    "--tools=all",
                    // (選填) 指定要啟用的工具
                    // "--tools=subscriptionPlans.list,subscriptionPlans.show",
                ],
                env: {
                    PAYPAL_ACCESS_TOKEN: PAYPAL_ACCESS_TOKEN,
                    PAYPAL_ENVIRONMENT: PAYPAL_ENVIRONMENT,
                },
            },
        }),
    ],
});

export { rootAgent };
```

</details>

注意

**Token過期**：PayPal 存取Token的有效期僅為 3-8 小時。如果您的代理程式停止運作，請確保您的Token尚未過期，並在必要時產生新Token。您應該實作Token重新整理邏輯來處理Token過期。

## 可用工具

### 型錄管理

| 工具                   | 描述                                                |
| ---------------------- | --------------------------------------------------- |
| `create_product`       | 在 PayPal 型錄中建立新產品                           |
| `list_products`        | 列出 PayPal 型錄中的產品                            |
| `show_product_details` | 顯示 PayPal 型錄中特定產品的詳細資訊                |
| `update_product`       | 更新 PayPal 型錄中的現有產品                        |

### 爭議管理

| 工具                   | 描述                                                |
| ---------------------- | --------------------------------------------------- |
| `list_disputes`        | 擷取所有爭議的摘要，可進行選用篩選                  |
| `get_dispute`          | 擷取特定爭議的詳細資訊                              |
| `accept_dispute_claim` | 接受爭議索賠，解決結果有利於買家                    |

### 發票

| 工具                       | 描述                                         |
| -------------------------- | -------------------------------------------- |
| `create_invoice`           | 在 PayPal 系統中建立新發票                   |
| `list_invoices`            | 列出發票                                     |
| `get_invoice`              | 擷取特定發票的詳細資訊                       |
| `send_invoice`             | 將現有發票發送給指定的收件人                 |
| `send_invoice_reminder`    | 為現有發票發送提醒                           |
| `cancel_sent_invoice`      | 取消已發送的發票                             |
| `generate_invoice_qr_code` | 為發票產生 QR code                          |

### 付款

| 工具            | 描述                                                        |
| --------------- | ----------------------------------------------------------- |
| `create_order`  | 根據提供的詳細資訊在 PayPal 系統中建立訂單                  |
| `create_refund` | 為已扣款的付款處理退款                                      |
| `get_order`     | 取得特定付款的詳細資訊                                      |
| `get_refund`    | 取得特定退款的詳細資訊                                      |
| `pay_order`     | 為已授權的訂單扣款                                          |

### 報告與洞察

| 工具                    | 描述                                                         |
| ----------------------- | ------------------------------------------------------------ |
| `get_merchant_insights` | 擷取商家的商業智慧指標和分析                                 |
| `list_transactions`     | 列出所有交易                                                 |

### 出貨追蹤

| 工具                       | 描述                                                   |
| -------------------------- | ------------------------------------------------------ |
| `create_shipment_tracking` | 為 PayPal 交易建立出貨追蹤資訊                        |
| `get_shipment_tracking`    | 取得特定貨件的出貨追蹤資訊                            |
| `update_shipment_tracking` | 更新特定貨件的出貨追蹤資訊                            |

### 訂閱管理

| 工具                             | 描述                                  |
| -------------------------------- | ------------------------------------- |
| `cancel_subscription`            | 取消有效的訂閱                        |
| `create_subscription`            | 建立新訂閱                            |
| `create_subscription_plan`       | 建立新訂閱方案                        |
| `update_subscription`            | 更新現有訂閱                          |
| `list_subscription_plans`        | 列出訂閱方案                          |
| `show_subscription_details`      | 顯示特定訂閱的詳細資訊                |
| `show_subscription_plan_details` | 顯示特定訂閱方案的詳細資訊            |

## 設定

您可以使用 `--tools` 命令列參數來控制啟用哪些工具。這對於限制代理程式的權限範圍非常有用。

您可以使用 `--tools=all` 啟用所有工具，或指定以逗號分隔的特定工具識別碼列表。

**注意**：下方的設定識別碼使用點號標記法（例如 `invoices.create`），這與向代理程式公開的工具名稱（例如 `create_invoice`）不同。

**產品**：`products.create`, `products.list`, `products.update`, `products.show`

**爭議**：`disputes.list`, `disputes.get`, `disputes.create`

**發票**：`invoices.create`, `invoices.list`, `invoices.get`, `invoices.send`, `invoices.sendReminder`, `invoices.cancel`, `invoices.generateQRC`

**訂單與付款**：`orders.create`, `orders.get`, `orders.capture`, `payments.createRefund`, `payments.getRefunds`

**交易**：`transactions.list`

**出貨**：`shipment.create`, `shipment.get`

**訂閱**：`subscriptionPlans.create`, `subscriptionPlans.list`, `subscriptionPlans.show`, `subscriptions.create`, `subscriptions.show`, `subscriptions.cancel`

## 額外資源

- [PayPal MCP 伺服器文件](https://docs.paypal.ai/developer/tools/ai/mcp-quickstart)
- [PayPal MCP 伺服器儲存庫](https://github.com/paypal/paypal-mcp-server)
- [PayPal 代理程式工具參考](https://docs.paypal.ai/developer/tools/ai/agent-tools-ref)

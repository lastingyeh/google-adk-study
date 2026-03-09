# Stripe ADK MCP 工具

> 🔔 `更新日期：2026-03-09`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/stripe/

[`ADK 支援`: `Python` | `TypeScript`]

[Stripe MCP 伺服器](https://docs.stripe.com/mcp) 將您的 ADK 代理連接到 [Stripe](https://stripe.com/) 生態系統。此整合使您的代理能夠使用自然語言管理付款、客戶、訂閱和發票，從而實現自動化的商業工作流和財務營運。

## 使用場景

- **自動化付款營運**：透過對話式命令建立付款連結、處理退款並列出付款意向。
- **簡化發票處理**：在不離開開發環境的情況下產生並完成發票、新增明細項目並追蹤未付帳款。
- **獲取業務洞察**：查詢帳戶餘額、列出產品和價格，並在 Stripe 資源中進行搜尋以做出數據驅動的決策。

## 前置作業

- 建立一個 [Stripe 帳戶](https://dashboard.stripe.com/register)
- 從 Stripe 儀表板產生一個 [受限 API 金鑰 (Restricted API key)](https://dashboard.stripe.com/apikeys)

## 在代理中使用

<details>
<summary>範例說明</summary>

> Python

**Local MCP Server**
```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# 設定您的 Stripe 秘密金鑰
STRIPE_SECRET_KEY = "YOUR_STRIPE_SECRET_KEY"

# 初始化根代理
root_agent = Agent(
    model="gemini-2.5-pro",
    name="stripe_agent",
    instruction="幫助使用者管理他們的 Stripe 帳戶",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@stripe/mcp",
                        "--tools=all",
                        # (選填) 指定要啟用的工具
                        # "--tools=customers.read,invoices.read,products.read",
                    ],
                    env={
                        "STRIPE_SECRET_KEY": STRIPE_SECRET_KEY,
                    }
                ),
                timeout=30,
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
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

# 設定您的 Stripe 秘密金鑰
STRIPE_SECRET_KEY = "YOUR_STRIPE_SECRET_KEY"

# 使用可串流的 HTTP 連接初始化代理
root_agent = Agent(
    model="gemini-2.5-pro",
    name="stripe_agent",
    instruction="幫助使用者管理他們的 Stripe 帳戶",
    tools=[
        McpToolset(
            connection_params=StreamableHTTPServerParams(
                url="https://mcp.stripe.com",
                headers={
                    "Authorization": f"Bearer {STRIPE_SECRET_KEY}",
                },
            ),
        )
    ],
)
```

> typescript

**Local MCP Server**
```typescript
import { LlmAgent, MCPToolset } from "@google/adk";

// 設定您的 Stripe 秘密金鑰
const STRIPE_SECRET_KEY = "YOUR_STRIPE_SECRET_KEY";

// 建立根代理
const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "stripe_agent",
    instruction: "幫助使用者管理他們的 Stripe 帳戶",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: [
                    "-y",
                    "@stripe/mcp",
                    "--tools=all",
                    // (選填) 指定要啟用的工具
                    // "--tools=customers.read,invoices.read,products.read",
                ],
                env: {
                    STRIPE_SECRET_KEY: STRIPE_SECRET_KEY,
                },
            },
        }),
    ],
});

export { rootAgent };
```

> typescript

**Remote MCP Server**
```typescript
import { LlmAgent, MCPToolset } from "@google/adk";

// 設定您的 Stripe 秘密金鑰
const STRIPE_SECRET_KEY = "YOUR_STRIPE_SECRET_KEY";

// 使用可串流的 HTTP 連接建立根代理
const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "stripe_agent",
    instruction: "幫助使用者管理他們的 Stripe 帳戶",
    tools: [
        new MCPToolset({
            type: "StreamableHTTPConnectionParams",
            url: "https://mcp.stripe.com",
            transportOptions: {
                requestInit: {
                    headers: {
                        Authorization: `Bearer ${STRIPE_SECRET_KEY}`,
                    },
                },
            },
        }),
    ],
});

export { rootAgent };
```
</details>


> [!TIP]最佳實踐
啟用工具操作的人員確認，並在與其他 MCP 伺服器同時使用 Stripe MCP 伺服器時保持謹慎，以降低提示注入 (prompt injection) 的風險。

## 可用工具

| 資源          | 工具                          | API                     |
| ------------- | ----------------------------- | ----------------------- |
| 帳戶 (Account) | `get_stripe_account_info`     | 取得帳戶資訊            |
| 餘額 (Balance) | `retrieve_balance`            | 查詢餘額                |
| 優惠券 (Coupon) | `create_coupon`               | 建立優惠券              |
| 優惠券 (Coupon) | `list_coupons`                | 列出優惠券              |
| 客戶 (Customer) | `create_customer`             | 建立客戶                |
| 客戶 (Customer) | `list_customers`              | 列出客戶                |
| 爭議 (Dispute) | `list_disputes`               | 列出爭議                |
| 爭議 (Dispute) | `update_dispute`              | 更新爭議                |
| 發票 (Invoice) | `create_invoice`              | 建立發票                |
| 發票 (Invoice) | `create_invoice_item`         | 建立發票項目            |
| 發票 (Invoice) | `finalize_invoice`            | 完成發票                |
| 發票 (Invoice) | `list_invoices`               | 列出發票                |
| 付款連結 (Payment Link) | `create_payment_link`         | 建立付款連結            |
| 付款意向 (PaymentIntent) | `list_payment_intents`        | 列出付款意向 (PaymentIntents) |
| 價格 (Price)   | `create_price`                | 建立價格                |
| 價格 (Price)   | `list_prices`                 | 列出價格                |
| 產品 (Product) | `create_product`              | 建立產品                |
| 產品 (Product) | `list_products`               | 列出產品                |
| 退款 (Refund)  | `create_refund`               | 建立退款                |
| 訂閱 (Subscription) | `cancel_subscription`         | 取消訂閱                |
| 訂閱 (Subscription) | `list_subscriptions`          | 列出訂閱                |
| 訂閱 (Subscription) | `update_subscription`         | 更新訂閱                |
| 其他 (Others)  | `search_stripe_resources`     | 搜尋 Stripe 資源        |
| 其他 (Others)  | `fetch_stripe_resources`      | 擷取 Stripe 物件        |
| 其他 (Others)  | `search_stripe_documentation` | 搜尋 Stripe 知識庫      |

## 延伸資源

- [Stripe MCP 伺服器文件](https://docs.stripe.com/mcp)
- [GitHub 上的 Stripe MCP 伺服器](https://github.com/stripe/ai/tree/main/tools/modelcontextprotocol)
- [使用 LLM 在 Stripe 上開發](https://docs.stripe.com/building-with-llms)
- [將 Stripe 加入您的代理工作流](https://docs.stripe.com/agents)

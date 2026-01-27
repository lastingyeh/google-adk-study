# Stripe

> 🔔 `更新日期：2026-01-27`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/tools/third-party/stripe/

[Stripe MCP 伺服器](https://docs.stripe.com/mcp) 將您的 ADK 代理程式連接到 [Stripe](https://stripe.com/) 生態系統。此整合使您的代理程式能夠使用自然語言管理付款、客戶、訂閱和發票，從而實現自動化的商業工作流程和金融操作。

## 使用案例

- **自動化付款操作**：透過對話式指令建立付款連結、處理退款並列出付款意圖。

- **簡化發票流程**：無需離開開發環境即可產生並完成發票、新增明細項目並追蹤未付帳款。

- **獲取業務洞察**：查詢帳戶餘額、列出產品和價格，並在 Stripe 資源中進行搜尋以做出數據驅動的決策。

## 前置作業

- 建立 [Stripe 帳戶](https://dashboard.stripe.com/register)
- 從 Stripe 管理後台產生 [受限 API 金鑰 (Restricted API key)](https://dashboard.stripe.com/apikeys)

## 搭配代理程式使用

<details>
<summary>範例說明</summary>

> Local MCP Server

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# 設定您的 Stripe 私密金鑰
STRIPE_SECRET_KEY = "YOUR_STRIPE_SECRET_KEY"

# 初始化根代理程式
root_agent = Agent(
    model="gemini-2.5-pro",
    name="stripe_agent",
    instruction="協助使用者管理他們的 Stripe 帳戶",
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
                # 設定逾時時間（秒）
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

# 設定您的 Stripe 私密金鑰
STRIPE_SECRET_KEY = "YOUR_STRIPE_SECRET_KEY"

# 初始化根代理程式並連接至遠端 MCP 伺服器
root_agent = Agent(
    model="gemini-2.5-pro",
    name="stripe_agent",
    instruction="協助使用者管理他們的 Stripe 帳戶",
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

</details>

> [!TIP] 最佳實務
啟用工具操作的人員確認功能，並在與其他 MCP 伺服器同時使用 Stripe MCP 伺服器時保持謹慎，以降低提示注入 (prompt injection) 的風險。

## 可用工具

資源 | 工具 | API
-------- | ---- | ----
帳戶 | `get_stripe_account_info` | 擷取帳戶資訊
餘額 | `retrieve_balance` | 擷取餘額
優惠券 | `create_coupon` | 建立優惠券
優惠券 | `list_coupons` | 列出優惠券
客戶 | `create_customer` | 建立客戶
客戶 | `list_customers` | 列出客戶
爭議 | `list_disputes` | 列出爭議
爭議 | `update_dispute` | 更新爭議
發票 | `create_invoice` | 建立發票
發票 | `create_invoice_item` | 建立發票項目
發票 | `finalize_invoice` | 完成發票
發票 | `list_invoices` | 列出發票
付款連結 | `create_payment_link` | 建立付款連結
付款意圖 | `list_payment_intents` | 列出 PaymentIntents
價格 | `create_price` | 建立價格
價格 | `list_prices` | 列出價格
產品 | `create_product` | 建立產品
產品 | `list_products` | 列出產品
退款 | `create_refund` | 建立退款
訂閱 | `cancel_subscription` | 取消訂閱
訂閱 | `list_subscriptions` | 列出訂閱
訂閱 | `update_subscription` | 更新訂閱
其他 | `search_stripe_resources` | 搜尋 Stripe 資源
其他 | `fetch_stripe_resources` | 擷取 Stripe 物件
其他 | `search_stripe_documentation` | 搜尋 Stripe 知識庫

## 其他資源

- [Stripe MCP 伺服器文件](https://docs.stripe.com/mcp)
- [GitHub 上的 Stripe MCP 伺服器](https://github.com/stripe/ai/tree/main/tools/modelcontextprotocol)
- [使用 LLM 在 Stripe 上開發](https://docs.stripe.com/building-with-llms)
- [將 Stripe 加入您的代理工作流程](https://docs.stripe.com/agents)

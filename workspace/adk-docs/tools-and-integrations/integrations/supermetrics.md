# Supermetrics MCP ADK 工具

> 🔔 `更新日期：2026-03-09`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/supermetrics/

[`ADK 支援`: `Python` | `TypeScript`]

[Supermetrics MCP 伺服器](https://mcp.supermetrics.com) 將您的 ADK 代理程式連接到 [Supermetrics](https://supermetrics.com/) 平台，使其能夠存取超過 100 個來源的行銷數據，包括 Google Ads、Meta Ads、LinkedIn Ads 和 Google Analytics 4。您的代理程式可以使用自然語言發現數據源、探索可用指標，並針對已連接的帳戶執行查詢。

## 使用場景

- **行銷成效報表**：查詢各個廣告活動和時間段的曝光次數、點擊次數、花費和轉換次數。建立自動化報表，在單一回應中彙總來自多個平台的數據。
- **跨平台分析**：並排比較 Google Ads、Meta Ads、LinkedIn Ads 和其他管道的成效，無論底層平台為何，皆使用一致的查詢介面。
- **廣告活動監控**：檢索活動中廣告活動和廣告帳戶的最新指標，使代理程式能夠發現異常、追蹤進度或總結每日成效。
- **數據探索**：在建立查詢之前，發現特定使用者可用的數據源、帳戶和欄位，以便代理程式能夠根據每個使用者連接的整合動態調整。

## 先決條件

- 建立 [Supermetrics 帳戶](https://supermetrics.com/)（首次登入時會自動建立 14 天免費試用）
- 從 [Supermetrics Hub](https://hub.supermetrics.com/) 產生 API 金鑰

## 搭配代理程式使用

<details>
<summary>範例說明</summary>

> Python

**Remote MCP Server**
```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

# 您的 Supermetrics API 金鑰
SUPERMETRICS_API_KEY = "YOUR_SUPERMETRICS_API_KEY"

# 初始化根代理程式
root_agent = Agent(
    model="gemini-2.5-pro",
    name="supermetrics_agent",
    # 指令：協助使用者查詢與分析來自 Supermetrics 的行銷數據
    instruction="Help users query and analyze their marketing data from Supermetrics",
    tools=[
        # 設定 MCP 工具集
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://mcp.supermetrics.com/mcp",
                headers={
                    "Authorization": f"Bearer {SUPERMETRICS_API_KEY}",
                },
            ),
        )
    ],
)
```

> TypeScript

**Remote MCP Server**
```typescript
import { LlmAgent, MCPToolset } from "@google/adk";

// 您的 Supermetrics API 金鑰
const SUPERMETRICS_API_KEY = "YOUR_SUPERMETRICS_API_KEY";

// 初始化根代理程式
const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "supermetrics_agent",
    // 指令：協助使用者查詢與分析來自 Supermetrics 的行銷數據
    instruction: "Help users query and analyze their marketing data from Supermetrics",
    tools: [
        new MCPToolset({
            type: "StreamableHTTPConnectionParams",
            url: "https://mcp.supermetrics.com/mcp",
            transportOptions: {
                requestInit: {
                    headers: {
                        Authorization: `Bearer ${SUPERMETRICS_API_KEY}`,
                    },
                },
            },
        }),
    ],
});

export { rootAgent };
```

</details>

> [!TIP]查詢工作流
數據檢索遵循多步驟工作流：根據使用者請求，首先使用 `get_today` 獲取當前日期。接著使用 `data_source_discovery` 發現數據源，使用 `accounts_discovery` 尋找已連接的帳戶，使用 `field_discovery` 檢查可用欄位，使用 `data_query` 提交查詢；然後使用返回的 `schedule_id` 輪詢 `get_async_query_results` 直到結果就緒。

## 可用工具

| 工具 | 描述 |
| ------------------------- | -------------------------------------------------------------------------------- |
| `data_source_discovery`   | 列出可用的行銷數據源（Google Ads、Meta Ads 等）及其 ID |
| `accounts_discovery`      | 發現特定數據源的已連接帳戶 |
| `field_discovery`         | 探索數據源的可用指標和維度 |
| `data_query`              | 提交數據查詢；返回用於非同步結果檢索的 `schedule_id` |
| `get_async_query_results` | 根據 `schedule_id` 輪詢並檢索已提交查詢的結果 |
| `user_info`               | 檢索已驗證使用者的個人資料、團隊資訊和授權狀態 |
| `get_today`               | 獲取適合查詢日期範圍參數格式的當前日期 |

## 其他資源

- [Supermetrics Hub](https://hub.supermetrics.com/)
- [Supermetrics 知識庫](https://docs.supermetrics.com/)
- [數據源文件](https://docs.supermetrics.com/docs/connect)
- [OpenAPI 規範](https://mcp.supermetrics.com/openapi.json)

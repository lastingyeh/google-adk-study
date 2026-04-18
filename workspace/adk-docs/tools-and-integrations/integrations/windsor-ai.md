# Windsor.ai 的 ADK MCP 工具

> 🔔 `更新日期：2026-03-09`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/windsor-ai/

[`ADK 支援`: `Python` | `TypeScript`]

[Windsor MCP 伺服器](https://github.com/windsor-ai/windsor_mcp) 將您的 ADK 代理程式連接到 [Windsor.ai](https://windsor.ai/)，這是一個數據整合平台，統一了來自 325 個以上來源的行銷、銷售和客戶數據。此整合使您的代理程式能夠使用自然語言查詢和分析跨渠道業務數據，而無需編寫 SQL 或自定義腳本。

## 使用案例

- **行銷績效分析**：分析跨渠道（如 Facebook 廣告、Google 廣告、TikTok 廣告等）的活動績效。提出如「上個月哪些活動的廣告支出回報率 (ROAS) 最好？」等問題並獲得即時洞察。
- **跨渠道報告**：生成結合來自 GA4、Shopify、Salesforce 和 HubSpot 等多個平台數據的全面報告，以獲得業務績效的統一視圖。
- **預算優化**：識別表現不佳的活動，檢測預算效率低下的問題，並獲得 AI 驅動的廣告渠道支出分配建議。

## 先決條件

- 一個已連接數據源的 [Windsor.ai](https://windsor.ai/) 帳號
- 一個 Windsor.ai API 金鑰（從 [onboard.windsor.ai](https://onboard.windsor.ai) 取得）

## 與代理程式搭配使用

<details>
<summary>範例說明</summary>

> Python

**Remote MCP Server**
```python
import os
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

# MCP 架構中的遞迴 $ref 所需 (https://github.com/google/adk-python/issues/3870)
os.environ["ADK_ENABLE_JSON_SCHEMA_FOR_FUNC_DECL"] = "1"

WINDSOR_API_KEY = "YOUR_WINDSOR_API_KEY"

# 初始化 Windsor 代理程式
root_agent = Agent(
    model="gemini-2.5-pro",
    name="windsor_agent",
    instruction="協助使用者分析其行銷和業務數據。",
    tools=[
        McpToolset(
            connection_params=StreamableHTTPServerParams(
                url="https://mcp.windsor.ai",
                headers={
                    "Authorization": f"Bearer {WINDSOR_API_KEY}",
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

const WINDSOR_API_KEY = "YOUR_WINDSOR_API_KEY";

// 初始化 Windsor 代理程式
const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "windsor_agent",
    instruction: "協助使用者分析其行銷和業務數據。",
    tools: [
        new MCPToolset({
            type: "StreamableHTTPConnectionParams",
            url: "https://mcp.windsor.ai",
            transportOptions: {
                requestInit: {
                    headers: {
                        Authorization: `Bearer {WINDSOR_API_KEY}`,
                    },
                },
            },
        }),
    ],
});

export { rootAgent };
```

</details>

## 能力

Windsor MCP 為您的整合業務數據提供自然語言介面。它不是公開離散的工具，而是解釋您的問題並從連接的數據源返回結構化洞察。

| 能力 | 描述 |
| -------------------- | ------------------------------------------------------------------ |
| 數據查詢 | 查詢來自 325 個以上連接平台的標準化數據 |
| 績效分析 | 分析關鍵績效指標 (KPI)、趨勢和跨渠道的活動指標 |
| 報告生成 | 建立行銷儀表板和跨渠道績效報告 |
| 預算分析 | 識別支出效率低下的問題並獲得優化建議 |
| 異常檢測 | 檢測績效數據中的離群值和不尋常模式 |

## 支援的數據源

Windsor.ai 連接到 325 個以上的平台，包括：

- **廣告**：Facebook Ads, Google Ads, TikTok Ads, LinkedIn Ads, Microsoft Ads
- **分析**：Google Analytics 4, Adobe Analytics
- **CRM**：Salesforce, HubSpot
- **電子商務**：Shopify
- **更多**：請參閱 Windsor.ai 網站上的[完整連接器清單](https://windsor.ai/)

## 其他資源

- [Windsor MCP 伺服器儲存庫](https://github.com/windsor-ai/windsor_mcp)
- [Windsor.ai 文件](https://windsor.ai/documentation/windsor-mcp/)
- [Windsor MCP 簡介](https://windsor.ai/introducing-windsor-mcp/)
- [Windsor MCP 使用案例與範例](https://windsor.ai/how-to-use-windsor-mcp-examples-use-cases/)

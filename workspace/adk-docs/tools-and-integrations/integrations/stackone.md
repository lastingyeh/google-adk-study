# StackOne ADK 外掛程式

> 🔔 `更新日期：2026-03-09`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/stackone/

[`ADK 支援`: `Python`]

[StackOne ADK 外掛程式](https://github.com/StackOneHQ/stackone-adk-plugin) 透過 [StackOne](https://stackone.com) 的統一 AI 整合網關，將您的 ADK 代理程式與數百個供應商連結。此外掛程式無需為每個 API 手動定義工具函數，而是從您已連結的供應商中動態探索可用工具，並將其作為 ADK 的原生工具公開。它支援人力資源資訊系統 (HRIS)、應徵者追蹤系統 (ATS)、客戶關係管理 (CRM)、生產力和排程工具等許多[整合項目](https://www.stackone.com/connectors)。

## 使用案例

- **銷售與營收營運**：建立代理程式在您的 CRM（例如 HubSpot、Salesforce）中尋找潛在客戶、豐富聯絡人數據、撰寫個人化推廣內容並記錄回報活動 —— 且這一切都在一次對話中完成。
- **人事營運**：建立代理程式在您的 ATS（例如 Greenhouse、Ashby）中篩選候選人、在您的行事曆工具（例如 Google Calendar、Calendly）中檢查可用性、收集面試評分表、將申請人推送到各個階段，並自動將入職資訊同步到您的 HRIS（例如 BambooHR、Workday）—— 無需手動干預即可覆蓋完整的員工生命週期。
- **行銷自動化**：建立行銷代理程式，將您的 CRM 受眾分眾同步到您的電子郵件平台（例如 Mailchimp、Klaviyo）、觸發電子郵件序列，並跨管道報告參與指標。
- **產品交付**：建立代理程式來分類來自您的支援工具（例如 Intercom、Zendesk、Slack）的傳入回饋、在您的專案管理工具（例如 Linear、Jira）中劃分優先順序並建立問題，並使用來自可觀測性平台（例如 PagerDuty、Datadog）的洞察來解決事件 —— 將產品研究、交付和可靠性整合在單一工作流中。

## 前置作業

- 具有至少一個已連結供應商的 [StackOne 帳戶](https://app.stackone.com)
- 來自 [StackOne 控制台](https://app.stackone.com) 的 StackOne API 金鑰
- [Gemini API 金鑰](https://aistudio.google.com/apikey)

## 安裝

```bash
# 使用 pip 安裝 stackone-adk
pip install stackone-adk
```

或使用 uv：

```bash
# 使用 uv 新增 stackone-adk
uv add stackone-adk
```

## 配合代理程式使用

> [!TIP]環境變數
> 在執行以下範例之前，請將您的 API 金鑰設置為環境變數：
>   ```bash
>   # 設置 StackOne 與 Google API 金鑰
>   export STACKONE_API_KEY="your-stackone-api-key"
>   export GOOGLE_API_KEY="your-google-api-key"
>   ```
> 一旦設置了 `STACKONE_API_KEY`，外掛程式將自動讀取它並探索您已連結的帳戶。

<details>
<summary>範例說明</summary>

> Python

** App (建議方式)**
```python
import asyncio

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from stackone_adk import StackOnePlugin


async def main():
    # 初始化 StackOne 外掛程式
    plugin = StackOnePlugin()
    # 或者針對特定帳戶：
    # plugin = StackOnePlugin(account_id="YOUR_ACCOUNT_ID")

    # 獲取發現的工具
    tools = plugin.get_tools()
    print(f"Discovered {len(tools)} tools")

    # 建立代理程式
    agent = Agent(
        model="gemini-2.5-flash",
        name="scheduling_agent",
        description="透過 StackOne 管理排程、HR 和 CRM。",
        instruction=(
            "你是一個由 StackOne 提供支援的得力助手。"
            "你透過使用可用工具來幫助用戶管理他們的排程、HR 和 CRM 任務。\n\n"
            "始終保持樂於助人並提供清晰、有條理的回覆。"
        ),
        tools=tools,
    )

    # 建立應用程式並加入外掛程式
    app = App(
        name="scheduling_app",
        root_agent=agent,
        plugins=[plugin],
    )

    # 使用 InMemoryRunner 執行代理程式
    async with InMemoryRunner(app=app) as runner:
        events = await runner.run_debug(
            "從 Calendly 獲取我最近排定的會議。",
            quiet=True,
        )
        # 提取代理程式最終的文字回覆
        for event in reversed(events):
            if event.content and event.content.parts:
                text_parts = [p.text for p in event.content.parts if p.text]
                if text_parts:
                    print("".join(text_parts))
                    break


# 執行非同步主函數
asyncio.run(main())
```

> Python

** Runner（直接使用外掛程式）**
```python
import asyncio

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from stackone_adk import StackOnePlugin


async def main():
    # 初始化外掛程式
    plugin = StackOnePlugin()
    # 或者針對特定帳戶：
    # plugin = StackOnePlugin(account_id="YOUR_ACCOUNT_ID")

    # 獲取工具列表
    tools = plugin.get_tools()
    print(f"Discovered {len(tools)} tools")

    # 設定代理程式
    agent = Agent(
        model="gemini-2.5-flash",
        name="scheduling_agent",
        description="透過 StackOne 管理排程、HR 和 CRM。",
        instruction=(
            "你是一個由 StackOne 提供支援的得力助手。"
            "你透過使用可用工具來幫助用戶管理他們的排程、HR 和 CRM 任務。\n\n"
            "始終保持樂於助人並提供清晰、有條理的回覆。"
        ),
        tools=tools,
    )

    # 直接使用 InMemoryRunner 運行
    async with InMemoryRunner(
        app_name="scheduling_app", agent=agent
    ) as runner:
        events = await runner.run_debug(
            "從 Calendly 獲取我最近排定的會議。",
            quiet=True,
        )
        # 提取最終文字回覆
        for event in reversed(events):
            if event.content and event.content.parts:
                text_parts = [p.text for p in event.content.parts if p.text]
                if text_parts:
                    print("".join(text_parts))
                    break


# 執行
asyncio.run(main())
```

</details>

## 可用工具

與具有固定工具集的整合不同，StackOne 工具是透過 StackOne API 從您已連結的供應商中**動態探索**的。可用工具取決於您在 [StackOne 控制台](https://app.stackone.com) 中連結了哪些 SaaS 供應商。

列出已探索的工具：

```python
# 初始化外掛程式（可選：省略以使用所有已連結帳戶）
plugin = StackOnePlugin(account_id="YOUR_ACCOUNT_ID")
# 遍歷並打印工具名稱與描述
for tool in plugin.get_tools():
    print(f"{tool.name}: {tool.description}")
```

### 支援的整合類別

| 類別 | 範例供應商 |
| ------------------- | --------------------------------------------------------------- |
| HRIS | HiBob, BambooHR, Workday, SAP SuccessFactors, Personio, Gusto |
| ATS | Greenhouse, Ashby, Lever, Bullhorn, SmartRecruiters, Teamtailor |
| CRM 與銷售 | Salesforce, HubSpot, Pipedrive, Zoho CRM, Close, Copper |
| 行銷 | Mailchimp, Klaviyo, ActiveCampaign, Brevo, GetResponse |
| 工單與支援 | Zendesk, Freshdesk, Jira, ServiceNow, PagerDuty, Linear |
| 生產力 | Asana, ClickUp, Slack, Microsoft Teams, Notion, Confluence |
| 排程 | Calendly, Cal.com |
| LMS 與學習 | 360Learning, Docebo, Go1, Cornerstone, LinkedIn Learning |
| 商務 | Shopify, BigCommerce, WooCommerce, Etsy |
| 開發者工具 | GitHub, GitLab, Twilio |

如需超過 200 個受支援供應商的完整列表，請訪問 [StackOne 整合頁面](https://www.stackone.com/connectors)。

## 配置

### 外掛程式參數

| 參數 | 類型 | 預設值 | 描述 |
| ------------- | ----------- | ------------------- | -------------------------- |
| `api_key` | str | None | `None` |
| `account_id` | str | None | `None` |
| `base_url` | str | None | `None` |
| `plugin_name` | `str` | `"stackone_plugin"` | ADK 的外掛程式識別碼。 |
| `providers` | list[str] | None | `None` |
| `actions` | list[str] | None | `None` |
| `account_ids` | list[str] | None | `None` |

### 工具過濾

按供應商、動作模式、帳戶 ID 或任何組合過濾工具：

```python
# 指定帳戶
plugin = StackOnePlugin(account_ids=["acct-hibob-1", "acct-bamboohr-1"])

# 唯讀操作
plugin = StackOnePlugin(actions=["*_list_*", "*_get_*"])

# 使用萬用字元過濾特定動作
plugin = StackOnePlugin(actions=["calendly_list_events", "calendly_get_event_*"])

# 組合過濾器
plugin = StackOnePlugin(
    actions=["*_list_*", "*_get_*"],
    account_ids=["acct-hibob-1"],
)
```

## 其他資源

- [StackOne ADK 外掛程式儲存庫](https://github.com/StackOneHQ/stackone-adk-plugin)
- [StackOne 文件](https://docs.stackone.com/)
- [StackOne 控制台](https://app.stackone.com)
- [StackOne Python AI SDK](https://github.com/StackOneHQ/stackone-ai-python)

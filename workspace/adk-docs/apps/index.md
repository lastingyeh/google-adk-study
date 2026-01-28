# Apps：工作流程管理類別

🔔 `更新日期：2026-01-18`

[`ADK 支援`: `Python v1.14.0`]

***App*** 類別是一個頂層容器，用於整個 Agent Development Kit (ADK) 代理工作流程。它旨在管理以 ***root agent***（根代理）為分組的代理集合的生命週期、配置和狀態。**App** 類別將代理工作流程的整體運作基礎設施的關注點，與個別代理的任務導向推理分開。

在您的 ADK 工作流程中定義 ***App*** 物件是可選的，這會改變您組織代理程式碼和執行代理的方式。從實務角度來看，您使用 ***App*** 類別來為您的代理工作流程配置以下功能：


*   [**情境快取**](../context/caching.md)

*   [**情境壓縮**](../context/compaction.md)

*   [**代理恢復**](../agent-runtime/resume.md)

*   [**外掛程式**](../plugins/index.md)

本指南說明如何使用 App 類別來配置和管理您的 ADK 代理工作流程。

## App 類別的用途

***App*** 類別解決了建構複雜代理系統時出現的幾個架構問題：

*   **集中式配置：** 提供單一、集中的位置來管理共用資源（如 API 金鑰和資料庫客戶端），避免需要將配置向下傳遞給每個代理。

*   **生命週期管理：** ***App*** 類別包含 ***啟動時 (on startup)*** 和 ***關閉時 (on shutdown)*** 掛鉤，允許可靠地管理需要在多次調用中存在的持久性資源，例如資料庫連線池或記憶體快取。

*   **狀態範圍：** 它定義了帶有 `app:*` 前綴的應用程式級狀態的明確邊界，使開發人員清楚此狀態的範圍和生命週期。

*   **部署單元：** ***App*** 概念建立了一個正式的 *可部署單元*，簡化了代理應用程式的版本控制、測試和服務。

## 定義 App 物件

***App*** 類別用作代理工作流程的主要容器，並包含專案的根代理 (root agent)。***root agent*** 是主要控制器代理和任何其他子代理的容器。

### 使用根代理定義應用程式

透過從 ***Agent*** 基類別建立子類別來為您的工作流程建立 ***root agent***。然後定義一個 ***App*** 物件，並使用 ***root agent*** 物件和可選功能對其進行配置，如下方程式碼範例所示：

`agent.py` 檔案中的範例程式碼：
```python title="agent.py"
from google.adk.agents.llm_agent import Agent
from google.adk.apps import App

root_agent = Agent(
    model='gemini-2.5-flash',
    name='greeter_agent',
    description='一個提供友善問候的代理。',
    instruction='回覆 Hello, World!',
)

app = App(
    name="agents",
    root_agent=root_agent,
    # 可選擇包含 App 層級的功能：
    # plugins, context_cache_config, resumability_config
)
```

> [!TIP] 建議：使用 `app` 變數名稱
    在您的代理專案程式碼中，將您的 ***App*** 物件設定為變數名稱 `app`，以便與 ADK 命令列介面執行器工具相容。

### 執行您的 App 代理

您可以使用 ***Runner*** 類別並透過 `app` 參數來執行您的代理工作流程，如下方程式碼範例所示：

`main.py` 檔案中的範例程式碼：
```python title="main.py"
import asyncio
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from agent import app

# load_dotenv() # 載入 API 金鑰和設定
load_dotenv()
# 使用匯入的應用程式物件設定 Runner
runner = InMemoryRunner(app=app)

async def main():
    try:
    # try:  # run_debug() 需要 ADK Python 1.18 或更高版本：
        response = await runner.run_debug("Hello there!")

    except Exception as e:
        print(f"An error occurred during agent execution: {e}")
        # print(f"代理執行期間發生錯誤：{e}")

if __name__ == "__main__":
    asyncio.run(main())

```

 > [!NOTE]
    `Runner.run_debug()` 命令需要 ADK Python v1.18.0 或更高版本。
    您也可以使用 `Runner.run()`，這需要更多的設定程式碼。如需更多詳細資訊，請參閱

使用以下命令執行包含 `main.py` 程式碼的 App 代理：

```console
python main.py
```

### 實作範例

-   [`Hello World App`](../../python/agents/hello-world-app/)

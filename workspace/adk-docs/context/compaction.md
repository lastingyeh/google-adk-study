# 壓縮 Agent 上下文以提升效能
🔔 `更新日期：2026-01-10`

[`ADK 支援`: `Python v1.16.0`]

當 ADK Agent 運行時，它會收集「上下文 (context)」資訊，包括使用者指令、檢索到的資料、工具回應以及生成的內容。隨著這些上下文資料量的增加，Agent 的處理時間通常也會隨之增長。越來越多的資料被發送到 Agent 所使用的生成式 AI 模型中，這會增加處理時間並減慢回應速度。ADK 上下文壓縮功能旨在透過摘要 Agent 工作流程事件歷史中較早的部分，來減少 Agent 運行時上下文的大小。

上下文壓縮功能使用「滑動視窗 (sliding window)」方法，在 [會話 (Session)](../sessions&memory/session/overview.md) 內收集並摘要 Agent 工作流程事件資料。當您在 Agent 中配置此功能時，一旦工作流程事件或調用達到特定數量的閾值，它就會摘要來自較舊事件的資料。

## 配置上下文壓縮

透過在工作流程的 App 物件中添加事件壓縮配置 (Events Compaction Configuration) 設定，將上下文壓縮加入您的 Agent 工作流程。作為配置的一部分，您必須指定壓縮間隔 (compaction interval) 和重疊大小 (overlap size)，如下列範例程式碼所示：

```python
from google.adk.apps.app import App
from google.adk.apps.app import EventsCompactionConfig

# 初始化 App 並配置事件壓縮
app = App(
    name='my-agent', # Agent 名稱
    root_agent=root_agent, # 根 Agent
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=3,  # 每隔 3 次新的調用觸發一次壓縮。
        overlap_size=1          # 包含來自前一個視窗的最後一次調用。
    ),
)
```

配置完成後，每當會話達到間隔時，ADK `Runner` 會在背景處理壓縮程序。

## 上下文壓縮範例

如果您將 `compaction_interval` 設置為 3 並將 `overlap_size` 設置為 1，則事件資料將在事件 3、6、9 等完成後進行壓縮。重疊設定會增加第二次摘要壓縮以及之後每次摘要的大小，如圖 1 所示。

![上下文壓縮範例圖解](https://google.github.io/adk-docs/assets/context-compaction.svg)
**圖 1.** 壓縮間隔為 3 且重疊為 1 的事件壓縮配置圖解。

在此範例配置下，上下文壓縮任務的執行過程如下：

1.  **事件 3 完成**：所有 3 個事件被壓縮成一個摘要。
2.  **事件 6 完成**：壓縮事件 3 到 6，包括前一個事件的 1 個重疊。
3.  **事件 9 完成**：壓縮事件 6 到 9，包括前一個事件的 1 個重疊。

## 配置設定

此功能的配置設定控制事件資料壓縮的頻率，以及在 Agent 工作流程運行期間保留多少資料。您可以選擇性地配置一個摘要器物件。

*   **`compaction_interval`**：設置觸發先前事件資料壓縮的已完成事件數量。
*   **`overlap_size`**：設置在新壓縮的上下文集合中包含多少個先前已壓縮的事件。
*   **`summarizer`**：(選填) 定義一個摘要器物件，包括用於摘要的特定 AI 模型。欲了解更多資訊，請參閱[定義摘要器](#定義摘要器)。

### 定義摘要器
您可以透過定義摘要器來客製化上下文壓縮的過程。`LlmEventSummarizer` 類別允許您指定特定的摘要模型。以下程式碼範例示範如何定義和配置自定義摘要器：

```python
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
from google.adk.models import Gemini

# 定義用於摘要的 AI 模型：
summarization_llm = Gemini(model="gemini-2.5-flash")

# 使用自定義模型建立摘要器：
my_summarizer = LlmEventSummarizer(llm=summarization_llm)

# 配置包含自定義摘要器和壓縮設定的 App：
app = App(
    name='my-agent',
    root_agent=root_agent,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=3,
        overlap_size=1,
        summarizer=my_summarizer,
    ),
)
```

您可以透過修改 `SlidingWindowCompactor` 的摘要器類別 `LlmEventSummarizer`（包括更改該類別的 `prompt_template` 設定），進一步優化其操作。更多細節請參閱 [`LlmEventSummarizer` 程式碼](https://github.com/google/adk-python/blob/main/src/google/adk/apps/llm_event_summarizer.py#L60)。

## 下一步

如需如何使用`LlmEventSummarizer` 完整實作，請參閱以下範例：

- [關於 LlmEventSummarizer 參考範例](../../python/agents/hello-world-app/)
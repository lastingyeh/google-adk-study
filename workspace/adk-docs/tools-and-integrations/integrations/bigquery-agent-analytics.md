# 適用於 ADK 的 BigQuery Agent Analytics 外掛程式

> 🔔 `更新日期：2026-03-04`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/bigquery-agent-analytics/

[`ADK 支援`: `Python v1.21.0` | `Preview`]

> [!TIP] 版本需求
請使用 ADK Python 版本 1.26.0 或更高版本，以充分利用本文檔中描述的功能，包括自動架構升級、工具來源追蹤和 HITL 事件追蹤。

BigQuery Agent Analytics 外掛程式透過為深入的代理行為分析提供強大的解決方案，顯著增強了代理開發套件 (ADK)。利用 ADK 外掛程式架構和 **BigQuery Storage Write API**，它能直接將關鍵營運事件擷取並記錄到 Google BigQuery 表格中，為您提供進階的偵錯、即時監控和全面的離線效能評估功能。

1.26.0 版本新增了**自動架構升級**（安全地向現有表格添加新資料欄）、**工具來源**追蹤（LOCAL、MCP、SUB_AGENT、A2A、TRANSFER_AGENT）以及用於人機協作互動的 **HITL 事件追蹤**。

> [!IMPORTANT] 預覽版本
BigQuery Agent Analytics 外掛程式目前處於預覽版本。如需更多資訊，請參閱[產品發布階段說明](https://cloud.google.com/products#product-launch-stages)。

> [!WARNING] BigQuery Storage Write API
此功能使用 **BigQuery Storage Write API**，這是一項付費服務。有關費用的資訊，請參閱 [BigQuery 說明文件](https://cloud.google.com/bigquery/pricing?e=48754805&hl=en#data-ingestion-pricing)。

## 使用案例

- **代理工作流偵錯與分析：** 將廣泛的*外掛程式生命週期事件*（LLM 調用、工具使用）和*代理產生的事件*（使用者輸入、模型回應）擷取到定義良好的架構中。
- **高交易量分析與偵錯：** 使用 Storage Write API 非同步執行記錄操作，以實現高吞吐量和低延遲。
- **多模態分析**：記錄並分析文字、影像和其他模態。大型檔案會卸載到 GCS，使其可透過物件表被 BigQuery ML 存取。
- **分散式追蹤**：內建對 OpenTelemetry 風格追蹤（`trace_id`、`span_id`）的支援，以視覺化代理執行流程。
- **工具來源**：追蹤每個工具調用的來源（本地函數、MCP 伺服器、子代理、A2A 遠端代理或傳輸代理）。
- **人機協作 (HITL) 追蹤**：針對憑證請求、確認提示和使用者輸入請求的專用事件類型。

記錄的代理事件資料根據 ADK 事件類型而異。如需更多資訊，請參閱[事件類型與資料內容](#事件類型與資料內容)。

## 先決條件

- 已啟用 **BigQuery API** 的 **Google Cloud 專案**。
- **BigQuery 資料集：** 在使用外掛程式之前，請先建立一個資料集來儲存記錄表。如果表格不存在，外掛程式會在資料集中自動建立必要的事件表。
- **Google Cloud Storage 儲存桶（選用）：** 如果您計劃記錄多模態內容（影像、音訊等），建議建立一個 GCS 儲存桶來卸載大型檔案。
- **驗證：**
  - **本地：** 執行 `gcloud auth application-default login`。
  - **雲端：** 確保您的服務帳戶具有所需的權限。

### IAM 權限

為了讓代理正常運作，執行代理的主體（例如服務帳戶、使用者帳戶）需要具備以下 Google Cloud 角色：
- 專案層級的 `roles/bigquery.jobUser`，用於執行 BigQuery 查詢。
- 表格層級的 `roles/bigquery.dataEditor`，用於寫入記錄/事件資料。
- **如果使用 GCS 卸載：** 目標儲存桶上的 `roles/storage.objectCreator` 和 `roles/storage.objectViewer`。

## 與代理搭配使用

您可以透過設定 BigQuery Agent Analytics 外掛程式並將其註冊到 ADK 代理的 App 物件來使用它。以下範例顯示了包含 GCS 卸載功能的代理實作：

`my_bq_agent/agent.py`
```python
# my_bq_agent/agent.py
import os
import google.auth
from google.adk.apps import App
from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryAgentAnalyticsPlugin, BigQueryLoggerConfig
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig


# --- OpenTelemetry 追蹤器供應商設定 (選用) ---
# ADK 將 OpenTelemetry 作為核心依賴項。
# 設定 TracerProvider 可啟用完整的分散式追蹤
# (使用標準 OTel 識別碼填充 trace_id, span_id)。
# 如果未設定 TracerProvider，外掛程式會回退到內部
# UUID 進行跨度關聯，同時仍保留父子層級結構。
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
trace.set_tracer_provider(TracerProvider())

# --- 設定 ---
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-gcp-project-id")
DATASET_ID = os.environ.get("BIG_QUERY_DATASET_ID", "your-big-query-dataset-id")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "US") # 外掛程式中的預設位置為 US
GCS_BUCKET = os.environ.get("GCS_BUCKET_NAME", "your-gcs-bucket-name") # 選用

if PROJECT_ID == "your-gcp-project-id":
    raise ValueError("請設定 GOOGLE_CLOUD_PROJECT 或更新程式碼。")

# --- 關鍵：在 Gemini 實例化之前設定環境變數 ---
os.environ['GOOGLE_CLOUD_PROJECT'] = PROJECT_ID
os.environ['GOOGLE_CLOUD_LOCATION'] = LOCATION
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'

# --- 使用設定初始化外掛程式 ---
bq_config = BigQueryLoggerConfig(
    enabled=True,
    gcs_bucket_name=GCS_BUCKET, # 為多模態內容啟用 GCS 卸載
    log_multi_modal_content=True,
    max_content_length=500 * 1024, # 內嵌文字限制為 500 KB
    batch_size=1, # 預設為 1 以實現低延遲，增加此值可提高吞吐量
    shutdown_timeout=10.0
)

bq_logging_plugin = BigQueryAgentAnalyticsPlugin(
    project_id=PROJECT_ID,
    dataset_id=DATASET_ID,
    table_id="agent_events", # 預設資料表名稱為 agent_events
    config=bq_config,
    location=LOCATION
)

# --- 初始化工具與模型 ---
credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
bigquery_toolset = BigQueryToolset(
    credentials_config=BigQueryCredentialsConfig(credentials=credentials)
)

llm = Gemini(model="gemini-2.5-flash")

root_agent = Agent(
    model=llm,
    name='my_bq_agent',
    instruction="你是一個有用的助手，可以使用 BigQuery 工具。",
    tools=[bigquery_toolset]
)

# --- 建立 App ---
app = App(
    name="my_bq_agent",
    root_agent=root_agent,
    plugins=[bq_logging_plugin],
)
```

### 執行並測試代理

透過執行代理並經由聊天介面發送一些請求（例如「告訴我你能做什麼」或「列出我的雲端專案中的資料集」）來測試外掛程式。這些操作會產生事件，並記錄在您的 Google Cloud 專案 BigQuery 實例中。處理完這些事件後，您可以使用以下查詢在 [BigQuery 控制台](https://console.cloud.google.com/bigquery)中查看它們的資料：

```sql
SELECT timestamp, event_type, content
FROM `your-gcp-project-id.your-big-query-dataset-id.agent_events`
ORDER BY timestamp DESC
LIMIT 20;
```

## 追蹤與可觀測性

外掛程式支援使用 **OpenTelemetry** 進行分散式追蹤。OpenTelemetry 已作為 ADK 的核心依賴項包含在內，並且始終可用。

- **自動跨度 (Span) 管理**：外掛程式會自動為代理執行、LLM 調用和工具執行產生跨度。
- **OpenTelemetry 整合**：如果設定了 `TracerProvider`（如上例所示），外掛程式將使用有效的 OTel 跨度，並使用標準 OTel 識別碼填充 `trace_id`、`span_id` 和 `parent_span_id`。這使您能夠將代理記錄與分散式系統中的其他服務關聯起來。
- **回退(Fallback)機制**：如果未設定 `TracerProvider`（即僅啟用預設的無操作提供者），外掛程式會自動回退到為跨度產生內部 UUID，並將 `invocation_id` 用作追蹤 ID。這確保了即使沒有設定 `TracerProvider`，父子層級結構（代理 -> 跨度 -> 工具/LLM）也*始終*保留在 BigQuery 記錄中。

## 設定選項

您可以使用 `BigQueryLoggerConfig` 自定義外掛程式。

| 配置選項 | 類型 | 預設值 | 說明 |
| :--- | :--- | :--- | :--- |
| **`enabled`** | `bool` | `True` | 要停用外掛程式將代理資料記錄到 BigQuery 表格，請將此參數設定為 False。 |
| **`table_id`** | `str` | `"agent_events"` | 資料集中的 BigQuery 表格 ID。也可以被 `BigQueryAgentAnalyticsPlugin` 建構函數中的 `table_id` 參數覆蓋，該參數具有優先權。 |
| **`clustering_fields`** | `List[str]` | `["event_type", "agent", "user_id"]` | 自動建立 BigQuery 表格時用於叢集的欄位。 |
| **`gcs_bucket_name`** | `Optional[str]` | `None` | 用於卸載大型內容（影像、二進位大型物件、長文字）的 GCS 儲存桶名稱。如果未提供，大型內容可能會被截斷或替換為預留位置。 |
| **`connection_id`** | `Optional[str]` | `None` | 用作 `ObjectRef` 欄位授權者的 BigQuery 連線 ID（例如 `us.my-connection`）。在 BigQuery ML 中使用 `ObjectRef` 時需要。 |
| **`max_content_length`** | `int` | `500 * 1024` | 在卸載到 GCS（如果已設定）或截斷之前，存儲在 BigQuery **內嵌**中的文字內容最大長度（以字元為單位）。預設為 500 KB。 |
| **`batch_size`** | `int` | `1` | 寫入 BigQuery 之前的事件批次大小。 |
| **`batch_flush_interval`** | `float` | `1.0` | 清空部分批次之前等待的最長時間（以秒為單位）。 |
| **`shutdown_timeout`** | `float` | `10.0` | 關閉期間等待記錄清空的時間（秒）。 |
| **`event_allowlist`** | `Optional[List[str]]` | `None` | 要記錄的事件類型列表。如果為 `None`，則記錄除 `event_denylist` 之外的所有事件，可參考：[事件類型與資料內容](#事件類型與資料內容)。 |
| **`event_denylist`** | `Optional[List[str]]` | `None` | 要跳過記錄的事件類型列表，可參考：[事件類型與資料內容](#事件類型與資料內容)。 |
| **`content_formatter`** | `Optional[Callable]` | `None` | 在記錄之前格式化事件內容的選用函數。接收原始內容和事件類型字串作為參數。 |
| **`log_multi_modal_content`** | `bool` | `True` | 是否記錄詳細的內容部分（包括 GCS 參考）。 |
| **`queue_max_size`** | `int` | `10000` | 在捨棄新事件之前，記憶體隊列中可保留的最大事件數。 |
| **`retry_config`** | `RetryConfig` | `RetryConfig()` | 失敗的 BigQuery 寫入重試設定（屬性：`max_retries`、`initial_delay`、`multiplier`、`max_delay`）。 |
| **`log_session_metadata`** | `bool` | `True` | 如果為 True，則將對話資訊記錄到 `attributes` 欄位中，包括 `session_id`、`app_name`、`user_id` 和對話 `state` 字典。 |
| **`custom_tags`** | `Dict[str, Any]` | `{}` | 要包含在每個事件的 `attributes` 欄位中的靜態標籤字典（例如 `{"env": "prod", "version": "1.0"}`）。 |
| **`auto_schema_upgrade`** | `bool` | `True` | 啟用後，當外掛程式架構演進時，自動向現有表格添加新資料欄。僅執行累加式更改。 |

以下程式碼範例顯示如何為 BigQuery Agent Analytics 外掛程式定義設定：

```python
import json
import re

from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryLoggerConfig

def redact_dollar_amounts(event_content: Any, event_type: str) -> str:
    """
    自定義格式化程式，用於隱藏金額（例如 $600、$12.50）
    並確保如果輸入是字典，則輸出 JSON。

    參數：
        event_content: 事件的原始內容。
        event_type: 事件類型字串（例如 "LLM_REQUEST"、"LLM_RESPONSE"）。
    """
    text_content = ""
    if isinstance(event_content, dict):
        text_content = json.dumps(event_content)
    else:
        text_content = str(event_content)

    # 用於查找金額的正規表示式：$ 後面跟著數字，可選包含逗號或小數點。
    # 範例：$600, $1,200.50, $0.99
    redacted_content = re.sub(r'\$\d+(?:,\d{3})*(?:\.\d+)?', 'xxx', text_content)

    return redacted_content

config = BigQueryLoggerConfig(
    enabled=True,
    event_allowlist=["LLM_REQUEST", "LLM_RESPONSE"], # 僅記錄這些事件
    # event_denylist=["TOOL_STARTING"], # 跳過這些事件
    shutdown_timeout=10.0, # 結束時最多等待 10 秒以清空記錄
    max_content_length=500, # 將內容截斷為 500 個字元
    content_formatter=redact_dollar_amounts, # 隱藏記錄內容中的金額
    queue_max_size=10000, # 記憶體中保留的最大事件數
    auto_schema_upgrade=True, # 自動向現有表格添加新資料欄
    # retry_config=RetryConfig(max_retries=3), # 選用：設定重試
)

plugin = BigQueryAgentAnalyticsPlugin(..., config=config)
```

## 架構與生產環境設定

### 架構參考

事件表 (`agent_events`) 使用靈活的架構。下表提供了包含範例值的全面參考。

| 欄位名稱 | 類型 | 模式 | 說明 | 範例值 |
| :--- | :--- | :--- | :--- | :--- |
| **timestamp** | `TIMESTAMP` | `REQUIRED` | 事件建立的 UTC 時間戳記。作為主要排序鍵和每日分區鍵。精度為微秒。 | `2026-02-03 20:52:17 UTC` |
| **event_type** | `STRING` | `NULLABLE` | 規範的事件類別。標準值包括 `LLM_REQUEST`、`LLM_RESPONSE`、`LLM_ERROR`、`TOOL_STARTING`、`TOOL_COMPLETED`、`TOOL_ERROR`、`AGENT_STARTING`、`AGENT_COMPLETED`、`STATE_DELTA`、`INVOCATION_STARTING`、`INVOCATION_COMPLETED`、`USER_MESSAGE_RECEIVED` 和 HITL 事件（參見 [HITL 事件](#hitl-events)）。用於高階過濾。 | `LLM_REQUEST` |
| **agent** | `STRING` | `NULLABLE` | 負責此事件的代理名稱。在代理初始化期間或透過 `root_agent_name` 上下文定義。 | `my_bq_agent` |
| **session_id** | `STRING` | `NULLABLE` | 整個對話執行緒的持久識別碼。在多次輪換和子代理調用中保持不變。 | `04275a01-1649-4a30-b6a7-5b443c69a7bc` |
| **invocation_id** | `STRING` | `NULLABLE` | 單次執行輪換或請求週期的唯一識別碼。在許多上下文中對應於 `trace_id`。 | `e-b55b2000-68c6-4e8b-b3b3-ffb454a92e40` |
| **user_id** | `STRING` | `NULLABLE` | 發起工作階段的使用者（人類或系統）識別碼。從 `User` 物件或中繼資料中擷取。 | `test_user` |
| **trace_id** | `STRING` | `NULLABLE` | **OpenTelemetry** 追蹤 ID（32 位元十六進位）。連結單個分散式請求生命週期內的所有操作。 | `e-b55b2000-68c6-4e8b-b3b3-ffb454a92e40` |
| **span_id** | `STRING` | `NULLABLE` | **OpenTelemetry** 跨度 ID（16 位元十六進位）。唯一標識此特定原子操作。 | `69867a836cd94798be2759d8e0d70215` |
| **parent_span_id** | `STRING` | `NULLABLE` | 直接調用者的跨度 ID。用於重建父子執行樹 (DAG)。 | `ef5843fe40764b4b8afec44e78044205` |
| **content** | `JSON` | `NULLABLE` | 主要事件資料內容。架構根據 `event_type` 呈現多型性。 | `{"system_prompt": "You are...", "prompt": [{"role": "user", "content": "hello"}], "response": "Hi", "usage": {"total": 15}}` |
| **attributes** | `JSON` | `NULLABLE` | 中繼資料/增強資訊（使用統計、模型資訊、工具來源、自定義標籤）。 | `{"model": "gemini-2.5-flash", "usage_metadata": {"total_token_count": 15}, "session_metadata": {"session_id": "...", "app_name": "...", "user_id": "...", "state": {}}, "custom_tags": {"env": "prod"}}` |
| **latency_ms** | `JSON` | `NULLABLE` | 效能指標。標準鍵為 `total_ms`（掛鐘時間持續時間）和 `time_to_first_token_ms`（串流延遲）。 | `{"total_ms": 1250, "time_to_first_token_ms": 450}` |
| **status** | `STRING` | `NULLABLE` | 高階結果。值：`OK`（成功）或 `ERROR`（失敗）。 | `OK` |
| **error_message** | `STRING` | `NULLABLE` | 人類可讀的異常訊息或堆疊追蹤片段。僅在 `status` 為 `ERROR` 時填入。 | `Error 404: Dataset not found` |
| **is_truncated** | `BOOLEAN` | `NULLABLE` | 如果 `content` 或 `attributes` 超過 BigQuery 單元格大小限制（預設 10MB）並被部分捨棄，則為 `true`。 | `false` |
| **content_parts** | `RECORD` | `REPEATED` | 多模態分段（文字、影像、大型二進位物件）陣列。當內容無法序列化為簡單 JSON 時使用（例如大型二進位檔案或 GCS 參考）。 | `[{"mime_type": "text/plain", "text": "hello"}]` |

如果表格不存在，外掛程式會自動建立。但是，對於生產環境，我們建議使用以下 DDL 手動建立表格，該 DDL 利用 **JSON** 類型來提供靈活性，並使用 **REPEATED RECORD** 來處理多模態內容。

**建議的 DDL：**

```sql
CREATE TABLE `your-gcp-project-id.adk_agent_logs.agent_events`
(
  timestamp TIMESTAMP NOT NULL OPTIONS(description="記錄事件的 UTC 時間。"),
  event_type STRING OPTIONS(description="指示正在記錄的事件類型（例如 'LLM_REQUEST'、'TOOL_COMPLETED'）。"),
  agent STRING OPTIONS(description="與事件相關聯的 ADK 代理或作者名稱。"),
  session_id STRING OPTIONS(description="用於在單個對話或使用者工作階段中分組事件的唯一識別碼。"),
  invocation_id STRING OPTIONS(description="工作階段中每個單獨代理執行或輪換的唯一識別碼。"),
  user_id STRING OPTIONS(description="與目前工作階段相關聯的使用者識別碼。"),
  trace_id STRING OPTIONS(description="用於分散式追蹤的 OpenTelemetry 追蹤 ID。"),
  span_id STRING OPTIONS(description="此特定操作的 OpenTelemetry 跨度 ID。"),
  parent_span_id STRING OPTIONS(description="用於重建層級結構的 OpenTelemetry 父跨度 ID。"),
  content JSON OPTIONS(description="以 JSON 格式存儲的特定事件資料（資料內容）。"),
  content_parts ARRAY<STRUCT<
    mime_type STRING,
    uri STRING,
    object_ref STRUCT<
      uri STRING,
      version STRING,
      authorizer STRING,
      details JSON
    >,
    text STRING,
    part_index INT64,
    part_attributes STRING,
    storage_mode STRING
  >> OPTIONS(description="多模態資料的詳細內容部分。"),
  attributes JSON OPTIONS(description="用於附加中繼資料的任意鍵值對（例如 'root_agent_name'、'model_version'、'usage_metadata'、'session_metadata'、'custom_tags'）。"),
  latency_ms JSON OPTIONS(description="延遲測量（例如 total_ms）。"),
  status STRING OPTIONS(description="事件的結果，通常為 'OK' 或 'ERROR'。"),
  error_message STRING OPTIONS(description="如果發生錯誤，則填入此項。"),
  is_truncated BOOLEAN OPTIONS(description="標記指示內容是否被截斷。")
)
PARTITION BY DATE(timestamp)
CLUSTER BY event_type, agent, user_id;
```

### 事件類型與資料內容

`content` 欄位現在包含一個特定於 `event_type` 的 **JSON** 物件。`content_parts` 欄位提供了內容的結構化視圖，對於影像或卸載的資料特別有用。

> [!NOTE] 內容截斷
> - 可變內容欄位會截斷為 `max_content_length`（在 `BigQueryLoggerConfig` 中設定，預設為 500KB）。
> - 如果設定了 `gcs_bucket_name`，大型內容將卸載到 GCS 而不是被截斷，並在 `content_parts.object_ref` 中存儲參考。

#### LLM 互動（外掛程式生命週期）

這些事件追蹤發送給 LLM 的原始請求以及從 LLM 接收的回應。

**1. LLM_REQUEST**

擷取發送給模型的提示，包括對話歷史記錄和系統指令。

```json
{
  "event_type": "LLM_REQUEST",
  "content": {
    "system_prompt": "You are a helpful assistant...",
    "prompt": [
      {
        "role": "user",
        "content": "hello how are you today"
      }
    ]
  },
  "attributes": {
    "root_agent_name": "my_bq_agent",
    "model": "gemini-2.5-flash",
    "tools": ["list_dataset_ids", "execute_sql"],
    "llm_config": {
      "temperature": 0.5,
      "top_p": 0.9
    }
  }
}
```

**2. LLM_RESPONSE**

擷取模型的輸出和權杖使用統計資料。

```json
{
  "event_type": "LLM_RESPONSE",
  "content": {
    "response": "text: 'Hello! I'm doing well...'",
    "usage": {
      "completion": 19,
      "prompt": 10129,
      "total": 10148
    }
  },
  "attributes": {
    "root_agent_name": "my_bq_agent",
    "model_version": "gemini-2.5-flash-001",
    "usage_metadata": {
      "prompt_token_count": 10129,
      "candidates_token_count": 19,
      "total_token_count": 10148
    }
  },
  "latency_ms": {
    "time_to_first_token_ms": 2579,
    "total_ms": 2579
  }
}
```

**3. LLM_ERROR**

當 LLM 調用失敗並出現異常時記錄。擷取錯誤訊息並關閉跨度。

```json
{
  "event_type": "LLM_ERROR",
  "content": null,
  "attributes": {
    "root_agent_name": "my_bq_agent"
  },
  "error_message": "Error 429: Resource exhausted",
  "latency_ms": {
    "total_ms": 350
  }
}
```

#### 工具使用（外掛程式生命週期）

這些事件追蹤代理對工具的執行。每個工具事件都包含一個 `tool_origin` 欄位，用於分類工具的來源：

| 工具來源 | 說明 |
| :--- | :--- |
| `LOCAL` | `FunctionTool` 實例（本地 Python 函數） |
| `MCP` | 模型上下文通訊協定工具（`McpTool` 實例） |
| `SUB_AGENT` | `AgentTool` 實例（子代理） |
| `A2A` | 遠端代理對代理實例 (`RemoteA2aAgent`) |
| `TRANSFER_AGENT` | `TransferToAgentTool` 實例 |
| `UNKNOWN` | 未分類的工具 |

**4. TOOL_STARTING**

當代理開始執行工具時記錄。

```json
{
  "event_type": "TOOL_STARTING",
  "content": {
    "tool": "list_dataset_ids",
    "args": {
      "project_id": "bigquery-public-data"
    },
    "tool_origin": "LOCAL"
  }
}
```

**5. TOOL_COMPLETED**

當工具執行完成時記錄。

```json
{
  "event_type": "TOOL_COMPLETED",
  "content": {
    "tool": "list_dataset_ids",
    "result": [
      "austin_311",
      "austin_bikeshare"
    ],
    "tool_origin": "LOCAL"
  },
  "latency_ms": {
    "total_ms": 467
  }
}
```

**6. TOOL_ERROR**

當工具執行失敗並出現異常時記錄。擷取工具名稱、引數、工具來源和錯誤訊息。

```json
{
  "event_type": "TOOL_ERROR",
  "content": {
    "tool": "list_dataset_ids",
    "args": {
      "project_id": "nonexistent-project"
    },
    "tool_origin": "LOCAL"
  },
  "error_message": "Error 404: Dataset not found",
  "latency_ms": {
    "total_ms": 150
  }
}
```

#### 狀態管理

這些事件追蹤代理狀態的更改，通常由工具觸發。

**7. STATE_DELTA**

追蹤代理內部狀態的更改（例如，權杖快取更新）。

```json
{
  "event_type": "STATE_DELTA",
  "attributes": {
    "state_delta": {
      "bigquery_token_cache": "{\"token\": \"ya29...\", \"expiry\": \"...\"}"
    }
  }
}
```

#### 代理生命週期與通用事件

| **事件類型** | **內容 (JSON) 結構** |
| :--- | :--- |
| `INVOCATION_STARTING` | `{}` |
| `INVOCATION_COMPLETED` | `{}` |
| `AGENT_STARTING` | `"你是一個有用的代理..."` |
| `AGENT_COMPLETED` | `{}` |
| `USER_MESSAGE_RECEIVED` | `{"text_summary": "Help me book a flight."}` |

#### 人機協作 (HITL) 事件

外掛程式會自動偵測對 ADK 綜合 HITL 工具的調用，並為其發送專用的事件類型。這些事件會**在**正常的 `TOOL_STARTING` / `TOOL_COMPLETED` 事件之外記錄。

可識別以下 HITL 工具名稱：

- `adk_request_credential` — 請求使用者憑證（例如 OAuth 權杖）
- `adk_request_confirmation` — 在繼續之前請求使用者確認
- `adk_request_input` — 請求自由格式的使用者輸入

| **事件類型** | **觸發因素** | **內容 (JSON) 結構** |
| :--- | :--- | :--- |
| `HITL_CREDENTIAL_REQUEST` | 代理調用 `adk_request_credential` | `{"tool": "adk_request_credential", "args": {...}}` |
| `HITL_CREDENTIAL_REQUEST_COMPLETED` | 使用者提供憑證回應 | `{"tool": "adk_request_credential", "result": {...}}` |
| `HITL_CONFIRMATION_REQUEST` | 代理調用 `adk_request_confirmation` | `{"tool": "adk_request_confirmation", "args": {...}}` |
| `HITL_CONFIRMATION_REQUEST_COMPLETED` | 使用者提供確認回應 | `{"tool": "adk_request_confirmation", "result": {...}}` |
| `HITL_INPUT_REQUEST` | 代理調用 `adk_request_input` | `{"tool": "adk_request_input", "args": {...}}` |
| `HITL_INPUT_REQUEST_COMPLETED` | 使用者提供輸入回應 | `{"tool": "adk_request_input", "result": {...}}` |

HITL 請求事件是從 `on_event_callback` 中的 `function_call` 部分偵測到的。HITL 完成事件是從 `on_event_callback` 和 `on_user_message_callback` 中的 `function_response` 部分偵測到的。

#### GCS 卸載範例（多模態與長文字）

設定 `gcs_bucket_name` 後，長文字和多模態內容（影像、音訊等）將自動卸載到 GCS。`content` 欄位將包含摘要或預留位置，而 `content_parts` 包含指向 GCS URI 的 `object_ref`。

**卸載文字範例**

```json
{
  "event_type": "LLM_REQUEST",
  "content_parts": [
    {
      "part_index": 1,
      "mime_type": "text/plain",
      "storage_mode": "GCS_REFERENCE",
      "text": "AAAA... [OFFLOADED]",
      "object_ref": {
        "uri": "gs://haiyuan-adk-debug-verification-1765319132/2025-12-10/e-f9545d6d/ae5235e6_p1.txt",
        "authorizer": "us.bqml_connection",
        "details": {"gcs_metadata": {"content_type": "text/plain"}}
      }
    }
  ]
}
```

**卸載影像範例**

```json
{
  "event_type": "LLM_REQUEST",
  "content_parts": [
    {
      "part_index": 2,
      "mime_type": "image/png",
      "storage_mode": "GCS_REFERENCE",
      "text": "[MEDIA OFFLOADED]",
      "object_ref": {
        "uri": "gs://haiyuan-adk-debug-verification-1765319132/2025-12-10/e-f9545d6d/ae5235e6_p2.png",
        "authorizer": "us.bqml_connection",
        "details": {"gcs_metadata": {"content_type": "image/png"}}
      }
    }
  ]
}
```

**查詢卸載的內容（獲取已簽署的 URL）**

```sql
SELECT
  timestamp,
  event_type,
  part.mime_type,
  part.storage_mode,
  part.object_ref.uri AS gcs_uri,
  -- 產生已簽署的 URL 以直接讀取內容（需要設定 connection_id）
  STRING(OBJ.GET_ACCESS_URL(part.object_ref, 'r').access_urls.read_url) AS signed_url
FROM `your-gcp-project-id.your-dataset-id.agent_events`,
UNNEST(content_parts) AS part
WHERE part.storage_mode = 'GCS_REFERENCE'
ORDER BY timestamp DESC
LIMIT 10;
```

## 進階分析查詢

**使用 trace_id 追蹤特定的對話輪換**

```sql
SELECT timestamp, event_type, agent, JSON_VALUE(content, '$.response') as summary
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE trace_id = 'your-trace-id'
ORDER BY timestamp ASC;
```

**權杖使用分析（存取 JSON 欄位）**

```sql
SELECT
  AVG(CAST(JSON_VALUE(content, '$.usage.total') AS INT64)) as avg_tokens
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type = 'LLM_RESPONSE';
```

**查詢多模態內容（使用 content_parts 和 ObjectRef）**

```sql
SELECT
  timestamp,
  part.mime_type,
  part.object_ref.uri as gcs_uri
FROM `your-gcp-project-id.your-dataset-id.agent_events`,
UNNEST(content_parts) as part
WHERE part.mime_type LIKE 'image/%'
ORDER BY timestamp DESC;
```

**使用 BigQuery 遠端模型 (Gemini) 分析多模態內容**

```sql
SELECT
  logs.session_id,
  -- 獲取影像的已簽署 URL
  STRING(OBJ.GET_ACCESS_URL(parts.object_ref, "r").access_urls.read_url) as signed_url,
  -- 使用遠端模型（例如 gemini-pro-vision）分析影像
  AI.GENERATE(
    ('簡要描述這張圖片。是什麼公司的標誌？', parts.object_ref)
  ) AS generated_result
FROM
  `your-gcp-project-id.your-dataset-id.agent_events` logs,
  UNNEST(logs.content_parts) AS parts
WHERE
  parts.mime_type LIKE 'image/%'
ORDER BY logs.timestamp DESC
LIMIT 1;
```

**延遲分析（LLM 與工具）**

```sql
SELECT
  event_type,
  AVG(CAST(JSON_VALUE(latency_ms, '$.total_ms') AS INT64)) as avg_latency_ms
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type IN ('LLM_RESPONSE', 'TOOL_COMPLETED')
GROUP BY event_type;
```

**跨度層級結構與持續時間分析**

```sql
SELECT
  span_id,
  parent_span_id,
  event_type,
  timestamp,
  -- 從已完成操作的 latency_ms 中擷取持續時間
  CAST(JSON_VALUE(latency_ms, '$.total_ms') AS INT64) as duration_ms,
  -- 識別特定的工具或操作
  COALESCE(
    JSON_VALUE(content, '$.tool'),
    'LLM_CALL'
  ) as operation
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE trace_id = 'your-trace-id'
  AND event_type IN ('LLM_RESPONSE', 'TOOL_COMPLETED')
ORDER BY timestamp ASC;
```

**錯誤分析（LLM 與工具錯誤）**

```sql
SELECT
  timestamp,
  event_type,
  agent,
  error_message,
  JSON_VALUE(content, '$.tool') as tool_name,
  CAST(JSON_VALUE(latency_ms, '$.total_ms') AS INT64) as latency_ms
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type IN ('LLM_ERROR', 'TOOL_ERROR')
ORDER BY timestamp DESC
LIMIT 20;
```

**工具來源分析**

```sql
SELECT
  JSON_VALUE(content, '$.tool_origin') as tool_origin,
  JSON_VALUE(content, '$.tool') as tool_name,
  COUNT(*) as call_count,
  AVG(CAST(JSON_VALUE(latency_ms, '$.total_ms') AS INT64)) as avg_latency_ms
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type = 'TOOL_COMPLETED'
GROUP BY tool_origin, tool_name
ORDER BY call_count DESC;
```

**HITL 互動分析**

```sql
SELECT
  timestamp,
  event_type,
  session_id,
  JSON_VALUE(content, '$.tool') as hitl_tool,
  content
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type LIKE 'HITL_%'
ORDER BY timestamp DESC
LIMIT 20;
```

### 7. AI 驅動的根因分析 (Agent Ops)

使用 BigQuery ML 和 Gemini 自動分析失敗的工作階段，以確定錯誤的根本原因。

```sql
DECLARE failed_session_id STRING;
-- 查找最近失敗的工作階段
SET failed_session_id = (
    SELECT session_id
    FROM `your-gcp-project-id.your-dataset-id.agent_events`
    WHERE error_message IS NOT NULL
    ORDER BY timestamp DESC
    LIMIT 1
);

-- 重建完整的對話上下文
WITH SessionContext AS (
    SELECT
        session_id,
        STRING_AGG(CONCAT(event_type, ': ', COALESCE(TO_JSON_STRING(content), '')), '\n' ORDER BY timestamp) as full_history
    FROM `your-gcp-project-id.your-dataset-id.agent_events`
    WHERE session_id = failed_session_id
    GROUP BY session_id
)
-- 請求 Gemini 診斷問題
SELECT
    session_id,
    AI.GENERATE(
        ('分析此對話日誌並解釋失敗的根本原因。日誌：', full_history),
        connection_id => 'your-gcp-project-id.us.my-connection',
        endpoint => 'gemini-2.5-flash'
    ).result AS root_cause_explanation
FROM SessionContext;
```

## BigQuery 中的對話式分析

您還可以使用 [BigQuery 對話式分析](https://cloud.google.com/bigquery/docs/conversational-analytics) 使用自然語言分析您的代理記錄。使用此工具來回答以下問題：

- 「顯示一段時間內的錯誤率」
- 「最常見的工具調用是什麼？」
- 「識別具有高權杖使用量的工作階段」

## Looker Studio 儀表板

您可以使用我們預先建立的 [Looker Studio 儀表板範本](https://lookerstudio.google.com/c/reporting/f1c5b513-3095-44f8-90a2-54953d41b125/page/8YdhF) 視覺化您的代理效能。

要將此儀表板連接到您自己的 BigQuery 表格，請使用以下鏈接格式，將預留位置替換為您的特定專案、資料集和表格 ID：

```text
https://lookerstudio.google.com/reporting/create?c.reportId=f1c5b513-3095-44f8-90a2-54953d41b125&ds.ds3.connector=bigQuery&ds.ds3.type=TABLE&ds.ds3.projectId=<your-project-id>&ds.ds3.datasetId=<your-dataset-id>&ds.ds3.tableId=<your-table-id>
```

## 回饋

我們歡迎您對 BigQuery Agent Analytics 提供回饋。如果您有任何疑問、建議或遇到任何問題，請透過 bqaa-feedback@google.com 與團隊聯繫。

## 其他資源

- [BigQuery Storage Write API](https://cloud.google.com/bigquery/docs/write-api)
- [物件表簡介](https://docs.cloud.google.com/bigquery/docs/object-table-introduction)
- [互動式展示筆記本](https://github.com/haiyuan-eng-google/demo_BQ_agent_analytics_plugin_notebook)

# BigQuery Agent Analytics 外掛程式

> 🔔 `更新日期：2026-01-28`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/observability/bigquery-agent-analytics/

[`ADK 支援`: `Python v1.21.0` | `Preview`]

> [!IMPORTANT] 版本要求
請使用 ***最新版本*** 的 ADK（1.21.0 或更高版本），以充分利用本文件所述的功能。

BigQuery Agent Analytics 外掛程式透過提供強大的代理行為深入分析解決方案，顯著增強了代理開發套件 (ADK)。利用 ADK 外掛程式架構和 **BigQuery Storage Write API**，它能直接將關鍵營運事件擷取並記錄到 Google BigQuery 資料表中，為您提供進階的除錯、即時監控和全面的離線效能評估功能。

1.21.0 版本引入了 **混合多模態記錄 (Hybrid Multimodal Logging)**，允許您將大型負載（圖片、音訊、大型二進位物件）卸載至 Google Cloud Storage (GCS)，同時在 BigQuery 中保留結構化引用 (`ObjectRef`)，以此來記錄大型負載。

> [!TIP] 預覽版本
BigQuery Agent Analytics 外掛程式目前處於預覽階段。如需詳細資訊，請參閱
[發布階段說明](https://cloud.google.com/products#product-launch-stages)。

> [!WARNING] BigQuery Storage Write API
此功能使用 **BigQuery Storage Write API**，這是一項付費服務。
有關費用的資訊，請參閱[BigQuery 文件](https://cloud.google.com/bigquery/pricing?e=48754805&hl=en#data-ingestion-pricing)。

## 使用案例

-   **代理工作流除錯與分析：** 將各種 *外掛程式生命週期事件*（LLM 呼叫、工具使用）和 *代理產生的事件*（使用者輸入、模型回應）擷取到定義完善的結構化結構 (Schema) 中。
-   **高吞吐量分析與除錯：** 使用 Storage Write API 非同步執行記錄操作，以實現高吞吐量和低延遲。
-   **多模態分析：** 記錄並分析文本、圖片和其他模態。大型檔案會卸載至 GCS，使其可透過物件表格 (Object Tables) 供 BigQuery ML 存取。
-   **分散式追蹤：** 內建支援 OpenTelemetry 風格的追蹤 (`trace_id`, `span_id`)，以視覺化代理執行流程。

記錄的代理事件資料會因 ADK 事件類型而異。如需詳細資訊，請參閱 [事件類型與負載](#事件類型與負載)。

## 前置作業

-   已啟用 **BigQuery API** 的 **Google Cloud 專案**。
-   **BigQuery 資料集：** 在使用外掛程式之前，建立一個資料集來儲存記錄表。如果資料表不存在，外掛程式會在資料集中自動建立必要的事件表。
-   **Google Cloud Storage 儲存桶（選用）：** 如果您計畫記錄多模態內容（圖片、音訊等），建議建立一個 GCS 儲存桶來卸載大型檔案。
-   **驗證：**
    -   **本地端：** 執行 `gcloud auth application-default login`。
    -   **雲端：** 確保您的服務帳戶具有必要的權限。

### IAM 權限

為了讓代理正常運作，執行代理的主體（例如服務帳戶、使用者帳戶）需要具備以下 Google Cloud 角色：
* 專案層級的 `roles/bigquery.jobUser`，用於執行 BigQuery 查詢。
* 資料表層級的 `roles/bigquery.dataEditor`，用於寫入記錄/事件資料。
* **如果使用 GCS 卸載：** 目標儲存桶上的 `roles/storage.objectCreator` 和 `roles/storage.objectViewer`。

## 與代理搭配使用

您可以透過設定並向 ADK 代理的 App 物件註冊，來使用 BigQuery Agent Analytics 外掛程式。以下範例顯示了一個包含此外掛程式（包含 GCS 卸載功能）的代理實作：

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

# --- OpenTelemetry 初始化 (選用) ---
# 建議用於啟用分散式追蹤 (填入 trace_id, span_id)。
# 如果未配置，外掛程式將使用內部 UUID 進行跨度 (span) 關聯。
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    trace.set_tracer_provider(TracerProvider())
except ImportError:
    pass # OpenTelemetry 是選用的

# --- 設定 ---
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-gcp-project-id")
DATASET_ID = os.environ.get("BIG_QUERY_DATASET_ID", "your-big-query-dataset-id")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "US") # 外掛程式中的預設位置為 US
GCS_BUCKET = os.environ.get("GCS_BUCKET_NAME", "your-gcs-bucket-name") # 選用

if PROJECT_ID == "your-gcp-project-id":
    raise ValueError("請設置 GOOGLE_CLOUD_PROJECT 或更新程式碼。")

# --- 關鍵：在 Gemini 實例化之前設置環境變數 ---
os.environ['GOOGLE_CLOUD_PROJECT'] = PROJECT_ID
os.environ['GOOGLE_CLOUD_LOCATION'] = LOCATION
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'

# --- 使用設定初始化外掛程式 ---
bq_config = BigQueryLoggerConfig(
    enabled=True,
    gcs_bucket_name=GCS_BUCKET, # 為多模態內容啟用 GCS 卸載
    log_multi_modal_content=True,
    max_content_length=500 * 1024, # 內嵌文本限制為 500 KB
    batch_size=1, # 低延遲預設為 1，高吞吐量可增加此值
    shutdown_timeout=10.0
)

bq_logging_plugin = BigQueryAgentAnalyticsPlugin(
    project_id=PROJECT_ID,
    dataset_id=DATASET_ID,
    table_id="agent_events_v2", # 預設資料表名稱為 agent_events_v2
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
    instruction="你是一個樂於助人的助手，可以使用 BigQuery 工具。",
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

透過執行代理並在聊天介面中發送一些請求（例如「告訴我你能做什麼」或「列出我的雲端專案 <your-gcp-project-id> 中的資料集」）來測試外掛程式。這些操作會產生事件，並記錄在您的 Google Cloud 專案 BigQuery 實例中。處理完這些事件後，您可以在 [BigQuery 主控台](https://console.cloud.google.com/bigquery) 中使用此查詢查看相關資料。

```sql
SELECT timestamp, event_type, content
FROM `your-gcp-project-id.your-big-query-dataset-id.agent_events_v2`
ORDER BY timestamp DESC
LIMIT 20;
```

#### 追蹤與可觀測性

此外掛程式支援使用 **OpenTelemetry** 進行分散式追蹤。

- **自動跨度 (Span) 管理**：外掛程式會自動為代理執行、LLM 呼叫和工具執行產生跨度。
- **OpenTelemetry 整合**：如果配置了 OpenTelemetry `TracerProvider`（如上例所示），外掛程式將使用有效的 OTel 跨度，並使用標準 OTel 識別碼填充 `trace_id`、`span_id` 和 `parent_span_id`。這使您能夠將代理記錄與分散式系統中的其他服務建立關聯。
- **備用機制**：如果未安裝或未配置 OpenTelemetry，外掛程式會自動退而求其次，為跨度產生內部 UUID，並將 `invocation_id` 用作追蹤 ID (trace ID)。這確保了即使沒有完整的 OTel 設置，父子階層結構 (Agent -> Span -> Tool/LLM) 也 *始終* 保存在 BigQuery 記錄中。

#### 設定選項

您可以使用 `BigQueryLoggerConfig` 自定義外掛程式。

-   **`enabled`** (`bool`, 預設: `True`): 若要停用外掛程式將代理資料記錄到 BigQuery 資料表，請將此參數設置為 False。
-   **`clustering_fields`** (`List[str]`, 預設: `["event_type", "agent", "user_id"]`): 自動建立資料表時，用於對 BigQuery 資料表進行叢集化的欄位。
-   **`gcs_bucket_name`** (`Optional[str]`, 預設: `None`): 用於卸載大型內容（圖片、二進位物件、大型文本）的 GCS 儲存桶名稱。如果未提供，大型內容可能會被截斷或被預留位置取代。
-   **`connection_id`** (`Optional[str]`, 預設: `None`): 作為 `ObjectRef` 欄位授權者的 BigQuery 連線 ID（例如 `us.my-connection`）。在 BigQuery ML 中使用 `ObjectRef` 時需要此設定。
-   **`max_content_length`** (`int`, 預設: `500 * 1024`): 在卸載至 GCS（如果已配置）或截斷之前，儲存在 BigQuery **內聯** 的文本內容最大長度（以字元為單位）。預設為 500 KB。
-   **`batch_size`** (`int`, 預設: `1`): 寫入 BigQuery 之前要批次處理的事件數量。
-   **`batch_flush_interval`** (`float`, 預設: `1.0`): 刷新部分批次之前的最長等待時間（以秒為單位）。
-   **`shutdown_timeout`** (`float`, 預設: `10.0`): 關閉期間等待記錄刷新的秒數。
-   **`event_allowlist`** (`Optional[List[str]]`, 預設: `None`): 要記錄的事件類型清單。如果為 `None`，則記錄除 `event_denylist` 中的事件外的所有事件。有關支援的事件類型的完整清單，請參閱 [事件類型與負載](#event-types) 部分。
-   **`event_denylist`** (`Optional[List[str]]`, 預設: `None`): 要跳過記錄的事件類型清單。有關支援的事件類型的完整清單，請參閱 [事件類型與負載](#event-types) 部分。
-   **`content_formatter`** (`Optional[Callable[[Any, str], Any]]`, 預設: `None`): 在記錄之前格式化事件內容的選用函數。
-   **`log_multi_modal_content`** (`bool`, 預設: `True`): 是否記錄詳細的內容部分（包括 GCS 引用）。
-   **`queue_max_size`** (`int`, 預設: `10000`): 在捨棄新事件之前，記憶體隊列中可容納的最大事件數。
-   **`retry_config`** (`RetryConfig`, 預設: `RetryConfig()`): 重試失敗的 BigQuery 寫入的配置（屬性：`max_retries`, `initial_delay`, `multiplier`, `max_delay`）。


以下程式碼範例顯示如何為 BigQuery Agent Analytics 外掛程式定義設定：

```python
import json
import re

from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryLoggerConfig

def redact_dollar_amounts(event_content: Any) -> str:
    """
    自定義格式化程式，用於隱藏金額（例如 $600、$12.50）
    並在輸入為字典時確保 JSON 輸出。
    """
    text_content = ""
    if isinstance(event_content, dict):
        text_content = json.dumps(event_content)
    else:
        text_content = str(event_content)

    # 用於查找金額的正規表示式：$ 後跟數字，可選擇帶有逗號或小數。
    # 範例：$600, $1,200.50, $0.99
    redacted_content = re.sub(r'\$\d+(?:,\d{3})*(?:\.\d+)?', 'xxx', text_content)

    return redacted_content

config = BigQueryLoggerConfig(
    enabled=True,
    event_allowlist=["LLM_REQUEST", "LLM_RESPONSE"], # 僅記錄這些事件
    # event_denylist=["TOOL_STARTING"], # 跳過這些事件
    shutdown_timeout=10.0, # 退出時最多等待 10 秒以刷新記錄
    client_close_timeout=2.0, # 最多等待 2 秒以關閉 BQ 用戶端
    max_content_length=500, # 將內容截斷為 500 個字元
    content_formatter=redact_dollar_amounts, # 隱藏記錄內容中的金額
    queue_max_size=10000, # 記憶體中可保存的最大事件數
    # retry_config=RetryConfig(max_retries=3), # 選用：配置重試
)

plugin = BigQueryAgentAnalyticsPlugin(..., config=config)
```

## 結構 (Schema) 與生產環境設置

如果資料表不存在，外掛程式會自動建立。但是，對於生產環境，我們建議使用以下 DDL 手動建立資料表，該 DDL 利用 **JSON** 類型以獲得靈活性，並使用 **REPEATED RECORD**s 來處理多模態內容。

**建議的 DDL：**

```sql
CREATE TABLE `your-gcp-project-id.adk_agent_logs.agent_events_v2`
(
  timestamp TIMESTAMP NOT NULL OPTIONS(description="記錄事件的 UTC 時間。"),
  event_type STRING OPTIONS(description="指示正在記錄的事件類型（例如 'LLM_REQUEST'、'TOOL_COMPLETED'）。"),
  agent STRING OPTIONS(description="與事件相關聯的 ADK 代理或作者的名稱。"),
  session_id STRING OPTIONS(description="在單次對話或使用者工作階段中對事件進行分組的唯一識別碼。"),
  invocation_id STRING OPTIONS(description="工作階段中每個代理執行或輪次的唯一識別碼。"),
  user_id STRING OPTIONS(description="與當前工作階段關聯的使用者識別碼。"),
  trace_id STRING OPTIONS(description="用於分散式追蹤的 OpenTelemetry 追蹤 ID。"),
  span_id STRING OPTIONS(description="此特定操作的 OpenTelemetry 跨度 ID。"),
  parent_span_id STRING OPTIONS(description="用於重建階層結構的 OpenTelemetry 父跨度 ID。"),
  content JSON OPTIONS(description="以 JSON 格式儲存的事件特定資料（負載）。"),
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
  attributes JSON OPTIONS(description="用於額外中繼資料的任意鍵值對（例如 'root_agent_name'、'model_version'、'usage_metadata'）。"),
  latency_ms JSON OPTIONS(description="延遲測量值（例如 total_ms）。"),
  status STRING OPTIONS(description="事件的結果，通常為 'OK' 或 'ERROR'。"),
  error_message STRING OPTIONS(description="如果發生錯誤則填入此處。"),
  is_truncated BOOLEAN OPTIONS(description="指示內容是否被截斷的旗標。")
)
PARTITION BY DATE(timestamp)
CLUSTER BY event_type, agent, user_id;
```

### 事件類型與負載

`content` 欄位現在包含一個特定於 `event_type` 的 **JSON** 物件。
`content_parts` 欄位提供了內容的結構化檢視，對於圖片或卸載的資料特別有用。

> [!NOTE] 內容截斷
> - 變數內容欄位會被截斷為 `max_content_length`（在 `BigQueryLoggerConfig` 中配置，預設為 500KB）。
> - 如果配置了 `gcs_bucket_name`，大型內容將卸載至 GCS 而不是被截斷，並在 `content_parts.object_ref` 中存儲引用。

#### LLM 互動（外掛程式生命週期）

這些事件追蹤發送給 LLM 的原始請求以及從中收到的回應。

<table>
  <thead>
    <tr>
      <th><strong>事件類型</strong></th>
      <th><strong>內容 (JSON) 結構</strong></th>
      <th><strong>屬性 (JSON)</strong></th>
      <th><strong>範例內容（簡化）</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><pre>LLM_REQUEST</pre></p></td>
      <td><p><pre>
{
  "prompt": [
    {"role": "user", "content": "..."}
  ],
  "system_prompt": "..."
}
</pre></p></td>
      <td><p><pre>
{
  "tools": ["tool_a", "tool_b"],
  "llm_config": {"temperature": 0.5},
  "root_agent_name": "my_root_agent"
}
</pre></p></td>
      <td><p><pre>
{
  "prompt": [
    {"role": "user", "content": "法國的首都是哪裡？"}
  ],
  "system_prompt": "你是一個樂於助人的地理助手。"
}
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>LLM_RESPONSE</pre></p></td>
      <td><p><pre>
{
  "response": "...",
  "usage": {...}
}
</pre></p></td>
      <td><p><pre>
{
  "model_version": "gemini-2.5-pro-001",
  "usage_metadata": {
    "prompt_token_count": 15,
    "candidates_token_count": 7,
    "total_token_count": 22
  }
}
</pre></p></td>
      <td><p><pre>
{
  "response": "法國的首都是巴黎。",
  "usage": {
    "prompt": 15,
    "completion": 7,
    "total": 22
  }
}
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>LLM_ERROR</pre></p></td>
      <td><p><pre>null</pre></p></td>
      <td><p><pre>{}</pre></p></td>
      <td><p><pre>null (請參閱 error_message 欄位)</pre></p></td>
    </tr>
  </tbody>
</table>

#### 工具使用（外掛程式生命週期）

這些事件追蹤代理對工具的執行情況。

<table>
  <thead>
    <tr>
      <th><strong>事件類型</strong></th>
      <th><strong>內容 (JSON) 結構</strong></th>
      <th><strong>屬性 (JSON)</strong></th>
      <th><strong>範例內容</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><pre>TOOL_STARTING</pre></p></td>
      <td><p><pre>
{
  "tool": "...",
  "args": {...}
}
</pre></p></td>
      <td><p><pre>{}</pre></p></td>
      <td><p><pre>
{"tool": "list_datasets", "args": {"project_id": "my-project"}}
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>TOOL_COMPLETED</pre></p></td>
      <td><p><pre>
{
  "tool": "...",
  "result": "..."
}
</pre></p></td>
      <td><p><pre>{}</pre></p></td>
      <td><p><pre>
{"tool": "list_datasets", "result": ["ds1", "ds2"]}
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>TOOL_ERROR</pre></p></td>
      <td><p><pre>
{
  "tool": "...",
  "args": {...}
}
</pre></p></td>
      <td><p><pre>{}</pre></p></td>
      <td><p><pre>
{"tool": "list_datasets", "args": {}}
</pre></p></td>
    </tr>
  </tbody>
</table>

#### 代理生命週期與通用事件

<table>
  <thead>
    <tr>
      <th><strong>事件類型</strong></th>
      <th><strong>內容 (JSON) 結構</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><pre>INVOCATION_STARTING</pre></p></td>
      <td><p><pre>{}</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>INVOCATION_COMPLETED</pre></p></td>
      <td><p><pre>{}</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>AGENT_STARTING</pre></p></td>
      <td><p><pre>"你是一個樂於助人的代理..."</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>AGENT_COMPLETED</pre></p></td>
      <td><p><pre>{}</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>USER_MESSAGE_RECEIVED</pre></p></td>
      <td><p><pre>{"text_summary": "幫我預訂航班。"}</pre></p></td>
    </tr>

  </tbody>
</table>

#### GCS 卸載範例（多模態與大型文本）

配置 `gcs_bucket_name` 後，大型文本和多模態內容（圖片、音訊等）將自動卸載到 GCS。`content` 欄位將包含摘要或預留位置，而 `content_parts` 包含指向 GCS URI 的 `object_ref`。

**卸載文本範例 (Offloaded Text Example)**

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

**卸載圖片範例 (Offloaded Image Example)**

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

**查詢卸載內容（Get Signed URLs）**

```sql
SELECT
  timestamp,
  event_type,
  part.mime_type,
  part.storage_mode,
  part.object_ref.uri AS gcs_uri,
  -- 產生簽署 URL 以直接讀取內容（需要 connection_id 設定）
  STRING(OBJ.GET_ACCESS_URL(part.object_ref, 'r').access_urls.read_url) AS signed_url
FROM `your-gcp-project-id.your-dataset-id.agent_events_v2`,
UNNEST(content_parts) AS part
WHERE part.storage_mode = 'GCS_REFERENCE'
ORDER BY timestamp DESC
LIMIT 10;
```

## 進階分析查詢

**使用 trace_id 追蹤特定對話輪次**

```sql
SELECT timestamp, event_type, agent, JSON_VALUE(content, '$.response') as summary
FROM `your-gcp-project-id.your-dataset-id.agent_events_v2`
WHERE trace_id = 'your-trace-id'
ORDER BY timestamp ASC;
```

**權仗 (Token) 使用情況分析（存取 JSON 欄位）**

```sql
SELECT
  AVG(CAST(JSON_VALUE(content, '$.usage.total') AS INT64)) as avg_tokens
FROM `your-gcp-project-id.your-dataset-id.agent_events_v2`
WHERE event_type = 'LLM_RESPONSE';
```

**查詢多模態內容（使用 content_parts 和 ObjectRef）**

```sql
SELECT
  timestamp,
  part.mime_type,
  part.object_ref.uri as gcs_uri
FROM `your-gcp-project-id.your-dataset-id.agent_events_v2`,
UNNEST(content_parts) as part
WHERE part.mime_type LIKE 'image/%'
ORDER BY timestamp DESC;
```

**使用 BigQuery 遠端模型 (Gemini) 分析多模態內容**

```sql
SELECT
  logs.session_id,
  -- 取得圖片的簽署 URL
  STRING(OBJ.GET_ACCESS_URL(parts.object_ref, "r").access_urls.read_url) as signed_url,
  -- 使用遠端模型（例如 gemini-pro-vision）分析圖片
  AI.GENERATE(
    ('請簡要描述此圖片。這是哪家公司的標誌？', parts.object_ref)
  ) AS generated_result
FROM
  `your-gcp-project-id.your-dataset-id.agent_events_v2` logs,
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
FROM `your-gcp-project-id.your-dataset-id.agent_events_v2`
WHERE event_type IN ('LLM_RESPONSE', 'TOOL_COMPLETED')
GROUP BY event_type;
```

**跨度 (Span) 階層結構與持續時間分析**

```sql
SELECT
  span_id,
  parent_span_id,
  event_type,
  timestamp,
  -- 從已完成操作的 latency_ms 中提取持續時間
  CAST(JSON_VALUE(latency_ms, '$.total_ms') AS INT64) as duration_ms,
  -- 識別特定的工具或操作
  COALESCE(
    JSON_VALUE(content, '$.tool'),
    'LLM_CALL'
  ) as operation
FROM `your-gcp-project-id.your-dataset-id.agent_events_v2`
WHERE trace_id = 'your-trace-id'
  AND event_type IN ('LLM_RESPONSE', 'TOOL_COMPLETED')
ORDER BY timestamp ASC;
```

### 7. AI 驅動的根因分析 (Agent Ops)

使用 BigQuery ML 和 Gemini 自動分析失敗的工作階段，以確定錯誤的根本原因。

```sql
DECLARE failed_session_id STRING;
-- 查找最近失敗的工作階段
SET failed_session_id = (
    SELECT session_id
    FROM `your-gcp-project-id.your-dataset-id.agent_events_v2`
    WHERE error_message IS NOT NULL
    ORDER BY timestamp DESC
    LIMIT 1
);

-- 重建完整的對話上下文
WITH SessionContext AS (
    SELECT
        session_id,
        STRING_AGG(CONCAT(event_type, ': ', COALESCE(TO_JSON_STRING(content), '')), '\n' ORDER BY timestamp) as full_history
    FROM `your-gcp-project-id.your-dataset-id.agent_events_v2`
    WHERE session_id = failed_session_id
    GROUP BY session_id
)
-- 請求 Gemini 診斷問題
SELECT
    session_id,
    AI.GENERATE(
        ('分析此對話記錄並解釋失敗的根本原因。記錄：', full_history),
        connection_id => 'your-gcp-project-id.us.my-connection',
        endpoint => 'gemini-2.5-flash'
    ).result AS root_cause_explanation
FROM SessionContext;
```

## BigQuery 中的對話式分析

您還可以使用
[BigQuery 對話式分析 (Conversational Analytics)](https://cloud.google.com/bigquery/docs/conversational-analytics)
來使用自然語言分析代理記錄。使用此工具回答如下問題：

*   「顯示隨時間變化的錯誤率」
*   「最常見的工具呼叫有哪些？」
*   「識別 Token 使用量較高的工作階段」

## Looker Studio 儀表板

您可以使用我們預先建立的 [Looker Studio 儀表板範本](https://lookerstudio.google.com/c/reporting/f1c5b513-3095-44f8-90a2-54953d41b125/page/8YdhF) 來視覺化代理的效能。

要將此儀表板連接到您自己的 BigQuery 資料表，請使用以下連結格式，並將預留位置替換為您特定的專案、資料集和資料表 ID：

```text
https://lookerstudio.google.com/reporting/create?c.reportId=f1c5b513-3095-44f8-90a2-54953d41b125&ds.ds3.connector=bigQuery&ds.ds3.type=TABLE&ds.ds3.projectId=<your-project-id>&ds.ds3.datasetId=<your-dataset-id>&ds.ds3.tableId=<your-table-id>
```

## 其他資源

-   [BigQuery Storage Write API](https://cloud.google.com/bigquery/docs/write-api)
-   [物件表格 (Object Tables) 簡介](https://cloud.google.com/bigquery/docs/object-tables-intro)
-   [互動式示範筆記本](https://github.com/haiyuan-eng-google/demo_BQ_agent_analytics_plugin_notebook)

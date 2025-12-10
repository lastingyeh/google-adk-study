# 官方 Google ADK OpenTelemetry 設定指南

基於 `research/adk-python/src/google/adk/telemetry/` 中的官方原始碼

## 概覽

Google ADK 提供內建的 OpenTelemetry 整合，以實現 AI 代理 (Agents) 的全面可觀測性。本指南說明官方設定模式，以及如何正確設定追蹤 (Traces)、日誌 (Logs) 和指標 (Metrics)。

## 官方 ADK 遙測架構

### 關鍵元件

ADK 的遙測系統包含三種主要的訊號類型：

1. **追蹤 (Traces)**：分散式請求追蹤 (代理的主要訊號)
2. **日誌 (Logs)**：與追蹤相關聯的結構化日誌
3. **指標 (Metrics)**：效能測量 (選用)

### 官方語意慣例 (Semantic Conventions)

ADK 遵循 GenAI 系統的 OpenTelemetry Semantic Conventions v1.37+：

```python
# 來自 research/adk-python/src/google/adk/telemetry/tracing.py
GEN_AI_AGENT_NAME = 'gen_ai.agent.name'
GEN_AI_AGENT_DESCRIPTION = 'gen_ai.agent.description'
GEN_AI_CONVERSATION_ID = 'gen_ai.conversation.id'
GEN_AI_OPERATION_NAME = 'gen_ai.operation.name'
GEN_AI_TOOL_NAME = 'gen_ai.tool.name'
GEN_AI_TOOL_DESCRIPTION = 'gen_ai.tool.description'
GEN_AI_TOOL_TYPE = 'gen_ai.tool.type'
GEN_AI_TOOL_CALL_ID = 'gen_ai.tool.call.id'
```

### 自動儀表化 (Automatic Instrumentation)

ADK 自動儀表化以下項目：

- ✅ **代理調用 (Agent Invocations)**：帶有代理元資料的 `invoke_agent` span
- ✅ **工具呼叫 (Tool Calls)**：帶有參數和回應的 `execute_tool` span
- ✅ **LLM 請求 (LLM Requests)**：模型、使用的 token、結束原因
- ✅ **資料交換 (Data Exchange)**：輸入/輸出資料 (可設定)

## 官方設定模式

### 1. 基本遙測設定 (僅追蹤)

來自 `research/adk-python/src/google/adk/telemetry/setup.py`：

```python
from google.adk.telemetry import setup

# 使用標準 OTLP 匯出器設定 (使用環境變數)
setup.maybe_set_otel_providers(
    otel_hooks_to_setup=[
        # 將自動偵測 OTEL_EXPORTER_OTLP_ENDPOINT 環境變數
    ]
)
```

### 2. 使用 Jaeger 進行本地開發

**本教學推薦：**

```python
# otel_config.py - 在任何 ADK 匯入之前初始化
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry import trace

# 建立資源
resource = Resource(attributes={
    "service.name": "my-adk-agent",
    "service.version": "1.0.0",
})

# 建立帶有 OTLP 匯出器的 provider
provider = TracerProvider(resource=resource)
exporter = OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces")
processor = BatchSpanProcessor(exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# 在您的主代理模組中
# math_agent/agent.py
from otel_config import initialize_otel
initialize_otel()  # 必須是第一個！

from google.adk.agents import Agent
# ... 其餘的代理程式碼
```

### 3. 搭配日誌 (生產環境推薦)

來自 `research/adk-python/src/google/adk/telemetry/setup.py`：

```python
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry import _logs, _events
from opentelemetry.sdk._events import EventLoggerProvider

# 建立 logger provider
logger_provider = LoggerProvider(resource=resource)

# 新增用於日誌的 OTLP 匯出器
log_exporter = OTLPLogExporter(
    endpoint="http://localhost:4318/v1/logs"
)
processor = BatchLogRecordProcessor(log_exporter)
logger_provider.add_log_record_processor(processor)
_logs.set_logger_provider(logger_provider)

# 啟用 gen_ai 語意慣例的事件
event_logger_provider = EventLoggerProvider(logger_provider)
_events.set_event_logger_provider(event_logger_provider)
```

### 4. Google Cloud 整合 (生產環境)

用於 Cloud Trace、Cloud Logging、Cloud Monitoring：

```python
from google.adk.telemetry.google_cloud import (
    get_gcp_exporters,
    get_gcp_resource
)
from google.adk.telemetry.setup import maybe_set_otel_providers

# 取得 GCP 匯出器 (使用應用程式預設憑證)
gcp_hooks = get_gcp_exporters(
    enable_cloud_tracing=True,
    enable_cloud_metrics=True,
    enable_cloud_logging=True,
)

# 取得帶有 GCP 屬性的資源
resource = get_gcp_resource(project_id="my-project")

# 設定所有 providers
maybe_set_otel_providers(
    otel_hooks_to_setup=[gcp_hooks],
    otel_resource=resource,
)
```

## 控制 Span 內容

### 隱私：停用 Spans 中的敏感資料

```python
import os

# 停用 span 中的請求/回應內容
# 在處理 PII 或敏感資訊時很有用
os.environ["ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS"] = "false"

# 現在 spans 對於以下項目將會有空的 {}：
# - gcp.vertex.agent.llm_request
# - gcp.vertex.agent.llm_response
# - gcp.vertex.agent.tool_call_args
# - gcp.vertex.agent.tool_response
```

預設值：`true` (向後相容)

## OTLP 的環境變數

ADK 遵守標準的 OpenTelemetry 環境變數：

```bash
# 標準 OTLP 設定
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf

# 分開的端點 (覆蓋 OTEL_EXPORTER_OTLP_ENDPOINT)
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://localhost:4318/v1/traces
export OTEL_EXPORTER_OTLP_METRICS_ENDPOINT=http://localhost:4318/v1/metrics
export OTEL_EXPORTER_OTLP_LOGS_ENDPOINT=http://localhost:4318/v1/logs

# 資源屬性 (服務名稱、版本等)
export OTEL_RESOURCE_ATTRIBUTES=service.name=my-agent,service.version=1.0.0
export OTEL_SERVICE_NAME=my-agent
```

## 什麼會被追蹤：官方 Span 階層

### invoke_agent (Root Span)

```
invoke_agent (ADK 代理調用)
├── 屬性:
│   ├── gen_ai.agent.name = "math_assistant"
│   ├── gen_ai.agent.description = "數學助手..."
│   ├── gen_ai.conversation.id = "<會話ID>"
│   ├── gen_ai.operation.name = "invoke_agent"
│   └── gcp.vertex.agent.invocation_id = "<調用ID>"
│
├── call_llm (LLM 請求)
│   ├── gen_ai.system = "gcp.vertex.agent"
│   ├── gen_ai.request.model = "gemini-2.5-flash"
│   ├── gen_ai.request.top_p = 0.9
│   ├── gen_ai.request.max_tokens = 8192
│   ├── gen_ai.usage.input_tokens = 150
│   ├── gen_ai.usage.output_tokens = 45
│   ├── gcp.vertex.agent.llm_request = "{...}"
│   └── gcp.vertex.agent.llm_response = "{...}"
│
├── execute_tool (工具呼叫)
│   ├── gen_ai.tool.name = "add_numbers"
│   ├── gen_ai.tool.description = "將兩個數字相加..."
│   ├── gen_ai.tool.type = "FunctionTool"
│   ├── gen_ai.tool.call.id = "<工具呼叫ID>"
│   ├── gcp.vertex.agent.tool_call_args = "{...}"
│   └── gcp.vertex.agent.tool_response = "{...}"
│
└── send_data (傳送資料)
    ├── gcp.vertex.agent.data = "{...}"
    └── gcp.vertex.agent.event_id = "<事件ID>"
```

## 什麼**不**被追蹤 (設計上)

來自官方原始碼註釋：

- ❌ `gen_ai.agent.id`：語意不明確 (全域 vs 範圍本地)
- ❌ `gen_ai.data_source.id`：在 ADK 模型中不可用
- ❌ `server.*` 屬性：等待框架確認

## 在 Jaeger 中檢視追蹤

### 尋找您的追蹤

1. **Service 下拉選單**：選擇 "google-adk-math-agent" (或您的服務名稱)
2. **尋找**：名為 `invoke_agent` (root) 且帶有 `execute_tool` 子項目的 Spans
3. **Attributes 面板**：顯示所有 `gen_ai` 語意慣例資料

### 常見追蹤檢查任務

| 任務 | 如何做 |
|------|-----|
| 查看工具呼叫 | 展開 `invoke_agent` 下的 `execute_tool` spans |
| 檢視 LLM 請求 | 查看 `call_llm` span 屬性 |
| 檢查 token 使用量 | `gen_ai.usage.input_tokens` 和 `gen_ai.usage.output_tokens` |
| 查看工具參數 | 展開 `gcp.vertex.agent.tool_call_args` |
| 取得對話 ID | 透過 `gen_ai.conversation.id` 屬性搜尋 |

## 與 Python Logging 整合

為了更好的可見性，新增 Python logging handler：

```python
import logging

# 在 OTel 設定後取得 logger
logger = logging.getLogger("my_agent")

# 日誌將自動在結構化日誌中包含追蹤上下文 (trace context)
logger.info("Agent started", extra={"user_id": "123"})

# 在 Jaeger 中，日誌可以透過 trace_id/span_id 關聯
```

## 測試您的設定

```python
# 驗證追蹤是否被發送
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("test_span") as span:
    span.set_attribute("test", "value")
    print("Check Jaeger UI for test_span")

# 驗證 logger provider
from opentelemetry import _logs
logger_provider = _logs.get_logger_provider()
print(f"Logger provider: {logger_provider}")
```

## 效能考量

### BatchSpanProcessor (推薦)

```python
# 本教學中使用
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# 優點：
# ✅ 批次處理 spans 以提高效率
# ✅ 減少網路開銷
# ✅ 非同步匯出 (非阻塞)
# ✅ 可以處理突發流量
processor = BatchSpanProcessor(exporter)
```

### 設定選項

```python
# 自訂批次設定
processor = BatchSpanProcessor(
    exporter,
    max_queue_size=2048,  # 最大緩衝 spans 數
    batch_size=512,       # 達到此大小時匯出
    schedule_delay_millis=5000,  # 每 5 秒匯出一次
)
```

## 疑難排解

### Spans 未出現在 Jaeger 中

1. **檢查 Jaeger 是否執行中**：`docker ps | grep jaeger`
2. **驗證端點**：確認 OTLP 端點可以連線
3. **檢查服務名稱**：確保篩選條件符合您的 `service.name`
4. **啟用除錯日誌**：`os.environ["OTEL_LOG_LEVEL"] = "DEBUG"`

### "Overriding of current TracerProvider is not allowed" (不允許覆蓋目前的 TracerProvider)

此警告出現在：
- 在呼叫 `trace.set_tracer_provider()` 之前已經設定了 OTel provider
- 在同一程序中多次初始化呼叫

**解決方案**：僅在應用程式啟動時初始化一次

### Spans 中的 PII 資料

**停用方式**：
```python
os.environ["ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS"] = "false"
```

## 官方參考資料

參考的原始檔：
- `research/adk-python/src/google/adk/telemetry/setup.py` - 核心設定函式
- `research/adk-python/src/google/adk/telemetry/tracing.py` - 語意慣例
- `research/adk-python/src/google/adk/telemetry/google_cloud.py` - GCP 整合

官方 OpenTelemetry 文件：
- [OpenTelemetry Semantic Conventions for GenAI](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [OTLP Exporter Documentation](https://opentelemetry.io/docs/languages/python/exporting-data/)

## 下一步

1. **執行您的代理** 並檢查 Jaeger UI：`http://localhost:16686`
2. **匯出至 Cloud Trace** 用於生產環境，使用 `get_gcp_exporters()`
3. **新增自訂 spans** 用於特定領域操作
4. **監控指標** 使用 Cloud Monitoring 或 Prometheus

## 範例：完整設定

請參閱本教學中的 `math_agent/otel_config.py` 以取得完整、生產就緒的範例，包含：
- ✅ 追蹤至 Jaeger
- ✅ 整合 OTel 的日誌
- ✅ gen_ai 語意慣例的事件
- ✅ Python logging handler
- ✅ 隱私控制

---

## 重點摘要

- **核心概念**：Google ADK 內建 OpenTelemetry 整合，提供 Traces (分散式追蹤)、Logs (日誌) 和 Metrics (指標) 三種訊號，用於 AI 代理的全面可觀測性。
- **關鍵技術**：
    - OpenTelemetry Semantic Conventions v1.37+ (GenAI 專用)。
    - Jaeger (本地追蹤視覺化)。
    - OTLP Exporter (資料匯出)。
    - BatchSpanProcessor (批次處理提升效能)。
    - GCP Integration (Cloud Trace/Logging/Monitoring)。
- **重要結論**：
    - ADK 自動儀表化 `invoke_agent` (代理調用)、`execute_tool` (工具執行) 和 `call_llm` (LLM 請求)。
    - 推薦在生產環境使用 BatchSpanProcessor 和 Python Logging 整合。
    - 應注意隱私，可透過環境變數 `ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS` 停用敏感資料擷取。
    - 避免重複初始化 TracerProvider。
- **行動項目**：
    - 依照官方模式設定 OpenTelemetry (本地使用 Jaeger，生產使用 GCP)。
    - 設定環境變數 `OTEL_EXPORTER_OTLP_ENDPOINT` 等。
    - 使用 Jaeger UI 檢查追蹤和屬性，驗證設定是否正確。

"""
ADK 數學代理的 OpenTelemetry 設定。

此模組展示了 OTel 匯出的**兩種**方法：

1. **ADK 內建支援 (推薦)** - 在 google-adk >= 1.17.0 中可用
   - 用於 GCP Cloud Trace：使用 `adk web --otel_to_cloud`
   - 用於自訂 OTLP：設定 OTEL_EXPORTER_OTLP_ENDPOINT 環境變數

2. **手動 OTel 設定** - 用於詳細控制或舊版 ADK
   - 手動設定 TracerProvider、匯出器 (exporters) 和處理器 (processors)

本教學使用方法 #2 (手動) 來顯示所有細節，但在生產環境中您應該使用方法 #1 搭配 ADK 的內建支援。

參考資料：
- ADK 官方文件：https://github.com/google/adk-python
- OpenTelemetry：https://opentelemetry.io/docs/instrumentation/python/
- Jaeger：https://www.jaegertracing.io/docs/
"""

import logging
import os
import sys
from typing import Optional

from opentelemetry import _logs, _events, trace
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._events import EventLoggerProvider


# ============================================================================
# 簡化方法：讓 ADK 透過環境變數處理 OTel 設定
# ============================================================================
#
# 在生產環境使用時，您可以**略過**此檔案，只需設定環境變數：
#
#   export OTEL_SERVICE_NAME=google-adk-math-agent
#   export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318/v1/traces
#   export OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true
#   adk web .
#
# 然後 ADK (v1.17.0+) 將自動為您設定 OTel！
#
# ============================================================================


def initialize_otel_env(
    service_name: str = "google-adk-math-agent",
    service_version: str = "0.1.0",
    jaeger_endpoint: str = "http://localhost:4318/v1/traces",
) -> None:
    """
    為 ADK 的內建 OpenTelemetry 支援設定環境變數。

    這是生產環境中的**推薦**方法。

    **運作方式**：
    1. 設定 ADK 會自動讀取的環境變數
    2. ADK (v1.17.0+) 根據這些變數設定 OTel 匯出器
    3. 所有追蹤都會自動匯出，無需手動設定

    **用法**：

    ```python
    # 選項 A：呼叫此函式 (如本處所示)
    initialize_otel_env()
    from google.adk.agents import Agent
    # ... 定義代理 ...

    # 選項 B：直接設定環境變數 (更簡單)
    export OTEL_SERVICE_NAME=google-adk-math-agent
    export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318/v1/traces
    adk web .
    ```

    參數:
        service_name: 所有遙測的服務名稱
        service_version: 服務版本
        jaeger_endpoint: OTLP HTTP 端點 (用於非 GCP 後端)
    """
    # 設定 ADK 將讀取並使用的變數
    os.environ.setdefault("OTEL_SERVICE_NAME", service_name)
    os.environ.setdefault("OTEL_EXPORTER_OTLP_ENDPOINT",
                          jaeger_endpoint.rsplit("/v1", 1)[0])  # 移除 /v1/traces
    os.environ.setdefault("OTEL_EXPORTER_OTLP_PROTOCOL", "http/protobuf")

    # 啟用在追蹤中擷取 LLM 提示詞/回應 (對除錯很有用)
    os.environ.setdefault("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "true")

    # 啟用 Python logging 自動儀表化
    os.environ.setdefault("OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED", "true")

    # 用於更好追蹤識別的資源屬性
    os.environ.setdefault("OTEL_RESOURCE_ATTRIBUTES",
                          f"service.name={service_name},service.version={service_version}")

    logger = logging.getLogger("otel_config")
    logger.info(f"✅ 已為 {service_name} 設定 OTel 環境")
    logger.info(f"   匯出器端點：{os.environ.get('OTEL_EXPORTER_OTLP_ENDPOINT')}")
    logger.info("   ADK 將自動使用這些設定 (v1.17.0+)")


# ============================================================================
# 手動 OTel 設定：用於詳細控制或舊版 ADK
# ============================================================================
#
# 如果您需要手動控制 span processors、sampling 等，
# 請改用此方法。這比較繁瑣，但給您完全的控制權。
#
# ============================================================================

# 用於手動遙測設定的全域狀態
_trace_provider = None
_logger_provider = None
_initialized = False


def initialize_otel(
    service_name: str = "google-adk-math-agent",
    service_version: str = "0.1.0",
    jaeger_endpoint: str = "http://localhost:4318/v1/traces",
    enable_logging: bool = True,
    enable_events: bool = True,
    log_level: int = logging.INFO,
    force_reinit: bool = False,
) -> tuple[TracerProvider, Optional[LoggerProvider]]:
    """
    **替代方案**：手動設定 OpenTelemetry (用於詳細控制)。

    ⚠️  **推薦**：改用 `initialize_otel_env()`！
    該方法利用了 ADK 的內建支援 (v1.17.0+)。

    此函式用於：
    - 詳細控制 span processors
    - 取樣設定 (Sampling configuration)
    - 自訂匯出器或多個處理器
    - 舊版 ADK (<1.17.0)

    參數:
        service_name: 所有遙測的服務名稱
        service_version: 服務版本
        jaeger_endpoint: OTLP HTTP 端點
        enable_logging: 啟用 OTel logging
        enable_events: 啟用 OTel events
        log_level: Python logging 等級
        force_reinit: 強制重新初始化 (用於測試)

    傳回:
        (TracerProvider, LoggerProvider 或 None) 的 Tuple
    """
    global _trace_provider, _logger_provider, _initialized

    # 冪等性：除非強制，否則僅初始化一次
    if _initialized and not force_reinit:
        return _trace_provider, _logger_provider

    # 首先設定環境變數 (用於框架自動探索)
    os.environ.setdefault("OTEL_EXPORTER_OTLP_ENDPOINT", jaeger_endpoint.rsplit("/v1", 1)[0])
    os.environ.setdefault("OTEL_EXPORTER_OTLP_PROTOCOL", "http/protobuf")
    os.environ.setdefault("OTEL_RESOURCE_ATTRIBUTES",
                          f"service.name={service_name},service.version={service_version}")
    os.environ.setdefault("OTEL_SERVICE_NAME", service_name)

    # 建立資源
    resource = Resource(attributes={
        "service.name": service_name,
        "service.version": service_version,
        "telemetry.sdk.name": "opentelemetry",
        "telemetry.sdk.language": "python",
    })

    # 設定追蹤 (Traces)
    _trace_provider = TracerProvider(resource=resource)
    trace_exporter = OTLPSpanExporter(endpoint=jaeger_endpoint)
    trace_processor = BatchSpanProcessor(trace_exporter)
    _trace_provider.add_span_processor(trace_processor)
    trace.set_tracer_provider(_trace_provider)

    # ====== 日誌設定 (LOGGING SETUP) ======
    if enable_logging:
        _logger_provider = LoggerProvider(resource=resource)

        # 透過 OTLP HTTP 將日誌匯出到 Jaeger (Jaeger v2 支援 OTLP logs)
        # 注意：日誌是批次處理並非同步匯出的 - 匯出期間的錯誤
        # 不會阻塞應用程式，但會被記錄到 stderr
        try:
            log_exporter = OTLPLogExporter(
                endpoint=jaeger_endpoint.replace("/v1/traces", "/v1/logs")
            )
            log_processor = BatchLogRecordProcessor(log_exporter)
            _logger_provider.add_log_record_processor(log_processor)
            _logs.set_logger_provider(_logger_provider)
        except Exception as e:
            # 如果日誌匯出失敗，繼續僅使用控制台記錄
            logger = logging.getLogger("otel_config")
            logger.warning(f"無法設定 OTLP 日誌匯出：{e}。繼續僅使用控制台記錄。")
            _logs.set_logger_provider(_logger_provider)

        # 啟用 gen_ai 語意慣例的事件
        if enable_events:
            event_logger_provider = EventLoggerProvider(_logger_provider)
            _events.set_event_logger_provider(event_logger_provider)

    # ====== PYTHON LOGGING 設定 (用於控制台輸出) ======
    _setup_python_logging(service_name, log_level)

    # 標記為已初始化
    _initialized = True

    return _trace_provider, _logger_provider


def get_tracer_provider() -> Optional[TracerProvider]:
    """取得全域 tracer provider (如果未初始化則為 None)。"""
    return _trace_provider


def force_flush(timeout_millis: int = 30000) -> bool:
    """
    強制刷新任何待處理的 spans 和 logs 到 Jaeger。

    ⚠️  對 adk web 至關重要：這必須在代理調用後呼叫，
    以確保 spans 在 HTTP 回應傳回之前發送到 Jaeger。

    參數:
        timeout_millis: 等待刷新的最長時間 (預設 30 秒)

    傳回:
        若刷新成功為 True，若逾時為 False
    """
    global _trace_provider, _logger_provider

    if _trace_provider is None:
        return True

    # 刷新追蹤
    success = _trace_provider.force_flush(timeout_millis)

    # 如果可用，刷新日誌
    if _logger_provider is not None:
        success = _logger_provider.force_flush(timeout_millis) and success

    return success


def _setup_python_logging(service_name: str, log_level: int) -> None:
    """
    設定 Python logging 以匯出到 OpenTelemetry (然後到 Jaeger)。

    此函式：
    1. 設定指定等級的 root logger
    2. 建立自訂 handler 將 Python logging 橋接到 OTel
    3. 日誌會同時出現在控制台和透過 OTLP 匯出的 Jaeger 中

    日誌會透過 OpenTelemetry context 自動與追蹤關聯。
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 僅在沒有 handlers 存在時設定
    if not root_logger.handlers:
        # 建立控制台 handler 以獲得即時可見性
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)

        # 格式：時間戳 | 服務 | 等級 | logger | 訊息
        formatter = logging.Formatter(
            fmt=(
                f"%(asctime)s | {service_name} | %(levelname)s | "
                "%(name)s | %(message)s"
            ),
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # 建立橋接到 LoggerProvider 的 OTel handler
        # 這會透過 OTLP 匯出將日誌發送到 Jaeger
        from opentelemetry.sdk._logs import LoggingHandler
        otel_handler = LoggingHandler(level=log_level, logger_provider=_logs.get_logger_provider())
        root_logger.addHandler(otel_handler)

    # 抑制冗長的 OTel exporter logs (在開發中預期會有日誌匯出錯誤)
    logging.getLogger("opentelemetry.exporter.otlp.proto.http._log_exporter").setLevel(
        logging.CRITICAL
    )
    logging.getLogger("opentelemetry").setLevel(
        logging.DEBUG if log_level == logging.DEBUG else logging.WARNING
    )

import os
import warnings

from arize.otel import register
from dotenv import load_dotenv
from openinference.instrumentation.google_adk import GoogleADKInstrumentor
from opentelemetry import trace

"""
## 摘要
本檔案負責將 Google ADK 的遙測資料（Telemetry）整合至 Arize 平台。它設定了 OpenTelemetry 追蹤器（Tracer），以便監控代理人的執行流程。

### 核心重點
- **核心概念**：實現代理人的可觀察性（Observability）。
- **關鍵技術**：Arize AI, OpenTelemetry (OTEL), Google ADK Instrumentation。
- **重要結論**：必須提供 `ARIZE_SPACE_ID` 與 `ARIZE_API_KEY` 才能啟動追蹤功能。
"""

# 載入 .env 環境變數
load_dotenv()


def instrument_adk_with_arize() -> trace.Tracer | None:
    """使用 Arize 對 ADK 進行檢測（Instrumentation）。"""

    # 檢查必要的 Arize 環境變數
    if os.getenv("ARIZE_SPACE_ID") is None:
        warnings.warn("未設定 ARIZE_SPACE_ID", stacklevel=2)
        return None
    if os.getenv("ARIZE_API_KEY") is None:
        warnings.warn("未設定 ARIZE_API_KEY", stacklevel=2)
        return None

    # 註冊 Arize OTEL 追蹤提供者
    tracer_provider = register(
        space_id=os.getenv("ARIZE_SPACE_ID"),
        api_key=os.getenv("ARIZE_API_KEY"),
        project_name=os.getenv("ARIZE_PROJECT_NAME", "adk-rag-agent"),
    )

    # 啟動 Google ADK 的自動檢測
    GoogleADKInstrumentor().instrument(tracer_provider=tracer_provider)

    # 取得並回傳追蹤器實例
    return tracer_provider.get_tracer(__name__)

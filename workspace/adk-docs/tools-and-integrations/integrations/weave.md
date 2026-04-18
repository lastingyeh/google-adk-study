# 為 ADK 提供 W&B Weave 觀測能力

> 🔔 `更新日期：2026-03-09`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/weave/

[`ADK 支援`: `Python`]

[W&B Weave](https://weave-docs.wandb.ai/) 為記錄和視覺化模型調用提供了一個強大的平台。透過將 Google ADK 與 Weave 整合，您可以利用 OpenTelemetry (OTEL) 追蹤來監控並分析代理的效能與行為。

## 前置作業

1. 在 [WandB](https://wandb.ai) 註冊帳號。
2. 從 [WandB Authorize](https://wandb.ai/authorize) 取得您的 API 金鑰。
3. 設定環境變數所需的 API 金鑰：

```bash
# 設定 WandB API 金鑰
export WANDB_API_KEY=<your-wandb-api-key>
# 設定 Google API 金鑰
export GOOGLE_API_KEY=<your-google-api-key>
```

## 安裝依賴項目

確保您已安裝必要的套件：

```bash
# 安裝 Google ADK 以及 OpenTelemetry 相關套件
pip install google-adk opentelemetry-sdk opentelemetry-exporter-otlp-proto-http
```

## 將追蹤數據傳送到 Weave

此範例展示如何配置 OpenTelemetry 以將 Google ADK 的追蹤數據傳送到 Weave。

`math_agent/agent.py`
```python
import base64
import os
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry import trace

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 配置 Weave 端點與認證資訊
WANDB_BASE_URL = "https://trace.wandb.ai"
PROJECT_ID = "your-entity/your-project"  # 例如："teamid/projectid"
OTEL_EXPORTER_OTLP_ENDPOINT = f"{WANDB_BASE_URL}/otel/v1/traces"

# 設置身份驗證
WANDB_API_KEY = os.getenv("WANDB_API_KEY")
AUTH = base64.b64encode(f"api:{WANDB_API_KEY}".encode()).decode()

OTEL_EXPORTER_OTLP_HEADERS = {
    "Authorization": f"Basic {AUTH}",
    "project_id": PROJECT_ID,
}

# 建立 OTLP span 匯出器，包含端點與標頭設定
exporter = OTLPSpanExporter(
    endpoint=OTEL_EXPORTER_OTLP_ENDPOINT,
    headers=OTEL_EXPORTER_OTLP_HEADERS,
)

# 建立 tracer 提供者並添加匯出器
tracer_provider = trace_sdk.TracerProvider()
tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))

# 在匯入或使用 ADK 之前，務必先設置全域 tracer 提供者
trace.set_tracer_provider(tracer_provider)

# 定義一個簡單的工具用於示範
def calculator(a: float, b: float) -> str:
    """相加兩個數字並回傳結果。

    參數:
        a: 第一個數字
        b: 第二個數字

    回傳:
        a 與 b 的總和
    """
    return str(a + b)

calculator_tool = FunctionTool(func=calculator)

# 建立 LLM 代理
root_agent = LlmAgent(
    name="MathAgent",
    model="gemini-2.0-flash-exp",
    instruction=(
        "你是一個可以進行數學運算的得力助手。"
        "當被問到數學問題時，請使用 calculator 工具來解決。"
    ),
    tools=[calculator_tool],
)
```

## 在 Weave 儀表板查看追蹤

代理運行後，其所有的追蹤記錄都會被記錄到 [Weave 儀表板](https://wandb.ai/home) 上對應的專案中。

![traces-overview](https://wandb.github.io/weave-public-assets/google-adk/traces-overview.png)

您可以查看 ADK 代理在執行期間發出的調用時間軸。

![adk-weave-timeline](https://wandb.github.io/weave-public-assets/google-adk/adk-weave-timeline.gif)

## 注意事項

- **環境變數**：確保您的環境變數已正確設定 WandB 和 Google 的 API 金鑰。
- **專案配置**：將 `<your-entity>/<your-project>` 替換為您實際的 WandB 實體名稱與專案名稱。
- **實體名稱**：您可以透過訪問您的 [WandB 儀表板](https://wandb.ai/home) 並查看左側欄位中的 **Teams** 欄位來找到您的實體名稱。
- **Tracer 提供者**：在開始使用任何 ADK 組件之前，設定全域 tracer 提供者至關重要，以確保追蹤功能正常運作。

透過遵循這些步驟，您可以有效地將 Google ADK 與 Weave 整合，實現對 AI 代理的模型調用、工具調用和推理過程的全面記錄與視覺化。

## 相關資源

- **[將 OpenTelemetry 追蹤發送至 Weave](https://weave-docs.wandb.ai/guides/tracking/otel)** - 關於在 Weave 中配置 OTEL 的全面指南，包含身份驗證和進階配置選項。
- **[導覽追蹤視圖](https://weave-docs.wandb.ai/guides/tracking/trace-tree)** - 了解如何有效地在 Weave UI 中分析和調試您的追蹤，包括理解追蹤層次結構和 span 詳細資訊。
- **[Weave 整合](https://weave-docs.wandb.ai/guides/integrations/)** - 探索其他框架整合，並了解 Weave 如何與您的整個 AI 技術棧協作。

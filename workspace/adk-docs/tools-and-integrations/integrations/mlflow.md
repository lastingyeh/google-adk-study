# ADK 的 MLflow 觀測性 (Observability)

> 🔔 `更新日期：2026-03-08`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/mlflow/

[`ADK 支援`: `Python`]

[MLflow 追蹤 (Tracing)](https://mlflow.org/docs/latest/genai/tracing/) 提供了一流的 OpenTelemetry (OTel) 追蹤擷取支援。Google ADK 會針對代理程式執行 (agent runs)、工具呼叫 (tool calls) 和模型請求 (model requests) 發送 OTel span，您可以將這些資訊直接傳送到 MLflow 追蹤伺服器進行分析與除錯。

## 前提條件

- MLflow 版本 3.6.0 或更新版本。OpenTelemetry 擷取僅在 MLflow 3.6.0+ 中受支援。
- 基於 SQL 的後端儲存（例如 SQLite、PostgreSQL、MySQL）。基於檔案的儲存不支援 OTLP 擷取。
- 您的環境中已安裝 Google ADK。

## 安裝依賴項

```bash
# 安裝 MLflow、Google ADK 以及 OpenTelemetry 相關套件
pip install "mlflow>=3.6.0" google-adk opentelemetry-sdk opentelemetry-exporter-otlp-proto-http
```

## 啟動 MLflow 追蹤伺服器

使用 SQL 後端和連接埠（本例為 5000）啟動 MLflow：

```bash
# 使用 SQLite 作為後端儲存並啟動伺服器
mlflow server --backend-store-uri sqlite:///mlflow.db --port 5000
```

您可以將 `--backend-store-uri` 指向其他 SQL 後端（PostgreSQL、MySQL、MSSQL）。基於檔案的後端不支援 OTLP 擷取。

## 設定 OpenTelemetry（必要）

在應用任何 ADK 元件之前，您必須設定 OTLP 匯出器 (exporter) 並設置全域追蹤器提供者 (global tracer provider)，以便將 span 發送到 MLflow。

在匯入或建構 ADK 代理程式/工具之前的程式碼中，初始化 OTLP 匯出器和全域追蹤器提供者：

```python
# my_agent/agent.py
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

# 初始化 OTLP Span 匯出器，指向 MLflow 伺服器的追蹤端點
exporter = OTLPSpanExporter(
    endpoint="http://localhost:5000/v1/traces",
    headers={"x-mlflow-experiment-id": "123"}  # 請替換為您的實驗 ID
)

# 設定追蹤提供者並加入 Span 處理器
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(exporter))

# 在匯入或使用 ADK 之前設定全域追蹤器提供者
trace.set_tracer_provider(provider)
```

這會設定 OpenTelemetry 管線，並在每次執行時將 ADK span 傳送至 MLflow 伺服器。

## 範例：追蹤 ADK 代理程式

在設置好 OTLP 匯出器和追蹤器提供者的程式碼之後，您現在可以為一個簡單的數學代理程式加入代理程式程式碼：

```python
# my_agent/agent.py
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

# 定義一個簡單的加法工具
def calculator(a: float, b: float) -> str:
    """將兩個數字相加並返回結果。"""
    return str(a + b)

# 將函式封裝為 ADK 工具
calculator_tool = FunctionTool(func=calculator)

# 建立 LlmAgent 實例
root_agent = LlmAgent(
    name="MathAgent",
    model="gemini-2.0-flash-exp",
    instruction=(
        "你是一個能進行數學運算的得力助手。"
        "當遇到數學問題時，請使用 calculator 工具來解決它。"
    ),
    tools=[calculator_tool],
)
```

使用以下指令執行代理程式：

```bash
adk run my_agent
```

並詢問一個數學問題：

```console
What is 12 + 34?
```

您應該會看到類似以下的輸出：

```console
[MathAgent]: The answer is 46.
```

## 在 MLflow 中查看追蹤

開啟 MLflow UI 位址 `http://localhost:5000`，選擇您的實驗，然後檢查由您的 ADK 代理程式產生的追蹤樹和 span。

![google-adk-tracing](https://mlflow.org/docs/latest/images/llms/tracing/google-adk-tracing.png)
## 提示

- 請在匯入或初始化 ADK 物件**之前**設定追蹤器提供者，以便擷取所有 span。
- 若在代理伺服器後方或遠端主機上，請將 `localhost:5000` 替換為您的伺服器位址。

## 資源

- [MLflow 追蹤文件](https://mlflow.org/docs/latest/genai/tracing/)：MLflow 追蹤的官方文件，涵蓋了其他程式庫整合以及追蹤的下游用法，例如評估、監控、搜尋等。
- [MLflow 中的 OpenTelemetry](https://mlflow.org/docs/latest/genai/tracing/opentelemetry/)：關於如何將 OpenTelemetry 與 MLflow 搭配使用的詳細指南。
- [代理程式專用的 MLflow](https://mlflow.org/docs/latest/genai/)：關於如何使用 MLflow 構建生產級代理程式的全面指南。

# 使用 MLflow 進行 Agent 觀測

> 🔔 `更新日期：2026-01-29`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/observability/mlflow/

[MLflow Tracing](https://mlflow.org/docs/latest/genai/tracing/) 為攝取 OpenTelemetry (OTel) 追蹤提供了一流的支持。Google ADK 為 Agent 運行、工具調用和模型請求發出 OTel span，您可以將其直接發送到 MLflow Tracking Server 進行分析和調試。

## 前置作業

- MLflow 版本 3.6.0 或更新版本。OpenTelemetry 攝取僅在 MLflow 3.6.0+ 中受支持。
- 基於 SQL 的後端存儲（例如 SQLite、PostgreSQL、MySQL）。基於文件的存儲不支持 OTLP 攝取。
- 您的環境中已安裝 Google ADK。

## 安裝依賴項目

```bash
pip install "mlflow>=3.6.0" google-adk opentelemetry-sdk opentelemetry-exporter-otlp-proto-http
```

## 啟動 MLflow Tracking Server

使用 SQL 後端和端口（本例中為 5000）啟動 MLflow：

```bash
mlflow server --backend-store-uri sqlite:///mlflow.db --port 5000
```

您可以將 `--backend-store-uri` 指向其他 SQL 後端（PostgreSQL、MySQL、MSSQL）。基於文件的後端不支持 OTLP 攝取。

## 配置 OpenTelemetry（必填）

在使用任何 ADK 組件之前，您必須配置 OTLP 匯出器並設置全域追蹤提供者 (global tracer provider)，以便將 span 發送到 MLflow。

在導入或構建 ADK Agent/工具之前的代碼中初始化 OTLP 匯出器和全域追蹤提供者：

```python
# my_agent/agent.py
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

# 初始化 OTLP Span 匯出器，指向 MLflow 伺服器的端點
exporter = OTLPSpanExporter(
    endpoint="http://localhost:5000/v1/traces",
    headers={"x-mlflow-experiment-id": "123"}  # 將其替換為您的實驗 ID
)

# 建立追蹤提供者並添加處理器
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(exporter))
# 在導入或使用 ADK 之前設置全域追蹤提供者
trace.set_tracer_provider(provider)
```

這會配置 OpenTelemetry 管道，並在每次運行時將 ADK span 發送到 MLflow 伺服器。

## 範例：追蹤 ADK Agent

現在，在設置 OTLP 匯出器和追蹤提供者的代碼之後，您可以為簡單的數學 Agent 添加 Agent 代碼：

```python
# my_agent/agent.py
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool


# 定義一個簡單的計算器工具函數
def calculator(a: float, b: float) -> str:
    """相加兩個數字並返回結果。"""
    return str(a + b)


# 將函數封裝為 ADK 工具
calculator_tool = FunctionTool(func=calculator)

# 建立一個 LlmAgent，配置模型、指令和工具
root_agent = LlmAgent(
    name="MathAgent",
    model="gemini-2.0-flash-exp",
    instruction=(
        "You are a helpful assistant that can do math. "
        "When asked a math problem, use the calculator tool to solve it."
    ),
    tools=[calculator_tool],
)
```

使用以下命令運行 Agent：

```bash
adk run my_agent
```

並詢問它一個數學問題：

```console
What is 12 + 34?
```

您應該會看到類似於以下的輸出：

```console
[MathAgent]: The answer is 46.
```

## 在 MLflow 中查看追蹤

在 `http://localhost:5000` 打開 MLflow UI，選擇您的實驗，並檢查由您的 ADK Agent 生成的追蹤樹和 span。

![MLflow Traces](https://mlflow.org/docs/latest/images/llms/tracing/google-adk-tracing.png)

## 提示

- 在導入或初始化 ADK 對象之前設置追蹤提供者，以便捕獲所有 span。
- 在代理伺服器後方或遠端主機上，將 `localhost:5000` 替換為您的伺服器地址。

## 資源

- [MLflow Tracing 文件](https://mlflow.org/docs/latest/genai/tracing/)：MLflow Tracing 的官方文件，涵蓋了其他庫集成和追蹤的下游用途，例如評估、監控、搜索等。
- [MLflow 中的 OpenTelemetry](https://mlflow.org/docs/latest/genai/tracing/opentelemetry/)：關於如何將 OpenTelemetry 與 MLflow 結合使用的詳細指南。
- [Agent 專用的 MLflow](https://mlflow.org/docs/latest/genai/)：關於如何使用 MLflow 構建生產級 Agent 的綜合指南。

# 教學 24: 進階可觀測性與監控

企業級可觀測性系統，展示 ADK 的外掛程式架構，實現全面的監控、指標收集、警報與效能分析。

## 功能特性

- **SaveFilesAsArtifactsPlugin**: 用於除錯的自動構件儲存
- **MetricsCollectorPlugin**: 全面的請求/回應指標
- **AlertingPlugin**: 即時錯誤檢測與警報
- **PerformanceProfilerPlugin**: 詳細的效能分析
- **Production Monitoring System**: 完整的監控解決方案

## 快速入門

### 1. 設定

```bash
# 安裝依賴項
make setup

# 設定驗證 (選擇一種方法)

# 方法 1: API Key (Gemini API)
export GOOGLE_API_KEY=your_api_key_here

# 方法 2: Service Account (VertexAI)
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1

# 方法 3: Application Default Credentials (VertexAI)
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1
```

### 2. 執行 Agent

```bash
# 啟動 ADK 網頁介面
make dev

# 打開 http://localhost:8000
# 從下拉選單中選擇 'observability_plugins_agent'
```

### 3. 嘗試示範提示

```bash
# 查看示範說明
make demo
```

## 學習重點

### 外掛程式系統

ADK 外掛程式系統允許在不修改 Agent 程式碼的情況下進行模組化可觀測性：

```python
runner = InMemoryRunner(
    agent=agent,
    app_name='my_app',
    plugins=[
        SaveFilesAsArtifactsPlugin(),
        MetricsCollectorPlugin(),
        AlertingPlugin(),
        PerformanceProfilerPlugin()
    ]
)
```

### 自訂外掛程式

透過繼承 `BasePlugin` 建立自訂外掛程式：

```python
from google.adk.plugins import BasePlugin

class MetricsCollectorPlugin(BasePlugin):
    async def on_request_start(self, request_id: str, agent: Agent, query: str):
        # 追蹤請求開始
        pass

    async def on_request_complete(self, request_id: str, result):
        # 收集指標
        pass
```

### Cloud Trace 整合

啟用 Cloud Trace 進行分散式追蹤：

```bash
# 部署並啟用追蹤
adk deploy cloud_run --trace_to_cloud

# 本地測試並啟用追蹤
adk web --trace_to_cloud
```

## 專案結構

```
observability-plugins-agent/
├── observability_plugins_agent/       # Agent 實作
│   ├── __init__.py
│   └── agent.py              # 包含外掛程式的主 Agent
├── tests/                    # 測試套件
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_imports.py
│   ├── test_plugins.py
│   └── test_structure.py
├── pyproject.toml           # 套件配置
├── requirements.txt         # 依賴項
├── Makefile                # 指令
├── .env.example           # 環境範本
└── README.md             # 本檔案
```

## 程式碼架構圖
 ```mermaid
 classDiagram
     class Agent {
         +model: str
         +name: str
         +description: str
         +instruction: str
     }

     class BasePlugin {
         +name: str
         +on_event_callback(event)
     }

     class MetricsCollectorPlugin {
         +metrics: AggregateMetrics
         +on_event_callback(event)
         +get_summary()
     }

     class AlertingPlugin {
         +latency_threshold: float
         +error_threshold: int
         +on_event_callback(event)
     }

     class PerformanceProfilerPlugin {
         +profiles: List[Dict]
         +on_event_callback(event)
         +get_profile_summary()
     }

     BasePlugin <|-- MetricsCollectorPlugin
     BasePlugin <|-- AlertingPlugin
     BasePlugin <|-- PerformanceProfilerPlugin
     Agent --> BasePlugin : 使用
```

## 執行測試

```bash
# 執行所有測試並包含覆蓋率
make test

# 執行特定測試檔案
pytest tests/test_plugins.py -v

# 執行並顯示詳細輸出
pytest tests/ -vv --tb=long
```

## 核心概念

### 可觀測性支柱

1. **Traces (追蹤)**: 請求在系統中的流向
2. **Metrics (指標)**: 定量測量
3. **Logs (日誌)**: 詳細事件記錄
4. **Events (事件)**: 狀態變更與操作

### 外掛程式生命週期

1. `on_request_start()` - 請求開始
2. `on_tool_call_start()` - 工具執行開始
3. `on_tool_call_complete()` - 工具執行完成
4. `on_request_complete()` - 請求成功
5. `on_request_error()` - 請求失敗

### 收集的指標

- **請求指標**: 總數、成功率、延遲
- **效能**: Token 計數、工具呼叫持續時間
- **錯誤**: 錯誤率、連續失敗
- **警報**: 閾值違規、異常

## 生產環境部署

### Cloud Trace 設定

```bash
# 部署到 Cloud Run 並啟用追蹤
adk deploy cloud_run \
  --project your-project-id \
  --region us-central1 \
  --trace_to_cloud

# 部署到 Agent Engine
adk deploy agent_engine \
  --project your-project-id \
  --region us-central1 \
  --trace_to_cloud
```

### 監控儀表板

在 Cloud Console 中查看追蹤：
```
https://console.cloud.google.com/traces?project=your-project-id
```

## 疑難排解

### 常見問題

**外掛程式未運作？**
- 確保外掛程式已在 Runner/App 建構函式中註冊
- 檢查外掛程式生命週期方法是否正確實作

**未收集到指標？**
- 確認外掛程式在 plugins 列表中
- 檢查生命週期方法中的 async/await 語法

**Cloud Trace 未顯示？**
- 使用 `--trace_to_cloud` CLI 標誌
- 確保 Google Cloud 專案已設定
- 檢查 Cloud Trace 的 IAM 權限

## 資源

- [教學 24 文件](../../docs/tutorial/24_advanced_observability.md)
- [ADK 外掛程式系統](https://github.com/google/adk-python)
- [Cloud Trace 文件](https://cloud.google.com/trace/docs)
- [Prometheus 最佳實踐](https://prometheus.io/docs/practices/)
- [Basic Plugins 補充說明](./observability_plugins_agent/plugins.md)

---

# 重點摘要
- **核心概念**: 進階可觀測性與監控系統，整合 Cloud Trace。
- **關鍵技術**: Google ADK Plugin System, Cloud Trace, Metrics Collection, Alerting.
- **行動項目**: 實作自訂外掛程式，設定 Cloud Trace，部署至生產環境並監控。

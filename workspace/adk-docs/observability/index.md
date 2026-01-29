# Agent Observability & Analytics

可觀測性（Observability）是將 AI Agent 從原型推向生產環境的關鍵。Google ADK 提供了靈活的架構，支援多種可觀測性解決方案，幫助開發者進行除錯、效能評估、成本分析與行為監控。

本文檔提供 ADK 支援的各類可觀測性工具的技術選型指南，協助您根據專案需求選擇最合適的整合方案。

## 技術選型指南 (Selection Guide)

下表總結了各整合工具的關鍵特性，協助您快速進行技術選型：

| 工具名稱 | 部署模式 | 核心強項 | 整合標準 | 數據存儲 | 適用階段 | 連結 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AgentOps** | SaaS | 會話重播、成本追蹤 | SDK / Proprietary | Vendor Cloud | Dev & Prod | [查看](agentops.md) |
| **Arize AX** | SaaS | 企業級評估、監控 | OpenInference | Vendor Cloud | Production | [查看](arize-ax.md) |
| **BigQuery** | Cloud Native | 大數據分析、多模態 | Plugin / Native | User GCP (BQ) | Prod & Analytics | [查看](bigquery-agent-analytics.md) |
| **Cloud Trace** | Cloud Native | 分散式追蹤 | OpenTelemetry | User GCP | Production | [查看](cloud-trace.md) |
| **Freeplay** | SaaS | 提示詞管理、人工審閱 | SDK / Plugin | Vendor Cloud | Dev & Eval | [查看](freeplay.md) |
| **Monocle** | Local / OSS | 本地追蹤、VS Code 整合 | OpenTelemetry | Local JSON | Development | [查看](monocle.md) |
| **Phoenix** | Self / Cloud | 追蹤、評估 (OSS) | OpenInference | Local / Self | Dev & Eval | [查看](phoenix.md) |
| **MLflow** | Self-Hosted | 實驗追蹤 | OpenTelemetry | User SQL DB | Experimentation | [查看](mlflow.md) |
| **Weave** | SaaS | 模型調用記錄、時間軸 | OpenTelemetry | Vendor Cloud | Dev & Eval | [查看](weave.md) |
| **Logging** | Local | 基礎除錯 (純文字) | Python Native | Local / Stdout | Development | [查看](logging.md) |

## 整合工具詳解

### ☁️ SaaS 平台 (Managed Platforms)
這些平台提供開箱即用的儀表板與分析功能，適合希望快速獲得洞察且不想維護基礎設施的團隊。

- **[AgentOps](agentops.md)**: 提供直觀的會話重播 (Session Replay) 功能，只需兩行程式碼即可整合，特別適合分析 Agent 的實際互動流程與 Token 成本。
- **[Arize AX](arize-ax.md)**: 專注於 LLM 的評估與生產環境監控，適合需要大規模部署與企業級 SLA 的場景。
- **[Freeplay](freeplay.md)**: 強調「提示詞工程」與「人工審閱」的工作流，支援從 UI 直接更新 Prompt 到程式碼中，適合需要頻繁迭代 Prompt 的團隊。
- **[Weave (by WandB)](weave.md)**: 來自 Weights & Biases，提供強大的模型調用視覺化與時間軸檢視，適合已有使用 WandB 經驗的團隊。

### 🌩️ 雲端原生 (Google Cloud Native)
直接整合於 Google Cloud 生態系中，享有高安全性與擴展性。

- **[BigQuery Agent Analytics](bigquery-agent-analytics.md)**: **ADK 官方外掛**。將所有事件（含圖片、音訊）結構化存入 BigQuery，支援使用 SQL 進行深度分析，適合需要客製化報表與大規模數據分析的場景。
- **[Cloud Trace](cloud-trace.md)**: GCP 的分散式追蹤服務。適合用來分析 Agent 在微服務架構中的延遲瓶頸。

### 🛠️ 開源與自託管 (Open Source & Self-Hosted)
適合重視數據隱私、需要完全掌控數據或離線開發的場景。

- **[Monocle](monocle.md)**: 輕量級的本地追蹤工具，生成的 Trace 可直接透過 VS Code 擴充功能查看，開發體驗極佳。
- **[Phoenix](phoenix.md)**: Arize 的開源版本，提供強大的本地 Server 進行追蹤與評估 (Evals)，支援 OpenInference 標準。
- **[MLflow](mlflow.md)**: 機器學習領域的標準實驗追蹤工具，透過 OpenTelemetry 支援 LLM Trace，適合已有 MLflow 基礎設施的團隊。
- **[Logging](logging.md)**: ADK 內建的標準 Python Logging 機制，最基礎但也最通用的除錯方式。

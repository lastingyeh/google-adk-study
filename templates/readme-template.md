# RAG Agent with Document Retrieval using ADK Starter Pack

這是一個基於 ADK (Agent Development Kit) 的 RAG (Retrieval-Augmented Generation) 代理程式範本，專為文件檢索與問答場景設計。它包含完整的資料處理管道，能將文件擷取並索引至 Vertex AI Search 或 Vector Search，並透過生成式 AI 提供精準回答。

本專案基於 [`googleCloudPlatform/agent-starter-pack`](https://github.com/GoogleCloudPlatform/agent-starter-pack) 版本 `0.29.3` 建構。

---

## 目錄

1. [專案概述](#1-專案概述)
2. [核心架構解析](#2-核心架構解析)
3. [快速開始](#3-快速開始)
4. [專案結構](#4-專案結構)
5. [開發與使用指南](#5-開發與使用指南)
6. [部署說明](#6-部署說明)
7. [監控與可觀測性](#7-監控與可觀測性)

---

## 1. 專案概述

本專案整合了 **RAG (檢索增強生成)**、**Agent 開發框架**、**企業級安全**與**維運監控**等核心能力。它遵循「自備代理程式 (Bring Your Own Agent)」的方法，讓您專注於業務邏輯，而範本則處理 UI、基礎設施、部署與監控等繁瑣工作。

### 端到端工作流程
1. **知識準備**: 資料擷取管道 → BigQuery → Vertex AI Search
2. **代理開發**: 定義工具 & 指令 → 本機測試 → 品質檢查
3. **代理部署**: Terraform 佈建 → Cloud Run 部署 → 啟用監控
4. **安全加固**: IAP & WIF 配置 → IAM 權限 → 隱私模式
5. **運行優化**: 監控分析 → 迭代改進 → 實時知識更新

---

## 2. 核心架構解析

本專案從四個關鍵面向構建完整的企業級代理程式：

### 2.1 知識管理與 RAG (Knowledge Management)
核心是透過結構化的資料管道與智能檢索，為代理提供動態知識基礎。

- **資料管道 (Data Ingestion)**:
    - **來源**: BigQuery (如 StackOverflow 公開資料集)。
    - **處理**: HTML 轉 Markdown -> 文本分塊 (Chunking) -> 向量化 (Embedding)。
    - **儲存**: 生成 JSONL 並匯入 Vertex AI Search。
- **RAG 檢索流程**:
    - **查詢向量化**: 使用 `text-embedding-005` 模型。
    - **語義搜索**: Vertex AI Search 執行混合檢索。
    - **相關性重排**: Vertex AI Rank 重新排序結果 (Top N)。
    - **生成**: Gemini 模型結合檢索上下文生成回應。

### 2.2 代理運營 (Agent Operations)
負責代理程式的生命週期管理，確保高可用與可觀測性。
- **計算**: Cloud Run (無伺服器容器)。
- **存儲**: Cloud SQL (PostgreSQL) 用於對話狀態；GCS/BigQuery 用於日誌。
- **監控**: OpenTelemetry 分佈式追蹤 (Cloud Trace) + 集中式日誌 (Cloud Logging)。

### 2.3 代理安全 (Agent Security)
確保身份驗證、授權與數據隱私。
- **身份驗證**: Identity-Aware Proxy (IAP) 與 Workload Identity Federation (WIF)。
- **權限控制**: 基於最小權限原則的 IAM 角色配置。
- **隱私**: 支援「無內容記錄」模式，僅記錄元數據而不儲存敏感對話內容。

### 2.4 代理開發 (Agent Development)
利用 ADK 與 LangChain 生態加速開發。
- **核心**: Gemini 3.0 Flash 模型。
- **框架**: Google ADK + LangChain + FastAPI。
- **工具**: 完整的測試套件 (Pytest)、代碼檢查 (Ruff/MyPy) 與 Jupyter 筆記本原型環境。

---

## 3. 快速開始

### 環境需求
開始前請確保安裝以下工具：
- **uv**: Python 套件管理器 - [安裝說明](https://docs.astral.sh/uv/getting-started/installation/)
- **Google Cloud SDK**: GCP 命令行工具 - [安裝說明](https://cloud.google.com/sdk/docs/install)
- **Terraform**: 基礎設施即程式碼工具 - [安裝說明](https://developer.hashicorp.com/terraform/downloads)
- **make**: 自動化建置工具

### 本機啟動
1. **安裝依賴並啟動遊樂場**:
   ```bash
   make install && make playground
   ```
   此指令會安裝所有套件並啟動包含後端與前端的本機開發環境。

### 常用指令
| 指令 | 說明 |
|------|------|
| `make install` | 使用 uv 安裝所有相依性 |
| `make playground` | 啟動本機開發環境 (Web UI + Backend) |
| `make local-backend` | 僅啟動後端伺服器 (具備熱重載) |
| `make test` | 執行單元和整合測試 |
| `make lint` | 執行程式碼品質檢查 (codespell, ruff, mypy) |
| `make deploy` | 部署至 Cloud Run |
| `make data-ingestion` | 執行資料擷取管道 (開發環境) |

---

## 4. 專案結構

```text
├── app/                        # 代理程式核心邏輯
│   ├── agent.py                # 定義代理程式邏輯與工具
│   ├── retrievers.py           # RAG 檢索邏輯實作
│   ├── templates.py            # 前端 UI 模板
│   └── fast_api_app.py         # FastAPI 伺服器設定
├── data_ingestion/             # 資料擷取管道
│   ├── data_ingestion_pipeline # 管道核心邏輯與元件
│   └── pipeline.py             # Vertex AI Pipeline 定義
├── deployment/                 # 基礎設施設定 (Terraform)
│   ├── terraform/              # Terraform 模組與環境設定
│   └── ARCHI.md                # 架構說明文件
├── notebooks/                  # 原型設計與評估
│   ├── adk_app_testing.ipynb   # 應用程式測試
│   └── evaluating_adk_agent.ipynb # 效能評估
├── tests/                      # 測試目錄 (整合測試、負載測試)
├── Makefile                    # 專案指令定義
├── Dockerfile                  # 容器化設定
└── pyproject.toml              # Python 專案設定
```

---

## 5. 開發與使用指南

建議遵循以下流程進行開發：

1. **原型設計**:
   使用 `notebooks/` 中的 Jupyter Notebooks 快速實驗想法，並利用 Vertex AI Evaluation 評估效果。

2. **整合實作**:
   編輯 `app/agent.py` 將您的業務邏輯與工具整合進應用程式。若需調整 RAG 邏輯，請修改 `app/retrievers.py`。

3. **本機測試**:
   使用 `make playground` 在本機進行互動式測試。系統支援熱重載，程式碼變更會即時生效。

4. **品質保證**:
   執行 `make test` 與 `make lint` 確保程式碼品質與功能正確性。

5. **資料管道管理**:
   參考 `data_ingestion/README.md` 了解如何配置與執行資料索引管道，確保代理程式擁有最新知識。

---

## 6. 部署說明

本專案使用 Terraform 管理基礎設施。

### 開發環境部署
```bash
gcloud config set project <your-dev-project-id>
make setup-dev-env  # 設定基礎設施
make deploy         # 部署應用程式
```

### CI/CD 自動化
建議使用 `agent-starter-pack setup-cicd` CLI 指令來設定自動化的 CI/CD 管道 (支援 GitHub Actions 與 Cloud Build)。

詳細部署說明請參閱 [deployment/README.md](deployment/README.md)。

---

## 7. 監控與可觀測性

系統提供多層次的監控機制：

### 遙測與日誌
| 類型 | 工具 | 說明 | 預設狀態 |
|------|------|------|----------|
| **代理程式遙測** | Cloud Trace | OpenTelemetry 追蹤執行路徑與延遲 | ✅ 始終啟用 |
| **互動日誌** | Cloud Logging / BigQuery | 記錄 Prompt 與 Response (支援隱私過濾) | ❌ 本機停用 <br> ✅ 部署啟用 (僅元數據) |

**配置說明**:
- **本機啟用日誌**: 設定 `LOGS_BUCKET_NAME` 環境變數。
- **隱私設定**: 透過 `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` 控制是否記錄詳細對話內容。

更多詳情請參閱 [可觀測性指南](https://googlecloudplatform.github.io/agent-starter-pack/guide/observability.html)。

---

## 8. 參考資源
- [Agent Starter Pack 文件](https://googlecloudplatform.github.io/agent-starter-pack/)
- [Gemini CLI](https://github.com/google-gemini/gemini-cli) (專案內附 `GEMINI.md` 供 AI 輔助開發使用)

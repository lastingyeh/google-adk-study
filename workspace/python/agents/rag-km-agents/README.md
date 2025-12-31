# RAG Agent with Document Retrieval using ADK Starter Pack

用於文件檢索和問答的 ADK RAG 代理。包含一個資料管道，用於將文件擷取並索引到 Vertex AI Search 或 Vector Search。
代理程式使用 [`googleCloudPlatform/agent-starter-pack`](https://github.com/GoogleCloudPlatform/agent-starter-pack) 版本 `0.29.3` 產生

## 專案結構

此專案的組織結構如下：
```
├── Dockerfile                  # 用於將應用程式容器化的設定檔
├── GEMINI.md                   # 為 AI 工具 (如 Gemini CLI) 提供專案上下文的檔案
├── Makefile                    # 定義了專案的常用指令，如安裝、測試和部署
├── README.md                   # 專案的主要說明文件 (本檔案)
├── app                         # 主要代理程式 root-agent 應用程式核心邏輯的目錄
│   ├── __init__.py             # 將 `app` 目錄標示為 Python 套件
│   ├── agent.py                # 定義代理程式核心邏輯的地方
│   ├── app_utils               # 包含應用程式共用工具的目錄
│   │   ├── telemetry.py        # 處理遙測和監控的設定
│   │   └── typing.py           # 定義自訂型別提示
│   ├── fast_api_app.py         # 設定 FastAPI 網頁伺服器和端點
│   ├── retrievers.py           # 實現資料檢索邏輯
│   └── templates.py            # 包含 Jinja2 模板，用於前端 UI
├── data_ingestion              # 包含資料擷取管道相關程式碼的目錄
│   ├── README.md               # 資料擷取管道的說明文件
│   ├── data_ingestion_pipeline # 管道的核心邏輯
│   │   ├── components          # 管道的各個元件
│   │   │   ├── ingest_data.py  # 負責從來源擷取資料的元件
│   │   │   └── process_data.py # 負責處理和轉換資料的元件
│   │   ├── pipeline.py         # 定義 Vertex AI Pipeline 的工作流程
│   │   └── submit_pipeline.py  # 用於提交和執行管道的腳本
│   ├── pyproject.toml          # 資料擷取管道的 Python 專案設定檔
│   └── uv.lock                 # 鎖定資料擷取管道的 Python 相依性版本
├── deployment                  # 包含基礎設施即程式碼 (IaC) 設定的目錄
│   ├── ARCHI.md                # 專案架構圖和說明
│   ├── README.md               # 部署說明的詳細文件
│   └── terraform               # Terraform 設定檔，用於管理雲端資源
│       ├── apis.tf             # 管理需要啟用的 Google Cloud API
│       ├── dev                 # 開發環境專用的 Terraform 設定
│       │   ├── apis.tf         # 開發環境的 API 設定
│       │   ├── iam.tf          # 開發環境的 IAM 權限設定
│       │   ├── providers.tf    # 開發環境的 Terraform 提供者設定
│       │   ├── service.tf      # 開發環境的 Cloud Run 服務設定
│       │   ├── storage.tf      # 開發環境的儲存資源 (如 GCS) 設定
│       │   ├── telemetry.tf    # 開發環境的遙測和監控資源設定
│       │   ├── variables.tf    # 開發環境的 Terraform 變數定義
│       │   └── vars            # 存放開發環境變數值的目錄
│       │       └── env.tfvars  # 開發環境的變數檔案
│       ├── github.tf           # GitHub 與 GCP 整合的設定 (例如 CI/CD)
│       ├── iam.tf              # 通用的 IAM 權限設定
│       ├── locals.tf           # 定義本地變數以簡化設定
│       ├── providers.tf        # 設定 Terraform 提供者 (如 Google Cloud)
│       ├── service.tf          # Cloud Run 服務的通用設定
│       ├── service_accounts.tf # 設定服務帳戶
│       ├── sql                 # 存放 SQL 查詢的目錄
│       │   └── completions.sql # 用於 BigQuery 的範例 SQL 查詢
│       ├── storage.tf          # 儲存資源 (如 GCS) 的通用設定
│       ├── telemetry.tf        # 遙測和監控資源 (如 Logging, Tracing) 的通用設定
│       ├── variables.tf        # 通用的 Terraform 變數定義
│       ├── vars                # 存放通用變數值的目錄
│       │   └── env.tfvars      # 通用的變數檔案
│       └── wif.tf              # Workload Identity Federation 的設定
├── notebooks                   # 包含 Jupyter 筆記本，用於原型設計和測試
│   ├── adk_app_testing.ipynb   # 測試 ADK 應用程式的筆記本
│   └── evaluating_adk_agent.ipynb # 評估 ADK 代理程式效能的筆記本
├── pyproject.toml              # 專案的 Python 專案設定檔 (PEP 621)
├── tests                       # 包含所有測試程式碼的目錄
│   ├── integration             # 整合測試
│   │   ├── test_agent.py       # 測試代理程式與其他元件的整合
│   │   └── test_server_e2e.py  # 端對端伺服器測試
│   ├── load_test               # 負載測試
│   │   ├── README.md           # 負載測試說明文件
│   │   └── load_test.py        # 執行負載測試的腳本
│   └── unit                    # 單元測試
│       └── test_dummy.py       # 範例單元測試檔案
└── uv.lock                     # 鎖定專案的 Python 相依性版本
```

> 💡 **提示：** 使用 [Gemini CLI](https://github.com/google-gemini/gemini-cli) 進行 AI 輔助開發 - 專案上下文已在 `GEMINI.md` 中預先設定。

## 環境需求

在開始之前，請確保您已具備：

- **uv**：Python 套件管理器 (此專案中所有相依性管理皆使用此工具) - [安裝](https://docs.astral.sh/uv/getting-started/installation/) (使用 `uv add <package>` [新增套件](https://docs.astral.sh/uv/concepts/dependencies/))
- **Google Cloud SDK**：用於 GCP 服務 - [安裝](https://cloud.google.com/sdk/docs/install)
- **Terraform**：用於基礎設施部署 - [安裝](https://developer.hashicorp.com/terraform/downloads)
- **make**：建置自動化工具 - [安裝](https://www.gnu.org/software/make/) (在大多數 Unix-based 系統上已預先安裝)

## 快速入門 (本機測試)

安裝所需套件並啟動本機開發環境：

```bash
make install && make playground
```

> **📊 可觀測性說明：** 代理程式遙測 (Cloud Trace) 始終啟用。提示-回應記錄 (GCS、BigQuery、Cloud Logging) 在本機**預設停用**，在已部署的環境中**預設啟用** (僅限元資料 - 無提示/回應內容)。詳情請參閱 [監控與可觀測性](#監控與可觀測性)。

## 指令

| 指令                  | 說明                                                                                               |
| --------------------- | -------------------------------------------------------------------------------------------------- |
| `make install`        | 使用 uv 安裝所有必要的相依性                                                                       |
| `make playground`     | 啟動包含後端和前端的本機開發環境 - 利用 `adk web` 指令。                                           |
| `make deploy`         | 將代理程式部署到 Cloud Run (使用 `IAP=true` 啟用 Identity-Aware Proxy，`PORT=8080` 指定容器連接埠) |
| `make local-backend`  | 啟動具有熱重載功能的本機開發伺服器                                                                 |
| `make test`           | 執行單元和整合測試                                                                                 |
| `make lint`           | 執行程式碼品質檢查 (codespell, ruff, mypy)                                                         |
| `make setup-dev-env`  | 使用 Terraform 設定開發環境資源                                                                    |
| `make data-ingestion` | 在開發環境中執行資料擷取管道                                                                       |

有關完整的指令選項和用法，請參閱 [Makefile](Makefile)。

## 使用方式

此範本遵循「自備代理程式」的方法 - 您專注於您的業務邏輯，而範本處理其他所有事情 (UI、基礎設施、部署、監控)。

1. **原型設計：** 參考 `notebooks/` 中的入門筆記本，建構您的生成式 AI 代理程式。使用 Vertex AI Evaluation 評估效能。
2. **整合：** 編輯 `app/agent.py` 將您的代理程式匯入應用程式中。
3. **測試：** 使用 `make playground` 在本機遊樂場中探索您的代理程式功能。遊樂場會在程式碼變更時自動重新載入您的代理程式。
4. **部署：** 設定並啟動 CI/CD 管道，並根據需要自訂測試。有關詳細說明，請參閱 [部署部分](#部署)。若要簡化基礎設施部署，只需執行 `uvx agent-starter-pack setup-cicd`。請查看 [`agent-starter-pack setup-cicd` CLI 指令](https://googlecloudplatform.github.io/agent-starter-pack/cli/setup_cicd.html)。目前支援 GitHub，並可使用 Google Cloud Build 和 GitHub Actions 作為 CI/CD 執行器。
5. **監控：** 使用 BigQuery 遙測資料、Cloud Logging 和 Cloud Trace 追蹤效能並收集洞見，以迭代您的應用程式。

專案中包含一個 `GEMINI.md` 檔案，當您對範本提出問題時，它會為 Gemini CLI 等 AI 工具提供上下文。

## 部署

> **注意：** 若要使用 Terraform 透過單一指令簡化整個 CI/CD 管道和基礎設施的部署，您可以使用 [`agent-starter-pack setup-cicd` CLI 指令](https://googlecloudplatform.github.io/agent-starter-pack/cli/setup_cicd.html)。目前支援 GitHub，並可使用 Google Cloud Build 和 GitHub Actions 作為 CI/CD 執行器。

### 開發環境

您可以使用以下指令測試對開發環境的部署：

```bash
gcloud config set project <your-dev-project-id>
make deploy
```

此儲存庫包含用於設定開發 Google Cloud 專案的 Terraform 設定。
請參閱 [deployment/README.md](deployment/README.md) 以取得說明。

### 生產環境部署

此儲存庫包含用於設定生產 Google Cloud 專案的 Terraform 設定。有關如何部署基礎設施和應用程式的詳細說明，請參閱 [deployment/README.md](deployment/README.md)。

## 監控與可觀測性

應用程式提供兩個層級的可觀測性：

**1. 代理程式遙測事件 (始終啟用)**

- OpenTelemetry 追蹤和跨度匯出至 **Cloud Trace**
- 追蹤代理程式執行、延遲和系統指標

**2. 提示-回應記錄 (可設定)**

- GenAI 檢測工具會擷取 LLM 互動 (權杖、模型、時間)
- 匯出至 **Google Cloud Storage** (JSONL)、**BigQuery** (外部資料表) 和 **Cloud Logging** (專用儲存桶)

| 環境                             | 提示-回應記錄                                        |
| -------------------------------- | ---------------------------------------------------- |
| **本機開發** (`make playground`) | ❌ 預設停用                                           |
| **已部署環境** (透過 Terraform)  | ✅ **預設啟用** (保護隱私：僅元資料，無提示/回應內容) |

**若要在本機啟用：** 設定 `LOGS_BUCKET_NAME` 和 `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=NO_CONTENT`。

**若要在部署中停用：** 編輯 Terraform 設定，將 `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=false`。

有關詳細說明、範例查詢和視覺化選項，請參閱[可觀測性指南](https://googlecloudplatform.github.io/agent-starter-pack/guide/observability.html)。

### 內容完整說明

這份導讀將幫助您快速了解專案的各個重要部分：

- **專案根目錄**：從[**專案主說明文件 (README.md)**](README.md)開始，這裡提供了專案的整體結構、快速入門指南以及核心指令。
- **資料擷取**：如果您想了解資料如何被處理、轉換並載入至 Vertex AI Search，請參閱**[**資料擷取管道說明 (data_ingestion/README.md)**](data_ingestion/README.md)。其中包含了詳細的流程圖與元件說明。
- **部署與架構**：關於專案的雲端基礎設施、開發與生產環境的架構圖，以及如何使用 Terraform 進行部署的資訊，都可以在[**部署說明文件 (deployment/README.md)**](deployment/README.md)中找到。
- **負載測試**：若您需要對應用程式進行壓力測試，[**負載測試指南 (tests/load_test/README.md)**](tests/load_test/README.md)提供了使用 Locust 進行本地和遠端測試的詳細步驟。
- **環境變數**：有關可用環境變數的完整列表及其說明，請參閱[**環境變數說明文件 (VARS.md)**](VARS.md)。

---
### 參考資源
- [Agent Starter Pack 文件](https://googlecloudplatform.github.io/agent-starter-pack/)
- [ADK GitHub 儲存庫](https://github.com/GoogleCloudPlatform/agent-starter-pack)
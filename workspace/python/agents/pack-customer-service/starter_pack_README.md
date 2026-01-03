# pack-customer-service

使用 Agent Development Kit 的客戶服務演示
由 [`googleCloudPlatform/agent-starter-pack`](https://github.com/GoogleCloudPlatform/agent-starter-pack) 版本 `0.20.4` 生成的 Agent

## 專案結構

本專案組織如下：

```
pack-customer-service/
├── customer_service/    # 核心應用程式代碼
│   ├── agent.py         # 主要 Agent 邏輯
│   ├── fast_api_app.py  # FastAPI 後端伺服器
│   └── app_utils/       # 應用程式工具和輔助程式
├── .cloudbuild/         # Google Cloud Build 的 CI/CD 流程配置
├── deployment/          # 基礎架構和部署腳本
├── notebooks/           # 用於原型設計和評估的 Jupyter notebooks
├── tests/               # 單元測試、整合測試和負載測試
├── Makefile             # 常用指令的 Makefile
├── GEMINI.md            # AI 輔助開發指南
└── pyproject.toml       # 專案依賴和配置
```

## 需求

在開始之前，請確保您已安裝：
- **uv**: Python 套件管理器（本專案用於所有依賴管理）- [安裝](https://docs.astral.sh/uv/getting-started/installation/) (使用 `uv add <package>` [新增套件](https://docs.astral.sh/uv/concepts/dependencies/))
- **Google Cloud SDK**: 用於 GCP 服務 - [安裝](https://cloud.google.com/sdk/docs/install)
- **Terraform**: 用於基礎架構部署 - [安裝](https://developer.hashicorp.com/terraform/downloads)
- **make**: 建置自動化工具 - [安裝](https://www.gnu.org/software/make/) (大多數 Unix 系統已預裝)


## 快速開始（本地測試）

安裝所需套件並啟動本地開發環境：

```bash
make install && make playground
```

## 指令

| 指令 | 描述 |
| -------------------- | ------------------------------------------------------------------------------------------- |
| `make install`       | 使用 uv 安裝所有必要的依賴項 |
| `make playground`    | 啟動包含後端和前端的本地開發環境 - 利用 `adk web` 指令。|
| `make deploy`        | 將 Agent 部署到 Cloud Run (使用 `IAP=true` 啟用 Identity-Aware Proxy，`PORT=8080` 指定容器連接埠) |
| `make local-backend` | 啟動具有熱重載功能的本地開發伺服器 |
| `make test`          | 執行單元測試和整合測試 |
| `make lint`          | 執行代碼品質檢查 (codespell, ruff, mypy) |
| `make setup-dev-env` | 使用 Terraform 設置開發環境資源 |

有關完整的指令選項和用法，請參閱 [Makefile](Makefile)。


## 使用方法

此範本採用「自帶 Agent (bring your own agent)」的方法 - 您專注於業務邏輯，範本處理其他所有事務（UI、基礎架構、部署、監控）。

1. **原型設計 (Prototype):** 使用 `notebooks/` 中的介紹性 notebooks 作為指導來構建您的生成式 AI Agent。使用 Vertex AI Evaluation 來評估效能。
2. **整合 (Integrate):** 通過編輯 `customer_service/agent.py` 將您的 Agent 匯入應用程式中。
3. **測試 (Test):** 使用 `make playground` 透過 Streamlit playground 探索您的 Agent 功能。Playground 提供聊天記錄、使用者回饋和各種輸入類型等功能，並會在代碼變更時自動重新載入您的 Agent。
4. **部署 (Deploy):** 設置並啟動 CI/CD 流程，並根據需要自定義測試。請參閱 [部署部分](#deployment) 以獲取完整說明。要簡化基礎架構部署，只需執行 `uvx agent-starter-pack setup-cicd`。查看 [`agent-starter-pack setup-cicd` CLI 指令](https://googlecloudplatform.github.io/agent-starter-pack/cli/setup_cicd.html)。目前支援 GitHub 以及 Google Cloud Build 和 GitHub Actions 作為 CI/CD 執行器。
5. **監控 (Monitor):** 使用 Cloud Logging、Tracing 和 Looker Studio 儀表板追蹤效能並收集見解，以迭代您的應用程式。

專案包含一個 `GEMINI.md` 文件，當使用 Gemini CLI 等 AI 工具詢問有關範本的問題時，該文件可提供上下文。


## 部署

> **注意：** 若要使用 Terraform 透過單一指令簡化整個 CI/CD 流程和基礎架構的部署，您可以使用 [`agent-starter-pack setup-cicd` CLI 指令](https://googlecloudplatform.github.io/agent-starter-pack/cli/setup_cicd.html)。目前支援 GitHub 以及 Google Cloud Build 和 GitHub Actions 作為 CI/CD 執行器。

### 開發環境 (Dev Environment)

您可以使用以下指令測試部署到開發環境：

```bash
gcloud config set project <your-dev-project-id>
make deploy
```


儲存庫包含用於設置開發 Google Cloud 專案的 Terraform 配置。
請參閱 [deployment/README.md](deployment/README.md) 以獲取說明。

### 生產部署 (Production Deployment)

儲存庫包含用於設置生產 Google Cloud 專案的 Terraform 配置。請參閱 [deployment/README.md](deployment/README.md) 以獲取有關如何部署基礎架構和應用程式的詳細說明。


## 監控和可觀測性
> 您可以使用 [此 Looker Studio 儀表板](https://lookerstudio.google.com/reporting/46b35167-b38b-4e44-bd37-701ef4307418/page/tEnnC
) 範本來視覺化記錄在 BigQuery 中的事件。請參閱「設定說明 (Setup Instructions)」標籤頁以開始使用。

本應用程式使用 OpenTelemetry 進行全面的可觀測性，所有事件都會發送到 Google Cloud Trace 和 Logging 進行監控，並發送到 BigQuery 進行長期儲存。

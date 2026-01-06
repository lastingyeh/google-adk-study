# Policy As Code Agent

Policy-as-Code Agent 是一款由生成式 AI 驅動的工具，可自動化資料治理。
本代理程式由 [`googleCloudPlatform/agent-starter-pack`](https://github.com/GoogleCloudPlatform/agent-starter-pack) 版本 `0.29.3` 產生。


## 專案結構

本專案結構如下：

```
pack-policy-as-code/
├── policy_as_code_agent/# 核心應用程式程式碼
│   ├── agent.py         # 主要代理程式邏輯
│   ├── fast_api_app.py  # FastAPI 後端伺服器
│   └── app_utils/       # 應用程式工具與輔助程式
├── .cloudbuild/         # Google Cloud Build CI/CD 管線設定
├── deployment/          # 基礎設施與部署腳本
├── notebooks/           # Jupyter 筆記本，用於原型設計與評估
├── tests/               # 單元、整合與負載測試
├── Makefile             # 常用指令的 Makefile
├── GEMINI.md            # AI 協作開發指南
└── pyproject.toml       # 專案依賴與設定
```

> 💡 **提示：** 使用 [Gemini CLI](https://github.com/google-gemini/gemini-cli) 進行 AI 協作開發，專案上下文已預設於 `GEMINI.md`。


## 環境需求

開始前請確認已安裝以下工具：
- **uv**：Python 套件管理工具（本專案所有依賴均由 uv 管理） - [安裝教學](https://docs.astral.sh/uv/getting-started/installation/)（[新增套件](https://docs.astral.sh/uv/concepts/dependencies/) 使用 `uv add <package>`）
- **Google Cloud SDK**：GCP 服務工具 - [安裝教學](https://cloud.google.com/sdk/docs/install)
- **Terraform**：基礎設施部署工具 - [安裝教學](https://developer.hashicorp.com/terraform/downloads)
- **make**：建置自動化工具 - [安裝教學](https://www.gnu.org/software/make/)（大多數 Unix 系統預設安裝）

## 快速開始（本機測試）

安裝必要套件並啟動本機開發環境：

```bash
make install && make playground
```
> **📊 觀測性說明：** Agent telemetry（Cloud Trace）永遠啟用。Prompt-response logging（GCS、BigQuery、Cloud Logging）本機預設停用，部署環境預設啟用（僅記錄 metadata，不含 prompt/response）。詳見 [監控與觀測性](#monitoring-and-observability)。


## 指令總覽

| 指令                 | 說明                                                                                          |
| -------------------- | --------------------------------------------------------------------------------------------- |
| `make install`       | 使用 uv 安裝所有必要依賴                                                                      |
| `make playground`    | 啟動本機開發環境（後端與前端），利用 `adk web` 指令                                           |
| `make deploy`        | 部署代理程式至 Cloud Run（可用 `IAP=true` 啟用 Identity-Aware Proxy，`PORT=8080` 指定容器埠） |
| `make local-backend` | 啟動本機後端伺服器並支援熱重載                                                                |
| `make test`          | 執行單元測試與整合測試                                                                        |
| `make lint`          | 執行程式碼品質檢查（codespell, ruff, mypy）                                                   |
| `make setup-dev-env` | 使用 Terraform 建立開發環境資源                                                               |

完整指令與用法請參考 [Makefile](Makefile)。

## 使用方式

本範本採「自帶代理程式」設計，你專注於商業邏輯，範本自動處理 UI、基礎設施、部署、監控。
1. **Prototype：** 於 `notebooks/` 目錄使用入門筆記本開發生成式 AI 代理程式，並利用 Vertex AI Evaluation 評估效能。
2. **Integrate：** 編輯 `policy_as_code_agent/agent.py` 匯入你的代理程式。
3. **Test：** 以 `make playground` 測試代理程式功能，支援程式碼變更自動重載。
4. **Deploy：** 建立並啟動 CI/CD 流程，根據需求自訂測試。詳見 [部署說明](#deployment)。基礎設施快速部署可用 `uvx agent-starter-pack setup-cicd`。參考 [`agent-starter-pack setup-cicd` CLI 指令](https://googlecloudplatform.github.io/agent-starter-pack/cli/setup_cicd.html)。目前支援 GitHub，CI/CD 執行器包含 Google Cloud Build 與 GitHub Actions。
5. **Monitor：** 利用 BigQuery telemetry、Cloud Logging、Cloud Trace 追蹤效能並優化應用。

專案內含 `GEMINI.md`，可供 Gemini CLI 等 AI 工具查詢範本上下文。


## 部署說明

> **注意：** 可用 [`agent-starter-pack setup-cicd` CLI 指令](https://googlecloudplatform.github.io/agent-starter-pack/cli/setup_cicd.html) 一鍵部署完整 CI/CD 流程與基礎設施。現支援 GitHub，CI/CD 執行器包含 Google Cloud Build 與 GitHub Actions。

### 開發環境

可用以下指令測試部署至開發環境：

```bash
gcloud config set project <your-dev-project-id>
make deploy
```

本儲存庫已包含 Terraform 設定檔，可協助建立 Dev Google Cloud 專案。
詳見 [deployment/README.md](deployment/README.md) 取得詳細說明。


### 正式環境部署

本儲存庫已包含正式環境的 Terraform 設定檔。請參考 [deployment/README.md](deployment/README.md) 取得詳細部署與基礎設施說明。

## 監控與觀測性

本應用程式提供兩層級的觀測性：

**1. Agent Telemetry Events（永遠啟用）**
- OpenTelemetry traces 與 spans 匯出至 **Cloud Trace**
- 追蹤代理程式執行、延遲與系統指標

**2. Prompt-Response Logging（可設定）**
- GenAI 工具記錄 LLM 互動（tokens、model、timing）
- 匯出至 **Google Cloud Storage**（JSONL）、**BigQuery**（external tables）、**Cloud Logging**（dedicated bucket）

| 環境                                      | Prompt-Response Logging                                           |
| ----------------------------------------- | ----------------------------------------------------------------- |
| **Local Development** (`make playground`) | ❌ 預設停用                                                        |
| **Deployed Environments** (via Terraform) | ✅ **預設啟用**（隱私保護：僅記錄 metadata，不含 prompt/response） |

**本機啟用方式：** 設定 `LOGS_BUCKET_NAME` 並將 `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=NO_CONTENT`。

**部署環境停用方式：** 編輯 Terraform 設定檔，將 `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=false`。

詳見 [觀測性指南](https://googlecloudplatform.github.io/agent-starter-pack/guide/observability.html) 取得詳細教學、查詢範例與視覺化方式。

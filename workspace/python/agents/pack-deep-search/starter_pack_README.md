# pack-deep-search

一個可用於生產環境的全端研究代理，利用 Gemini 進行策略規劃、研究與綜合報告，並支援人機協作。
代理由 [`googleCloudPlatform/agent-starter-pack`](https://github.com/GoogleCloudPlatform/agent-starter-pack) 版本 `0.29.4` 產生。

## 專案結構

本專案結構如下：

```
pack-deep-search/
├── app/                 # 核心應用程式碼
│   ├── agent.py         # 主要代理邏輯
│   ├── fast_api_app.py  # FastAPI 後端伺服器
│   └── app_utils/       # 應用程式工具與輔助程式
├── .cloudbuild/         # Google Cloud Build CI/CD 管線設定
├── deployment/          # 基礎設施與部署腳本
├── notebooks/           # Jupyter 筆記本，用於原型設計與評估
├── tests/               # 單元、整合與負載測試
├── Makefile             # 常用指令的 Makefile
├── GEMINI.md            # AI 協作開發指南
└── pyproject.toml       # 專案相依性與設定
```

> 💡 **提示：** 使用 [Gemini CLI](https://github.com/google-gemini/gemini-cli) 進行 AI 協作開發，專案上下文已預先設定於 `GEMINI.md`。

## 需求

開始前，請確保你已安裝：
- **uv**：Python 套件管理工具（本專案所有相依性管理皆使用 uv）
  - [安裝說明](https://docs.astral.sh/uv/getting-started/installation/)（[新增套件](https://docs.astral.sh/uv/concepts/dependencies/) 請用 `uv add <package>`）
- **Google Cloud SDK**：使用 GCP 服務 - [安裝說明](https://cloud.google.com/sdk/docs/install)
- **Terraform**：基礎設施部署 - [安裝說明](https://developer.hashicorp.com/terraform/downloads)
- **make**：建置自動化工具 - [安裝說明](https://www.gnu.org/software/make/)（大多數 Unix 系統預設已安裝）


## 快速開始（本地測試）

安裝所需套件並啟動本地開發環境：

```bash
make install && make playground
```
> **📊 可觀測性說明：** 代理遙測（Cloud Trace）始終啟用。提示-回應日誌（GCS、BigQuery、Cloud Logging）本地預設關閉，部署環境預設開啟（僅記錄中繼資料，不含提示/回應內容）。詳見 [監控與可觀測性](#monitoring-and-observability)。

## 指令

| 指令                  | 說明                                                                                 |
| --------------------- | ------------------------------------------------------------------------------------ |
| `make install`        | 使用 uv 安裝所有相依套件                                                             |
| `make playground`     | 啟動本地開發環境（後端與前端），使用 `adk web` 指令                                  |
| `make deploy`         | 部署代理至 Cloud Run（可用 `IAP=true` 啟用 Identity-Aware Proxy，`PORT=8080` 指定容器埠）|
| `make local-backend`  | 啟動本地開發伺服器，支援 hot-reload                                                  |
| `make test`           | 執行單元與整合測試                                                                   |
| `make lint`           | 執行程式碼品質檢查（codespell、ruff、ty）                                             |
| `make setup-dev-env`  | 使用 Terraform 建立開發環境資源                                                      |

完整指令與用法請參考 [Makefile](Makefile)。

## 使用方式

本範本採「自帶代理」模式——你專注於業務邏輯，其餘（UI、基礎設施、部署、監控）皆由範本處理。
1. **原型設計：** 於 `notebooks/` 內的入門筆記本設計你的生成式 AI 代理，並用 Vertex AI Evaluation 評估效能。
2. **整合：** 編輯 `app/agent.py` 將你的代理導入應用程式。
3. **測試：** 使用 `make playground` 啟動本地 playground 測試代理功能，程式碼變更會自動重新載入。
4. **部署：** 設定並啟動 CI/CD 管線，並依需求自訂測試。詳見 [部署章節](#deployment)。如需快速部署基礎設施，可執行 `uvx agent-starter-pack setup-cicd`。參考 [`agent-starter-pack setup-cicd` CLI 指令](https://googlecloudplatform.github.io/agent-starter-pack/cli/setup_cicd.html)。目前支援 GitHub，CI/CD 執行器可選 Google Cloud Build 或 GitHub Actions。
5. **監控：** 透過 BigQuery 遙測資料、Cloud Logging 與 Cloud Trace 追蹤效能並優化應用程式。

專案內的 `GEMINI.md` 提供 Gemini CLI 等 AI 工具的上下文說明。

## 部署

> **注意：** 若需一鍵部署完整 CI/CD 管線與基礎設施（Terraform），可使用 [`agent-starter-pack setup-cicd` CLI 指令](https://googlecloudplatform.github.io/agent-starter-pack/cli/setup_cicd.html)。目前支援 GitHub，CI/CD 執行器可選 Google Cloud Build 或 GitHub Actions。

### 開發環境

可用下列指令部署至開發環境：

```bash
gcloud config set project <your-dev-project-id>
make deploy
```

本儲存庫已包含 Terraform 設定檔，可用於建立 Dev Google Cloud 專案。
詳見 [deployment/README.md](deployment/README.md)。

### 正式環境部署

本儲存庫已包含 Terraform 設定檔，可用於建立正式 Google Cloud 專案。請參考 [deployment/README.md](deployment/README.md) 取得詳細部署說明。

## 監控與可觀測性

本應用程式提供兩層級的可觀測性：

**1. 代理遙測事件（始終啟用）**
- OpenTelemetry traces 與 spans 匯出至 **Cloud Trace**
- 追蹤代理執行、延遲與系統指標

**2. 提示-回應日誌（可設定）**
- GenAI 工具記錄 LLM 互動（tokens、模型、時間）
- 匯出至 **Google Cloud Storage**（JSONL）、**BigQuery**（外部資料表）、**Cloud Logging**（專屬 bucket）

| 環境 | 提示-回應日誌 |
|------|---------------|
| **本地開發**（`make playground`） | ❌ 預設關閉 |
| **部署環境**（Terraform 部署） | ✅ **預設開啟**（隱私保護：僅記錄中繼資料，不含提示/回應內容） |

**本地啟用方式：** 設定 `LOGS_BUCKET_NAME` 並將 `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=NO_CONTENT`。

**部署環境停用方式：** 編輯 Terraform 設定，將 `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=false`。

詳見 [可觀測性指南](https://googlecloudplatform.github.io/agent-starter-pack/guide/observability.html) 取得詳細說明、查詢範例與視覺化方式。

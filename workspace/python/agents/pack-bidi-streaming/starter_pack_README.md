
# pack-bidi-streaming

<!--
本檔案為 ADK Bidi-streaming 範例應用程式之說明文件。
由 [`googleCloudPlatform/agent-starter-pack`](https://github.com/GoogleCloudPlatform/agent-starter-pack) 版本 `0.33.0` 產生。
-->

ADK Bidi-streaming 範例應用程式
代理程式由 [`googleCloudPlatform/agent-starter-pack`](https://github.com/GoogleCloudPlatform/agent-starter-pack) 版本 `0.33.0` 產生

## 專案結構

<!--
說明專案目錄結構與各資料夾/檔案用途。
-->
```
pack-bidi-streaming/
├── bidi_demo/         # 核心代理程式碼
│   ├── agent.py               # 主要代理邏輯
│   ├── fast_api_app.py        # FastAPI 後端伺服器
│   └── app_utils/             # 應用程式工具與輔助程式
├── .cloudbuild/               # Google Cloud Build CI/CD 管線設定
├── deployment/                # 基礎建設與部署腳本
├── notebooks/                 # Jupyter 筆記本，原型設計與評估
├── tests/                     # 單元、整合與負載測試
├── GEMINI.md                  # AI 輔助開發指南
├── Makefile                   # 開發指令
└── pyproject.toml             # 專案相依套件
```

> 💡 **提示：** 建議使用 [Gemini CLI](https://github.com/google-gemini/gemini-cli) 進行 AI 輔助開發，專案上下文已預先設定於 `GEMINI.md`。

## 環境需求

<!--
列出開始前需安裝的工具與其用途。
-->
開始前請確保已安裝：
- **uv**：Python 套件管理工具（本專案所有相依套件皆以 uv 管理） - [安裝說明](https://docs.astral.sh/uv/getting-started/installation/)（[新增套件](https://docs.astral.sh/uv/concepts/dependencies/)請用 `uv add <package>`）
- **Google Cloud SDK**：GCP 服務工具 - [安裝說明](https://cloud.google.com/sdk/docs/install)
- **Terraform**：基礎建設部署工具 - [安裝說明](https://developer.hashicorp.com/terraform/downloads)
- **make**：建置自動化工具 - [安裝說明](https://www.gnu.org/software/make/)（大多數 Unix 系統預設已安裝）

## 快速開始

<!--
說明如何安裝相依套件並啟動本地開發環境。
-->
安裝所需套件並啟動本地開發環境：

```bash
make install && make playground
```
> **📊 可觀測性說明：** 代理遙測（Cloud Trace）永遠啟用。提示-回應紀錄（GCS、BigQuery、Cloud Logging）本地預設停用，部署環境預設啟用（僅記錄中繼資料，不含提示/回應內容）。詳見[監控與可觀測性](#監控與可觀測性)。

## 指令說明

<!--
列出常用 make 指令與說明。
-->
| 指令                 | 說明                             |
| -------------------- | -------------------------------- |
| `make install`       | 使用 uv 安裝相依套件             |
| `make playground`    | 啟動本地開發環境                 |
| `make lint`          | 執行程式碼品質檢查               |
| `make test`          | 執行單元與整合測試               |
| `make deploy`        | 部署代理至 Cloud Run             |
| `make local-backend` | 啟動本地後端伺服器（支援熱重載） |
| `make setup-dev-env` | 使用 Terraform 建立開發環境資源  |

完整指令與用法請參閱 [Makefile](Makefile)。

## 使用方式

<!--
說明開發流程與各步驟。
-->
本範本採「自帶代理」模式——您專注於業務邏輯，範本處理 UI、基礎建設、部署與監控。
1. **原型設計：** 於 `notebooks/` 內的 Jupyter 筆記本設計生成式 AI 代理，並用 Vertex AI Evaluation 評估效能。
2. **整合：** 編輯 `bidi_demo/agent.py` 匯入您的代理。
3. **測試：** 使用 `make playground` 啟動本地 playground 測試代理功能，支援程式碼熱重載。
4. **部署：** 設定並啟動 CI/CD 管線，可依需求自訂測試。詳見[部署說明](#部署)。如需快速部署基礎建設，可執行 `uvx agent-starter-pack setup-cicd`。參考 [`agent-starter-pack setup-cicd` CLI 指令](https://googlecloudplatform.github.io/agent-starter-pack/cli/setup_cicd.html)。目前支援 GitHub，CI/CD 執行器可選 Google Cloud Build 或 GitHub Actions。
5. **監控：** 利用 BigQuery 遙測資料、Cloud Logging 與 Cloud Trace 追蹤效能並優化應用。

專案內含 `GEMINI.md`，可供 Gemini CLI 等 AI 工具查詢專案上下文。

## 部署

<!--
說明如何一鍵部署 CI/CD 與基礎建設。
-->
> **注意：** 可用 [`agent-starter-pack setup-cicd` CLI 指令](https://googlecloudplatform.github.io/agent-starter-pack/cli/setup_cicd.html) 一鍵部署完整 CI/CD 管線與基礎建設。目前支援 GitHub，CI/CD 執行器可選 Google Cloud Build 或 GitHub Actions。

### 開發環境部署

可用下列指令部署至開發環境：

```bash
gcloud config set project <your-dev-project-id>
make deploy
```

本儲存庫已包含 Terraform 設定檔，可用於建立 Dev Google Cloud 專案。
詳見 [deployment/README.md](deployment/README.md)。

### 正式環境部署

本儲存庫亦包含正式環境的 Terraform 設定檔。請參閱 [deployment/README.md](deployment/README.md) 取得詳細部署說明。

## 監控與可觀測性

<!--
說明遙測與提示-回應紀錄的啟用方式與差異。
-->
本應用提供兩層級可觀測性：

**1. 代理遙測事件（永遠啟用）**
- OpenTelemetry 追蹤與 span 匯出至 **Cloud Trace**
- 追蹤代理執行、延遲與系統指標

**2. 提示-回應紀錄（可設定）**
- GenAI 工具記錄 LLM 互動（token、模型、時間）
- 匯出至 **Google Cloud Storage**（JSONL）、**BigQuery**（外部表）、**Cloud Logging**（專屬 bucket）

| 環境                             | 提示-回應紀錄                                                 |
| -------------------------------- | ------------------------------------------------------------- |
| **本地開發** (`make playground`) | ❌ 預設停用                                                    |
| **部署環境** (Terraform)         | ✅ **預設啟用**（隱私保護：僅記錄中繼資料，不含提示/回應內容） |

**本地啟用方式：** 設定 `LOGS_BUCKET_NAME` 與 `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=NO_CONTENT`。

**部署環境停用方式：** 編輯 Terraform 設定檔，將 `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=false`。

詳見[可觀測性指南](https://googlecloudplatform.github.io/agent-starter-pack/guide/observability.html)，內含詳細說明、查詢範例與視覺化方式。

## 保持最新

<!--
說明如何升級範本版本並保留自訂內容。
-->
如需升級至最新版 agent-starter-pack：

```bash
uvx agent-starter-pack upgrade
```

此指令會智慧合併更新並保留您的自訂內容。可加上 `--dry-run` 預覽變更。詳見 [升級 CLI 說明](https://googlecloudplatform.github.io/agent-starter-pack/cli/upgrade.html)。

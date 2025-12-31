# live-interact-agent

使用 ADK 和 Gemini Live API 的即時多模態代理，可實現低延遲的語音和視訊互動。
代理程式使用 [`googleCloudPlatform/agent-starter-pack`](https://github.com/GoogleCloudPlatform/agent-starter-pack) 版本 `0.29.3` 產生

## 專案結構

本專案的組織結構如下：

```
live-interact-agent/
├── app/                 # 核心應用程式碼
│   ├── agent.py         # 主要代理邏輯
│   ├── fast_api_app.py  # FastAPI 後端伺服器
│   └── app_utils/       # 應用程式工具和輔助函式
├── .cloudbuild/         # Google Cloud Build 的 CI/CD 管線設定
├── deployment/          # 基礎架構和部署腳本
├── tests/               # 單元、整合和負載測試
├── Makefile             # 用於常見指令的 Makefile
├── GEMINI.md            # AI 輔助開發指南
└── pyproject.toml       # 專案依賴項和設定
```

> 💡 **提示：** 使用 [Gemini CLI](https://github.com/google-gemini/gemini-cli) 進行 AI 輔助開發 - 專案上下文已在 `GEMINI.md` 中預先設定。

## 需求

在開始之前，請確保您已具備：

- **uv**：Python 套件管理器（本專案中所有依賴項管理都使用它） - [安裝](https://docs.astral.sh/uv/getting-started/installation/)（使用 `uv add <package>` [新增套件](https://docs.astral.sh/uv/concepts/dependencies/)）
- **Google Cloud SDK**：用於 GCP 服務 - [安裝](https://cloud.google.com/sdk/docs/install)
- **Terraform**：用於基礎架構部署 - [安裝](https://developer.hashicorp.com/terraform/downloads)
- **make**：建置自動化工具 - [安裝](https://www.gnu.org/software/make/)（預先安裝在大多數 Unix-based 系統上）

## 快速入門（本機測試）

安裝所需套件並啟動本機開發環境：

```bash
# 安裝所有必要的相依套件，並啟動本機的開發遊樂場環境
make install && make playground
```

> **📊 可觀測性說明：** 代理程式遙測（Cloud Trace）始終啟用。提示-回應記錄（GCS、BigQuery、Cloud Logging）在本機 **停用**，在已部署的環境中 **預設啟用**（僅元數據 - 無提示/回應）。詳情請參閱 [監控與可觀測性](#monitoring-and-observability)。

## 指令

| 指令                 | 說明                                                                                                |
| -------------------- | --------------------------------------------------------------------------------------------------- |
| `make install`       | 使用 uv 安裝所有必要的依賴項                                                                        |
| `make playground`    | 啟動包含後端和前端的本機開發環境 - 利用 `adk web` 指令。                                            |
| `make deploy`        | 將代理程式部署到 Cloud Run（使用 `IAP=true` 啟用 Identity-Aware Proxy，`PORT=8080` 指定容器連接埠） |
| `make local-backend` | 啟動具有熱重載功能的本機開發伺服器                                                                  |
| `make test`          | 執行單元和整合測試                                                                                  |
| `make lint`          | 執行程式碼品質檢查（codespell、ruff、mypy）                                                         |
| `make setup-dev-env` | 使用 Terraform 設定開發環境資源                                                                     |

有關完整的指令選項和用法，請參閱 [Makefile](Makefile)。

## 用法

此範本遵循「自備代理」的方法 - 您專注於 `app/agent.py` 中的業務邏輯，而範本會處理周邊的元件（UI、基礎架構、部署、監控）。

以下是建議的本機開發工作流程：

1.  **安裝依賴項（如果需要）：**

    ```bash
    # 執行 make install 來安裝所有必要的相依套件
    make install
    ```

2.  **啟動全端伺服器：**
    FastAPI 伺服器現在同時提供後端 API 和前端介面：

    ```bash
    # 啟動本地後端伺服器
    make local-backend
    ```

    當您看到 `INFO:     Application startup complete.` 時，表示伺服器已準備就緒。前端將在 `http://localhost:8000` 上可用。

    <details>
    <summary><b>可選：使用 AI Studio / API 金鑰而非 Vertex AI</b></summary>

    預設情況下，後端使用 Vertex AI 和應用程式預設憑證。如果您偏好使用 Google AI Studio 和 API 金鑰：

    ```bash
    # 設定環境變數，不使用 Vertex AI
    export VERTEXAI=false
    # 設定您的 Google API 金鑰
    export GOOGLE_API_KEY="your-google-api-key" # 請替換為您的實際金鑰
    # 啟動本地後端伺服器
    make local-backend
    ```

    請確保在您的環境中正確設定 `GOOGLE_API_KEY`。
    </details>
    <br>

    <details>
    <summary><b>替代方案：單獨執行前端</b></summary>

    如果您偏好單獨執行前端（這對前端開發很有用），您仍然可以使用：

    ```bash
    # 啟動使用者介面
    make ui
    ```

    這會啟動前端應用程式，它會連接到 `http://localhost:8000` 的後端伺服器。
    </details>
    <br>

3.  **互動與迭代：**
    - 開啟您的瀏覽器並導覽至 `http://localhost:8000` 以存取整合的前端。
    - 在 UI 中點擊播放按鈕以連接到後端。
    - 與代理程式互動！試試看這樣的提示：_"Using the tool you have, define Governance in the context MLOPs"_
    - 在 `app/agent.py` 中修改代理程式邏輯。當您儲存變更時，後端伺服器（使用 `uvicorn --reload` 的 FastAPI）應該會自動重新啟動。如果需要，請重新整理前端以查看行為變更。

</details>

## 部署

> **注意：** 若要使用 Terraform 透過單一指令簡化整個 CI/CD 管線和基礎架構的部署，您可以使用 [`agent-starter-pack setup-cicd` CLI 指令](https://googlecloudplatform.github.io/agent-starter-pack/cli/setup_cicd.html)。目前支援 GitHub，並可使用 Google Cloud Build 和 GitHub Actions 作為 CI/CD 執行器。

### 開發環境

您可以使用以下指令測試對開發環境的部署：

```bash
# 設定 gcloud 的專案為您的開發專案 ID
gcloud config set project <your-dev-project-id>
# 執行部署
make deploy
```

**注意：** 為了安全地存取您已部署的後端，請考慮執行 `make deploy IAP=true` 來使用 Identity-Aware Proxy (IAP)。

該儲存庫包含用於設定開發 Google Cloud 專案的 Terraform 設定。
有關說明，請參閱 [deployment/README.md](deployment/README.md)。

### 生產環境部署

該儲存庫包含用於設定生產 Google Cloud 專案的 Terraform 設定。有關如何部署基礎架構和應用程式的詳細說明，請參閱 [deployment/README.md](deployment/README.md)。

## 監控與可觀測性

該應用程式提供兩個層級的可觀測性：

**1. 代理程式遙測事件（始終啟用）**

- 將 OpenTelemetry 追蹤和跨度匯出到 **Cloud Trace**
- 追蹤代理程式執行、延遲和系統指標

**2. 提示-回應記錄（可設定）**

- GenAI 檢測功能會擷取 LLM 互動（權杖、模型、時間）
- 匯出到 **Google Cloud Storage** (JSONL)、**BigQuery**（外部資料表）和 **Cloud Logging**（專用儲存桶）

| 環境                               | 提示-回應記錄                                      |
| ---------------------------------- | -------------------------------------------------- |
| **本機開發** (`make playground`)   | ❌ 預設停用                                        |
| **已部署的環境**（透過 Terraform） | ✅ **預設啟用**（保護隱私：僅元數據，無提示/回應） |

**若要在本機啟用：** 設定 `LOGS_BUCKET_NAME` 和 `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=NO_CONTENT`。

**若要在部署中停用：** 編輯 Terraform 設定以設定 `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=false`。

有關詳細說明、範例查詢和視覺化選項，請參閱[可觀測性指南](https://googlecloudplatform.github.io/agent-starter-pack/guide/observability.html)。

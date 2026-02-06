# 文檔檢索代理

🔗 參考來源：[ADK-Samples [RAG]](https://github.com/google/adk-samples/tree/main/python/agents/RAG)

## 概述

此代理旨在回答與您上傳到 Vertex AI RAG 引擎的文檔相關的問題。它利用 Retrieval-Augmented Generation (RAG) 和 Vertex AI RAG 引擎來獲取相關文檔片段和代碼參考，然後由 LLM (Gemini) 綜合這些信息以提供帶有引用的信息性答案。

![RAG 架構](RAG_architecture.png)

此圖表概述了代理的工作流程，旨在提供知情和上下文感知的響應。用戶查詢由代理開發工具包處理。LLM 確定是否需要外部知識 (RAG 語料庫)。如果需要，`VertexAiRagRetrieval` 工具從配置的 Vertex RAG 引擎語料庫中獲取相關信息。然後 LLM 將檢索到的信息與其內部知識進行綜合，生成準確的答案，包括指向源文檔 URL 的引用。

## 專案結構

```
pack-rag/
├── rag/                       # 核心代理代碼
│   ├── agent.py               # 主要代理邏輯
│   ├── fast_api_app.py        # FastAPI 後端服務器
│   ├── prompts.py             # 代理提示模板
│   ├── tracing.py             # 分佈式追蹤配置
│   ├── __init__.py
│   ├── README.md
│   ├── app_utils/             # 應用工具和幫助程序
│   │   ├── telemetry.py       # 遙測和監控
│   │   └── typing.py          # 類型定義
│   └── shared_libraries/
│       └── prepare_corpus_and_data.py  # RAG 語料庫準備
├── .cloudbuild/               # Google Cloud Build 的 CI/CD 管道配置
├── deployment/                # 基礎設施和部署腳本
│   ├── deploy.py              # 部署自動化
│   ├── run.py                 # 遠程代理測試
│   ├── grant_permissions.sh   # 權限配置
│   ├── terraform/             # IaC 配置
│   └── README.md              # 部署文檔
├── eval/                      # 評估框架
│   ├── test_eval.py           # 主評估腳本
│   ├── test_eval_arize.py     # Arize 評估集成
│   └── data/                  # 測試數據和配置
│       ├── conversation.test.json
│       └── test_config.json
├── notebooks/                 # Jupyter 筆記本
│   ├── adk_app_testing.ipynb  # ADK 應用測試
│   └── evaluating_adk_agent.ipynb  # 代理評估
├── tests/                     # 自動化測試
│   ├── unit/                  # 單元測試
│   ├── integration/           # 集成測試
│   └── load_test/             # 負載測試
├── GEMINI.md                  # AI 輔助開發指南
├── Makefile                   # 開發命令
├── pyproject.toml             # 項目依賴項和配置
└── README.md                  # 此文件
```

> 💡 **提示：** 使用 [Gemini CLI](https://github.com/google-gemini/gemini-cli) 進行 AI 輔助開發 - 項目上下文已在 `GEMINI.md` 中預配置。

## 代理詳情

| 屬性 | 詳情 |
| :---------------- | :---------- |
| **交互類型** | 對話式 |
| **複雜度** | 中等 |
| **代理類型** | 單代理 |
| **組件** | 工具、RAG、評估 |
| **應用領域** | 通用 |

### 代理架構

![RAG](RAG_workflow.png)

### 主要功能

*   **檢索增強生成 (RAG)：** 利用 [Vertex AI RAG Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-overview) 獲取相關文檔。
*   **引用支持：** 為檢索的內容提供準確的引用，格式為 URL。
*   **清晰指示：** 遵循嚴格的指南以提供事實性答案和適當的引用。
*   **可觀測性與監控：** 內置 OpenTelemetry 跟蹤和 GenAI 檢測。
*   **多種部署選項：** 支持本地開發、Cloud Run 和 Vertex AI Agent Engine。

## 要求

在開始之前，請確保您有以下工具已安裝：

*   **Google Cloud 帳戶：** 您需要一個 Google Cloud 帳戶。
*   **Python 3.10+：** 確保安裝了 Python 3.10 或更高版本。
*   **uv：** Python 包管理器，用於依賴管理和打包。
    - 安裝說明：[uv 官方文件](https://docs.astral.sh/uv/getting-started/installation/)
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

*   **Google Cloud SDK：** 用於 GCP 服務交互 - [安裝](https://cloud.google.com/sdk/docs/install)
*   **Terraform：** 用於基礎設施部署 - [安裝](https://developer.hashicorp.com/terraform/downloads)
*   **make：** 構建自動化工具 - [安裝](https://www.gnu.org/software/make/)
    - 大多數基於 Unix 的系統上已預裝
    - macOS 用戶可通過 `brew install make` 安裝
*   **Git：** 版本控制工具 - [安裝](https://git-scm.com/book/zh-tw/v2)

## 快速開始

安裝所需包並啟動本地開發環境：

```bash
make install && make playground
```

> **📊 可觀測性注意：** 代理遙測（Cloud Trace）始終啟用。提示-響應日誌記錄（GCS、BigQuery、Cloud Logging）在本地**禁用**，在已部署環境中**默認啟用**（僅限元數據 - 無提示/響應）。詳見[監控和可觀測性](#監控和可觀測性)。

## 開發命令


| 命令 | 說明 |
| --- | --- |
| `make install` | 使用 uv 套件管理器安裝依賴項 |
| `make playground` | 啟動本機開發遊樂場（Web UI + 後端） |
| `make local-backend` | 使用熱重載啟動本地開發伺服器（FastAPI） |
| `make debug-backend` | 以 debug 模式啟動本地後端伺服器（可指定 PORT） |
| `make debug-playground` | 以 debug 模式啟動本地遊樂場（可指定 PORT） |
| `make deploy` | 將代理部署到 Cloud Run（支援 IAP/自訂 PORT） |
| `make backend` | `make deploy` 的別名（向後相容） |
| `make setup-dev-env` | 使用 Terraform 設定開發環境資源 |
| `make test` | 執行單元測試和整合測試 |
| `make lint` | 執行程式碼品質檢查（codespell、ruff、mypy） |
| `make clean` | 清除快取、測試、建置、Terraform 狀態等檔案 |

有關完整命令選項和用法，請參閱 [Makefile](Makefile)。

## 使用方法

此項目遵循「自帶代理」的方法 - 您專注於業務邏輯，模板處理其他所有事項（UI、基礎設施、部署、監控）。

### 開發工作流程

1. **原型設計：** 使用 `notebooks/` 中的介紹筆記本構建您的生成式 AI 代理。使用 Vertex AI 評估來評估性能。

2. **集成：** 通過編輯 [rag/agent.py](rag/agent.py) 將您的代理邏輯集成到應用。

3. **測試：** 使用 `make playground` 在本地遊樂場探索您的代理功能。遊樂場會在代碼更改時自動重新加載您的代理。

4. **部署：** 設置並啟動 CI/CD 管道，根據需要自定義測試。有關全面說明，請參閱[部署章節](#部署)。為了簡化基礎設施部署，可運行：
   ```bash
   uvx agent-starter-pack setup-cicd
   ```
   查看 [`agent-starter-pack setup-cicd` CLI 命令](https://googlecloudplatform.github.io/agent-starter-pack/cli/setup_cicd.html)。目前支持 GitHub 以及 Google Cloud Build 和 GitHub Actions 作為 CI/CD 運行器。

5. **監控：** 使用 BigQuery 遙測數據、Cloud Logging 和 Cloud Trace 追蹤性能並收集見解，以迭代您的應用。

此項目包含一個 [GEMINI.md](GEMINI.md) 文件，該文件為 Gemini CLI 等 AI 工具在提問時提供上下文。

## 設置和安裝說明

此部分涵蓋使用 ADK（Agent Development Kit）和 Starter Pack 兩種方法的項目設置。

### 方法 1：使用 ADK（推薦新用戶）

#### 前置要求

*   **Google Cloud 帳戶：** 您需要一個 Google Cloud 帳戶。
*   **Python 3.10+：** 確保安裝了 Python 3.10 或更高版本。
*   **uv：** 用於依賴管理和打包。請遵循官方 [uv 網站](https://docs.astral.sh/uv/) 上的說明進行安裝。

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

*   **Git：** 確保已安裝 git。

#### 項目設置

1.  **克隆存儲庫：**

    ```bash
    git clone https://github.com/google/adk-samples.git
    cd adk-samples/python/agents/pack-rag
    ```

2.  **安裝依賴項：**

    ```bash
    uv sync
    ```

    此命令讀取 `pyproject.toml` 文件並將所有必要的依賴項安裝到虛擬環境中。

3.  **設置環境變量：**
    - 將文件 ".env.example" 重命名為 ".env"
    - 按照文件中的步驟設置環境變量

4. **配置 RAG 語料庫：**
    - 如果您在 Vertex AI RAG Engine 中已有現有語料庫，請在 .env 文件中設置語料庫信息。例如：`RAG_CORPUS='projects/123/locations/us-central1/ragCorpora/456'`。
    - 如果您還沒有設置語料庫，請遵循下面的「**上傳文件到 RAG 語料庫**」部分。`prepare_corpus_and_data.py` 腳本將自動創建語料庫（如需要）並使用創建或檢索的語料庫的資源名稱更新 `.env` 文件中的 `RAG_CORPUS` 變量。

### 方法 2：使用 Starter Pack（推薦生產部署）

Starter Pack 提供了一個生產就緒的模板，具有完整的 CI/CD、基礎設施和部署功能。

```bash
# 安裝 starter pack
pip install --upgrade agent-starter-pack

# 創建項目
agent-starter-pack create my-rag-agent -a adk@rag
cd my-rag-agent

# 安裝依賴項並啟動開發環境
make install && make playground
```

**替代方案：使用 uv 進行無需預先安裝的快速設置**

如果安裝了 `uv`，您可以使用單個命令創建和設置項目：

```bash
uvx agent-starter-pack create my-rag-agent -a adk@rag
cd my-rag-agent
make install && make playground
```

此命令無需預先將軟件包安裝到虛擬環境中即可處理項目創建。

**重點：** Starter Pack 將提示您選擇部署選項，並提供包括自動 CI/CD 部署腳本在內的其他生產就緒功能。

## 上傳文件到 RAG 語料庫

`rag/shared_libraries/prepare_corpus_and_data.py` 腳本幫助您設置 RAG 語料庫並上傳初始文檔。默認情況下，它下載 Alphabet 的 2024 10-K PDF 並將其上傳到新語料庫。

### 前置步驟

1.  **使用 Google Cloud 帳戶進行身份驗證：**
    ```bash
    gcloud auth application-default login
    ```

2.  **在 `.env` 文件中設置環境變量：**
    確保從 `.env.example` 複製的 `.env` 文件設置了以下變量：
    ```
    GOOGLE_CLOUD_PROJECT=your-project-id
    GOOGLE_CLOUD_LOCATION=your-location  # 例如，us-central1
    ```

### 使用默認行為（上傳 Alphabet 的 10K PDF）

只需運行腳本：

```bash
uv run python rag/shared_libraries/prepare_corpus_and_data.py
```

這將創建一個名為 `Alphabet_10K_2024_corpus` 的語料庫（如果不存在）並上傳從腳本中指定的 URL 下載的 PDF `goog-10-k-2024.pdf`。

### 從 URL 上傳不同的 PDF

a. 打開 `rag/shared_libraries/prepare_corpus_and_data.py` 文件。

b. 修改腳本頂部的以下變量：
   ```python
   # --- 請填入您的配置 ---
   # ... project 和 location 從 .env 讀取 ...
   CORPUS_DISPLAY_NAME = "Your_Corpus_Name"  # 根據需要更改
   CORPUS_DESCRIPTION = "Description of your corpus" # 根據需要更改
   PDF_URL = "https://path/to/your/document.pdf"  # 您的 PDF 文檔的 URL
   PDF_FILENAME = "your_document.pdf"  # 語料庫中文件的名稱
   # --- 腳本開始 ---
   ```

c. 運行腳本：
   ```bash
   uv run python rag/shared_libraries/prepare_corpus_and_data.py
   ```

### 上傳本地 PDF 文件

a. 打開 `rag/shared_libraries/prepare_corpus_and_data.py` 文件。

b. 根據需要修改 `CORPUS_DISPLAY_NAME` 和 `CORPUS_DESCRIPTION` 變量（見上文）。

c. 修改腳本底部的 `main()` 函數以直接調用 `upload_pdf_to_corpus`，提供您的本地文件詳情：

   ```python
   def main():
     initialize_vertex_ai()
     corpus = create_or_get_corpus() # 使用 CORPUS_DISPLAY_NAME & CORPUS_DESCRIPTION

     # 將本地 PDF 上傳到語料庫
     local_file_path = "/path/to/your/local/file.pdf" # 設置正確的路徑
     display_name = "Your_File_Name.pdf" # 設置所需的顯示名稱
     description = "Description of your file" # 設置描述

     # 上傳前確保文件存在
     if os.path.exists(local_file_path):
         upload_pdf_to_corpus(
             corpus_name=corpus.name,
             pdf_path=local_file_path,
             display_name=display_name,
             description=description
         )
     else:
         print(f"Error: Local file not found at {local_file_path}")

     # 列出語料庫中的所有文件
     list_corpus_files(corpus_name=corpus.name)
   ```

d. 運行腳本：
   ```bash
   uv run python rag/shared_libraries/prepare_corpus_and_data.py
   ```

有關 Vertex RAG Engine 中數據管理的更多詳情，請參閱[官方文檔頁面](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-quickstart)。

## 運行代理

### 使用 ADK 命令（推薦）

您可以在終端中使用 ADK 命令運行代理。從根項目目錄運行：

1.  **在 CLI 中運行代理：**

    ```bash
    adk run rag
    ```

2.  **使用 ADK Web UI 運行代理：**
    ```bash
    adk web
    ```
    從下拉菜單中選擇 RAG

### 使用 Starter Pack 命令（生產推薦）

```bash
# 啟動本地開發環境（包含 Web UI 和後端）
make playground
```

此命令將啟動一個完整的本地開發環境，包含可視化界面和 API 後端。

### 交互示例

以下是用戶如何與代理交互的快速示例：

**示例 1：文檔信息檢索**

**用戶：** Alphabet 2024 10-K 報告中提到的主要業務部門是什麼？

**代理：** 根據 Alphabet 2024 10-K 報告，主要業務部門是：
1. Google 服務（包括 Google 搜索、YouTube、Google 地圖、Play 商店）
2. Google Cloud（提供云計算服務、數據分析和 AI 解決方案）
3. 其他投資（包括用於自動駕駛技術的 Waymo）

[來源：goog-10-k-2024.pdf]

## 評估代理

### 運行評估

可以從 `pack-rag` 目錄使用 `pytest` 模塊運行評估：

```bash
uv sync --dev
uv run pytest eval
```

### 評估框架

評估框架由三個主要組件組成：

1. **test_eval.py**：主測試腳本，協調評估過程。它使用 Google ADK 中的 `AgentEvaluator` 針對測試數據集運行代理，並根據預定義條件評估其性能。

2. **conversation.test.json**：包含結構化為對話的一系列測試用例。每個測試用例包括：
   - 用戶查詢（例如，關於 Alphabet 10-K 報告的問題）
   - 預期的工具使用（代理應調用哪些工具及其參數）
   - 參考答案（代理應提供的理想響應）

3. **test_config.json**：定義評估標準和閾值：
   - `tool_trajectory_avg_score`：衡量代理使用適當工具的效果
   - `response_match_score`：衡量代理響應與參考答案的匹配程度

### 評估流程

當您運行評估時，系統會：
1. 從 conversation.test.json 加載測試用例
2. 將每個查詢發送給代理
3. 將代理的工具使用與預期的工具使用進行比較
4. 將代理的響應與參考答案進行比較
5. 根據 test_config.json 中的標準計算分數

此評估有助於確保代理正確利用 RAG 功能來檢索相關信息，並生成帶有適當引用的準確響應。

## 部署

部署代理有多種選擇，取決於您的需求和環境（開發或生產）。

### 開發環境部署

#### 使用 Starter Pack 部署到 Cloud Run

```bash
gcloud config set project <your-dev-project-id>
make deploy
```

#### 使用 ADK 部署到 Vertex AI Agent Engine

代理可以使用以下命令部署到 Vertex AI Agent Engine：

```bash
uv run python deployment/deploy.py
```

部署代理後，您將能夠讀到以下 INFO 日誌消息：

```
Deployed agent to Vertex AI Agent Engine successfully, resource name: projects/<PROJECT_NUMBER>/locations/us-central1/reasoningEngines/<AGENT_ENGINE_ID>
```

請記下您的 Agent Engine 資源名稱，並相應地更新 `.env` 文件，因為這對於測試遠程代理至關重要。

您也可以根據您的使用案例修改部署腳本。

### 生產環境部署

該存儲庫包含用於設置生產 Google Cloud 項目的 Terraform 配置。詳見 [deployment/README.md](deployment/README.md) 以了解如何部署基礎設施和應用。

使用 Starter Pack 的一鍵設置：

```bash
uvx agent-starter-pack setup-cicd
```

此命令將自動配置 CI/CD 管道和所有必要的基礎設施。查看 [`agent-starter-pack setup-cicd` CLI 命令](https://googlecloudplatform.github.io/agent-starter-pack/cli/setup_cicd.html) 了解詳細信息。

## 測試已部署的代理

部署代理後，請遵循以下步驟進行測試：

### 1. 更新環境變量

- 打開您的 `.env` 文件。
- 當您部署代理時，`deployment/deploy.py` 腳本應已自動更新 `AGENT_ENGINE_ID`。驗證其設置正確：
   ```
   AGENT_ENGINE_ID=projects/<PROJECT_NUMBER>/locations/us-central1/reasoningEngines/<AGENT_ENGINE_ID>
   ```

### 2. 授予 RAG 語料庫訪問權限

- 確保您的 `.env` 文件正確設置了以下變量：
   ```
   GOOGLE_CLOUD_PROJECT=your-project-id
   RAG_CORPUS=projects/<project-number>/locations/us-central1/ragCorpora/<corpus-id>
   ```
- 运行权限脚本：
   ```bash
   chmod +x deployment/grant_permissions.sh
   ./deployment/grant_permissions.sh
   ```
- 此腳本將：
   - 從 `.env` 文件讀取環境變量
   - 創建具有 RAG 語料庫查詢權限的自定義角色
   - 向 AI Platform Reasoning Engine Service Agent 授予必要的權限

### 3. 測試遠程代理

- 運行測試腳本：
   ```bash
   uv run python deployment/run.py
   ```
- 此腳本將：
   - 連接到您已部署的代理
   - 發送一系列測試查詢
   - 顯示代理的響應並進行適當的格式設置

測試腳本包括關於 Alphabet 10-K 報告的示例查詢。您可以修改 `deployment/run.py` 中的查詢以測試已部署代理的不同方面。

## 監控和可觀測性

應用提供兩個級別的可觀測性：

### 1. 代理遙測事件（始終啟用）

- OpenTelemetry 跟蹤和跨度導出到 **Cloud Trace**
- 追蹤代理執行、延遲和系統指標

### 2. 提示-響應日誌記錄（可配置）

- GenAI 插裝捕獲 LLM 交互（令牌、模型、時序）
- 導出到 **Google Cloud Storage**（JSONL）、**BigQuery**（外部表）和 **Cloud Logging**（專用存儲桶）

| 環境 | 提示-響應日誌記錄 |
|-------------|-------------------------|
| **本地開發** (`make playground`) | ❌ 默認禁用 |
| **已部署環境** (通過 Terraform) | ✅ **默認啟用**（隱私保護：僅限元數據，無提示/響應） |

#### 本地啟用提示-響應日誌記錄

設置以下環境變量：
```bash
LOGS_BUCKET_NAME=your-bucket-name
OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=NO_CONTENT
```

#### 在部署中禁用提示-響應日誌記錄

編輯 Terraform 配置以設置：
```
OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=false
```

詳見[可觀測性指南](https://googlecloudplatform.github.io/agent-starter-pack/guide/observability.html)了解詳細說明、示例查詢和可視化選項。

## 自定義

### 自定義代理

您可以自定義代理的系統指示並添加更多工具以滿足您的需求，例如 Google 搜索。編輯 [rag/agent.py](rag/agent.py) 以修改代理的邏輯、提示和工具。

### 自定義 Vertex RAG Engine

您可以閱讀[官方 Vertex RAG Engine 文檔](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-quickstart)以了解更多關於自定義語料庫和數據的詳情。

### 集成其他檢索來源

您還可以集成您首選的檢索來源來增強代理的功能。例如，您可以無縫地替換或增強現有的 `VertexAiRagRetrieval` 工具，使用利用 Vertex AI Search 或任何其他檢索機制的工具。這種靈活性允許您根據特定的數據源和檢索需求定制代理。

## 故障排除

### 超出配額錯誤

運行 `prepare_corpus_and_data.py` 腳本時，您可能會遇到與 API 配額相關的錯誤，例如：

```
Error uploading file ...: 429 Quota exceeded for aiplatform.googleapis.com/online_prediction_requests_per_base_model with base model: textembedding-gecko.
```

這對於具有較低默認配額的新 Google Cloud 項目特別常見。

#### 解決方案

您需要請求增加您使用的模型的配額。

1.  在 Google Cloud 控制台中導航至**配額**頁面：[https://console.cloud.google.com/iam-admin/quotas](https://console.cloud.google.com/iam-admin/quotas)
2.  按照官方文檔中的說明請求增加配額：[https://cloud.google.com/vertex-ai/docs/quotas#request_a_quota_increase](https://cloud.google.com/vertex-ai/docs/quotas#request_a_quota_increase)

## 保持最新狀態

要將此項目升級到最新的 agent-starter-pack 版本：

```bash
uvx agent-starter-pack upgrade
```

這會在保留您的自定義設置的同時智能地合併更新。使用 `--dry-run` 預覽更改。詳見 [upgrade CLI 參考](https://googlecloudplatform.github.io/agent-starter-pack/cli/upgrade.html)。


## 📝 免責聲明

本文件僅為個人學習與教育目的而創建。其內容主要是參考線上資源，並基於個人在學習 Google ADK 過程中的理解與整理，並非 Google 的官方觀點或文件。所有資訊請以 Google 官方發布為準。

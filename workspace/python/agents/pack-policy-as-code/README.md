# Policy As Code Agent

一個由生成式 AI 驅動的代理，旨在自動化 Google Cloud 上的數據治理。它允許使用者使用自然語言查詢來定義、驗證和執行數據政策，並將其轉換為可執行的程式碼，該程式碼可在 **Google Cloud Dataplex** 和 **BigQuery** 中的元數據上運行。

> [!NOTE] 安裝與相關執行說明
> 請參閱本 [starter_pack_README.md](./starter_pack_README.md#指令總覽)。

## 🚀 快速開始

按照以下步驟，使用 **Agent Development Kit (ADK)** 網頁介面在本地啟動並運行代理。

### 1. 先決條件

*   **Python 3.11+**
*   已安裝並驗證的 **Google Cloud SDK (`gcloud`)**。
*   **Git**
*   **uv**（建議用於依賴管理）或標準的 `pip`。

### 2. 安裝

克隆存儲庫並導航到代理的目錄：

```bash
# 克隆存儲庫
git clone https://github.com/google/adk-samples.git
cd adk-samples/python/agents/policy-as-code
```

設置虛擬環境並安裝依賴項。

使用 `uv`（建議）：
```bash
uv sync
```

使用 `pip`：
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

### 3. 配置

代理需要一些環境變數才能運行。

1.  複製示例配置文件：
    ```bash
    cp .env.example .env
    ```

2.  打開 `.env` 並填寫您的詳細信息：
    *   `GOOGLE_CLOUD_PROJECT`：您的 Google Cloud 專案 ID。
    *   `GOOGLE_CLOUD_LOCATION`：（例如，`us-central1`）。
    *   `ENABLE_MEMORY_BANK`：設置為 `True` 以啟用長期記憶（需要 Firestore）。設置為 `False` 以在未啟用的情況下運行。詳情請參閱 [記憶體整合](./docs/MEMORY_INTEGRATION.md)。
    *   `FIRESTORE_DATABASE`：（可選）除非使用命名數據庫，否則保持為 `(default)`。

3.  **身份驗證**：確保您已使用 Google Cloud 驗證：
    ```bash
    gcloud auth application-default login
    ```

### 4. 運行代理

使用 ADK 網頁介面啟動代理。

**使用 `uv`（建議）：**
```bash
uv run adk web
```

**使用 `pip`：**
```bash
# 確保您的虛擬環境已啟動
adk web
```

**可選：** 若要啟用短期上下文記憶（代理引擎）以獲得更好的對話歷史記錄，請添加 `--memory_service_uri` 標誌：

**使用 `uv`：**
```bash
uv run adk web --memory_service_uri="agentengine://AGENT_ENGINE_ID"
```

**使用 `pip`：**
```bash
adk web --memory_service_uri="agentengine://AGENT_ENGINE_ID"
```

這將啟動一個本地網頁伺服器（通常位於 `http://localhost:3000` 或 `http://127.0.0.1:5000`）。打開瀏覽器中的 URL 與代理進行聊天！

### 5. CICD 配置

參考 [CICD.md](./CICD.md) 以設置自動化建置和部署流程。

---

## 💡 主要功能

*   **自然語言政策**：例如，“財務數據集中的所有表格都必須有描述。”
*   **混合執行**：即時生成 Python 程式碼以提高靈活性，但在沙盒環境中執行以確保安全性。
*   **記憶與學習**：使用 **Firestore** 和 **向量搜索** 記住有效的政策。如果您稍後提出類似問題，它將重用已驗證的程式碼，而不是重新生成。
*   **雙模式操作**：
    *   **即時模式**：即時查詢 **Dataplex Universal Catalog**。
    *   **離線模式**：分析存儲在 **Google Cloud Storage (GCS)** 中的元數據導出。
*   **合規性記分卡**：使用一條命令對您的數據資產進行全面健康檢查。
*   **補救措施**：可以為識別的違規行為建議具體的修復措施。

## 🏗️ 架構

該代理使用 **Google Cloud Agent Development Kit (ADK)** 構建，並利用了多個 Google Cloud 服務：

*   **Gemini 2.5 Pro**：用於複雜程式碼生成（將自然語言轉換為 Python）。
*   **Gemini 2.5 Flash**：用於對話邏輯、工具選擇和補救建議。
*   **Vertex AI 向量搜索**：用於過去政策的語義檢索。
*   **Firestore**：存儲政策定義、版本和執行歷史記錄。
*   **Dataplex API**：用於獲取即時元數據。

### 專案結構

*   `policy_as_code_agent/`
    *   `agent.py`：入口點和核心代理定義。
    *   `memory.py`：處理 Firestore 交互（保存/檢索政策）。
    *   `utils/`：用於 LLM 邏輯、Dataplex、GCS 和常用工具的實用模組。
    *   `simulation.py`：用於運行政策程式碼的沙盒執行引擎。
    *   `prompts/`：LLM 指令的 Markdown 模板。
*   `tests/`：單元測試和整合測試。
*   `data/`：本地測試的示例元數據。

## 🧪 運行測試

運行測試套件以確保一切正常運行：

**使用 `uv`（建議）：**
```bash
uv run pytest
```

**使用 `pip`：**
```bash
pytest
```

## 📚 文件

要深入了解實現細節，請查看 `docs/` 文件夾：
- [高層架構](./docs/HIGH_LEVEL_DETAILS.md)
- [低層實現](./docs/LOW_LEVEL_DETAILS.md)
- [記憶體整合](./docs/MEMORY_INTEGRATION.md)
- [記憶體實現](./docs/MEMORY_IMPLEMENTATION.md)

程式碼目錄結構和文件說明，請參閱：
- [CICD 流程說明](CICD.md)
- [Terraform 部署說明](./deployment/README.md)
- [代理開發設計](./policy_as_code_agent/README.md)
- [對話範例](./policy_as_code_agent/prompts/EXAMPLE.md)
- [單元測試](./tests/unit/README.md)
- [整合測試](./tests/integration/README.md)
- [效能測試](./tests/load_test//README.md)


## 📄 其他說明

- [MANIFEST.in](./MANIFEST.in)

  **說明**:
    - **用途**：MANIFEST.in 是 Python 包在使用 `setuptools` 打包時，用來指定非 Python 原始碼資源（例如 README、範本、靜態檔案、資料檔等）應該被包含在分發套件（source distribution，sdist）中的清單檔。當你執行 `python setup.py sdist` 或使用 `build`/`pip` 建立源碼發行包時，MANIFEST.in 控制哪些檔案會被加入到最終的 `.tar.gz` 或 `.zip` 中。
    - **具體這行的意義**：`recursive-include policy_as_code_agent/prompts *.md` 表示：遞迴地將 prompts 目錄及其所有子目錄中，所有副檔名為 `.md` 的檔案（Markdown 檔）包含到 source distribution。也就是說，包發行檔會帶上 prompts 目錄下的所有 Markdown 提示檔案，讓使用者或部署端能夠存取這些說明/範本/提示內容。
    - **為什麼常見**：很多專案會把文字說明、提示模板或範例資料放在 package 目錄下，為了確保這些不是純程式碼但又必要的資源能發佈給使用者，就要在 MANIFEST.in 裡指明包含它們。

    **建議（選用）**:
    - 若還需要包含其他類型的檔案（例如 `.json`, `.yaml`, `.txt`, 或其他資料目錄），可以新增對應規則，例如：
    - `recursive-include policy_as_code_agent/prompts *.json`
    - `include README.md`
    - `recursive-include policy_as_code_agent/static *.*`
    - 若專案使用 `package_data`（在 `setup.cfg` 或 `setup.py`）並且搭配 `setuptools_scm` 或 `include_package_data=True`，請確認這些設定與 MANIFEST.in 不衝突。
    - 可檢查 pyproject.toml / `setup.cfg`（若存在）確保打包設定一致，避免遺漏需要的資源。

## 🔗 參考資源

- [adk-samples 存儲庫 (policy as code)](https://github.com/google/adk-samples/tree/3d9fe35ce097760c5dceb7136a2c72802c3c6021/python/agents/policy-as-code)
- [agent-starter-pack 官方文件](https://github.com/GoogleCloudPlatform/agent-starter-pack)
- [Gemini CLI](https://github.com/google-gemini/gemini-cli)
- [Terraform 官方教學](https://developer.hashicorp.com/terraform/tutorials)
- [uv 官方文件](https://docs.astral.sh/uv/)
- [Cloud Trace 介紹](https://cloud.google.com/trace)
- [`agent-starter-pack setup-cicd` CLI 指令](https://googlecloudplatform.github.io/agent-starter-pack/cli/setup_cicd.html)
- [Google Cloud Run](https://cloud.google.com/run)
- [OpenTelemetry 官方網站](https://opentelemetry.io/)
- [Cloud Logging 介紹](https://cloud.google.com/logging)

## 📝 免責聲明

本文件僅為個人學習與教育目的而創建。其內容主要是參考線上資源，並基於個人在學習 Google ADK 過程中的理解與整理，並非 Google 的官方觀點或文件。所有資訊請以 Google 官方發布為準。
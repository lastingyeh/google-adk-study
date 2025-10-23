# `pyproject.toml` 檔案說明

這個檔案是 `software-bug-assistant` 專案的設定檔，遵循 [PEP 621](https://peps.python.org/pep-0621/) 標準。它定義了專案的元數據、依賴項以及各種開發工具（如 Linter、類型檢查器、測試框架和建置系統）的設定。

## `[project]` - 專案元數據

此區塊定義了專案的核心資訊。

-   `name = "software-bug-assistant"`: 專案的名稱，發佈到 PyPI 時會使用此名稱。
-   `version = "0.1.0"`: 專案的目前版本。
-   `description = "Software bug assistant using ADK"`: 專案的簡短描述。
-   `authors = [...]`: 專案的作者資訊。
-   `license = "Apache-2.0"`: 專案使用的授權條款。
-   `readme = "README.md"`: 指向專案的 README 檔案，通常會作為在 PyPI 上的詳細說明。
-   `requires-python = ">=3.10,<3.13"`: 指定專案支援的 Python 版本範圍。
-   `dependencies = [...]`: 列出專案運作所需的核心依賴套件。
    -   `google-adk`: Google Agents Development Kit (ADK)。
    -   `langchain`: 用於開發由語言模型驅動的應用程式的框架。
    -   `google-cloud-aiplatform`: 用於與 Google Cloud Vertex AI 互動的函式庫。
    -   `langchain-community`: LangChain 的社群維護整合。
    -   `python-dotenv`: 用於管理環境變數。
    -   `stackapi`: Stack Exchange API 的 Python 封裝。
    -   `toolbox-core`: 一個核心工具庫。

## `[dependency-groups]` - 依賴項群組

此區塊定義了特定用途的依賴項群組。

-   `dev = [...]`: 開發環境所需的依賴項，例如執行測試。
    -   `pytest` & `pytest-asyncio`: 用於測試的框架。
    -   `agent-starter-pack`: 用於 Agent 開發的入門套件。

## `[project.optional-dependencies]` - 可選依賴項

此區塊定義了可選的依賴項，可以根據需要安裝。

-   `lint = [...]`: 用於程式碼品質檢查（Linting）的工具。
    -   `ruff`: 一個快速的 Python Linter 和格式化工具。
    -   `mypy`: 靜態類型檢查器。
    -   `codespell`: 檢查程式碼中拼寫錯誤的工具。
    -   `types-*`: 為沒有內建類型提示的函式庫提供類型資訊。

## `[tool.ruff]` - Ruff Linter 設定

此區塊設定了 `ruff` Linter 的行為。

-   `line-length = 88`: 設定每行的最大長度為 88 個字元。
-   `target-version = "py310"`: 指定程式碼的目標 Python 版本為 3.10。
-   `select = [...]`: 啟用一系列的 Linting 規則，例如 `E` (pycodestyle 錯誤)、`F` (pyflakes)、`I` (isort) 等。
-   `ignore = ["E501", "C901"]`: 忽略特定的規則（行太長、函式太複雜）。
-   `[tool.ruff.lint.isort]`: 設定 `isort`（匯入排序工具）的行為，將 `software_bug_assistant` 視為第一方函式庫。

## `[tool.mypy]` - MyPy 類型檢查器設定

此區塊為 `mypy` 設定了嚴格的類型檢查規則，以確保程式碼的類型安全。

## `[tool.codespell]` - Codespell 設定

此區塊設定了拼寫檢查工具 `codespell`。

-   `ignore-words-list = "rouge"`: 忽略清單中的單字。
-   `skip = "./locust_env/*,..."`: 跳過指定的檔案和目錄，不進行檢查。

## `[tool.pytest.ini_options]` - Pytest 測試框架設定

此區塊設定了 `pytest` 的行為。

-   `pythonpath = "."`: 將目前目錄加入到 Python 的搜尋路徑中，以便測試可以找到專案模組。
-   `asyncio_default_fixture_loop_scope = "function"`: 設定 `asyncio` 事件迴圈在測試中的作用域。

## `[build-system]` - 建置系統設定

此區塊定義了如何建置專案。

-   `requires = ["uv_build>=0.8.14,<0.9.0"]`: 指定建置時需要的工具。
-   `build-backend = "uv_build"`: 指定用於執行建置過程的後端。

## `[tool.agent-starter-pack]` - Agent Starter Pack 設定

此區塊是 `goo.gle/agent-starter-pack` 工具的特定設定，用於遠端模板化。

-   `example_question = "Can you help me debug a login page issue?"`: 提供一個範例問題，可能用於測試或初始化 Agent。
-   `agent_directory = "software_bug_assistant"`: 指定 Agent 原始碼所在的目錄。

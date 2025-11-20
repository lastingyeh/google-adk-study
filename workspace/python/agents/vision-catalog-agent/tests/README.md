# Vision Catalog Agent 測試案例

## 簡介

此文件提供了 `vision-catalog-agent` 專案的詳細測試案例說明，旨在確保所有關鍵功能都得到充分的驗證。

## Agent 設定測試 (`tests/test_agent.py`)

此部分涵蓋對 Agent 的基本設定、結構、工具整合與生成設定的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Agent 基本設定** | **TC-AGENT-001** | 測試 `root_agent` 是否已定義 | Agent 已初始化 | 1. 檢查 `root_agent` 物件 | `root_agent` | 物件不為 `None` |
| **Agent 基本設定** | **TC-AGENT-002** | 測試 `root_agent` 的名稱是否為 `vision_catalog_coordinator` | Agent 已初始化 | 1. 讀取 `root_agent.name` | `root_agent` | 名稱為 `vision_catalog_coordinator` |
| **Agent 基本設定** | **TC-AGENT-003** | 測試 `root_agent` 是否使用指定的模型 | Agent 已初始化 | 1. 讀取 `root_agent.model` | `root_agent` | 模型為指定的 `gemini` 模型之一 |
| **Agent 基本設定** | **TC-AGENT-004** | 測試 `root_agent` 是否已設定足夠的工具 | Agent 已初始化 | 1. 檢查 `root_agent.tools` | `root_agent` | 工具列表不為 `None` 且數量大於等於 5 |
| **Agent 基本設定** | **TC-AGENT-005** | 測試 `root_agent` 是否包含指令與描述 | Agent 已初始化 | 1. 檢查 `root_agent.instruction`<br>2. 檢查 `root_agent.description` | `root_agent` | 指令與描述的長度大於 0 |
| **視覺分析 Agent** | **TC-AGENT-006** | 測試 `vision_analyzer` 的設定是否正確 | Agent 已初始化 | 1. 檢查 `vision_analyzer` 物件、名稱、模型、指令與溫度設定 | `vision_analyzer` | 物件存在、名稱正確、模型包含 `gemini`、指令與視覺相關、溫度小於等於 0.5 |
| **目錄生成 Agent** | **TC-AGENT-007** | 測試 `catalog_generator` 的設定是否正確 | Agent 已初始化 | 1. 檢查 `catalog_generator` 物件、名稱、工具與指令 | `catalog_generator` | 物件存在、名稱正確、已設定工具、指令與目錄相關 |
| **工具函式** | **TC-AGENT-008** | 測試所有工具函式是否皆可呼叫 | Agent 已初始化 | 1. 檢查每個工具函式的 `callable` 狀態 | `agent.py` 中的工具函式 | 所有工具函式皆為 `callable` |
| **工具函式** | **TC-AGENT-009** | 測試所有工具函式的簽章是否正確 | Agent 已初始化 | 1. 使用 `inspect` 檢查每個工具函式的參數 | `agent.py` 中的工具函式 | 參數符合預期 |
| **Agent 與工具整合** | **TC-AGENT-010** | 測試 `root_agent` 是否整合了預期的工具 | Agent 已初始化 | 1. 獲取 `root_agent` 中的工具名稱 | `root_agent` | 包含所有預期的工具 |
| **Agent 與工具整合** | **TC-AGENT-011** | 測試 `catalog_generator` 是否整合了產物生成工具 | Agent 已初始化 | 1. 獲取 `catalog_generator` 中的工具名稱 | `catalog_generator` | 包含 `generate_catalog_entry` 工具 |
| **生成設定** | **TC-AGENT-012** | 測試所有 Agent 的生成設定是否合理 | Agent 已初始化 | 1. 檢查各 Agent 的 `generate_content_config` | `root_agent`, `vision_analyzer`, `catalog_generator` | 溫度在 0.0 至 1.0 之間，且 `max_output_tokens` 大於 0 |

## 模組匯入測試 (`tests/test_imports.py`)

此部分涵蓋對專案所有必要模組和函式是否能成功匯入的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **模組匯入**| **TC-IMPORT-001** | 測試是否能成功匯入主要的 Agent 模組 | `vision_catalog_agent` 套件已安裝 | 1. `from vision_catalog_agent import agent` | `None` | 成功匯入 `agent` 模組 |
| **模組匯入**| **TC-IMPORT-002** | 測試是否能成功匯入 `root_agent` | `vision_catalog_agent` 套件已安裝 | 1. `from vision_catalog_agent import root_agent` | `None` | 成功匯入 `root_agent` |
| **模組匯入**| **TC-IMPORT-003** | 測試是否能成功匯入 ADK 的相依性套件 | ADK 套件已安裝 | 1. 匯入 `Agent`, `FunctionTool`, `types` | `None` | 成功匯入所有 ADK 相依性 |
| **模組匯入**| **TC-IMPORT-004** | 測試是否能成功匯入圖片處理工具 | `vision_catalog_agent` 套件已安裝 | 1. 從 `agent` 模組匯入圖片處理函式 | `None` | 成功匯入所有圖片處理工具 |
| **模組匯入**| **TC-IMPORT-005** | 測試是否能成功匯入 Agent 的各個元件 | `vision_catalog_agent` 套件已安裝 | 1. 從 `agent` 模組匯入各 Agent 元件 | `None` | 成功匯入 `vision_analyzer`, `catalog_generator`, `root_agent` |
| **模組匯入**| **TC-IMPORT-006** | 測試是否能成功匯入所有的工具函式 | `vision_catalog_agent` 套件已安裝 | 1. 從 `agent` 模組匯入所有工具函式 | `None` | 成功匯入所有工具函式 |
| **模組匯入**| **TC-IMPORT-007** | 測試 PIL/Pillow 套件是否已安裝且可用 | `None` | 1. `from PIL import Image` | `None` | 若已安裝則成功匯入，否則跳過測試 |

## 多模態功能測試 (`tests/test_multimodal.py`)

此部分涵蓋對圖片載入、優化、範例圖片生成，以及多模態工具的完整測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **圖片載入**| **TC-MM-001** | 測試從檔案載入圖片 | 提供有效的圖片路徑 | 1. 呼叫 `load_image_from_file` | 合法的 `.jpg` 圖片 | 回傳 `types.Part` 物件，MIME 類型為 `image/jpeg` |
| **圖片載入**| **TC-MM-002** | 測試載入不存在的檔案 | 提供無效的圖片路徑 | 1. 呼叫 `load_image_from_file` | `nonexistent.jpg` | 拋出 `FileNotFoundError` |
| **圖片載入**| **TC-MM-003** | 測試載入不支援的圖片格式 | 提供不支援格式的檔案 | 1. 呼叫 `load_image_from_file` | 任意非圖片檔案 | 拋出 `ValueError` |
| **圖片優化**| **TC-MM-004** | 測試圖片優化功能 | 提供圖片的位元組數據 | 1. 呼叫 `optimize_image` | 一張大型 JPEG 圖片的位元組 | 回傳優化後的位元組，長度小於等於原始長度 |
| **範例圖片生成**| **TC-MM-005** | 測試建立範例圖片 | 提供儲存路徑 | 1. 呼叫 `create_sample_image` | 暫存路徑 | 成功建立圖片檔案，且目錄若不存在會自動建立 |
| **分析產品圖片**| **TC-MM-006** | 測試 `analyze_product_image` 工具 | 模擬 `tool_context` | 1. 呼叫 `analyze_product_image` | 產品 ID 與圖片路徑 | 成功時回傳 `status: 'success'`，檔案不存在時回傳 `status: 'error'` |
| **比較產品圖片**| **TC-MM-007** | 測試 `compare_product_images` 工具 | 模擬 `tool_context` | 1. 呼叫 `compare_product_images` | 圖片路徑列表 | 成功時回傳 `status: 'success'`，圖片數量不足或檔案不存在時回傳 `status: 'error'` |
| **生成目錄條目**| **TC-MM-008** | 測試 `generate_catalog_entry` 工具 | 模擬 `tool_context` | 1. 呼叫 `generate_catalog_entry` | 產品名稱與分析內容 | 成功時回傳 `status: 'success'`，儲存失敗時回傳 `status: 'error'` |
| **分析上傳圖片**| **TC-MM-009** | 測試 `analyze_uploaded_image` 工具 | 模擬 `tool_context` | 1. 呼叫 `analyze_uploaded_image` | 產品名稱 | 回傳包含分析框架與指引的成功訊息 |
| **列出範例圖片**| **TC-MM-010** | 測試 `list_sample_images` 工具 | `_sample_images` 目錄存在 | 1. 呼叫 `list_sample_images` | `None` | 回傳 `status: 'success'` 或 `'info'`，並列出可用的圖片 |
| **多模態內容**| **TC-MM-011** | 測試多模態查詢的結構 | `None` | 1. 建立包含文字與圖片的 `types.Part` 列表 | `None` | 成功建立包含 3 個部分的 `types.Part` 列表 |

## 專案結構測試 (`tests/test_structure.py`)

此部分涵蓋對專案的目錄結構、設定檔與相依性是否符合預期的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **專案結構**| **TC-STRUCT-001** | 測試專案根目錄與核心目錄是否存在 | 專案已 checkout | 1. 檢查 `vision_catalog_agent` 目錄<br>2. 檢查 `tests` 目錄 | 專案根目錄 | 所有核心目錄皆存在 |
| **專案結構**| **TC-STRUCT-002** | 測試所有必要的設定檔是否存在 | 專案已 checkout | 1. 檢查 `requirements.txt`<br>2. 檢查 `pyproject.toml`<br>3. 檢查 `Makefile`<br>4. 檢查 `.env.example`<br>5. 檢查 `.adkignore` | 專案根目錄 | 所有設定檔皆存在 |
| **專案結構**| **TC-STRUCT-003** | 測試 Agent 原始碼檔案是否存在 | 專案已 checkout | 1. 檢查 `__init__.py`<br>2. 檢查 `agent.py` | `vision_catalog_agent` 目錄 | `__init__.py` 與 `agent.py` 檔案皆存在 |
| **相依性**| **TC-STRUCT-004** | 測試 `requirements.txt` 是否包含必要的套件 | `requirements.txt` 存在 | 1. 讀取檔案內容並檢查 | `requirements.txt` | 包含 `google-genai`, `pillow`, `pytest` |
| **設定檔**| **TC-STRUCT-005** | 測試 `pyproject.toml` 是否包含必要的區段與設定 | `pyproject.toml` 存在 | 1. 讀取檔案內容並檢查 | `pyproject.toml` | 包含 `[build-system]`, `[project]` 等區段，且專案名稱設定正確 |
| **設定檔**| **TC-STRUCT-006** | 測試 `Makefile` 是否包含標準的目標 | `Makefile` 存在 | 1. 讀取檔案內容並檢查 | `Makefile` | 包含 `setup`, `dev`, `test`, `demo`, `clean` 等目標 |
| **範例圖片**| **TC-STRUCT-007** | 測試 `_sample_images` 目錄是否存在 | 專案已 checkout | 1. 檢查 `_sample_images` 目錄 | 專案根目錄 | `_sample_images` 目錄存在且為目錄 |

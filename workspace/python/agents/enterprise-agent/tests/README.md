# 詳細測試案例文件

## 簡介

此文件提供了一個詳細的測試案例說明，旨在為 `enterprise-agent` 專案建立清晰、一致且全面的測試文件。

## 代理配置與功能測試 (`tests/test_agent.py`)

此部分涵蓋對企業潛在客戶資格審查代理配置與功能的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **代理配置** | **TC-AGENT-001** | 測試 root_agent 是否已定義 | 專案環境已設置 | 檢查 `root_agent` 是否不為 None | None | `root_agent` 應存在 |
| **代理配置** | **TC-AGENT-002** | 測試代理是否具有正確的名稱 | 專案環境已設置 | 檢查 `root_agent.name` | None | 名稱應為 "lead_qualifier" |
| **代理配置** | **TC-AGENT-003** | 測試代理是否使用正確的模型 | 專案環境已設置 | 檢查 `root_agent.model` | None | 模型應為 "gemini-2.0-flash" |
| **代理配置** | **TC-AGENT-004** | 測試代理是否有描述 | 專案環境已設置 | 檢查 `root_agent.description` | None | 描述應存在且包含 "enterprise" 和 "qualification" |
| **代理配置** | **TC-AGENT-005** | 測試代理是否有指令 | 專案環境已設置 | 檢查 `root_agent.instruction` | None | 指令內容不應為空 |
| **代理配置** | **TC-AGENT-006** | 測試指令是否包含關鍵的資格審查標準 | 專案環境已設置 | 檢查指令內容 | None | 指令應包含 "company size", "industry", "budget" 及評分相關關鍵字 |
| **代理配置** | **TC-AGENT-007** | 測試代理是否已配置工具 | 專案環境已設置 | 檢查 `root_agent.tools` | None | 工具列表不應為空 |
| **代理配置** | **TC-AGENT-008** | 測試代理是否擁有預期數量的工具 | 專案環境已設置 | 計算 `root_agent.tools` 的長度 | None | 工具數量應大於等於 2 |
| **代理類型** | **TC-AGENT-TYPE-001** | 測試 root_agent 是否為 Agent 實例 | 專案環境已設置 | 檢查 `root_agent` 實例類型 | None | 應為 `google.adk.agents.Agent` 的實例 |
| **代理類型** | **TC-AGENT-TYPE-002** | 測試這是一個簡單的代理，而不是順序工作流程 | 專案環境已設置 | 檢查 `root_agent` 實例類型 | None | 不應為 `SequentialAgent` |
| **代理類型** | **TC-AGENT-TYPE-003** | 測試這是一個簡單的代理，而不是並行工作流程 | 專案環境已設置 | 檢查 `root_agent` 實例類型 | None | 不應為 `ParallelAgent` |

## 匯入驗證測試 (`tests/test_imports.py`)

此部分涵蓋對專案依賴項和模組匯入的驗證。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **核心匯入** | **TC-IMPORT-001** | 測試匯入 google.adk.agents | 安裝了 google-adk | 嘗試匯入 `Agent` | None | 匯入成功無錯誤 |
| **核心匯入** | **TC-IMPORT-002** | 測試匯入 google.adk.tools | 安裝了 google-adk | 嘗試匯入 `FunctionTool` | None | 匯入成功無錯誤 |
| **模組匯入** | **TC-IMPORT-003** | 測試匯入 enterprise_agent 模組 | 專案路徑正確 | 嘗試匯入 `enterprise_agent` | None | 匯入成功無錯誤 |
| **模組匯入** | **TC-IMPORT-004** | 測試從模組匯入 root_agent | 專案路徑正確 | 嘗試從 `enterprise_agent` 匯入 `root_agent` | None | 匯入成功無錯誤 |
| **模組匯入** | **TC-IMPORT-005** | 測試匯入 enterprise_agent.agent 模組 | 專案路徑正確 | 嘗試匯入 `enterprise_agent.agent` | None | 匯入成功無錯誤 |
| **工具匯入** | **TC-IMPORT-006** | 測試匯入 check_company_size 函數 | 專案路徑正確 | 嘗試匯入 `check_company_size` | None | 匯入成功且為可呼叫對象 |
| **工具匯入** | **TC-IMPORT-007** | 測試匯入 score_lead 函數 | 專案路徑正確 | 嘗試匯入 `score_lead` | None | 匯入成功且為可呼叫對象 |
| **工具匯入** | **TC-IMPORT-008** | 測試匯入 get_competitive_intel 函數 | 專案路徑正確 | 嘗試匯入 `get_competitive_intel` | None | 匯入成功且為可呼叫對象 |
| **模組屬性** | **TC-IMPORT-009** | 測試模組是否定義了 __all__ | 專案路徑正確 | 檢查 `enterprise_agent.__all__` | None | `__all__` 應包含 'root_agent' |
| **模組屬性** | **TC-IMPORT-010** | 測試 root_agent 是否可從模組訪問 | 專案路徑正確 | 檢查 `enterprise_agent.root_agent` | None | `root_agent` 應可訪問 |

## 專案結構驗證測試 (`tests/test_structure.py`)

此部分涵蓋對專案目錄結構和必要檔案的驗證。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **專案結構** | **TC-STRUCT-001** | 測試 enterprise_agent 目錄是否存在 | 無 | 檢查目錄存在性 | "enterprise_agent" | 目錄應存在 |
| **專案結構** | **TC-STRUCT-002** | 測試 tests 目錄是否存在 | 無 | 檢查目錄存在性 | "tests" | 目錄應存在 |
| **專案結構** | **TC-STRUCT-003** | 測試 enterprise_agent/__init__.py 是否存在 | 無 | 檢查檔案存在性 | "enterprise_agent/__init__.py" | 檔案應存在 |
| **專案結構** | **TC-STRUCT-004** | 測試 enterprise_agent/agent.py 是否存在 | 無 | 檢查檔案存在性 | "enterprise_agent/agent.py" | 檔案應存在 |
| **專案結構** | **TC-STRUCT-005** | 測試 .env.example 是否存在 | 無 | 檢查檔案存在性 | "enterprise_agent/.env.example" | 檔案應存在 |
| **專案結構** | **TC-STRUCT-006** | 測試 pyproject.toml 是否存在 | 無 | 檢查檔案存在性 | "pyproject.toml" | 檔案應存在 |
| **專案結構** | **TC-STRUCT-007** | 測試 requirements.txt 是否存在 | 無 | 檢查檔案存在性 | "requirements.txt" | 檔案應存在 |
| **專案結構** | **TC-STRUCT-008** | 測試 Makefile 是否存在 | 無 | 檢查檔案存在性 | "Makefile" | 檔案應存在 |
| **專案結構** | **TC-STRUCT-009** | 測試 README.md 是否存在 | 無 | 檢查檔案存在性 | "README.md" | 檔案應存在 |
| **測試檔案** | **TC-STRUCT-010** | 測試 tests/__init__.py 是否存在 | 無 | 檢查檔案存在性 | "tests/__init__.py" | 檔案應存在 |
| **測試檔案** | **TC-STRUCT-011** | 測試 test_agent.py 是否存在 | 無 | 檢查檔案存在性 | "tests/test_agent.py" | 檔案應存在 |
| **測試檔案** | **TC-STRUCT-012** | 測試 test_tools.py 是否存在 | 無 | 檢查檔案存在性 | "tests/test_tools.py" | 檔案應存在 |
| **測試檔案** | **TC-STRUCT-013** | 測試 test_imports.py 是否存在 | 無 | 檢查檔案存在性 | "tests/test_imports.py" | 檔案應存在 |
| **測試檔案** | **TC-STRUCT-014** | 測試 test_structure.py 是否存在 | 無 | 檢查檔案存在性 | "tests/test_structure.py" | 檔案應存在 |
| **檔案內容** | **TC-STRUCT-015** | 測試 pyproject.toml 是否定義了專案名稱 | 無 | 讀取檔案並檢查 "name" | "pyproject.toml" | 應包含 "name" 和 "tutorial26" |
| **檔案內容** | **TC-STRUCT-016** | 測試 requirements.txt 是否包含 google-adk | 無 | 讀取檔案並檢查內容 | "requirements.txt" | 應包含 "google-adk" |
| **檔案內容** | **TC-STRUCT-017** | 測試 Makefile 是否包含標準目標 | 無 | 讀取檔案並檢查目標 | "Makefile" | 應包含 setup, test, dev, clean |
| **檔案內容** | **TC-STRUCT-018** | 測試 README.md 是否包含教學資訊 | 無 | 讀取檔案並檢查內容 | "README.md" | 應包含 "Tutorial 26" |
| **檔案內容** | **TC-STRUCT-019** | 測試 .env.example 是否有 API 金鑰佔位符 | 無 | 讀取檔案並檢查內容 | "enterprise_agent/.env.example" | 應包含 "GOOGLE_API_KEY" |

## 工具函數測試 (`tests/test_tools.py`)

此部分涵蓋對企業代理使用的工具函數的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **公司規模檢查** | **TC-TOOL-001** | 測試查詢已知的公司 | 無 | 呼叫 `check_company_size` | "TechCorp" | 返回成功，員工數 250，營收 50M |
| **公司規模檢查** | **TC-TOOL-002** | 測試查詢金融公司 | 無 | 呼叫 `check_company_size` | "FinanceGlobal" | 返回成功，員工數 1200，產業 finance |
| **公司規模檢查** | **TC-TOOL-003** | 測試查詢醫療保健公司 | 無 | 呼叫 `check_company_size` | "HealthPlus" | 返回成功，員工數 450，產業 healthcare |
| **公司規模檢查** | **TC-TOOL-004** | 測試查詢未知公司返回預設值 | 無 | 呼叫 `check_company_size` | "UnknownCompany" | 返回成功，員工數 0，營收 Unknown |
| **公司規模檢查** | **TC-TOOL-005** | 測試函數返回人類可讀的報告 | 無 | 呼叫 `check_company_size` | "TechCorp" | 返回結果包含 "report" 欄位 |
| **潛在客戶評分** | **TC-TOOL-006** | 測試評分高資格的潛在客戶（70+ 分） | 無 | 呼叫 `score_lead` | size=250, industry="technology", budget="enterprise" | 分數 >= 70, 資格為 "HIGHLY QUALIFIED" |
| **潛在客戶評分** | **TC-TOOL-007** | 測試評分合格的潛在客戶（40-69 分） | 無 | 呼叫 `score_lead` | size=150, industry="retail", budget="business" | 40 <= 分數 < 70, 資格為 "QUALIFIED" |
| **潛在客戶評分** | **TC-TOOL-008** | 測試評分不合格的潛在客戶（<40 分） | 無 | 呼叫 `score_lead` | size=20, industry="retail", budget="startup" | 分數 < 40, 資格為 "UNQUALIFIED" |
| **潛在客戶評分** | **TC-TOOL-009** | 測試大公司獲得額外加分 | 無 | 呼叫 `score_lead` | size=150, industry="other", budget="startup" | 分數為 30 |
| **潛在客戶評分** | **TC-TOOL-010** | 測試目標產業獲得額外加分 | 無 | 呼叫 `score_lead` | size=50, industry="finance", budget="startup" | 分數為 30 |
| **潛在客戶評分** | **TC-TOOL-011** | 測試醫療保健作為目標產業 | 無 | 呼叫 `score_lead` | size=50, industry="healthcare", budget="startup" | 分數為 30 |
| **潛在客戶評分** | **TC-TOOL-012** | 測試企業預算層級評分 | 無 | 呼叫 `score_lead` | size=50, industry="retail", budget="enterprise" | 分數為 40 |
| **潛在客戶評分** | **TC-TOOL-013** | 測試商業預算層級評分 | 無 | 呼叫 `score_lead` | size=50, industry="retail", budget="business" | 分數為 20 |
| **潛在客戶評分** | **TC-TOOL-014** | 測試完美資格（100 分） | 無 | 呼叫 `score_lead` | size=500, industry="finance", budget="enterprise" | 分數為 100, 資格為 "HIGHLY QUALIFIED" |
| **潛在客戶評分** | **TC-TOOL-015** | 測試評分提供詳細的因素 | 無 | 呼叫 `score_lead` | size=250, industry="technology", budget="enterprise" | 結果包含 "factors" 列表 |
| **潛在客戶評分** | **TC-TOOL-016** | 測試評分返回人類可讀的報告 | 無 | 呼叫 `score_lead` | size=250, industry="technology", budget="enterprise" | 結果包含 "report" 且包含分數 |
| **競爭情報** | **TC-TOOL-017** | 測試獲取競爭情報 | 無 | 呼叫 `get_competitive_intel` | "OurCompany", "CompetitorX" | 返回包含公司和競爭對手的數據 |
| **競爭情報** | **TC-TOOL-018** | 測試競爭情報包含差異化因素 | 無 | 呼叫 `get_competitive_intel` | "OurCompany", "CompetitorX" | 結果包含 "differentiators" |
| **競爭情報** | **TC-TOOL-019** | 測試競爭情報包含競爭對手弱點 | 無 | 呼叫 `get_competitive_intel` | "OurCompany", "CompetitorX" | 結果包含 "competitor_weaknesses" |
| **競爭情報** | **TC-TOOL-020** | 測試競爭情報包含最新消息 | 無 | 呼叫 `get_competitive_intel` | "OurCompany", "CompetitorX" | 結果包含 "recent_news" |
| **競爭情報** | **TC-TOOL-021** | 測試競爭情報返回格式化的報告 | 無 | 呼叫 `get_competitive_intel` | "OurCompany", "CompetitorX" | 結果包含 "report" |
| **工具整合** | **TC-TOOL-022** | 測試完整的潛在客戶資格審查流程 | 無 | 依序呼叫 `check_company_size`, `score_lead`, `get_competitive_intel` | "TechCorp" | 所有步驟均成功且分數正確 |
| **工具整合** | **TC-TOOL-023** | 測試所有工具返回一致的回應格式 | 無 | 檢查各工具的回傳結果 | 多組輸入 | 均包含 "status": "success" 和 "report" |

# 詳細測試案例範本

## 簡介

此文件提供了一個詳細的測試案例範本，旨在為專案建立清晰、一致且全面的測試文件。使用此範本可以幫助開發者和測試人員標準化測試流程，確保所有關鍵功能都得到充分的驗證。

## 金融計算機代理測試 (`tests/test_agent.py`)

此部分涵蓋對金融計算機代理的功能測試，確保其設定、程式碼執行能力、模型需求、程式碼品質及效能符合預期。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **代理程式組態** | **TC-AGENT-001** | 測試代理程式是否能成功匯入 | `code_calculator` 套件已安裝 | 1. 匯入 `root_agent` | `from code_calculator import root_agent` | `root_agent` 物件成功匯入，不為 `None` |
| **代理程式組態** | **TC-AGENT-002** | 測試 `root_agent` 是否為 `Agent` 的實例 | `root_agent` 已成功匯入 | 1. 檢查 `root_agent` 的類型 | `isinstance(root_agent, Agent)` | 返回 `True` |
| **代理程式組態** | **TC-AGENT-003** | 測試代理程式的名稱是否正確 | `root_agent` 已成功匯入 | 1. 存取 `root_agent.name` | `root_agent.name` | 名稱為 "FinancialCalculator" |
| **代理程式組態** | **TC-AGENT-004** | 測試代理程式是否使用 Gemini 2.0+ 進行程式碼執行 | `root_agent` 已成功匯入 | 1. 檢查 `root_agent.model` | `root_agent.model.startswith("gemini-2")` | 返回 `True` |
| **代理程式組態** | **TC-AGENT-005** | 測試代理程式是否有描述 | `root_agent` 已成功匯入 | 1. 檢查 `root_agent.description` 是否存在<br>2. 檢查描述是否包含關鍵字 | `root_agent.description` | 描述存在，且包含 "financial" 和 "code" |
| **代理程式組態** | **TC-AGENT-006** | 測試代理程式是否有全面的指令 | `root_agent` 已成功匯入 | 1. 檢查 `root_agent.instruction` 是否存在<br>2. 檢查指令長度與關鍵字 | `len(root_agent.instruction) > 500` | 指令存在，長度超過 500，且包含 "code" 和 "calculation" |
| **代理程式組態** | **TC-AGENT-007** | 測試代理程式是否已設定 `BuiltInCodeExecutor` | `root_agent` 已成功匯入 | 1. 檢查 `root_agent.code_executor` | `isinstance(root_agent.code_executor, BuiltInCodeExecutor)` | `code_executor` 存在且類型正確 |
| **代理程式組態** | **TC-AGENT-008** | 測試代理程式是否使用低 `temperature` 以確保準確性 | `root_agent` 已成功匯入 | 1. 檢查 `generate_content_config.temperature` | `root_agent.generate_content_config.temperature <= 0.2` | `temperature` 小於或等於 0.2 |
| **代理程式組態** | **TC-AGENT-009** | 測試指令是否包含財務公式 | `root_agent` 已成功匯入 | 1. 檢查指令是否包含財務相關關鍵字 | `any(term in root_agent.instruction.lower() for term in ["compound", "interest", "loan", "formula"])` | 返回 `True` |
| **代理程式組態** | **TC-AGENT-010** | 測試指令是否強調程式碼執行 | `root_agent` 已成功匯入 | 1. 檢查指令是否包含程式碼執行關鍵字 | `"code" in root_agent.instruction.lower() and "python" in root_agent.instruction.lower()` | 返回 `True` |
| **代理程式匯入與結構** | **TC-STRUCT-001** | 測試 `root_agent` 是否能正確匯出 | `code_calculator` 套件已安裝 | 1. 匯入 `root_agent` | `from code_calculator import root_agent` | `root_agent` 物件成功匯入，不為 `None` |
| **代理程式匯入與結構** | **TC-STRUCT-002** | 測試代理程式模組的結構是否正確 | `code_calculator` 套件已安裝 | 1. 匯入 `code_calculator.agent` 模組<br>2. 檢查模組屬性 | `import code_calculator.agent as agent_module` | 模組包含 `root_agent` 和 `financial_calculator` |
| **代理程式匯入與結構** | **TC-STRUCT-003** | 測試 `financial_calculator` 與 `root_agent` 是否為同一個物件 | `code_calculator.agent` 已匯入 | 1. 比較 `financial_calculator` 與 `root_agent` | `financial_calculator is root_agent` | 返回 `True` |
| **代理程式匯入與結構** | **TC-STRUCT-004** | 測試模型是否支援程式碼執行 | `root_agent` 已成功匯入 | 1. 檢查 `root_agent.model` | `root_agent.model.startswith("gemini-2")` | 返回 `True` |
| **程式碼執行能力** | **TC-EXEC-001** | 測試簡單的算術計算 | GOOGLE_API_KEY 環境變數已設定 | 1. 執行簡單計算 | `None` | 測試被跳過，需手動執行 |
| **程式碼執行能力** | **TC-EXEC-002** | 測試階乘計算 | GOOGLE_API_KEY 環境變數已設定 | 1. 計算 10 的階乘 | `None` | 測試被跳過，需手動執行 |
| **程式碼執行能力** | **TC-EXEC-003** | 測試統計計算 | GOOGLE_API_KEY 環境變數已設定 | 1. 計算列表的平均值 | `None` | 測試被跳過，需手動執行 |
| **模型需求** | **TC-MODEL-001** | 測試代理程式是否需要 Gemini 2.0+ 模型 | `root_agent` 已成功匯入 | 1. 檢查 `root_agent.model` | `root_agent.model.startswith("gemini-2")` | 返回 `True` |
| **模型需求** | **TC-MODEL-002** | 測試程式碼執行器的類型是否正確 | `root_agent` 已成功匯入 | 1. 檢查 `root_agent.code_executor` | `isinstance(root_agent.code_executor, BuiltInCodeExecutor)` | `code_executor` 類型正確 |
| **模型需求** | **TC-MODEL-003** | 測試舊版模型是否會因程式碼執行而引發錯誤 | `None` | 1. 邏輯驗證 | `None` | 組態測試通過，驗證對需求的理解 |
| **程式碼品質** | **TC-QUALITY-001** | 測試代理程式模組是否有適當的文件 | `code_calculator.agent` 模組存在 | 1. 檢查 `agent_module.__doc__` | `len(agent_module.__doc__) > 50` | 模組文件存在且長度足夠 |
| **程式碼品質** | **TC-QUALITY-002** | 測試套件是否有適當的文件 | `code_calculator` 套件存在 | 1. 檢查 `code_calculator.__doc__` | `code_calculator.__doc__ is not None` | 套件文件存在 |
| **程式碼品質** | **TC-QUALITY-003** | 測試指令是否全面 | `root_agent` 已成功匯入 | 1. 檢查指令長度 | `len(root_agent.instruction) > 1000` | 指令長度超過 1000 |
| **程式碼品質** | **TC-QUALITY-004** | 測試描述是否提及關鍵能力 | `root_agent` 已成功匯入 | 1. 檢查描述是否包含關鍵字 | `any(term in root_agent.description.lower() for term in ["financial", "calculator", "code", "execution", "python"])` | 返回 `True` |
| **效能測試** | **TC-PERF-001** | 測試 `temperature` 是否設定較低以確保程式碼生成的準確性 | `root_agent` 已成功匯入 | 1. 檢查 `generate_content_config.temperature` | `root_agent.generate_content_config.temperature <= 0.2` | `temperature` 小於或等於 0.2 |
| **效能測試** | **TC-PERF-002** | 測試 `token` 限制是否合理 | `root_agent` 已成功匯入 | 1. 檢查 `max_output_tokens` | `root_agent.generate_content_config.max_output_tokens >= 1024` | `max_output_tokens` 大於或等於 1024 |
| **摘要測試** | **TC-SUM-001** | 測試是否有全面的測試覆蓋率 | 測試套件已執行 | 1. 計算測試函式與類別數量 | `None` | 總測試數量大於等於 25 |

---

### **欄位說明**

*   **群組**: 測試案例所屬的功能子群組或類別。例如：`代理程式組態`、`程式碼執行能力`。
*   **測試案例編號**: 唯一的測試案例識別碼。格式為 `TC-[模組]-[編號]`，例如 `TC-AGENT-001`。
*   **描述**: 對此測試案例目標的簡潔說明。
*   **前置條件**: 執行測試前系統或環境必須處於的狀態。
*   **測試步驟**: 執行測試所需遵循的具體步驟，應清晰且可重複。
*   **測試數據**: 在測試步驟中使用的具體輸入數據。
*   **預期結果**: 在成功執行測試步驟後，系統應顯示的確切結果或狀態。

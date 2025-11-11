# 詳細測試案例範本

## 簡介

此文件提供了一個詳細的測試案例範本，旨在為專案建立清晰、一致且全面的測試文件。使用此範本可以幫助開發者和測試人員標準化測試流程，確保所有關鍵功能都得到充分的驗證。

## 代理與規劃器模組測試 (`tests/test_agent.py`)

此部分涵蓋對代理 (agent) 與規劃器 (planner) 的配置、實作與指令內容的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **代理配置** | **TC-AGENT-001** | 測試 BuiltInPlanner 代理的配置 | `builtin_planner_agent` 已被正確匯入 | 1. 檢查代理是否為 `Agent` 實例<br>2. 驗證代理名稱、模型<br>3. 檢查規劃器是否為 `BuiltInPlanner` 實例 | `builtin_planner_agent` 物件 | 代理配置符合預期設定 |
| **代理配置** | **TC-AGENT-002** | 測試 PlanReActPlanner 代理的配置 | `plan_react_agent` 已被正確匯入 | 1. 檢查代理是否為 `Agent` 實例<br>2. 驗證代理名稱<br>3. 檢查規劃器是否為 `PlanReActPlanner` 實例 | `plan_react_agent` 物件 | 代理配置符合預期設定 |
| **代理配置** | **TC-AGENT-003** | 測試 StrategicPlanner 代理的配置 | `strategic_planner_agent` 已被正確匯入 | 1. 檢查代理是否為 `Agent` 實例<br>2. 驗證代理名稱<br>3. 檢查規劃器是否為 `StrategicPlanner` 實例 | `strategic_planner_agent` 物件 | 代理配置符合預期設定 |
| **代理配置** | **TC-AGENT-004** | 測試 root_agent 是否使用 PlanReActPlanner | `root_agent` 與 `plan_react_agent` 已被正確匯入 | 1. 驗證 `root_agent` 是否等同於 `plan_react_agent`<br>2. 檢查 `root_agent` 的規劃器是否為 `PlanReActPlanner` 實例 | `root_agent` 物件 | `root_agent` 正確指向 `plan_react_agent` |
| **代理配置** | **TC-AGENT-005** | 測試所有代理是否都擁有必要的工具 | 所有代理物件已被正確匯入 | 1. 迭代檢查每個代理<br>2. 驗證工具數量是否為 4<br>3. 檢查是否包含所有必要的業務分析工具 | 代理物件列表 | 所有代理都包含指定的 4 個工具 |
| **代理配置** | **TC-AGENT-006** | 測試代理是否具有適當的輸出鍵 | 所有代理物件已被正確匯入 | 1. 檢查 `builtin_planner_agent` 的輸出鍵<br>2. 檢查 `plan_react_agent` 的輸出鍵<br>3. 檢查 `strategic_planner_agent` 的輸出鍵 | 代理物件 | 每個代理都有其對應的唯一輸出鍵 |
| **規劃器配置** | **TC-PLANNER-001** | 測試 BuiltInPlanner 是否已啟用思考配置 | `builtin_planner_agent` 已被正確匯入 | 1. 取得代理的規劃器<br>2. 驗證 `include_thoughts` 是否為 `True` | `builtin_planner_agent.planner` | `BuiltInPlanner` 的思考配置已啟用 |
| **規劃器配置** | **TC-PLANNER-002** | 測試 PlanReActPlanner 是否已正確實例化 | `plan_react_agent` 已被正確匯入 | 1. 取得代理的規劃器<br>2. 驗證其為 `PlanReActPlanner` 的實例 | `plan_react_agent.planner` | 規劃器已正確實例化 |
| **規劃器配置** | **TC-PLANNER-003** | 測試 StrategicPlanner 是否繼承自 BasePlanner | `strategic_planner_agent` 已被正確匯入 | 1. 取得代理的規劃器<br>2. 驗證其為 `StrategicPlanner` 與 `BasePlanner` 的實例 | `strategic_planner_agent.planner` | `StrategicPlanner` 的繼承結構正確 |
| **自訂規劃器** | **TC-STRATEGIC-001** | 測試 StrategicPlanner 是否可以被建立 | `StrategicPlanner` 類別已匯入 | 1. 建立 `StrategicPlanner` 的實例<br>2. 驗證其繼承結構 | None | `StrategicPlanner` 實例建立成功 |
| **自訂規劃器** | **TC-STRATEGIC-002** | 測試 StrategicPlanner 是否能建立規劃指令 | `StrategicPlanner` 實例已建立 | 1. 呼叫 `build_planning_instruction` 方法<br>2. 驗證回傳的指令包含所有必要區段 | `MagicMock` 上下文與請求 | 規劃指令包含所有預期的分析階段 |
| **自訂規劃器** | **TC-STRATEGIC-003** | 測試 StrategicPlanner 是否能處理規劃回應 | `StrategicPlanner` 實例已建立 | 1. 呼叫 `process_planning_response` 方法 | `MagicMock` 回呼上下文與組件 | 回應內容未被修改並直接回傳 |
| **代理指令** | **TC-INSTR-001** | 測試 BuiltInPlanner 代理是否包含適當的指令 | `builtin_planner_agent` 已被正確匯入 | 1. 取得代理的指令內容<br>2. 驗證是否包含關鍵字，如 "strategic consultant" 與工具名稱 | `builtin_planner_agent.instruction` | 指令內容符合預期 |
| **代理指令** | **TC-INSTR-002** | 測試 PlanReActPlanner 代理是否包含結構化的指令 | `plan_react_agent` 已被正確匯入 | 1. 取得代理的指令內容<br>2. 驗證是否包含關鍵字，如 "systematic"、"planning tags" | `plan_react_agent.instruction` | 指令內容符合預期 |
| **代理指令** | **TC-INSTR-003** | 測試 StrategicPlanner 代理是否包含領域特定的指令 | `strategic_planner_agent` 已被正確匯入 | 1. 取得代理的指令內容<br>2. 驗證是否包含關鍵字，如 "business strategy consultant" 與分析階段 | `strategic_planner_agent.instruction` | 指令內容符合預期 |
| **內容生成** | **TC-GEN-001** | 測試不同代理的溫度設定 | 所有代理物件已被正確匯入 | 1. 檢查每個代理的 `generate_content_config.temperature` | 代理物件 | 溫度設定符合一致性與創造性的要求 |
| **內容生成** | **TC-GEN-002** | 測試最大輸出 token 設定 | 所有代理物件已被正確匯入 | 1. 迭代檢查每個代理的 `max_output_tokens` | 代理物件 | 所有代理的最大輸出 token 皆為 3000 |
| **展示功能** | **TC-DEMO-001** | 測試展示函式是否可以被匯入 | `demo_strategic_planning` 函式存在 | 1. 從 `strategic_solver.agent` 匯入函式<br>2. 驗證其為可呼叫的函式 | None | 函式成功匯入且可呼叫 |
| **展示功能** | **TC-DEMO-002** | 測試展示函式執行時不會拋出例外 | `demo_strategic_planning` 函式已匯入 | 1. 執行 `demo_strategic_planning` 函式<br>2. 捕捉並過濾預期的 API 金鑰錯誤 | None | 函式在沒有非預期錯誤的情況下執行完畢 |

## 匯入與結構測試 (`tests/test_imports.py`)

此部分涵蓋對專案模組匯入、基本代理結構及專案檔案完整性的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **模組匯入** | **TC-IMPORT-001** | 測試 strategic_solver.agent 模組是否能被匯入 | 專案環境已設定 | 1. 使用 `importlib.util.find_spec` 尋找模組 | `strategic_solver.agent` | 模組被成功找到，`spec` 不為 `None` |
| **模組匯入** | **TC-IMPORT-002** | 測試 strategic_solver.agent 是否包含 root_agent | `strategic_solver.agent` 模組可匯入 | 1. 匯入 `strategic_solver.agent`<br>2. 檢查 `root_agent` 屬性是否存在 | `strategic_solver.agent` 模組 | 模組中存在 `root_agent` |
| **模組匯入** | **TC-IMPORT-003** | 測試 root_agent 是否為 Agent 的實例 | `root_agent` 可從模組中匯入 | 1. 匯入 `root_agent`<br>2. 檢查其是否為 `Agent` 的實例 | `root_agent` 物件 | `root_agent` 是 `Agent` 的一個實例 |
| **模組匯入** | **TC-IMPORT-004** | 測試所有規劃器代理變體是否存在 | 代理物件可從模組中匯入 | 1. 匯入所有規劃器代理<br>2. 檢查每個代理是否為 `Agent` 的實例 | 代理物件 | 所有規劃器代理都正確存在且為 `Agent` 實例 |
| **模組匯入** | **TC-IMPORT-005** | 測試規劃器類別是否能被匯入 | `google.adk.planners` 套件已安裝 | 1. 從 `google.adk.planners` 匯入規劃器類別 | None | 所有規劃器類別成功匯入不拋出錯誤 |
| **專案結構** | **TC-STRUCT-001** | 測試 strategic_solver 目錄是否存在 | 測試於專案根目錄執行 | 1. 檢查 `strategic_solver` 目錄是否存在 | 檔案路徑 | 目錄存在 |
| **專案結構** | **TC-STRUCT-002** | 測試 __init__.py 檔案是否存在 | `strategic_solver` 目錄存在 | 1. 檢查 `strategic_solver/__init__.py` 檔案是否存在 | 檔案路徑 | `__init__.py` 存在 |
| **專案結構** | **TC-STRUCT-003** | 測試 agent.py 檔案是否存在 | `strategic_solver` 目錄存在 | 1. 檢查 `strategic_solver/agent.py` 檔案是否存在 | 檔案路徑 | `agent.py` 存在 |
| **專案結構** | **TC-STRUCT-004** | 測試 .env.example 檔案是否存在 | `strategic_solver` 目錄存在 | 1. 檢查 `strategic_solver/.env.example` 檔案是否存在 | 檔案路徑 | `.env.example` 存在 |
| **專案結構** | **TC-STRUCT-005** | 測試 __init__.py 的內容是否正確 | `__init__.py` 檔案存在 | 1. 讀取檔案內容<br>2. 檢查是否包含 "Strategic Problem Solver" 與 "Tutorial 12" | `__init__.py` 內容 | 檔案內容符合預期 |
| **專案結構** | **TC-STRUCT-006** | 測試 .env.example 是否包含必要的變數 | `.env.example` 檔案存在 | 1. 讀取檔案內容<br>2. 檢查是否包含 "GOOGLE_API_KEY" 與 "GOOGLE_GENAI_USE_VERTEXAI" | `.env.example` 內容 | 檔案內容符合預期 |
| **專案結構** | **TC-STRUCT-007** | 測試 agent.py 是否為一個有效的 Python 檔案 | `agent.py` 檔案存在 | 1. 匯入 `strategic_solver.agent`<br>2. 檢查 `__file__` 屬性是否以 "agent.py" 結尾 | `strategic_solver.agent` 模組 | `agent.py` 是一個有效的 Python 模組 |
| **工具定義** | **TC-TOOL-001** | 測試工具函式是否能被匯入 | 工具函式定義於 `agent.py` | 1. 從 `strategic_solver.agent` 匯入所有工具函式<br>2. 檢查每個工具是否為可呼叫的函式 | 工具函式 | 所有工具函式皆可成功匯入且為可呼叫狀態 |
| **工具定義** | **TC-TOOL-002** | 測試工具是否包含適當的文件字串 | 工具函式已匯入 | 1. 檢查每個工具函式的 `__doc__` 屬性<br>2. 驗證文件字串內容是否包含預期的描述 | 工具函式 | 所有工具都具備描述其功能的正確文件字串 |

## 整合測試 (`tests/test_integration.py`)

此部分涵蓋對完整工作流程、代理互動、工具組合及錯誤處理的端到端測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **規劃器整合** | **TC-INTEG-001** | 測試 BuiltInPlanner 代理的實例化與配置 | `builtin_planner_agent` 已匯入 | 1. 驗證代理不為 `None`<br>2. 檢查名稱、模型、工具數量<br>3. 確認規劃器存在且有 `thinking_config` | `builtin_planner_agent` | 代理已正確配置 |
| **規劃器整合** | **TC-INTEG-002** | 測試 PlanReActPlanner 代理的實例化與配置 | `plan_react_agent` 已匯入 | 1. 驗證代理不為 `None`<br>2. 檢查名稱、模型、工具數量<br>3. 確認規劃器為 `PlanReActPlanner` | `plan_react_agent` | 代理已正確配置 |
| **工具整合** | **TC-INTEG-003** | 測試市場分析與 ROI 計算的整合 | `analyze_market`, `calculate_roi` 已匯入 | 1. 執行市場分析<br>2. 從結果中提取成長率<br>3. 使用成長率計算 ROI | "healthcare", "North America", 100000, 5 | 市場分析與 ROI 計算皆成功，且 ROI 為正數 |
| **工具整合** | **TC-INTEG-004** | 測試風險評估與策略發展的整合 | `assess_risk`, `save_strategy_report` 已匯入 | 1. 評估風險<br>2. 根據風險等級建立策略<br>3. 儲存策略報告 | `risk_factors` 列表 | 風險評估與報告儲存皆成功，報告內容包含策略 |
| **工具整合** | **TC-INTEG-005** | 測試完整的業務分析工作流程 | 所有工具已匯入 | 1. 市場分析<br>2. ROI 計算<br>3. 風險評估<br>4. 產生綜合策略<br>5. 儲存報告 | "finance", "Asia", 500000, 3 | 所有步驟皆成功，最終報告包含所有分析結果 |
| **錯誤處理** | **TC-ERR-001** | 測試工具錯誤不會中斷整體工作流程 | `calculate_roi`, `assess_risk`, `analyze_market` 已匯入 | 1. 使用無效輸入呼叫 `calculate_roi`<br>2. 使用空列表呼叫 `assess_risk`<br>3. 呼叫 `analyze_market` | 無效投資金額 (-1000) | `calculate_roi` 回傳錯誤，但後續的風險評估與市場分析仍成功執行 |
| **錯誤處理** | **TC-ERR-002** | 測試多步驟工作流程中部分失敗的處理 | 所有工具已匯入 | 1. 成功執行市場分析<br>2. 使用無效輸入執行 ROI 計算使其失敗<br>3. 成功執行風險評估<br>4. 儲存包含成功與失敗結果的策略 | 零投資金額 (0) | 報告成功儲存，且內容正確反映了部分成功、部分失敗的分析結果 |
| **規劃器比較** | **TC-COMP-001** | 測試不同規劃器之間的指令差異 | 所有代理已匯入 | 1. 取得各規劃器代理的指令<br>2. 比較指令內容是否不同<br>3. 驗證各指令是否包含其獨特關鍵字 | 代理物件 | 三個規劃器的指令皆不相同且具備獨特性 |
| **規劃器比較** | **TC-COMP-002** | 測試規劃器是否具備適當的溫度設定 | 所有代理已匯入 | 1. 檢查 `builtin_planner_agent` 的溫度設定<br>2. 檢查 `strategic_planner_agent` 的溫度設定<br>3. 檢查 `plan_react_agent` 的溫度設定 | 代理物件 | 溫度設定符合預期 (0.3, 0.3, 0.4) |
| **規劃器比較** | **TC-COMP-003** | 測試規劃器是否具備唯一的輸出鍵 | 所有代理已匯入 | 1. 取得所有代理的輸出鍵<br>2. 驗證輸出鍵列表中的所有項目皆為唯一 | 代理物件 | 所有輸出鍵皆不重複 |

## 業務分析工具測試 (`tests/test_tool.py`)

此部分涵蓋對每個獨立業務分析工具的單元測試，確保其功能正確性與錯誤處理能力。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **市場分析** | **TC-TOOL-101** | 測試醫療保健產業的市場分析 | `analyze_market` 已匯入 | 1. 呼叫 `analyze_market` 函式 | `industry="healthcare"`, `region="North America"` | 回傳成功狀態，分析報告包含產業、地區、成長率與競爭程度 |
| **市場分析** | **TC-TOOL-102** | 測試金融產業的市場分析 | `analyze_market` 已匯入 | 1. 呼叫 `analyze_market` 函式 | `industry="finance"`, `region="Europe"` | 回傳成功狀態，分析報告包含金融科技趨勢 |
| **市場分析** | **TC-TOOL-103** | 測試未知產業的市場分析 | `analyze_market` 已匯入 | 1. 呼叫 `analyze_market` 函式 | `industry="unknown"`, `region="Global"` | 回傳成功狀態，並提供預設的成長率與競爭程度 |
| **市場分析** | **TC-TOOL-104** | 測試市場分析中的錯誤處理 | `analyze_market` 已匯入 | 1. 使用任意測試數據呼叫函式 | `industry="test"`, `region="test"` | 函式優雅地處理所有輸入，回傳成功狀態 |
| **ROI 計算** | **TC-TOOL-201** | 測試正報酬率的 ROI 計算 | `calculate_roi` 已匯入 | 1. 呼叫 `calculate_roi` 函式 | `investment=10000`, `return_rate=8`, `years=5` | 回傳成功狀態，ROI 百分比為正數，並包含年度明細 |
| **ROI 計算** | **TC-TOOL-202** | 測試零年份的 ROI 計算 | `calculate_roi` 已匯入 | 1. 呼叫 `calculate_roi` 函式 | `years=0` | 回傳錯誤狀態，錯誤訊息提示年份必須為正數 |
| **ROI 計算** | **TC-TOOL-203** | 測試負投資額的 ROI 計算 | `calculate_roi` 已匯入 | 1. 呼叫 `calculate_roi` 函式 | `investment=-1000` | 回傳錯誤狀態，錯誤訊息提示投資額必須為正數 |
| **ROI 計算** | **TC-TOOL-204** | 測試高報酬率的 ROI 計算 | `calculate_roi` 已匯入 | 1. 呼叫 `calculate_roi` 函式 | `investment=50000`, `return_rate=25`, `years=3` | 回傳成功狀態，ROI 百分比顯著高於 50% |
| **ROI 計算** | **TC-TOOL-205** | 測試年度明細是否計算正確 | `calculate_roi` 已匯入 | 1. 呼叫 `calculate_roi` 函式 | `investment=1000`, `return_rate=10`, `years=2` | 年度明細包含兩年，且第二年的價值高於第一年 |
| **風險評估** | **TC-TOOL-301** | 測試高風險因子的風險評估 | `assess_risk` 已匯入 | 1. 呼叫 `assess_risk` 函式 | 高風險因子列表 | 回傳成功狀態，風險等級為 "High" 或 "Medium"，並提供緩解建議 |
| **風險評估** | **TC-TOOL-302** | 測試低風險因子的風險評估 | `assess_risk` 已匯入 | 1. 呼叫 `assess_risk` 函式 | 低風險因子列表 | 回傳成功狀態，風險等級為 "Low"，平均分數低於 5 |
| **風險評估** | **TC-TOOL-303** | 測試空因子列表的風險評估 | `assess_risk` 已匯入 | 1. 呼叫 `assess_risk` 函式 | `[]` (空列表) | 回傳成功狀態，平均分數為預設值 5.0 |
| **風險評估** | **TC-TOOL-304** | 測試混合風險因子的風險評估 | `assess_risk` 已匯入 | 1. 呼叫 `assess_risk` 函式 | 混合風險因子列表 | 回傳成功狀態，平均分數介於 5 到 7 之間 |
| **風險評估** | **TC-TOOL-305** | 測試未知風險因子的風險評估 | `assess_risk` 已匯入 | 1. 呼叫 `assess_risk` 函式 | 未知因子列表 | 回傳成功狀態，所有未知因子的分數皆為預設值 5 |
| **報告儲存** | **TC-TOOL-401** | 測試策略報告的成功儲存 | `save_strategy_report` 已匯入 | 1. 呼叫 `save_strategy_report` 函式 | 測試問題與策略 | 回傳成功狀態，檔名包含 "strategy_"，且 `mock_context` 中增加一筆報告 |
| **報告儲存** | **TC-TOOL-402** | 測試儲存的報告是否包含正確的內容 | `save_strategy_report` 已匯入 | 1. 呼叫 `save_strategy_report` 函式 | 問題與策略內容 | 儲存的報告內容包含傳入的問題、策略及標題 |
| **報告儲存** | **TC-TOOL-403** | 測試策略報告儲存中的錯誤處理 | `save_strategy_report` 已匯入 | 1. 模擬 `mock_context` 拋出例外<br>2. 呼叫 `save_strategy_report` | 測試問題與策略 | 回傳錯誤狀態，並包含錯誤訊息 |

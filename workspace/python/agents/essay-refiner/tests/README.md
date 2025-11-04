# 詳細測試案例範本

## 簡介

此文件提供了一個詳細的測試案例範本，旨在為專案建立清晰、一致且全面的測試文件。使用此範本可以幫助開發者和測試人員標準化測試流程，確保所有關鍵功能都得到充分的驗證。

## Essay Refiner Agent 測試 (`tests/test_agent.py`)

此部分涵蓋對 Essay Refiner Agent 的測試，確保各個代理及整體系統結構的正確性。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **獨立代理測試** | **TC-AGENT-001** | 測試 `root_agent` 是否已正確設定 | `root_agent` 已被定義 | 1. 檢查 `root_agent.name`<br>2. 檢查 `root_agent.sub_agents` 數量<br>3. 檢查子代理的名稱 | None | `root_agent` 的名稱應為 "EssayRefinementSystem"，且包含 "InitialWriter" 和 "RefinementLoop" 兩個子代理。 |
| **獨立代理測試** | **TC-AGENT-002** | 測試 `InitialWriter` 代理的設定 | `initial_writer` 已被定義 | 1. 檢查 `initial_writer.name`<br>2. 檢查 `initial_writer.model`<br>3. 檢查 `initial_writer.output_key`<br>4. 檢查指令內容 | None | `initial_writer` 的名稱應為 "InitialWriter"，模型為 "gemini-2.0-flash"，輸出鍵為 "current_essay"，且指令包含 "first draft" 和 "3-4 paragraphs"。 |
| **獨立代理測試** | **TC-AGENT-003** | 測試 `Critic` 代理的設定 | `critic` 已被定義 | 1. 檢查 `critic.name`<br>2. 檢查 `critic.model`<br>3. 檢查 `critic.output_key`<br>4. 檢查指令內容 | None | `critic` 的名稱應為 "Critic"，模型為 "gemini-2.0-flash"，輸出鍵為 "critique"，且指令包含 "evaluation criteria" 和 "approved - essay is complete"。 |
| **獨立代理測試** | **TC-AGENT-004** | 測試 `Refiner` 代理的設定 | `refiner` 已被定義 | 1. 檢查 `refiner.name`<br>2. 檢查 `refiner.model`<br>3. 檢查 `refiner.output_key`<br>4. 檢查工具數量<br>5. 檢查指令內容 | None | `refiner` 的名稱應為 "Refiner"，模型為 "gemini-2.0-flash"，輸出鍵為 "current_essay"，擁有 1 個工具，且指令包含 "exit_loop" 和 "APPROVED - Essay is complete"。 |
| **獨立代理測試** | **TC-AGENT-005** | 測試 `LoopAgent` 的設定 | `refinement_loop` 已被定義 | 1. 檢查 `refinement_loop.name`<br>2. 檢查 `refinement_loop.sub_agents` 數量<br>3. 檢查 `refinement_loop.max_iterations`<br>4. 檢查子代理的名稱 | None | `refinement_loop` 的名稱應為 "RefinementLoop"，最大迭代次數為 5，且包含 "Critic" 和 "Refiner" 兩個子代理。 |
| **循序代理結構測試** | **TC-STRUCT-001** | 測試完整系統是否具有正確的結構 | `essay_refinement_system` 已被定義 | 1. 檢查 `essay_refinement_system.name`<br>2. 檢查 `essay_refinement_system.sub_agents` 數量<br>3. 檢查各階段的代理名稱和類型 | None | `essay_refinement_system` 的名稱應為 "EssayRefinementSystem"，包含 "InitialWriter" 和 "RefinementLoop" 兩個階段，且 `RefinementLoop` 的最大迭代次數為 5。 |
| **循環代理邏輯測試** | **TC-LOGIC-001** | 測試循環是否有適當的安全限制 | `refinement_loop` 已被定義 | 1. 檢查 `refinement_loop.max_iterations` | None | `refinement_loop.max_iterations` 應為 5。 |
| **循環代理邏輯測試** | **TC-LOGIC-002** | 測試 `exit_loop` 工具函式 | `exit_loop` 已被定義 | 1. 模擬 `ToolContext`<br>2. 呼叫 `exit_loop` 函式<br>3. 檢查回傳結果 | 模擬的 `ToolContext` | `exit_loop` 應將 `end_of_agent` 設為 `True`，並回傳成功的訊息。 |
| **狀態管理測試** | **TC-STATE-001** | 測試輸出鍵是否一致地用於狀態管理 | `initial_writer`, `refiner`, `critic` 已被定義 | 1. 檢查 `initial_writer.output_key`<br>2. 檢查 `refiner.output_key`<br>3. 檢查 `critic.output_key` | None | `initial_writer` 和 `refiner` 的輸出鍵應為 "current_essay"，`critic` 的輸出鍵應為 "critique"。 |
| **代理指令測試** | **TC-INSTR-001** | 測試初始寫手的指令是否完整 | `initial_writer` 已被定義 | 1. 檢查指令是否包含所有必要片語 | None | 指令應包含 "creative writer", "first draft", "3-4 paragraphs" 等關鍵片語。 |
| **工具整合測試** | **TC-TOOL-001** | 測試優化器代理是否擁有 `exit_loop` 工具 | `refiner` 已被定義 | 1. 檢查 `refiner.tools` 數量<br>2. 檢查工具是否為 `exit_loop` 函式 | None | `refiner` 應擁有 1 個工具，且該工具為 `exit_loop`。 |
| **系統整合測試** | **TC-SYS-001** | 測試所有代理是否能無誤地匯入 | None | 1. 從 `essay_refiner.agent` 匯入所有代理 | None | 所有代理應能成功匯入且不為 `None`。 |
| **設定驗證測試** | **TC-CONF-001** | 測試所有代理是否使用相同的模型 | `initial_writer`, `critic`, `refiner` 已被定義 | 1. 檢查各代理的 `model` 屬性 | None | 所有代理的模型應為 "gemini-2.0-flash"。 |

---

### **欄位說明**

*   **群組**: 測試案例所屬的功能子群組或類別。例如：`獨立代理測試`、`系統整合測試`。
*   **測試案例編號**: 唯一的測試案例識別碼。建議格式為 `TC-[模組]-[編號]`，例如 `TC-AGENT-001`。
*   **描述**: 對此測試案例目標的簡潔說明。
*   **前置條件**: 執行測試前系統或環境必須處於的狀態。
*   **測試步驟**: 執行測試所需遵循的具體步驟，應清晰且可重複。
*   **測試數據**: 在測試步驟中使用的具體輸入數據。
*   **預期結果**: 在成功執行測試步驟後，系統應顯示的確切結果或狀態。

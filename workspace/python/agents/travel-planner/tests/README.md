# 詳細測試案例說明

## 簡介

此文件提供了對 `travel-planner` 代理測試案例的詳細說明，旨在為專案建立清晰、一致且全面的測試文件。

## 代理功能測試 (`tests/test_agent.py`)

此部分涵蓋對旅遊規劃系統中各個代理模組的整合測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **獨立代理配置** | **TC-AGENT-001** | 測試 `flight_finder` 代理的配置 | `flight_finder` 代理已定義 | 1. 檢查代理名稱<br>2. 檢查模型<br>3. 檢查描述<br>4. 檢查指令內容<br>5. 檢查輸出鍵 | None | 名稱、模型、描述、指令和輸出鍵符合預期設定 |
| **獨立代理配置** | **TC-AGENT-002** | 測試 `hotel_finder` 代理的配置 | `hotel_finder` 代理已定義 | 1. 檢查代理名稱<br>2. 檢查模型<br>3. 檢查描述<br>4. 檢查指令內容<br>5. 檢查輸出鍵 | None | 名稱、模型、描述、指令和輸出鍵符合預期設定 |
| **獨立代理配置** | **TC-AGENT-003** | 測試 `activity_finder` 代理的配置 | `activity_finder` 代理已定義 | 1. 檢查代理名稱<br>2. 檢查模型<br>3. 檢查描述<br>4. 檢查指令內容<br>5. 檢查輸出鍵 | None | 名稱、模型、描述、指令和輸出鍵符合預期設定 |
| **獨立代理配置** | **TC-AGENT-004** | 測試所有代理是否都具有唯一的輸出鍵 | 所有搜索代理已定義 | 收集所有代理的輸出鍵 | None | 輸出鍵集合的大小與輸出鍵列表的長度相同 |
| **獨立代理配置** | **TC-AGENT-005** | 測試所有搜索代理是否都定義了輸出鍵 | 所有搜索代理已定義 | 檢查每個搜索代理的 `output_key` 屬性 | None | `output_key` 屬性不為 `None` |
| **ParallelAgent 結構** | **TC-AGENT-006** | 測試 `parallel_search` 是否為 `ParallelAgent` | `parallel_search` 已定義 | 檢查 `parallel_search` 的實例類型 | None | `parallel_search` 是 `ParallelAgent` 的一個實例 |
| **ParallelAgent 結構** | **TC-AGENT-007** | 測試並行搜索代理的名稱 | `parallel_search` 已定義 | 檢查 `parallel_search.name` 屬性 | None | 名稱為 "ParallelSearch" |
| **ParallelAgent 結構** | **TC-AGENT-008** | 測試並行搜索是否正好有 3 個子代理 | `parallel_search` 已定義 | 檢查 `parallel_search.sub_agents` 的長度 | None | 長度為 3 |
| **ParallelAgent 結構** | **TC-AGENT-009** | 測試並行搜索是否具有正確的子代理 | `parallel_search` 已定義 | 比較子代理名稱與預期列表 | None | 子代理名稱集合與預期相符 |
| **ParallelAgent 結構** | **TC-AGENT-010** | 測試並行搜索的描述 | `parallel_search` 已定義 | 檢查描述中是否包含 "concurrently" | None | 描述包含 "concurrently" |
| **SequentialAgent 結構** | **TC-AGENT-011** | 測試 `travel_planning_system` 是否為 `SequentialAgent` | `travel_planning_system` 已定義 | 檢查 `travel_planning_system` 的實例類型 | None | `travel_planning_system` 是 `SequentialAgent` 的一個實例 |
| **SequentialAgent 結構** | **TC-AGENT-012** | 測試旅遊規劃系統的名稱 | `travel_planning_system` 已定義 | 檢查 `travel_planning_system.name` 屬性 | None | 名稱為 "TravelPlanningSystem" |
| **SequentialAgent 結構** | **TC-AGENT-013** | 測試旅遊規劃系統是否正好有 2 個子代理 | `travel_planning_system` 已定義 | 檢查 `travel_planning_system.sub_agents` 的長度 | None | 長度為 2 |
| **SequentialAgent 結構** | **TC-AGENT-014** | 測試序列中的第一個代理是否為並行搜索 | `travel_planning_system` 已定義 | 檢查第一個子代理的實例類型 | None | 第一個子代理是 `ParallelAgent` 的一個實例 |
| **SequentialAgent 結構** | **TC-AGENT-015** | 測試序列中的第二個代理是否為行程建立器 | `travel_planning_system` 已定義 | 檢查第二個子代理是否為 `itinerary_builder` | None | 第二個子代理是 `itinerary_builder` |
| **行程建立器** | **TC-AGENT-016** | 測試行程建立器代理的配置 | `itinerary_builder` 已定義 | 1. 檢查代理名稱<br>2. 檢查模型<br>3. 檢查描述<br>4. 檢查輸出鍵 | None | 名稱、模型、描述和輸出鍵符合預期設定 |
| **行程建立器** | **TC-AGENT-017** | 測試行程建立器的指令是否引用了所有狀態鍵 | `itinerary_builder` 已定義 | 檢查指令字串是否包含預期的狀態鍵 | None | 指令包含 "{flight_options}", "{hotel_options}", 和 "{activity_options}" |
| **根代理** | **TC-AGENT-018** | 測試 `root_agent` 是否為旅遊規劃系統 | `root_agent` 已定義 | 檢查 `root_agent` 是否等於 `travel_planning_system` | None | `root_agent` 與 `travel_planning_system` 是同一個物件 |
| **根代理** | **TC-AGENT-019** | 測試 `root_agent` 是否為 `SequentialAgent` | `root_agent` 已定義 | 檢查 `root_agent` 的實例類型 | None | `root_agent` 是 `SequentialAgent` 的一個實例 |
| **狀態管理** | **TC-AGENT-020** | 測試並行代理是否將狀態保存以供行程建立器讀取 | `parallel_search` 和 `itinerary_builder` 已定義 | 檢查 `itinerary_builder` 的指令是否包含並行代理的輸出鍵 | None | 指令中包含了所有並行代理的輸出鍵 |
| **狀態管理** | **TC-AGENT-021** | 測試流程中是否存在循環依賴 | 所有代理已定義 | 檢查行程建立器的指令是否只依賴於並行代理的輸出 | None | 依賴關係正確，無循環依賴 |
| **代理指令** | **TC-AGENT-022** | 測試 `flight_finder` 指令的格式 | `flight_finder` 已定義 | 檢查指令中是否包含特定關鍵字 | None | 指令包含預期的關鍵字，如 "flight search specialist" |
| **代理指令** | **TC-AGENT-023** | 測試 `hotel_finder` 指令的格式 | `hotel_finder` 已定義 | 檢查指令中是否包含特定關鍵字 | None | 指令包含預期的關鍵字，如 "hotel search specialist" |
| **代理指令** | **TC-AGENT-024** | 測試 `activity_finder` 指令的格式 | `activity_finder` 已定義 | 檢查指令中是否包含特定關鍵字 | None | 指令包含預期的關鍵字，如 "local activities expert" |
| **代理指令** | **TC-AGENT-025** | 測試行程建立器的指令是否全面 | `itinerary_builder` 已定義 | 檢查指令中是否包含特定關鍵字 | None | 指令包含預期的關鍵字，如 "complete, well-organized itinerary" |
| **代理指令** | **TC-AGENT-026** | 測試所有指令是否都強調輸出格式 | 所有代理已定義 | 檢查每個指令是否包含格式化相關的詞語 | None | 所有指令都包含格式化指導 |
| **代理整合** | **TC-AGENT-027** | 測試完整的流程是否可以在沒有錯誤的情況下實例化 | `travel_planning_system` 已定義 | 嘗試導入 `travel_planning_system` | None | 導入成功，無異常引發 |
| **代理整合** | **TC-AGENT-028** | 測試流程是否具有 ADK API 的有效配置 | `root_agent` 已定義 | 檢查 `root_agent` 的必要屬性 | None | `root_agent` 具有 `name`, `description`, `sub_agents` 屬性 |
| **代理整合** | **TC-AGENT-029** | 測試代理之間的狀態流是否已正確配置 | `parallel_search` 和 `itinerary_builder` 已定義 | 檢查並行代理的輸出鍵和行程建立器的指令 | None | 狀態流配置正確 |

## 導入測試 (`tests/test_imports.py`)

此部分涵蓋對專案模組導入的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **導入測試** | **TC-IMPRT-001** | 測試 `google.adk.agents` 是否可以被導入 | Python 環境已設定 | `importlib.util.find_spec("google.adk.agents")` | None | `spec` 不為 `None` |
| **導入測試** | **TC-IMPRT-002** | 測試 `travel_planner.agent` 模組是否可以被導入 | 專案路徑已設定 | `importlib.util.find_spec("travel_planner.agent")` | None | `spec` 不為 `None` |
| **導入測試** | **TC-IMPRT-003** | 測試 `root_agent` 是否已定義且可訪問 | `travel_planner.agent` 模組可導入 | `from travel_planner.agent import root_agent` | None | `root_agent` 不為 `None`，且無 `ImportError` |
| **導入測試** | **TC-IMPRT-004** | 測試 `__future__ annotations` 是否已導入 | `travel_planner.agent` 模組可導入 | 檢查 `travel_planner.agent` 模組是否具有 `root_agent` 屬性 | None | `hasattr(travel_planner.agent, "root_agent")` 為 `True` |

## 結構測試 (`tests/test_structure.py`)

此部分涵蓋對專案檔案和目錄結構的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **結構測試** | **TC-STRC-001** | 測試 `google.adk.agents` 是否可以被導入 | Python 環境已設定 | `importlib.util.find_spec("google.adk.agents")` | None | `spec` 不為 `None` |
| **結構測試** | **TC-STRC-002** | 測試 `travel_planner.agent` 模組是否可以被導入 | 專案路徑已設定 | `importlib.util.find_spec("travel_planner.agent")` | None | `spec` 不為 `None` |
| **結構測試** | **TC-STRC-003** | 測試 `root_agent` 是否已定義且可訪問 | `travel_planner.agent` 模組可導入 | `from travel_planner.agent import root_agent` | None | `root_agent` 不為 `None`，且無 `ImportError` |
| **結構測試** | **TC-STRC-004** | 測試 `__future__ annotations` 是否已導入 | `travel_planner.agent` 模組可導入 | 檢查 `travel_planner.agent` 模組是否具有 `root_agent` 屬性 | None | `hasattr(travel_planner.agent, "root_agent")` 為 `True` |

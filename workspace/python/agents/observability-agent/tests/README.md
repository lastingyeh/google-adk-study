# Observability Agent 測試案例

## 簡介

此文件提供了 `observability-agent` 專案的詳細測試案例說明，旨在確保所有關鍵功能都得到充分的驗證。

## Agent 設定與初始化 (`tests/test_agent.py`)

此部分涵蓋對 `observability_agent` 的設定與初始化進行測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Agent 設定** | **TC-AGENT-001** | 測試 `CustomerServiceMonitor` 是否能正確初始化。 | None | 1. 建立 `CustomerServiceMonitor` 實例。 | None | `monitor` 物件已建立，`agent` 是 `Agent` 的實例，`events` 列表為空，`runner` 物件已建立。 |
| **Agent 設定** | **TC-AGENT-002** | 測試代理程式是否有正確的名稱。 | None | 1. 建立 `CustomerServiceMonitor` 實例。<br>2. 檢查 `agent.name` 屬性。 | None | 代理程式名稱應為 `'customer_service'`。 |
| **Agent 設定** | **TC-AGENT-003** | 測試代理程式是否使用正確的模型。 | None | 1. 建立 `CustomerServiceMonitor` 實例。<br>2. 檢查 `agent.model` 屬性。 | None | 模型名稱應包含 `'gemini'`。 |
| **Agent 設定** | **TC-AGENT-004** | 測試代理程式是否具備必要的工具。 | None | 1. 建立 `CustomerServiceMonitor` 實例。<br>2. 檢查 `agent.tools` 屬性。 | None | 工具列表不為 `None` 且數量為 3。 |
| **Agent 設定** | **TC-AGENT-005** | 測試代理程式是否已設定指令。 | None | 1. 建立 `CustomerServiceMonitor` 實例。<br>2. 檢查 `agent.instruction` 屬性。 | None | 指令不為 `None`，長度大於 0，且包含 `'customer service'`。 |
| **Agent 設定** | **TC-AGENT-006** | 測試 `root_agent` 是否已正確匯出。 | None | 1. 匯入 `root_agent`。<br>2. 檢查其型別與名稱。 | None | `root_agent` 不為 `None`，是 `Agent` 的實例，且名稱為 `'customer_service'`。 |
| **Agent 設定** | **TC-AGENT-007** | 測試代理程式是否有描述。 | None | 1. 建立 `CustomerServiceMonitor` 實例。<br>2. 檢查 `agent.description` 屬性。 | None | 描述不為 `None` 且包含 `'event tracking'`。 |
| **工具設定** | **TC-AGENT-008** | 測試所有工具是否皆可呼叫。 | None | 1. 建立 `CustomerServiceMonitor` 實例。<br>2. 迭代檢查每個工具是否可呼叫。 | None | 所有工具都是可呼叫的函式。 |
| **工具設定** | **TC-AGENT-009** | 測試 `check_order_status` 工具是否存在。 | None | 1. 建立 `CustomerServiceMonitor` 實例。<br>2. 檢查工具名稱列表。 | None | `'check_order_status'` 應在工具名稱列表中。 |
| **工具設定** | **TC-AGENT-010** | 測試 `process_refund` 工具是否存在。 | None | 1. 建立 `CustomerServiceMonitor` 實例。<br>2. 檢查工具名稱列表。 | None | `'process_refund'` 應在工具名稱列表中。 |
| **工具設定** | **TC-AGENT-011** | 測試 `check_inventory` 工具是否存在。 | None | 1. 建立 `CustomerServiceMonitor` 實例。<br>2. 檢查工具名稱列表。 | None | `'check_inventory'` 應在工具名稱列表中。 |

## 事件追蹤功能 (`tests/test_events.py`)

此部分涵蓋對事件追蹤功能進行測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **事件記錄** | **TC-EVENTS-001** | 測試工具呼叫是否能正確記錄。 | None | 1. 建立 `CustomerServiceMonitor` 實例。<br>2. 呼叫 `_log_tool_call` 方法。 | `tool_name='test_tool'`, `arguments={'arg1': 'value1'}` | 事件數量為 1，且事件類型、工具名稱、參數皆正確。 |
| **事件記錄** | **TC-EVENTS-002** | 測試代理程式事件是否能正確記錄。 | None | 1. 建立 `CustomerServiceMonitor` 實例。<br>2. 呼叫 `_log_agent_event` 方法。 | `event_type='test_event'`, `data={'key': 'value'}` | 事件數量為 1，且事件類型與資料皆正確。 |
| **事件記錄** | **TC-EVENTS-003** | 測試事件是否包含時間戳。 | None | 1. 建立 `CustomerServiceMonitor` 實例。<br>2. 記錄一個事件。<br>3. 檢查事件內容。 | `tool_name='test_tool'` | 事件中包含 `'timestamp'` 欄位且為 ISO 格式。 |
| **事件記錄** | **TC-EVENTS-004** | 測試多個事件是否能正確記錄。 | None | 1. 建立 `CustomerServiceMonitor` 實例。<br>2. 記錄三個不同事件。 | None | 事件總數為 3，且內容依序正確。 |
| **事件報告** | **TC-EVENTS-005** | 測試事件摘要報告的生成。 | None | 1. 記錄數個事件。<br>2. 呼叫 `get_event_summary` 方法。 | None | 報告中包含標題、總事件數及各類型事件計數。 |
| **事件報告** | **TC-EVENTS-006** | 測試詳細時間軸的生成。 | None | 1. 記錄一個事件。<br>2. 呼叫 `get_detailed_timeline` 方法。 | `tool_name='test_tool'` | 報告中包含標題、事件類型及工具名稱。 |
| **事件報告** | **TC-EVENTS-007** | 測試摘要中的工具使用統計。 | None | 1. 記錄多個工具呼叫。<br>2. 呼叫 `get_event_summary` 方法。 | `tool_name='tool1'` (2次), `tool_name='tool2'` (1次) | 報告中包含各工具的呼叫次數統計。 |
| **事件報告** | **TC-EVENTS-008** | 測試報告中的升級追蹤。 | None | 1. 記錄一個升級事件。<br>2. 呼叫 `get_event_summary` 方法。 | `event_type='escalation'` | 報告中包含升級次數及原因。 |

## 匯入與模組結構 (`tests/test_imports.py`)

此部分涵蓋對匯入與模組結構進行測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **模組匯入** | **TC-IMPORTS-001** | 測試 `CustomerServiceMonitor` 是否能被匯入。 | None | 1. 從 `observability_agent` 匯入 `CustomerServiceMonitor`。 | None | 匯入成功，物件不為 `None`。 |
| **模組匯入** | **TC-IMPORTS-002** | 測試 `root_agent` 是否能被匯入。 | None | 1. 從 `observability_agent` 匯入 `root_agent`。 | None | 匯入成功，物件不為 `None`。 |
| **模組匯入** | **TC-IMPORTS-003** | 測試 `EventLogger` 是否能被匯入。 | None | 1. 從 `observability_agent` 匯入 `EventLogger`。 | None | 匯入成功，物件不為 `None`。 |
| **模組匯入** | **TC-IMPORTS-004** | 測試 `MetricsCollector` 是否能被匯入。 | None | 1. 從 `observability_agent` 匯入 `MetricsCollector`。 | None | 匯入成功，物件不為 `None`。 |
| **模組匯入** | **TC-IMPORTS-005** | 測試 `EventAlerter` 是否能被匯入。 | None | 1. 從 `observability_agent` 匯入 `EventAlerter`。 | None | 匯入成功，物件不為 `None`。 |
| **模組匯入** | **TC-IMPORTS-006** | 測試 `AgentMetrics` 是否能被匯入。 | None | 1. 從 `observability_agent` 匯入 `AgentMetrics`。 | None | 匯入成功，物件不為 `None`。 |
| **模組匯入** | **TC-IMPORTS-007** | 測試 `__all__` 的匯出是否正確。 | None | 1. 匯入 `observability_agent` 模組。<br>2. 檢查 `__all__` 變數。 | None | `__all__` 包含所有預期的公開物件。 |

## 可觀察性類別 (`tests/test_observability.py`)

此部分涵蓋對可觀察性類別（EventLogger、MetricsCollector、EventAlerter）進行測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **EventLogger** | **TC-OBS-001** | 測試 `EventLogger` 是否能正確初始化。 | None | 1. 建立 `EventLogger` 實例。 | None | 物件已建立，`logger` 屬性已設定。 |
| **EventLogger** | **TC-OBS-002** | 測試記錄包含內容的事件。 | None | 1. 建立包含內容的 `Event` 物件。<br>2. 呼叫 `log_event` 方法。 | `content` 包含 `types.Part` | 不應引發例外。 |
| **EventLogger** | **TC-OBS-003** | 測試記錄不含內容的事件。 | None | 1. 建立不含內容的 `Event` 物件。<br>2. 呼叫 `log_event` 方法。 | `content` 為 `None` | 不應引發例外。 |
| **MetricsCollector** | **TC-OBS-004** | 測試 `MetricsCollector` 是否能正確初始化。 | None | 1. 建立 `MetricsCollector` 實例。 | None | 物件已建立，`metrics` 字典為空。 |
| **MetricsCollector** | **TC-OBS-005** | 測試追蹤呼叫是否能建立指標項目。 | None | 1. 首次呼叫 `track_invocation`。 | `agent_name='test_agent'`, `latency=0.5` | `metrics` 字典中建立新項目，計數和延遲正確。 |
| **MetricsCollector** | **TC-OBS-006** | 測試追蹤多次呼叫。 | None | 1. 多次呼叫 `track_invocation`。 | `agent_name='test_agent'`, `latency=0.5` 及 `0.3` | 累加呼叫計數和總延遲。 |
| **MetricsCollector** | **TC-OBS-007** | 測試追蹤工具呼叫。 | None | 1. 呼叫 `track_invocation` 並傳入 `tool_calls`。 | `tool_calls=3` | 正確記錄工具呼叫次數。 |
| **MetricsCollector** | **TC-OBS-008** | 測試追蹤錯誤。 | None | 1. 呼叫 `track_invocation` 並傳入 `had_error=True`。 | `had_error=True` | 正確記錄錯誤次數。 |
| **MetricsCollector** | **TC-OBS-009** | 測試追蹤升級。 | None | 1. 呼叫 `track_invocation` 並傳入 `escalated=True`。 | `escalated=True` | 正確記錄升級次數。 |
| **MetricsCollector** | **TC-OBS-010** | 測試 `get_summary` 是否能計算正確的平均值。 | None | 1. 記錄指標後呼叫 `get_summary`。 | None | 計算出正確的平均延遲、錯誤率和升級率。 |
| **MetricsCollector** | **TC-OBS-011** | 測試對不存在的代理程式呼叫 `get_summary`。 | None | 1. 對不存在的代理程式名稱呼叫 `get_summary`。 | `agent_name='nonexistent'` | 應回傳空字典。 |
| **EventAlerter** | **TC-OBS-012** | 測試 `EventAlerter` 是否能正確初始化。 | None | 1. 建立 `EventAlerter` 實例。 | None | 物件已建立，`rules` 列表為空。 |
| **EventAlerter** | **TC-OBS-013** | 測試新增警報規則。 | None | 1. 呼叫 `add_rule` 方法。 | `condition=lambda e: True`, `alert_fn=lambda e: None` | 新規則被新增至 `rules` 列表中。 |
| **EventAlerter** | **TC-OBS-014** | 測試事件檢查在條件符合時是否能觸發警報。 | None | 1. 新增一個必定觸發的規則。<br>2. 呼叫 `check_event`。 | `condition=lambda e: True` | 對應的警報函式被呼叫。 |
| **EventAlerter** | **TC-OBS-015** | 測試事件檢查在條件不符合時不觸發警報。 | None | 1. 新增一個永不觸發的規則。<br>2. 呼叫 `check_event`。 | `condition=lambda e: False` | 警報函式不應被呼叫。 |
| **EventAlerter** | **TC-OBS-016** | 測試多個警報規則。 | None | 1. 新增多個規則。<br>2. 呼叫 `check_event`。 | `condition=lambda e: True` (多個) | 所有符合條件的警報都被觸發。 |
| **AgentMetrics** | **TC-OBS-017** | 測試 `AgentMetrics` 是否能以預設值初始化。 | None | 1. 建立 `AgentMetrics` 實例。 | None | 所有屬性應有正確的預設值（0 或 0.0）。 |
| **AgentMetrics** | **TC-OBS-018** | 測試 `AgentMetrics` 使用自訂值。 | None | 1. 建立 `AgentMetrics` 實例並傳入自訂值。 | `invocation_count=10`, `total_latency=5.5`, etc. | 物件能正確接收並儲存傳入的自訂值。 |

## 專案結構 (`tests/test_structure.py`)

此部分涵蓋對專案結構與必要檔案進行測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **專案結構** | **TC-STRUCT-001** | 測試所有必要的專案檔案是否存在。 | 專案已 clone | 1. 檢查指定的檔案列表是否存在於專案根目錄中。 | None | 所有核心檔案都存在於預期的位置。 |
| **專案結構** | **TC-STRUCT-002** | 測試 `observability_agent` 目錄是否為一個合法的 Python 套件。 | 專案已 clone | 1. 檢查 `observability_agent` 目錄下是否存在 `__init__.py` 檔案。 | None | `__init__.py` 存在，確認其為可匯入的套件。 |
| **專案結構** | **TC-STRUCT-003** | 測試 `tests` 目錄是否存在。 | 專案已 clone | 1. 檢查 `tests` 目錄是否存在於專案中。 | None | `tests` 目錄存在且為一個目錄。 |
| **專案結構** | **TC-STRUCT-004** | 測試 `pyproject.toml` 是否包含必要欄位。 | `pyproject.toml` 存在 | 1. 讀取 `pyproject.toml` 檔案內容。<br>2. 檢查是否包含特定字串。 | None | 檔案中包含 `[project]` 區塊、專案名稱及 `google-genai` 依賴項。 |
| **專案結構** | **TC-STRUCT-005** | 測試 `Makefile` 是否包含必要指令。 | `Makefile` 存在 | 1. 讀取 `Makefile` 檔案內容。<br>2. 檢查是否存在指定的 target。 | None | `Makefile` 中存在 `setup`、`dev`、`test` 等常用開發指令。 |

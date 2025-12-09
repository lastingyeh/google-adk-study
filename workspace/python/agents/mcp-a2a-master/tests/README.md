# 詳細測試案例文件

## 簡介

此文件提供了一個詳細的測試案例範本，旨在為專案建立清晰、一致且全面的測試文件。使用此範本可以幫助開發者和測試人員標準化測試流程，確保所有關鍵功能都得到充分的驗證。

## HostAgent 測試 (`tests/test_host_agent.py`)

此部分涵蓋對 HostAgent 的核心功能與配置的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TestHostAgentConfiguration** | **TC-HOST-001** | 測試 HostAgent 初始化 | 無 | 1. 匯入 HostAgent 類別<br>2. 建立 HostAgent 實例<br>3. 驗證實例是否成功建立且不為 None | None | 實例成功建立且不為 None |
| **TestHostAgentConfiguration** | **TC-HOST-002** | 測試系統指令是否載入 | 無 | 1. 建立 HostAgent 實例<br>2. 檢查 system_instruction 屬性是否存在<br>3. 驗證 system_instruction 是否為字串且不為空 | None | system_instruction 存在且內容正確 |
| **TestHostAgentConfiguration** | **TC-HOST-003** | 測試描述是否載入 | 無 | 1. 建立 HostAgent 實例<br>2. 檢查 description 屬性是否存在<br>3. 驗證 description 是否為字串且不為空 | None | description 存在且內容正確 |
| **TestHostAgentConfiguration** | **TC-HOST-004** | 測試 MCP Connector 是否初始化 | 無 | 1. 建立 HostAgent 實例<br>2. 檢查 MCPConnector 屬性是否存在<br>3. 驗證 MCPConnector 是否已初始化 | None | MCPConnector 存在且已初始化 |
| **TestHostAgentConfiguration** | **TC-HOST-005** | 測試 Agent Discovery 是否初始化 | 無 | 1. 建立 HostAgent 實例<br>2. 檢查 AgentDiscovery 屬性是否存在<br>3. 驗證 AgentDiscovery 是否已初始化 | None | AgentDiscovery 存在且已初始化 |
| **TestHostAgentConfiguration** | **TC-HOST-006** | 測試初始狀態 | 無 | 1. 建立 HostAgent 實例<br>2. 驗證 _agent 屬性初始為 None<br>3. 驗證 _runner 屬性初始為 None<br>4. 驗證 _user_id 屬性初始值正確 | None | 屬性初始狀態正確 |
| **TestHostAgentCreation** | **TC-HOST-007** | 測試 create 方法 | 無 | 1. 建立 HostAgent 實例<br>2. Mock MCPConnector.get_tools 方法以避免外部連接<br>3. 呼叫 agent.create() 方法<br>4. 驗證 _agent 和 _runner 屬性是否已建立 | None | _agent 和 _runner 已建立 |
| **TestHostAgentCreation** | **TC-HOST-008** | 測試 _build_agent 建立 LLM Agent | 無 | 1. 建立 HostAgent 實例<br>2. Mock MCPConnector.get_tools 方法<br>3. 呼叫 agent._build_agent() 方法<br>4. 驗證回傳物件是否為 LlmAgent 實例 | None | 回傳 LlmAgent 實例 |
| **TestHostAgentCreation** | **TC-HOST-009** | 測試 Agent 是否包含 Function Tools | 無 | 1. 建立 HostAgent 實例<br>2. Mock MCPConnector.get_tools 方法<br>3. 呼叫 agent._build_agent()<br>4. 驗證生成的 agent 是否包含 tools 屬性<br>5. 驗證 tools 數量是否正確 (至少包含 _delegate_task 和 _list_agents) | None | 包含正確數量的 tools |
| **TestHostAgentCreation** | **TC-HOST-010** | 測試 Agent 模型配置 | 無 | 1. 建立 HostAgent 實例<br>2. Mock MCPConnector.get_tools 方法<br>3. 呼叫 agent._build_agent()<br>4. 驗證 agent 名稱是否為 "host_agent"<br>5. 驗證 agent 使用的模型是否在允許的清單中 | None | Agent 名稱和模型配置正確 |
| **TestHostAgentTools** | **TC-HOST-011** | 測試 _list_agents 回傳列表 | 無 | 1. 建立 HostAgent 實例<br>2. Mock AgentDiscovery.list_agent_cards 方法回傳空列表<br>3. 呼叫 agent._list_agents()<br>4. 驗證回傳結果是否為列表型別 | None | 回傳結果為列表 |
| **TestHostAgentTools** | **TC-HOST-012** | 測試 _list_agents 與 mock agent cards | 無 | 1. 建立 HostAgent 實例<br>2. Mock AgentDiscovery.list_agent_cards 方法回傳包含 mock_agent_card 的列表<br>3. 呼叫 agent._list_agents()<br>4. 驗證回傳列表長度為 1<br>5. 驗證回傳的 agent 名稱是否正確 | mock_agent_card | 回傳正確的 agent 列表 |
| **TestHostAgentTools** | **TC-HOST-013** | 測試 _delegate_task 成功委派 | 無 | 1. 建立 HostAgent 實例<br>2. Mock AgentDiscovery 回傳有效的 agent cards<br>3. Mock AgentConnector 及其 send_task 方法回傳成功訊息<br>4. 呼叫 agent._delgate_task() 委派任務<br>5. 驗證回傳結果與預期相符 | agent_name="test_website_builder" | 回傳 "Task completed" |
| **TestHostAgentTools** | **TC-HOST-014** | 測試 _delegate_task 找不到 Agent | 無 | 1. 建立 HostAgent 實例<br>2. Mock AgentDiscovery 回傳空列表<br>3. 呼叫 agent._delgate_task() 嘗試委派給不存在的 agent<br>4. 驗證回傳錯誤訊息包含 "Agent not found" | agent_name="nonexistent_agent" | 回傳 "找不到代理 (Agent not found)" |
| **TestHostAgentInvoke** | **TC-HOST-015** | 測試 invoke 建立 session | 無 | 1. 建立 HostAgent 實例<br>2. Mock MCPConnector.get_tools<br>3. 呼叫 agent.create()<br>4. Mock runner.run_async 方法以回傳生成器<br>5. 呼叫 agent.invoke()<br>6. 驗證 invoke 過程回傳了結果 | "Test query" | 回傳至少一個結果 |
| **TestHostAgentExecutor** | **TC-HOST-016** | 測試 Executor 初始化 | 無 | 1. 匯入 HostAgentExecutor<br>2. 建立實例<br>3. 驗證實例是否存在且包含 agent 屬性 | None | 實例存在且屬性正確 |
| **TestHostAgentExecutor** | **TC-HOST-017** | 測試 Executor create 方法 | 無 | 1. 建立 HostAgentExecutor 實例<br>2. Mock executor.agent.create 方法<br>3. 呼叫 executor.create()<br>4. 驗證 agent.create 方法被呼叫一次 | None | agent.create 被呼叫 |

## 匯入測試 (`tests/test_imports.py`)

此部分涵蓋對所有模組的匯入功能測試，確保沒有循環相依或遺失的套件。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TestAgentImports** | **TC-IMP-001** | 測試 HostAgent 能否匯入 | 無 | 1. 嘗試匯入 HostAgent 類別<br>2. 驗證匯入成功<br>3. 若匯入失敗，使用 pytest.fail 報告錯誤 | None | 成功匯入 HostAgent |
| **TestAgentImports** | **TC-IMP-002** | 測試 HostAgentExecutor 能否匯入 | 無 | 1. 嘗試匯入 HostAgentExecutor 類別<br>2. 驗證匯入成功<br>3. 若匯入失敗，使用 pytest.fail 報告錯誤 | None | 成功匯入 HostAgentExecutor |
| **TestAgentImports** | **TC-IMP-003** | 測試 WebsiteBuilderSimple 能否匯入 | 無 | 1. 嘗試匯入 WebsiteBuilderSimple 類別<br>2. 驗證匯入成功<br>3. 若匯入失敗，使用 pytest.fail 報告錯誤 | None | 成功匯入 WebsiteBuilderSimple |
| **TestAgentImports** | **TC-IMP-004** | 測試 WebsiteBuilderSimpleAgentExecutor 能否匯入 | 無 | 1. 嘗試匯入 WebsiteBuilderSimpleAgentExecutor 類別<br>2. 驗證匯入成功<br>3. 若匯入失敗，使用 pytest.fail 報告錯誤 | None | 成功匯入 WebsiteBuilderSimpleAgentExecutor |
| **TestUtilitiesImports** | **TC-IMP-005** | 測試 AgentConnector 能否匯入 | 無 | 1. 嘗試匯入 AgentConnector 類別<br>2. 驗證匯入成功<br>3. 若匯入失敗，使用 pytest.fail 報告錯誤 | None | 成功匯入 AgentConnector |
| **TestUtilitiesImports** | **TC-IMP-006** | 測試 AgentDiscovery 能否匯入 | 無 | 1. 嘗試匯入 AgentDiscovery 類別<br>2. 驗證匯入成功<br>3. 若匯入失敗，使用 pytest.fail 報告錯誤 | None | 成功匯入 AgentDiscovery |
| **TestUtilitiesImports** | **TC-IMP-007** | 測試 MCPConnector 能否匯入 | 無 | 1. 嘗試匯入 MCPConnector 類別<br>2. 驗證匯入成功<br>3. 若匯入失敗，使用 pytest.fail 報告錯誤 | None | 成功匯入 MCPConnector |
| **TestUtilitiesImports** | **TC-IMP-008** | 測試 MCPDiscovery 能否匯入 | 無 | 1. 嘗試匯入 MCPDiscovery 類別<br>2. 驗證匯入成功<br>3. 若匯入失敗，使用 pytest.fail 報告錯誤 | None | 成功匯入 MCPDiscovery |
| **TestUtilitiesImports** | **TC-IMP-009** | 測試 file_loader 能否匯入 | 無 | 1. 嘗試匯入 load_instructions_file 函式<br>2. 驗證匯入成功<br>3. 若匯入失敗，使用 pytest.fail 報告錯誤 | None | 成功匯入 load_instructions_file |
| **TestDependenciesImports** | **TC-IMP-010** | 測試 Google ADK 相依套件能否匯入 | 無 | 1. 嘗試匯入 Google ADK 相關模組 (LlmAgent, Runner, FunctionTool, types)<br>2. 驗證所有模組匯入成功<br>3. 若匯入失敗，使用 pytest.fail 報告錯誤 | None | 成功匯入 Google ADK 模組 |
| **TestDependenciesImports** | **TC-IMP-011** | 測試 A2A SDK 相依套件能否匯入 | 無 | 1. 嘗試匯入 A2A SDK 相關模組 (AgentCard, Task, TaskState, A2AClient, AgentExecutor)<br>2. 驗證所有模組匯入成功<br>3. 若匯入失敗，使用 pytest.fail 報告錯誤 | None | 成功匯入 A2A SDK 模組 |
| **TestDependenciesImports** | **TC-IMP-012** | 測試 MCP 相依套件能否匯入 | 無 | 1. 嘗試匯入 MCP 相關模組 (MCPToolset, StdioConnectionParams, StdioServerParameters)<br>2. 驗證所有模組匯入成功<br>3. 若匯入失敗，使用 pytest.fail 報告錯誤 | None | 成功匯入 MCP 模組 |
| **TestDependenciesImports** | **TC-IMP-013** | 測試其他相依套件能否匯入 | 無 | 1. 嘗試匯入其他必要套件 (httpx, asyncio, pydantic, rich)<br>2. 驗證所有套件匯入成功<br>3. 若匯入失敗，使用 pytest.fail 報告錯誤 | None | 成功匯入其他相依套件 |

## 整合測試 (`tests/test_integration.py`)

此部分涵蓋對多個元件協同工作的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TestHostAgentMCPIntegration** | **TC-INT-001** | 測試 HostAgent 載入 MCP 工具 | 無 | 1. 建立 HostAgent 實例<br>2. Mock MCPConnector.get_tools 方法回傳包含模擬工具的列表<br>3. 呼叫 agent._build_agent() 觸發工具載入<br>4. 驗證 agent.tools 列表長度（應包含 function tools 和 MCP tools）<br>5. 驗證 mock_get_tools 方法被呼叫一次 | None | 工具正確載入且包含 MCP 工具 |
| **TestHostAgentMCPIntegration** | **TC-INT-002** | 測試 MCP Connector 與 Discovery 整合 | 無 | 1. 建立 MCPConnector 實例<br>2. 驗證 connector.discovery 屬性已初始化<br>3. 驗證 discovery 物件包含 list_servers 方法 | None | Discovery 正確整合 |
| **TestHostAgentA2AIntegration** | **TC-INT-003** | 測試 Agent Discovery 整合 | 無 | 1. 建立 HostAgent 實例<br>2. Mock AgentDiscovery.list_agent_cards 回傳模擬的 agent card<br>3. 呼叫 agent._list_agents()<br>4. 驗證回傳的列表長度和內容是否正確 | None | 回傳正確的 agent 列表 |
| **TestHostAgentA2AIntegration** | **TC-INT-004** | 測試任務委派到子 Agent | 無 | 1. 建立 HostAgent 實例<br>2. Mock AgentDiscovery 回傳有效的 agent cards<br>3. Mock AgentConnector 及其 send_task 方法回傳成功結果<br>4. 呼叫 agent._delgate_task()<br>5. 驗證回傳結果包含預期的成功訊息<br>6. 驗證 send_task 方法被呼叫一次 | agent_name="test_website_builder" | 回傳包含成功訊息 |
| **TestAgentExecutorIntegration** | **TC-INT-005** | 測試 HostAgentExecutor 執行 | 無 | 1. 建立 HostAgentExecutor 實例並初始化<br>2. Mock RequestContext 和 EventQueue<br>3. Mock agent.invoke 方法回傳模擬的回應<br>4. 呼叫 executor.execute()<br>5. 驗證 event_queue.enqueue_event 方法被呼叫，確認事件已加入佇列 | "Test query" | 事件被加入佇列 |
| **TestAgentExecutorIntegration** | **TC-INT-006** | 測試 WebsiteBuilderSimpleAgentExecutor 執行 | 無 | 1. 建立 WebsiteBuilderSimpleAgentExecutor 實例<br>2. Mock RequestContext 和 EventQueue<br>3. Mock agent.invoke 方法回傳模擬的回應<br>4. 呼叫 executor.execute()<br>5. 驗證 event_queue.enqueue_event 方法被呼叫，確認事件已加入佇列 | "Build a website" | 事件被加入佇列 |
| **TestUtilitiesIntegration** | **TC-INT-007** | 測試 AgentConnector 與 Discovery 整合 | 無 | 1. 建立 AgentDiscovery 實例<br>2. Mock list_agent_cards 方法回傳模擬的 agent card<br>3. 呼叫 discovery.list_agent_cards()<br>4. 使用取得的 agent card 建立 AgentConnector<br>5. 驗證 connector.agent_card 不為 None | None | AgentConnector 建立成功 |
| **TestUtilitiesIntegration** | **TC-INT-008** | 測試 MCPConnector 與 Discovery 整合 | 無 | 1. 建立 MCPConnector 實例<br>2. 驗證 discovery 屬性被正確設定<br>3. 呼叫 discovery.list_servers()<br>4. 驗證回傳結果為字典型別 | None | Discovery 設定正確且 list_servers 回傳字典 |
| **TestEndToEndWorkflow** | **TC-INT-009** | 測試完整工作流程（使用 mocks） | 無 | 1. 初始化 HostAgent<br>2. Mock MCPConnector 和 AgentDiscovery 以模擬外部相依<br>3. 呼叫 agent.create() 建立 agent<br>4. Mock runner.run_async 回傳模擬的對話事件<br>5. 呼叫 agent.invoke() 執行完整工作流程<br>6. 驗證執行結果包含 is_task_complete=True | "Test workflow" | 工作流程完成 (is_task_complete=True) |

## 結構測試 (`tests/test_structure.py`)

此部分涵蓋對專案結構與檔案組織的測試，確保所有必要的檔案與目錄都存在。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TestProjectStructure** | **TC-STR-001** | 測試主要目錄是否存在 | 無 | 1. 定義必要的目錄清單 (agents, utilities, mcp, app, tests)<br>2. 遍歷每個目錄名稱<br>3. 驗證該目錄是否存在且確實為目錄 | required_dirs | 所有主要目錄存在 |
| **TestProjectStructure** | **TC-STR-002** | 測試 agents 目錄結構 | 無 | 1. 驗證 agents 目錄是否存在<br>2. 定義必要的 agent 子目錄清單<br>3. 遍歷每個子目錄<br>4. 驗證子目錄是否存在且確實為目錄 | agents_dir | 所有 agent 子目錄存在 |
| **TestProjectStructure** | **TC-STR-003** | 測試 host_agent 必要檔案是否存在 | 無 | 1. 定義 host_agent 目錄路徑<br>2. 定義必要的檔案清單 (__init__.py, agent.py 等)<br>3. 遍歷每個檔案名稱<br>4. 驗證檔案是否存在且確實為檔案 | required_files | 所有 host_agent 檔案存在 |
| **TestProjectStructure** | **TC-STR-004** | 測試 website_builder_simple 必要檔案是否存在 | 無 | 1. 定義 website_builder_simple 目錄路徑<br>2. 定義必要的檔案清單 (__init__.py, agent.py 等)<br>3. 遍歷每個檔案名稱<br>4. 驗證檔案是否存在且確實為檔案 | required_files | 所有 website_builder_simple 檔案存在 |
| **TestProjectStructure** | **TC-STR-005** | 測試 utilities 目錄結構 | 無 | 1. 驗證 utilities 目錄是否存在<br>2. 定義必要的子目錄清單 (a2a, mcp, common)<br>3. 遍歷每個子目錄<br>4. 驗證子目錄是否存在且確實為目錄 | utilities_dir | 所有 utilities 子目錄存在 |
| **TestProjectStructure** | **TC-STR-006** | 測試 A2A utilities 檔案是否存在 | 無 | 1. 定義 a2a utilities 目錄路徑<br>2. 定義必要的檔案清單 (agent_connect.py 等)<br>3. 遍歷每個檔案<br>4. 驗證檔案是否存在 | required_files | 所有 A2A utilities 檔案存在 |
| **TestProjectStructure** | **TC-STR-007** | 測試 MCP utilities 檔案是否存在 | 無 | 1. 定義 mcp utilities 目錄路徑<br>2. 定義必要的檔案清單 (mcp_connect.py 等)<br>3. 遍歷每個檔案<br>4. 驗證檔案是否存在 | required_files | 所有 MCP utilities 檔案存在 |
| **TestProjectStructure** | **TC-STR-008** | 測試 common utilities 檔案是否存在 | 無 | 1. 定義 common utilities 目錄路徑<br>2. 驗證 file_loader.py 檔案是否存在 | None | file_loader.py 存在 |
| **TestProjectStructure** | **TC-STR-009** | 測試 tests 目錄結構 | 無 | 1. 驗證 tests 目錄是否存在且為目錄<br>2. 定義必要的測試檔案清單<br>3. 遍歷每個檔案<br>4. 驗證檔案是否存在 | required_test_files | 所有測試檔案存在 |
| **TestProjectStructure** | **TC-STR-010** | 測試專案配置檔案是否存在 | 無 | 1. 定義必要的專案配置檔案清單 (pyproject.toml, Makefile 等)<br>2. 遍歷每個檔案<br>3. 驗證檔案是否存在且確實為檔案 | required_config_files | 所有配置檔案存在 |
| **TestProjectStructure** | **TC-STR-011** | 測試 mcp 目錄結構 | 無 | 1. 驗證 mcp 目錄是否存在<br>2. 檢查 servers 子目錄是否存在（若存在則確認其為目錄）<br>3. 檢查 workspace 子目錄是否存在（若存在則確認其為目錄） | mcp_dir | mcp 目錄結構正確 |
| **TestProjectStructure** | **TC-STR-012** | 測試 app 目錄結構 | 無 | 1. 驗證 app 目錄是否存在<br>2. 確認 app 目錄確實為目錄 | app_dir | app 目錄存在 |
| **TestProjectStructure** | **TC-STR-013** | 測試 main.py 是否存在 | 無 | 1. 驗證 main.py 檔案是否存在<br>2. 確認 main.py 確實為檔案 | None | main.py 存在 |

## Utilities 測試 (`tests/test_utilities.py`)

此部分涵蓋對 Utilities 模組功能的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TestFileLoader** | **TC-UTIL-001** | 測試成功載入檔案 | 無 | 1. 匯入 load_instructions_file 函式<br>2. 呼叫函式載入存在的檔案<br>3. 驗證回傳結果不為 None<br>4. 驗證回傳結果為字串且長度大於 0 | "agents/host_agent/description.txt" | 成功載入檔案內容 |
| **TestFileLoader** | **TC-UTIL-002** | 測試檔案不存在時的行為 | 無 | 1. 匯入 load_instructions_file 函式<br>2. 呼叫函式載入不存在的檔案<br>3. 驗證回傳結果為預設值 | "nonexistent_file.txt" | 回傳預設值 |
| **TestFileLoader** | **TC-UTIL-003** | 測試使用預設值 | 無 | 1. 匯入 load_instructions_file 函式<br>2. 呼叫函式載入不存在的檔案並指定預設值<br>3. 驗證回傳結果為指定的預設值 | default="fallback" | 回傳指定的預設值 |
| **TestAgentConnector** | **TC-UTIL-004** | 測試 AgentConnector 初始化 | 無 | 1. 匯入 AgentConnector<br>2. 使用 mock_agent_card 初始化 AgentConnector<br>3. 驗證實例建立成功且 agent_card 屬性正確 | mock_agent_card | 實例建立成功 |
| **TestAgentConnector** | **TC-UTIL-005** | 測試使用有效的 AgentCard 初始化 | 無 | 1. 建立 AgentConnector 實例<br>2. 驗證 agent_card 的 name 和 url 屬性是否正確 | mock_agent_card | 屬性正確 |
| **TestAgentConnector** | **TC-UTIL-006** | 測試 send_task（使用 mock） | 無 | 1. 建立 AgentConnector 實例<br>2. Mock httpx.AsyncClient 和 A2AClient<br>3. 設定 mock 回應<br>4. 呼叫 connector.send_task()<br>5. 驗證回傳結果不為 None | "Test message" | 回傳結果不為 None |
| **TestAgentDiscovery** | **TC-UTIL-007** | 測試 AgentDiscovery 初始化 | 無 | 1. 匯入 AgentDiscovery<br>2. 建立實例<br>3. 驗證實例建立成功 | None | 實例建立成功 |
| **TestAgentDiscovery** | **TC-UTIL-008** | 測試使用自訂 registry 檔案 | 無 | 1. 建立臨時 registry 檔案<br>2. 寫入測試資料<br>3. 使用自訂 registry 檔案路徑初始化 AgentDiscovery<br>4. 驗證實例建立成功 | test_registry.json | 實例建立成功 |
| **TestAgentDiscovery** | **TC-UTIL-009** | 測試載入 registry 成功 | 無 | 1. 建立 AgentDiscovery 實例<br>2. 呼叫 _load_registry() 方法<br>3. 驗證回傳結果為列表 | None | 回傳列表 |
| **TestAgentDiscovery** | **TC-UTIL-010** | 測試 list_agent_cards（使用 mock） | 無 | 1. 建立 AgentDiscovery 實例<br>2. Mock _fetch_agent_card 方法回傳模擬的 agent card<br>3. (此測試目前尚未完成完整的 assertion，需根據實際情況補充) | None | (需根據實作補充) |
| **TestMCPDiscovery** | **TC-UTIL-011** | 測試 MCPDiscovery 初始化 | 無 | 1. 匯入 MCPDiscovery<br>2. 建立實例<br>3. 驗證實例建立成功 | None | 實例建立成功 |
| **TestMCPDiscovery** | **TC-UTIL-012** | 測試使用自訂配置檔案 | 無 | 1. 建立臨時配置檔案<br>2. 寫入測試配置資料<br>3. 使用自訂配置檔案路徑初始化 MCPDiscovery<br>4. 驗證實例建立成功 | test_mcp_config.json | 實例建立成功 |
| **TestMCPDiscovery** | **TC-UTIL-013** | 測試載入配置成功 | 無 | 1. 建立 MCPDiscovery 實例<br>2. 呼叫 _load_config() 方法<br>3. 驗證回傳結果為字典 | None | 回傳字典 |
| **TestMCPDiscovery** | **TC-UTIL-014** | 測試 list_servers 回傳字典 | 無 | 1. 建立 MCPDiscovery 實例<br>2. 呼叫 list_servers() 方法<br>3. 驗證回傳結果為字典 | None | 回傳字典 |
| **TestMCPConnector** | **TC-UTIL-015** | 測試 MCPConnector 初始化 | 無 | 1. 匯入 MCPConnector<br>2. 建立實例<br>3. 驗證實例建立成功<br>4. 驗證 tools 屬性為列表 | None | 實例建立且 tools 為列表 |
| **TestMCPConnector** | **TC-UTIL-016** | 測試使用自訂配置初始化 | 無 | 1. 建立臨時配置檔案<br>2. 寫入測試配置資料<br>3. 使用自訂配置檔案路徑初始化 MCPConnector<br>4. 驗證實例建立成功 | test_mcp_config.json | 實例建立成功 |
| **TestMCPConnector** | **TC-UTIL-017** | 測試 get_tools 回傳列表 | 無 | 1. 建立 MCPConnector 實例<br>2. 直接存取 tools 屬性<br>3. 驗證 tools 為列表型別 | None | tools 為列表 |
| **TestMCPConnector** | **TC-UTIL-018** | 測試 _load_all_tools（使用 mock） | 無 | 1. 建立 MCPConnector 實例<br>2. Mock discovery.list_servers 方法回傳空字典<br>3. 呼叫 _load_all_tools()<br>4. 驗證 tools 屬性仍為列表型別 | None | tools 為列表 |

## WebsiteBuilderSimple 測試 (`tests/test_website_builder_agent.py`)

此部分涵蓋對 WebsiteBuilderSimple Agent 的核心功能與配置的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TestWebsiteBuilderConfiguration** | **TC-WEB-001** | 測試 Agent 初始化 | 無 | 1. 匯入 WebsiteBuilderSimple 類別<br>2. 建立實例<br>3. 驗證實例建立成功且不為 None | None | 實例建立成功 |
| **TestWebsiteBuilderConfiguration** | **TC-WEB-002** | 測試系統指令是否載入 | 無 | 1. 建立 WebsiteBuilderSimple 實例<br>2. 檢查 system_instruction 屬性是否存在<br>3. 驗證 system_instruction 是否為字串且不為空 | None | system_instruction 存在且內容正確 |
| **TestWebsiteBuilderConfiguration** | **TC-WEB-003** | 測試描述是否載入 | 無 | 1. 建立 WebsiteBuilderSimple 實例<br>2. 檢查 description 屬性是否存在<br>3. 驗證 description 是否為字串且不為空 | None | description 存在且內容正確 |
| **TestWebsiteBuilderConfiguration** | **TC-WEB-004** | 測試 AgentResponse 模型是否存在 | 無 | 1. 嘗試匯入 AgentResponse 類別<br>2. 驗證類別是否存在 | None | AgentResponse 類別存在 |
| **TestWebsiteBuilderConfiguration** | **TC-WEB-005** | 測試 AgentResponse 模型驗證 | 無 | 1. 建立包含所有必要欄位的 AgentResponse 實例<br>2. 驗證各欄位值是否正確 (is_task_complete, updates, content) | AgentResponse data | 欄位值正確 |
| **TestWebsiteBuilderConfiguration** | **TC-WEB-006** | 測試初始狀態 | 無 | 1. 建立 WebsiteBuilderSimple 實例<br>2. 驗證 _agent 屬性已初始化且為 LlmAgent 實例<br>3. 驗證 _runner 屬性已初始化且為 Runner 實例 | None | 屬性初始化正確 |
| **TestWebsiteBuilderCreation** | **TC-WEB-007** | 測試 _build_agent 建立 LLM Agent | 無 | 1. 建立 WebsiteBuilderSimple 實例<br>2. 呼叫 _build_agent() 方法<br>3. 驗證回傳物件為 LlmAgent 實例 | None | 回傳 LlmAgent 實例 |
| **TestWebsiteBuilderCreation** | **TC-WEB-008** | 測試 Agent 模型配置 | 無 | 1. 建立 WebsiteBuilderSimple 實例<br>2. 呼叫 _build_agent()<br>3. 驗證 agent 名稱是否為 "website_builder_simple"<br>4. 驗證 agent 使用的模型是否在允許的清單中 | None | 模型配置正確 |
| **TestWebsiteBuilderCreation** | **TC-WEB-009** | 測試 Agent 是否有系統指令 | 無 | 1. 建立 WebsiteBuilderSimple 實例<br>2. 呼叫 _build_agent()<br>3. 驗證 agent.instruction 不為 None 且長度大於 0 | None | instruction 存在且有內容 |
| **TestWebsiteBuilderFunctionality** | **TC-WEB-010** | 測試 invoke 回傳 generator | 無 | 1. 建立 WebsiteBuilderSimple 實例<br>2. Mock runner.run_async 方法回傳模擬的對話事件<br>3. 呼叫 agent.invoke()<br>4. 驗證 invoke 過程回傳了結果 | sample_queries[0] | 回傳至少一個結果 |
| **TestWebsiteBuilderFunctionality** | **TC-WEB-011** | 測試查詢長度驗證 | 無 | 1. 匯入查詢長度常數<br>2. 驗證 MAX_QUERY_LENGTH > 0<br>3. 驗證 MIN_QUERY_LENGTH > 0<br>4. 驗證 MAX_QUERY_LENGTH > MIN_QUERY_LENGTH | None | 常數值驗證正確 |
| **TestWebsiteBuilderExecutor** | **TC-WEB-012** | 測試 Executor 初始化 | 無 | 1. 匯入 WebsiteBuilderSimpleAgentExecutor<br>2. 建立實例<br>3. 驗證實例建立成功<br>4. 驗證 agent 屬性存在<br>5. 驗證 _cancel_requested 屬性存在 | None | 實例與屬性存在 |
| **TestWebsiteBuilderExecutor** | **TC-WEB-013** | 測試 Executor 取消旗標初始狀態 | 無 | 1. 建立 WebsiteBuilderSimpleAgentExecutor 實例<br>2. 驗證 _cancel_requested 初始值為 False | None | _cancel_requested 為 False |
| **TestWebsiteBuilderExecutor** | **TC-WEB-014** | 測試 Executor execute 方法（使用 mock） | 無 | 1. 建立 Executor 實例<br>2. Mock RequestContext 和 EventQueue<br>3. Mock agent.invoke 方法回傳模擬的回應<br>4. 呼叫 executor.execute()<br>5. 驗證 agent.invoke 方法被呼叫一次 | "Build a test website" | agent.invoke 被呼叫 |
| **TestWebsiteBuilderExecutor** | **TC-WEB-015** | 測試 Executor 超時常數 | 無 | 1. 匯入 TASK_EXECUTION_TIMEOUT<br>2. 驗證超時值大於 0 且為整數 | None | 常數值正確 |
| **TestAgentResponseModel** | **TC-WEB-016** | 測試包含所有欄位的 response | 無 | 1. 使用所有欄位建立 AgentResponse 實例<br>2. 驗證各欄位值是否正確 | Full data | 欄位值正確 |
| **TestAgentResponseModel** | **TC-WEB-017** | 測試預設值 | 無 | 1. 只使用必要欄位建立 AgentResponse 實例<br>2. 驗證必要欄位值是否正確 | Partial data | 必要欄位正確且有預設值 |

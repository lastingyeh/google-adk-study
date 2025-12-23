# 詳細測試案例範本

## 簡介

此文件提供了一個詳細的測試案例範本，旨在為專案建立清晰、一致且全面的測試文件。使用此範本可以幫助開發者和測試人員標準化測試流程，確保所有關鍵功能都得到充分的驗證。

## 深度研究代理 (Deep Research Agent) 測試 (`tests/test_research.py`)

此部分涵蓋對深度研究代理的核心邏輯、配置及數據結構的單元測試，不包含實際 API 調用。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **模組導入** | **TC-IMPORT-001** | 驗證主模組導入 | 環境依賴已安裝 | 1. 導入 DeepResearchAgent<br>2. 導入相關工具函數 | None | 所有模組成功導入，DeepResearchAgent 不為 None |
| **模組導入** | **TC-IMPORT-002** | 驗證串流工具導入 | 環境依賴已安裝 | 1. 導入 stream_research<br>2. 導入 ResearchProgress | None | stream_research 可調用，ResearchProgress 為 dataclass |
| **配置驗證** | **TC-CONFIG-001** | API Key 驗證 (缺少 Key) | 清除環境變數 | 1. 嘗試初始化 DeepResearchAgent | OS 環境變數為空 | 拋出 ValueError，訊息包含 "GOOGLE_API_KEY" |
| **配置驗證** | **TC-CONFIG-002** | 顯式 API Key 處理 | None | 1. 使用 api_key 參數初始化 | api_key="test-key" | agent.api_key 為 "test-key" |
| **配置驗證** | **TC-CONFIG-003** | 環境變數 API Key 處理 | 設定環境變數 | 1. 初始化 DeepResearchAgent | GOOGLE_API_KEY="env-key" | agent.api_key 為 "env-key" |
| **配置驗證** | **TC-CONFIG-004** | 客戶端延遲初始化 | None | 1. 初始化 agent<br>2. 檢查 _client 屬性 | None | _client 初始值為 None |
| **資料結構** | **TC-DATA-001** | ResearchResult 結構驗證 | None | 1. 建立 ResearchResult 實例 | 完整欄位數據 | 各欄位值與輸入一致，error 為 None |
| **資料結構** | **TC-DATA-002** | ResearchResult 錯誤處理 | None | 1. 建立帶有錯誤的 ResearchResult | error="Something went wrong" | status 為 FAILED，error 欄位正確 |
| **資料結構** | **TC-DATA-003** | ResearchProgress 結構驗證 | None | 1. 建立 ResearchProgress 實例 | type=THOUGHT, content... | 各欄位值與輸入一致 |
| **資料結構** | **TC-DATA-004** | ProgressType 值驗證 | None | 1. 檢查所有 ProgressType 枚舉值 | None | start, thought, content, complete, error 值正確 |
| **核心方法** | **TC-METHOD-001** | Start Research (Mocked) | Mock Client | 1. 調用 start_research | Query="Test query" | 返回包含 id 和 status 的字典，Client 收到正確參數 |
| **核心方法** | **TC-METHOD-002** | Poll Research (In Progress) | Mock Client | 1. 調用 poll_research | id="research-id-123" | 返回 status="in_progress"，不包含 report |
| **核心方法** | **TC-METHOD-003** | Poll Research (Completed) | Mock Client | 1. 調用 poll_research | id="research-id-123" | 返回 status="completed"，包含 report 內容 |
| **工具邏輯** | **TC-UTIL-001** | URL 提取驗證 | None | 1. 調用 _extract_citations | 包含多個 URL 的文本 | 成功提取所有有效 URL |
| **工具邏輯** | **TC-UTIL-002** | 無 URL 文本處理 | None | 1. 調用 _extract_citations | 無 URL 文本 | 返回空列表 |
| **工具邏輯** | **TC-UTIL-003** | URL 去重驗證 | None | 1. 調用 _extract_citations | 包含重複 URL 的文本 | 返回去重後的 URL 列表 |
| **串流邏輯** | **TC-STREAM-001** | Reconnector 初始化 | 環境變數 Key | 1. 初始化 ResearchStreamReconnector | None | 預設重試次數為 3，狀態屬性為空 |
| **串流邏輯** | **TC-STREAM-002** | Reconnector 顯式 Key | None | 1. 帶 Key 初始化 ResearchStreamReconnector | api_key="explicit-key" | 正確使用提供的 API Key |
| **常數驗證** | **TC-CONST-001** | Agent ID 驗證 | None | 1. 檢查 DEEP_RESEARCH_AGENT_ID | None | 值為 "deep-research-pro-preview-12-2025" |
| **常數驗證** | **TC-CONST-002** | 輪詢間隔驗證 | None | 1. 檢查 DEFAULT_POLL_INTERVAL | None | 值為 10 |
| **常數驗證** | **TC-CONST-003** | 最大研究時間驗證 | None | 1. 檢查 MAX_RESEARCH_TIME | None | 值為 3600 |

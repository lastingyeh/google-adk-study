# 測試案例說明

本文件列出 `workspace/python/agents/pack-rag/tests` 目錄下的測試案例。

## 整合測試 - Agent (`integration/test_agent.py`)

此部分涵蓋 Agent 串流回應的整合測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Agent 串流** | **TC-INT-AGENT-001** | 驗證 Agent 是否回傳有效的串流回應 | 1. `InMemorySessionService` 可用<br>2. `root_agent` 已定義 | 1. 建立會話<br>2. 初始化 Runner<br>3. 發送訊息<br>4. 收集回應事件 | Message: "Why is the sky blue?"<br>Config: StreamingMode.SSE | 1. 收到至少一個事件<br>2. 至少有一個事件包含文字內容 |

## 整合測試 - 伺服器 E2E (`integration/test_server_e2e.py`)

此部分涵蓋 FastAPI 伺服器的端對端測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **API 串流** | **TC-INT-SRV-001** | 測試聊天串流功能 | 1. 伺服器已啟動<br>2. 用戶 ID 和 Session ID 可用 | 1. 建立 Session<br>2. 發送訊息到 `/run_sse`<br>3. 接收 SSE 事件 | User ID: "test_user_123"<br>Message: "Hi!"<br>Streaming: True | 1. 回應 200 OK<br>2. 收到 SSE 事件<br>3. 事件包含文字內容 |
| **API 錯誤處理** | **TC-INT-SRV-002** | 測試聊天串流的錯誤處理 | 伺服器已啟動 | 1. 發送無效的輸入資料到 `/run_sse` | Input: Invalid type structure | 回應 422 Unprocessable Entity |
| **API 回饋** | **TC-INT-SRV-003** | 測試回饋收集端點 | 伺服器已啟動 | 1. 發送回饋資料到 `/feedback` | Score: 4<br>Text: "Great response!" | 回應 200 OK |

## 負載測試 (`load_test/load_test.py`)

此部分涵蓋使用 Locust 進行的 API 負載測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **聊天 API 負載** | **TC-LOAD-001** | 模擬多用戶並發聊天請求 | 1. API 服務已啟動<br>2. Locust 環境就緒 | 1. 建立 Session<br>2. 發送聊天請求 `/run_sse`<br>3. 記錄回應時間和成功率 | Users: 并發用戶<br>Wait Time: 1-3s | 1. 請求成功率符合預期<br>2. 回應時間在可接受範圍 |

## 單元測試 - Agent 配置 (`unit/test_agent.py`)

此部分涵蓋 Agent 的基本配置與屬性驗證。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Agent 配置** | **TC-UNIT-AGENT-001** | 驗證 Agent 基本屬性 | 模組可導入 | 1. 檢查名稱<br>2. 檢查模型<br>3. 檢查指令 | N/A | 1. Name: "ask_rag_agent"<br>2. Model in expected list<br>3. Instruction has content |
| **工具配置** | **TC-UNIT-AGENT-002** | 驗證 Agent 工具配置 | 模組可導入 | 1. 檢查工具列表<br>2. 檢查檢索工具 | N/A | 1. Tools list not empty<br>2. Contains "retrieve_rag_documentation" |
| **檢索工具** | **TC-UNIT-AGENT-003** | 驗證檢索工具詳細配置 | 模組可導入 | 1. 檢查 RAG 資源<br>2. 檢查相似度參數 | N/A | 1. Resources configured<br>2. Top K > 0<br>3. Threshold between 0-1 |

## 單元測試 - 環境配置 (`unit/test_config.py`)

此部分涵蓋環境變數與初始化邏輯的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **環境變數** | **TC-UNIT-CONF-001** | 驗證環境變數設定 | 模組可導入 | 1. 檢查 Google 認證<br>2. 檢查 Cloud Location<br>3. 檢查 VertexAI 標記 | N/A | 1. Auth Initialized<br>2. Location: "global"<br>3. VertexAI: Enabled |
| **模組初始化** | **TC-UNIT-CONF-002** | 驗證模組初始化順序 | 環境變數未設 | 1. 匯入 RAG 模組<br>2. 檢查變數設定順序 | N/A | 1. Agent 導入成功<br>2. 環境變數在 Agent 前設定 |
| **Corpus 配置** | **TC-UNIT-CONF-003** | 驗證 RAG Corpus 配置 | N/A | 1. 檢查 RAG_CORPUS 格式<br>2. 檢查工具資源配置 | RAG_CORPUS | 1. 格式正確 (if set)<br>2. 工具使用該 Corpus |

## 單元測試 - 範本 (`unit/test_dummy.py`)

此部分為測試範本。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **範本測試** | **TC-UNIT-DUMMY-001** | 驗證測試環境可用 | N/A | 執行 assert 1 == 1 | N/A | Pass |

## 單元測試 - FastAPI 應用 (`unit/test_fastapi.py`)

此部分涵蓋 FastAPI 應用程式的配置與路由測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **App 實例** | **TC-UNIT-API-001** | 驗證 FastAPI 應用實例化 | 模組可導入 | 1. 檢查 app 是否存在<br>2. 檢查類型與屬性 | N/A | 1. App exists<br>2. Is FastAPI instance<br>3. Title/Desc correct |
| **回饋端點** | **TC-UNIT-API-002** | 驗證回饋端點定義 | 模組可導入 | 1. 檢查函式與簽名<br>2. 檢查路由註冊<br>3. 檢查 HTTP 方法 | N/A | 1. Callable exists<br>2. Route /feedback exists<br>3. Method is POST |
| **服務配置** | **TC-UNIT-API-003** | 驗證服務配置 (Logging, Session, Artifact) | 環境變數可選 | 1. 檢查 Logging 初始化<br>2. 檢查 Session URI<br>3. 檢查 Artifact URI | Env Vars | 1. Logging ready<br>2. URIs generated based on Env |

## 單元測試 - 匯入驗證 (`unit/test_imports.py`)

此部分驗證專案依賴與模組結構的正確性。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **內部模組** | **TC-UNIT-IMP-001** | 驗證內部模組匯入 | N/A | 嘗試匯入 rag, agent, prompts 等 | N/A | 匯入成功無錯誤 |
| **外部依賴** | **TC-UNIT-IMP-002** | 驗證外部套件匯入 | 安裝依賴 | 嘗試匯入 google.adk, vertexai, arize | N/A | 匯入成功無錯誤 |

## 單元測試 - Pydantic 模型 (`unit/test_models.py`)

此部分驗證資料模型的定義與驗證邏輯。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Request 模型** | **TC-UNIT-MOD-001** | 驗證 Request 模型 | 模組可導入 | 1. 建立 Request<br>2. 驗證預設值 (User/Session ID)<br>3. 驗證必要欄位 | Message Content | 1. Created successfully<br>2. IDs generated<br>3. Schema matches |
| **Feedback 模型** | **TC-UNIT-MOD-002** | 驗證 Feedback 模型 | 模組可導入 | 1. 建立 Feedback<br>2. 驗證分數類型<br>3. 驗證預設值 | Score: 5 | 1. Created successfully<br>2. Score accepted (int/float)<br>3. Metadata auto-filled |

## 單元測試 - Prompts (`unit/test_prompts.py`)

此部分驗證 Agent 使用的提示詞 (Prompt) 生成邏輯。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **指令生成** | **TC-UNIT-PRM-001** | 驗證根代理人指令生成 | 模組可導入 | 1. 呼叫 `return_instructions_root` | N/A | 1. 回傳字串<br>2. 內容不為空<br>3. 格式正確 |
| **指令內容** | **TC-UNIT-PRM-002** | 驗證指令關鍵內容 | 模組可導入 | 1. 檢查檢索指引<br>2. 檢查引用指引<br>3. 檢查角色定義 | N/A | 包含所有必要關鍵字與指引 |

## 單元測試 - 專案結構 (`unit/test_structure.py`)

此部分驗證專案目錄結構與檔案完整性。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **結構驗證** | **TC-UNIT-STR-001** | 驗證核心目錄與檔案 | N/A | 檢查 rag, tests, pyproject.toml 等 | N/A | 檔案與目錄存在 |
| **配置驗證** | **TC-UNIT-STR-002** | 驗證設定檔內容 | N/A | 1. 檢查 pyproject.toml 依賴<br>2. 檢查 Makefile 目標<br>3. 檢查 .env.example 格式 | N/A | 內容符合預期 |

## 單元測試 - 遙測功能 (`unit/test_telemetry.py`)

此部分驗證 OpenTelemetry 整合與遙測配置。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **遙測初始化** | **TC-UNIT-TEL-001** | 驗證 setup_telemetry 行為 | 環境變數控制 | 1. 呼叫 setup_telemetry<br>2. 驗證不同 env 變數下的行為 | Env Vars | 1. Bucket not set -> None<br>2. Bucket set -> Return Bucket |
| **安全配置** | **TC-UNIT-TEL-002** | 驗證隱私安全設定 | 嘗試啟用內容記錄 | 1. 設定 capture_content=true<br>2. 呼叫 setup_telemetry | N/A | 強制覆蓋為 NO_CONTENT |

## 單元測試 - 追蹤功能 (`unit/test_tracing.py`)

此部分驗證 Arize 追蹤整合與儀表化。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Arize 儀表化** | **TC-UNIT-TRC-001** | 驗證 Arize 儀表化函式 | 環境變數控制 | 1. 呼叫儀表化函式<br>2. 驗證憑證檢查 | Env Vars (Space ID, API Key) | 1. 缺少憑證 -> Warning/None<br>2. 憑證完整 -> Return Tracer |
| **追蹤整合** | **TC-UNIT-TRC-002** | 驗證追蹤模組依賴 | 安裝依賴 | 嘗試匯入 tracing 相關模組 | N/A | 匯入成功無錯誤 |

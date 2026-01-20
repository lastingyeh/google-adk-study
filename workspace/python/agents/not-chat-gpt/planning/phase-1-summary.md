# Phase 1 Summary

## 1.3 Session State Management

**目標達成**: 實作具備狀態管理能力的對話 Agent，能夠記住使用者資訊並維持跨會話的持久化狀態。

### 核心實作內容

#### 1. ToolContext 狀態管理架構

- **實作位置**: `backend/agents/conversation_agent.py`
- **核心概念**: 使用 `ToolContext` 作為狀態容器，透過 `tool_context.state` 管理會話數據
- **狀態分類**:
  - `user:` 前綴: 跨會話永久保存的使用者資訊 (姓名、偏好等)
  - 一般狀態: 會話級別的暫時資訊

#### 2. 狀態管理工具函式

**`remember_user_info` 工具**:

```python
def remember_user_info(key: str, value: str, tool_context: ToolContext) -> Dict[str, Any]:
    tool_context.state[f"user:{key}"] = value
    return {"status": "success", "message": f"已記住 {key} 為 {value}"}
```

- 功能: 儲存使用者個人資訊
- 設計: 使用 `user:` 前綴確保跨會話持久化

**`get_user_info` 工具**:

```python
def get_user_info(tool_context: ToolContext) -> Dict[str, Any]:
    user_data = {}
    for key, value in tool_context.state.to_dict().items():
        if key.startswith("user:"):
            clean_key = key.replace("user:", "")
            user_data[clean_key] = value
    return {"user_context": user_data, "total_items": len(user_data)}
```

- 功能: 載入完整使用者上下文
- 設計: 過濾並整理所有 `user:` 開頭的狀態資料

#### 3. Agent 整合配置

- **工具註冊**: 將狀態管理工具註冊到 `root_agent`
- **指令整合**: 系統指令中明確定義記憶與回憶的使用時機
- **自動化流程**: Agent 能自動偵測個人資訊並呼叫對應工具

#### 4. ADK API Server 整合

- **會話建立**: 使用內建的 `POST /apps/{appName}/users/{userId}/sessions/{sessionId}` 端點
- **狀態持久化**: 透過 `sessionId` 自動管理狀態生命週期
- **跨請求記憶**: 使用者資訊在多輪對話中自動保持

#### 5. 測試驗證

**多輪對話測試流程**:

1. 建立會話: `POST /apps/conversation_agent/users/u_123/sessions/s_123`
2. 第一輪對話: 使用者自我介紹 ("Hi, 我是 Chris...")
3. 第二輪對話: 測試記憶功能 ("我是誰?")
4. 驗證: Agent 能正確回憶並使用先前儲存的使用者資訊

### 技術特色

- **零配置記憶**: 無需額外資料庫，使用 ADK 內建狀態管理
- **自動持久化**: `user:` 前綴資料自動跨會話保存
- **工具化設計**: 記憶功能透過工具實現，可獨立測試與擴展
- **對話自然性**: Agent 能在適當時機自動記憶與回憶，保持對話流暢度

### 勘誤與最佳實踐

- **ADK 會話管理**: `adk api_server` 啟動後會自動建立並管理 `session.db`，處理會話狀態的持久化，開發者無需手動設定。
- **長期記憶儲存策略**: 雖然 ADK 提供了跨會話的狀態保存能力，但不建議使用 `after_agent_response` 這類 callback 自動儲存所有資訊。這樣會導致記憶量劇烈上升。
- **最佳實踐**: 較好的做法是將記憶儲存的權力交給 LLM。透過工具 (Tool)，讓模型根據對話上下文自行判斷是否有儲存長期記憶的必要，或由使用者明確發出指令要求儲存。

### 完成狀態

- ✅ ToolContext 整合
- ✅ 狀態管理工具實作
- ✅ ADK API Server 會話管理
- ✅ 多輪對話測試驗證
- ✅ 跨會話記憶功能

## 1.4 思考模式切換

### Agent Session 隔離與限制

根據 ADK 的預設行為，每個 Agent 的會話管理是獨立且隔離的。

- **獨立 Session 資料庫**: 每個 Agent 會在其專屬的資料夾中建立一個 `session.db` 檔案來管理會話。
- **Session 表格與 `appName`**: 在 `session.db` 的 `session` 表格中，會有一欄 `appName` 用來記錄該會話屬於哪個 Agent。
- **無法共享 Session**: 由於這種設計，ADK 的預設機制不支援讓多個不同的 Agent 共享同一個 Session 狀態。若要實現跨 Agent 的狀態共享，需要額外設計外部的共享狀態儲存機制。

## 1.5 Callbacks 與 Guardrails 實作挑戰

**目標達成**: 實作 Callbacks 機制與 Guardrails 功能，但在過程中發現官方教學文件與實際 API 存在版本落差問題。

### API 變更與相容性問題

#### 1. Tutorial 09 範例代碼過時問題

**已識別的 API 變更**:

- **`after_agent_callback` 參數變更**:
  - ❌ **已移除**: `content: types.Content` 參數
  - ✅ **現行版本**: 需參考最新 API 文件確認正確參數結構

- **回傳類型更新**:
  - ❌ **舊版本**: `GenerateContentResponse`
  - ✅ **新版本**: `LlmResponse`

#### 2. 解決方案與最佳實踐

**推薦開發流程**:

1. **官方文件優先**: 始終以最新的官方 API 文件為準，而非教學範例
2. **Debug 驅動開發**: 使用 debug 模式快速識別 API 變更與相容性問題
3. **漸進式測試**: 每個 callback 功能獨立測試，確保 API 呼叫正確性
4. **版本追蹤**: 記錄當前使用的 ADK 版本，便於後續問題追蹤

#### 3. Callbacks 功能用途與應用

**Callback 機制的核心價值**:

- **請求前處理**: `before_agent_callback` - 輸入驗證、預處理、權限檢查
- **回應後處理**: `after_agent_callback` - 輸出過濾、日誌記錄、效能監控
- **錯誤處理**: 異常狀況的統一處理與恢復機制
- **監控與分析**: 對話品質追蹤、使用者行為分析

#### 4. Guardrails 整合策略

**Guardrails 與 Callbacks 的協作模式**:

- **輸入過濾**: 在 `before_agent_callback` 中整合輸入內容檢查
- **輸出審核**: 在 `after_agent_callback` 中實施內容安全性檢查
- **即時阻斷**: 偵測到違規內容時的即時處理機制

### 經驗總結

#### 快速函式庫適應策略

1. **文件版本確認**: 確認教學文件的發佈日期與目前使用的 ADK 版本
2. **API 差異測試**: 建立小型測試程式快速驗證 API 變更
3. **社群資源**: 善用官方 Discord 或 GitHub Issues 獲取最新資訊
4. **向下相容性**: 了解哪些 API 變更會導致破壞性更新

#### 開發建議

- **漸進式升級**: 不要一次性實作所有 callback 功能，逐步驗證每個部分
- **錯誤處理優先**: 優先實作錯誤處理的 callback，確保系統穩定性
- **測試覆蓋**: 為每個 callback 建立對應的單元測試
- **版本鎖定**: 在開發階段可以暫時鎖定 ADK 版本，避免開發中途的 API 變更

## 2.1 串流回應功能驗證

**目標達成**: 驗證 ADK 內建串流支援，確認無需額外實作即可使用完整的串流功能。

### ADK 內建串流支援

**三種內建端點**:

- **`/run`**: 同步回應
- **`/run_sse`**: SSE 串流
- **`/run_live`**: WebSocket 雙向串流

**重要發現**: ADK 框架完全內建串流功能，開發者無需實作任何 API 或中介層。

### 測試驗證結果

**功能驗證**:

- ✅ SSE 端點正常運作 (`curl -N /run_sse`)
- ✅ Web 界面原生支援串流顯示
- ✅ 長回應打字機效果流暢
- ✅ 錯誤處理與重連機制完善

**與原始規劃差異**:

- ❌ 原計畫: 需實作串流 API、修改 Agent 支援 generator
- ✅ 實際情況: ADK 完全內建，零配置即可使用

### CLI 限制

`adk run` 因終端機限制無法顯示視覺串流效果，主要測試透過 `adk web` 進行。

### 關鍵學習

ADK 提供的內建功能比預期更完整，建議優先驗證框架能力再規劃實作。

## 2.2 對話持久化升級 (Redis Session 快取層)

**目標達成**: 成功將會話管理從 ADK 內建的 SQLite 升級至 Redis，提升了系統的效能、可擴展性與狀態管理的靈活性。

### 核心實作內容

#### 1. Redis 環境與服務

- **環境**: 透過 `docker-compose.yml` 建立獨立、可複用的 Redis 服務容器。
- **服務層**: 在 `service/redis_session_service.py` 中實作了 `BaseSessionService` 介面，封裝了所有與 Redis 的互動邏輯，包含：
  - 連接管理與錯誤處理。
  - 會話的 CRUD (Create, Read, Update, Delete) 操作。
  - 使用 TTL (Time-To-Live) 實現會話的自動過期。

#### 2. ADK 服務註冊與工廠模式

- **挑戰**: ADK 預設只認識內建的 `session.db`。要讓它支援 Redis，必須在 ADK 應用啟動前就「告訴」它 Redis Session 服務的存在。
- **解決方案**:
  - 在 `backend/main.py` 中建立一個工廠函式 (Factory Function)。
  - 此函式負責解析傳入的 `session_service_uri` (如 `redis://...`)，並實例化對應的 `RedisSessionService`。
  - 使用 `session_services.register()` 將這個工廠函式註冊到 ADK 的服務註冊表中。

#### 3. 啟動流程的關鍵變更

- **重要心得**: 為了讓自定義服務的註冊生效，**不能再直接使用 `adk web backend` 或 `adk run backend` 指令**。
- **正確的啟動方式**:
  1. 必須以 `backend/main.py` 作為應用程式的進入點。
  2. `main.py` 首先執行服務註冊邏輯。
  3. 然後，`main.py` 再將命令列參數（如 `web`, `backend`, `--session_service_uri=...`）傳遞給 ADK 的 CLI 處理函式。
- **命令範例**:

  ```bash
  # 透過 main.py 啟動，確保 Redis 服務被註冊
  uv run backend/main.py web backend --session_service_uri=redis://localhost:6379
  ```

  這確保了當 ADK 處理 `--session_service_uri` 參數時，它已經能在註冊表中找到對應的 `redis://` 處理工廠。

### 技術特色與優勢

- **效能提升**: Redis 的記憶體內存取速度遠高於 SQLite 的磁碟 I/O。
- **可擴展性**: 將 Session 狀態外部化，為未來多節點部署打下基礎。
- **集中管理**: 所有 Session 數據集中儲存在 Redis，方便監控與管理。
- **靈活性**: 透過工廠模式和服務註冊，ADK 展現了良好的擴展性，允許開發者無縫接入自定義的後端服務。

### 完成狀態

- ✅ Redis 服務容器化
- ✅ `RedisSessionService` 實作與測試
- ✅ 服務註冊與工廠模式整合
- ✅ 啟動流程改造與驗證
- ✅ Makefile 指令更新 (`make dev-main`)

---

## 2.5.1 Gemini File Search 整合 (Agentic RAG)

**目標達成**: 成功整合 Gemini File Search API，為 Agent 賦予了從指定文檔中檢索資訊並回答問題的能力 (Agentic RAG)，實現了知識庫問答功能。

### 核心實作內容

#### 1. DocumentService 服務層封裝

- **實作位置**: `backend/services/document_service.py`
- **核心概念**: 建立一個 `DocumentService` 來集中管理所有與 Gemini File API 的互動。
- **主要職責**:
  - **封裝 SDK 操作**: 使用 `google-generativeai` SDK，將底層的 `genai.files` API 呼叫（如 `upload_file`, `list_files`, `get_file`, `delete_file`）封裝成高階的服務方法。
  - **狀態管理**: 追蹤已上傳檔案的狀態與元資料。
  - **錯誤處理**: 統一處理 API 請求可能發生的錯誤。

#### 2. `file_search` 功能工具化

- **實作位置**: `backend/tools/document_tools.py`
- **核心概念**: 將 `DocumentService` 的 `file_search` 功能包裝成一個 Agent 可以直接呼叫的工具 (Tool)。
- **設計模式**:
  - Agent 本身不直接與 `DocumentService` 或 Gemini SDK 互動。
  - Agent 透過呼叫 `file_search` 工具來觸發 RAG 流程。
  - 工具內部再呼叫 `DocumentService` 來執行實際的檔案檢索。
  - 這種設計降低了 Agent 的複雜性，並提高了模組的獨立性與可測試性。

#### 3. Agent 整合與模型配置

- **工具註冊**: 將 `file_search` 工具註冊到 `ConversationAgent` 和 `StrategicPlannerAgent` 中。
- **模型配置**: 在初始化 Gemini 模型時，將 `file_search` 工具傳遞給模型，使其具備使用此工具的能力。
- **自動化 RAG**: 當使用者提出與已上傳文件相關的問題時，LLM 會自動判斷並呼叫 `file_search` 工具來尋找答案，並根據檢索結果生成回應。

### 技術特色與優勢

- **關注點分離 (SoC)**: 透過 `Service -> Tool -> Agent` 的分層架構，將資料處理、工具邏輯和 Agent 決策清晰地分開。
- **Agent 輕量化**: Agent 只需專注於對話流程與工具選擇，無需了解檔案檢索的底層實作細節。
- **可擴展性**: 未來若要增加新的文檔來源（如資料庫、Web API），只需擴展 `DocumentService` 或新增工具，而無需修改 Agent 核心邏輯。
- **零配置 RAG**: 對於 Agent 來說，RAG 是一個開箱即用的能力，由模型根據上下文自動觸發。

### 完成狀態

- ✅ `google-generativeai` SDK 安裝與配置
- ✅ `DocumentService` 服務層封裝完成
- ✅ `file_search` 工具實作與註冊
- ✅ Agent 成功整合 RAG 工具
- ✅ 文檔上傳與問答功能測試驗證

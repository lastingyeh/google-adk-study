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

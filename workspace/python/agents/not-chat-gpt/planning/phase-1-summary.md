# Phase 1 Summary

## 1.3 Session State Management (參考 Day 17: personal-tutor)

### 實踐概述

成功在 `ConversationAgent` 中實作了三層狀態管理機制，模仿 GPT 的記憶與上下文能力。此實作參考了 personal-tutor 範例的狀態管理設計，並透過 ADK 的 `ToolContext` 實現了持久化的會話狀態。

### 核心架構

#### 三層狀態設計

1. **永久使用者狀態** (`user:` 前綴)
   - 跨會話永久保存的使用者個人資訊
   - 例如：姓名、偏好設定
   - 使用 `remember_user_info()` 和 `get_user_info()` 工具管理

2. **會話狀態** (無前綴)
   - 當前對話的歷史紀錄
   - 維持多輪對話的上下文連貫性
   - 透過 `add_message_to_history()` 工具管理

3. **暫存狀態** (`temp:` 前綴)
   - 單次呼叫的暫時分析資料
   - 用於意圖分析、中間步驟思考
   - 使用 `analyze_intent()` 工具管理

#### 狀態管理工具實作

```python
# 永久使用者資訊管理
def remember_user_info(key: str, value: str, tool_context: ToolContext)
def get_user_info(key: str, tool_context: ToolContext)

# 會話歷史管理
def add_message_to_history(role: str, content: str, tool_context: ToolContext)

# 暫存意圖分析
def analyze_intent(intent: str, tool_context: ToolContext)
```

### 技術實作細節

#### ToolContext 整合

- 使用 ADK 提供的 `ToolContext` 作為狀態容器
- 透過 `tool_context.state` 字典存取各層狀態
- 狀態前綴機制區分不同生命週期的資料

#### 會話生命週期管理

- 利用 `adk api_server` 內建的會話管理端點
- `POST /apps/{appName}/users/{userId}/sessions/{sessionId}` 建立會話
- `/run` 端點執行時自動載入對應會話狀態

#### 多輪對話流程

1. 使用者訊息透過 `/run` 端點傳入
2. Agent 將訊息加入對話歷史
3. 如偵測到個人資訊，自動儲存至永久狀態
4. 生成回應並同樣加入歷史紀錄
5. 狀態自動持久化至會話中

### 測試驗證

#### 會話建立測試

```bash
curl --location 'http://localhost:8000/apps/conversation_agent/users/u_123/sessions/s_123' \
--header 'Content-Type: application/json' \
--data '{"key1": "value1", "key2": 42}'
```

#### 多輪對話測試

**第一輪 - 資訊收集**:

```bash
curl --location 'http://localhost:8000/run' \
--data '{
    "appName": "conversation_agent",
    "userId": "u_123",
    "sessionId": "s_123",
    "newMessage": {
        "role": "user",
        "parts": [{"text": "Hi, 我是 Chris, 是一名資深工程師, 喜歡跑步."}]
    }
}'
```

**第二輪 - 記憶驗證**:

```bash
curl --location 'http://localhost:8000/run' \
--data '{
    "appName": "conversation_agent",
    "userId": "u_123",
    "sessionId": "s_123",
    "newMessage": {
        "role": "user",
        "parts": [{"text": "我是誰?"}]
    }
}'
```

### 關鍵成果

1. **狀態持久化**: 成功實現跨請求的狀態保持
2. **記憶能力**: Agent 能記住並引用先前的使用者資訊
3. **上下文連貫**: 多輪對話保持話題連續性
4. **架構彈性**: 三層設計支援不同生命週期需求
5. **ADK 整合**: 完全利用 ADK 內建功能，無需自建會話管理

### 後續優化方向

1. **狀態壓縮**: 當對話歷史過長時的自動摘要機制
2. **智能遺忘**: 根據時間或重要性自動清理過時資訊
3. **狀態同步**: 多設備間的狀態同步機制
4. **性能優化**: 大量狀態資料的高效存取策略

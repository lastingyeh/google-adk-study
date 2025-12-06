# ADK 中使用特定使用者身分進行測試 (Testing with Specific User Identities in ADK)

**如何測試商務代理人的多用戶隔離與偏好**

## ⚠️ 重要：沒有用於設定 User ID 的 UI

**`adk web` 介面「不提供」用於設定 User ID 或 Session ID 的 UI 面板。**

ADK 網頁介面針對所有基於瀏覽器的會話使用 **固定的預設使用者 ID ("user")**。要使用特定使用者身分進行測試，您 **必須直接使用 API 端點**。

---

## 測試方法

### 方法 1：使用 curl 進行 API 測試 ✅ 推薦

使用 ADK REST API 為特定使用者建立會話並以程式設計方式發送訊息。

### 方法 2：Python 腳本 ✅ 替代方案

編寫 Python 腳本，以不同的 User ID 呼叫 API 端點。

### 方法 3：~~UI 面板~~ ❌ 不可用

在 `adk web` 中沒有用於設定自定義 User ID 的 UI 面板。

---

## 方法 1：使用 curl 進行 API 測試

### 先決條件

```bash
# 終端機 1：啟動伺服器
cd tutorial_implementation/commerce_agent_e2e
make dev-sqlite  # 或：make dev

# 伺服器執行於 http://localhost:8000
```

### 步驟 1：為不同使用者建立會話

```bash
# 為 Alice (跑者) 建立會話
curl -X POST http://localhost:8000/apps/commerce_agent/users/alice/sessions/session_001 \
  -H "Content-Type: application/json" \
  -d '{"state": {}}'

# 為 Bob (騎行者) 建立會話
curl -X POST http://localhost:8000/apps/commerce_agent/users/bob/sessions/session_002 \
  -H "Content-Type: application/json" \
  -d '{"state": {}}'
```

**回應：**
```json
{"id":"session_001","appName":"commerce_agent","userId":"alice","state":{},"events":[],"lastUpdateTime":1730000000.0}
```

### 步驟 2：以特定使用者身分發送訊息

**Alice (150 歐元以下的慢跑鞋)：**
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "commerce_agent",
    "user_id": "alice",
    "session_id": "session_001",
    "new_message": {
      "role": "user",
      "parts": [{"text": "I want running shoes under 150 euros"}]
    }
  }'
```

**Bob (騎行裝備，預算 200 歐元)：**
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "commerce_agent",
    "user_id": "bob",
    "session_id": "session_002",
    "new_message": {
      "role": "user",
      "parts": [{"text": "I am into cycling. My budget is 200 euros"}]
    }
  }'
```

### 步驟 3：驗證使用者隔離

**檢查 Alice 的偏好 (應該是跑步，而不是騎行)：**
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "commerce_agent",
    "user_id": "alice",
    "session_id": "session_001",
    "new_message": {
      "role": "user",
      "parts": [{"text": "What are my preferences?"}]
    }
  }'
```

**預期結果：** 代理人回應跑步偏好，未提及騎行。

### 步驟 4：檢查會話狀態

```bash
# 取得 Alice 的會話
curl -X GET http://localhost:8000/apps/commerce_agent/users/alice/sessions/session_001

# 取得 Bob 的會話
curl -X GET http://localhost:8000/apps/commerce_agent/users/bob/sessions/session_002
```

**回應顯示隔離的狀態：**
```json
{
  "id": "session_001",
  "appName": "commerce_agent",
  "userId": "alice",
  "state": {
    "user:sport": "running",
    "user:budget": 150,
    "user:experience": "beginner"
  },
  "events": [...],
  "lastUpdateTime": 1730000000.0
}
```

---

## 方法 2：Python 腳本測試

建立一個測試腳本以自動化多用戶測試：

```python
# test_multi_user.py
import requests
import json

BASE_URL = "http://localhost:8000"

def create_session(user_id, session_id):
    """為使用者建立新會話"""
    url = f"{BASE_URL}/apps/commerce_agent/users/{user_id}/sessions/{session_id}"
    response = requests.post(url, json={"state": {}})
    print(f"✅ Created session for {user_id}: {response.status_code}")
    return response.json()

def send_message(user_id, session_id, message):
    """以特定使用者身分發送訊息"""
    url = f"{BASE_URL}/run"
    payload = {
        "app_name": "commerce_agent",
        "user_id": user_id,
        "session_id": session_id,
        "new_message": {
            "role": "user",
            "parts": [{"text": message}]
        }
    }
    response = requests.post(url, json=payload)
    events = response.json()

    # 提取代理人的文字回應
    for event in events:
        if event.get("content", {}).get("role") == "model":
            parts = event["content"]["parts"]
            for part in parts:
                if "text" in part:
                    return part["text"]
    return "No response"

def get_session_state(user_id, session_id):
    """取得會話狀態"""
    url = f"{BASE_URL}/apps/commerce_agent/users/{user_id}/sessions/{session_id}"
    response = requests.get(url)
    return response.json()

# 測試多用戶隔離
if __name__ == "__main__":
    print("🧪 Testing Multi-User Isolation (測試多用戶隔離)\n")

    # 設定 Alice (跑者)
    print("👤 ALICE (Runner)")
    create_session("alice", "session_001")
    response = send_message("alice", "session_001", "I want running shoes under 150 euros")
    print(f"Agent: {response[:100]}...\n")

    # 設定 Bob (騎行者)
    print("👤 BOB (Cyclist)")
    create_session("bob", "session_002")
    response = send_message("bob", "session_002", "I am into cycling. Budget 200 euros")
    print(f"Agent: {response[:100]}...\n")

    # 驗證 Alice 的偏好 (不應提及騎行)
    print("🔍 Verifying Alice's Preferences (驗證 Alice 的偏好)")
    response = send_message("alice", "session_001", "What are my preferences?")
    print(f"Agent: {response}\n")

    if "cycling" in response.lower():
        print("❌ FAILURE: Alice's preferences contaminated with Bob's data!")
    else:
        print("✅ SUCCESS: User isolation working correctly!")

    # 顯示狀態
    print("\n📊 Session States (會話狀態):")
    alice_state = get_session_state("alice", "session_001")
    bob_state = get_session_state("bob", "session_002")
    print(f"Alice state: {alice_state.get('state', {})}")
    print(f"Bob state: {bob_state.get('state', {})}")
```

**執行腳本：**
```bash
python test_multi_user.py
```

---

## SQLite 持久性測試

### 測試跨重啟的會話持久性

```bash
# 1. 使用 SQLite 啟動
make dev-sqlite

# 2. 為 athlete_test 建立會話
curl -X POST http://localhost:8000/apps/commerce_agent/users/athlete_test/sessions/persistent_session \
  -H "Content-Type: application/json" \
  -d '{"state": {}}'

# 3. 儲存偏好
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "commerce_agent",
    "user_id": "athlete_test",
    "session_id": "persistent_session",
    "new_message": {
      "role": "user",
      "parts": [{"text": "I prefer running shoes under 150 euros"}]
    }
  }'

# 4. 停止伺服器 (在終端機 1 按 Ctrl+C)

# 5. 重啟伺服器
make dev-sqlite

# 6. 驗證資料仍存在
curl -X GET http://localhost:8000/apps/commerce_agent/users/athlete_test/sessions/persistent_session

# 7. 發送新訊息 (應該記得偏好)
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "commerce_agent",
    "user_id": "athlete_test",
    "session_id": "persistent_session",
    "new_message": {
      "role": "user",
      "parts": [{"text": "What do you recommend?"}]
    }
  }'
```

**預期結果：** 代理人在重啟後記得跑步偏好和預算。 ✅

---

## 使用 ADK Web UI (僅限預設使用者)

`adk web` 瀏覽器介面仍可用於測試，但將 **始終使用 User ID "user"**：

```bash
# 啟動伺服器
make dev

# 打開瀏覽器：http://localhost:8000
# 在 UI 中聊天

# 所有瀏覽器會話使用：
#   User ID: "user"
#   Session ID: 由 UI 自動產生
```

**限制：** 無法僅透過 UI 測試多用戶隔離。

**解決方法：** 使用 UI 進行初始測試，然後切換到 API 端點進行多用戶情境測試。

---

## 常見測試情境

### 情境 1：新用戶導引 (New User Onboarding)

```bash
# User: new_customer_123
# 目標：測試首次偏好收集

curl -X POST http://localhost:8000/apps/commerce_agent/users/new_customer_123/sessions/onboarding_001 \
  -H "Content-Type: application/json" \
  -d '{"state": {}}'

curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "commerce_agent",
    "user_id": "new_customer_123",
    "session_id": "onboarding_001",
    "new_message": {
      "role": "user",
      "parts": [{"text": "I want running shoes"}]
    }
  }'
```

**預期結果：** 代理人詢問預算、經驗水平、偏好。

### 情境 2：回訪客戶 (Returning Customer)

```bash
# 同一位使用者，新會話
curl -X POST http://localhost:8000/apps/commerce_agent/users/new_customer_123/sessions/returning_002 \
  -H "Content-Type: application/json" \
  -d '{"state": {}}'

curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "commerce_agent",
    "user_id": "new_customer_123",
    "session_id": "returning_002",
    "new_message": {
      "role": "user",
      "parts": [{"text": "Show me new products"}]
    }
  }'
```

**預期結果：** 代理人從先前的會話召回偏好 (如果使用 SQLite 或 user: state)。

### 情境 3：多用戶家庭 (Multi-User Household)

```bash
# 家庭成員共用一個裝置
# User: parent_runner (跑者父母)
# User: child_beginner (初學者小孩)
# User: partner_cyclist (騎行者伴侶)

# 每個人獲得隔離的偏好
curl -X POST http://localhost:8000/apps/commerce_agent/users/parent_runner/sessions/s001 \
  -H "Content-Type: application/json" -d '{"state": {}}'

curl -X POST http://localhost:8000/apps/commerce_agent/users/child_beginner/sessions/s001 \
  -H "Content-Type: application/json" -d '{"state": {}}'

curl -X POST http://localhost:8000/apps/commerce_agent/users/partner_cyclist/sessions/s001 \
  -H "Content-Type: application/json" -d '{"state": {}}'
```

**預期結果：** 家庭成員之間完全的資料隔離。

---

## 除錯技巧

### 問題：偏好未儲存

**檢查會話狀態：**
```bash
curl -X GET http://localhost:8000/apps/commerce_agent/users/YOUR_USER_ID/sessions/YOUR_SESSION_ID
```

**驗證狀態包含 `user:` 前綴的鍵：**
```json
{
  "state": {
    "user:sport": "running",
    "user:budget": 150
  }
}
```

### 問題：偏好在使用者之間混淆

**驗證使用不同的 User IDs：**
```bash
# 錯誤 - 相同 user ID
user_id: "alice" → session_001
user_id: "alice" → session_002  # 相同使用者，不同會話

# 正確 - 不同 user ID
user_id: "alice" → session_001
user_id: "bob" → session_002   # 不同使用者
```

### 問題：偏好在重啟後遺失

**檢查持久化模式：**

| 模式 | 行為 |
|------|----------|
| `make dev` | ADK 狀態 - 偏好可能「不會」跨重啟持久化 |
| `make dev-sqlite` | SQLite DB - 偏好「應該」跨重啟持久化 |

**驗證 SQLite 資料庫：**
```bash
sqlite3 commerce_sessions.db
> SELECT id, user_id FROM sessions;
> .quit
```

---

## 摘要

### ✅ 有效的方法

- **API 端點**：完全控制 User ID 和 Session ID
- **Python 腳本**：自動化多用戶測試
- **SQLite 持久性**：會話資料在重啟後仍然存在

### ❌ 無效的方法

- **UI 面板**：沒有 User ID 的 UI 控制 (使用固定的 "user")
- **瀏覽器測試**：受限於預設使用者，無法進行 API 呼叫

### 🎯 最佳實踐

**對於多用戶測試：**
1. 使用 `make dev-sqlite` 進行持久化
2. 透過 API 使用特定 User IDs 建立會話
3. 透過 API 為每位使用者發送訊息
4. 透過檢查會話狀態驗證隔離
5. 使用 Python 腳本自動化測試情境

---

## 參考連結

- **官方 ADK 測試指南**：https://google.github.io/adk-docs/get-started/testing/
- **ADK API 參考**：https://google.github.io/adk-docs/api-reference/rest/
- **會話管理**：https://google.github.io/adk-docs/sessions/
- **SQLite 持久性指南**：`docs/SQLITE_SESSION_PERSISTENCE_GUIDE.md`

---

**最後更新**：2025-10-27
**ADK 版本**：1.17.0+

---
# 重點摘要

- **核心概念**：
    - **API 測試**：繞過 Web UI 限制，直接與 ADK 後端互動。
    - **多用戶隔離**：驗證不同 `user_id` 的資料互不干擾。
    - **會話狀態檢查**：透過 GET 請求驗證後端儲存的狀態是否正確。

- **關鍵技術**：
    - **curl**：命令列 HTTP 客戶端，用於發送 API 請求。
    - **REST API**：ADK 提供的標準介面，用於管理會話和執行代理人。
    - **Python Requests**：用於編寫自動化測試腳本。

- **重要結論**：
    - Web UI 僅適合單一使用者 ("user") 的基本測試。
    - 要驗證多用戶功能，必須使用 API (curl 或腳本)。
    - `make dev-sqlite` 是測試持久性的關鍵，`make dev` 僅使用記憶體內儲存。

- **行動項目**：
    - 建立 `test_multi_user.py` 腳本以自動化驗證流程。
    - 在開發過程中使用 `make dev-sqlite` 來模擬真實的生產環境行為。
    - 使用 `sqlite3` CLI 工具直接檢查資料庫內容以進行除錯。

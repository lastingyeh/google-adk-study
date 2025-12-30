# NotChatGPT CLI 使用指南

## ✅ 驗證狀態

**最後驗證時間**: 2025-12-30

所有功能已驗證可正常執行：
- ✅ 模組 Import
- ✅ 對話記憶（多輪對話上下文）
- ✅ 思考模式切換
- ✅ 安全防護（PII 偵測）
- ✅ Session 管理（資料庫持久化）

## 🚀 快速開始

### 1. 安裝依賴

```bash
pip install -r backend/requirements.txt
```

### 2. 設定環境變數

建立 `.env` 檔案：

```env
GOOGLE_API_KEY=your_api_key_here
MODEL_NAME=gemini-2.0-flash-exp
```

### 3. 執行 CLI

```bash
python backend/cli.py
```

## 📖 指令說明

### 基本指令

| 指令 | 說明 |
|------|------|
| `/thinking` | 切換到思考模式（顯示詳細思考過程） |
| `/standard` | 切換到標準模式 |
| `/safe on` | 啟用安全防護（PII 偵測） |
| `/safe off` | 停用安全防護 |
| `/quit` | 退出 CLI |

### Session 管理指令

| 指令 | 說明 |
|------|------|
| `/new` | 建立新對話 |
| `/list` | 列出所有對話 |
| `/load <id>` | 載入指定對話（支援 ID 前綴匹配） |
| `/history` | 顯示當前對話歷史 |

## 🎯 功能特色

### 1. 多輪對話記憶

CLI 會自動記住對話上下文：

```
You: 我叫小明
Agent: 你好，小明！

You: 我剛才說我叫什麼名字？
Agent: 你剛才說你叫小明。
```

### 2. 思考模式

啟用思考模式後，Agent 會展示詳細的思考過程：

```
You: /thinking
💭 已切換到思考模式

You: 為什麼 Python 很受歡迎？
Agent: [顯示詳細的分析過程...]
```

### 3. 安全防護

自動偵測並攔截敏感資訊（PII）：

```
You: 我的信用卡號是 1234-5678-9012-3456
⚠️ 無法處理此請求: 偵測到敏感資訊: credit_card
```

支援的 PII 類型：
- 信用卡號
- Email
- 電話號碼
- 台灣身份證號

封鎖關鍵字：
- 密碼
- 信用卡
- 身份證
- 帳號

### 4. 對話持久化

所有對話自動儲存到 SQLite 資料庫（`not_chat_gpt.db`）：

```
You: /list
📝 對話清單 (共 3 個):
👉 abc12345... - CLI Session (更新: 2025-12-30 10:30)
   def67890... - CLI Session (更新: 2025-12-30 09:15)
```

重啟 CLI 後可以載入歷史對話：

```
You: /load abc12345
📂 已載入對話: abc12345...
📜 對話歷史 (共 4 則訊息)
```

## 🧪 測試驗證

### 執行功能驗證

```bash
python verify_cli.py
```

預期輸出：

```
============================================================
CLI 功能驗證測試
============================================================

🧪 測試 1: 檢查模組 import...
✅ 所有模組 import 成功

🧪 測試 2: ModeConfig 功能...
✅ ModeConfig 測試通過

🧪 測試 3: SessionService 功能...
✅ SessionService 測試通過

🧪 測試 4: PII 偵測功能...
✅ PII 偵測測試通過

🧪 測試 5: safe_generate_response 簽名...
✅ safe_generate_response 簽名正確

🎉 所有測試通過！(5/5)
```

### 執行完整功能測試

```bash
./test_cli.sh
```

## 📂 資料庫結構

CLI 使用 SQLite 資料庫儲存對話：

### conversations 表

| 欄位 | 類型 | 說明 |
|------|------|------|
| id | String | 對話 ID（UUID） |
| title | String | 對話標題 |
| state | Text | JSON 格式的狀態 |
| created_at | DateTime | 建立時間 |
| updated_at | DateTime | 更新時間 |

### messages 表

| 欄位 | 類型 | 說明 |
|------|------|------|
| id | Integer | 訊息 ID（自動遞增） |
| conversation_id | String | 所屬對話 ID |
| role | String | 角色（'user' 或 'model'） |
| content | Text | 訊息內容 |
| created_at | DateTime | 建立時間 |

## 🔧 故障排除

### 問題：Import 錯誤

```
ModuleNotFoundError: No module named 'config'
```

**解決方案**：確保從正確的目錄執行 CLI

```bash
cd /path/to/not-chat-gpt
python backend/cli.py
```

### 問題：API Key 未設定

```
❌ 錯誤: GOOGLE_API_KEY 未設定在 .env 檔案中
```

**解決方案**：檢查 `.env` 檔案是否存在且包含正確的 API Key

### 問題：資料庫鎖定

```
sqlite3.OperationalError: database is locked
```

**解決方案**：關閉其他正在使用資料庫的 CLI 實例

## 📝 開發說明

### 架構設計

```
backend/
├── cli.py                          # CLI 主程式
├── agents/
│   └── safe_conversation_agent.py  # 安全對話 Agent
├── config/
│   └── mode_config.py              # 模式配置
├── services/
│   └── session_service.py          # Session 管理
└── guardrails/
    ├── pii_detector.py             # PII 偵測
    └── safety_callbacks.py         # 安全回調
```

### 執行流程

1. **初始化**：載入環境變數、建立 Session
2. **使用者輸入**：處理命令或訊息
3. **載入歷史**：從資料庫載入對話歷史
4. **安全檢查**：驗證輸入（如果啟用）
5. **生成回應**：呼叫 Gemini API
6. **過濾輸出**：清理回應中的 PII
7. **儲存記錄**：寫入資料庫

## 🎉 完成狀態

- [x] 基礎對話功能
- [x] 多輪對話記憶
- [x] 思考模式切換
- [x] 安全防護（PII 偵測）
- [x] Session 管理
- [x] 對話持久化
- [x] 完整測試驗證

---

**版本**: Phase 1 Complete  
**最後更新**: 2025-12-30

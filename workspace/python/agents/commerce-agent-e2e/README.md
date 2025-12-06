# Commerce Agent E2E - 端到端實作

**一個具備生產力等級的多用戶商務代理人 (Commerce Agent)**，展示了 Google ADK v1.17.0 的進階功能，包括：
- ✅ 使用 SQLite 進行持久化會話管理 (Persistent Session Management)
- ✅ **Grounding Metadata** 提取以進行來源歸因
- ✅ 具備完整資料安全性的多用戶隔離
- ✅ 克服 ADK 限制的工具整合模式
- ✅ 具備資料庫支援的自定義工具
- ✅ 多代理人協作 (Multi-agent Coordination)
- ✅ 完整的測試套件

## 🎯 你將學到什麼

本教學展示了：

- ✅ **會話持久性 (Session Persistence)**：使用 ADK 的 `DatabaseSessionService` 搭配 SQLite 資料庫
- ✅ **Grounding Metadata**：從 Google Search 提取並顯示來源歸因
- ✅ **引用管理 (Citation Management)**：追蹤哪些來源支持哪些產品聲明
- ✅ **URL 驗證**：透過僅使用真實的搜尋結果 URL 來防止幻覺 (Hallucination)
- ✅ **多用戶支援**：使用者之間完全的資料隔離
- ✅ **工具架構**：使用子代理人模式克服 ADK 限制
- ✅ **自定義工具**：資料庫支援的偏好管理與引用驗證
- ✅ **多代理人協作**：由根代理人 (Root Agent) 編排 3 個專門的子代理人
- ✅ **完整的測試**：單元測試、整合測試與端到端測試套件
- ✅ **生產模式**：錯誤處理、確認流程、狀態管理
- ✅ **型別安全 (Type Safety)**：所有工具介面的 `TypedDict` 定義
- ✅ **可觀察性 (Observability)**：用於來源歸因追蹤的 `GroundingMetadataCallback`

### 🌟 Grounding Metadata 功能

**新增：來源歸因與引用**

商務代理人現在可以從 Google Search 結果中提取並保留接地元數據：

| 功能 | 優點 |
|---------|---------|
| **來源區塊 (Source Chunks)** | 來自搜尋結果的確切 URL 和標題 |
| **片段歸因 (Segment Attribution)** | 知道哪些來源支持哪些聲明 |
| **信心分數 (Confidence Scores)** | 多個來源 = 更高的信心 |
| **URL 驗證** | 所有 URL 皆經過搜尋結果驗證 |
| **引用驗證** | 檢測 URL 幻覺的工具 |
| **品質評分** | 整體的接地品質指標 |

**客戶體驗影響**：
- 🎯 **信任**：每一個產品事實都可追溯至權威來源
- 🔗 **驗證**：使用者可以點擊以獨立驗證資訊
- 💯 **準確性**：多個來源降低了幻覺風險
- 🏪 **透明度**：確切知道每個連結來自哪家零售商

## 🚀 快速開始 (Quick Start)

### 先決條件

- Python 3.9+
- Vertex AI Service Account (推薦) 或 Google API Key
- SQLite3 (macOS/Linux 已預先安裝)

### 兩種執行方式

**選項 1：ADK Web 介面** (預設 - 使用 ADK 狀態)
```bash
make dev  # 訪問 http://localhost:8000
```

**選項 2：SQLite 持久化會話** (進階 - 重啟後資料仍存在)
```bash
python runner_with_sqlite.py
```

請參閱下方的 **[會話持久性選項](#1-會話持久性)** 進行比較。

### 驗證設定 (Authentication Setup)

**⚠️ 重要：** 此代理人使用 **Vertex AI 驗證** 效果最佳。使用 Gemini API (`GOOGLE_API_KEY`) 會破壞 "site:decathlon.com.hk" 搜尋運算子。

#### 選項 A：Vertex AI (推薦)

```bash
# 導航至教學目錄
cd tutorial_implementation/commerce_agent_e2e

# 執行 Vertex AI 設定腳本 (處理環境變數)
make setup-vertex-ai

# 按照提示設定服務帳戶 (Service Account)
```

該腳本將會：
1. ✅ 驗證位於 `./credentials/commerce-agent-key.json` 的服務帳戶憑證
2. ✅ 取消設定任何衝突的 Gemini API 金鑰
3. ✅ 設定 `GOOGLE_CLOUD_PROJECT` 和 `GOOGLE_APPLICATION_CREDENTIALS`
4. ✅ 測試憑證是否正常運作

#### 選項 B：Gemini API (受限)

```bash
# 導航至教學目錄
cd tutorial_implementation/commerce_agent_e2e

# 設定 API 金鑰
export GOOGLE_API_KEY=your_key_here
# 在此獲取免費金鑰: https://aistudio.google.com/app/apikey
```

**⚠️ 限制：** "site:decathlon.com.hk" 搜尋運算子無法與 Gemini API 一起使用。

### 安裝 (2 分鐘)

```bash
# 安裝相依套件
make setup

# 執行測試 (可選)
make test

# 啟動開發 UI
make dev

# 在瀏覽器中打開 http://localhost:8000
# 從下拉選單中選擇 "commerce_agent"
```

## 💾 會話持久性選項 (Session Persistence Options)

為您的使用案例選擇合適的持久性策略：

### 選項 1：ADK 狀態 (預設 - 簡單)

**它是什麼？**
ADK 內建的狀態管理，使用 `user:` 前綴進行跨會話持久化。

**如何運作：**
```python
# 工具修改狀態
def save_preferences(sport: str, tool_context: ToolContext):
    tool_context.state["user:sport"] = sport  # 自動持久化
    return {"status": "success"}

# 狀態在不同調用間持續存在
def get_preferences(tool_context: ToolContext):
    return {"data": tool_context.state.get("user:sport")}
```

**最適合：**
- ✅ 簡單的使用者偏好 (運動、預算、經驗水平)
- ✅ 快速原型製作和開發
- ✅ 單一伺服器部署
- ✅ 鍵值 (Key-value) 資料模式

**目前的實作：** 這就是商務代理人目前使用的模式。

### 選項 2：使用 SQLite 的 DatabaseSessionService (進階)

**它是什麼？**
ADK 內建的 SQL 持久化，用於會話、狀態和對話歷史記錄。

**如何運作：**
```python
from google.adk.sessions import DatabaseSessionService

# 一次性設定
session_service = DatabaseSessionService(
    db_url="sqlite:///./sessions.db?mode=wal"
)

runner = Runner(
    agent=root_agent,
    session_service=session_service
)

# 一切都會持久化：狀態、事件、時間戳記
session = await session_service.get_session("app", "user", "session_id")
# 資料在應用程式重啟後仍然存在！ ✅
```

**與 adk web 一起使用 (官方支援)：**
```bash
# SQLite 持久化 (會話在重啟後存在)
adk web --session_service_uri sqlite:///./sessions.db

# 使用 WAL 模式 (推薦)
adk web --session_service_uri "sqlite:///./sessions.db?mode=wal"

# PostgreSQL (生產環境)
adk web --session_service_uri postgresql://user:pass@localhost/adk_sessions
```

**參考：** [ADK CLI 文件](https://google.github.io/adk-docs/api-reference/cli/cli.html#web)

**最適合：**
- ✅ 具有隔離要求的多用戶應用程式
- ✅ 對話歷史記錄保存
- ✅ 複雜查詢 (SQL JOINs, filters)
- ✅ 生產環境部署

**立即嘗試：**
```bash
# 執行 SQLite 展示
python runner_with_sqlite.py

# 查看完整指南
cat docs/SQLITE_SESSION_PERSISTENCE_GUIDE.md
```

### 比較表

| 功能 | ADK 狀態 (`user:` 前綴) | DatabaseSessionService (SQLite) |
|---------|----------------------------|----------------------------------|
| **設定** | ✅ 零設定 | ⚠️ 需要資料庫 URL |
| **持久性** | ✅ 跨會話 | ✅ 跨重啟 |
| **對話歷史** | ❌ 不儲存 | ✅ 完整事件日誌 |
| **多用戶隔離** | ✅ 良好 (透過狀態鍵) | ✅ 極佳 (透過 DB 行) |
| **查詢** | ❌ 僅鍵值 | ✅ SQL 查詢、JOINs |
| **可擴展性** | ✅ 適合簡單資料 | ✅ 適合複雜資料 |
| **生產資料庫** | ❌ 記憶體內/臨時儲存 | ✅ PostgreSQL/MySQL/Spanner |
| **目前商務代理人** | ✅ **使用此方式** | ⏳ 可作為選項提供 |

### 何時切換？

**保持 ADK 狀態，如果：**
- 您有簡單的使用者偏好 (運動、預算、經驗)
- 您正在製作原型或開發中
- 您不需要對話歷史記錄

**切換到 DatabaseSessionService，如果：**
- 您需要跨重啟保留對話歷史記錄
- 您有複雜的多用戶需求
- 您需要 SQL 查詢功能
- 您正在大規模部署到生產環境

**文件：**
- **SQLite 指南**：`docs/SQLITE_SESSION_PERSISTENCE_GUIDE.md` (綜合)
- **工作範例**：`runner_with_sqlite.py` (可直接執行)
- **ADK 文件**：https://google.github.io/adk-docs/sessions/

## 📂 專案結構

```
commerce-agent-e2e/
├── commerce_agent/              # 主套件
│   ├── __init__.py             # 套件導出
│   ├── agent.py                # 基礎代理人 (根代理人 + 3 個子代理人)
│   ├── agent_enhanced.py       # 增強型多代理人協調器
│   ├── tools.py                # 自定義偏好與策展工具
│   ├── models.py               # Pydantic 資料模型
│   ├── types.py                # 增強型別定義
│   ├── config.py               # 設定常數
│   ├── database.py             # SQLite 持久層
│   ├── callbacks.py            # 代理人生命週期回調
│   ├── grounding_metadata.py   # 來源歸因處理
│   ├── search_agent.py         # 產品搜尋專家
│   ├── search_product.py       # 搜尋工具實作
│   ├── preferences_agent.py    # 使用者偏好管理器
│   ├── sub_agents/             # 增強型專門子代理人
│   │   ├── preference_collector.py
│   │   ├── product_advisor.py
│   │   ├── visual_assistant.py
│   │   └── checkout_assistant.py
│   └── tools/                  # 增強型工具模組
│       ├── cart_tools.py
│       └── multimodal_tools.py
│
├── tests/                      # 完整的測試套件
│   ├── conftest.py             # 測試固定裝置 (Fixtures) 和設定
│   ├── test_tools.py           # 工具的單元測試
│   ├── test_integration.py     # 整合測試
│   ├── test_e2e.py             # 端到端使用者情境測試
│   └── test_agent_instructions.py # 代理人指令測試
│
├── eval/                       # 評估框架
│   ├── eval_data/              # 測試情境和資料集
│   └── test_eval.py            # 評估測試
│
├── scripts/                    # 設定和實用腳本
│   └── setup-vertex-ai.sh      # Vertex AI 驗證設定
│
├── credentials/                # 服務帳戶金鑰 (gitignored)
├── pyproject.toml              # Python 專案元數據
├── requirements.txt            # 相依套件
├── Makefile                    # 常用指令
├── .env.example                # 環境變數範本
├── .gitignore                  # Git 忽略規則
└── README.md                   # 本檔案
```

## 🏗️ 代理人架構 (Agent Architecture)

```mermaid
graph TD
    User((使用者)) --> Root[商務協調員<br/>CommerceCoordinator]
    Root --> Search[產品搜尋代理人<br/>ProductSearchAgent]
    Root --> Pref[偏好管理器<br/>PreferenceManager]
    Root --> Story[敘事代理人<br/>StorytellerAgent]

    Search --> Google[Google Search 工具]
    Pref --> DB[(SQLite 資料庫)]
    Story --> LLM[LLM 生成]
```

### 根代理人：CommerceCoordinator

編排三個專門的子代理人：

- **ProductSearchAgent**：負責產品搜尋 (Google Search 工具)
- **PreferenceManager**：負責偏好管理 (自定義偏好工具)
- **StorytellerAgent**：負責產生引人入勝的敘事 (純 LLM)

### 狀態管理 (State Management)

三層狀態範圍系統：

| 範圍 | 前綴 | 生命週期 | 範例 |
|-------|--------|----------|---------|
| Session (會話) | 無 | 當前聊天 | `current_query` |
| User (使用者) | `user:` | 持久化 | `user:preferences` |
| App (應用程式) | `app:` | 全域 | `app:product_cache` |
| Temp (臨時) | `temp:` | 當前輪次 | `temp:buffer` |

**關鍵**：使用者範圍的資料 (`user:*`) 在 SQLite 中透過 `user_id` 完全隔離。

### 資料庫架構

```sql
user_preferences      -- 使用者運動項目、價格範圍、品牌
interaction_history   -- 搜尋查詢和結果追蹤
user_favorites        -- 願望清單和儲存的產品
product_cache         -- 搜尋結果快取 (應用程式範圍)
```

## 🧪 測試

### 執行所有測試

```bash
make test
```

### 使用特定使用者身分進行測試

**⚠️ 重要：ADK web UI 沒有用於設定 User ID 的面板**

`adk web` 瀏覽器介面使用固定的預設使用者 ID ("user") 進行所有會話。要使用特定使用者身分 (alice, bob 等) 進行測試，您 **必須直接使用 API 端點**。

**完整指南**：請參閱 [docs/TESTING_WITH_USER_IDENTITIES.md](docs/TESTING_WITH_USER_IDENTITIES.md)，內容包括：
-  **使用 curl 進行 API 測試** (設定自定義 User ID 的唯一方法)
- 🐍 **Python 腳本** 用於自動化多用戶測試
- 👥 **多用戶隔離測試** (Alice 與 Bob 情境)
- 💾 **SQLite 持久性驗證** 跨重啟測試
- 🎯 **常見測試情境** (新用戶導引、回訪客戶、多用戶家庭)
- 🐛 **除錯技巧** 針對偏好問題

**快速查看指南**：
```bash
make test-guide   # 在終端機查看 API 測試說明
```

**快速 API 範例**：
```bash
# 為 alice 建立會話
curl -X POST http://localhost:8000/apps/commerce_agent/users/alice/sessions/s1 \
  -H "Content-Type: application/json" -d '{"state": {}}'

# 以 alice 身分發送訊息
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d '{
  "app_name": "commerce_agent", "user_id": "alice", "session_id": "s1",
  "new_message": {"role": "user", "parts": [{"text": "I want running shoes"}]}
}'
```

### 測試層級

**第 1 層：單元測試 (Unit Tests)** (test_tools.py)
- 獨立的工具函式
- 資料庫操作
- 錯誤處理

**第 2 層：整合測試 (Integration Tests)** (test_integration.py)
- 代理人設定
- 工具整合
- 資料庫整合
- 匯入路徑

**第 3 層：端到端測試 (End-to-End Tests)** (test_e2e.py)
- 完整的使用者工作流程
- 多用戶情境
- 會話持久性
- 參與度追蹤
- 錯誤復原

### 測試覆蓋率

```bash
make test
# 產生：htmlcov/index.html
open htmlcov/index.html
```

## 📚 關鍵功能

### 1. 會話持久性

```python
from commerce_agent import root_agent
from google.adk.sessions import DatabaseSessionService

session_service = DatabaseSessionService(
    db_url="sqlite:///./sessions.db"
)

# 資料在應用程式重啟後仍然存在
session = await session_service.get_session(
    "commerce_agent", "user123", "session456"
)
```

### 2. 多用戶隔離

```python
# Alice 的會話
alice_prefs = await get_user_preferences("alice")
# 回傳：{"sports": ["running"]}

# Bob 的會話
bob_prefs = await get_user_preferences("bob")
# 回傳：{"sports": ["cycling"]}

# 保證完全隔離
```

### 3. 具備資料庫的自定義工具

```python
from commerce_agent import manage_user_preferences

result = manage_user_preferences(
    action="update",
    user_id="athlete_1",
    data={"sports": ["running", "cycling"]}
)
```

### 4. Grounding Metadata Callback (新增)

從 Google Search 結果中提取來源歸因：

```python
from commerce_agent import root_agent, create_grounding_callback
from google.adk.runners import Runner

runner = Runner(
    agent=root_agent,
    after_model_callbacks=[create_grounding_callback(verbose=True)]
)

async for event in runner.run_async(...):
    if event.is_final_response():
        # 存取提取的來源於 callback_context.state
        # (注意：回調在 after_model階段儲存於狀態中)
        print("Response with grounded sources generated")
```

**優點**：
- ✅ 主控台日誌在開發期間顯示來源歸因
- ✅ 即時監控接地品質
- ✅ 驗證 URL 來自真實的搜尋結果
- ✅ 除錯哪些來源支持哪些聲明

**注意**：對於 `adk web` 使用，回調會自動執行，但輸出會出現在伺服器日誌中，而不是 Web UI。

**文件**：請參閱 `docs/GROUNDING_CALLBACK_GUIDE.md` 獲取完整使用指南。

### 5. 使用 TypedDict 的型別安全 (新增)

所有工具介面現在都使用 TypedDict 以獲得更好的 IDE 支援：

```python
from commerce_agent.types import ToolResult, UserPreferences

def my_tool(param: str, tool_context: ToolContext) -> ToolResult:
    return {
        "status": "success",
        "report": "Operation completed",
        "data": {"result": "value"}
    }
```

**優點**：
- ✅ 完整的 IDE 自動完成
- ✅ 使用 mypy 進行型別檢查
- ✅ 清晰的 API 契約
- ✅ 減少執行時錯誤

### 6. 工具確認流程

對於昂貴的物品 (€100+)，代理人在推薦之前會要求確認。

## 🔧 設定

### 環境變數

從 `.env.example` 建立 `.env`：

```bash
cp .env.example .env
```

編輯 `.env`：

```bash
# 驗證 (擇一)
GOOGLE_API_KEY=your_key

# 資料庫
DATABASE_URL=sqlite:///./commerce_agent_sessions.db

# 日誌
ADK_LOG_LEVEL=INFO
```

### ADK Web 設定

```bash
adk web --port 8000
```

打開 http://localhost:8000

## 🐛 故障排除

| 問題 | 解決方案 |
|-------|----------|
| 下拉選單中沒有代理人 | 在此目錄中執行 `pip install -e .` |
| "database is locked" (資料庫被鎖定) | 確保只有一個程序存取 db |
| 無搜尋結果 | 驗證 `GOOGLE_API_KEY` 已設定且有效 |
| 測試失敗 | 先執行 `make setup` |
| SQLite 錯誤 | 刪除 `commerce_agent_sessions.db` 並重啟 |

##  驗證故障排除

### "site:decathlon.com.hk" 運算子無法運作

**問題：** 搜尋傳回其他零售商 (Amazon, eBay, Adidas) 的結果

**原因：** 使用 Gemini API 而非 Vertex AI

**解決方案：**

```bash
# 1. 檢查已設定哪些憑證
echo $GOOGLE_API_KEY
echo $GOOGLE_APPLICATION_CREDENTIALS

# 2. 如果兩者都已設定，取消設定 API key：
unset GOOGLE_API_KEY

# 3. 重新執行代理人
make dev
```

### 同時設定了 GOOGLE_API_KEY 和 GOOGLE_APPLICATION_CREDENTIALS

**問題：** 代理人使用 Gemini API 而非 Vertex AI，導致搜尋中斷

**警告：** Makefile 會在 `make dev` 期間顯示此警告

**解決方案：**

```bash
# 執行設定腳本以修復憑證
make setup-vertex-ai

# 或者手動取消設定並重新執行
unset GOOGLE_API_KEY
make dev
```

### Vertex AI 憑證未載入

**問題：** 出現 "Could not authenticate with Google Cloud" 之類的錯誤

**解決方案：**

```bash
# 1. 驗證憑證檔案是否存在
ls -la ./credentials/commerce-agent-key.json

# 2. 驗證環境變數
echo $GOOGLE_CLOUD_PROJECT
echo $GOOGLE_APPLICATION_CREDENTIALS

# 3. 使用 gcloud CLI 測試
gcloud auth list

# 4. 如果 gcloud 顯示錯誤的帳戶，切換：
gcloud config set project $GOOGLE_CLOUD_PROJECT
gcloud auth application-default login

# 5. 重新執行設定
make setup-vertex-ai
```

## 📈 部署

### 本地開發

```bash
make dev
# 持久化至本地 SQLite
```

### 生產環境 (Cloud Run)

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa-key.json
adk deploy cloud_run \
  --session-db "sqlite:///./sessions.db" \
  --name commerce-agent
```

### 企業級規模 (Agent Engine)

切換至 Cloud Spanner 進行多區域部署：

```python
session_service = DatabaseSessionService(
    db_url="spanner://projects/MY_PROJECT/instances/MY_INSTANCE/databases/commerce"
)
```

## 📚 參考資料

- [官方 ADK 文件](https://google.github.io/adk-docs/)
- [會話管理](https://google.github.io/adk-docs/sessions/)
- [工具整合](https://google.github.io/adk-docs/tools/)
- [多代理人系統](https://google.github.io/adk-docs/agents/multi-agents/)
- [測試指南](https://google.github.io/adk-docs/get-started/testing/)

---
# 重點摘要

- **核心概念**：
    - **端到端商務代理人 (End-to-End Commerce Agent)**：實作一個完整的商務助理。
    - **會話持久性 (Session Persistence)**：利用 SQLite 和 `DatabaseSessionService` 確保使用者會話在應用程式重啟後仍保留。
    - **多用戶隔離 (Multi-User Isolation)**：確保不同使用者的資料和偏好完全分開。
    - **接地 (Grounding)**：透過提取搜尋來源元數據 (Metadata) 來增強信任和可驗證性。

- **關鍵技術**：
    - **Google ADK v1.17.0**：代理人開發套件。
    - **SQLite**：輕量級關聯式資料庫，用於本地持久化。
    - **Vertex AI / Gemini API**：用於 LLM 推論和 Google Search (Vertex AI 推薦用於完整功能)。
    - **TypedDict**：用於 Python 中的型別安全工具定義。
    - **Mermaid Diagrams**：用於視覺化架構。

- **重要結論**：
    - 使用 `DatabaseSessionService` 是生產環境中管理會話和歷史記錄的最佳實踐。
    - 接地元數據對於建立使用者信任至關重要，可避免幻覺。
    - 正確的測試策略 (單元、整合、E2E) 對於複雜的代理人系統是必要的。
    - 透過 API 測試是驗證多用戶隔離的唯一可靠方法 (因 Web UI 限制)。

- **行動項目**：
    - 執行 `make setup` 和 `make test` 以驗證環境。
    - 閱讀 `docs/TESTING_WITH_USER_IDENTITIES.md` 了解如何測試多用戶情境。
    - 考慮在生產環境中使用 Vertex AI 以獲得最佳搜尋體驗。

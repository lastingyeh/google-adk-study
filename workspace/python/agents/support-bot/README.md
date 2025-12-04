# 課程 33 實作：Slack 機器人與 ADK 整合

這是 ADK Training 專案中課程 33 (Tutorial 33) 的實作版本。它展示了如何使用 Google ADK 建立智慧 Slack 機器人以提供團隊支援。

## 功能 (Features)

- ✅ **知識庫搜尋**：搜尋公司政策與程序
- ✅ **支援工單建立**：建立並追蹤支援工單
- ✅ **ADK Agent**：具有可呼叫工具 (tools) 的 Root agent
- ✅ **Slack Bolt 整合**：處理提及 (mentions)、私訊 (DMs) 和斜線指令 (slash commands) (位於 `bot.py`)
- ✅ **綜合測試**：單元測試、整合測試與結構測試

## Agent 流程圖
流程圖 (search_knowledge_base 邏輯)
```mermaid
graph TD
    Start[開始搜尋] --> Input[輸入查詢 Query]
    Input --> Lowercase[轉換為小寫]
    Lowercase --> Iterate[遍歷知識庫文章]

    Iterate --> CheckTitle{標題匹配?}
    CheckTitle -- Yes --> Score3[分數 +3]
    CheckTitle -- No --> CheckTags{標籤匹配?}

    Score3 --> CheckTags
    CheckTags -- Yes --> Score2[分數 +2]
    CheckTags -- No --> CheckContent{內容匹配?}

    Score2 --> CheckContent
    CheckContent -- Yes --> Score1[分數 +1]
    CheckContent -- No --> CheckScore{分數 > 0?}

    Score1 --> CheckScore
    CheckScore -- Yes --> AddMatch[加入候選列表]
    CheckScore -- No --> NextArticle[下一篇文章]
    AddMatch --> NextArticle

    NextArticle --> HasMore{還有文章?}
    HasMore -- Yes --> Iterate
    HasMore -- No --> SortMatches[依分數排序候選列表]

    SortMatches --> HasMatches{有匹配結果?}
    HasMatches -- Yes --> ReturnBest[回傳最佳匹配文章]
    HasMatches -- No --> ReturnNone[回傳查無結果訊息]
```

## Bot Dev 流程圖

```mermaid
sequenceDiagram
    autonumber
    participant Slack as Slack Platform
    participant Handler as Socket Mode Handler
    participant Router as Event Router
    participant Mention as Mention Handler
    participant MsgHandler as Message Handler
    participant Agent as ADK Agent
    participant Logger as Logger

    Note over Handler: 啟動程式

    Handler->>Slack: 建立 WebSocket 連線 (Connect)

    loop 監聽事件 (Event Loop)
        Slack->>Handler: 推送事件 (Event Received)
        Handler->>Router: 傳送事件進行路由

        alt 事件類型 == app_mention
            Router->>Mention: 呼叫 handle_mention
            activate Mention
            Mention->>Mention: 提取訊息內容
            Mention->>Logger: 記錄日誌 (Log)
            Mention->>Agent: 呼叫 ADK Agent
            activate Agent
            Agent-->>Mention: 回傳處理結果
            deactivate Agent
            Mention->>Slack: 回覆訊息 (Respond)
            deactivate Mention

        else 事件類型 == message
            Router->>MsgHandler: 呼叫 handle_message
            activate MsgHandler

            alt 檢查是否有文字內容 (CheckText)
                MsgHandler->>Logger: 記錄日誌 (LogMsg)
                MsgHandler->>Slack: 回覆 DM (Reply DM)
            else 無文字內容
                Note right of MsgHandler: 忽略不處理
            end
            deactivate MsgHandler

        else 發生錯誤 (Error)
            Handler->>Logger: 記錄錯誤 (LogError)
        end
    end

    Note over Handler: 接收到中斷訊號 (Interrupt / Ctrl+C)
    Handler->>Handler: 關閉連線並停止 (Stop)
```


### 1. 設定環境

```bash
make setup
```

此指令會安裝相依套件並設定套件以供 ADK 探索。

### 2. 設定 Slack App

在 `support_bot/` 目錄下建立 `.env` 檔案：

```bash
cp support_bot/.env.example support_bot/.env
```

新增您的憑證：
```bash
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_APP_TOKEN=xapp-your-token
GOOGLE_API_KEY=your-api-key
```

### 3. 測試 Agent

```bash
make test
```

### 4. 在開發模式下執行

```bash
make dev
```

這將在 http://localhost:8000 啟動 ADK 網頁介面。

### 5. 觀看範例 (Demo)

```bash
make demo
```

## 專案結構

```
support-bot/
├── support_bot/              # Agent 模組
│   ├── __init__.py          # 模組進入點
│   ├── agent.py             # 具有工具的 Root agent
│   └── .env.example         # 環境變數範本
├── tests/                    # 測試套件
│   ├── test_agent.py        # Agent 與工具測試
│   ├── test_imports.py      # Import 測試
│   └── test_structure.py    # 結構測試
├── Makefile                 # 開發指令
├── pyproject.toml          # 套件設定
├── requirements.txt        # Python 相依套件
└── README.md              # 本檔案
```

## 已實作的工具 (Tools Implemented)

### 1. search_knowledge_base(query: str)

搜尋公司知識庫以獲取資訊。

**回傳值 (Returns):**
```python
{
    'status': 'success',
    'report': 'Found article: ...',
    'article': {
        'title': '...',
        'content': '...'
    }
}
```

**範例:**
```python
result = search_knowledge_base("password reset")
# 回傳密碼重設程序
```

### 2. create_support_ticket(subject, description, priority)

為複雜問題建立支援工單。

**回傳值 (Returns):**
```python
{
    'status': 'success',
    'report': 'Support ticket created: TKT-ABC123...',
    'ticket': {
        'id': 'TKT-ABC123',
        'subject': '...',
        'priority': 'normal',
        'created_at': '2025-10-18T...'
    }
}
```

**範例:**
```python
result = create_support_ticket(
    subject="VPN Issue",
    description="Cannot connect to company VPN",
    priority="high"
)
```

## 測試覆蓋率 (Test Coverage)

本實作包含完整的測試：

- **test_imports.py**：測試 agent 和工具是否可被匯入
- **test_structure.py**：測試專案結構與檔案配置
- **test_agent.py**：涵蓋以下內容的 40+ 個測試：
  - Agent 設定
  - 工具功能
  - 知識庫搜尋
  - 工單建立
  - 回傳格式驗證
  - 錯誤處理

執行測試：

```bash
make test              # 執行所有測試
make test-coverage    # 執行並產生覆蓋率報告
```

## 部署至 Slack

### 入門指南

若要將此 agent 部署至 Slack，請遵循以下 8 個步驟：

#### 1. 建立 Slack App

1. 前往 [api.slack.com/apps](https://api.slack.com/apps)
2. 點擊綠色的 **"Create New App"** 按鈕
3. 選擇 **"From scratch"**
4. 填寫詳細資訊：
   - **App Name**: `Support Bot`
   - **Workspace**: 選擇您的工作區
5. 點擊 **"Create App"**

#### 2. 設定 Bot Scopes (OAuth Permissions)

這賦予您的機器人讀取訊息、傳送回覆及存取使用者資訊的權限。

1. 在左側欄，點擊 **"OAuth & Permissions"**
2. 捲動至 **"Bot Token Scopes"**
3. 點擊 **"Add an OAuth Scope"** 並新增以下 scopes：
   - `app_mentions:read` (回應 @提及)
   - `chat:write` (傳送訊息)
   - `channels:history` (讀取頻道訊息)
   - `channels:read` (存取公開頻道)
   - `groups:history` (讀取私人訊息)
   - `groups:read` (存取私人頻道)
   - `im:history` (讀取直接訊息)
   - `im:read` (存取 DMs)
   - `users:read` (查詢使用者資訊)

#### 3. 取得您的 Bot Token

這是您的機器人用來向 Slack 進行驗證的 token。

1. 新增 scopes 後，向上捲動至 **"OAuth Tokens for Your Workspace"**
2. 點擊綠色的 **"Install to Workspace"** 按鈕
3. 檢視權限並點擊 **"Allow"**
4. 您將看到 **"Bot User OAuth Token"** (以 `xoxb-` 開頭)
5. 點擊 **"Copy"** 複製它

**您的 token 應該長得像這樣：**

```bash
xoxb-<workspace-id>-<bot-id>-<secret>
```

⚠️ **重要**：請妥善保管此 token！切勿分享或提交至 git。

#### 4. 啟用 Socket Mode

Socket Mode 讓您的機器人無需公開 webhook 即可接收即時事件。

1. 在左側欄，點擊 **"Socket Mode"**
2. 將開關切換至 **"Enable Socket Mode"**
3. 點擊 **"Generate App-Level Token"**
4. 填寫：
   - **Token Name**: `socket_token`
   - **Scope**: 勾選 `connections:write`
5. 點擊 **"Generate"**
6. 複製 token (以 `xapp-` 開頭)

**您的 token 應該長得像這樣：**

```bash
xapp-1-<app-id>-<token-id>-<secret>
```

#### 5. 訂閱機器人事件 (Subscribe to Bot Events)

1. 在左側欄，點擊 **"Event Subscriptions"**
2. 將 **"Enable Events"** 切換至 ON
3. 捲動至 **"Subscribe to bot events"**
4. 點擊 **"Add Bot User Event"** 並新增以下 4 個事件：
   - `app_mention` (機器人被提及)
   - `message.channels` (公開頻道中的訊息)
   - `message.groups` (私人頻道中的訊息)
   - `message.im` (直接訊息)
5. 點擊 **"Save Changes"**

#### 6. 安裝 App 至您的工作區

1. 在左側欄，點擊 **"Install App"**
2. 點擊 **"Install to Workspace"**
3. 檢視權限
4. 點擊 **"Allow"** 以授權

#### 7. 設定您的環境變數檔案

現在將您的 tokens 新增至專案：

```bash
cd /path/to/tutorial33
cp support_bot/.env.example support_bot/.env
```

編輯 `support_bot/.env` 並新增您的三個 tokens：

```bash
# 從步驟 3：Bot Token (以 xoxb- 開頭)
SLACK_BOT_TOKEN=xoxb-<workspace-id>-<bot-id>-<secret>

# 從步驟 4：App Token (以 xapp- 開頭)
SLACK_APP_TOKEN=xapp-1-<app-id>-<token-id>-<secret>

# 從 https://ai.google.dev (Google Gemini API key)
GOOGLE_API_KEY=AIzaSyD_your_actual_key_here
```

**設定後的檔案結構：**

```
support_bot/
├── __init__.py
├── agent.py          (具有工具的 ADK agent)
├── .env              (← 您的 tokens 放在這裡)
└── .env.example      (範本，請勿修改)
```

#### 8. 執行您的 Slack 機器人

**開發用 (Socket Mode):**

```bash
make slack-dev
```

此指令將會：

- 檢查您的 tokens 是否已設定
- 透過 Socket Mode 連線至 Slack
- 監聽提及 (mentions) 和訊息
- 將任何錯誤列印至終端機

**生產用 (Cloud Run):**

```bash
make slack-deploy
```

此指令將會：

- 建置 Docker 容器
- 部署至 Google Cloud Run
- 將 Socket Mode 轉換為 HTTP webhooks
- 24/7 全天候執行，無需使用您的電腦

#### 9. 在 Slack 中測試您的機器人

1. 前往您的 Slack 工作區
2. 找到 **#general** 頻道 (或任何頻道)
3. 輸入提及您的機器人的訊息：

```text
@Support Bot What is the password reset procedure?
```

**嘗試這些測試指令：**

```bash
@Support Bot 幫助
@Support Bot 休假政策是什麼？
@Support Bot 為「我的筆電很慢」建立一個工單
@Support Bot 顯示遠端工作政策
```

**預期結果：**

```bash
使用者：@Support Bot 密碼重設的流程是什麼？

支援機器人：
找到相關文章：密碼重設
流程：
1. 前往 account.company.com
2. 點擊「忘記密碼」
3. 依照電子郵件中的連結操作
4. 建立新密碼
```

### 整合流程 (Integration Flow)

```mermaid
sequenceDiagram
    participant User as 使用者
    participant Slack as Slack 平台
    participant Bolt as Bolt App (後端)
    participant Agent as ADK Agent
    participant Tools as 工具 (知識庫/工單)

    User->>Slack: 傳送訊息 (@Bot 詢問)
    Slack->>Bolt: 透過 Webhook/Socket Mode 轉發事件
    activate Bolt

    Bolt->>Agent: 呼叫 Agent 處理請求
    activate Agent

    Agent->>Tools: 根據意圖選擇並呼叫工具 (例如: search_kb)
    activate Tools
    Tools-->>Agent: 回傳工具執行結果
    deactivate Tools

    Agent-->>Bolt: 生成並回傳最終回覆
    deactivate Agent

    Bolt->>Slack: 將回覆傳送至 Slack API
    deactivate Bolt

    Slack-->>User: 在頻道中顯示機器人回覆
```

### 可用指令

```bash
make slack-dev         # 以 Socket Mode 執行機器人 (開發模式)
make slack-deploy      # 部署至 Cloud Run (生產環境)
make slack-test        # 測試 Slack 整合
```

詳情請參閱 Makefile。

### 生產環境部署

部署至 Google Cloud Run：

```bash
make slack-deploy
```

此指令將會：

- 建置 Docker 映像檔
- 部署至 Cloud Run
- 在 Slack 設定 HTTP webhook
- 為 Cloud Run 設定 `PORT=8080`

詳細生產環境部署 (Cloud Run)

請遵循以下步驟將 Slack 機器人部署至 Google Cloud Run。這是一個明確、可重複的流程，您可以從工作站執行。

1. 先決條件

- 安裝並驗證 Google Cloud CLI (gcloud)：

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

- 啟用所需的 APIs：

```bash
gcloud services enable run.googleapis.com iam.googleapis.com artifactregistry.googleapis.com
```

- 安裝 Docker 並確保您可以建置和推送映像檔。

2. 建置容器映像檔

將 `[REGION]`, `[PROJECT]` 和 `[REPOSITORY]` 替換為您的數值。使用 Artifact Registry 或 Container Registry。使用預設 GCR 命名的範例：

```bash
IMAGE=gcr.io/[PROJECT]/support-bot:latest
docker build -t "$IMAGE" .
```

3. 推送映像檔

```bash
docker push "$IMAGE"
```

如果您使用具有自訂 repository 的 Artifact Registry，請相應地標記並推送：

```bash
IMAGE=[REGION]-docker.pkg.dev/[PROJECT]/[REPOSITORY]/support-bot:latest
docker build -t "$IMAGE" .
docker push "$IMAGE"
```

4. 部署至 Cloud Run (managed)

這會將容器部署為一項服務。請適當地替換 `[REGION]`。

```bash
gcloud run deploy support-bot \
    --image "$IMAGE" \
    --region [REGION] \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars ENVIRONMENT=production,PORT=8080
```

注意：
- 對於 secrets (Slack tokens, API keys)，建議使用 Secret Manager 並透過 `--set-secrets` 參照它們，或在部署後於 Cloud Run 服務中設定。
- 如果您想透過 IAP 或負載平衡器限制存取，請使用 `--no-allow-unauthenticated`。

5. 設定 Slack (HTTP webhook)

部署後，您將獲得一個服務 URL，例如 `https://support-bot-xxxxx-uc.a.run.app`。

1. 在 Slack App 設定 → Event Subscriptions 或 Interactivity 中，將 Request URL 設定為：

```text
https://[CLOUD_RUN_URL]/slack/events
```

2. 驗證 Slack 可以存取該 URL (Cloud Run 必須允許未經身分驗證的請求，或者您必須透過簽名標頭設定驗證)。

6. 使用 Secret Manager (建議)

安全地儲存 secrets，避免盡可能將 tokens 直接注入環境變數中。建立 secret 的範例 (單行指令)：

```bash
echo -n "$SLACK_BOT_TOKEN" | gcloud secrets create SLACK_BOT_TOKEN --data-file=-
```

如果需要，新增 secret 版本：

```bash
echo -n "$SLACK_BOT_TOKEN" | gcloud secrets versions add SLACK_BOT_TOKEN --data-file=-
```

然後透過 `--set-secrets` 將 secret 綁定到 Cloud Run 服務，或在 Cloud Console 中進行設定。

7. 健康檢查與日誌

- 新增一個 `/health` 端點，回傳 200 以進行就緒檢查 (Cloud Run 健康探測依賴流量；擁有一個簡單的端點對負載平衡器很有用)。
- 使用 Cloud Logging 並為事件和錯誤設定結構化日誌。

8. 復原 (Rollback)

- 使用 `gcloud run services update --image` 復原到先前的標籤，或重新部署舊的映像檔標籤。

9. 選用：網域對應與 HTTPS

- 透過 `gcloud beta run domain-mappings create --service support-bot --domain your.domain.com` 對應自訂網域，並相應更新 Slack request URLs。

10. 完整流程範例 (dry-run，建議手動確認)：

```bash
# build
docker build -t "$IMAGE" .
# push
docker push "$IMAGE"
# deploy
gcloud run deploy support-bot --image "$IMAGE" --region us-central1 --platform managed --allow-unauthenticated --set-env-vars ENVIRONMENT=production,PORT=8080
```

### 快速疑難排解

| 問題 | 解決方案 |
|-------|----------|
| 機器人無回應 | 檢查 Socket Mode 是否啟用，驗證 `.env` 中的 tokens |
| "Socket connection failed" | 確保 `SLACK_APP_TOKEN` 以 `xapp-` 開頭 |
| 工具無法執行 | 驗證 `GOOGLE_API_KEY` 已設定，執行 `make test` |
| 模組匯入錯誤 | 執行 `pip install -e .` |

## 知識庫 (Knowledge Base)

Agent 可以存取這些文章：

- 🔐 Password Reset (密碼重設)
- 💰 Expense Reports (費用報告)
- 🏖️ Vacation & PTO Policy (休假與特休政策)
- 🏠 Remote Work Policy (遠端工作政策)
- 🛠️ IT Support Contacts (IT 支援聯絡人)

試著向 agent 詢問有關這些主題的問題！

## 學習成果 (Learning Outcomes)

完成此實作後，您將了解：

- ✅ 如何建立具有工具的 ADK agents
- ✅ 如何建構工具以回傳適當格式
- ✅ 如何實作知識庫搜尋
- ✅ 如何使用 Slack Bolt 與 Slack 整合
- ✅ 如何全面地測試 agents
- ✅ 如何將 agents 部署至 Cloud Run

## 下一步

1. **擴充知識庫**：在 `agent.py` 的 KNOWLEDGE_BASE 中新增更多文章
2. **新增更多工具**：實作額外的工具以進行工單管理、使用者查詢
3. **Slack 整合**：新增 bot.py 檔案以處理 Slack 事件
4. **生產環境部署**：使用 HTTP 模式部署至 Cloud Run
5. **進階功能**：新增豐富的 Slack blocks、互動式按鈕、排程訊息

## 疑難排解 (Troubleshooting)

### 問題：Imports 失敗

```bash
# 確保套件已以開發模式安裝
pip install -e .
```

### 問題：測試失敗

```bash
# 安裝測試相依套件
pip install pytest pytest-cov
make test
```

### 問題：ADK web 找不到 agent

```bash
# Agent 必須安裝為套件
pip install -e .
adk web  # 不是 'adk web support_bot'
```

## 資源

- 📚 [ADK 文件](https://google.github.io/adk-docs/)
- 💬 [Slack Bolt 文件](https://docs.slack.dev/tools/bolt-python/)
- 🤖 [Gemini API](https://ai.google.dev/gemini-api/docs)


**最後更新**：2025 年 10 月 18 日

**測試環境**：

- google-adk >= 1.16.0
- slack-bolt >= 1.26.0
- google-genai >= 1.45.0
- Python 3.9+

## 重點摘要

- **核心概念**：整合 Slack Bot 與 Google ADK 的完整教學。
- **關鍵技術**：Google ADK (Agent Development Kit), Slack Bolt SDK, Google Cloud Run.
- **重要結論**：本專案展示了從開發、測試到部署一整套建立企業級 AI 支援機器人的流程。
- **行動項目**：請依照「快速開始」步驟設定環境，並嘗試在 Slack 中與機器人互動。

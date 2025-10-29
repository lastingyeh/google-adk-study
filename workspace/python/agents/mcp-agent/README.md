# 教學 16：MCP 整合

**學習模型上下文協定 (MCP) 與 Google ADK 的整合以實現標準化工具存取。**

## 概述

本實作示範如何：
- 使用 `MCPToolset` 將代理連接到 MCP 伺服器
- **實作人在迴路 (HITL) 批准工作流程** ✨ 新功能
- **限制檔案系統存取至安全目錄** 🔒 安全性
- 使用 stdio、SSE 和 HTTP 連接類型
- 透過 MCP 實作檔案系統操作
- 建構文件組織系統
- 處理 OAuth2 認證以進行生產部署

## 🔒 安全功能

- **目錄範圍限制**：MCP 伺服器僅限於 `sample_files/` 目錄
- **人在迴路**：破壞性操作需要使用者批准
- **操作記錄**：所有檔案操作都會記錄以供稽核
- **工具前回呼**：執行前的驗證和授權

## 快速開始

### 先決條件

- Python 3.10+
- Node.js 和 npx（用於 MCP 伺服器）
- Google API 金鑰

### 安裝

```bash
# 1. 安裝相依套件
make setup

# 2. 設定環境
cp mcp_agent/.env.example mcp_agent/.env
# 編輯 mcp_agent/.env 並加入您的 GOOGLE_API_KEY

# 3. 啟動開發伺服器
make dev

# 4. 在瀏覽器中開啟 http://localhost:8000
```

### 驗證安裝

```bash
# 檢查 Node.js 是否已安裝
make check-node

# 執行測試
make test
```

### 快速示範

```bash
# 查看代理能做什麼
make about

# 建立範例檔案供實驗
make create-sample-files

# 啟動代理並嘗試組織檔案
make dev
# 然後詢問："按檔案類型組織 sample_files/mixed_content 資料夾"

# 查看範例提示
make demo

# 完成時清理範例檔案
make clean-samples
```

## 專案結構

```
tutorial16/
├── mcp_agent/              # 代理實作
│   ├── __init__.py         # 套件匯出
│   ├── agent.py            # 具有 MCP 檔案系統的根代理
│   ├── document_organizer.py  # 文件組織範例
│   └── .env.example        # 環境模板
├── tests/                  # 測試套件
│   ├── test_agent.py       # 代理設定測試
│   ├── test_imports.py     # 匯入驗證
│   └── test_structure.py   # 專案結構測試
├── Makefile                # 開發指令
├── requirements.txt        # 相依套件
├── pyproject.toml          # 套件設定
└── README.md               # 本檔案
```

## 功能

### 1. 人在迴路 (HITL) 工作流程

**什麼是人在迴路？**

HITL 是一種安全模式，代理在執行敏感操作前會請求人類批准。這可防止意外的資料遺失，並讓使用者控制破壞性動作。

**在此代理中的實作：**

```python
# 破壞性操作需要批准
DESTRUCTIVE_OPERATIONS = {
  'write_file': '寫入檔案會修改內容',
  'write_text_file': '寫入檔案會修改內容',
  'move_file': '移動檔案會改變檔案位置',
  'create_directory': '建立目錄會修改檔案系統結構',
}

# 讀取操作會自動允許
SAFE_OPERATIONS = [
  'read_file',
  'list_directory',
  'search_files',
  'get_file_info'
]
```

**運作方式：**

1. **工具前回呼**：在執行前攔截每個工具呼叫
2. **操作分類**：檢查操作是否為破壞性
3. **批准請求**：暫停執行並請求使用者確認
4. **記錄**：記錄所有操作以供稽核追蹤

**親自試試：**

```bash
# 啟動代理
make dev

# 嘗試安全操作（立即執行）
"列出 sample_files 中的所有檔案"

# 嘗試破壞性操作（需要批准）
"建立一個名為 test.txt 的新檔案，內容為：Hello World"
# 代理回應："⚠️ 需要批准 - 此操作因安全考量已被阻擋"

# 若要批准操作，在 ADK 狀態中設定批准旗標
# state['user:auto_approve_file_ops'] = True
```

**ADK 最佳實務：**

使用 `before_tool_callback` 用於：
- ✅ 輸入驗證和清理
- ✅ 授權檢查和權限
- ✅ 速率限制和配額管理
- ✅ 合規稽核記錄
- ✅ 敏感操作的人工批准

### 2. 限制檔案系統存取

**安全設計：**

代理**僅限於 `sample_files/` 目錄**。這可防止：
- ❌ 存取系統檔案
- ❌ 修改重要專案檔案
- ❌ 讀取敏感設定
- ❌ 刪除關鍵資料

**實作：**

```python
# MCP 伺服器限定於特定目錄
server_params = StdioServerParameters(
  command='npx',
  args=[
    '-y',
    '@modelcontextprotocol/server-filesystem',
    '/path/to/sample_files'  # 僅此目錄可存取
  ]
)
```

**為什麼這很重要：**

在生產環境中，您可以：
- 讓代理存取特定客戶資料資料夾
- 防止跨客戶資料洩漏
- 實作每個使用者的目錄隔離
- 稽核範圍內的所有檔案操作

### 3. MCP 檔案系統代理

核心代理透過 MCP 提供檔案系統存取：

```python
from mcp_agent import root_agent
from google.adk.agents import Runner

runner = Runner()
result = runner.run(
  "列出目前目錄中的所有檔案",
  agent=root_agent
)
```

**可用操作：**
- `read_file` - 讀取檔案內容
- `write_file` - 建立/更新檔案
- `list_directory` - 列出目錄內容
- `create_directory` - 建立資料夾
- `move_file` - 移動/重新命名檔案
- `search_files` - 按模式搜尋
- `get_file_info` - 取得檔案中繼資料

### 2. 文件組織器

自動化文件組織系統：

```python
from mcp_agent.document_organizer import DocumentOrganizer
import asyncio

async def main():
  organizer = DocumentOrganizer('/path/to/documents')
  await organizer.organize()
  await organizer.search_documents('預算報告')
  await organizer.summarize_directory()

asyncio.run(main())
```

### 3. 連接類型 (ADK 1.16.0+)

**Stdio 連接**（本地）：
```python
from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams

mcp_tools = MCPToolset(
  connection_params=StdioConnectionParams(
    command='npx',
    args=['-y', '@modelcontextprotocol/server-filesystem', '/path']
  )
)
```

**SSE 連接**（遠端）：
```python
from google.adk.tools.mcp_tool import SseConnectionParams

mcp_tools = MCPToolset(
  connection_params=SseConnectionParams(
    url='https://api.example.com/mcp/sse',
    timeout=30.0,
    sse_read_timeout=300.0
  )
)
```

**HTTP 串流**（遠端）：
```python
from google.adk.tools.mcp_tool import StreamableHTTPConnectionParams

mcp_tools = MCPToolset(
  connection_params=StreamableHTTPConnectionParams(
    url='https://api.example.com/mcp/stream',
    timeout=30.0
  )
)
```

### 4. OAuth2 認證

安全的 MCP 伺服器存取：

```python
from google.adk.auth.auth_credential import (
  AuthCredential, AuthCredentialTypes, OAuth2Auth
)

oauth2_credential = AuthCredential(
  auth_type=AuthCredentialTypes.OAUTH2,
  oauth2=OAuth2Auth(
    client_id='your-client-id',
    client_secret='your-client-secret',
    auth_uri='https://auth.example.com/authorize',
    token_uri='https://auth.example.com/token',
    scopes=['read', 'write']
  )
)

mcp_tools = MCPToolset(
  connection_params=SseConnectionParams(url='...'),
  auth_credential=oauth2_credential
)
```

## 示範提示

### 使用範例檔案

建立具有多種檔案類型的遊樂場來測試代理：

```bash
# 建立測試用範例檔案
make create-sample-files

# 這會建立：
#   - 文字文件 (document1.txt, notes.txt, meeting_notes.txt)
#   - 程式碼檔案 (script.py, app.js, main.go)
#   - 設定檔案 (package.json, config.toml, settings.yaml)
#   - 文件 (README.md, TODO.md)
#   - 資料檔案 (data.csv, users.json)
#   - mixed_content/ 中的混合未排序檔案

# 現在啟動代理
make dev

# 完成時清理
make clean-samples
```

在 ADK UI (<http://localhost:8000>) 中嘗試這些：

### 基本操作

1. **列出檔案：**

   ```text
   列出 sample_files 目錄中的所有檔案
   ```

2. **讀取檔案：**

   ```text
   讀取 sample_files/README.md 的內容
   ```

3. **建立檔案：**

   ```text
   建立一個名為 test.txt 的新檔案，內容為：Hello MCP!
   ```

4. **搜尋檔案：**

   ```text
   在 sample_files 中找到所有 Python 檔案
   ```

5. **檔案資訊：**

   ```text
   requirements.txt 的大小和最後修改日期是什麼？
   ```

### 進階操作

1. **目錄組織：**

   ```text
   按檔案類型組織 sample_files/mixed_content 資料夾
   ```

2. **檔案分析：**

   ```text
   分析 sample_files 中的所有程式碼檔案並列出其主要函數
   ```

3. **批次操作：**

   ```text
   建立名為 'code'、'docs' 和 'config' 的資料夾，然後相應地移動檔案
   ```

4. **內容摘要：**

   ```text
   讀取 sample_files 中的所有 markdown 檔案並建立合併摘要
   ```

8. **批次操作：**
   ```
   找到所有圖片檔案並將它們移動到 Images 資料夾
   ```

## 測試

執行完整的測試套件：

```bash
# 所有測試
make test

# 特定測試檔案
pytest tests/test_agent.py -v

# 包含覆蓋率
pytest tests/ --cov=mcp_agent --cov-report=html
```

**測試覆蓋率：**
- 代理設定和建立
- MCP 工具集初始化
- 連接參數驗證
- 匯入驗證
- 專案結構驗證
- ADK 1.16.0+ 功能相容性

## 環境設定

`.env.example` 檔案包含所有可用選項：

```bash
# 必要
GOOGLE_API_KEY=your_api_key_here

# 選用：Vertex AI
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# 選用：MCP 設定
MCP_BASE_DIRECTORY=/path/to/your/directory

# 選用：OAuth2
OAUTH_CLIENT_ID=your-client-id
OAUTH_CLIENT_SECRET=your-client-secret
OAUTH_TOKEN_URL=https://auth.example.com/token

# 選用：SSE/HTTP
MCP_SSE_URL=https://api.example.com/sse
MCP_HTTP_URL=https://api.example.com/stream
```

## 常見問題

### "找不到 npx 指令"

**問題：** 未安裝 Node.js

**解決方案：**
```bash
# macOS
brew install node

# Ubuntu
sudo apt install nodejs npm

# 驗證
npx --version
```

### "MCP 伺服器連接失敗"

**問題：** 伺服器未啟動或路徑錯誤

**解決方案：**
1. 手動測試伺服器：
   ```bash
   npx -y @modelcontextprotocol/server-filesystem /path/to/dir
   ```

2. 驗證目錄存在：
   ```python
   import os
   print(os.path.exists('/path/to/dir'))
   ```

3. 檢查錯誤記錄

### "匯入錯誤"

**問題：** 缺少相依套件

**解決方案：**
```bash
pip install -r requirements.txt
pip install -e .
```

## 關鍵學習

### MCP 優點

- ✅ 工具整合的標準化協定
- ✅ 100+ 伺服器的社群生態系統
- ✅ 多種連接類型（stdio、SSE、HTTP）
- ✅ 安全認證支援
- ✅ 生產就緒模式

### 最佳實務

- ✅ 在 MCP 連接前驗證目錄路徑
- ✅ 在生產部署中使用 OAuth2
- ✅ 為代理提供明確指示
- ✅ 優雅地處理連接錯誤
- ✅ 使用實際 MCP 伺服器進行測試
- ✅ 監控 MCP 伺服器健康狀況

### 生產檢查清單

- [ ] 已安裝 Node.js/npx
- [ ] 目錄路徑已驗證
- [ ] 認證已設定
- [ ] 憑證安全儲存
- [ ] 錯誤處理已實作
- [ ] 測試通過
- [ ] 監控已就位

## 資源

- **教學文件：** [docs/tutorial/16_mcp_integration.md](../../docs/tutorial/16_mcp_integration.md)
- **MCP 規範：** https://spec.modelcontextprotocol.io/
- **官方 MCP 伺服器：** https://github.com/modelcontextprotocol/servers
- **ADK 文件：** https://google.github.io/adk-docs/

## 下一步

掌握 MCP 整合後：

1. **教學 17：** 代理對代理 (A2A) 溝通
2. **教學 18：** 事件與可觀測性
3. **教學 19：** 產物與檔案管理

## 授權

ADK 訓練存儲庫的一部分 - 教育用途。

---

**需要協助？** 查看教學文件或在存儲庫中開啟問題。
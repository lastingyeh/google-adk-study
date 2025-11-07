# 教學 16: 模型內容協議 (MCP) 整合 - 標準化工具協議

**目標**: 使用模型內容協議 (MCP) 將外部工具和服務整合到您的代理程式中，利用社群建構的工具伺服器擴展代理程式的功能。

---

## 🚀 快速入門

開始的最簡單方法是使用我們的**工作實作**:

```bash
cd tutorial_implementation/tutorial16
make setup
make dev
```

然後在瀏覽器中開啟 `http://localhost:8000` 並嘗試 MCP 檔案系統代理程式！

**先決條件**:

- 教學 01 (Hello World 代理程式)
- 教學 02 (函式工具)
- 已安裝 Node.js (用於 MCP 伺服器)
- 對協議和 API 有基本了解
- **ADK 版本**: 建議 1.15.0+ (支援 `tool_name_prefix`, OAuth2 功能)

**您將學到**:

- 了解模型內容協議 (MCP)
- 使用 `MCPToolset` 連接到 MCP 伺服器
- 設定基於 stdio 的 MCP 連線
- 建構具有檔案系統存取權限的代理程式
- 建立自訂 MCP 伺服器整合
- 會話池和資源管理
- 生產環境中 MCP 部署的最佳實踐

**完成時間**: 50-65 分鐘

---

### ADK 1.16.0+ 回呼簽章變更

**重要更新**: ADK 1.16.0 更改了 `before_tool_callback` 的簽章。

- **舊版 (< 1.16.0)**: `callback_context, tool_name, args`
- **新版 (1.16.0+)**: `tool, args, tool_context`

詳情請參閱 **第 7 節: 使用 MCP 的人機迴圈 (HITL)**。

---

## 為何 MCP 很重要

**問題**: 為每個外部服務建構自訂工具既耗時又重複。

**解決方案**: **模型內容協議 (MCP)** 是一個開放標準，用於將 AI 代理程式連接到外部工具和資料來源。您可以使用社群**預先建構的 MCP 伺服器**，而無需編寫自訂整合。

**優點**:

- 🔌 **隨插即用**: 立即連接到現有的 MCP 伺服器。
- 🌐 **社群生態系統**: 利用社群建構的工具。
- [TOOLS] **標準化介面**: 所有工具都有一致的 API。
- 📦 **豐富功能**: 檔案系統、資料庫、API 等。
- [FLOW] **可重複使用**: 同一個伺服器可與多個代理程式配合使用。
- 🚀 **可擴展**: 需要時可建構自訂伺服器。

**MCP 生態系統**:

- 官方 MCP 伺服器: 檔案系統、GitHub、Slack、資料庫等。
- 社群伺服器: 超過 100 個可用伺服器，涵蓋資料庫、API、開發工具和專業服務。
- 自訂伺服器: 為您的專有系統建構自己的伺服器。

---

## 1. MCP 基礎

### 什麼是模型內容協議？

**MCP** 定義了 AI 模型發現和使用外部工具的標準方式。一個 **MCP 伺服器** 會公開：

- **工具**: 代理程式可以呼叫的函式。
- **資源**: 代理程式可以存取的資料。
- **提示**: 預定義的指令範本。

**架構**:

```
代理程式 (ADK)
  ↓
MCPToolset (ADK 封裝)
  ↓
MCP 客戶端
  ↓
MCP 伺服器 (stdio/HTTP)
  ↓
外部服務 (檔案系統、API、資料庫等)
```

**原始碼**: `google/adk/tools/mcp_tool/mcp_tool.py`, `mcp_toolset.py`

### MCP 連線類型

- **Stdio** (標準輸入/輸出):

  ```python
  from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams
  # 透過 stdio 連線 (最常見)
  mcp_tools = MCPToolset(
      connection_params=StdioConnectionParams(
          command='npx',  # Node 套件執行器
          args=['-y', '@modelcontextprotocol/server-filesystem', '/path/to/directory']
      )
  )
  ```

- **HTTP** (即將推出):

  ```python
  # 未來: 基於 HTTP 的連線
  # mcp_tools = MCPToolset(
  #     connection_params=HttpConnectionParams(
  #         url='http://localhost:3000'
  #     )
  # )
  ```

- **SSE (伺服器發送事件)** - ✅ **ADK 1.16.0+ 支援**

  ```python
  from google.adk.tools.mcp_tool import MCPToolset, SseConnectionParams
  # 透過伺服器發送事件 (SSE) 連線
  mcp_tools = MCPToolset(
      connection_params=SseConnectionParams(
          url='https://api.example.com/mcp/sse',
          headers={'Authorization': 'Bearer your-token'},  # 可選標頭
          timeout=30.0,  # 連線逾時
          sse_read_timeout=300.0  # SSE 讀取逾時
      )
  )
  ```

- **可串流 HTTP** - ✅ **ADK 1.16.0+ 支援**
  ```python
  from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
  # 透過可串流 HTTP 連線
  mcp_tools = MCPToolset(
      connection_params=StreamableHTTPConnectionParams(
          url='https://api.example.com/mcp/stream',
          headers={'Authorization': 'Bearer your-token'},  # 可選標頭
          timeout=30.0,  # 連線逾時
          sse_read_timeout=300.0  # 讀取逾時
      )
  )
  ```

---

## 2. 使用 MCP 檔案系統伺服器

最常見的 MCP 伺服器是**檔案系統伺服器**，它為代理程式提供受控的檔案存取權限。

### 基本設定

```python
from google.adk.agents import Agent, Runner
from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams

# 建立用於檔案系統存取的 MCP 工具集
mcp_tools = MCPToolset(
    connection_params=StdioConnectionParams(
        command='npx',
        args=[
            '-y',  # 需要時自動安裝
            '@modelcontextprotocol/server-filesystem',
            '/Users/username/documents'  # 要存取的目錄
        ]
    )
)

# 建立具有 MCP 工具的代理程式
agent = Agent(
    model='gemini-2.0-flash',
    name='file_assistant',
    instruction='您可以在 documents 目錄中讀取和寫入檔案。',
    tools=[mcp_tools]
)

runner = Runner()
result = runner.run(
    "列出目錄中的所有文字檔案",
    agent=agent
)
print(result.content.parts[0].text)
```

### 可用的檔案系統操作

檔案系統 MCP 伺服器提供以下工具：

- `read_file`: 讀取檔案內容
- `write_file`: 寫入檔案
- `list_directory`: 列出目錄內容
- `create_directory`: 建立新目錄
- `move_file`: 移動或重新命名檔案
- `search_files`: 搜尋檔案
- `get_file_info`: 取得檔案元數據

---

## 3. 真實世界範例：文件整理器

讓我們建構一個使用 MCP 檔案系統存取權限來整理文件的代理程式。

### 完整實作

```python
"""使用 MCP 檔案系統伺服器的文件整理器
自動按類型、日期和內容整理文件。"""
import asyncio
import os
from google.adk.agents import Agent, Runner, Session
from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams
from google.genai import types

# 環境設定
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = '1'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-project-id'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'

class DocumentOrganizer:
    """使用 MCP 的智慧文件整理器。"""
    def __init__(self, base_directory: str):
        self.base_directory = base_directory
        self.mcp_tools = MCPToolset(
            connection_params=StdioConnectionParams(
                command='npx',
                args=[
                    '-y',
                    '@modelcontextprotocol/server-filesystem',
                    base_directory
                ]
            ),
            retry_on_closed_resource=True
        )
        self.agent = Agent(
            model='gemini-2.0-flash',
            name='document_organizer',
            description='智慧文件整理代理程式',
            instruction="""
            您是一位具有檔案系統存取權限的文件整理專家。
            您的職責：
            1. 依名稱、類型和內容分析檔案
            2. 建立邏輯資料夾結構
            3. 將檔案移動到適當位置
            4. 重新命名檔案以求清晰
            5. 產生整理報告
            指南：
            - 按類別建立資料夾（例如，文件、圖片、程式碼、封存）
            - 在需要時使用子類別（例如，文件/2024/，文件/工作/）
            - 除非不清楚，否則保留原始檔名
            - 絕不刪除檔案
            - 報告所有變更
            您有權存取檔案系統工具：
            - read_file, write_file, list_directory, create_directory, move_file, search_files, get_file_info
            """.strip(),
            tools=[self.mcp_tools],
            generate_content_config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=2048
            )
        )
        self.runner = Runner()
        self.session = Session()

    async def organize(self):
        """
        整理基本目錄中的文件。
        """
        print(f"{'='*70}\nORGANIZING: {self.base_directory}\n{'='*70}\n")
        result = await self.runner.run_async(
            """
            整理目錄中的所有檔案：
            1. 列出所有檔案並分析其類型
            2. 建立適當的資料夾結構
            3. 將檔案移動到其邏輯位置
            4. 產生變更摘要報告
            從列出目錄內容開始。
            """.strip(),
            agent=self.agent,
            session=self.session
        )
        print("\n📊 整理報告:\n")
        print(result.content.parts[0].text)
        print(f"\n{'='*70}\n")

    async def search_documents(self, query: str):
        """
        依內容搜尋文件。
        """
        print(f"\n🔍 正在搜尋: {query}\n")
        result = await self.runner.run_async(
            f"搜尋所有檔案中與以下內容相關的內容: {query}",
            agent=self.agent,
            session=self.session
        )
        print("結果:\n")
        print(result.content.parts[0].text)
        print()

    async def summarize_directory(self):
        """
        產生目錄摘要。
        """
        print("\n📁 目錄摘要:\n")
        result = await self.runner.run_async(
            """
            產生全面的目錄摘要：
            1. 檔案總數
            2. 按類型分類的檔案（文件、圖片、程式碼等）
            3. 總大小
            4. 最大的檔案
            5. 進一步整理的建議
            """.strip(),
            agent=self.agent,
            session=self.session
        )
        print(result.content.parts[0].text)
        print()

async def main():
    """
    主進入點。
    """
    base_dir = '/Users/username/Documents/ToOrganize'
    organizer = DocumentOrganizer(base_dir)
    await organizer.organize()
    await organizer.search_documents('預算報告')
    await organizer.summarize_directory()

if __name__ == '__main__':
    asyncio.run(main())
```

---

## 4. 進階 MCP 功能

### 會話池

MCPToolset 維護一個連線池以提高效率：

```python
from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams
mcp_tools = MCPToolset(
    connection_params=StdioConnectionParams(
        command='npx',
        args=['-y', '@modelcontextprotocol/server-filesystem', '/path']
    ),
    retry_on_closed_resource=True,  # 連線中斷時自動重試
)
# 池自動管理：
# - 連線重複使用
# - 資源清理
# - 錯誤復原
```

### 多個 MCP 伺服器

同時使用多個 MCP 伺服器：

```python
from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams

# 檔案系統伺服器
filesystem_tools = MCPToolset(
    connection_params=StdioConnectionParams(
        command='npx',
        args=['-y', '@modelcontextprotocol/server-filesystem', '/documents']
    ),
    tool_name_prefix='fs_'  # ADK 1.15.0+: 避免名稱衝突
)

# GitHub 伺服器 (假設)
github_tools = MCPToolset(
    connection_params=StdioConnectionParams(
        command='npx',
        args=['-y', '@modelcontextprotocol/server-github', '--token', 'YOUR_TOKEN']
    ),
    tool_name_prefix='gh_'  # ADK 1.15.0+: 避免名稱衝突
)

# 具有多個 MCP 工具集的代理程式
agent = Agent(
    model='gemini-2.0-flash',
    name='multi_tool_agent',
    instruction='您可以存取檔案系統 (fs_*) 和 GitHub (gh_*) 操作。',
    tools=[filesystem_tools, github_tools]
)
```

---

## 5. MCP 限制

### ❌ 不支援取樣 (ADK 1.16.0)

**重要限制**: Google ADK 的 MCP 實作在 1.16.0 版本中**不支援取樣**。

#### 什麼是 MCP 取樣？

MCP 取樣允許伺服器向客戶端請求 LLM 完成/生成：

```json
// 伺服器可以請求 LLM 生成 (ADK 不支援):
{
  "method": "sampling/createMessage",
  "params": {
    "messages": [{ "role": "user", "content": "總結此資料" }],
    "modelPreferences": { "hints": [{ "name": "gemini-2.0-flash" }] },
    "maxTokens": 100
  }
}
```

#### 因應措施

- **對於 MCP 伺服器**: 實作自己的 LLM 整合（直接呼叫 Gemini API）。
- **對於 ADK 應用程式**: 使用 ADK 的原生 LLM 功能，而不是 MCP 取樣。

---

## 6. 建構自訂 MCP 伺服器

### 簡單的 MCP 伺服器 (Node.js)

```javascript
// custom-mcp-server.js
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

const server = new Server(
  { name: 'custom-calculator-server', version: '1.0.0' },
  { capabilities: { tools: {} } }
);

server.setRequestHandler('tools/list', async () => {
  return {
    tools: [
      {
        name: 'calculate',
        description: '執行數學計算',
        inputSchema: {
          type: 'object',
          properties: {
            expression: { type: 'string', description: '要評估的數學表達式' },
          },
          required: ['expression'],
        },
      },
    ],
  };
});

server.setRequestHandler('tools/call', async (request) => {
  if (request.params.name === 'calculate') {
    const expression = request.params.arguments.expression;
    try {
      const result = eval(expression); // 在生產環境中，請使用安全的數學解析器
      return { content: [{ type: 'text', text: `結果: ${result}` }] };
    } catch (error) {
      return {
        content: [{ type: 'text', text: `錯誤: ${error.message}` }],
        isError: true,
      };
    }
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

---

## 7. 使用 MCP 的人機迴圈 (HITL)

**ADK 1.16.0+ 回呼簽章**: 為破壞性操作實作審批工作流程。

### 完整 HITL 實作

```python
"""具有人機迴圈審批工作流程的 MCP 代理程式
展示 ADK 1.16.0 回呼簽章。"""
import os
import logging
from typing import Dict, Any, Optional
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def before_tool_callback(
    tool,  # BaseTool 物件
    args: Dict[str, Any],
    tool_context  # 具有 .state 屬性
) -> Optional[Dict[str, Any]]:
    """MCP 檔案系統操作的人機迴圈回呼。"""
    tool_name = tool.name if hasattr(tool, 'name') else str(tool)
    logger.info(f"[工具請求] {tool_name}，參數: {args}")

    DESTRUCTIVE_OPERATIONS = {
        'write_file': '寫入檔案會修改內容',
        'move_file': '移動檔案會改變檔案位置',
        'create_directory': '建立目錄會修改檔案系統結構',
    }

    if tool_name in DESTRUCTIVE_OPERATIONS:
        reason = DESTRUCTIVE_OPERATIONS[tool_name]
        logger.warning(f"[需要審批] {tool_name}: {reason}")
        auto_approve = tool_context.state.get('user:auto_approve_file_ops', False)
        if not auto_approve:
            return {
                'status': 'requires_approval',
                'message': f"⚠️ 需要審批\n\n操作: {tool_name}\n原因: {reason}\n參數: {args}\n\n此操作已被安全阻止。",
                'tool_name': tool_name,
                'args': args,
                'requires_approval': True
            }
    return None

# ... (其餘程式碼)
```

---

## 8. 最佳實踐

- ✅ **使用 `retry_on_closed_resource=True`**: 在連線中斷時自動重試。
- ✅ **驗證目錄路徑**: 確保 MCP 伺服器指向的目錄存在。
- ✅ **提供清晰的指令**: 指導代理程式如何使用可用的 MCP 工具。
- ✅ **處理 MCP 錯誤**: 使用 `try...except` 區塊來捕捉潛在的連線或執行錯誤。

---

## 9. 疑難排解

- **錯誤: "npx command not found"**: 安裝 Node.js。
- **錯誤: "MCP server connection failed"**: 手動測試伺服器指令以檢查錯誤。
- **問題: "Tools not appearing"**: 啟用 ADK 的偵錯日誌以查看工具發現過程。

---

## 10. MCP OAuth 驗證

MCP 支援多種驗證方法以保護對 MCP 伺服器的存取。

### 支援的驗證方法

1.  **OAuth2** (客戶端憑證流程)
2.  **HTTP Bearer Token**
3.  **HTTP 基本驗證**
4.  **API 金鑰**

### OAuth2 驗證 (最安全)

```python
from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams

mcp_tools = MCPToolset(
    connection_params=StdioConnectionParams(
        command='npx',
        args=['-y', '@mycompany/secure-mcp-server']
    ),
    credential={
        'type': 'oauth2',
        'token_url': 'https://auth.example.com/oauth/token',
        'client_id': 'your-client-id',
        'client_secret': 'your-client-secret',
        'scopes': ['read', 'write']
    }
)
```

---

## 總結

您已掌握 MCP 整合和驗證，以擴展代理程式的功能。

**主要收穫**:

- ✅ MCP 為外部工具提供標準化協議。
- ✅ `MCPToolset` 將代理程式連接到 MCP 伺服器。
- ✅ **OAuth2 驗證** 用於安全的生產部署。
- ✅ 可用超過 100 個社群 MCP 伺服器。

## 程式碼實現 (Code Implementation)
- mcp-agent：[程式碼連結](../../../python/agents/mcp-agent/README.md)
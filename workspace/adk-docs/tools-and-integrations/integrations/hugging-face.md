# 適用於 ADK 的 Hugging Face MCP 工具

> 🔔 `更新日期：2026-03-06`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/hugging-face/

[`ADK 支援`: `Python` | `TypeScript`]

[Hugging Face MCP 伺服器](https://github.com/huggingface/hf-mcp-server) 可用於將您的 ADK 代理程式連接到 Hugging Face Hub 以及數千個 Gradio AI 應用程式。

## 使用案例

- **發現 AI/ML 資產**：根據任務、程式庫或關鍵字在 Hub 中搜尋和篩選模型、資料集和論文。
- **建立多步驟工作流**：將工具串聯在一起，例如使用一個工具轉錄音訊，然後使用另一個工具總結生成的文字。
- **尋找 AI 應用程式**：搜尋可以執行特定任務的 Gradio Spaces，例如背景移除或文字轉語音。

## 前置作業

- 在 Hugging Face 中建立 [使用者存取權杖](https://huggingface.co/settings/tokens)。如需更多資訊，請參閱 [說明文件](https://huggingface.co/docs/hub/en/security-tokens)。

## 搭配代理程式使用

<details>
<summary>範例說明</summary>

> Python

**Local MCP Server**
```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# 您的 Hugging Face 存取權杖
HUGGING_FACE_TOKEN = "YOUR_HUGGING_FACE_TOKEN"

# 初始化根代理程式
root_agent = Agent(
    model="gemini-2.5-pro",
    name="hugging_face_agent",
    instruction="幫助使用者從 Hugging Face 獲取資訊",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@llmindset/hf-mcp-server",
                    ],
                    env={
                        "HF_TOKEN": HUGGING_FACE_TOKEN,
                    }
                ),
                timeout=30,
            ),
        )
    ],
)
```

> Python

**Remote MCP Server**
```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

# 您的 Hugging Face 存取權杖
HUGGING_FACE_TOKEN = "YOUR_HUGGING_FACE_TOKEN"

# 初始化根代理程式
root_agent = Agent(
    model="gemini-2.5-pro",
    name="hugging_face_agent",
    instruction="幫助使用者從 Hugging Face 獲取資訊",
    tools=[
        McpToolset(
            connection_params=StreamableHTTPServerParams(
                url="https://huggingface.co/mcp",
                headers={
                    "Authorization": f"Bearer {HUGGING_FACE_TOKEN}",
                },
            ),
        )
    ],
)
```

> TypeScript

**Local MCP Server**
```typescript
import { LlmAgent, MCPToolset } from "@google/adk";

// 您的 Hugging Face 存取權杖
const HUGGING_FACE_TOKEN = "YOUR_HUGGING_FACE_TOKEN";

// 初始化根代理程式
const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "hugging_face_agent",
    instruction: "幫助使用者從 Hugging Face 獲取資訊",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: ["-y", "@llmindset/hf-mcp-server"],
                env: {
                    HF_TOKEN: HUGGING_FACE_TOKEN,
                },
            },
        }),
    ],
});

export { rootAgent };
```

> TypeScript (HTTP 串流連接)

**Remote MCP Server**
```typescript
import { LlmAgent, MCPToolset } from "@google/adk";

// 您的 Hugging Face 存取權杖
const HUGGING_FACE_TOKEN = "YOUR_HUGGING_FACE_TOKEN";

// 初始化根代理程式
const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "hugging_face_agent",
    instruction: "幫助使用者從 Hugging Face 獲取資訊",
    tools: [
        new MCPToolset({
            type: "StreamableHTTPConnectionParams",
            url: "https://huggingface.co/mcp",
            transportOptions: {
                requestInit: {
                    headers: {
                        Authorization: `Bearer ${HUGGING_FACE_TOKEN}`,
                    },
                },
            },
        }),
    ],
});

export { rootAgent };
```

</details>

## 可用工具

| 工具 | 描述 |
| ----------------------------- | ---------------------------------------------------------- |
| Spaces 語義搜尋 | 透過自然語言查詢尋找最佳 AI 應用程式 |
| 論文語義搜尋 | 透過自然語言查詢尋找機器學習研究論文 |
| 模型搜尋 | 透過任務、程式庫等篩選條件搜尋機器學習模型 |
| 資料集搜尋 | 透過作者、標籤等篩選條件搜尋資料集 |
| 說明文件語義搜尋 | 搜尋 Hugging Face 說明文件庫 |
| Hub 儲存庫詳情 | 獲取有關模型、資料集和 Spaces 的詳細資訊 |

## 配置

要配置 Hugging Face Hub MCP 伺服器中哪些工具可用，請造訪您 Hugging Face 帳戶中的 [MCP 設定頁面](https://huggingface.co/settings/mcp)。

要配置本機 MCP 伺服器，您可以使用以下環境變數：

- `TRANSPORT`：要使用的傳輸類型（`stdio`、`sse`、`streamableHttp` 或 `streamableHttpJson`）
- `DEFAULT_HF_TOKEN`：⚠️ 請求將使用在 `Authorization: Bearer` 標頭中收到的 `HF_TOKEN` 進行服務。如果未發送標頭，則使用 `DEFAULT_HF_TOKEN`。僅在開發/測試環境或本機 STDIO 部署中設置此項。⚠️
- 如果使用 stdio 傳輸運行，且未設置 `DEFAULT_HF_TOKEN`，則使用 `HF_TOKEN`。
- `HF_API_TIMEOUT`：Hugging Face API 請求的逾時時間（以毫秒為單位）（預設值：12500ms / 12.5 秒）
- `USER_CONFIG_API`：用於使用者設定的 URL（預設為本機前端）
- `MCP_STRICT_COMPLIANCE`：在 JSON 模式下，設置為 True 以拒絕 GET 405（預設提供歡迎頁面）。
- `AUTHENTICATE_TOOL`：是否包含一個在調用時發出 OAuth 挑戰的驗證工具
- `SEARCH_ENABLES_FETCH`：設置為 true 時，每當啟用 `hf_doc_search` 時，都會自動啟用 `hf_doc_fetch` 工具

## 其他資源

- [Hugging Face MCP 伺服器儲存庫](https://github.com/huggingface/hf-mcp-server)
- [Hugging Face MCP 伺服器說明文件](https://huggingface.co/docs/hub/en/hf-mcp-server)

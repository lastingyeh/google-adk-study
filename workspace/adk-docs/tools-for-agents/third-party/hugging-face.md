# Hugging Face

> 🔔 `更新日期：2026-01-27`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/tools/third-party/hugging-face/

[Hugging Face MCP 伺服器](https://github.com/huggingface/hf-mcp-server) 可用於將您的 ADK 代理程式連接到 Hugging Face Hub 以及數千個 Gradio AI 應用程式。

## 使用案例

- **探索 AI/ML 資產**：在 Hub 上根據任務、程式庫或關鍵字搜尋並篩選模型、資料集和論文。
- **建構多步驟工作流**：將工具鏈結在一起，例如使用一個工具轉錄音訊，然後使用另一個工具總結生成的文字。
- **尋找 AI 應用程式**：搜尋可以執行特定任務的 Gradio Spaces，例如背景移除或文字轉語音。

## 先決條件

- 在 Hugging Face 中建立 [使用者存取權杖 (user access token)](https://huggingface.co/settings/tokens)。更多資訊請參考 [文件](https://huggingface.co/docs/hub/en/security-tokens)。

## 與代理程式搭配使用

<details>
<summary>範例說明</summary>

> 本地 MCP 伺服器 (Local MCP Server)

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# 設定您的 Hugging Face 權杖
HUGGING_FACE_TOKEN = "YOUR_HUGGING_FACE_TOKEN"

# 初始化 Hugging Face 代理程式
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

> 遠端 MCP 伺服器 (Remote MCP Server)

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

# 設定您的 Hugging Face 權杖
HUGGING_FACE_TOKEN = "YOUR_HUGGING_FACE_TOKEN"

# 初始化 Hugging Face 代理程式，使用遠端伺服器連接
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

</details>

## 可用工具

| 工具 | 描述 |
| --- | --- |
| Spaces 語義搜尋 (Spaces Semantic Search) | 透過自然語言查詢尋找最佳 AI 應用程式 |
| 論文語義搜尋 (Papers Semantic Search) | 透過自然語言查詢尋找機器學習研究論文 |
| 模型搜尋 (Model Search) | 使用任務、程式庫等篩選條件搜尋機器學習模型 |
| 資料集搜尋 (Dataset Search) | 使用作者、標籤等篩選條件搜尋資料集 |
| 文件語義搜尋 (Documentation Semantic Search) | 搜尋 Hugging Face 文件庫 |
| Hub 儲存庫詳情 (Hub Repository Details) | 獲取有關模型、資料集和 Spaces 的詳細資訊 |

## 配置

要配置您的 Hugging Face Hub MCP 伺服器中可以使用哪些工具，請造訪您 Hugging Face 帳戶中的 [MCP 設定頁面](https://huggingface.co/settings/mcp)。

要配置本地 MCP 伺服器，您可以使用以下環境變數：

- `TRANSPORT`：要使用的傳輸類型（`stdio`、`sse`、`streamableHttp` 或 `streamableHttpJson`）
- `DEFAULT_HF_TOKEN`：⚠️ 請求將使用在 `Authorization: Bearer` 標頭中收到的 `HF_TOKEN` 進行服務。如果未發送標頭，則使用 `DEFAULT_HF_TOKEN`。請僅在開發/測試環境或本地 STDIO 部署中設置此項。⚠️
- 如果使用 stdio 傳輸執行，且未設置 `DEFAULT_HF_TOKEN`，則使用 `HF_TOKEN`。
- `HF_API_TIMEOUT`：Hugging Face API 請求的逾時時間（以毫秒為單位，預設為 12500ms / 12.5 秒）
- `USER_CONFIG_API`：用於使用者設定的 URL（預設為本地前端）
- `MCP_STRICT_COMPLIANCE`：在 JSON 模式下，設置為 True 以拒絕 GET 405（預設提供歡迎頁面）。
- `AUTHENTICATE_TOOL`：是否包含一個在呼叫時發出 OAuth 挑戰的驗證工具
- `SEARCH_ENABLES_FETCH`：設置為 true 時，每當啟用 `hf_doc_search` 時，都會自動啟用 `hf_doc_fetch` 工具

## 額外資源

- [Hugging Face MCP 伺服器儲存庫](https://github.com/huggingface/hf-mcp-server)
- [Hugging Face MCP 伺服器文件](https://huggingface.co/docs/hub/en/hf-mcp-server)

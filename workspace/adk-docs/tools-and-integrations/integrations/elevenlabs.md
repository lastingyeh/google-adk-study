# ElevenLabs MCP tool for ADK

> 🔔 `更新日期：2025-03-06`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/elevenlabs/

[`ADK 支援`: `Python` | `TypeScript`]

[ElevenLabs MCP 伺服器](https://github.com/elevenlabs/elevenlabs-mcp) 將您的 ADK 代理程式連接到 [ElevenLabs](https://elevenlabs.io/) AI 音訊平台。此整合讓您的代理程式具備生成語音、複製聲音、轉錄音訊、建立音效以及使用自然語言建立對話式 AI 體驗的能力。

## 使用案例

- **文字轉語音生成**：使用多種聲音將文字轉換為自然聽感的語音，並能精細控制穩定性、風格和相似度設定。
- **聲音複製與設計**：從音訊樣本複製聲音，或根據對年齡、性別、口音和語調等期望特徵的文字描述生成新聲音。
- **音訊處理**：從背景噪音中分離語音，將音訊轉換為不同聲音，或進行帶有說話者識別的語音轉文字。
- **音效與音景**：從文字描述生成音效和環境音景，例如「茂密叢林中的雷陣雨，動物們對天氣做出反應」。

## 前置作業

- 註冊 [ElevenLabs 帳號](https://elevenlabs.io/app/sign-up)
- 從您的帳號設定中生成 [API 金鑰](https://elevenlabs.io/app/settings/api-keys)

## 與代理程式搭配使用

<details>
<summary>範例說明</summary>

> Python

**Local MCP Server**
```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# 設定您的 ElevenLabs API 金鑰
ELEVENLABS_API_KEY = "YOUR_ELEVENLABS_API_KEY"

# 初始化 ElevenLabs 代理程式
root_agent = Agent(
    model="gemini-2.5-pro",
    name="elevenlabs_agent",
    instruction="幫助使用者生成語音、複製聲音並處理音訊",
    tools=[
        # 使用 MCPToolset 載入 ElevenLabs MCP 工具
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="uvx",
                    args=["elevenlabs-mcp"],
                    env={
                        "ELEVENLABS_API_KEY": ELEVENLABS_API_KEY,
                    }
                ),
                timeout=30,
            ),
        )
    ],
)
```

> TypeScript

**Local MCP Server**
```typescript
import { LlmAgent, MCPToolset } from "@google/adk";

// 設定您的 ElevenLabs API 金鑰
const ELEVENLABS_API_KEY = "YOUR_ELEVENLABS_API_KEY";

// 初始化 ElevenLabs 代理程式
const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "elevenlabs_agent",
    instruction: "幫助使用者生成語音、複製聲音並處理音訊",
    tools: [
        // 使用 MCPToolset 載入 ElevenLabs MCP 工具
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "uvx",
                args: ["elevenlabs-mcp"],
                env: {
                    ELEVENLABS_API_KEY: ELEVENLABS_API_KEY,
                },
            },
        }),
    ],
});

export { rootAgent };
```

</details>

## 可用的工具

### 文字轉語音與聲音

| 工具 | 描述 |
| --------------------------- | ------------------------------------------------- |
| `text_to_speech` | 使用指定的聲音從文字生成語音 |
| `speech_to_speech` | 轉換音訊使其聽起來像不同的聲音 |
| `text_to_voice` | 從文字描述生成聲音預覽 |
| `create_voice_from_preview` | 將生成的聲音預覽儲存到您的程式庫 |
| `voice_clone` | 從音訊樣本複製聲音 |
| `get_voice` | 獲取特定聲音的詳細資訊 |
| `search_voices` | 在您的程式庫中搜尋聲音 |
| `search_voice_library` | 搜尋公開聲音程式庫 |
| `list_models` | 列出可用的文字轉語音模型 |

### 音訊處理

| 工具 | 描述 |
| ------------------------- | ---------------------------------------------------- |
| `speech_to_text` | 進行帶有說話者識別的語音轉文字 |
| `text_to_sound_effects` | 從文字描述生成音效 |
| `isolate_audio` | 將語音從背景噪音和音樂中分離 |
| `play_audio` | 在本地播放音訊檔案 |
| `compose_music` | 從描述生成音樂 |
| `create_composition_plan` | 建立音樂創作計劃 |

### 對話式 AI

| 工具 | 描述 |
| ----------------------------- | ---------------------------------------------- |
| `create_agent` | 建立對話式 AI 代理程式 |
| `get_agent` | 獲取特定代理程式的詳細資訊 |
| `list_agents` | 列出您所有的對話式 AI 代理程式 |
| `add_knowledge_base_to_agent` | 為代理程式增加知識庫 |
| `make_outbound_call` | 使用代理程式發起外撥電話 |
| `list_phone_numbers` | 列出可用的電話號碼 |
| `get_conversation` | 獲取特定對話的詳細資訊 |
| `list_conversations` | 列出所有對話 |

### 帳號

| 工具 | 描述 |
| -------------------- | ---------------------------------------- |
| `check_subscription` | 檢查您的訂閱和額度使用情況 |

## 配置

ElevenLabs MCP 伺服器可以使用環境變數進行配置：

| 變數 | 描述 | 預設值 |
| ---------------------------- | --------------------------------------- | ----------- |
| `ELEVENLABS_API_KEY` | 您的 ElevenLabs API 金鑰 | 必填 |
| `ELEVENLABS_MCP_BASE_PATH` | 檔案操作的基礎路徑 | `~/Desktop` |
| `ELEVENLABS_MCP_OUTPUT_MODE` | 生成檔案的傳回方式 | `files` |
| `ELEVENLABS_API_RESIDENCY` | 資料落地區域（僅限企業版） | `us` |

### 輸出模式

`ELEVENLABS_MCP_OUTPUT_MODE` 環境變數支援三種模式：

- **`files`** (預設)：將檔案儲存到磁碟並傳回檔案路徑
- **`resources`**：將檔案作為 MCP 資源傳回 (base64 編碼的二進位數據)
- **`both`**：將檔案儲存到磁碟並同時作為 MCP 資源傳回

## 更多資源

- [ElevenLabs MCP 伺服器儲存庫](https://github.com/elevenlabs/elevenlabs-mcp)
- [ElevenLabs MCP 介紹](https://elevenlabs.io/blog/introducing-elevenlabs-mcp)
- [ElevenLabs 文件](https://elevenlabs.io/docs)

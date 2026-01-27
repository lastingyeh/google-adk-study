# ElevenLabs

> 🔔 `更新日期：2026-01-27`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/tools/third-party/elevenlabs/

[ElevenLabs MCP 伺服器](https://github.com/elevenlabs/elevenlabs-mcp) 將您的 ADK 代理連接到 [ElevenLabs](https://elevenlabs.io/) AI 音訊平台。這項整合賦予您的代理使用自然語言生成語音、複製聲音、轉錄音訊、建立音效以及構建對話式 AI 體驗的能力。

## 使用案例

- **文字轉語音生成**：使用各種聲音將文字轉換為聽起來自然的語音，並能精細控制穩定性、風格和相似度設置。

- **聲音複製與設計**：從音訊樣本中複製聲音，或根據對年齡、性別、口音和音調等所需特徵的文字描述生成新聲音。

- **音訊處理**：從背景噪音中分離出語音，將音訊轉換為聽起來像不同聲音的內容，或透過說話者識別將語音轉錄為文字。

- **音效與音景**：從文字描述中生成音效和環境音景，例如「茂密叢林中的一場雷雨，動物們對天氣做出反應」。

## 先決條件

- 註冊一個 [ElevenLabs 帳號](https://elevenlabs.io/app/sign-up)
- 從您的帳號設定中生成一個 [API 金鑰](https://elevenlabs.io/app/settings/api-keys)

## 搭配代理使用

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# 設定您的 ElevenLabs API 金鑰
ELEVENLABS_API_KEY = "YOUR_ELEVENLABS_API_KEY"

# 初始化 root_agent
root_agent = Agent(
    model="gemini-2.5-pro",
    name="elevenlabs_agent",
    instruction="幫助使用者生成語音、複製聲音並處理音訊",
    tools=[
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

## 可用工具

### 文字轉語音與聲音

工具 | 描述
---- | -----------
`text_to_speech` | 使用指定的聲音從文字生成語音
`speech_to_speech` | 將音訊轉換為聽起來像不同聲音的內容
`text_to_voice` | 從文字描述生成聲音預覽
`create_voice_from_preview` | 將生成的聲音預覽儲存到您的庫中
`voice_clone` | 從音訊樣本複製聲音
`get_voice` | 獲取特定聲音的詳細資訊
`search_voices` | 在您的庫中搜尋聲音
`search_voice_library` | 搜尋公開聲音庫
`list_models` | 列出可用的文字轉語音模型

### 音訊處理

工具 | 描述
---- | -----------
`speech_to_text` | 透過說話者識別將音訊轉錄為文字
`text_to_sound_effects` | 從文字描述生成音效
`isolate_audio` | 將語音與背景噪音和音樂分離
`play_audio` | 在本地播放音訊檔案
`compose_music` | 從描述生成音樂
`create_composition_plan` | 建立音樂創作計畫

### 對話式 AI

工具 | 描述
---- | -----------
`create_agent` | 建立一個對話式 AI 代理
`get_agent` | 獲取特定代理的詳細資訊
`list_agents` | 列出您所有的對話式 AI 代理
`add_knowledge_base_to_agent` | 向代理添加知識庫
`make_outbound_call` | 使用代理發起撥出電話
`list_phone_numbers` | 列出可用的電話號碼
`get_conversation` | 獲取特定對話的詳細資訊
`list_conversations` | 列出所有對話

### 帳號

工具 | 描述
---- | -----------
`check_subscription` | 檢查您的訂閱和額度使用情況

## 配置

ElevenLabs MCP 伺服器可以使用環境變數進行配置：

變數 | 描述 | 預設值
-------- | ----------- | -------
`ELEVENLABS_API_KEY` | 您的 ElevenLabs API 金鑰 | 必填
`ELEVENLABS_MCP_BASE_PATH` | 檔案操作的基礎路徑 | `~/Desktop`
`ELEVENLABS_MCP_OUTPUT_MODE` | 生成檔案的傳回方式 | `files`
`ELEVENLABS_API_RESIDENCY` | 資料落地區域（僅限企業版） | `us`

### 輸出模式

`ELEVENLABS_MCP_OUTPUT_MODE` 環境變數支援三種模式：

- **`files`**（預設）：將檔案儲存到磁碟並傳回檔案路徑
- **`resources`**：將檔案作為 MCP 資源傳回（base64 編碼的二進位資料）
- **`both`**：將檔案儲存到磁碟，並且作為 MCP 資源傳回

## 更多資源

- [ElevenLabs MCP 伺服器儲存庫](https://github.com/elevenlabs/elevenlabs-mcp)
- [ElevenLabs MCP 介紹](https://elevenlabs.io/blog/introducing-elevenlabs-mcp)
- [ElevenLabs 文件](https://elevenlabs.io/docs)

# Cartesia

> 🔔 `更新日期：2026-01-27`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/tools/third-party/cartesia/

[Cartesia MCP 伺服器](https://github.com/cartesia-ai/cartesia-mcp) 將您的 ADK 代理程式連接到 [Cartesia](https://cartesia.ai/) AI 音訊平台。此整合讓您的代理程式具備生成語音、跨語言在地化聲音，以及使用自然語言建立音訊內容的能力。

## 使用案例

- **文字轉語音生成**：使用 Cartesia 多樣化的聲音庫將文字轉換為自然聽感的語音，並可控制聲音選擇和輸出格式。

- **語音在地化**：將現有聲音轉換為不同語言，同時保留原始說話者的特徵——非常適合多語言內容創作。

- **音訊填補 (Audio Infill)**：填補音訊片段之間的間隙以建立平滑過渡，適用於播客編輯或有聲書製作。

- **語音轉換**：將音訊剪輯轉換為聽起來像 Cartesia 資料庫中不同聲音的效果。

## 前置作業

- 註冊 [Cartesia 帳號](https://play.cartesia.ai/sign-in)
- 從 Cartesia 遊樂場 (playground) 生成 [API 金鑰](https://play.cartesia.ai/keys)

## 與代理程式搭配使用

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters

    # 您的 Cartesia API 金鑰
    CARTESIA_API_KEY = "YOUR_CARTESIA_API_KEY"

    # 定義根代理程式
    root_agent = Agent(
        model="gemini-2.5-pro",
        name="cartesia_agent",
        instruction="幫助使用者生成語音並處理音訊內容",
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command="uvx",
                        args=["cartesia-mcp"],
                        env={
                            "CARTESIA_API_KEY": CARTESIA_API_KEY,
                            # "OUTPUT_DIRECTORY": "/path/to/output",  # 選填：輸出目錄
                        }
                    ),
                    timeout=30, # 逾時設定（秒）
                ),
            )
        ],
    )
    ```

## 可用工具

工具 | 說明
---- | -----------
`text_to_speech` | 使用指定的聲音將文字轉換為音訊
`list_voices` | 列出所有可用的 Cartesia 聲音
`get_voice` | 取得特定聲音的詳細資訊
`clone_voice` | 從音訊樣本複製聲音
`update_voice` | 更新現有聲音
`delete_voice` | 從您的資料庫中刪除聲音
`localize_voice` | 將聲音轉換為不同語言
`voice_change` | 轉換音訊檔案以使用不同的聲音
`infill` | 填補音訊片段之間的間隙

## 配置

Cartesia MCP 伺服器可以使用環境變數進行配置：

變數 | 說明 | 是否必填
-------- | ----------- | --------
`CARTESIA_API_KEY` | 您的 Cartesia API 金鑰 | 是
`OUTPUT_DIRECTORY` | 儲存生成的音訊檔案的目錄 | 否

## 其他資源

- [Cartesia MCP 伺服器儲存庫](https://github.com/cartesia-ai/cartesia-mcp)
- [Cartesia MCP 文件](https://docs.cartesia.ai/integrations/mcp)
- [Cartesia Playground](https://play.cartesia.ai/)

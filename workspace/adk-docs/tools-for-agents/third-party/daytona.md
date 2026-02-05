# Daytona

> 🔔 `更新日期：2026-01-27`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/tools/third-party/daytona/

[Daytona ADK 外掛程式](https://github.com/daytonaio/daytona-adk-plugin) 將您的 ADK 代理程式連線至 [Daytona](https://www.daytona.io/) 沙箱。此整合賦予您的代理程式在隔離環境中執行程式碼、執行 shell 命令以及管理檔案的能力，從而實現 AI 生成程式碼的安全執行。

## 使用案例

- **安全程式碼執行**：在隔離的沙箱中執行 Python、JavaScript 和 TypeScript 程式碼，而不會對您的本機環境造成風險。

- **Shell 命令自動化**：執行具有可設定逾時和工作目錄的 shell 命令，用於建置任務、安裝或系統操作。

- **檔案管理**：將指令碼和資料集上傳到沙箱，然後擷取產生的輸出和結果。

## 前置作業

- 一個 [Daytona](https://www.daytona.io/) 帳戶
- Daytona API 金鑰

## 安裝

```bash
# 安裝 Daytona ADK 套件
pip install daytona-adk
```

## 與代理程式搭配使用

```python
from daytona_adk import DaytonaPlugin
from google.adk.agents import Agent

# 初始化 Daytona 外掛程式
plugin = DaytonaPlugin(
  api_key="your-daytona-api-key" # 或者設定 DAYTONA_API_KEY 環境變數
)

# 建立根代理程式並整合 Daytona 工具
root_agent = Agent(
    model="gemini-2.5-pro",
    name="sandbox_agent",
    instruction="協助使用者在安全的沙箱中執行程式碼和命令",
    tools=plugin.get_tools(), # 取得 Daytona 提供的工具列表
)
```

## 可用的工具

工具 | 說明
---- | -----------
`execute_code_in_daytona` | 執行 Python、JavaScript 或 TypeScript 程式碼
`execute_command_in_daytona` | 執行 shell 命令
`upload_file_to_daytona` | 將指令碼或資料檔案上傳到沙箱
`read_file_from_daytona` | 讀取指令碼輸出或產生的檔案
`start_long_running_command_daytona` | 啟動背景處理程序（伺服器、監聽程式）

## 了解更多

如需關於建置一個能在安全沙箱中編寫、測試並驗證程式碼的程式碼生成代理程式的詳細指南，請參閱 [此指南](https://www.daytona.io/docs/en/google-adk-code-generator)。

## 其他資源

- [程式碼生成代理程式指南](https://www.daytona.io/docs/en/google-adk-code-generator)
- [PyPI 上的 Daytona ADK](https://pypi.org/project/daytona-adk/)
- [GitHub 上的 Daytona ADK](https://github.com/daytonaio/daytona-adk-plugin)
- [Daytona 文件](https://www.daytona.io/docs)

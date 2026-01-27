# ADK for Python 快速入門

> 🔔 `更新日期：2026-01-23`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/get-started/python/

本指南將引導您快速上手使用 Agent Development Kit (ADK) for Python。在開始之前，請確保您已安裝以下環境：

*   Python 3.10 或更新版本
*   `pip` (用於安裝套件)

## 安裝

執行以下指令來安裝 ADK：

```shell
pip install google-adk
```

> [!TIP] 推薦：建立並啟用 Python 虛擬環境**
>
> 首先，建立一個 Python 虛擬環境：
>
> ```shell
> python -m venv .venv
> ```
>
> 接著，根據您的作業系統啟用虛擬環境：
>
> **Windows CMD**
>
> ```console
> .venv\Scripts\activate.bat
> ```
>
> **Windows Powershell**
>
> ```console
> .venv\Scripts\Activate.ps1
> ```
>
> **MacOS / Linux**
>
> ```bash
> source .venv/bin/activate
> ```

## 建立 Agent 專案

執行 `adk create` 指令來啟動一個新的 Agent 專案。

```shell
adk create my_agent
```

### 探索 Agent 專案

建立完成的 Agent 專案結構如下，其中 `agent.py` 檔案包含了 Agent 的主要控制程式碼。

```
my_agent/
    agent.py      # 主要的 Agent 程式碼
    .env          # 存放 API 金鑰或專案 ID
    __init__.py
```

## 更新您的 Agent 專案

`agent.py` 檔案中包含一個 `root_agent` 的定義，這是 ADK Agent 唯一必要的元素。您也可以為 Agent 定義可供其使用的工具 (Tools)。如下方程式碼所示，更新產生的 `agent.py` 程式碼，為 Agent 加入一個名為 `get_current_time` 的工具：

```python
from google.adk.agents.llm_agent import Agent

# 模擬一個工具的實作
def get_current_time(city: str) -> dict:
    """回傳指定城市的目前時間。"""
    return {"status": "success", "city": city, "time": "10:30 AM"}

root_agent = Agent(
    model='gemini-3-flash-preview',
    name='root_agent',
    description="告知指定城市的目前時間。",
    instruction="你是一個樂於助人的助理，會告知城市的目前時間。請使用 'get_current_time' 工具來達成此目的。",
    tools=[get_current_time],
)
```

### 設定您的 API 金鑰

此專案使用 Gemini API，因此需要一組 API 金鑰。如果您尚未擁有，請在 Google AI Studio 的 [API Keys](https://aistudio.google.com/app/apikey) 頁面建立一組金鑰。

在終端機視窗中，將您的 API 金鑰寫入 `.env` 檔案，作為一個環境變數：

```console
echo 'GOOGLE_API_KEY="YOUR_API_KEY"' > .env
```

> **💡 在 ADK 中使用其他 AI 模型**
>
> ADK 支援使用多種生成式 AI 模型。想了解更多在 ADK Agent 中設定其他模型的資訊，請參閱 [模型與驗證](https://google.github.io/adk-docs/agents/models/)。

## 執行您的 Agent

您可以使用 `adk run` 指令透過互動式命令列介面執行您的 ADK Agent，或使用 ADK 提供的 `adk web` 指令啟動網頁使用者介面。這兩種方式都可以讓您測試並與您的 Agent 互動。

### 使用命令列介面執行

使用 `adk run` 命令列工具來執行您的 Agent。

```console
adk run my_agent
```

![adk-run.png](https://google.github.io/adk-docs/assets/adk-run.png)

### 使用 Web 介面執行

ADK 框架提供了一個網頁介面，您可以用它來測試並與您的 Agent 互動。您可以使用以下指令來啟動網頁介面：

```console
adk web --port 8000
```

> [!NOTE] 注意**
>
> 請在包含您 `my_agent/` 資料夾的**父目錄**下執行此指令。例如，如果您的 Agent 位於 `agents/my_agent/`，請從 `agents/` 目錄執行 `adk web`。

此指令會啟動一個帶有聊天介面的網頁伺服器。您可以透過 (http://localhost:8000) 存取此介面。在左上角選擇您的 Agent，然後輸入您的請求。

![adk-web-dev-ui-chat.png](https://google.github.io/adk-docs/assets/adk-web-dev-ui-chat.png)

> [!WARNING] 警告：ADK Web 僅供開發使用
>
> ADK Web **不適用於正式的生產環境部署**。您應該僅將 ADK Web 用於開發和除錯目的。

## 下一步：建構您的 Agent

現在您已經安裝了 ADK 並執行了您的第一個 Agent，試著跟隨我們的建構指南來打造您自己的 Agent：
- [建立你的代理](https://google.github.io/adk-docs/tutorials/)
---

## 參考資源

*   **Google AI Studio API Keys**: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

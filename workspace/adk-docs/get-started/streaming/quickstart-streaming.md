# 使用 Python 建構串流代理 (Streaming Agent)
> 🔔 `更新日期：2026-01-30`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming/

透過此快速入門，您將學習如何建立一個簡單的代理，並使用 ADK Streaming 來實現低延遲且雙向的語音與影片通訊。我們將安裝 ADK，設定一個基礎的「Google 搜尋」代理，嘗試使用 `adk web` 工具執行代理，接著說明如何使用 ADK Streaming 和 [FastAPI](https://fastapi.tiangolo.com/) 自行建構一個簡單的非同步網頁應用程式。

**注意：** 本指南假設您具有在 Windows、Mac 和 Linux 環境中使用終端機的經驗。

## 支援語音/影片串流的模型

若要在 ADK 中使用語音/影片串流，您需要使用支援 Live API 的 Gemini 模型。您可以在文件中找到支援 Gemini Live API 的**模型 ID**：

- [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
- [Vertex AI: Gemini Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

## 1. 設定環境並安裝 ADK

建立並啟動虛擬環境（建議）：

```bash
# 建立虛擬環境
python -m venv .venv
# 啟動虛擬環境 (每個新的終端機視窗)
# macOS/Linux: source .venv/bin/activate
# Windows CMD: .venv\Scripts\activate.bat
# Windows PowerShell: .venv\Scripts\Activate.ps1
```

安裝 ADK：

```bash
# 使用 pip 安裝 google-adk 套件
pip install google-adk
```

## 2. 專案結構

建立以下包含空白檔案的資料夾結構：

```console
adk-streaming/  # 專案資料夾
└── app/ # 網頁應用程式資料夾
    ├── .env # Gemini API 金鑰
    └── google_search_agent/ # 代理資料夾
        ├── __init__.py # Python 套件初始化檔案
        └── agent.py # 代理定義檔案
```

### agent.py

將以下程式碼區塊複製並貼上到 `agent.py` 檔案中。

關於 `model`，請務必按照先前[模型章節](#supported-models)所述，再次確認模型 ID。

```py
from google.adk.agents import Agent
from google.adk.tools import google_search  # 匯入工具

# 定義根代理 (root agent)
root_agent = Agent(
   # 代理的唯一名稱
   name="basic_search_agent",
   # 代理將使用的語言模型 (LLM)
   # 請從以下網址填入支援 live 的最新模型 ID：
   # https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming/#supported-models
   model="...",
   # 代理用途的簡短描述
   description="使用 Google 搜尋來回答問題的代理。",
   # 設定代理行為的指令
   instruction="你是一位專家研究員。你總是堅持事實。",
   # 新增 google_search 工具以透過 Google 搜尋進行落地 (grounding)
   tools=[google_search]
)
```

`agent.py` 是存放所有代理邏輯的地方，且您必須定義一個 `root_agent`。

請注意整合 [Google 搜尋落地 (grounding with Google Search)](https://ai.google.dev/gemini-api/docs/grounding?lang=python#configure-search) 功能是多麼容易。`Agent` 類別和 `google_search` 工具處理了與 LLM 互動以及搜尋 API 落地的複雜交互作用，讓您可以專注於代理的「用途」和「行為」。

![intro_components.png](https://google.github.io/adk-docs/assets/quickstart-streaming-tool.png)

將以下程式碼區塊複製並貼上到 `__init__.py` 檔案。

```py title="__init__.py"
# 從當前目錄匯入 agent 模組
from . import agent
```

## 3. 設定平台

要執行代理，請從 Google AI Studio 或 Google Cloud Vertex AI 中選擇一個平台：

<details>
<summary>Gemini - Google AI Studio</summary>

1. 從 [Google AI Studio](https://aistudio.google.com/apikey) 取得 API 金鑰。
2. 開啟位於 `app/` 內的 **`.env`** 檔案，並複製貼上以下程式碼。

    ```env title=".env"
    # 設定不使用 Vertex AI
    GOOGLE_GENAI_USE_VERTEXAI=FALSE
    # 填入您的 API 金鑰
    GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
    ```
3. 將 `PASTE_YOUR_ACTUAL_API_KEY_HERE` 替換為您實際的 `API KEY`。
</details>

<details>
<summary>Gemini - Google Cloud Vertex AI</summary>

1. 您需要一個現有的 [Google Cloud](https://cloud.google.com/?e=48754805&hl=en) 帳戶和專案。
  * 設定 [Google Cloud 專案](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-gcp)
  * 設定 [gcloud CLI](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-local)
  * 在終端機執行 `gcloud auth login` 以進行 Google Cloud 驗證。
  * [啟用 Vertex AI API](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com)。
2. 開啟位於 `app/` 內的 **`.env`** 檔案。複製貼上以下程式碼，並更新專案 ID 與地區 (location)。

  ```env title=".env"
  # 設定使用 Vertex AI
  GOOGLE_GENAI_USE_VERTEXAI=TRUE
  # 填入您的專案 ID
  GOOGLE_CLOUD_PROJECT=PASTE_YOUR_ACTUAL_PROJECT_ID
  # 設定地區
  GOOGLE_CLOUD_LOCATION=us-central1
  ```
</details>

## 4. 使用 `adk web` 嘗試代理

現在可以嘗試執行代理了。執行以下指令來啟動 **開發 UI (dev UI)**。首先，請確保將當前目錄切換至 `app`：

```shell
# 切換到應用程式目錄
cd app
```

另外，使用以下指令設定 `SSL_CERT_FILE` 變數。這對於之後的語音和影片測試是必要的。

> OS X & Linux
```bash
# 設定 SSL 憑證檔案路徑
export SSL_CERT_FILE=$(python -m certifi)
```

> Windows
```powershell
# 設定 SSL 憑證檔案路徑
$env:SSL_CERT_FILE = (python -m certifi)
```

接著，執行開發 UI：

```shell
# 啟動 ADK 網頁介面
adk web
```

> [!NOTE] Windows 使用者注意
如果遇到 `_make_subprocess_transport NotImplementedError` 錯誤，請考慮改用 `adk web --no-reload`。

> [!WARNING] 警告：ADK Web 僅供開發使用
ADK Web **並非用於正式環境部署**。您應該僅將 ADK Web 用於開發和除錯目的。

**直接在您的瀏覽器中**開啟提供的 URL（通常是 `http://localhost:8000` 或 `http://127.0.0.1:8000`）。此連線完全保留在您的本機機器上。選擇 `google_search_agent`。

### 使用語音和影片嘗試

要嘗試語音功能，請重新整理網頁瀏覽器，點擊麥克風按鈕以啟用語音輸入，並用口頭詢問以下問題。代理將使用 `google_search` 工具取得最新資訊來回答這些問題。您將即時聽到語音回答。

* 紐約的天氣如何？
* 現在紐約幾點？
* 巴黎的天氣如何？
* 現在巴黎幾點？

要嘗試影片功能，請重新整理網頁瀏覽器，點擊攝影機按鈕以啟用影片輸入，並詢問如「你看到了什麼？」之類的問題。代理將回答他們在影片輸入中看到的內容。

#### 注意事項

- 您無法在原生音訊模型中使用文字聊天。在 `adk web` 上輸入文字訊息時，您會看到錯誤。

### 停止工具

在主控台按 `Ctrl-C` 即可停止 `adk web`。

### 關於 ADK Streaming 的說明

以下功能將在未來版本的 ADK Streaming 中支援：Callback、LongRunningTool、ExampleTool 以及 Shell 代理（例如 SequentialAgent）。

恭喜！您已成功使用 ADK 建立並與您的第一個串流代理進行互動！

## 下一步：建構自定義串流應用程式

[雙向串流開發指南系列](../../bidi-streaming-live/dev-guide/part1.md) 概述了使用 ADK Streaming 建構的自定義非同步網頁應用程式的伺服器與用戶端程式碼，該程式碼可實現即時、雙向的音訊和文字通訊。

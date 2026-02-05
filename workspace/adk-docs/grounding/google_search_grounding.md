# 代理程式的 Google 搜尋基礎 (Grounding)

[`ADK 支援`: `Python v0.1.0` | `TypeScript v0.2.0`]

> 🔔 `更新日期：2026-02-05`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/grounding/google_search_grounding/

[Google 搜尋基礎工具](../tools-for-agents/gemini-api/google-search.md) 是代理程式開發套件 (ADK) 中的一項強大功能，它使 AI 代理程式能夠從網路上存取即時且權威的資訊。透過將您的代理程式連接到 Google 搜尋，您可以為使用者提供由可靠來源支持的最新答案。

此功能對於需要當前資訊（如天氣更新、新聞事件、股票價格或自模型訓練數據截止日期以來可能發生變化的任何事實）的查詢特別有價值。當您的代理程式確定需要外部資訊時，它會自動執行網路搜尋，並將結果併入其回應中，並附上適當的引用。

## 您將學到什麼

在本指南中，您將發現：

- **快速設定**：如何從頭開始建立並執行一個啟用 Google 搜尋的代理程式
- **基礎架構**：網路基礎 (Grounding) 背後的資料流和技術流程
- **回應結構**：如何解析基礎回應及其元數據
- **最佳實踐**：向使用者展示搜尋結果和引用的準則

### 額外資源

作為額外資源，[Deep Search 代理程式開發套件 (ADK) 快速入門](../../python/agents/pack-deep-search/) 有一個將 Google 搜尋基礎作為全端應用程式範例的實際用途。

## Google 搜尋基礎快速入門

本快速入門將引導您建立一個具有 Google 搜尋基礎功能的 ADK 代理程式。本快速入門假設您有一個本地 IDE（VS Code 或 PyCharm 等），並安裝了 Python 3.10+ 且可存取終端機。

### 1. 設定環境並安裝 ADK

以下是為 Python 和 TypeScript 專案設定環境並安裝 ADK 的步驟。

<details>
<summary>範例程式碼</summary>

> Python

建立並啟用虛擬環境：

```bash
# 建立虛擬環境
python -m venv .venv

# 啟用虛擬環境 (每個新終端機)
# macOS/Linux: source .venv/bin/activate
# Windows CMD: .venv\Scripts\activate.bat
# Windows PowerShell: .venv\Scripts\Activate.ps1
```

安裝 ADK：

```bash
# 安裝 Python 版 ADK
pip install google-adk
```

> TypeScript

建立一個新的 Node.js 專案：

```bash
# 初始化專案
npm init -y
```

安裝 ADK：

```bash
# 安裝 TypeScript 版 ADK
npm install @google/adk
```

</details>

### 2. 建立代理程式專案

在專案目錄下，執行以下指令：

> OS X & Linux

```bash
# 步驟 1：為您的代理程式建立一個新目錄
mkdir google_search_agent

# 步驟 2：為代理程式建立 __init__.py
echo "from . import agent" > google_search_agent/__init__.py

# 步驟 3：建立 agent.py (代理程式定義) 和 .env (Gemini 認證配置)
touch google_search_agent/agent.py .env
```

> Windows

```shell
# 步驟 1：為您的代理程式建立一個新目錄
mkdir google_search_agent

# 步驟 2：為代理程式建立 __init__.py
echo "from . import agent" > google_search_agent/__init__.py

# 步驟 3：建立 agent.py (代理程式定義) 和 .env (Gemini 認證配置)
type nul > google_search_agent\agent.py
type nul > google_search_agent\.env
```

#### 編輯 `agent.py` 或 `agent.ts`

將以下程式碼複製並貼上到 `agent.py` 或 `agent.ts` 中：

<details>
<summary>範例程式碼</summary>

> Python

`google_search_agent/agent.py`

```python
from google.adk.agents import Agent
from google.adk.tools import google_search

# 建立具備 Google 搜尋功能的代理程式
root_agent = Agent(
    name="google_search_agent",
    model="gemini-2.5-flash",
    instruction="根據需要使用 Google 搜尋回答問題。務必引用來源。",
    description="具備 Google 搜尋能力的專業搜尋助手",
    tools=[google_search] # 加入 google_search 工具
)
```

現在您將擁有以下目錄結構：

```shell
my_project/
    google_search_agent/
        __init__.py
        agent.py
    .env
```

> TypeScript

google_search_agent/agent.ts

```typescript
import { LlmAgent, GOOGLE_SEARCH } from '@google/adk';

// 建立具備 Google 搜尋功能的代理程式
const rootAgent = new LlmAgent({
    name: "google_search_agent",
    model: "gemini-2.5-flash",
    instruction: "根據需要使用 Google 搜尋回答問題。務必引用來源。",
    description: "具備 Google 搜尋能力的專業搜尋助手",
    tools: [GOOGLE_SEARCH], // 加入 GOOGLE_SEARCH 工具
});
```

現在您將擁有以下目錄結構：

```shell
my_project/
    google_search_agent/
        agent.ts
    package.json
    tsconfig.json
    .env
```
</details>

### 3. 選擇平台

要執行代理程式，您需要選擇一個供代理程式呼叫 Gemini 模型的平台。從 Google AI Studio 或 Vertex AI 中選擇一個：

<details>
<summary>Google AI Studio</summary>

1. 從 [Google AI Studio](https://aistudio.google.com/apikey) 取得 API 金鑰。

2. 使用 Python 時，開啟 **`.env`** 檔案並複製貼上以下程式碼。

    ```shell
    #.env
    # 關閉 Vertex AI 使用
    GOOGLE_GENAI_USE_VERTEXAI=FALSE
    # 填入您的 API 金鑰
    GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
    ```
3. 將 `PASTE_YOUR_ACTUAL_API_KEY_HERE` 替換為您的實際 `API KEY`。

</details>

<details>
<summary>Gemini-Google Cloud Vertex AI</summary>

1. 您需要一個現有的 [Google Cloud](https://cloud.google.com/?e=48754805&hl=en) 帳戶和一個專案。

   - 設定 [Google Cloud 專案](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-gcp)
   - 設定 [gcloud CLI](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-local)
   - 在終端機執行 `gcloud auth login` 向 Google Cloud 進行身分驗證。
   - [啟用 Vertex AI API](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com)。

2. 使用 Python 時，開啟 **`.env`** 檔案並複製貼上以下程式碼，並更新專案 ID 和位置。

    ```shell
    # .env
    # 啟用 Vertex AI 使用
    GOOGLE_GENAI_USE_VERTEXAI=TRUE
    # 您的專案 ID
    GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
    # 您的位置 (區域)
    GOOGLE_CLOUD_LOCATION=LOCATION
    ```
</details>


### 4. 執行您的代理程式

有多種方式可以與您的代理程式互動：

<details>
<summary>Dev UI(adk web)</summary>

執行以下指令來啟動 **開發 UI (dev UI)**。

```shell
# 啟動 ADK 網頁介面
adk web
```

> [!NOTE] Windows 使用者注意事項
當遇到 `_make_subprocess_transport NotImplementedError` 時，請考慮改用 `adk web --no-reload`。

**步驟 1：** 直接在瀏覽器中開啟提供的 URL（通常是 `http://localhost:8000` 或 `http://127.0.0.1:8000`）。

**步驟 2.** 在 UI 的左上角，您可以在下拉選單中選擇您的代理程式。選擇 "google_search_agent"。

> [!WARNING]疑難排解
如果您在下拉選單中沒看到 "google_search_agent"，請確保您是在代理程式資料夾的 **父資料夾**（即 google_search_agent 的父資料夾）中執行 `adk web`。

**步驟 3.** 現在您可以使用文字框與您的代理程式聊天。

</details>

<details>
<summary>Terminal (adk run)</summary>

執行以下指令，與您的天氣代理程式聊天。

```shell
# 在終端機執行代理程式
adk run google_search_agent
```
要退出，請使用 Cmd/Ctrl+C。
</details>

### 可嘗試的範例提示

透過這些問題，您可以確認代理程式確實正在呼叫 Google 搜尋來獲取最新的天氣和時間。

- 紐約的天氣如何？
- 紐約現在幾點？
- 巴黎的天氣如何？
- 巴黎現在幾點？

![google_search_grd_adk-web](https://google.github.io/adk-docs/assets/google_search_grd_adk_web.png)

您已成功使用 ADK 建立並與您的 Google 搜尋代理程式互動！

## Google 搜尋基礎的工作原理

基礎 (Grounding) 是將您的代理程式與網路上的即時資訊連接起來的過程，使其能夠產生更準確、更新的回應。當使用者的提示需要模型未受過訓練的資訊或具有時效性的資訊時，代理程式底層的大型語言模型會智慧地決定調用 google_search 工具來尋找相關事實。

### **資料流圖**

此圖表說明了使用者查詢如何產生基礎回應的逐步過程。

![google_search_grd_dataflow](https://google.github.io/adk-docs/assets/google_search_grd_dataflow.png)

### **詳細說明**

基礎代理程式使用圖表中描述的資料流來檢索、處理外部資訊，並將其併入呈現給使用者的最終答案中。

1. **使用者查詢**：終端使用者透過提問或發出指令與您的代理程式互動。
2. **ADK 編排**：代理程式開發套件編排代理程式的行為，並將使用者的訊息傳遞給代理程式的核心。
3. **LLM 分析與工具呼叫**：代理程式的 LLM（例如 Gemini 模型）分析提示。如果它確定需要外部、最新的資訊，它會透過呼叫 google_search 工具觸發基礎機制。這非常適合回答有關最近新聞、天氣或模型訓練數據中不存在的事實的查詢。
4. **基礎服務互動**：google_search 工具與內部基礎服務互動，該服務制定並向 Google 搜尋索引發送一個或多個查詢。
5. **內容注入**：基礎服務檢索相關網頁和片段。然後，它在產生最終回應之前將這些搜尋結果整合到模型的內容 (context) 中。這關鍵的一步允許模型對事實性的即時數據進行「推理」。
6. **產生基礎回應**：現在有了最新搜尋結果的資訊，LLM 產生一個併入了檢索到的資訊的回應。
7. **展示帶有來源的回應**：ADK 接收最終的基礎回應，其中包括必要的來源 URL 和 groundingMetadata，並將其連同引用呈現給使用者。這使終端使用者能夠驗證資訊，並建立對代理程式答案的信任。

### 理解 Google 搜尋基礎的回應

當代理程式使用 Google 搜尋來基礎化回應時，它會返回一組詳細的資訊，不僅包括最終的文字答案，還包括用於產生該答案的來源。此元數據對於驗證回應以及提供原始來源的引用至關重要。

#### **基礎回應範例**

以下是模型在基礎查詢後返回的內容對象範例。

**最終答案文字：**

```text
"是的，國際邁阿密在 FIFA 俱樂部世界盃的上一場比賽中獲勝。他們在第二場分組賽中以 2-1 擊敗了波爾圖。他們在錦標賽的第一場比賽中與阿赫利足球俱樂部以 0-0 戰平。國際邁阿密預計將於 2025 年 6 月 23 日星期一進行對陣帕梅拉斯的第三場分組賽。"
```

**基礎元數據片段：**

```json
"groundingMetadata": {
  "groundingChunks": [
    { "web": { "title": "mlssoccer.com", "uri": "..." } },
    { "web": { "title": "intermiamicf.com", "uri": "..." } },
    { "web": { "title": "mlssoccer.com", "uri": "..." } }
  ],
  "groundingSupports": [
    {
      "groundingChunkIndices": [0, 1],
      "segment": {
        "startIndex": 65,
        "endIndex": 126,
        "text": "他們在第二場分組賽中以 2-1 擊敗了波爾圖。"
      }
    },
    {
      "groundingChunkIndices": [1],
      "segment": {
        "startIndex": 127,
        "endIndex": 196,
        "text": "他們在錦標賽的第一場比賽中與阿赫利足球俱樂部以 0-0 戰平。"
      }
    },
    {
      "groundingChunkIndices": [0, 2],
      "segment": {
        "startIndex": 197,
        "endIndex": 303,
        "text": "國際邁阿密預計將於 2025 年 6 月 23 日星期一進行對陣帕梅拉斯的第三場分組賽。"
      }
    }
  ],
  "searchEntryPoint": { ... }
}
```

#### **如何解析回應**

元數據提供了模型生成的文字與支持它的來源之間的連結。以下是逐步分解：

1. **groundingChunks**：這是模型參考的網頁列表。每個區塊包含網頁標題和連結到來源的 uri。
2. **groundingSupports**：此列表將最終答案中的特定句子連結回 groundingChunks。
3. **segment**：此對象識別最終文字答案的特定部分，由其 startIndex、endIndex 和文字本身定義。
4. **groundingChunkIndices**：此陣列包含對應於 groundingChunks 中所列來源的索引編號。例如，「他們以 2-1 擊敗了波爾圖...」這句話得到了來自索引 0 和 1 的 groundingChunks 資訊的支持（皆來自 mlssoccer.com 和 intermiamicf.com）。

### 如何展示 Google 搜尋基礎的回應

使用基礎功能的一個關鍵部分是正確地向終端使用者展示資訊，包括引用和搜尋建議。這可以建立信任並允許使用者驗證資訊。

![google_search_grd_resp](https://google.github.io/adk-docs/assets/google_search_grd_resp.png)

#### **展示搜尋建議**

`groundingMetadata` 中的 `searchEntryPoint` 對象包含用於展示搜尋查詢建議的預先格式化 HTML。如範例圖所示，這些通常渲染為可點擊的標籤 (chips)，允許使用者探索相關主題。

**來自 searchEntryPoint 的渲染 HTML：** 元數據提供了必要的 HTML 和 CSS 來渲染搜尋建議欄，其中包括 Google 標誌以及諸如「下一屆 FIFA 俱樂部世界盃是什麼時候」和「國際邁阿密 FIFA 俱樂部世界盃歷史」等相關查詢標籤。將此 HTML 直接整合到您應用程式的前端，將按預期展示建議。

如需更多資訊，請參閱 Vertex AI 文件中的 [使用 Google 搜尋建議](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-search-suggestions)。

## 總結

Google 搜尋基礎將 AI 代理程式從靜態知識庫轉變為動態、連網的助手，能夠提供即時、準確的資訊。透過將此功能整合到您的 ADK 代理程式中，您可以使它們能夠：

- 存取超出其訓練數據的當前資訊
- 為透明度和信任提供來源引用
- 提供具有可驗證事實的全面答案
- 透過相關搜尋建議增強使用者體驗

基礎過程無縫地將使用者查詢連接到 Google 龐大的搜尋索引，在保持對話流的同時豐富具有最新背景的回應。透過正確實施和展示基礎回應，您的代理程式將成為資訊發現和決策的強大工具。

# 代理程式的 Vertex AI Search Grounding (grouding )

[`ADK 支援`: `Python v0.1.0` | `TypeScript v0.2.0`]

> 🔔 `更新日期：2026-02-05`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/grounding/vertex_ai_search_grounding/

[Vertex AI Search](../tools-for-agents/google-cloud/vertex-ai-search.md) 是代理程式開發套件 (ADK) 的強大工具，它使 AI 代理程式能夠存取來自您的私人企業文件和數據庫的信息。通過將您的代理程式連接到已索引的企業內容，您可以為用戶提供基於您組織知識庫的答案。

此功能對於需要來自內部文檔、政策、研究論文或任何已在您的 [Vertex AI Search](https://cloud.google.com/enterprise-search) 資料儲存中索引的專有內容的企業特定查詢特別有價值。當您的代理程式確定需要來自您知識庫的信息時，它會自動搜索您的索引文檔，並將結果納入其 回應中，並附上適當的引用。

## 您將學習到的內容

在本指南中，您將發現：

- **快速設置 (Quick Setup)**：如何從頭開始創建並運行一個啟用了 Vertex AI Search 的代理程式
- **Grounding 架構 (Grounding Architecture)**：企業文件grouding 背後的數據流和技術流程
- **Response 結構 (Response Structure)**：如何解讀grouding 的 回應及其元數據
- **最佳實踐 (Best Practices)**：向用戶顯示引文和文件參考的準則

## Vertex AI Search Grounding 快速上手

本快速上手指南將引導您創建一個具有 Vertex AI Search  grouding 功能的 ADK 代理程式。本快速上手假設您擁有一個本地 IDE（如 VS Code 或 PyCharm 等），並安裝了 Python 3.10+ 及具備終端訪問權限。

### 1. 準備 Vertex AI Search

如果您已經擁有 Vertex AI Search 資料儲存 (Data Store) 及其資料儲存 ID，可以跳過此部分。如果沒有，請按照 [開始使用自定義搜索](https://cloud.google.com/generative-ai-app-builder/docs/try-enterprise-search#unstructured-data) 中的說明操作，直到 [創建資料儲存](https://cloud.google.com/generative-ai-app-builder/docs/try-enterprise-search#create_a_data_store) 結束，並選擇 `非結構化數據` (Unstructured data) 選項卡。通過此說明，您將使用來自 [Alphabet 投資者網站](https://abc.xyz/) 的收益報告 PDF 構建一個示例資料儲存。

完成創建資料儲存部分後，打開 [資料儲存 (Data Stores)](https://console.cloud.google.com/gen-app-builder/data-stores/) 並選擇您創建的資料儲存，找到 `資料儲存 ID`：

請記下此 `資料儲存 ID`，我們稍後將使用它。

![vertex_ai_search_grd_data_store](https://google.github.io/adk-docs/assets/vertex_ai_search_grd_data_store.png)

### 2. 設置環境與安裝 ADK

以下是為 Python 和 TypeScript 項目設置環境並安裝 ADK 的步驟。

創建並激活虛擬環境：

<details>
<summary>範例說明</summary>

> Python
```bash
# 創建虛擬環境
python -m venv .venv

# 激活虛擬環境 (每個新終端)
# macOS/Linux: source .venv/bin/activate
# Windows CMD: .venv\\Scripts\\activate.bat
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
```

安裝 ADK：
```bash
# 使用 pip 安裝 Google ADK 套件
pip install google-adk
```

> Typescript

創建一個新的 Node.js 項目：

```bash
# 初始化新的 Node.js 項目，並使用預設值
npm init -y
```

安裝 ADK：
```bash
# 使用 npm 安裝 Google ADK 套件
npm install @google/adk
```
</details>

### 3. 創建代理程式項目

在項目目錄下，運行以下命令：

<details>
<summary>OS X & Linux</summary>

```shell
# 步驟 1: 為您的代理程式創建一個新目錄
mkdir vertex_search_agent

# 步驟 2: 為代理程式創建 __init__.py 文件
echo "from . import agent" > vertex_search_agent/__init__.py

# 步驟 3: 創建 agent.py (代理程式定義) 和 .env (身份驗證配置)
touch vertex_search_agent/agent.py .env
```

</details>

<details>
<summary>Windows</summary>

```shell
# 步驟 1: 為您的代理程式創建一個新目錄
mkdir vertex_search_agent

# 步驟 2: 為代理程式創建 __init__.py 文件
echo "from . import agent" > vertex_search_agent/__init__.py

# 步驟 3: 創建 agent.py (代理程式定義) 和 .env (身份驗證配置)
type nul > vertex_search_agent\agent.py
type nul > google_search_agent\.env
```

</details>

#### 編輯 `agent.py`

將以下代碼複製並粘貼到 `agent.py` 中，並在 `配置` 部分將 `YOUR_PROJECT_ID` 和 `YOUR_DATASTORE_ID` 分別替換為您的項目 ID 和資料儲存 ID：

`vertex_search_agent/agent.py`

```python
from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool

# 配置資訊
# 請將 YOUR_PROJECT_ID 替換為您的專案 ID，YOUR_DATASTORE_ID 替換為您的資料儲存 ID
DATASTORE_ID = "projects/YOUR_PROJECT_ID/locations/global/collections/default_collection/dataStores/YOUR_DATASTORE_ID"

# 定義根代理程式
root_agent = Agent(
    name="vertex_search_agent",
    model="gemini-2.5-flash",
    # 設定指令：指示代理程式使用 Vertex AI Search 從內部文件中尋找答案，並始終引用來源
    instruction="Answer questions using Vertex AI Search to find information from internal documents. Always cite sources when available.",
    description="具備 Vertex AI Search 能力的企業文件搜索助手",
    # 註冊 Vertex AI Search 工具
    tools=[VertexAiSearchTool(data_store_id=DATASTORE_ID)]
)
```

現在您將擁有以下目錄結構：

```shell
my_project/
    vertex_search_agent/
        __init__.py
        agent.py
    .env
```

### 4. 身份驗證設置

**注意：Vertex AI Search 需要 Google Cloud Platform (Vertex AI) 身份驗證。此工具不支持 Google AI Studio。**

- 設置 [gcloud CLI](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-local)

- 通過在終端運行 `gcloud auth login` 向 Google Cloud 進行身份驗證。

- 打開 **`.env`** 文件，複製並粘貼以下代碼，並更新項目 ID 和位置。

    `.env`
    ```shell
    # 啟用 Vertex AI
    GOOGLE_GENAI_USE_VERTEXAI=TRUE
    # 您的 Google Cloud 專案 ID
    GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
    # 您的 Google Cloud 區域位置
    GOOGLE_CLOUD_LOCATION=LOCATION
    ```

### 5. 運行您的代理程式

有多種方式可以與您的代理程式互動：

運行以下命令啟動 **開發 UI (dev UI)**。

<details>
<summary>Dev UI (adk web)</summary>

```shell
# 啟動 ADK 網頁介面
adk web
```

> [!NOTE] Windows 用戶注意
當遇到 `_make_subprocess_transport NotImplementedError` 時，請考慮改用 `adk web --no-reload`。

**步驟 1：** 直接在瀏覽器中打開提供的 URL（通常為 `http://localhost:8000` 或 `http://127.0.0.1:8000`）。

**步驟 2.** 在 UI 的左上角，您可以在下拉菜單中選擇您的代理程式。選擇 "vertex_search_agent"。

> [!WARNING] 故障排除
如果您在下拉菜單中沒有看到 "vertex_search_agent"，請確保您是在代理程式文件夾的 **父文件夾** 中運行 `adk web`（即 vertex_search_agent 的父文件夾）。

**步驟 3.** 現在您可以使用文本框與您的代理程式聊天。
</details>


運行以下命令，與您的 Vertex AI Search 代理程式聊天。

<details>
<summary>Terminal (adk run)</summary>

```shell
# 在終端機中運行代理程式
adk run vertex_search_agent
```

要退出，請使用 Cmd/Ctrl+C。
</details>

### 嘗試示例提示

通過這些問題，您可以確認代理程式實際上正在調用 Vertex AI Search 從 Alphabet 報告中獲取信息：

- 2022 年第一季度 Google Cloud 的收入是多少？
- YouTube 的情況如何？

![vertex_ai_search_grd_adk_web](https://google.github.io/adk-docs/assets/vertex_ai_search_grd_adk_web.png)

您已成功使用 ADK 創建並與您的 Vertex AI Search 代理程式進行了互動！

## Vertex AI Search Grounding 的工作原理

Vertex AI Search grouding 是將您的代理程式連接到組織的索引文件和數據的過程，使其能夠基於私人企業內容生成準確的 回應。當用戶的提示需要來自內部知識庫的信息時，代理程式底層的 LLM 會智能地決定調用 `VertexAiSearchTool` 以從您的索引文件中查找相關事實。

### **數據流圖**

此圖說明了用戶查詢如何導致 grouding 回應的分步過程。

![vertex_ai_search_grd_dataflow](https://google.github.io/adk-docs/assets/vertex_ai_search_grd_dataflow.png)

### **詳細說明**

 grouding 代理程式使用圖中描述的數據流來檢索、處理企業信息，並將其納入呈現給用戶的最終答案中。

1. **用戶查詢**：終端用戶通過詢問有關內部文件或企業數據的問題與您的代理程式互動。
2. **ADK 編排**：代理程式開發套件編排代理程式的行為，並將用戶消息傳遞給代理程式的核心。
3. **LLM 分析和工具調用**：代理程式的 LLM（例如 Gemini 模型）分析提示。如果它確定需要來自索引文件的信息，它會通過調用 VertexAiSearchTool 觸發 grouding 機制。這對於回答有關公司政策、技術文檔或專有研究的查詢非常理想。
4. **Vertex AI Search 服務交互**：VertexAiSearchTool 與您配置的 Vertex AI Search 資料儲存交互，該資料儲存包含您的索引企業文件。該服務針對您的私人內容制定並執行搜索查詢。
5. **文件檢索與排序**：Vertex AI Search 根據語義相似性和相關性評分從您的資料儲存中檢索並排序最相關的文件區塊。
6. **上下文注入**：搜索服務在生成最終 回應之前將檢索到的文件片段集成到模型的上下文中。這一關鍵步驟允許模型對組織的事實數據進行「推理」。
7. **grouding 回應生成**：現在，LLM 在相關企業內容的告知下，生成一個包含從文件中檢索到的信息的 回應。
8. **帶來源的 回應呈現**：ADK 接收最終的 grouding 回應，其中包括必要的文件參考來源和 grouding 元數據 (groundingMetadata)，並將其呈現給用戶並附上引用。這允許終端用戶根據您的企業來源驗證信息。

## 理解 Vertex AI Search grounding 回應結構

當代理程式使用 Vertex AI Search grounding 回應結構時，它會返回詳細信息，包括最終的文本答案以及用於生成該答案的文件的元數據。此元數據對於驗證 回應並為您的企業來源提供引用至關重要。

### grouding 回應示例

以下是模型在針對企業文件進行 grouding 查詢後返回的內容對象示例。

**最終答案文本：**

```text
"為醫療記錄員 (medical scribe) 開發模型面臨多項重大挑戰，這主要是由於醫療文件的複雜性質、涉及的敏感數據以及臨床工作流程的苛刻要求。主要挑戰包括：**準確性和可靠性：** 醫療文件需要極高的準確性，因為錯誤可能導致誤診、錯誤治療和法律後果。確保 AI 模型能夠可靠地捕捉細微的醫療語言、區分主觀和客觀信息，並準確轉錄醫生與患者的互動是一個主要障礙。**自然語言理解 (NLU) 和語音識別：** 醫療對話通常節奏很快，涉及高度專業的術語、首字母縮略詞和縮寫，並且可能由具有不同口音或說話模式的個人說出... [ 回應繼續詳細分析隱私、整合和技術挑戰]"
```

**grouding 元數據片段：**

這是您將收到的 grouding 元數據。在 `adk web` 上，您可以在 `Response` 選項卡上找到它：

```json
{
  "groundingMetadata": {
    "groundingChunks": [
      {
        "document": {
          "title": "醫療記錄中的 AI：技術挑戰",
          "uri": "projects/your-project/locations/global/dataStores/your-datastore-id/documents/doc-medical-scribe-ai-tech-challenges",
          "id": "doc-medical-scribe-ai-tech-challenges"
        }
      },
      {
        "document": {
          "title": "醫療保健領域 AI 的監管與倫理障礙",
          "uri": "projects/your-project/locations/global/dataStores/your-datastore-id/documents/doc-ai-healthcare-ethics",
          "id": "doc-ai-healthcare-ethics"
        }
      }
      // ... 其他文件
    ],
    "groundingSupports": [
      {
        "groundingChunkIndices": [0, 1],
        "segment": {
          "endIndex": 637,
          "startIndex": 433,
          "text": "確保 AI 模型能夠可靠地捕捉細微的醫療語言..."
        }
      }
      // ... 連結文本段落到來源文件的其他支持資訊
    ],
    "retrievalQueries": [
      "medical domain NLP challenges",
      "AI medical scribe challenges",
      "difficulties in developing AI for medical scribes"
      // ... 執行的其他搜索查詢
    ]
  }
}
```

### 如何解讀回應

元數據提供了模型生成的文本與支持它的企業文件之間的聯繫。以下是逐步分解：

- **groundingChunks**：這是模型諮詢過的企業文件列表。每個區塊包含文件標題、uri（文件路徑）和 id。
- **groundingSupports**：此列表將最終答案中的特定句子連接回 `groundingChunks`。
- **segment**：此對象標識最終文本答案中的特定部分，由其 `startIndex`、`endIndex` 和 `text` 本身定義。
- **groundingChunkIndices**：此數組包含與 `groundingChunks` 中列出的來源相對應的索引號。例如，關於「HIPAA 合規性」的文本由來自索引 1（「監管與倫理障礙」文件）的 `groundingChunks` 信息支持。
- **retrievalQueries**：此數組顯示了為了查找相關信息而針對您的資料儲存執行的特定搜索查詢。

## 如何顯示 Vertex AI Search grouding 回應

與 Google Search grouding 不同，Vertex AI Search grouding 不需要特定的顯示組件。然而，顯示引文和文件參考可以建立信任，並允許用戶根據組織的權威來源驗證信息。

### 可選的引文顯示

由於提供了grouding 元數據，您可以根據應用程序需求選擇實現引文顯示：

**簡單文本顯示（最小化實現）：**

```python
# 遍歷事件流
for event in events:
    # 檢查是否為最終 回應
    if event.is_final_response():
        # 打印 回應文本
        print(event.content.parts[0].text)

        # 可選：顯示來源文件數量
        if event.grounding_metadata:
            print(f"\n基於 {len(event.grounding_metadata.grounding_chunks)} 份文件")
```

**增強型引文顯示（可選）：** 您可以實現交互式引文，顯示哪些文件支持每個聲明。grouding 元數據提供了將文本段落映射到來源文件所需的所有信息。

### 實現注意事項

在實現 Vertex AI Search grouding 顯示時：

1. **文件訪問權限**：驗證用戶對引用文件的權限
2. **簡單集成**：基本文本輸出不需要額外的顯示邏輯
3. **可選增強**：僅當您的用例從來源引用中受益時才添加引文
4. **文件鏈接**：需要時將文件 URI 轉換為可訪問的內部鏈接
5. **搜索查詢**：retrievalQueries 數組顯示了針對您的資料儲存執行了哪些搜索

## 總結

Vertex AI Search Grounding 將 AI 代理程式從通用助手轉變為企業特定的知識系統，能夠從組織的私人文件中提供準確、標註來源的信息。通過將此功能集成到您的 ADK 代理程式中，您可以使它們能夠：

- 訪問來自索引文件存儲庫的專有信息
- 提供來源引用以實現透明度和信任
- 提供具有可驗證企業事實的全面答案
- 在您的 Google Cloud 環境中維護數據隱私

grouding 過程將用戶查詢無縫連接到您組織的知識庫，在保持對話流的同時，利用來自私人文件的相關上下文豐富回應。通過適當的實施，您的代理程式將成為企業信息發現和決策的強大工具。
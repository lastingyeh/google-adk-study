# 第 1 部分：ADK 雙向串流簡介

> 🔔 `更新日期：2026-01-30`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/streaming/dev-guide/part1/

Google 的代理程式開發套件 ([ADK](https://google.github.io/adk-docs/)) 提供了一個用於使用 Gemini 模型構建生產級雙向串流 (Bidi-streaming) 應用程式的框架。本指南介紹了 ADK 的串流架構，該架構可透過多模態通道（文字、音訊、視訊）實現使用者與 AI 代理程式之間的即時雙向通訊。

**你將學到什麼**：本部分涵蓋了雙向串流的基礎知識、底層 Live API 技術（Gemini Live API 和 Vertex AI Live API）、ADK 的架構組件（`LiveRequestQueue`、`Runner`、`Agent`）以及一個完整的 FastAPI 實作範例。你將了解 ADK 如何處理對話執行緒管理、工具編排和平台抽象——將數月的基礎設施開發減少為宣告式配置。

## ADK 雙向串流展示

為了幫助你理解本指南中的概念，我們提供了一個示範應用程式，展示了 ADK 雙向串流的實際運作。這個基於 FastAPI 的示範透過一個實際的、現實世界的架構實現了完整的串流生命週期。

**範例儲存庫**：[adk-samples/python/agents/bidi-demo](https://github.com/google/adk-samples/tree/main/python/agents/bidi-demo)

![ADK 雙向串流展示](https://google.github.io/adk-docs/streaming/dev-guide/assets/bidi-demo-screen.png)

示範功能包括：

- **WebSocket 通訊**：具有並行上游/下游任務的即時雙向串流
- **多模態請求**：文字、音訊和圖像/影片輸入，並帶有自動逐字稿
- **靈活的響應**：基於模型能力的文字或音訊輸出
- **互動式使用者介面**：帶有事件控制台的網頁介面，用於監控 Live API 事件
- **Google 搜尋整合**：具備工具呼叫能力的代理程式

**我們強烈建議在深入閱讀指南之前安裝並執行此示範**。動手實驗將幫助你更深入地理解這些概念，且示範程式碼可在本指南的所有部分中作為實用的參考。

有關安裝說明和使用細節，請參閱 [示範 README](https://github.com/google/adk-samples/tree/main/python/agents/bidi-demo)。

## 1.1 什麼是雙向串流？

雙向串流 (Bidirectional streaming) 代表了與傳統 AI 互動的根本轉變。它不再是僵化的「提問並等待」模式，而是實現了**即時的雙向通訊**，人類和 AI 都可以同時說話、聆聽和回應。這創造了自然、像人一樣的對話，具有即時反應和革命性的中斷正在進行的互動的能力。

想像一下傳送電子郵件與進行電話交談之間的區別。傳統的 AI 互動就像電子郵件——你發送一條完整的訊息，等待完整的延遲，然後再發送另一條完整的訊息。雙向串流就像電話交談——流暢、自然，能夠即時中斷、澄清和回應。

### 關鍵特性

這些特性將雙向串流與傳統 AI 互動區分開來，並使其在創造迷人的使用者體驗方面具有獨特的力量：

- **雙向通訊**：持續的資料交換，無需等待完整的回應。使用者可以在 AI 回應中途以新輸入中斷，從而創造自然的對話流。AI 在檢測到使用者說完話後進行回應（透過自動語音活動檢測或明確的活動訊號）。

- **回應式中斷**：或許是自然使用者體驗中最重要的功能——使用者可以在代理程式回應中途以新輸入中斷，就像在人類對話中一樣。如果 AI 正在解釋量子物理學，而你突然問「等等，電子是什麼？」，AI 會立即停止並解決你的問題。

- **最適合多模態**：雙向串流在多模態互動中表現出色，因為它可以在單個連接中同時處理不同的輸入類型。使用者可以在展示文件的同時說話，在語音通話期間輸入追蹤問題，或在不丟失上下文的情況下無縫切換通訊模式。這種統一的方法消除了為每種模態管理單獨通道的複雜性。


```mermaid
sequenceDiagram
    participant Client as 使用者
    participant Agent as 代理程式

    Client->>Agent: 「嗨！」
    Client->>Agent: 「請解釋日本的歷史」
    Agent->>Client: 「你好！」
    Agent->>Client: 「好的！日本的歷史是...」（內容串流中）
    Client->>Agent: 「啊，等等。」

    Agent->>Client: 「好的，請問有什麼需要幫忙？」 [已中斷: true]
```

### 與其他串流類型的區別

了解雙向串流與其他方法的不同之處對於理解其獨特價值至關重要。串流領域包括幾種不同的模式，每種模式服務於不同的使用案例：

> [!NOTE] 串流類型比較
**雙向串流**與其他串流方法有根本的不同：
> - **伺服器端串流 (Server-Side Streaming)**：從伺服器到客戶端的單向資料流。就像觀看直播影片串流——你接收持續的資料，但無法即時與其互動。對儀表板或直播提要很有用，但不適用於對話。
> - **Token 級別串流 (Token-Level Streaming)**：順序的文字 Token 交付，不可中斷。AI 逐字生成回應，但你必須等待完成後才能發送新輸入。就像觀看某人即時輸入訊息——你看到它正在形成，但無法中斷。
> - **雙向串流 (Bidi-streaming)**：具備中斷支援的完整雙向通訊。真正的對話式 AI，雙方可以同時說話、聆聽和回應。這就是實現自然對話的原因，你可以在對話中途進行中斷、澄清或更改主題。

### 現實世界的應用

雙向串流透過使代理程式能夠以類人的響應能力和智慧運作，徹底改變了代理型 AI 應用程式。這些應用程式展示了串流如何將靜態 AI 互動轉變為感覺真正智慧且主動的動態、代理驅動體驗。

在 [Shopper's Concierge 示範](https://www.youtube.com/watch?v=LwHPYyw7u6U) 的影片中，多模態雙向串流功能透過實現更快速、更直觀的購物體驗，顯著提升了電子商務的使用者體驗。對話理解與快速、並行搜尋的結合，最終實現了虛擬試穿等高級功能，增強了買家信心並減少了線上購物的摩擦。

### 學習資源

- 影片：[Shopper's Concierge](https://www.youtube.com/watch?v=LwHPYyw7u6U) | [重點總結](#影片重點摘要shoppers-concierge)

#### 影片重點摘要：Shopper's Concierge

#### 展示功能

| 功能類別 | 影片中具體展示內容 | 對使用者體驗的價值 |
| :--- | :--- | :--- |
| **模糊語意搜尋** | 使用者要求尋找「印有跳舞的人的杯子」，AI 成功定位出一款具有波蘭民俗舞者設計與金邊裝飾的復古馬克杯。 | 解決了傳統關鍵字搜尋難以描述視覺特徵的痛點，讓 AI 能理解藝術風格與設計細節。 |
| **環境感知推薦** | AI 透過攝影機辨識出「居家辦公空間」（書桌、黑椅子、筆電）及「廚房場景」（木製櫥櫃、不鏽鋼水槽）。 | AI 不再只是被動等待指令，而是能主動觀察使用者身處的物理環境，並建議相關商品（如螢幕架、燈具或廚具）。 |
| **深度研究模式 (Deep Research)** | 使用者為 10 歲兒子挑選禮物時，AI 利用 Google 搜尋研究適合的類別，並自動生成查詢語句以篩選最佳禮物。 | 展現了 Multi-agent 協作，AI 能自行蒐集外部資訊並進行決策，最後產出精選結果 (Concierge's Pick)。 |
| **產品細節洞察** | AI 能詳細描述商品特性，例如檯燈具備無線充電與色溫調節功能，且適合裝飾藝術風格（Art Deco）。 | 透過多模態模型的理解力，AI 扮演了專業導購員的角色，主動解釋產品的規格與風格匹配度。 |

#### 技術解析

這段影片展示了幾項關鍵技術的整合應用，使其超越了傳統的聊天機器人：

1.  **向量搜尋與大規模數據處理：**
    系統標榜能在數百萬件商品中進行搜尋。這代表了背後使用了強大的向量資料庫（Vector Search），讓 AI 能將使用者的口語描述轉換為向量，並在海量庫存中快速找到語義最接近的商品（如那款波蘭復古杯）。

2.  **主動式視覺回饋（Visual-Aware Recommendation）：**
    影片中 AI 會主動說出：「我看到一個居家辦公室的配置，桌上有筆電... 你可能會對螢幕架或檯燈有興趣」。這顯示了 Google ADK 處理視覺串流的能力，AI 會持續分析影像序列並將其轉化為上下文資訊，從而觸發更精確的推薦邏輯。

3.  **深度研究 (Deep Research) 的自動化：**
    當使用者發起深度研究時，AI 會利用 Google 搜尋來獲取市場趨勢或禮物分類建議，這是一個典型的 Multi-agent 工作流程。AI 先執行外部研究代理（Research Agent），再將結果回傳給搜尋代理（Search Agent），最終將繁瑣的篩選過程自動化。

4.  **商品特性的精準解讀：**
    AI 能精確描述黑色的 Bright Ezra LED 檯燈，包含其無線充電功能和適用的裝修風格。這代表 AI 不僅是讀取數據表，更能將商品圖片與規格進行「跨模態融合」，以最自然的方式向使用者推銷商品。

總結來說，Shopper's Concierge 2 不僅是一個搜尋工具，它展示了未來 AI 代理如何透過**視覺觀察**、**深度研究**與**自然語言對話**，在電商領域提供極致的個性化服務。

---
此外，雙向串流還有許多可能的現實世界應用：

#### 客戶服務與聯絡中心

這是最直接的應用。該技術可以創建遠超傳統聊天機器人的複雜虛擬代理。

- 使用案例：客戶撥打零售公司的支援專線諮詢瑕疵產品。
- 多模態（影片）：客戶可以說：「我的咖啡機底部漏水了，我讓你看看。」然後他們可以使用手機攝像頭直播問題。AI 代理程式可以利用其視覺能力來識別型號和具體的故障點。
- 即時互動與中斷：如果代理程式說：「好的，我正在為您的 Model X 咖啡機處理退貨，」客戶可以中斷說：「不，等等，是 Model Y Pro，」代理程式可以立即修正其流程而無需重新啟動對話。

#### 電子商務與個人化購物

代理程式可以充當即時、互動的個人購物助理，提升線上零售體驗。

- 使用案例：使用者正在瀏覽時尚網站並希望獲得穿搭建議。
- 多模態（語音與圖像）：使用者可以將一件衣服對準網絡攝像頭並詢問：「你能幫我找一雙適合這條褲子的鞋子嗎？」代理程式分析褲子的顏色和風格。
- 即時互動：對話可以是流暢的來回互動：「給我看一些更休閒的。」……「好的，這雙運動鞋怎麼樣？」……「太棒了，把 10 號藍色的加入購物車。」

#### 現場服務與技術協助

現場工作的技術人員可以使用免持、語音啟動的助手來獲得即時幫助。

- 使用案例：一位 HVAC 技術人員正在現場嘗試診斷複雜的商用空調機組。
- 多模態（影片與語音）：技術人員戴著智慧眼鏡或使用手機，可以將他們的視角串流傳輸給 AI 代理程式。他們可以問：「我聽到這個壓縮機發出奇怪的聲音。你能識別它並調出這個型號的診斷流程圖嗎？」
- 即時互動：代理程式可以逐步引導技術人員，技術人員可以隨時詢問澄清問題或中斷，而無需放下工具。

#### 醫療保健與遠距醫療

代理程式可以作為患者接收、分診和基礎諮詢的第一個接觸點。

- 使用案例：患者使用供應商的應用程式進行關於皮膚狀況的初步諮詢。
- 多模態（影片/圖像）：患者可以安全地分享皮疹的即時影片或高解析度圖像。AI 可以進行初步分析並詢問澄清問題。

#### 金融服務與財富管理

代理程式可以為客戶提供一種安全、互動且資料豐富的方式來管理他們的財務。

- 使用案例：客戶想要查看他們的投資組合併討論市場趨勢。
- 多模態（螢幕共享）：代理程式可以共享其螢幕以顯示圖表、圖形和投資組合績效資料。客戶也可以共享他們的螢幕以指向特定的新聞文章並詢問：「這件事對我的科技股有什麼潛在影響？」
- 即時互動：透過訪問客戶的帳戶資料來分析其當前的投資組合配置。模擬潛在交易對投資組合風險概況的影響。

## 1.2 Gemini Live API 與 Vertex AI Live API

ADK 的雙向串流能力由 Live API 技術提供支援，該技術可透過兩個平台獲得：
**[Gemini Live API](https://ai.google.dev/gemini-api/docs/live)**（透過 Google AI Studio）和 **[Vertex AI Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)**（透過 Google Cloud）。兩者都提供與 Gemini 模型的即時、低延遲串流對話，但服務於不同的開發和部署需求。

在本指南中，我們使用 **「Live API」** 來統稱這兩個平台，僅在討論平台特定功能或差異時才註明「Gemini Live API」或「Vertex AI Live API」。

### 什麼是 Live API？

Live API 是 Google 的即時對話式 AI 技術，可實現與 Gemini 模型的**低延遲雙向串流**。與傳統的請求-響應 API 不同，Live API 建立持久的 WebSocket 連接，支援：

**核心能力：**

- **多模態串流**：即時處理音訊、影片和文字的持續流
- **語音活動檢測 (VAD)**：自動檢測使用者何時說完話，實現自然的輪流對話而無需明確訊號。AI 知道何時開始回應以及何時等待更多輸入
- **即時回應**：以極低的延遲交付類人的語音或文字回應
- **智慧中斷**：允許使用者在 AI 回應中途進行中斷，就像人類對話一樣
- **音訊逐字稿**：使用者輸入和模型輸出的即時逐字稿，無需單獨的逐字稿服務即可實現無障礙功能和對話日誌紀錄
- **對話執行緒管理**：長對話可以透過連線恢復跨越多個連接，API 可在重新連接時保留完整的對話歷史記錄和上下文
- **工具整合**：函式呼叫在串流模式下無縫運作，工具在背景執行，同時對話繼續進行

**原生音訊模型功能：**

- **主動式音訊 (Proactive Audio)**：模型可以根據上下文感知啟動回應，創造更自然的互動，AI 主動提供幫助或澄清（僅限原生音訊模型）
- **情感對話 (Affective Dialog)**：高級模型理解語氣和情感背景，調整回應以匹配對話氛圍和使用者情緒（僅限原生音訊模型）

> [!NOTE] 了解更多
有關原生音訊模型和這些功能的詳細資訊，請參閱 [第 5 部分：音訊和影片 - 主動性和情感對話](part5.md#主動性與情感對話-proactivity-and-affective-dialog)。

**技術規格：**

- **音訊輸入**：16 位元 PCM，16kHz（單聲道）
- **音訊輸出**：16 位元 PCM，24kHz（原生音訊模型）
- **影片輸入**：每秒 1 幀，建議解析度 768x768
- **上下文視窗**：因模型而異（Live API 模型通常為 32k-128k Token）。有關特定限制，請參閱 [Gemini 模型](https://ai.google.dev/gemini-api/docs/models/gemini)。
- **語言**：支援 24 種以上語言並具有自動檢測功能

### Gemini Live API vs Vertex AI Live API

這兩個 API 提供相同的核心 Live API 技術，但在部署平台、身份驗證和企業功能方面有所不同：

| **面向** | **Gemini Live API** | **Vertex AI Live API** |
|--------|-----------------|-------------------|
| **存取** | Google AI Studio | Google Cloud |
| **身份驗證** | API 金鑰 (`GOOGLE_API_KEY`) | Google Cloud 憑證 (`GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`) |
| **最適合** | 快速原型設計、開發、實驗 | 生產部署、企業應用程式 |
| **對話持續時間** | 僅音訊：15 分鐘<br>音訊+影片：2 分鐘<br>配合 [第 4 部分：上下文視窗壓縮](part4.md#live-api-context-window-compression)：無限 | 兩者：10 分鐘<br>配合 [第 4 部分：上下文視窗壓縮](part4.md#live-api-context-window-compression)：無限 |
| **並行對話數** | 基於層級的配額（見 [API 配額](https://ai.google.dev/gemini-api/docs/quota)） | 每個專案最多 1,000 個（可透過配額請求配置） |
| **企業功能** | 基礎 | 進階監控、日誌記錄、SLA、對話恢復 (24h) |
| **設定複雜性** | 極低（僅需 API 金鑰） | 需要 Google Cloud 專案設定 |
| **API 版本** | `v1beta` | `v1beta1` |
| **API 端點** | `generativelanguage.googleapis.com` | `{location}-aiplatform.googleapis.com` |
| **計費** | 透過 API 金鑰追蹤使用情況 | Google Cloud 專案計費 |

> [!NOTE] Live API 參考附註
> **並行對話限制**：基於配額，可能因帳戶層級或配置而異。在 Google AI Studio 或 Google Cloud Console 中檢查您目前的配額。
>
> **官方文件**：[Gemini Live API 指南](https://ai.google.dev/gemini-api/docs/live-guide) | [Vertex AI Live API 概覽](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

## 1.3 ADK 雙向串流：用於構建即時代理應用程式

從頭開始構建即時代理應用程式面臨著重大的工程挑戰。雖然 Live API 提供了底層串流技術，但將其整合到生產應用程式中需要解決複雜的問題：管理 WebSocket 連接和重連邏輯、編排工具執行和回應處理、跨對話持久化對話狀態、協調多模態輸入的並行資料流，以及處理開發與生產環境之間的平台差異。

ADK 將這些挑戰轉化為簡單的宣告式 API。開發人員不再需要花費數月時間構建用於對話執行緒管理、工具編排和狀態持久化的基礎設施，而是可以專注於定義代理程式行為和創造使用者體驗。本節探討 ADK 自動處理的內容，以及為什麼它是構建生產級串流應用程式的建議路徑。

**原生 Live API vs ADK 雙向串流：**

| 功能 | 原生 Live API (`google-genai` SDK) | ADK 雙向串流 (`adk-python` 和 `adk-java` SDK) |
|---------|-----------------------------------|------------------------------------------------------|
| **代理程式框架** | ❌ 不提供 | ✅ 單代理、帶子代理的多代理、順序工作流代理、工具生態系統、部署就緒、評估、安全等（見 [ADK 代理程式文件](https://google.github.io/adk-docs/agents/)） |
| **工具執行** | ❌ 手動工具執行和回應處理 | ✅ 自動工具執行（見 [第 3 部分：工具呼叫事件](part3#工具調用事件)） |
| **連接管理** | ❌ 手動重連和對話恢復 | ✅ 自動重連和對話恢復（見 [第 4 部分：Live API 對話恢復](part4.md#live-api-session-resumption)） |
| **事件模型** | ❌ 自定義事件結構和序列化 | ✅ 帶有中繼資料的統一事件模型（見 [第 3 部分：事件處理](part3.md)） |
| **非同步事件處理框架** | ❌ 手動非同步協調和串流處理 | ✅ `LiveRequestQueue`、`run_live()` 非同步產生器、自動雙向流協調（見 [第 2 部分](part2.md) 和 [第 3 部分](part3.md)） |
| **應用程式級對話持久化** | ❌ 手動實作 | ✅ SQL 資料庫 (PostgreSQL, MySQL, SQLite), Vertex AI, 記憶體內（見 [ADK 對話執行緒文件](https://google.github.io/adk-docs/sessions/)） |

### 平台靈活性

ADK 最強大的功能之一是其對 [Gemini Live API](https://ai.google.dev/gemini-api/docs/live) 和 [Vertex AI Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api) 的透明支援。這種平台靈活性實現了無縫的開發到生產工作流：在本地使用 Gemini API 和免費 API 金鑰進行開發，然後使用企業級 Google Cloud 基礎設施將其部署到生產環境的 Vertex AI——這一切**無需更改應用程式程式碼**，只需更改環境配置。

#### 平台選擇如何運作

ADK 使用 `GOOGLE_GENAI_USE_VERTEXAI` 環境變數來決定使用哪個 Live API 平台：

- `GOOGLE_GENAI_USE_VERTEXAI=FALSE`（或未設置）：透過 Google AI Studio 使用 Gemini Live API
- `GOOGLE_GENAI_USE_VERTEXAI=TRUE`：透過 Google Cloud 使用 Vertex AI Live API

當 ADK 建立 LLM 連接時，底層的 `google-genai` SDK 會讀取此環境變數。切換平台時不需要更改程式碼——只需更改環境配置。

##### 開發階段：Gemini Live API (Google AI Studio)

```bash
# .env.development
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_api_key_here
```

**好處：**

- 使用來自 Google AI Studio 的免費 API 金鑰進行快速原型設計
- 無需 Google Cloud 設定
- 立即進行串流功能實驗
- 開發期間基礎設施成本為零

##### 生產階段：Vertex AI Live API (Google Cloud)

```bash
# .env.production
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_LOCATION=us-central1
```

**好處：**

- 透過 Google Cloud 提供企業級基礎設施
- 進階監控、日誌記錄和成本控制
- 與現有 Google Cloud 服務整合
- 生產級 SLA 和支援
- **無需更改程式碼** - 只需環境配置

透過處理對話執行緒管理、工具編排、狀態持久化和平台差異的複雜性，ADK 讓您專注於構建智慧代理體驗，而不是與串流基礎設施作鬥爭。同樣的程式碼在開發和生產環境中無縫運作，為您提供雙向串流的全部功能，而沒有實作負擔。

## 1.4 ADK 雙向串流架構概覽

既然您了解了 Live API 技術以及為什麼 ADK 能增加價值，讓我們來探討 ADK 實際是如何運作的。本節映射了從您的應用程式透過 ADK 管線到 Live API 並返回的完整資料流，展示了哪些組件處理哪些職責。

您將看到像 `LiveRequestQueue`、`Runner` 和 `Agent` 這樣的關鍵組件如何編排串流對話，而無需您管理 WebSocket 連接、協調非同步流或處理平台特定的 API 差異。

### 高階架構

```mermaid
graph TB
    subgraph "應用程式 (Application)"
        subgraph "客戶端 (Client)"
            C1["Web / 行動裝置"]
        end

        subgraph "傳輸層 (Transport Layer)"
            T1["WebSocket / SSE (例如 FastAPI)"]
        end
    end

    subgraph "ADK"
        subgraph "ADK 雙向串流 (ADK Bidi-streaming)"
            L1[LiveRequestQueue]
            L2[Runner]
            L3[Agent]
            L4[LLM Flow]
        end

        subgraph "LLM 整合 (LLM Integration)"
            G1[GeminiLlmConnection]
            G2[Gemini Live API / Vertex AI Live API]
        end
    end

    C1 <--> T1
    T1 -->|"live_request_queue.send()"| L1
    L1 -->|"runner.run_live(queue)"| L2
    L2 -->|"agent.run_live()"| L3
    L3 -->|"_llm_flow.run_live()"| L4
    L4 -->|"llm.connect()"| G1
    G1 <--> G2
    G1 -->|"yield LlmResponse"| L4
    L4 -->|"yield Event"| L3
    L3 -->|"yield Event"| L2
    L2 -->|"yield Event"| T1

    classDef external fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef adk fill:#f3e5f5,stroke:#4a148c,stroke-width:2px

    class C1,T1 external
    class L1,L2,L3,L4,G1,G2 adk
```


| 開發人員提供： | ADK 提供： | Live API 提供： |
|---------------------|---------------|------------------|
| **Web / 行動裝置**：使用者互動的前端應用程式，處理 UI/UX、使用者輸入捕獲和回應顯示<br><br>**[WebSocket](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket) / [SSE](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events) 伺服器**：即時通訊伺服器（如 [FastAPI](https://fastapi.tiangolo.com/)），管理客戶端連接、處理串流協定，並在客戶端和 ADK 之間路由訊息<br><br>**`Agent`**：自定義 AI 代理程式定義，帶有根據您的應用程式需求量身定制的特定指令、工具和行為 | **[LiveRequestQueue](https://github.com/google/adk-python/blob/29c1115959b0084ac1169748863b35323da3cf50/src/google/adk/agents/live_request_queue.py)**：訊息隊列，緩衝並排序傳入的使用者訊息（文字內容、音訊塊、控制訊號），以便由代理程式有序處理<br><br>**[Runner](https://github.com/google/adk-python/blob/29c1115959b0084ac1169748863b35323da3cf50/src/google/adk/runners.py)**：執行引擎，編排代理程式對話，管理對話狀態，並提供 `run_live()` 串流介面<br><br>**[RunConfig](https://github.com/google/adk-python/blob/29c1115959b0084ac1169748863b35323da3cf50/src/google/adk/agents/run_config.py)**：用於配置串流行為、模態和進階功能的配置<br><br>**內部組件**（自動管理，不供開發人員直接使用）：用於處理管線的 [LLM Flow](https://github.com/google/adk-python/blob/29c1115959b0084ac1169748863b35323da3cf50/src/google/adk/flows/llm_flows/base_llm_flow.py) 和用於協定轉換的 [GeminiLlmConnection](https://github.com/google/adk-python/blob/29c1115959b0084ac1169748863b35323da3cf50/src/google/adk/models/gemini_llm_connection.py) | **[Gemini Live API](https://ai.google.dev/gemini-api/docs/live)**（透過 Google AI Studio）和 **[Vertex AI Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)**（透過 Google Cloud）：Google 的即時語言模型服務，負責處理串流輸入、生成回應、處理中斷、支援多模態內容（文字、音訊、影片），並提供函式呼叫和上下文理解等進階 AI 能力 |

這種架構展示了 ADK 明確的關注點分離：您的應用程式處理使用者互動和傳輸協定，ADK 管理串流編排和狀態，而 Live API 提供 AI 智慧。透過抽象化 LLM 端串流連接管理、事件迴圈和協定轉換的複雜性，ADK 讓您能夠專注於構建代理行為和使用者體驗，而不是串流基礎設施。

## 1.5 ADK 雙向串流應用程式生命週期

ADK 雙向串流將 Live API 對話整合到 ADK 框架的應用程式生命週期中。這種整合創造了一個四階段生命週期，將 ADK 的代理管理與 Live API 的即時串流能力相結合：

- **階段 1：應用程式初始化**（啟動時執行一次）
  - ADK 應用程式初始化
    - 建立 [Agent](https://google.github.io/adk-docs/agents/)：用於與使用者互動、利用外部工具並與其他代理程式協調。
    - 建立 [SessionService](https://google.github.io/adk-docs/sessions/session/#managing-sessions-with-a-sessionservice)：用於獲取或建立 ADK `Session`
    - 建立 [Runner](https://google.github.io/adk-docs/runtime/)：用於為代理程式提供執行環境

- **階段 2：對話執行緒初始化**（每個使用者對話一次）
  - ADK `Session` 初始化：
    - 使用 `SessionService` 獲取或建立 ADK `Session`
  - ADK 雙向串流初始化：
    - 建立 [RunConfig](part4.md) 用於配置 ADK 雙向串流
    - 建立 [LiveRequestQueue](part2.md) 用於將使用者訊息發送給 `Agent`
    - 啟動 [run_live()](part3.md) 事件迴圈

- **階段 3：使用 `run_live()` 事件迴圈進行雙向串流**（每個使用者對話一或多次）
  - 上游 (Upstream)：使用者透過 `LiveRequestQueue` 向代理程式發送訊息
  - 下游 (Downstream)：代理程式透過 `Event` 向使用者回應

- **階段 4：終止 Live API 對話**（每個使用者對話一或多次）
  - `LiveRequestQueue.close()`

**生命週期流程概覽：**

```mermaid
graph TD
    A[階段 1：應用程式初始化<br/>啟動時執行一次] --> B[階段 2：對話執行緒初始化<br/>每個使用者連接執行一次]
    B --> C[階段 3：雙向串流<br/>主動通訊中]
    C --> D[階段 4：終止<br/>關閉對話]
    D -.新連接.-> B

    style A fill:#e3f2fd
    style B fill:#e8f5e9
    style C fill:#fff3e0
    style D fill:#ffebee
```

此流程圖展示了高階生命週期階段及其連接方式。下面的詳細時序圖說明了每個階段內的特定組件和互動。

```mermaid
sequenceDiagram
    participant Client
    participant App as Application Server
    participant Queue as LiveRequestQueue
    participant Runner
    participant Agent
    participant API as Live API

    rect rgb(230, 240, 255)
        Note over App: 階段 1：應用程式初始化 (啟動時執行一次)
        App->>Agent: 1. Create Agent(model, tools, instruction)
        App->>App: 2. Create SessionService()
        App->>Runner: 3. Create Runner(app_name, agent, session_service)
    end

    rect rgb(240, 255, 240)
        Note over Client,API: 階段 2：對話執行緒初始化 (每次使用者連接時)
        Client->>App: 1. WebSocket connect(user_id, session_id)
        App->>App: 2. get_or_create_session(app_name, user_id, session_id)
        App->>App: 3. Create RunConfig(streaming_mode, modalities)
        App->>Queue: 4. Create LiveRequestQueue()
        App->>Runner: 5. Start run_live(user_id, session_id, queue, config)
        Runner->>API: Connect to Live API session
    end

    rect rgb(255, 250, 240)
        Note over Client,API: 階段 3：使用 run_live() 事件迴圈進行雙向串流

        par 上游：使用者透過 LiveRequestQueue 發送訊息
            Client->>App: 使用者訊息 (文字/音訊/影片)
            App->>Queue: send_content() / send_realtime()
            Queue->>Runner: 緩衝的請求
            Runner->>Agent: 處理請求
            Agent->>API: 串流到 Live API
        and 下游：代理程式透過事件回應
            API->>Agent: 串流回應
            Agent->>Runner: 處理回應
            Runner->>App: yield Event (text/audio/tool/turn)
            App->>Client: 透過 WebSocket 轉發事件
        end

        Note over Client,API: (事件迴圈持續直到收到關閉訊號)
    end

    rect rgb(255, 240, 240)
        Note over Client,API: 階段 4：終止 Live API 對話
        Client->>App: WebSocket 斷開連接
        App->>Queue: close()
        Queue->>Runner: 關閉訊號
        Runner->>API: 從 Live API 斷開連接
        Runner->>App: run_live() 退出
    end
```

在接下來的章節中，您將看到每個階段的詳細說明，展示確切的組件建立時機以及它們如何協同運作。理解這種生命週期模式對於構建能夠高效處理多個並行對話的強健串流應用程式至關重要。


### 階段 1：應用程式初始化

這些組件在您的應用程式啟動時建立一次，並在所有串流對話中共享。它們定義了您的代理程式能力、管理對話歷史記錄並編排串流執行。

#### 定義您的代理程式 (Agent)

`Agent` 是您的串流應用程式的核心——它定義了您的 AI 可以做什麼、它應該如何表現，以及由哪個 AI 模型驅動。您可以使用特定的模型、它可以使用的工具（如 Google 搜尋或自定義 API）以及塑造其個性和行為的指令來配置您的代理程式。

<details>
<summary>示範實作：agent.py:10-15</summary>

> Python

```python
"""ADK 雙向串流示範的 Google 搜尋代理程式定義。"""

import os
from google.adk.agents import Agent
from google.adk.tools import google_search

# 支援原生音訊的 Live API 預設模型：
# - Gemini Live API: gemini-2.5-flash-native-audio-preview-12-2025
# - Vertex AI Live API: gemini-live-2.5-flash-native-audio
agent = Agent(
    name="google_search_agent",
    model=os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash-native-audio-preview-12-2025"),
    tools=[google_search],
    instruction="你是一個可以搜尋網頁的有用助手。"
)
```

</details>

代理程式實例是**無狀態且可重用的**——您只需建立它一次，並將其用於所有串流對話。代理程式配置在 [ADK 代理程式文件](https://google.github.io/adk-docs/agents/) 中有詳細介紹。

> [!NOTE] 模型可用性
有關最新支援的模型及其能力的資訊，請參閱 [第 5 部分：理解音訊模型架構](part5.md#了解音訊模型架構)。

> [!NOTE] Agent vs LlmAgent
`Agent` 是 `LlmAgent` 的建議簡寫（兩者都從 `google.adk.agents` 導入）。它們是完全相同的——使用您喜歡的任何一個即可。本指南為了簡潔使用 `Agent`，但在其他 ADK 文件和範例中您可能會看到 `LlmAgent`。

#### 定義您的對話服務 (SessionService)

ADK [Session](https://google.github.io/adk-docs/sessions/session/) 管理跨串流對話的對話狀態和歷史記錄。它儲存和檢索對話資料，實現諸如對話恢復和上下文持久化等功能。

要建立 `Session` 或獲取指定 `session_id` 的現有對話，每個 ADK 應用程式都需要有一個 [SessionService](https://google.github.io/adk-docs/sessions/session/#managing-sessions-with-a-sessionservice)。出於開發目的，ADK 提供了一個簡單的 `InMemorySessionService`，它會在應用程式關閉時丟失 `Session` 狀態。

<details>
<summary>示範實作：main.py:37</summary>

> Python

```python
from google.adk.sessions import InMemorySessionService

# 定義您的對話服務
session_service = InMemorySessionService()
```

</details>

對於生產應用程式，請根據您的基礎設施選擇持久性對話服務：

**在以下情況下使用 `DatabaseSessionService`：**

- 您需要使用 SQLite、PostgreSQL 或 MySQL 進行持久化儲存
- 您正在構建單伺服器應用程式 (SQLite) 或多伺服器部署 (PostgreSQL/MySQL)
- 您希望完全控制資料儲存和備份
- 範例：
    - SQLite: `DatabaseSessionService(db_url="sqlite:///./sessions.db")`
    - PostgreSQL: `DatabaseSessionService(db_url="postgresql://user:pass@host/db")`

**在以下情況下使用 `VertexAiSessionService`：**

- 您已經在使用 Google Cloud Platform
- 您希望使用具有內建可擴展性的託管儲存
- 您需要與 Vertex AI 功能緊密整合
- 範例：`VertexAiSessionService(project="my-project")`

兩者都提供對話持久化能力——根據您的基礎設施和規模要求進行選擇。使用持久性對話服務，即使在應用程式關閉後，`Session` 的狀態也會被保留。有關更多詳細資訊，請參閱 [ADK 對話管理文件](https://google.github.io/adk-docs/sessions/)。

#### 定義您的運行器 (Runner)

[Runner](https://google.github.io/adk-docs/runtime/) 為 `Agent` 提供執行環境。它管理對話流、協調工具執行、處理事件並與對話儲存整合。您在應用程式啟動時建立一個 Runner 實例，並在所有串流對話中重複使用它。

<details>
<summary>示範實作：main.py:50,53</summary>

> Python

```python
from google.adk.runners import Runner

APP_NAME = "bidi-demo"

# 定義您的運行器
runner = Runner(
    app_name=APP_NAME,
    agent=agent,
    session_service=session_service
)
```

</details>

`app_name` 參數是必需的，用於在對話儲存中識別您的應用程式。您應用程式的所有對話都組織在此名稱之下。

### 階段 2：對話執行緒初始化

#### 獲取或建立對話 (Session)

ADK `Session` 提供雙向串流應用程式的「對話執行緒」。就像您不會從頭開始發送每條簡訊一樣，代理程式需要關於正在進行的互動的上下文。`Session` 是專門為跟蹤和管理這些單獨對話執行緒而設計的 ADK 對話物件。

##### ADK `Session` vs Live API 對話 (session)

ADK `Session`（由 SessionService 管理）提供**跨多個雙向串流對話的持久對話儲存**（可以跨越數小時、數天甚至數月），而 Live API 對話（由 Live API 後端管理）是**一個短暫的串流上下文**，僅存在於單個雙向串流事件迴圈期間（通常跨越數分鐘或數小時），我們將在稍後討論。當迴圈啟動時，ADK 使用來自 ADK `Session` 的歷史記錄初始化 Live API 對話，然後隨著新事件的發生更新 ADK `Session`。

> [!NOTE] 了解更多
有關帶有時序圖的詳細比較，請參閱 [第 4 部分：ADK `Session` vs Live API 對話](part4.md#adk-session-vs-live-api-session)。

##### 對話識別碼由應用程式定義

對話由三個參數識別：`app_name`、`user_id` 和 `session_id`。這種三級階層結構實現了多租戶應用程式，每個使用者可以擁有個並行的對話。

`user_id` 和 `session_id` 都是您根據應用程式需求定義的**任意字串識別碼**。ADK 除了對 `session_id` 進行 `.strip()` 之外，不執行任何格式驗證——您可以使用任何對您的應用程式有意義的字串值：

- **`user_id` 範例**：使用者 UUID (`"550e8400-e29b-41d4-a716-446655440000"`)、電子郵件地址 (`"alice@example.com"`)、資料庫 ID (`"user_12345"`) 或簡單識別碼 (`"demo-user"`)
- **`session_id` 範例**：自定義對話 Token、UUID、基於時間戳記的 ID (`"session_2025-01-27_143022"`) 或簡單識別碼 (`"demo-session"`)

**自動生成**：如果您將 `session_id=None` 或空字串傳遞給 `create_session()`，ADK 會自動為您生成 UUID（例如 `"550e8400-e29b-41d4-a716-446655440000"`）。

**組織階層**：這些識別碼按三級結構組織對話：

```text
app_name → user_id → session_id → Session
```

這種設計支援以下場景：

- 不同使用者擁有隔離對話空間的多租戶應用程式
- 擁有個並行聊天執行緒（例如不同主題）的單個使用者
- 基於設備或瀏覽器的對話隔離

##### 建議模式：獲取或建立 (Get-or-Create)

建議的生產模式是先檢查對話是否存在，然後僅在需要時建立。這種方法可以安全地處理新對話和對話恢復：

<details>
<summary>示範實作：main.py:155-161</summary>

> Python

```python
# 獲取或建立對話（處理新對話和重新連線）
session = await session_service.get_session(
    app_name=APP_NAME,
    user_id=user_id,
    session_id=session_id
)
if not session:
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id
    )
```

</details>

這種模式在所有情況下都能正常運作：

- **新對話**：如果對話不存在，會自動建立
- **恢復對話**：如果對話已存在（例如網路中斷後重新連線），則重複使用現有對話並保留完整對話歷史記錄
- **等冪性**：多次呼叫是安全的，不會出錯

**重要提示**：在呼叫具有相同識別碼的 `runner.run_live()` 之前，對話必須存在。如果對話不存在，`run_live()` 將引發 `ValueError: Session not found`。

#### 建立運行配置 (RunConfig)

[RunConfig](part4.md) 定義了此特定對話的串流行為——使用哪些模態（文字或音訊）、是否啟用逐字稿、語音活動檢測、主動性以及其他進階功能。

<details>
<summary>示範實作：main.py:110-124</summary>

> Python

```python
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.genai import types

# 原生音訊模型需要 AUDIO 響應模態以及音訊逐字稿
response_modalities = ["AUDIO"]
run_config = RunConfig(
    streaming_mode=StreamingMode.BIDI,
    response_modalities=response_modalities,
    input_audio_transcription=types.AudioTranscriptionConfig(),
    output_audio_transcription=types.AudioTranscriptionConfig(),
    session_resumption=types.SessionResumptionConfig()
)
```

</details>

`RunConfig` 是**對話特定的**——每個串流對話可以有不同的配置。例如，一位使用者可能偏好純文字回應，而另一位使用者則使用語音模式。有關完整的配置選項，請參閱 [第 4 部分：理解 RunConfig](part4.md)。

#### 建立即時請求隊列 (LiveRequestQueue)

`LiveRequestQueue` 是在串流期間向代理程式發送訊息的通訊通道。它是一個執行緒安全的非同步隊列，緩衝使用者訊息（文字內容、音訊塊、活動訊號）以進行有序處理。

<details>
<summary>示範實作：main.py:163</summary>

> Python

```python
from google.adk.agents.live_request_queue import LiveRequestQueue

live_request_queue = LiveRequestQueue()
```

</details>

`LiveRequestQueue` 是**對話特定且有狀態的**——您為每個串流對話建立一個新隊列，並在對話結束時關閉它。與 `Agent` 和 `Runner` 不同，隊列不能在對話之間重複使用。

> [!WARNING] 每個對話一個隊列
切勿在多個串流對話中重複使用 `LiveRequestQueue`。每次呼叫 `run_live()` 都需要一個新的隊列。重複使用隊列可能會導致訊息順序問題和狀態損壞。
關閉訊號會保留在隊列中（參見 [`live_request_queue.py:59-60`](https://github.com/google/adk-python/blob/fd2c0f556b786417a9f6add744827b07e7a06b7d/src/google/adk/agents/live_request_queue.py#L66-L67)）並終止發送器迴圈（參見 [`base_llm_flow.py:264-266`](https://github.com/google/adk-python/blob/fd2c0f556b786417a9f6add744827b07e7a06b7d/src/google/adk/flows/llm_flows/base_llm_flow.py#L260-L262)）。重複使用隊列會帶入此訊號以及上一個對話中剩餘的任何訊息。

### 階段 3：使用 `run_live()` 事件迴圈進行雙向串流

一旦串流迴圈運行起來，您可以**並行**地向代理程式發送訊息並接收回應——這就是實戰中的雙向串流。代理程式可以在生成回應的同時接收您的新輸入，從而實現自然的基於中斷的對話。

#### 向代理程式發送訊息

在串流對話期間，使用 `LiveRequestQueue` 方法向代理程式發送不同類型的訊息：

<details>
<summary>示範實作：main.py:169-217</summary>

> Python

```python
from google.genai import types

# 發送文字內容
content = types.Content(parts=[types.Part(text=json_message["text"])])
live_request_queue.send_content(content)

# 發送音訊塊 (blob)
audio_blob = types.Blob(
    mime_type="audio/pcm;rate=16000",
    data=audio_data
)
live_request_queue.send_realtime(audio_blob)
```

</details>

這些方法是**非阻塞的**——它們立即將訊息加入隊列而無需等待處理。這使得即使在繁重的 AI 處理期間也能提供流暢、靈敏的使用者體驗。

有關詳細的 API 文件，請參閱 [第 2 部分：使用 LiveRequestQueue 發送訊息](part2.md)。

#### 接收並處理事件

`run_live()` 非同步產生器會隨著代理程式處理輸入和生成回應而持續產生 `Event` 物件。每個事件代表一個離散的發生——部分文字生成、音訊片段、工具執行、逐字稿、中斷或輪流結束。

<details>
<summary>示範實作：main.py:219-234</summary>

> Python

```python
async for event in runner.run_live(
    user_id=user_id,
    session_id=session_id,
    live_request_queue=live_request_queue,
    run_config=run_config
):
    event_json = event.model_dump_json(exclude_none=True, by_alias=True)
    await websocket.send_text(event_json)
```

</details>

事件專為**串流交付 (streaming delivery)**而設計——您接收產生的部分回應，而不僅僅是完整的訊息。這實現了即時 UI 更新和靈敏的使用者體驗。

有關完整的事件處理模式，請參閱 [第 3 部分：使用 run_live() 進行事件處理](part3.md)。

### 階段 4：終止 Live API 對話

當串流對話應結束時（使用者斷開連線、對話完成、發生逾時），優雅地關閉隊列以發出終止 Live API 對話的訊號。

#### 關閉隊列

透過隊列發送關閉訊號以終止串流迴圈：

<details>
<summary>示範實作：main.py:253</summary>

> Python

```python
live_request_queue.close()
```

</details>

這會指示 `run_live()` 停止產生事件並退出非同步產生器迴圈。代理程式會完成任何正在進行的處理，且串流對話會乾淨地結束。

### FastAPI 應用程式範例

這是一個完整的 FastAPI WebSocket 應用程式，展示了與適當的雙向串流整合的所有四個階段。關鍵模式是**上游/下游任務**：上游任務從 WebSocket 接收訊息並將其發送到 `LiveRequestQueue`，而下游任務從 `run_live()` 接收 `Event` 物件並將其發送到 WebSocket。

> [!NOTE] 完整的示範實作
有關支援多模態（文字、音訊、圖像）的生產級實作，請參閱完整的 [`main.py`](https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py) 檔案。

**完整實作：**

```python
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from google.adk.runners import Runner
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google_search_agent.agent import agent

# ========================================
# 階段 1：應用程式初始化 (啟動時執行一次)
# ========================================

APP_NAME = "bidi-demo"

app = FastAPI()

# 定義您的對話服務
session_service = InMemorySessionService()

# 定義您的運行器
runner = Runner(
    app_name=APP_NAME,
    agent=agent,
    session_service=session_service
)

# ========================================
# WebSocket 端點
# ========================================

@app.websocket("/ws/{user_id}/{session_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, session_id: str) -> None:
    await websocket.accept()

    # ========================================
    # 階段 2：對話執行緒初始化 (每個串流對話執行一次)
    # ========================================

    # 建立運行配置 (RunConfig)
    response_modalities = ["AUDIO"]
    run_config = RunConfig(
        streaming_mode=StreamingMode.BIDI,
        response_modalities=response_modalities,
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
        session_resumption=types.SessionResumptionConfig()
    )

    # 獲取或建立對話
    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id
    )
    if not session:
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id
        )

    # 建立即時請求隊列 (LiveRequestQueue)
    live_request_queue = LiveRequestQueue()

    # ========================================
    # 階段 3：活動對話 (並行雙向通訊)
    # ========================================

    async def upstream_task() -> None:
        """從 WebSocket 接收訊息並發送到 LiveRequestQueue。"""
        try:
            while True:
                # 從 WebSocket 接收文字訊息
                data: str = await websocket.receive_text()

                # 發送到 LiveRequestQueue
                content = types.Content(parts=[types.Part(text=data)])
                live_request_queue.send_content(content)
        except WebSocketDisconnect:
            # 客戶端斷開連接 - 通知隊列關閉
            pass

    async def downstream_task() -> None:
        """從 run_live() 接收事件並發送到 WebSocket。"""
        async for event in runner.run_live(
            user_id=user_id,
            session_id=session_id,
            live_request_queue=live_request_queue,
            run_config=run_config
        ):
            # 將事件以 JSON 格式發送到 WebSocket
            await websocket.send_text(
                event.model_dump_json(exclude_none=True, by_alias=True)
            )

    # 同時執行兩個任務
    try:
        await asyncio.gather(
            upstream_task(),
            downstream_task(),
            return_exceptions=True
        )
    finally:
        # ========================================
        # 階段 4：對話終止
        # ========================================

        # 務必關閉隊列，即使發生了異常
        live_request_queue.close()
```

> [!NOTE] 需要非同步上下文
所有 ADK 雙向串流應用程式**都必須在非同步上下文中運行**。此要求源於多個組件：
> - **`run_live()`**：ADK 的串流方法是一個非同步產生器，沒有同步包裝器（與 `run()` 不同）
> - **對話操作**：`get_session()` 和 `create_session()` 是非同步方法
> - **WebSocket 操作**：FastAPI 的 `websocket.accept()`、`receive_text()` 和 `send_text()` 都是非同步的
> - **並行任務**：上游/下游模式需要 `asyncio.gather()` 來進行並行執行
>
> 本指南中的所有程式碼範例都假設您在非同步上下文中運行（例如，在非同步函數或協程內）。為了與 ADK 的官方文件模式保持一致，範例顯示了核心邏輯而沒有包裝函數。

### 關鍵概念

**上游任務 (WebSocket → LiveRequestQueue)**

上游任務持續從 WebSocket 客戶端接收訊息並將其轉發給 `LiveRequestQueue`。這使得使用者可以隨時向代理程式發送訊息，即使代理程式正在生成回應。

<details>
<summary>示範實作：main.py:169-217</summary>

> Python

```python
async def upstream_task() -> None:
    """從 WebSocket 接收訊息並發送到 LiveRequestQueue。"""
    try:
        while True:
            data: str = await websocket.receive_text()
            content = types.Content(parts=[types.Part(text=data)])
            live_request_queue.send_content(content)
    except WebSocketDisconnect:
        pass  # 客戶端斷開連接
```

</details>

**下游任務 (run_live() → WebSocket)**

下游任務持續從 `run_live()` 接收 `Event` 物件並將其發送到 WebSocket 客戶端。這會將代理程式的回應、工具執行、逐字稿和其他事件即時串流給使用者。

<details>
<summary>示範實作：main.py:219-234</summary>

> Python

```python
async def downstream_task() -> None:
    """從 run_live() 接收事件並發送到 WebSocket。"""
    async for event in runner.run_live(
        user_id=user_id,
        session_id=session_id,
        live_request_queue=live_request_queue,
        run_config=run_config
    ):
        await websocket.send_text(
            event.model_dump_json(exclude_none=True, by_alias=True)
        )
```

</details>

**並行執行與清理**

兩個任務使用 `asyncio.gather()` 同時運行，實現了真正的雙向串流。`try/finally` 塊確保即使發生異常也會呼叫 `LiveRequestQueue.close()`，從而最大限度地減少對話資源消耗。

<details>
<summary>示範實作：main.py:238-253</summary>

> Python

```python
try:
    await asyncio.gather(
        upstream_task(),
        downstream_task(),
        return_exceptions=True
    )
finally:
    live_request_queue.close()  # 務必清理
```

</details>

這種模式——具有保證清理能力的並行上游/下游任務——是生產級串流應用程式的基礎。生命週期模式（初始化一次，串流多次）實現了高效的資源利用和明確的關注點分離，應用程式組件保持無狀態且可重用，而對話特定狀態則被隔離在 `LiveRequestQueue`、`RunConfig` 和對話記錄中。

#### 生產考慮因素

此範例顯示了核心模式。對於生產應用程式，請考慮：

- **錯誤處理 (ADK)**：為 ADK 串流事件添加適當的錯誤處理。有關錯誤事件處理的詳細資訊，請參閱 [第 3 部分：錯誤事件](part3.md#錯誤事件)。
    - 透過在關閉期間捕捉 `asyncio.CancelledError` 來優雅地處理任務取消
    - 使用 `return_exceptions=True` 檢查來自 `asyncio.gather()` 的異常 - 異常不會自動傳播
- **錯誤處理 (Web)**：在上游/下游任務中處理特定於 Web 應用程式的錯誤。例如，使用 FastAPI 您需要：
    - 捕捉 `WebSocketDisconnect`（客戶端斷開連接）、`ConnectionClosedError`（連接丟失）和 `RuntimeError`（發送到已關閉的連接）
    - 在發送前使用 `websocket.client_state` 驗證 WebSocket 連接狀態，以防止在連接關閉時出錯
- **身份驗證與授權**：為您的端點實作身份驗證和授權
- **頻率限制與配額**：添加頻率限制和逾時控制。有關並行對話和配額管理的指導，請參閱 [第 4 部分：並行 Live API 對話和配額管理](part4.md#concurrent-live-api-sessions-and-quota-management)。
- **結構化日誌**：使用結構化日誌進行除錯。
- **持久性對話服務**：考慮使用持久性對話服務（`DatabaseSessionService` 或 `VertexAiSessionService`）。有關更多詳細資訊，請參閱 [ADK 對話服務文件](https://google.github.io/adk-docs/sessions/)。

## 1.6 我們將學到什麼

本指南逐步帶領您了解 ADK 的雙向串流架構，遵循串流應用程式的自然流程：訊息如何從使用者上游傳輸到代理程式、事件如何從代理程式下游流向使用者、如何配置對話行為以及如何實作多模態功能。每個部分都專注於串流架構的一個特定組件，並提供您可以立即應用的實用模式：

- **[第 2 部分：使用 LiveRequestQueue 發送訊息](part2.md)** - 了解 ADK 的 `LiveRequestQueue` 如何為處理文字、音訊和控制訊息提供統一的介面。您將理解 `LiveRequest` 訊息模型、如何發送不同類型的內容、管理使用者活動訊號，以及如何透過單個優雅的 API 處理優雅的對話終止。

- **[第 3 部分：使用 run_live() 進行事件處理](part3.md)** - 掌握 ADK 串流架構中的事件處理。學習如何處理不同的事件類型（文字、音訊、逐字稿、工具呼叫）、透過中斷和輪流完成訊號管理對話流、為網絡傳輸序列化事件，以及利用 ADK 的自動工具執行。理解事件處理對於構建靈敏的串流應用程式至關重要。

- **[第 4 部分：理解 RunConfig](part4.md)** - 配置複雜的串流行為，包括多模態互動、智慧主動性、對話恢復和成本控制。了解不同模型上可用的功能，以及如何透過 RunConfig 宣告式地控制您的串流對話。

- **[第 5 部分：如何使用音訊、圖像和影片](part5.md)** - 利用 ADK 的多模態能力實作語音和影片功能。了解音訊規格、串流架構、語音活動檢測、音訊逐字稿，以及構建自然語音 AI 體驗的最佳實踐。

### 先決條件與學習資源

為了在生產環境中構建 ADK 雙向串流應用程式，我們建議具備以下技術的基礎知識：

**[ADK (Agent Development Kit)](https://google.github.io/adk-docs/)**

Google 用於構建具有串流能力的 AI 代理程式的生產級框架。ADK 為對話執行緒管理、工具編排和狀態持久化提供高階抽象，消除了從頭開始實作低階串流基礎設施的需求。

**Live API ([Gemini Live API](https://ai.google.dev/gemini-api/docs/live) 和 [Vertex AI Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api))**

Google 的即時對話式 AI 技術，可實現與 Gemini 模型的低延遲雙向串流。Live API 提供驅動 ADK 串流能力的底層基於 WebSocket 的協定，處理多模態輸入/輸出和自然對話流。

**[Python 非同步編程 (Async Programming)](https://docs.python.org/3/library/asyncio.html)**

Python 對使用 `async`/`await` 語法和 `asyncio` 函式庫的非同步編程的內建支援。ADK 串流建立在非同步產生器和協程之上，需要熟悉非同步函數、等待任務以及使用 `asyncio.gather()` 進行並行執行等概念。

**[Pydantic](https://docs.pydantic.dev/)**

一個使用 Python 型別註解進行資料驗證和設定管理的 Python 函式庫。ADK 廣泛使用 Pydantic 模型來處理結構化資料（如 `Event`、`RunConfig` 和 `Content`），提供型別安全、自動驗證和透過 `.model_dump_json()` 進行的 JSON 序列化。

**[FastAPI](https://fastapi.tiangolo.com/)**

一個現代、高效能的 Python 網頁框架，用於構建具有自動 OpenAPI 文件的 API。FastAPI 對 WebSockets 和非同步請求處理的原生支援使其成為構建 ADK 串流端點的理想選擇。FastAPI 包含在 `adk-python` 套件中，並被 ADK 的 `adk web` 工具用於快速原型設計。也可以使用其他支援 WebSocket 的框架（如 Flask-SocketIO 或 Starlette）。

**[WebSockets](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)**

一種在單個 TCP 連接上提供全雙工（雙向）通訊通道的協定。WebSockets 實現了客戶端和伺服器之間的即時雙向資料流，使其成為串流應用程式的標準傳輸方式。與 HTTP 請求-響應不同，WebSocket 連接是持久的，允許雙方隨時發送訊息。

**[SSE (Server-Sent Events)](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)**

伺服器透過 HTTP 向網頁客戶端推送資料的標準。與 WebSockets 不同，SSE 是單向的（僅限伺服器到客戶端），因此更簡單但靈活性較低。當您不需要客戶端到伺服器的串流（例如當使用者輸入來自單獨的 HTTP POST 請求時），SSE 對於串流代理程式回應很有用。

雖然本指南深入介紹了特定於 ADK 的概念，但熟悉這些底層技術將幫助您構建更強健的生產應用程式。

## 總結

在本次簡介中，您了解了 ADK 如何將複雜的即時串流基礎設施轉變為開發人員友好的框架。我們介紹了 Live API 雙向串流能力的基礎知識，研究了 ADK 如何透過 `LiveRequestQueue`、`Runner` 和 `run_live()` 等抽象化來簡化串流複雜性，並探索了從初始化到對話終止的完整應用程式生命週期。您現在了解了 ADK 如何處理繁重的工作——LLM 端串流連接管理、狀態持久化、平台差異和事件協調——因此您可以專注於構建智慧代理體驗。有了這個基礎，您就可以在接下來的部分中深入研究發送訊息、處理事件、配置對話以及實作多模態功能的細節。

---

[下一部分：第 2 部分：使用 LiveRequestQueue 發送訊息](part2.md) →

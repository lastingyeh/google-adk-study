# ADK 中的雙向串流 (Live)

> 🔔 `更新日期：2026-01-30`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/streaming/

[`ADK 支援`: `Python v0.5.0` | `Experimental`]

ADK 中的雙向 (Bidi) 串流 (Live) 為 AI 代理增加了 [Gemini Live API](https://ai.google.dev/gemini-api/docs/live) 的低延遲雙向語音和視訊互動能力。

透過雙向串流（即 Live 模式），您可以為終端用戶提供自然、類人的語音對話體驗，包括用戶可以使用語音指令中斷代理回應的能力。具備串流功能的代理可以處理文字、音訊和視訊輸入，並提供文字和音訊輸出。

---
### 學習資源
- 影片：[ADK Bidi-streaming in 5 minutes](https://www.youtube.com/watch?v=vLUkAGeLR1k) | [重點總結](#影片重點摘要adk-bidi-streaming-in-5-minutes)

- 影片：[Shopper's Concierge 2 demo](https://www.youtube.com/watch?v=Hwx94smxT_0) | [重點總結](#影片重點摘要shoppers-concierge-2-demo)

## 內容總覽

- **快速上手 (雙向串流)**

    ---

    在此快速上手指南中，您將建立一個簡單的代理，並使用 ADK 中的串流功能來實作低延遲且雙向的語音與視訊通訊。

    - [快速上手 (雙向串流)](../get-started/streaming/quickstart-streaming.md)

- **雙向串流展示應用程式**

    ---

    一個具備正式生產能力的參考實作，展示了具備多模態支援（文字、音訊、圖片）的 ADK 雙向串流。這個基於 FastAPI 的展示專案演示了即時 WebSocket 通訊、自動逐字稿、使用 Google 搜尋的工具調用，以及完整的串流生命週期管理。此範例在整個開發指南系列中被廣泛引用。

    - [ADK 雙向串流展示 (ADK Bidi-streaming Demo)](../../python/agents/pack-bidi-streaming/)

- **部落格文章：ADK 雙向串流視覺指南**

    ---

    使用 ADK 雙向串流開發即時多模態 AI 代理的視覺指南。本文提供了直觀的圖表和插圖，幫助您理解雙向串流的工作原理以及如何構建互動式 AI 代理。

    - [部落格文章：ADK 雙向串流視覺指南 (ADK Bidi-streaming Visual Guide)](https://medium.com/google-cloud/adk-bidi-streaming-a-visual-guide-to-real-time-multimodal-ai-agent-development-62dd08c81399)

- **雙向串流開發指南系列**

    ---

    深入探討 ADK 雙向串流開發的一系列文章。您可以學習基本概念和使用案例、核心 API 以及端到端應用程式設計。

    - [第 1 部分：ADK 雙向串流簡介](dev-guide/part1.md) - 雙向串流基礎、Live API 技術、ADK 架構組件，以及包含 FastAPI 範例的完整應用程式生命週期
    - [第 2 部分：使用 LiveRequestQueue 發送訊息](dev-guide/part2.md) - 上行訊息流、發送文字/音訊/視訊、活動訊號和並行模式
    - [第 3 部分：使用 run_live() 處理事件](dev-guide/part3.md) - 處理事件、處理文字/音訊/逐字稿、自動工具執行以及多代理工作流
    - [第 4 部分：理解 RunConfig](dev-guide/part4.md) - 回應模態、串流模式、工作階段管理、工作階段恢復、上下文視窗壓縮和配額管理
    - [第 5 部分：如何使用音訊、圖片和視訊](dev-guide/part5.md) - 音訊規格、模型架構、音訊轉寫、語音活動檢測以及主動式/情感化對話功能

- **串流工具 (Streaming Tools)**

    ---

    串流工具允許工具（函式）將中間結果串流回代理，代理可以對這些中間結果做出回應。例如，我們可以使用串流工具來監控股票價格的變化，並讓代理對此做出反應。另一個例子是我們可以讓代理監控視訊串流，當視訊串流發生變化時，代理可以報告這些變化。

    - [串流工具 (Streaming Tools)](streaming-tools.md)

- **部落格文章：Google ADK + Vertex AI Live API**

    ---

    本文展示如何使用 ADK 中的雙向串流 (Live) 進行即時音訊/視訊串流。它提供了一個使用 LiveRequestQueue 構建自訂互動式 AI 代理的 Python 伺服器範例。

    - [部落格文章：Google ADK + Vertex AI Live API](https://medium.com/google-cloud/google-adk-vertex-ai-live-api-125238982d5e)

- **部落格文章：使用 Claude Code Skills 加速 ADK 開發**

    ---

    本文演示如何使用 Claude Code Skills 加速 ADK 開發，並以構建雙向串流聊天應用程式為例。了解如何利用 AI 輔助編碼來更快地構建更好的代理。

    - [部落格文章：使用 Claude Code Skills 加速 ADK 開發 (Supercharge ADK Development with Claude Code Skills)](https://medium.com/@kazunori279/supercharge-adk-development-with-claude-code-skills-d192481cbe72)


## 更多說明

### 影片重點摘要：`ADK Bidi-streaming in 5 minutes`
#### ADK Bidi-streaming 核心技術概覽

| 功能分類 | 技術特性與優勢 | 對使用者體驗的提升 |
| :--- | :--- | :--- |
| **原生多模態 (Native Multimodal)** | 採用 Gemini 原生音訊模型，直接理解語音並生成語音，不需經過 STT（語音轉文字）或 TTS（文字轉語音）的中間處理。 | 實現極低延遲，對話極其流暢且自然，如同與真人對談。 |
| **雙向串流 (Bidirectional Streaming)** | 支持即時插嘴偵測（Interruption Detection），使用者可在代理說話時隨時打斷。 | 使用者不必等待 AI 講完即可修正問題，對話節奏完全由使用者主導。 |
| **語音活動偵測 (VAD)** | 內建 VAD 機制，能自動判斷使用者何時說完話並開始回應。 | 消除尷尬的停頓，AI 能精準掌握輪替對話（Turn-taking）的時機。 |
| **視覺感知 (Vision Capabilities)** | 支援每秒處理一張圖像的頻率，讓 AI 持續理解影像序列中的事件。 | 賦予 AI 「眼睛」，能協助進行居家裝修建議或電子商務產品故障排除。 |
| **內建工具整合 (Built-in Tools)** | 內建 Google 搜尋工具，自動處理函數調用（Function Call）與事件處理。 | 讓 AI 能獲取最新資訊、減少幻覺，並根據使用者意圖動態收集背景資訊。 |
| **情感對話 (Affective Dialogue)** | 最新的 Gemini Live API 支援感知使用者的情緒信號，並以此調整回應邏輯。 | 增強 AI 的共情能力，特別適合電商客服等直接面對消費者的服務場景。 |

#### 為什麼選擇 ADK 而非直接使用 Raw API？

對於想要開發「生產級」應用的團隊來說，僅依賴原始的 Live API 是遠遠不夠的。這正是 ADK 展現價值的地方。以下是開發生產級 AI 代理時，ADK 協助解決的痛點：

1.  **簡化架構：** 若直接使用原始 API，開發者必須自行實作代理框架（Agent Framework）、工具執行機制、連線管理、異步事件框架以及會話持久化（Session Persistence）等複雜功能。ADK 則將這些核心功能封裝，讓開發者專注於商業邏輯。
2.  **自動化轉錄：** ADK 內建自動將使用者與代理的語音轉錄為文字的功能，並即時顯示在 UI 上，這不僅讓使用者能確認語音辨識是否正確，也方便隨時回顧對話歷史。
3.  **無縫的 UI 控制：** ADK 提供的各種事件（如插嘴偵測、VAD 事件）可被直接用於精確控制 UI 行為，創造卓越的使用者介面體驗。
4.  **高效的視覺處理：** ADK 能以每秒一張圖的速度上傳影像序列，這對於理解環境變化非常有用，雖然不足以追蹤高速運動，但已足以應付大多數生活場景的理解。

總結來說，ADK Bidi-streaming 是將強大的 Gemini Live API 轉化為商業應用程式的最佳利器，它讓複雜的即時多模態互動變得觸手可及。

---
### 影片重點摘要：`Shopper's Concierge 2 Demo`

#### 核心功能展示

| 展示場景 | 使用者需求 / 互動內容 | AI 執行的動作與結果 |
| :--- | :--- | :--- |
| **模糊語意搜尋** | 尋找「有跳舞的人在上面的杯子」。 | 從千萬件商品中識別意圖，搜尋並找到 88 件相關商品，推薦如「跳舞合唱線馬克杯」等 Top 3 項目。 |
| **個性化贈禮建議** | 幫 10 歲兒子找生日禮物（興趣是玩具）。 | 篩選出 75 件商品，推薦蜘蛛人玩具、對講機及 10 合 1 電力建築玩具。 |
| **深度研究模式 (Deep Research)** | 要求對特定類別進行深入研究。 | 自動將商品分類為 STEM 套裝、動作公仔、戶外冒險裝備等 5 大類，並發送「管家精選 (Concierge's Pick)」。 |
| **視覺環境感知** | AI 透過攝影機觀察使用者的桌面環境。 | 主動辨識出桌子、椅子與筆記型電腦，並詢問是否需要尋找相關的電子產品或家具。 |
| **精準物件識別** | 使用者確認需要尋找電子產品。 | 辨識出螢幕、手機支架、網路攝影機支架等具體物件，並提供購買選項。 |

#### 影片展現的關鍵技術價值

這段 Demo 不僅僅是搜尋引擎的進化，更是 **AI 代理（AI Agent）** 概念的實體化。從影片中我們可以提煉出三個關鍵的演進方向：

1.  **從「關鍵字」轉向「對話式意圖」：**
    使用者不再需要精確的商品名稱。AI 能夠處理如「有跳舞的人在上面的杯子」這種帶有強烈視覺描述的自然語言，這背後仰賴的是 Gemini 模型對大規模數據的跨模態理解能力。

2.  **主動式深度研究（Deep Research）：**
    當使用者面對大量搜尋結果感到困惑時，AI 能主動執行「Deep Research」。它不只是列出清單，而是進行**歸納與分類**（如 STEM 套裝、創意手工套裝等），並主動推送精選結果，極大地縮短了消費者的決策路徑。

3.  **多模態視覺融合（Visual Awareness）：**
    這是 Demo 中最驚艷的部分。AI 能夠「看見」使用者的實體空間（如桌上的筆電），並根據空間背景主動推廣相關商品（如螢幕、支架）。這證明了 ADK Bidi-streaming 處理即時視覺串流的能力，讓 AI 能夠理解物理世界的上下文環境。

4.  **處理海量數據的規模感：**
    系統能即時在 **1,000 萬件商品** 的數據庫中進行檢索與處理，這展示了企業級 RAG（檢索增強生成）與即時語音 API 結合後的強大性能。

總結來說，這段影片展示了未來的電商體驗：AI 不再只是一個搜尋框，而是一個有眼睛、能對話、且具備專業研究能力的私人購物管家。

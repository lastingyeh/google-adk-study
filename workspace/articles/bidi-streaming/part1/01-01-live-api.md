歡迎回到這份深度技術筆記。我是你們的資深技術導師。在前幾次的討論中，我們已經解構了 ADK 的四大生命週期與事件處理。今天，我們要將視野放大，探討驅動這一切的底層心臟：**Live API 平台**。

在 ADK 的架構脈絡下，Live API 不僅僅是一個接口，它是 Google 實作「低延遲雙向串流」的核心技術平台。它分為 **Gemini Live API** 與 **Vertex AI Live API** 兩個版本，雖然共享相同的技術基因，但在企業級架構中扮演著截然不同的角色。

### 📌 Live API 平台學習地圖

1.  **平台核心技術定義**：WebSocket 全雙工通訊的本質。
2.  **雙平台對比分析**：Gemini Live API 與 Vertex AI Live API 的權衡實務。
3.  **模型架構抉擇**：原生音訊模型 vs. 半串聯模型的深層邏輯。
4.  **連線與會話管理**：解構物理連線與邏輯會話的生存週期。
5.  **生產環境配置**：從開發到雲端部署的透明切換策略。

---

### 一、 技術本質：為什麼是 WebSocket？

Live API 代表了 AI 互動模式的根本轉變：從「發送電子郵件」演進到「撥打電話」。傳統 API 使用 HTTP 的請求-回應模式，而 Live API 建立持久的 **WebSocket 連線**，這賦予了平台以下核心能力：

*   **全雙工通訊**：資料（文字、音訊、視訊）可以同時在上游與下游流動，無需等待。
*   **低延遲多模態處理**：直接處理 16kHz 的 PCM 音訊與每秒 1 幀 (1 FPS) 的視訊影格，實現類人的亞秒級回應。
*   **環境感知**：模型能透過視覺串流觀察物理空間（如書桌、電腦），主動觸發推薦邏輯。

---

### 二、 雙平台實戰對比：Gemini vs. Vertex AI

對於開發者來說，選擇哪個平台決定了你的認證方式、成本結構與擴展上限。ADK 的強大之處在於它提供了**平台靈活性**，讓你可以用同一套代碼在兩個平台間無縫切換。

| 維度           | Gemini Live API (Google AI Studio) | Vertex AI Live API (Google Cloud) |
| :------------- | :--------------------------------- | :-------------------------------- |
| **最適合場景** | 快速原型設計、開發實驗             | 生產部署、企業級應用程式          |
| **認證機制**   | API 金鑰 (GOOGLE_API_KEY)          | Google Cloud 憑證 (IAM)           |
| **連線限制**   | 音訊 15min / 視訊 2min             | 所有會話 10min                    |
| **配額管理**   | 基於層級 (1,000 並行/第2層)        | 基於專案 (1,000 並行/需申請)      |
| **企業功能**   | 基礎能力                           | 進階監控、日誌、SLA、24h 恢復     |

**我們如何切換？** 關鍵在於環境變數 `GOOGLE_GENAI_USE_VERTEXAI`。當設為 `TRUE` 時，ADK 會透明地將底層連線導向 Google Cloud 的專屬端點，而無需更動任何業務代碼。

---

### 三、 模型架構的深度抉擇：原生音訊 vs. 半串聯

在 Live API 平台之上，選擇不同的「模型架構」會直接影響 AI 的「人味」與「可靠性」。這是架構設計中最關鍵的一環。

#### 1. 原生音訊模型 (Native Audio Models)
這是真正的端到端架構。模型不經過文字轉換，直接聽取音訊並產生音訊。
*   **優勢**：語調極其自然，支援**情感對話**（偵測你的沮喪或開心）與**主動音訊**（AI 決定何時該插話）。
*   **限制**：僅支援 `AUDIO` 回應模式，初始回應可能較慢，不支援純文字輸出。

#### 2. 半串聯模型 (Half-Cascade Models)
這是一種混合架構，音訊輸入是原生的，但輸出則結合了文字轉語音 (TTS) 技術。
*   **優勢**：在生產環境中非常穩定，工具執行 (Function Call) 較穩健，且支援 `TEXT` 回應模式，在純文字場景效能更佳。
*   **關鍵點在於**：如果你需要極高的工具精準度，半串聯是首選；如果你追求情感共鳴，原生音訊則是未來。

---

### 四、 邏輯具象化：連線 (Connection) 與 會話 (Session)

很多開發者會混淆這兩個概念。理解它們的差異是解決「為什麼連線會斷開」的鑰匙。

*   **連線 (Connection)**：物理性的 WebSocket 連結，受限於約 10 分鐘的網路限制。
*   **會話 (Session)**：邏輯上的對話上下文（包括對話歷史與工具狀態）。

**這代表什麼？** 當網路斷開時，物理連線消失了，但邏輯會話還在。ADK 透過 **會話恢復 (Session Resumption)** 技術，自動在背景快取恢復句柄 (Resumption handle)，當偵測到連線中斷時，它會透明地發起新的連線並接回舊的會話，使用者完全不會察覺。

#### ⚡ 代碼即真理：RunConfig 中的平台自動適應
在 `bidi-demo` 中，我們可以看到導師如何根據模型名稱自動配置平台行為：

```python
# [導師點評]：這裡體現了 ADK 如何應對模型架構差異
# 我們透過檢測模型名稱中是否包含 "native-audio" 來決定配置

model_name = agent.model
is_native_audio = "native-audio" in model_name.lower()

if is_native_audio:
    # [關鍵在於]：原生音訊模型必須使用 AUDIO 模式
    run_config = RunConfig(
        streaming_mode=StreamingMode.BIDI,
        response_modalities=["AUDIO"], # 限制
        # 僅原生模型支援的功能
        proactivity=types.ProactivityConfig(proactive_audio=True) if proactivity else None,
        enable_affective_dialog=affective_dialog if affective_dialog else None,
        session_resumption=types.SessionResumptionConfig(), # 必備自動重連
    )
else:
    # 半串聯模型為了效能，我們預設使用 TEXT
    run_config = RunConfig(
        streaming_mode=StreamingMode.BIDI,
        response_modalities=["TEXT"],
        session_resumption=types.SessionResumptionConfig(),
    )
```

---

### 五、 知識收斂：生產環境的配額規劃

當你將應用程式推向市場時，Live API 的「並行會話」配額是你的硬性邊界。

*   **Gemini (Studio)** 的配額隨層級大幅擴展（50 到 1,000 個會話），適合快速擴張的使用者群。
*   **Vertex AI (Cloud)** 的連線建立速度較慢（每分鐘 10 個），但穩定性更高，適合企業內部或預期增長穩定的環境。

**實戰建議**：若預期尖峰時段會超過配額，應採用「會話池與佇列」模式，在應用程式層級緩衝使用者的連線請求，而非讓 API 直接報錯。

---

### 💡 導師總結

Live API 平台是實現「未來 AI」的基石。它不只提供了音訊或視訊的管道，更透過 **上下文視窗壓縮 (Context Window Compression)** 解決了長對話的記憶問題，讓會話持續時間從數分鐘變為「無限」。

身為開發者，你的任務是善用 ADK 提供的抽象層，在 `Gemini` 的靈活性與 `Vertex AI` 的穩定性之間找到平衡，並根據業務需求（是需要情感互動還是穩定的工具執行）選擇正確的模型架構。

🏷️ `live-api-platform`, `gemini-live`, `vertex-ai-live`, `bidi-architecture`, `native-audio`

**延伸學習資源**：
*   有關 VAD 與活動訊號的細節，請參閱《第 5 部分：語音活動檢測》。
*   有關配額增加的具體流程，請至 Google Cloud 主控台的「配額」頁面。
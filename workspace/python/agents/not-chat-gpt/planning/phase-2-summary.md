# Phase 2 Summary

## 3.1 Grounding

這是一個非常關鍵的實作發現！在開發基於 Google Gen AI SDK (ADK) 的 Agent 時，「單一特殊工具限制」確實是一個容易踩到的坑。

以下為你整理的 **3.1 實作心得**，我將其結構化為開發挑戰、解決方案與架構建議，方便你記錄在專案文檔中。

---

## 💡 實作心得：3.1 Google Search Grounding 整合

在 Phase 2 的工具整合過程中，最核心的學習點在於理解 **ADK 工具的使用限制**，以及如何透過「代理人封裝」來繞過這些硬性約束。

### 1. 關鍵技術挑戰：工具互斥限制

在實作初期，我嘗試直接將 `Google Search` 與其他自定義工具（如檔案讀寫、計算邏輯）同時放入同一個 Agent 的 `tools` 陣列中，導致系統報錯。

> **⚠️ 核心限制 (Limitations for ADK Tools):**
> 以下特定工具在單一 Agent 物件中具有**排他性**，無法與其他工具共存：
>
> * **Code Execution** (Gemini API)
> * **Google Search** (Gemini API)
> * **Vertex AI Search**
>
>

### 2. 解決方案：Agent 工具化 (Agent as a Tool)

為了解決上述限制，我採取了**「解耦封裝」**的策略。不再強求一個 Agent 成為「全能工具箱」，而是改用以下結構：

* **獨立封裝**：建立一個專門負責搜尋的 `SearchAgent`，該 Agent 僅配置 `Google Search` 工具。
* **工具引用**：利用 `AgentTool` 功能，將 `SearchAgent` 包裝成一個工具，再提供給主控 Agent（如 `StrategicPlannerAgent`）呼叫。

**調整後的架構邏輯：**

1. **Main Agent**: 負責理解需求，決定何時需要「搜尋」。
2. **Search Tool (Wrapper)**: 實際上是一個背後跑著 `SearchAgent` 的接口。
3. **Result**: 搜尋結果回傳給 Main Agent 進行整合與回覆。

### 3. 實作效益與驗證

* **穩定性提升**：遵循官方工具約束後，解決了 API 調用衝突，Agent 能正確觸發網路搜尋。
* **引用透明化**：成功保留了 Grounding 的原始優勢，回傳結果包含完整的引用來源 (Citations)，增強了資訊的可信度。
* **模組化設計**：未來若需更換搜尋引擎或增加 Code Execution 模組，只需替換對應的子 Agent，不需更動主邏輯。

---

### 🚀 經驗小結

> 「不要試圖打造一個會所有技能的超人 Agent，而是要建立一個知道如何指揮專家的團隊。」

這次錯誤讓我深刻體會到，在設計複雜 Agent 系統時，**「單一職責原則」** 不僅是軟體工程的好習慣，更是避開模型 API 硬體限制的必要手段。

---

## 3.2 Code Execution (參考 Day 21: code-calculator)

從單一任務的角度來看，為了一個簡單的 123 * 456 計算就啟用 StrategicPlannerAgent，確實有「殺雞用牛刀」的感覺。ConversationAgent 看

起來就足以應付。

不過，從整體架構設計和未來擴展性的角度來看，這個決策是合理且有遠見的。原因如下：

1. 職責分離 (Separation of Concerns)
    這是最重要的原因。在這個架構中，兩個 Agent 有明確的分工：

    ConversationAgent:

    職責：負責純粹的對話、聊天、問答和資訊檢索 (Grounding)。
    特性：輕量、快速、安全。它不應該持有高風險的工具。
    StrategicPlannerAgent:

    職責：負責所有需要執行工具 (Tool Use) 的複雜任務，例如程式碼執行、檔案操作、API 呼叫等。它需要思考、規劃步驟並執行。
    特性：功能強大，但啟動和運行的成本也較高。
    將 BuiltInCodeExecutor 放在 StrategicPlannerAgent 中，是嚴格遵守了這個職責分離的原則。即使是簡單的計算，其本質仍然是「執行程式碼」，這個行為就應該由專門負責工具執行的 Agent 來處理。

2. 安全性考量 (Security)
    如我們先前討論的，程式碼執行是高風險操作。將這個能力嚴格限制在一個特定的 Agent (StrategicPlannerAgent) 和一個特定的模式 (#think) 中，可以：

    最小化攻擊面：讓 ConversationAgent 保持「純淨」，不接觸任何可能被利用來執行惡意程式碼的工具。
    簡化安全審計：當需要檢查安全漏洞時，只需要專注於 StrategicPlannerAgent 的邏輯，而不用擔心 ConversationAgent 也可能成為入口。
3. 一致性與可預測性 (Consistency & Predictability)
    這個設計讓系統的行為非常一致：

    只要是純對話，就是 ConversationAgent。
    只要需要動用工具，就是 StrategicPlannerAgent。
    這種一致性讓開發者和使用者都能輕易預測系統的行為，減少了「什麼情況下會觸發哪個 Agent」的混亂。

4. 未來的擴展性 (Scalability)
    現在可能只有簡單的計算，但未來呢？

    #think 畫一張圖表顯示這份 CSV 的數據分佈
    #think 呼叫外部 API 取得天氣資訊，並轉換成華氏溫度
    #think 結合檔案 A 和檔案 B 的內容，產生一份總結報告
    這些複雜的任務都需要一個能夠規劃步驟並組合使用多種工具的 Agent。StrategicPlannerAgent 正是為此而生。

    如果今天為了簡單計算而在 ConversationAgent 開了特例，那麼未來當任務變複雜時，你就得不斷地在 ConversationAgent 中添加更多的工具和邏輯，最終會讓它變得臃腫不堪，並打破了原有的職責分離設計。

### 結論

所以，雖然對於 123 * 456 這種簡單任務來說，使用 StrategicPlannerAgent 看似「小題大作」，但這其實是為了維護一個清晰、安全、可擴展的架構而做出的正確取捨。

你可以把它想像成公司的部門分工：

- 客服部 (ConversationAgent): 負責與客戶溝通。
- 工程部 (StrategicPlannerAgent): 負責解決需要動手操作的技術問題。
- 即使客戶只是問了一個簡單的技術問題（「重啟能解決嗎？」），客服也應該將這個問題轉交給工程部來確認，而不是自己上手操作客戶的設備。這確保了流程的標準化和責任的清晰。

# Workflow Orchestration: 工作流編排與執行控制

在多代理（Multi-agent）架構的設計中，**「秩序」** 往往比「智慧」更重要。當我們面對一個需要多步驟處理、且步驟間存在嚴格邏輯依賴的任務時，最常見的錯誤就是試圖讓一個全能的代理（Omnipotent Agent）處理所有細節，或者依賴 LLM 自行決定下一步（非確定性路由）。

本章將深入探討 Google ADK 提供的三大核心工作流代理：`SequentialAgent`（順序）、`ParallelAgent`（並行）與 `LoopAgent`（循環），協助開發者建立確定性高、可預測且高效的 AI 應用。

---

## 1. SequentialAgent：順序執行邏輯

`SequentialAgent` 作為 Google ADK 的核心工作流代理，提供了一種 **確定性(Deterministic)** 的編排方式。它不具備 LLM 的推理能力，但它擁有最強大的特性：確保任務 A 必須在任務 B 之前完成，並確保 A 的產出能安全地傳遞給 B。

### 情境：將複雜邏輯拆解為單向流水線，而非單一 Agent 承擔

在設計 AI 系統時，應遵循「單一職責原則」。如果一個流程中存在明確的先後順序（例如：獲取網頁 -> 摘要內容），將其拆解為多個專用代理並透過 `SequentialAgent` 串聯，能顯著提升系統的穩定性。

#### 程式碼範例（Bad vs. Better）

```python
# ❌ Bad: 在單一 Agent 中處理所有步驟
# 缺點：指令過於複雜，LLM 容易在多個工具調用間遺失上下文，且難以對各步驟進行獨立測試。
agent = LlmAgent(
    name="OmniSummarizer",
    instruction="先獲取網頁內容，然後進行摘要。如果失敗了，嘗試報告錯誤。",
    tools=[get_page_tool, summarize_tool]
)

# ✅ Better: 使用 SequentialAgent 建立確定的流水線
# 優點：步驟明確，每個 Agent 專注於單一任務。獲取失敗時會直接終止或觸發預期行為，流程 100% 可預測。
fetcher = LlmAgent(name="Fetcher", tools=[get_page_tool], output_key="raw_content")
summarizer = LlmAgent(name="Summarizer", instruction="請根據 {raw_content} 進行摘要")

pipeline = SequentialAgent(
    sub_agents=[fetcher, summarizer]
)
```

#### 底層原理探討與權衡
`SequentialAgent` 的本質是 **編排 (Orchestration)** 而非推理。它的執行邏輯是 Python/TypeScript 等宿主語言的確定性迴圈。
*   **權衡**：它失去了動態路由的靈活性（無法根據中途結果跳轉到任意步驟），但換取了高可靠性。在生產環境中，對於標準化的 ETL 或代碼審查流程，可靠性通常優先於靈活性。

---

## 2. ParallelAgent：併發代理執行與多代理規劃

在構建複雜的 GenAI 應用時，我們經常面臨效能與反應速度的挑戰。如果您的任務包含多個互不依賴的子任務（例如：同時向多個數據源檢索資訊、並行執行程式碼測試、或是對同一份輸入進行不同維度的分析），那麼「依序執行」無疑是對資源與時間的巨大浪費。

`ParallelAgent` 正是為了解決這一問題而生的「編排者」。它能確保您的子代理們同時開工，並在最終將戰果彙整。

### 情境：優先使用 `ParallelAgent` 處理無相依性的獨立任務

當多個代理程式的輸入互不依賴，且執行結果最終需要被統一彙整時，應將其置於 `ParallelAgent` 中。這能將總執行時間從「所有任務之和」降低至「耗時最長的單一任務」。

#### 程式碼範例（Bad vs. Better）

```python
# ❌ Bad: 依序執行獨立的研究任務
# 這種做法會導致線性增長的延遲，User 必須等待任務 A 完成才能開始任務 B。
research_pipeline = SequentialAgent(
    sub_agents=[
        LlmAgent(name="WeatherExpert", instructions="分析天氣數據..."),
        LlmAgent(name="MarketExpert", instructions="分析市場趨勢..."),
        LlmAgent(name="NewsExpert", instructions="收集即時新聞...")
    ]
)

# ✅ Better: 使用 ParallelAgent 同時啟動
# 任務同時觸發，I/O 等待時間重疊，顯著提升反應速度。
from google.adk.agents import ParallelAgent, SequentialAgent

concurrent_research = ParallelAgent(
    name="ConcurrentResearch",
    sub_agents=[
        LlmAgent(name="WeatherExpert", output_key="weather_data", ...),
        LlmAgent(name="MarketExpert", output_key="market_data", ...),
        LlmAgent(name="NewsExpert", output_key="news_data", ...)
    ]
)

# 通常配合 SequentialAgent 進行結果彙整
final_report_agent = SequentialAgent(
    sub_agents=[
        concurrent_research,
        LlmAgent(name="Aggregator", instructions="根據 {weather_data}, {market_data}, {news_data} 撰寫總結。")
    ]
)
```

#### 底層原理探討與權衡
*   **分支隔離 (Branching)**：ADK 為每個並行分支創建獨立的 `InvocationContext.branch`。這保證了各個代理的對話歷史（History）不會交織干擾。
*   **狀態共享 (Shared State)**：雖然分支隔離，但它們共享同一個 `session.state`。透過 `output_key`，子代理能將結果寫入共享區，供後續代理讀取。

---

## 3. LoopAgent：持續迭代優化與自我修正

在生成式 AI 的應用開發中，單次 Prompt 的輸出往往難以達到生產環境要求的完美程度。正如軟體工程中的「重構」是提升代碼質量的必經之路，AI Agent 也需要一種機制來自我審查、反思並修正。Google ADK 提供的 `LoopAgent` 便是為此而生，它透過確定性的迴圈結構，讓代理能夠在達成預期目標前，進行有節制的反覆優化。

### 情境：明確定義結束條件，優先設置「安全閥」而非僅依賴邏輯判斷

`LoopAgent` 本身是不具備意識的確定性執行器。如果你沒有為其設定明確的終止機制，它會像沒有邊界條件的 `while(true)` 一樣消耗大量的 API 配額。即使你信任 LLM 的邏輯判斷能力，也應該始終配置一個物理上限（Max Iterations）作為最後的防線。

#### 程式碼範例（Bad vs. Better）

```python
# ❌ Bad: 僅依賴子代理的邏輯判斷，缺乏物理保護機制
# 如果子代理始終認為輸出不夠完美，或者陷入邏輯死循環，將導致昂貴的費用支出
loop_agent = LoopAgent(
    name="RefinementLoop",
    sub_agents=[CriticAgent, EditorAgent]
    # 缺少 max_iterations，風險極高
)

# ✅ Better: 結合 max_iterations 安全閥與動態退出邏輯
# 設置物理上限 5 次，並在子代理達成目標時主動發出退出訊號
loop_agent = LoopAgent(
    name="RefinementLoop",
    sub_agents=[CriticAgent, EditorAgent],
    max_iterations=5  # 強制物理上限，保護資源
)

# 在子代理（EditorAgent）的工具中，當品質達標時執行：
# tool_context.actions.escalate = True
# 這會立即終止 LoopAgent 的執行
```

#### 底層原理探討與權衡
`LoopAgent` 的設計初衷是「確定性」的流程管理。它與 `SequentialAgent` 的區別在於它會重複執行 `sub_agents` 列表。在底層，ADK 會追蹤 `times_looped` 狀態。當達到 `max_iterations` 時，事件迴圈會停止產生新的執行步驟。設置過小的次數可能導致任務半途而廢，設置過大則增加成本。對於大多數修訂任務，3 到 5 次通常是性價比最高的選擇。

---

## 4. 適用場景與拇指法則 (Rule of Thumb)

*   **拇指法則 1**：當任務具有明確的先後順序（如 ETL），且需要高度可預測性時，優先使用 `SequentialAgent`。
*   **拇指法則 2**：當任務包含多個互不依賴的子任務（如多源檢索），且對延遲敏感時，優先使用 `ParallelAgent`。
*   **拇指法則 3**：當任務需要反覆優化（如代碼重構、文章潤色）直到達成特定品質標準時，使用 `LoopAgent` 並務必設定 `max_iterations`。
*   **拇指法則 4**：在並行執行中，務必為每個子代理指定唯一的 `output_key` 以避免狀態覆蓋。
*   **拇指法則 5**：將 `ParallelAgent` 嵌套於 `SequentialAgent` 中（展開-收集模式）是處理複雜分析任務的最佳實踐。

---

## 5. 延伸思考 (Q&A)

**1️⃣ 問題一**：如果 `SequentialAgent` 中的某個中間步驟失敗了（例如 API 報錯），整個流程會如何？

**👆 回答**：預設情況下，ADK 的 `SequentialAgent` 採用「Fail Fast」策略。如果子代理拋出未捕獲的異常，執行會立即中斷，這能防止錯誤的數據傳遞到後續步驟。在生產環境中，建議在 `LlmAgent` 或 `CustomTool` 層級處理重試邏輯，或使用 `LoopAgent` 進行錯誤修復。

**2️⃣ 問題二**：ParallelAgent 的子代理數量有限制嗎？

**👆 回答**：技術上受限於底層運算資源與 LLM API 的 Quota（配額）。每個子代理都會發起獨立的 API 請求，如果您同時啟動 100 個 `LlmAgent`，極大機率會觸發 `Rate Limit`。建議在設計時評估 API 的併發上限，並考慮使用 Batch API 或具備佇列管理能力的 Runner。

**3️⃣ 問題三**：如果 `LoopAgent` 達到了 `max_iterations` 但任務仍未完成，該如何處理？

**👆 回答**：這通常意味著 Prompt 需要優化，或者是任務過於複雜。在生產環境中，你應該在 `LoopAgent` 結束後加入一個「最後檢查點（Final Check）」。如果狀態顯示任務未達標，可以觸發「人工介入（Human-in-the-loop）」或將當前狀態記錄為失敗並發出警報，而不是無限制地增加迭代次數。

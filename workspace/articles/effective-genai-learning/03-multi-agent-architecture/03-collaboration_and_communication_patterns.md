# Collaboration & Communication Patterns: 代理人協作與通訊模式

在多代理系統（Multi-Agent Systems, MAS）的設計中，代理人（Agent）並非孤島。它們需要共享知識、達成共識、解決衝突，並在資源有限的環境中進行談判。本章將探討如何利用 Google ADK 的 `session.state`、`MemoryService` 以及各種協作模式，建立高效且健壯的溝通機制。

---

## 1. Blackboard Pattern：黑板模式與狀態管理

在軟體架構的設計中，當系統面對「定義模糊」且「無單一專家能解決」的複雜問題時，我們必須避免讓代理人間陷入混亂的點對點通訊。**黑板模式（Blackboard Pattern）** 是將「問題狀態」與「解題邏輯」徹底解耦的高階協作模式。

### 情境：針對複雜遞增型問題，優先使用 Blackboard 模式而非點對點通訊

在處理如醫療診斷或複雜欺詐檢測等場景時，單一代理人無法掌握全貌。若採用點對點通訊，通訊路徑會隨代理人數呈 $O(N^2)$ 爆炸，且狀態難以追蹤。

#### 程式碼範例（Bad vs. Better）

```python
# ❌ Bad: 混亂的點對點通訊 (Peer-to-Peer Spaghetti)
# 代理人間必須互相知道對方的存在，任何一方異動都會造成連鎖反應。
# 代理人 A 必須知道要傳給 B，B 必須知道要傳給 C
async def process_task(data):
    # 高度耦合，難以增加新專家
    result_a = await specialist_a.run(data)
    if result_a.needs_b:
        result_b = await specialist_b.run(result_a)
        # ...

# ✅ Better: 使用 ADK `session.state` 實作 Blackboard 模式
# 利用 `session.state` 作為共享黑板，代理人僅需對狀態變更負責。
# 定義一個作為「黑板」的事實庫 (事實上 session.state 就是最佳實作)
# Specialist A: 觀察狀態並貢獻事實
class SymptomAgent(LlmAgent):
    async def _run_async_impl(self, ctx):
        # 1. 從黑板讀取初始資料
        patient_data = ctx.session.state.get("patient_history")
        # 2. 發布初步假設到黑板
        ctx.session.state["hypotheses"] = {
            "symptom": "fever",
            "confidence": 0.8,
            "timestamp": time.time()
        }
        yield Event(content="症狀分析已更新至黑板。")

# Specialist B: 偵測到相關事實後介入
class DiagnosisAgent(LlmAgent):
    async def _run_async_impl(self, ctx):
        # 僅當黑板出現 "fever" 時才觸發
        if ctx.session.state.get("hypotheses", {}).get("symptom") == "fever":
            # 進行深度診斷並更新黑板
            ctx.session.state["final_diagnosis"] = "Viral Infection"
```

#### 底層原理探討與權衡
*   **優點**：具備極佳的 **靈活性 (Flexibility)**。你可以隨時在不修改現有邏輯的情況下，增加一個新的「化驗專家」進來觀察黑板。此外，黑板本身就是天然的 **審核軌跡 (Audit Trail)**，能完整呈現解決方案是如何從碎片演化成定論的。
*   **權衡**：延遲較高。因為每次寫入與評估都需要中央仲裁，且 Controller 可能成為吞吐量的瓶頸。

---

## 2. Knowledge Sharing：知識共享與記憶服務

在構建多代理人系統時，確保代理人間資訊的一致性是架構設計中最棘手的挑戰之一。當多個代理人獨立作業卻又共享同一個目標時，若缺乏有效的知識同步機制，容易導致「資訊孤島」或執行邏輯衝突。

### 情境：優先使用共享 `MemoryService` 而非重複注入上下文

在多代理人環境中，當多個代理人需要訪問相同的背景知識（如產品手冊或用戶歷史）時，開發者常犯的錯誤是將這些知識手動注入到每個代理人的 System Instruction 中。這不僅浪費 Token，更會導致知識更新時的不一致。

#### 程式碼範例（Bad vs. Better）

```python
# ❌ Bad: 將相同知識重複注入多個代理人
# 缺點：Token 消耗高、難以維護、知識更新不同步
agent_a = LlmAgent(
    name="SupportAgent",
    instruction="你是客服，請根據以下手冊回答：[手冊內容 A...]"
)
agent_b = LlmAgent(
    name="BillingAgent",
    instruction="你是帳務專員，請根據以下手冊回答：[手冊內容 A...]"
)

# ✅ Better: 使用共享 MemoryService 並掛載 LoadMemory 工具
# 優點：節省 Token、知識集中管理、按需檢索
from google.adk.tools import load_memory
from google.adk.memory import VertexAiMemoryBankService

# 建立共享的記憶服務
shared_memory = VertexAiMemoryBankService(
    project="my-project",
    agent_engine_id="shared-knowledge-base"
)

# 代理人透過工具按需查詢
agent_a = LlmAgent(
    name="SupportAgent",
    instruction="若需產品資訊，請使用 load_memory 工具查詢。",
    tools=[load_memory]
)
agent_b = LlmAgent(
    name="BillingAgent",
    instruction="處理帳務時若需參考政策，請使用 load_memory 工具。",
    tools=[load_memory]
)
```

#### 底層原理探討與權衡
*   **Token 經濟學**：重複注入靜態上下文會導致每輪對話的 Input Token 呈線性增長。RAG（檢索增強生成）模式下的 `MemoryService` 僅在需要時引入相關片段，大幅降低運算成本。
*   **語義一致性**：Vertex AI Memory Bank 利用向量嵌入（Vector Embeddings）進行語義搜尋。當代理人 A 更新了某項知識（透過 `add_session_to_memory`），代理人 B 在下一秒進行檢索時即可獲得最新資訊。

---

## 3. Consensus Pattern：共識模式與辯論

在多代理系統 (MAS) 的架構設計中，「共識模式 (Consensus Pattern)」是解決大型語言模型 (LLM) 隨機性、幻覺 (Hallucination) 以及單一視角偏差的核心技術。

### 情境：優先使用並行採樣與聚合，而非依賴單一 LLM 的第一次回應

LLM 的輸出本質上是機率性的。單次生成（Zero-shot 或單一代理）容易陷入區域性錯誤或生成「聽起來正確但事實錯誤」的資訊。透過 `ParallelAgent` 同時啟動多個具備不同溫度 (Temperature) 或視角的代理進行採樣，能有效拉高回答的基準線。

#### 程式碼範例（Bad vs. Better）

```python
# ❌ Bad: 依賴單一代理處理複雜問題，容易產生單點失效 (Single Point of Failure)
from google.adk.agents import LlmAgent

# 單一代理容易受提示詞偏差 (Prompt Bias) 影響
expert = LlmAgent(
    name="SingleExpert",
    model="gemini-2.0-flash",
    instruction="請詳細分析這份醫療報告的潛在風險。"
)
# 缺點：若模型在單次推理中出錯，系統將直接輸出錯誤結果。

# ✅ Better: 使用 ParallelAgent 進行並行採樣，並透過共享狀態聚合
from google.adk.agents import ParallelAgent, SequentialAgent, LlmAgent

# 定義多個具備不同專業傾向的子代理
analyst_a = LlmAgent(name="Analyst_A", output_key="result_a", instruction="專注於症狀分析。")
analyst_b = LlmAgent(name="Analyst_B", output_key="result_b", instruction="專注於病歷對照。")

# 並行展開 (Fan-out)
gatherer = ParallelAgent(
    name="InfoGatherer",
    sub_agents=[analyst_a, analyst_b]
)

# 聚合與交叉驗證 (Gather)
synthesizer = LlmAgent(
    name="Synthesizer",
    instruction="根據 {result_a} 與 {result_b} 找出共識與矛盾點，產出最終報告。"
)

workflow = SequentialAgent(name="ConsensusWorkflow", sub_agents=[gatherer, synthesizer])
# 優點：透過多元採樣 (Diversity Sampling) 減少單一幻覺的影響。
```

---

## 4. Conflict Resolution：衝突解決策略

在多代理架構（Multi-Agent Architecture）中，當多個具備自主決策能力的 Agent 協同工作時，衝突（Conflict）與死鎖（Deadlock）並非機率問題，而是必然發生的技術挑戰。如同分散式系統中的資源爭奪，LLM Agent 之間的衝突往往發生在**狀態更新競爭**、**指令邏輯矛盾**或**無限迴圈的互相修正**中。

### 情境：優先使用「顯式輸出鍵 (Output Keys)」而非「隱式共享狀態」

在 `ParallelAgent` 的環境下，若多個子 Agent 同時嘗試寫入同一個狀態鍵（Shared State Key），會產生典型的競爭條件（Race Condition），導致最終結果不可預測。

#### 程式碼範例（Bad vs. Better）

```python
# ❌ Bad: 隱式競爭。多個 Agent 競爭寫入同一個 'report' 鍵，導致內容覆蓋或損壞。
agent_a = LlmAgent(name="ResearcherA", output_key="report")
agent_b = LlmAgent(name="ResearcherB", output_key="report")

parallel_executor = ParallelAgent(sub_agents=[agent_a, agent_b])

# ✅ Better: 顯式隔離。每個 Agent 擁有獨立的命名空間。
agent_a = LlmAgent(name="ResearcherA", output_key="research_A")
agent_b = LlmAgent(name="ResearcherB", output_key="research_B")

# 由後續的 MergerAgent 負責解決衝突與匯整
merger_agent = LlmAgent(
    name="Merger",
    instruction="整合來自 {research_A} 與 {research_B} 的資訊。若有衝突，以 A 為主並註明差異。"
)

workflow = SequentialAgent(
    sub_agents=[
        ParallelAgent(sub_agents=[agent_a, agent_b]),
        merger_agent
    ]
)
```

---

## 5. Agent Negotiation：資源談判模式

在多代理人系統 (MAS) 中，當多個具備自主決策能力的 Agent 試圖存取有限的資源（如計算配額、資料庫鎖、或實體設備存取權）時，簡單的「先搶先贏」往往會導致系統效率低下甚至陷入死結。**談判模式 (Negotiation)** 的核心在於引入博弈論 (Game Theory) 與協調機制，讓 Agent 能夠透過訊息交換達成共識，從而最大化系統整體的社會福利 (Social Welfare)。

### 情境：優先使用「出價補償機制」而非「無限重試」

當資源發生衝突時，傳統做法是不斷重試，這會造成資源浪費與延遲。在談判模式下，我們讓每個 Agent 根據其任務的優先順序（權重）進行「出價」，並在獲得資源後補償系統中的其他 Agent（或減少自身的信用額度），達成動態的資源分配。

#### 程式碼範例（Bad vs. Better）

```python
# ❌ Bad: 簡單的無限重試 (Spin-wait/Retry)
# 缺點：造成資源競爭、增加延遲、無法區分優先級
class ResourceConsumer(LlmAgent):
    async def process_task(self, ctx):
        while True:
            if ctx.session.state.get("shared_gpu_resource") == "free":
                ctx.session.state["shared_gpu_resource"] = self.name
                # 執行任務...
                break
            else:
                await asyncio.sleep(1) # 無效等待

# ✅ Better: 基於權重的談判與分配 (Weighted Negotiation)
# 優點：明確優先權、減少衝突、提高資源利用率
from google.adk.agents import LlmAgent, SequentialAgent

# 談判代理：作為協調者 (Coordinator)
negotiator = LlmAgent(
    name="ResourceNegotiator",
    instruction="""
    分析各 Agent 的任務緊急度（權重）。
    若發生衝突，優先將資源分配給高權重 Agent。
    低權重 Agent 需進入等待隊列，並獲得後續優先權補償。
    """,
    output_key="allocation_plan"
)
```

---

## 6. 適用場景與拇指法則 (Rule of Thumb)

*   **拇指法則 1**：當你的系統由多個「弱專才」組成，且問題需要跨領域資訊「拼圖式」地組合時，請使用 **Blackboard 模式**。
*   **拇指法則 2**：如果需要高度可解釋性（例如：為什麼系統在第 3 步推翻了第 1 步的假設），黑板模式的「版本化事實」是最佳解。
*   **拇指法則 3**：對於低延遲、確定性的簡單工具呼叫，切勿過度設計使用黑板模式，這會產生不必要的計算開銷。
*   **拇指法則 4**：對於低風險任務（如摘要），使用單次生成；對於中風險任務（如客服諮詢），使用並行聚合；對於高風險或邏輯複雜任務（如合規性檢查、複雜代碼生成），必須使用迭代辯論。
*   **拇指法則 5**：任何涉及「資料刪除」或「資金轉移」的工具呼叫，都應預設進入 `CONFIRM` 流程（人機協作）。

---

## 7. 延伸思考 (Q&A)

**1️⃣ 問題一**：在 Blackboard 模式中，如何防止多個 Agent 產生的衝突假設導致系統「邏輯崩潰」？

**👆 回答**：這需要引入 **衝突解決（Conflict Resolution）** 模式。Controller 不應只是搬運工，而應實施「基於策略的裁決（Policy-based Resolution）」，例如：法律專才的意見優先於行政專才，或者透過 **共識（Consensus）** 模式讓 Agent 們在黑板上進行一輪「辯論」，直到假設趨於一致。

**2️⃣ 問題二**：如何防止過期的錯誤資訊污染共享向量庫？

**👆 回答**：這是一個經典的資料清理問題。實務上應建立「審查機制（Reviewer Pattern）」。在將 `Session` 攝取到記憶之前，先由一個專屬的「清潔代理（Cleaner Agent）」進行事實查核或格式化，確保進入 `MemoryService` 的資訊是高品質且正確的。

**3️⃣ 問題三**：在並行架構（ParallelAgent）中，多個代理人同時寫入記憶會發生衝突嗎？

**👆 回答**：由於 `add_session_to_memory` 通常是異步操作且作用於向量庫，寫入衝突較少見。然而，為了確保資料完整性，建議在工作流結束後（例如 `SequentialAgent` 的最後一棒）才統一執行記憶攝取，而非在並行分支中各自寫入。

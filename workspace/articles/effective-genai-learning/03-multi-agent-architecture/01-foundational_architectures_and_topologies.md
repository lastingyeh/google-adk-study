# Agent Topologies: 代理人組織架構總覽

在構建複雜的 GenAI 應用時，單一代理（Agent）往往會因為上下文過長、指令過於複雜或任務邊界模糊而導致效能下降。如同資深架構師在設計軟體系統時會考慮模組化與解耦，設計多代理系統（Multi-Agent System, MAS）的核心在於**拓樸結構（Topology）**。正確的拓樸不僅能提升任務成功率，更能確保系統在長期運行下的健壯性。

本章將探討如何利用 Google ADK 的原生內建（Primitives），針對長期、複雜任務建構具備實戰指導性的組織結構。

---

## 1. 任務委派架構概論

在軟體架構的演進中，我們始終在「秩序」與「靈活性」之間尋找平衡。誠如 Joshua Bloch 在 *Effective Java* 中強調的「優先使用組合而非繼承」，在建構 AI 代理（Agent）系統時，我們也必須捨棄臃腫的單體式指令（Monolithic Prompt），轉向模組化的「代理人團隊」。

以下針對任務委派框架中「中心化（Supervisor）」與「去中心化（Swarm）」兩種模式進行深度實戰指導。

### 比較與整合 (Supervisor vs. Swarm)

| 特性         | Supervisor (中心化)            | Swarm (去中心化)                 |
| :----------- | :----------------------------- | :------------------------------- |
| **控制流**   | 階層式，由上而下委派           | 對等網路，自發性組織             |
| **協調機制** | 顯式協調，由管理者主導         | 湧現行為，源於局部互動           |
| **主要優點** | 流程可控、易於除錯與審計       | 高韌性、無單點故障、擴展性強     |
| **主要缺點** | 管理者可能成為效能瓶頸         | 行為難以預測，治理成本高         |
| **最佳應用** | 結構化業務流程（如：貸款處理） | 創意寫作、動態問題求解、災難復原 |

---

## 2. Supervisor Architecture：中央協調模式

在多代理系統（Multi-Agent Systems, MAS）的設計中，如何有效地分配任務並確保各個專家代理（Expert Agents）能各司其職，是決定系統健壯性的關鍵。**Supervisor Architecture**，即中央協調模式，仿照了企業中的管理層結構：由一個具備全域視野的「主管（Supervisor）」來接收需求、拆解任務，並決定由哪位「專家」來執行。

### 情境：優先使用中央協調器管理任務分配，而非讓代理間隨意通訊

當系統規模擴大時，若代理與代理之間採取點對點（Peer-to-Peer）的隨意轉移，會導致狀態管理混亂、權限難以追蹤，且極易產生循環調用的無限迴圈。

#### 核心概念簡述
Supervisor Architecture 透過一個中心化的 `LlmAgent` 作為協調員（Coordinator），所有的使用者請求首先進入協調員。協調員根據子代理（Sub-agents）的描述（Description）與當前任務上下文，動態地透過 `transfer_to_agent` 進行任務委派。

#### 程式碼範例（Bad vs. Better）

```python
# ❌ Bad: 代理間雜亂的點對點轉移
# 這種做法讓每個專家代理都需要知道其他所有代理的存在，造成高度耦合，且難以維護。
from google.adk.agents import LlmAgent

billing_agent = LlmAgent(
    name="Billing",
    instruction="處理帳單。如果問題涉及技術，轉交給 Support。",
    # 這裡強迫 Billing 必須知道 Support 的存在
)

support_agent = LlmAgent(
    name="Support",
    instruction="處理技術問題。如果問題涉及錢，轉交給 Billing。",
    # 這裡強迫 Support 必須知道 Billing 的存在
)

# ✅ Better: 使用 Supervisor (Coordinator) 模式
# 專家代理只需專注於自己的業務領域，由 Supervisor 負責全域調度。
from google.adk.agents import LlmAgent

# 1. 定義專家代理（只關注自身領域）
billing_agent = LlmAgent(
    name="Billing",
    description="專門處理帳單查詢、退款與付款問題。"
)

support_agent = LlmAgent(
    name="Support",
    description="專門處理技術故障排除、登入問題與產品設定。"
)

# 2. 定義 Supervisor (協調員)
supervisor = LlmAgent(
    name="HelpDeskSupervisor",
    model="gemini-2.0-flash",
    instruction="你是一個資深客服主管。請根據用戶問題內容，將任務委派給最合適的代理。對於付款問題使用 Billing，技術問題使用 Support。",
    sub_agents=[billing_agent, support_agent]
)
```

#### 底層原理探討與權衡
Supervisor 模式的核心在於**故障隔離（Fault Isolation）**。如果 `credit_checker` 遇到 API 超時，Supervisor 可以捕捉該錯誤並決定重試或轉交人工處理，而不至於中斷整個貸款流程。這提供了企業級應用不可或缺的「可預測性」與「審核透明度」。

---

## 3. Hierarchical Architectures：階層式架構

在建構複雜的 GenAI 應用程式時，開發者常會面臨「單一代理人過載」的困境。當一個 Agent 需要處理過多工具、複雜邏輯與多元使用者意圖時，LLM 的推理精確度會顯著下降，維護成本則呈指數級增長。階層式架構（Hierarchical Architectures）是軟體工程「分而治之（Divide and Conquer）」原則在多代理人系統中的極致體現。

### 情境：優先使用「中控調度者」而非「扁平化工具堆疊」

核心概念：當 Agent 的工具數量超過 LLM 的有效上下文理解範圍（通常建議不超過 5-10 個專業工具）時，應建立一個 Supervisor（協調員）來將意圖轉發給特定的子代理人（Sub-agents）。

#### 程式碼範例（Bad vs. Better）

```python
# ❌ Bad: 扁平化架構 - 單一 Agent 扛下所有任務
# 所有的工具 (查詢訂單、取消訂單、產品推薦、技術支援) 全部塞給同一個 Agent
# 這會導致 LLM 在選擇工具時容易產生幻覺，且 Prompt 變得極其龐大。
customer_service_agent = LlmAgent(
    name="MegaAgent",
    tools=[order_query_tool, cancel_order_tool, product_rec_tool, tech_support_tool],
    instruction="你負責處理所有客戶需求..."
)

# ✅ Better: 階層式架構 - 使用協調員模式 (Coordinator Pattern)
# 將任務專業化，協調員只負責路由意圖，具體執行交給專家。
billing_agent = LlmAgent(name="Billing", description="專門處理帳務、訂單查詢與退款。")
support_agent = LlmAgent(name="Support", description="專門解決技術障礙與產品操作問題。")

coordinator = LlmAgent(
    name="Coordinator",
    instruction="你是第一線接線生。判斷用戶需求：若涉及錢或訂單請轉接給 Billing；若涉及技術操作請轉接給 Support。",
    sub_agents=[billing_agent, support_agent]
)
```

#### 底層原理探討與權衡
*   **認知負荷（Cognitive Load）**：LLM 處理 `transfer_to_agent` 的決策成本遠低於在 20 個工具中選擇正確的一個。
*   **關注點分離（SoC）**：`Billing` Agent 的 Prompt 不需要知道 `Support` 的細節，這使得單一專業 Agent 的測試與優化變得可行。
*   **權衡**：增加了首字產出時間（TTFT），因為需要兩層推理（協調員判斷 + 子代理執行）。

---

## 4. Swarm Architecture：點對點協作模式

在多代理人系統（MAS）的演進過程中，我們經常見到高度中心化的「編排者模式」（Orchestrator Pattern）。然而，當系統規模擴大，中心節點往往成為效能瓶頸與複雜度的來源。**Swarm Architecture（群集架構）** 則提供了一種去中心化的方案：代理人之間透過點對點（P2P）的方式自發傳遞任務，形成一種「湧現式（Emergent）」的協作結構。

這正如 Scott Meyers 在處理資源管理時強調的「讓物件負責自己的行為」，在 Swarm 架構中，我們讓代理人負責自己的「導航」與「委派」。

### 情境：優先使用自發性轉移 (Transfer) 而非中心化調度器

當多個專業代理人協作時，應讓當前代理人根據上下文判斷「下一步該交給誰」，而不是依賴一個全知的中心調度器（Router）來分配所有工作。

#### 核心概念簡述
在 Google ADK 中，`LlmAgent` 具備內建的 `transfer_to_agent` 能力。透過在 `instructions` 中定義轉移邏輯，代理人可以像傳遞接力棒一樣，將 `InvocationContext` 直接轉移給同級（Peer）或子級（Sub）代理人。這種模式減少了中心節點的負擔，並容許更靈活的對話流。

#### 程式碼範例（Bad vs. Better）

```python
# ❌ Bad: 中心化的路由器 (God Object)
# 這種做法會導致 Router 代理人的 Prompt 極其龐大，且難以維護
router = LlmAgent(
    name="GodRouter",
    instruction="""
    如果是帳務問題，請調用 BillingAgent。
    如果是技術問題，請調用 TechAgent。
    如果是退貨問題，請調用 RefundAgent。
    (當代理人增加時，這裡會無限膨脹...)
    """,
    sub_agents=[billing_agent, tech_agent, refund_agent]
)

# ✅ Better: 湧現式的群集轉移 (Swarm Transfer)
# 每個代理人只需知道與自己相關的下一個對象
billing_agent = LlmAgent(
    name="BillingAgent",
    description="處理帳款與發票",
    instruction="如果你發現用戶的問題涉及技術故障，請轉移給 TechAgent。",
    sub_agents=[tech_agent] # 建立局部導航關係
)

tech_agent = LlmAgent(
    name="TechAgent",
    description="處理技術支援",
    instruction="如果用戶詢問退款政策，請轉移給 RefundAgent。",
    sub_agents=[refund_agent]
)
```

#### 底層原理探討與權衡
*   **權衡 (Trade-offs)**：
    *   **優點**：降低單點失效風險（SPoF），減少中心 Agent 的 Token 消耗。
    *   **缺點**：路徑追蹤變得複雜，若缺乏良好的 `description`，Agent 可能會陷入循環轉移（Infinite Loop）。
*   **機制**：ADK 的 `AutoFlow` 攔截 `transfer_to_agent` 函數調用，並透過 `find_agent` 尋找目標。這是一種「晚期綁定（Late Binding）」的體現，與物件導向中的多型（Polymorphism）有異曲同工之妙。

---

## 5. Agent Router 模式：基於意圖的流量分發

在建構複雜的 GenAI 應用時，我們常面臨一個困境：單一代理（Single Agent）搭載過多工具會導致 LLM 迷失在龐大的 Context 中，進而降低推理品質與反應速度。這就像讓一位全科醫生處理精密的外科手術、財務報表與法律訴訟。

**Agent Router 模式** 借鑒了傳統網路架構中的「路由器」概念，透過一個具備強大理解能力的中心代理，根據使用者的「意圖（Intent）」將任務分發（Dispatch）給最適合的專業子代理（Expert Agents）。

### 情境：優先使用「語意路由」而非「條件式硬編碼」

當系統需要處理多樣化的業務邏輯時，我們應該依賴 LLM 的自然語言理解能力來進行任務路由，而不是撰寫冗長的 `if-else` 或正則表達式。

#### 核心概念簡述
路由代理（Router Agent）扮演「調度員」的角色。它不直接執行具體業務，而是專注於分析使用者的 Prompt，並利用 ADK 的 `transfer_to_agent` 機制將執行焦點轉移。

#### 程式碼範例（Bad vs. Better）

```python
# ❌ Bad: 硬編碼路由 (Rigid Coding)
# 這種做法難以擴展，且無法處理語意模糊的請求。
def handle_request(user_input):
    if "訂單" in user_input or "買" in user_input:
        # 直接呼叫訂單處理代理 (假設 order_agent 與 run 函數已定義)
        return order_agent.run(user_input)
    elif "退貨" in user_input or "退款" in user_input:
        # 直接呼叫退貨處理代理 (假設 refund_agent 與 run 函數已定義)
        return refund_agent.run(user_input)
    else:
        # 無法辨識意圖，回傳一般客服代理的回應 (假設 general_support 與 run 函數已定義)
        return general_support.run(user_input)

# ✅ Better: ADK 語意路由 (Semantic Routing)
# 利用 LlmAgent 的描述 (description) 與指令 (instruction) 進行動態委派。
from google.adk.agents import LlmAgent

# 1. 定義專業子代理
order_expert = LlmAgent(
    name="OrderExpert",
    description="專門處理商品訂購、庫存查詢與訂單追蹤。"
)

refund_expert = LlmAgent(
    name="RefundExpert",
    description="專門處理退貨申請、退款進度與退貨政策諮詢。"
)

# 2. 定義路由代理 (Router)
router_agent = LlmAgent(
    name="SupportRouter",
    model="gemini-2.0-flash",
    instruction="""
    你是客戶服務的首席調度員。請根據使用者的需求性質進行轉發：
    - 如果涉及購買或訂單查詢，轉移給 OrderExpert。
    - 如果涉及退貨或款項問題，轉移給 RefundExpert。
    """,
    sub_agents=[order_expert, refund_expert] # 自動啟用 AutoFlow 轉移機制
)
```

#### 底層原理探討與權衡
*   **靈活性**：LLM 路由可以理解「我想把昨天買的鞋子換掉」這種不含「退貨」關鍵字但語意相關的請求。
*   **效能開銷**：路由代理會增加一次 LLM 推理（Inference）的延遲與成本。
*   **精準度**：路由的品質高度依賴於子代理的 `description`。如果描述過於模糊，LLM 可能會分發錯誤。

---

## 6. 適用場景與拇指法則 (Rule of Thumb)

*   **拇指法則 1**：如果任務包含嚴格的順序依賴（Step-by-Step）且需要符合法規，請使用 **Supervisor (SequentialAgent)**。
*   **拇指法則 2**：如果你有多個獨立任務且對延遲敏感，請使用 **ParallelAgent** 來實作中心化併發處理。
*   **拇指法則 3**：唯有在環境極度不穩定、且任務分配需要高度動態調整時，才考慮轉向 **Swarm** 或 **Marketplace (Contract-Net)** 模式。
*   **拇指法則 4**：當你的系統包含超過 3 個以上的專家代理，或者代理間的轉移邏輯並非固定，而是需要 LLM 根據內容動態決定時，優先使用 **Supervisor Architecture**。
*   **拇指法則 5**：當你的系統超過 5 個以上的專業領域，且領域間的邊界清晰時，應優先考慮 **Swarm Architecture**。
*   **拇指法則 6**：當子代理超過 3 個，且功能邊界明確時，應採用 **Agent Router** 模式。

---

## 7. 延伸思考 (Q&A)

**1️⃣ 問題一**：在 Supervisor 模式下，如果 Supervisor 錯誤地將任務分配給了不相關的專家代理，該如何處理？

**👆 回答**：這通常是因為專家代理的 `description` 不夠精確，或是 Supervisor 的 `instruction` 缺乏負面約束。在 Google ADK 中，我們可以透過在子代理上設置「拒絕處理並 Escalation（升級）」的邏輯。當子代理發現任務不屬於其範疇時，觸發一個帶有 `escalate=True` 的事件，將控制權強制交還給 Supervisor 進行重新路由。

**2️⃣ 問題二**：Swarm 模式如何解決「無限迴圈」或「任務遺失」的問題？

**👆 回答**：在實務上，即使是去中心化架構，也需要加入「超時監視器（Watchdog Timeout）」與「最大迭代限制（Max Iterations）」等安全性模式。此外，利用 ADK 的 `SessionState` 與外部資料庫（如 Redis）實現「增量檢查點（Incremental Checkpointing）」，確保當代理人崩潰重啟時能從最後一個狀態繼續工作，而非遺失任務。

**3️⃣ 問題三**：路由代理是否需要儲存完整的對話歷史？

**👆 回答**：通常需要。在 ADK 的多代理系統中，子代理會共享父代理的 `InvocationContext`。當流量從 Router 路由到專家代理時，專家代理需要知道 Router 之前與使用者的初步對話內容，才能精確對齊上下文。

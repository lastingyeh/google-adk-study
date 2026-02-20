# Resource Dispatch & Economic Models: 資源調度與經濟模型

在設計大規模多代理系統（Multi-Agent Systems, MAS）時，最常見的陷阱是將「調度（Dispatching）」視為一種靜態的、確定性的路由邏輯。這種思維在面對不可預測的 LLM 行為與變動的資源成本時，往往會導致負載不均或決策品質低落。

本章將介紹如何引入經典的經濟模型——**市場化架構 (Market-based Architecture)** 與 **招標網協定 (Contract Net Protocol, CNP)**，將任務指派轉化為一場「市場競標」，實現系統層級的資源最佳化配置。

---

## 1. Market-Based Dispatch：市場化架構中的效用最大化

真正的進階架構師會將代理系統視為一個「微觀經濟市場」。在這個市場中，任務是**商品**，代理人是**承包商**。透過模擬經濟行為（如投標、效用評估），我們可以讓系統自動尋找最優的資源配置，達成「效用最大化」。

### 情境：優先使用「動態投標」而非「靜態硬編碼路由」

傳統的調度器（Dispatcher）通常使用簡單的 `if-else` 或靜態描述來決定由誰執行。在市場化架構中，我們改用「招標（Request for Quotation, RFQ）」模式：先讓子代理評估自身當前狀態與專業度，回傳一個「投標（Bid）」，再由調度器選出最優者。

#### 程式碼範例（Bad vs. Better）

```python
# ❌ Bad: 靜態路由 (Hardcoded Routing)
# 調度器直接決定由誰做，無視代理人的實際狀態或任務難度
from google.adk.agents import LlmAgent

# 單純基於名稱描述，Dispatcher 盲目分配
billing_agent = LlmAgent(name="BillingAgent", description="處理所有帳單請求")
support_agent = LlmAgent(name="SupportAgent", description="處理所有技術支援")

# 缺點：如果 BillingAgent 負載過重，或該請求涉及技術性帳單，靜態路由無法彈性調整

# ✅ Better: 動態投標機制 (Market-based Bidding)
# 使用 ParallelAgent 詢問多個代理人的「執行預期」，再進行決策
from google.adk.agents import ParallelAgent, LlmAgent, SequentialAgent
from typing import Dict

# 讓代理人具備「自我評估」的能力，回傳效用指標 (例如：信心分數、預估成本)
bidder_1 = LlmAgent(
    name="Expert_A",
    instruction="評估以下任務並回傳 JSON: {confidence: 0-1, cost: tokens, speed: seconds}",
    output_key="bid_a"
)
bidder_2 = LlmAgent(
    name="Expert_B",
    instruction="評估以下任務並回傳 JSON: {confidence: 0-1, cost: tokens, speed: seconds}",
    output_key="bid_b"
)

# 使用 ParallelAgent 進行「招標」
auction_house = ParallelAgent(name="AuctionHouse", sub_agents=[bidder_1, bidder_2])

# 決策代理人 (Market Broker) 讀取 state['bid_a'] 與 state['bid_b'] 並決定最終執行者
broker = LlmAgent(
    name="MarketBroker",
    instruction="比較 bid_a 與 bid_b，選出效用值（信心/成本比）最高的代理人進行委派。"
)

market_dispatch = SequentialAgent(sub_agents=[auction_house, broker])
```

#### 底層原理探討與權衡
*   **為什麼（Rationale）**：靜態路由假設了環境是恆定的。然而在 GenAI 世界，模型可能會因為 Context Window 飽和、API 速率限制或特定提示詞的適應性而展現出不同的效能。動態投標將決策權「下放」給具備當前上下文資訊的代理人，能有效提升整體的**健壯性**。
*   **權衡（Trade-off）**：投標機制會增加初始的延遲（Latency）與 Token 成本，因為需要額外的一輪「諮詢」。但在處理高價值或高複雜度的任務時，這筆「市場調查費」換來的是更高的執行成功率。

---

## 2. Contract Net Protocol：招標網協定

招標網協定模擬了人類商業社會的招投標流程：
1.  **招標 (Task Announcement)**：管理器發布任務需求。
2.  **投標 (Bidding)**：具備能力的代理人根據自身資源、預計成本與時間計算標金。
3.  **評標 (Awarding)**：管理器選擇最優標單並簽署契約。

### 情境：優先使用招標機制而非硬編碼指派

當系統中存在多個具備相似能力但效能、成本或當前負載不同的代理人時，應避免由中心協調者（Manager）直接指定執行者。相反地，應讓代理人根據自身狀態參與競標。

#### 程式碼範例（Bad vs. Better）

```python
# ❌ Bad: 靜態委派 (Static Delegation)
# 協調者依賴硬編碼邏輯或簡單的 Round-robin，無視代理人的實際狀態。
# 硬編碼邏輯，無法應對代理人負載不均或離線狀態
from google.adk.agents import LlmAgent

# 協調者直接指定任務給 AgentA，即使 AgentA 目前極度繁忙
coordinator = LlmAgent(
    name="Coordinator",
    instruction="如果收到翻譯請求，直接轉發給 Translator_A。",
    sub_agents=[translator_a, translator_b]
)

# ✅ Better: 招標網機制 (Contract Net Implementation)
# 利用 ADK 的 `ParallelAgent` 收集報價，並由協調者進行最終決策。
# 透過動態評標選擇最佳執行者
from google.adk.agents import SequentialAgent, ParallelAgent, LlmAgent

# 1. 投標代理人：根據自身負載回報預計處理時間（模擬經濟模型中的成本）
bidder_a = LlmAgent(
    name="Translator_HighPrecision",
    instruction="評估翻譯任務。若目前負載低，報價 50 點；若高則報價 200 點。僅輸出 JSON 格式的報價。",
    output_key="bid_a"
)

bidder_b = LlmAgent(
    name="Translator_FastSpeed",
    instruction="評估翻譯任務。報價固定為 100 點。僅輸出 JSON 格式的報價。",
    output_key="bid_b"
)

# 2. 並行招標階段
bidding_phase = ParallelAgent(
    name="BiddingPhase",
    sub_agents=[bidder_a, bidder_b]
)

# 3. 評標與執行階段
evaluator = LlmAgent(
    name="ContractManager",
    instruction="比較 {bid_a} 與 {bid_b}。選擇標金最低的代理人執行任務並回報結果。",
)

# 總體招標工作流
contract_net_workflow = SequentialAgent(
    name="ContractNetWorkflow",
    sub_agents=[bidding_phase, evaluator]
)
```

#### 底層原理探討與權衡
招標網的本質是**資訊去中心化**。在集中式系統中，中心節點必須精確掌握所有子節點的即時狀態（CPU、記憶體、佇列長度），這會產生龐大的通訊開銷與同步延遲。

---

## 3. 適用場景與拇指法則 (Rule of Thumb)

*   **拇指法則 1**：當任務執行者的性能會隨負載大幅波動，或任務需要特定領域專家（Domain Experts）競逐時，優先使用 **Contract Net**。
*   **拇指法則 2**：唯有在環境極度不穩定、且任務分配需要高度動態調整時，才考慮轉向 **Marketplace (Contract-Net)** 模式。
*   **拇指法則 3**：避免使用招標網當任務極其微小（執行時間 < 通訊延遲）或代理人同質性極高時，簡單的 Load Balancer 效率更高。

---

## 4. 延伸思考 (Q&A)

**1️⃣ 問題一**：市場化架構是否會導致「公地悲劇（Tragedy of the Commons）」，即所有任務都搶佔同一個高效率資源？

**👆 回答**：在軟體架構中，這表現為特定模型 API 的 Rate Limit 耗盡。解決方案是在效用函數中加入「動態懲罰項」。當某代理人的並發數接近閾值時，手動調高其「投標報價」（Cost），迫使 Broker 選擇備援方案。

**2️⃣ 問題二**：如何防止惡意投標或「公地悲劇」？

**👆 回答**：可以引入「信譽分 (Reputation)」機制。管理器在 `session.state` 中記錄每個代理人的履約紀錄。若某代理人中標後頻繁逾時或出錯，在未來的評標環節中，其標金將被加權懲罰（Penalty），從而確保系統長期的穩定性。

**3️⃣ 問題三**：Google ADK 的哪些組件最適合實作這套經濟模型？

**👆 回答**：
*   **`ParallelAgent`**：用於「平行探尋（Parallel Exploration）」，模擬市場報價。
*   **`session.state`**：作為「市場資訊公告板（Market Board）」。
*   **`PolicyEngine`**：定義市場準入規則與治理策略。
*   **`AgentTool`**：讓 Agent 可以像「採購員」一樣主動詢問其他 Agent。

# Advanced Integration & Scaling: 分散式協作與系統擴展

在大規模 GenAI 系統中，單一代理（Monolithic Agent）往往難以應對跨組織、跨語言或高隔離要求的任務。正如微服務架構解決了軟體工程的擴展性問題，**Agent-to-Agent (A2A) 協議**與**適配器模式 (Adapter Pattern)** 則是多代理架構走向「分散式」與「專業化」的核心。

本章將探討如何利用 Google ADK 實作跨伺服器的遠端協同、異質系統整合以及團隊角色的專業化分工。

---

## 1. Distributed Collaboration：分散式協作與 A2A 協議

當代理需要與其他團隊維護的服務或不同語言開發的代理通訊時，不應隨意設計一組臨時的 REST API。應採用標準化的 A2A 協議，透過 `RemoteA2aAgent` 與 `Agent Card` 建立正式的服務合約。

### 情境：跨邊界協作時，優先使用 A2A 協議而非自定義 API

當你需要跨越服務邊界（跨進程或跨網路）調用另一個代理時，應優先考慮 Google ADK 的 A2A 協議。它提供了標準化的「代理卡（Agent Card）」機制，讓主代理能像發現服務一樣了解子代理的能力。

#### 程式碼範例（Bad vs. Better）

```python
# ❌ Bad: 使用自定義 requests 呼叫遠端服務
# 缺點：缺乏元數據描述、無法自動整合至 ADK 任務分配邏輯、維護成本高。
import requests

def call_remote_calculator(expression):
    response = requests.post("http://calc-service/eval", json={"expr": expression})
    return response.json()["result"]

# ✅ Better: 使用 RemoteA2aAgent 封裝遠端代理
# 優點：ADK 會自動處理網路、認證，並讓 LLM 了解遠端代理的能力（Skills）。
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH

calc_agent = RemoteA2aAgent(
    name="calculator_agent",
    description="負責處理複雜數學運算的遠端代理",
    agent_card=f"http://calc-service/a2a/calculator{AGENT_CARD_WELL_KNOWN_PATH}"
)
```

#### 底層原理探討與權衡
A2A 協議的核心在於 **Agent Card (代理卡)**。它不僅是技術上的端點（Endpoint），更包含了代理的「技能清單（Skills）」與「能力描述（Capabilities）」。這讓主代理（Root Agent）在編排任務時，能像看待本地工具一樣，精準地將子任務指派給遠端代理。

---

## 2. Agent Delegation & Adapters：委派代理與適配器

並非所有外部系統都支援 A2A 協議。當你需要連接一個傳統的 REST API 或是非 ADK 構建的 AI 服務時，你需要一個「適配器」來將其偽裝成 ADK 代理或工具。

### 情境：當代理介面不相容時，透過適配器（Adapter）轉發

適配器模式（Adapter Pattern）的作用是「抹平介面差異」。在 ADK 中，你可以透過實作一個自定義的 `Tool` 或將外部服務包裝成 `AgentTool` 來實現。

#### 程式碼範例（Bad vs. Better）

```python
# ❌ Bad: 在主代理的 Prompt 中硬寫如何調用外部 API
# 這會污染 Prompt 空間，且容易因為 API 格式微調而崩潰。
instruction = "如果需要查詢天氣，請呼叫 http://weather-api... 並解析傳回的複雜 XML"

# ✅ Better: 實作適配器將異質介面封裝為標準 Tool
def weather_adapter_tool(location: str) -> str:
    """
    獲取指定地點的天氣（適配器）。
    """
    # 底層邏輯處理傳統 API 的 XML/複雜格式
    raw_data = call_legacy_weather_service(location)
    return f"當前天氣是：{raw_data.summary}"

# 將適配器註冊到代理中
# agent = Agent(..., tools=[weather_adapter_tool])
```

#### 底層原理探討與權衡
使用適配器可以保護主代理（Root Agent）免受外部系統不穩定介面的影響。**權衡點**在於：適配器會引入一層額外的延遲，但它換取了主代理邏輯的「純潔度」。

---

## 3. Role Specialization：角色專業化

在構建生成式 AI 應用時，開發者常面臨一個抉擇：是該建立一個「無所不能」的大型代理（Generalist Agent），還是建立一群「各司其職」的小型專才代理（Specialist Agents）？

### 情境：優先使用「專才代理」而非「巨型通才」

在複雜任務中，試圖讓單一代理處理所有工具、多樣化的指令與長上下文，往往會導致性能下降與邏輯混亂。

#### 程式碼範例（Bad vs. Better）

```python
# ❌ Bad: 巨型通才代理 (Monolithic Generalist)
# 單一代理擁有一切權限，指令過於龐雜，難以測試與優化。
from google.adk.agents import LlmAgent

mega_agent = LlmAgent(
    name="MegaAgent",
    model="gemini-2.0-flash",
    instruction="""
    你是一個全能助理。
    如果你被要求查詢天氣，請使用 weather_tool。
    如果你被要求計算稅務，請使用 tax_calculator。
    如果你被要求生成圖像，請使用 image_gen_tool。
    ... (還有 20 個其他指令)
    """,
    tools=[weather_tool, tax_calculator, image_gen_tool, ...]
)

# ✅ Better: 專才代理協作 (Specialized Agents Team)
# 透過角色專業化，將任務委派給專家。
from google.adk.agents import LlmAgent

# 專家代理：專注於氣象
weather_specialist = LlmAgent(
    name="WeatherAgent",
    description="專精於全球氣象數據查詢與預測。",
    instruction="你是一個氣象專家，只負責解析天氣相關需求並使用 weather_tool。"
)

# 專家代理：專注於財務計算
finance_specialist = LlmAgent(
    name="FinanceAgent",
    description="專精於稅務計算與理財規劃建議。",
    instruction="你是一個精算師，負責使用 tax_calculator 進行精確計算。"
)

# 協調員：負責路由與管理
coordinator = LlmAgent(
    name="Coordinator",
    model="gemini-2.0-flash",
    instruction="根據用戶需求，將任務委派給合適的專家。",
    sub_agents=[weather_specialist, finance_specialist]
)
```

---

## 4. 適用場景與拇指法則 (Rule of Thumb)

*   **拇指法則 1**：當任務邊界極其模糊，或者開發初期的快速原型驗證（POC）階段，可使用通才模型。一旦業務流程固定化，轉向專業化是提升生產級系統穩定性的必經之路。
*   **拇指法則 2**：若子代理需頻繁存取主代理的內部狀態或大量記憶體對象，選**本地子代理**。
*   **拇指法則 3**：若其中一個代理必須用 Java 撰寫而另一個是 Python，或功能具備獨立生命週期且被多個系統共用，選 **A2A**。
*   **拇指法則 4**：使用 **`AgentTool` (顯式調用)** 當你希望父代理人「控制」子代理人的輸出，並將結果視為其決策過程的一部分時。
*   **拇指法則 5**：使用 **`sub_agents` (動態轉發)** 當你希望將「主導權」完全移交給另一個 Agent 時。

---

## 5. 延伸思考 (Q&A)

**1️⃣ 問題一**：在 A2A 架構下，如果遠端代理回應過慢，會如何影響主代理的執行？

**👆 回答**：A2A 調用在本質上是 I/O 密集型操作。主代理在等待遠端代理回應時會阻塞目前的執行分支。為了提升健壯性，建議在 `RemoteA2aAgent` 設定中加入超時（Timeout）機制，或在主代理的 `instruction` 中加入超時後的重試或備援邏輯。

**2️⃣ 問題二**：多層級委派（A -> B -> C）會導致什麼風險？

**👆 回答**：最主要的風險是 **「指令漂移（Prompt Drift）」** 與 **「延遲累積」**。每多一層委派，原始意圖就可能被稀釋。資深架構師通常會限制委派深度不超過兩層，並在中間層進行結果的「強型別校驗」。

**3️⃣ 問題三**：如果我有 50 個專才代理，路由代理（Coordinator）會不會因為負擔太重而失效？

**👆 回答**：會。這就是「層次化路由（Hierarchical Routing）」的重要性。你不應該在一個 Coordinator 下放 50 個代理，而是應該按領域分組。例如：`MainCoordinator` 負責路由到 `FinanceDept` 或 `ITDept`，而 `FinanceDept` 本身又是另一個 Coordinator，下轄數個財務專門代理。

# 上下文工程：深入解析 Google 生產級 AI 代理架構 (Context Engineering: Inside Google's Architecture for Production AI Agents)

> 📝 **原文翻譯自 Raphaël MANSUY 的 Blog**：[Context Engineering: Inside Google's Architecture for Production AI Agents](https://raphaelmansuy.github.io/adk_training/blog/2025/12/08/context-engineering-google-adk-architecture)

> 🖼️ 圖片來源：[context-engineering](https://github.com/raphaelmansuy/adk_training/tree/main/docs/blog/assets/context-engineering)

---

## 前言 (Preface)

生成式 AI 從新奇事物發展成為企業基石，必須從根本上改變系統建構方法。早期的 LLM 採用強調「提示工程 (Prompt Engineering)」——即臨時的字串串接、試誤式的措辭以及極少的狀態管理。雖然這對於簡單的聊天機器人來說已經足夠，但這種方法在生產需求下（可靠性、可觀察性、延遲和成本效率）會崩潰。

Google Gen AI Agent Development Kit (ADK) 標誌著 **上下文工程 (Context Engineering)** 的到來——這是一門將上下文視為 **編譯視圖 (compiled view)** 而非可變字串緩衝區的學科，建立在豐富的狀態系統之上。

![代理的工業化](./assets/context-engineering/industrialization-of-agency.png)

## 1. 簡介 (Introduction)

代理的工業化與上下文工程典範 (Introduction: The Industrialization of Agency and the Context Engineering Paradigm)

### 1.1 框架的必要性 (The Necessity of a Framework)

為什麼業界需要專門的代理框架？答案在於複雜性的爆炸。代理不僅僅是一個模型；它是一個能夠感知、推理、行動並記憶的系統。管理對話生命週期、狀態持久性、安全的工具執行和任務委派，需要原始 API 呼叫無法提供的機制。

ADK 透過模組化、模型無關、部署無關的框架填補了這一空白，將標準軟體開發原則應用於 AI 代理的創建。它提供了鷹架——Flows (流程)、Processors (處理器)、Session Services (會話服務)、Memory Banks (記憶體庫)——讓開發者能夠專注於認知邏輯，而不是基礎設施的管道工程。

---

## 2. 架構哲學：上下文作為一等公民系統 (Architectural Philosophy: Context as a First-Class System)

要精通 ADK，必須內化其核心論點：**上下文是一種需要主動管理的動態工程資源**，以防止認知過載和財務浪費。

![上下文作為系統](./assets/context-engineering/context-as-system.png)

### 2.1 「為什麼」：解決上下文窗口困境 (The "Why": Solving the Context Window Dilemma)

「僅追加日誌 (append-only log)」方法會導致三個關鍵失敗：

1.  **成本爆炸 (Cost Explosion)**：每一輪都發送完整的歷史記錄 = 代幣消耗呈線性增長
2.  **延遲惡化 (Latency Degradation)**：更大的上下文 = 更長的處理時間 = 使用者體驗下降
3.  **迷失在中間 (Lost in the Middle)**：模型難以處理埋藏在大量上下文窗口中的指令

透過將上下文視為具有自身架構的系統，ADK 實現了 **上下文壓縮 (Context Compaction)**、**快取 (Caching)** 和 **選擇性注入 (Selective Injection)**。

**工作上下文 (Working Context)**——實際發送給 LLM 的提示——不是原始歷史記錄；它是一個 **編譯視圖 (compiled view)**。就像編譯器將高階程式碼轉換為優化的機器碼一樣，ADK Runtime 將會話狀態（歷史記錄、變數、Artifacts）轉換為針對特定輪次量身定制的優化上下文窗口。

### 2.2 編譯器管道類比 (The Compiler Pipeline Analogy)

這體現在 **Flows** 和 **Processors** 中。編譯管道由作用於原始請求的處理器序列組成：

- 一個處理器注入代理身分
- 另一個檢索相關的長期記憶
- 第三個檢查快取的上下文前綴以優化推理速度

這種模組化允許架構師「編程」上下文窗口，插入自定義邏輯進行過濾、清理或增強，而無需重寫核心代理。

---

## 3. 代理單元：解剖與配置 (The Agentic Unit: Anatomy and Configuration)

ADK Agent 是一個由嚴格配置合約定義的可組合邏輯單元。

![代理結構](./assets/context-engineering/agent-anatomy.png)

### 3.1 LlmAgent：認知核心 (The LlmAgent: The Cognitive Core)

**LlmAgent** 代表一個使用 LLM 進行推理和行動的實體。

#### 3.1.1 身分與服務發現 (Identity and Service Discovery)

每個代理都需要唯一的 **名稱 (name)** 和 **描述 (description)**。在多代理系統中，這些欄位充當「服務發現 (Service Discovery)」機制：

- **Name**：路由委派的唯一位址
- **Description**：其他代理（路由代理）讀取的語義介面，用於了解同伴的能力

像「處理客戶退款」這樣的描述允許 Root Agent (根代理) 智慧地路由退款請求，而無需知道內部實作。

```python
# 繁體中文註解：基本的代理配置與身分
from google.adk.agents import LlmAgent

# 配置具有身分的基本代理
agent = LlmAgent(
    name="RefundSpecialist",  # 代理名稱：退款專員
    description="Handles customer refund requests and processes returns",  # 描述：處理客戶退款請求並處理退貨
    model="gemini-2.5-flash", # 使用的模型
)
```

#### 3.1.2 配置合約 (The Configuration Contract)

ADK 透過 **LlmAgent 配置**（包括 **GenerateContentConfig**）強制執行代理邏輯與執行時參數之間的嚴格分離：

- **隨機性控制 (Stochastic Control)** (temperature, top_p)：細粒度的隨機性控制。創意寫作代理需要高溫度 (0.9) 以產生新穎內容；資料提取代理需要接近零的溫度以產生確定性、有效的 JSON 輸出。
- **安全設定 (Safety Settings)**：企業部署需要嚴格的安全準則。ADK 允許直接在代理配置中定義安全閾值，確保安全性是一個編譯屬性。

```python
# 繁體中文註解：配置具有精確生成參數的代理
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig

# 配置資料提取代理
data_extractor = LlmAgent(
    name="DataExtractor",
    model="gemini-2.5-flash",
    generate_content_config=GenerateContentConfig(
        temperature=0.0,  # 確定性輸出，適用於結構化資料
        top_p=0.95,
    ),
)

# 配置創意寫作代理，使用較高溫度
creative_writer = LlmAgent(
    name="CreativeWriter",
    model="gemini-2.5-flash",
    generate_content_config=GenerateContentConfig(
        temperature=0.9,  # 高創造力
        top_p=1.0,
    ),
)
```

### 3.2 工作流代理：確定性編排 (Workflow Agents: Deterministic Orchestration)

LLM 是機率性的。企業工作流程有時需要確定性的執行。當業務流程強制「步驟 A 必須總是跟隨步驟 B」時，為什麼要讓 LLM 決定步驟順序？

ADK 提供 **Workflow Agents (工作流代理)**——SequentialAgent、ParallelAgent 和 LoopAgent：

- **SequentialAgent (循序代理)**：強制執行嚴格的線性執行。對於資料處理管道至關重要，其中一個代理的輸出（摘要器）是下一個代理的必要輸入（翻譯器）。
- **ParallelAgent (平行代理)**：同時執行多個子代理，減少可平行化任務的掛鐘時間（例如同時研究三個查詢面向）。
- **LoopAgent (循環代理)**：實作迭代回饋循環，執行子代理直到滿足終止條件（例如自我修正程式碼生成）。

```python
# 繁體中文註解：定義循序與平行工作流程
from google.adk.agents import SequentialAgent, ParallelAgent

# 循序工作流程：先摘要再翻譯
summarizer = LlmAgent(name="Summarizer", model="gemini-2.5-flash")
translator = LlmAgent(name="Translator", model="gemini-2.5-flash")

pipeline = SequentialAgent(
    name="SummarizeAndTranslate",
    agents=[summarizer, translator],
)

# 平行工作流程：同時研究多個主題
researcher_a = LlmAgent(name="ResearcherA", model="gemini-2.5-flash")
researcher_b = LlmAgent(name="ResearcherB", model="gemini-2.5-flash")
researcher_c = LlmAgent(name="ResearcherC", model="gemini-2.5-flash")

parallel_research = ParallelAgent(
    name="ParallelResearch",
    agents=[researcher_a, researcher_b, researcher_c],
)
```

透過混合 LlmAgents（機率性）與 WorkflowAgents（確定性），架構師可以平衡創造力與可靠性。

這些代理定義指定了系統做 _什麼_——認知能力和編排模式。但是 ADK Runtime 實際上 _如何_ 執行這些定義？這就是 Flows 和 Processors 提供認知引擎的地方。

---

## 4. 認知引擎：流程與處理器 (The Cognitive Engine: Flows and Processors)

我們已經定義了代理。現在我們需要了解賦予它們生命的執行機制。Agent（結構）和 Flow（執行）之間的區別是 ADK 最強大的功能之一。

![認知引擎](./assets/context-engineering/cognitive-engine.png)

### 4.1 BaseLlmFlow：執行迴圈 (BaseLlmFlow: The Execution Loop)

**BaseLlmFlow** 定義了標準的認知循環：

1.  **準備 (Preparation)**：收集歷史記錄、狀態、指令以建立 LlmRequest
2.  **呼叫 (Invocation)**：呼叫模型 API
3.  **處理 (Processing)**：解析 LlmResponse 以獲取文字或工具呼叫
4.  **行動 (Action)**：執行工具或委派給其他代理
5.  **遞迴 (Recursion)**：決定是返回結果還是將工具輸出回饋以進行下一輪

將 Flow 與 Agent 分離允許平台演進「最佳實踐」（錯誤處理、重試邏輯），而無需開發者更新特定的代理定義。

### 4.2 處理器管道：自定義認知 (The Processor Pipeline: Customizing Cognition)

「上下文作為編譯視圖」的哲學是透過 **Processors (處理器)** 實現的——攔截請求/回應週期的模組化元件。

#### 4.2.1 身分與指令處理器 (Identity and Instruction Processors)

**IdentityProcessor** 和 **InstructionProcessor** 開啟管道：

> **機制**：注入代理特定的指令。InstructionProcessor 解析動態變數——如果指令包含 `{user_name}`，它會在 `session.state` 中查找該值並進行替換。

**原因**：啟用動態模板而非靜態字串，無需更改程式碼即可實現個人化。

#### 4.2.2 上下文快取處理器 (Context Cache Processor)

隨著模型增長，每一輪重新處理相同的系統指令變得令人卻步。**ContextCacheProcessor** 解決了這個問題：

> **機制**：分析當前請求以識別「穩定前綴 (Stable Prefixes)」——未更改的提示部分（例如 2,000 字的系統提示）。與後端通訊以重複使用這些代幣的快取注意力機制。

**影響**：對於長時間運行的代理，可以將首字延遲 (TTFT) 和推理成本降低幾個數量級。

```python
# 繁體中文註解：啟用上下文快取
from google.adk.apps import App
from google.genai.types import ContextCacheConfig

# 在應用程式層級啟用上下文快取
app = App(
    context_cache_config=ContextCacheConfig(
        min_tokens=2048,      # 快取的最小前綴大小
        ttl_seconds=3600,     # 快取存活時間 (1 小時)
        cache_intervals=10,   # 使用 10 次後重新整理
    ),
)

# 使用 static_instruction 以獲得最大快取效率
agent = LlmAgent(
    name="CachedAgent",
    model="gemini-2.5-flash",
    static_instruction="Long unchanging system prompt...",  # 此部分將被快取
)
```

#### 4.2.3 規劃處理器 (Planning Processor)

對於複雜的任務，簡單的提示是不夠的。**PlanningProcessor** 注入特定的鷹架，鼓勵在行動之前進行規劃：

> **機制**：如果配置了 Planner（如 PlanReActPlanner），則附加指令強制模型在生成工具呼叫之前輸出「思考 (Thought)」和「計畫 (Plan)」。

**原因**：在基礎設施層級實作「思維鏈 (Chain of Thought)」推理，減輕開發者手動提示的負擔。

#### 4.2.4 代理轉移處理器 (Agent Transfer Processor)

在使用 AutoFlow 的多代理場景中，**AgentTransferProcessor** 至關重要：

> **機制**：動態注入 `transfer_to_agent` 工具定義。生成所有可用子代理的描述並將其注入系統提示。

**原因**：賦予代理「後設認知 (meta-cognition)」——對其團隊的意識。允許代理知道「我無法處理這個，但『研究員』代理可以」，並相應地呼叫轉移工具。

---

## 5. 狀態管理：連續性的基質 (State Management: The Substrate of Continuity)

一個反覆出現的失敗模式：將「歷史 (History)」（說了什麼）與「狀態 (State)」（什麼是真實的）混為一談。ADK 透過嚴格分離 **Session (會話)**、**State (狀態)** 和 **Memory (記憶)** 來解決這個問題。

![狀態管理](./assets/context-engineering/state-management.png)

### 5.1 會話：互動的容器 (Sessions: The Container of Interaction)

**Session (會話)** 是隔離的基本單元，代表單個對話執行緒。

- **隔離 (Isolation)**：一個會話的資料永遠不會滲透到另一個會話，確保隱私和安全
- **元件 (Components)**：包含 Events（不可變的互動日誌）和 State（可變變數）

### 5.2 持久層：會話服務 (The Persistence Layer: Session Services)

ADK 採用 Repository 模式進行會話管理，允許使用可替換的儲存後端：

#### 5.2.1 InMemorySessionService

- **機制**：將會話資料儲存在應用程式 RAM（Python 字典）中
- **使用案例**：嚴格用於本地原型設計和單元測試
- **關鍵警告**：在像 Google Cloud Run（無狀態）這樣的生產環境中，容器重啟會清除所有資料。ADK CLI 預設使用此服務——對於遷移到生產環境的粗心開發者來說是一個陷阱。

#### 5.2.2 VertexAiSessionService

- **機制**：將會話管理卸載到 Google Cloud Vertex AI Agent Engine
- **原因**：「無伺服器 (Serverless)」方法。提供持久性、可擴展性，並與更廣泛的 Vertex 生態系統整合，無需資料庫管理開銷。

#### 5.2.3 DatabaseSessionService

- **機制**：連接到 SQL 資料庫 (PostgreSQL, SQLite)
- **原因**：對於具有嚴格資料駐留要求或現有資料庫基礎設施的企業，允許完全控制會話資料架構和生命週期。

### 5.3 狀態：可變的暫存器 (State: The Mutable Scratchpad)

當 Events 追蹤歷史時，`session.state` 追蹤當前上下文：

- **問題**：如果使用者說「我想買張票」，然後說「其實，取消吧」，歷史記錄包含矛盾。讀取完整歷史的代理必須花費認知努力來解決這個問題。
- **解決方案**：代理在 `session.state` 中更新變數 `intent: "cancel_ticket"`。這提供了一個明確的「真實來源」，無需重新解釋。
- **上下文控制**：`include_contents='none'` 模式的主要機制。透過將特定狀態變數注入代理指令，開發者提供 _僅_ 必要的上下文（例如 `user_name`, `order_id`），而不會用整個聊天記錄污染上下文窗口。

```python
# 繁體中文註解：使用狀態管理工具
from google.adk.agents.callback_context import CallbackContext

async def update_intent_tool(context: CallbackContext, new_intent: str):
    """更新會話狀態中的使用者意圖。"""
    # 存取並修改會話狀態
    await context.session.state.set("intent", new_intent)
    await context.session.state.set("last_updated", context.session.current_time())
    return f"Intent updated to: {new_intent}"

async def get_context_tool(context: CallbackContext):
    """在不使用完整歷史記錄的情況下檢索當前狀態。"""
    intent = await context.session.state.get("intent")
    user_name = await context.session.state.get("user_name")
    return f"User {user_name} wants to: {intent}"
```

狀態解決了 _會話內_ 的上下文問題。但是當會話結束時會發生什麼？狀態是會話範圍的——當使用者幾天或幾週後回來時，該狀態就消失了。對於必須跨時間跨度記住事實的代理，我們完全需要一種不同的抽象。

---

## 6. 記憶體系統：跨越時間鴻溝 (Memory Systems: Bridging the Temporal Gap)

狀態提供對話內的連續性。記憶體提供跨對話的連續性。無論上下文窗口多大，它都是短暫的——當會話結束時它就會清除。為了建構能夠在數月或數年內「認識」使用者的代理，ADK 引入了 **Memory Services (記憶體服務)**。

![記憶體系統](./assets/context-engineering/memory-systems.png)

### 6.1 區別：上下文 vs. 記憶體 (The Distinction: Context vs. Memory)

- **上下文 (Context)**：短期、高保真、昂貴。「工作記憶 (Working Memory)」。
- **記憶體 (Memory)**：長期、壓縮、可搜尋。「長期儲存 (Long-Term Storage)」。

### 6.2 VertexAiMemoryBankService

ADK 透過 **VertexAiMemoryBankService** 提供複雜的長期記憶：

- **攝取 (Ingestion)** (`add_session_to_memory`)：不是簡單的文字傾倒。該服務使用 LLM 來「閱讀」已完成的會話並提取顯著事實（例如「使用者偏好靠走道的座位」、「使用者對花生過敏」）。這些事實被向量嵌入並儲存。
- **檢索 (Retrieval)** (`search_memory`)：當新會話開始時，代理可以語義搜尋此記憶體庫。
- **「為什麼」**：啟用「情節記憶 (Episodic Memory)」。代理可以回憶起三個月前的細節，而無需將三個月的聊天記錄載入上下文窗口。這大幅降低了成本和延遲，同時提高了感知的智慧。

```python
# 繁體中文註解：使用記憶體服務
from google.adk.memory import InMemoryMemoryService

memory_service = InMemoryMemoryService()

# 會話完成後，新增至長期記憶
await memory_service.add_session_to_memory(session)

# 在新會話中，搜尋相關的過去上下文
async def recall_preferences_tool(context: CallbackContext, query: str):
    """搜尋長期記憶以獲取使用者偏好。"""
    results = await context.memory_service.search_memory(query=query)
    return results
```

我們已經介紹了單個代理如何在會話內和跨會話記憶。但是複雜的問題通常超出單個代理的能力。當任務需要專業知識時，協調多個代理變得至關重要。

---

## 7. 多代理系統 (MAS)：編排與委派 (Multi-Agent Systems (MAS): Orchestration and Delegation)

單個代理有其限制——有限的上下文窗口、有限的工具集、單一的認知概況。複雜的企業工作流程需要專業化。ADK 的真正力量出現在多代理系統 (MAS) 中，為階層式、分散式或基於群體的代理網路提供原語。

![多代理系統](./assets/context-engineering/multi-agent-systems.png)

### 7.1 委派機制 (The Delegation Mechanism)

一個代理如何與另一個代理「交談」？在 ADK 中，這是透過 **LLM 驅動的委派 (LLM-Driven Delegation)** 處理的：

- **`transfer_to_agent` 工具**：當代理配置有子代理時，AutoFlow 會自動為其配備一個特殊工具：`transfer_to_agent(agent_name="TargetAgent")`
- **邏輯**：LLM 根據其指令和子代理描述，決定何時呼叫此工具
- **執行時移交 (Runtime Handoff)**：當呼叫該工具時，Runtime 會攔截請求。它不僅僅是執行一個函式；它執行 **上下文切換 (Context Switch)**。它暫停呼叫代理 (Root) 的執行並初始化目標代理 (Specialist) 的執行。

```python
# 繁體中文註解：多代理系統配置
from google.adk.agents import LlmAgent
from google.adk.flows import AutoFlow

# 定義專家代理
refund_agent = LlmAgent(
    name="RefundSpecialist",
    description="Handles customer refund requests",  # 處理客戶退款請求
    model="gemini-2.5-flash",
)

support_agent = LlmAgent(
    name="SupportSpecialist",
    description="Handles technical support questions",  # 處理技術支援問題
    model="gemini-2.5-flash",
)

# 具有子代理的根代理 - AutoFlow 新增 transfer_to_agent 工具
root_agent = LlmAgent(
    name="CustomerService",
    model="gemini-2.5-flash",
    agents=[refund_agent, support_agent],  # 可供委派的子代理
)
```

### 7.2 上下文移交問題 (The Context Handoff Problem)

MAS 中的一個關鍵架構挑戰：決定什麼上下文從呼叫者傳遞給被呼叫者。

- **預設行為**：預設情況下，子代理可能會繼承完整的歷史記錄 (`include_contents='default'`)。在深層委派鏈中（Root → Manager → Specialist → Worker），這會導致上下文膨脹。
- **上下文壓縮 (Context Compaction)**：為了緩解這種情況，ADK 支援 **上下文壓縮**。此功能在傳遞給子代理之前使用滑動窗口或摘要模型來壓縮歷史記錄。子代理接收任務的「要點」，而沒有整個執行緒的雜訊。

### 7.3 A2A 協議：分散式代理 (The A2A Protocol: Distributed Agency)

對於跨越網路邊界（例如微服務）的系統，ADK 引入了 **Agent-to-Agent (A2A) 協議**：

- **「為什麼」**：在大型企業中，「銷售代理」可能歸銷售工程部門所有，而「庫存代理」歸物流部門所有。它們運行在不同的叢集，甚至不同的雲端上。
- **機制**：A2A 標準化了遠端代理呼叫的握手、驗證和訊息格式。它抽象了 HTTP/gRPC 傳輸，允許本地代理像對待任何其他子代理一樣對待遠端代理。這使得代理是鬆散耦合服務的「群體 (Swarm)」架構成為可能。

多代理協調處理任務委派。但是當代理需要推理非文字資料時會發生什麼？現實世界的工作流程需要處理文件、影像和媒體檔案。

---

## 8. Artifact 子系統：管理二進位現實 (The Artifact Subsystem: Managing Binary Reality)

工具處理函式呼叫和 API 互動。但代理並不生活在純文字世界中。它們必須處理 PDF、影像、試算表和音訊。ADK 透過 **Artifact Subsystem (Artifact 子系統)** 管理這些內容。

![Artifact 子系統](./assets/context-engineering/artifact-subsystem.png)

### 8.1 Artifact 模式 (The Artifact Pattern)

為什麼不直接將 PDF 文字貼上到提示中？

1.  **格式遺失 (Format Loss)**：PDF 包含在純文字提取中遺失的空間資訊（佈局、表格）
2.  **上下文限制 (Context Limits)**：大檔案超過代幣限制

ADK 將這些檔案視為 **Artifacts**。它們儲存在 ArtifactService（GCS 或本地）中，代理被給予該 Artifact 的 _參考 (reference)_。

- **延遲載入 (Lazy Loading)**：代理可能會收到檔案摘要。只有當它決定需要原始資料時，它才會使用特定工具來「讀取」Artifact。
- **短暫擴展 (Ephemeral Expansion)**：ADK 支援將 Artifact 內容載入到特定輪次的上下文窗口中，然後將其解除載入。這種動態上下文管理確保代理在需要推理時擁有資料，但不會在會話的其餘部分攜帶「無效負重」。

```python
# 繁體中文註解：Artifact 處理工具
from google.adk.agents.callback_context import CallbackContext
import google.genai.types as types

async def save_report_artifact(context: CallbackContext, report_bytes: bytes):
    """將報告儲存為 Artifact 並返回參考。"""
    report_part = types.Part.from_bytes(
        data=report_bytes,
        mime_type="application/pdf"
    )
    version = await context.artifact_service.save_artifact(
        artifact_name="monthly_report",
        artifact=report_part,
    )
    return f"Report saved as artifact version {version}"

async def load_artifact(context: CallbackContext, artifact_name: str):
    """載入 Artifact 內容以進行處理。"""
    artifact = await context.artifact_service.load_artifact(
        artifact_name=artifact_name,
    )
    return artifact  # 僅在當前輪次可用
```

---

## 9. 工具：通往確定性的橋樑 (Tooling: The Bridge to Determinism)

工具是代理的手。在 ADK 中，建立工具在 Python 中非常簡單，但底層機制卻很複雜。

![工具橋樑](./assets/context-engineering/tooling-bridge.png)

### 9.1 透過檢查定義 (Definition by Inspection)

ADK 使用反射將標準 Python 函式轉換為工具定義：

- **型別提示 (Type Hints)**：框架讀取 Python 型別提示 (`str`, `int`, `Optional`) 以生成工具的 JSON 架構
- **Docstrings 作為提示**：函式的 docstring 不僅僅是文件；它是告訴 LLM _何時_ 以及 _如何_ 使用該工具的提示。寫得好的 docstring 對於代理認知效能至關重要。

```python
# 繁體中文註解：定義並註冊工具
def get_weather(city: str, units: str = "celsius") -> str:
    """獲取特定城市的當前天氣。

    當使用者詢問天氣狀況時使用此工具。

    Args:
        city: 城市名稱 (例如 "Tokyo", "London")
        units: 溫度單位，"celsius" (攝氏) 或 "fahrenheit" (華氏)

    Returns:
        帶有溫度的天氣描述
    """
    # ADK 自動將此函式轉換為工具定義
    # 型別提示生成 JSON 架構，docstring 指導 LLM 使用
    return f"Weather in {city}: 22°{units[0].upper()}, sunny"

# 向代理註冊工具
agent = LlmAgent(
    name="WeatherAgent",
    model="gemini-2.5-flash",
    tools=[get_weather],
)
```

### 9.2 平行執行 (Parallel Execution)

ADK Runtime 開箱即支援 **平行函式呼叫 (Parallel Function Calling)**：

- **場景**：使用者問「東京、倫敦和紐約的天氣如何？」
- **執行**：LLM 生成三個不同的工具呼叫。Runtime 檢測到這一點並使用 `asyncio.gather()` 並行執行它們
- **影響**：大幅減少延遲。使用者只需等待單個最長請求的持續時間，而不是等待三個連續的 HTTP 請求。

### 9.3 人機迴圈 (Human-in-the-Loop)

對於敏感操作（例如「退款給使用者」、「刪除資料庫」），自主性是一種風險。ADK 支援 **工具確認 (Tool Confirmations)**：

- **機制**：工具可以配置為需要確認。當代理嘗試呼叫它時，Runtime 會暫停執行並向客戶端應用程式 (UI) 發送訊號。人類使用者必須明確批准該操作，Runtime 才會恢復執行並實際呼叫該函式。

---

## 10. 實作與可觀察性 (Implementation and Observability)

如果系統無法在生產環境中可靠運行，架構和功能就毫無意義。從原型過渡到生產需要關注環境限制和可觀察性基礎設施。

![可觀察性與生產](./assets/context-engineering/observability-production.png)

### 10.1 環境限制 (Environment Constraints)

ADK 建立在現代 Python 功能之上：

- **要求**：ADK v1.19.0+ 嚴格要求 **Python 3.10** 或更高版本。嘗試在舊環境中運行它的開發者將面臨立即的相容性失敗。
- **虛擬環境**：由於 Gen AI 依賴項快速變動，使用虛擬環境 (venv) 幾乎是強制性的，以避免相容性地獄。

### 10.2 可觀察性：多層策略 (Observability: A Multi-Layer Strategy)

> 你無法優化你無法測量的東西。

生產級代理系統需要多個層次的可觀察性：營運指標、認知效能和分散式追蹤。ADK 和更廣泛的生態系統提供了三種互補的方法。

#### 10.2.1 BigQuery Agent Analytics：認知效能分析

ADK 提供與 **Google Cloud BigQuery** 的深度整合以進行分析：

- **「為什麼」**：在生產中，您需要回答諸如：「『退款』工具多久失敗一次？」、「每個會話的平均代幣成本是多少？」、「使用者是否卡在迴圈中？」等問題。
- **機制**：BigQuery Agent Analytics 工具允許開發者將遙測資料直接串流傳輸到 BigQuery。這使得能夠對代理認知效能進行基於 SQL 的分析，從而允許對提示和配置進行資料驅動的迭代。
- **使用案例**：聚合分析、每個代理/會話的成本歸因、工具成功率、上下文窗口利用率趨勢、提示的 A/B 測試

```python
# 繁體中文註解：配置 BigQuery 可觀察性
from google.adk.observability import BigQueryObserver

# 配置 BigQuery 遙測串流
observer = BigQueryObserver(
    project_id="my-project",
    dataset_id="agent_telemetry",
    table_id="agent_events",
)

# 附加到應用程式以進行自動事件串流
app = App(
    agent=root_agent,
    observers=[observer],
)

# 透過 SQL 查詢見解
"""
SELECT
  agent_name,
  AVG(token_count) as avg_tokens,
  AVG(latency_ms) as avg_latency,
  COUNT(CASE WHEN status='error' THEN 1 END) as error_count
FROM agent_telemetry.agent_events
WHERE DATE(timestamp) = CURRENT_DATE()
GROUP BY agent_name
"""
```

#### 10.2.2 MLflow for GenAI：實驗追蹤與 LLM 可觀察性

**MLflow** 提供實驗追蹤、模型版本控制和專門的 GenAI 可觀察性：

- **「為什麼」**：代理開發是迭代的——您需要追蹤哪些提示變體、溫度設定或工具配置產生最佳結果。MLflow 為實驗和比較提供了結構化框架。
- **GenAI 追蹤**：MLflow 2.8+ 包含原生 LLM 追蹤功能。它自動將 LLM 呼叫、代幣計數、延遲和嵌入捕獲為結構化追蹤。這對於除錯多輪代理對話和了解認知失敗發生在哪裡至關重要。
- **整合模式**：MLflow 在實驗/開發層運作。在開發期間，將每個代理配置記錄為 MLflow 實驗。在生產中，使用 MLflow 追蹤來捕獲代表性會話或失敗互動的詳細執行追蹤。

```python
# 繁體中文註解：使用 MLflow 進行實驗追蹤
import mlflow
from mlflow.tracking import MlflowClient

# 在開發期間追蹤代理實驗
mlflow.set_experiment("agent_prompt_optimization")

with mlflow.start_run(run_name="refund_agent_v3"):
    # 將代理配置記錄為參數
    mlflow.log_param("model", "gemini-2.5-flash")
    mlflow.log_param("temperature", 0.3)
    mlflow.log_param("prompt_version", "v3_with_cot")

    # 運行代理評估
    result = evaluate_agent(agent, test_cases)

    # 記錄效能指標
    mlflow.log_metric("success_rate", result.success_rate)
    mlflow.log_metric("avg_latency_ms", result.avg_latency)
    mlflow.log_metric("avg_cost_per_session", result.avg_cost)

    # 將提示記錄為 Artifact
    mlflow.log_text(agent.instruction, "prompt.txt")

# 啟用 MLflow 追蹤以進行生產除錯
mlflow.langchain.autolog()  # 自動追蹤 LangChain/ADK 代理呼叫

# 或手動建立 span 以進行精細控制
with mlflow.start_span(name="refund_processing") as span:
    span.set_inputs({"user_request": user_input})
    result = await agent.run(user_input)
    span.set_outputs({"agent_response": result})
    span.set_attribute("token_count", result.token_count)
```

#### 10.2.3 OpenTelemetry：分散式追蹤與營運可觀察性

**OpenTelemetry (OTel)** 為分散式追蹤和指標提供供應商中立的檢測：

- **「為什麼」**：在多代理系統中，特別是那些使用 A2A 協議跨微服務的系統，了解完整的請求路徑至關重要。哪個代理花了多長時間？上下文在哪裡遺失了？OpenTelemetry 追蹤整個分散式執行 DAG。
- **機制**：OTel 使用組織成 **Traces (追蹤)**（端到端請求流）的 **Spans**（工作單元）概念。每個代理呼叫、工具執行或委派都變成一個 span。span 之間的父子關係揭示了執行層次結構。
- **整合**：透過用 OTel spans 包裝關鍵執行點（流程呼叫、工具執行、代理轉移）來檢測 ADK 代理。將追蹤匯出到 Jaeger、Grafana Tempo 或 Google Cloud Trace 等後端。

```python
# 繁體中文註解：使用 OpenTelemetry 進行分散式追蹤
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# 配置 OpenTelemetry 與 Google Cloud Trace 後端
tracer_provider = TracerProvider()
cloud_trace_exporter = CloudTraceSpanExporter()
tracer_provider.add_span_processor(
    BatchSpanProcessor(cloud_trace_exporter)
)
trace.set_tracer_provider(tracer_provider)

tracer = trace.get_tracer(__name__)

# 使用 spans 檢測代理執行
async def instrumented_agent_run(agent, user_input):
    with tracer.start_as_current_span(
        "agent.run",
        attributes={
            "agent.name": agent.name,
            "agent.model": agent.model,
        }
    ) as span:
        try:
            result = await agent.run(user_input)
            span.set_attribute("token.input", result.input_tokens)
            span.set_attribute("token.output", result.output_tokens)
            span.set_status(trace.Status(trace.StatusCode.OK))
            return result
        except Exception as e:
            span.set_status(trace.Status(trace.StatusCode.ERROR))
            span.record_exception(e)
            raise
```

#### 10.2.4 可觀察性堆疊：選擇您的層次 (The Observability Stack: Choosing Your Layer)

| 工具                   | 主要焦點             | 最適合                         | 整合工作量            |
| ---------------------- | -------------------- | ------------------------------ | --------------------- |
| **BigQuery Analytics** | 聚合認知指標         | 成本分析、A/B 測試、趨勢分析   | 低 (原生 ADK 支援)    |
| **MLflow**             | 實驗追蹤、LLM 追蹤   | 開發迭代、提示優化、模型比較   | 中 (需要明確日誌記錄) |
| **OpenTelemetry**      | 分散式追蹤、營運指標 | 多代理系統、延遲除錯、A2A 架構 | 高 (需要 span 檢測)   |

**建議策略**：協同使用這三者：

1.  **開發**：MLflow 用於實驗追蹤和提示優化
2.  **生產**：OpenTelemetry 用於請求級分散式追蹤和即時營運指標
3.  **分析**：BigQuery 用於聚合分析、成本歸因和長期趨勢分析

這種多層可觀察性策略確保您可以除錯個別請求 (OTel)、優化代理配置 (MLflow) 並了解全系統效能 (BigQuery)。

---

## 11. 結論：工程化代理的時代 (Conclusion: The Era of Engineered Agency)

![工程化代理的時代](./assets/context-engineering/engineered-agency-era.png)

我們從上下文工程作為典範轉移開始。我們歷經了代理結構、執行流程、狀態管理、記憶體系統、多代理協調、工具、Artifacts 和可觀察性。Google Gen AI Agent Development Kit 代表了邁向 AI 工業化的決定性一步。它將領域從「腳本」心態——代理是脆弱、不透明和無狀態的——轉移到「系統工程」心態。

透過將 **上下文視為編譯視圖**，強制執行 **狀態** 和 **記憶體** 的嚴格分離，並提供 **多代理編排** 的架構原語，ADK 賦予架構師建構可靠、可擴展且可維護系統的能力。

它承認代理「智慧」不僅在於模型權重，還在於圍繞它的架構。對於專業領域專家來說，ADK 不僅僅是一個工具包；它是智慧軟體未來的藍圖。

---

## 程式碼實現 (Code Implementation)

- Hello World Agent (基礎代理)：[程式碼連結](../../../python/agents/hello-agent/)

---

## 參考表格 (Reference Tables)

### 會話服務比較 (Session Service Comparison)

| 功能             | InMemorySessionService | DatabaseSessionService | VertexAiSessionService |
| ---------------- | ---------------------- | ---------------------- | ---------------------- |
| **持久性**       | 無 (易失性)            | 高 (SQL 後端)          | 高 (託管服務)          |
| **可擴展性**     | 單一實例               | 垂直/水平 DB 擴展      | 雲端原生 / 無伺服器    |
| **設定複雜度**   | 零 (預設)              | 中 (需要 DB)           | 低 (需要 GCP 專案)     |
| **主要使用案例** | 本地原型設計           | 地端 / 混合雲          | 雲端原生生產           |
| **風險**         | 重啟時資料遺失         | 架構管理開銷           | API 成本 / 供應商鎖定  |

### ADK 處理器管道 (ADK Processor Pipeline)

| 順序 | 處理器名稱                 | 功能與「為什麼」                     |
| ---- | -------------------------- | ------------------------------------ |
| 1    | **IdentityProcessor**      | 注入代理名稱/角色。建立自我意識。    |
| 2    | **InstructionProcessor**   | 編譯動態提示 (`{var}`)。啟用個人化。 |
| 3    | **ContextCacheProcessor**  | 檢查/注入快取代幣。降低成本/延遲。   |
| 4    | **PlanningProcessor**      | 注入推理鷹架。強制「思維鏈」。       |
| 5    | **CodeExecutionProcessor** | 準備程式碼執行環境。啟用動態計算。   |
| 6    | **AgentTransferProcessor** | 注入委派工具。啟用多代理路由。       |

### 工作流代理類型 (Workflow Agent Types)

| 代理類型            | 執行邏輯             | 理想使用案例           |
| ------------------- | -------------------- | ---------------------- |
| **SequentialAgent** | 線性 (A → B → C)     | 資料管道、嚴格 SOP     |
| **ParallelAgent**   | 並行 (A + B + C)     | 研究、扇出任務         |
| **LoopAgent**       | 迭代 (A → Check → A) | 寫程式、自我修正、精煉 |

---

## 資源 (Resources)

### 官方 Google ADK 資源 (Official Google ADK Resources)

- **ADK GitHub Repository**: [github.com/google/adk-python](https://github.com/google/adk-python)
- **Official Documentation**: [google.github.io/adk-docs](https://google.github.io/adk-docs/agents/llm-agents/)
- **Google Cloud Agent Engine**: [Cloud Agent Engine Docs](https://docs.cloud.google.com/agent-builder/agent-engine/sessions/manage-sessions-adk)

### 社群與教學 (Community and Tutorials)

- **ADK Deep Dives**: [iamulya.one](https://iamulya.one/posts/orchestrating-agent-behavior-flows-and-planners/)
- **Context Engineering Blog**: [developers.googleblog.com](https://developers.googleblog.com/architecting-efficient-context-aware-multi-agent-framework-for-production/)

### 相關文章 (Related Articles)

- [Agent Starter Pack Deep Dive](./2025-12-01-fast-track-agent-starter-pack.md)
- [OpenTelemetry with ADK and Jaeger](./2025-11-18-opentelemetry-adk-jaeger.md)
- [GEPA Optimization Tutorial](../adk_training/36-gepa_optimization_advanced.md))

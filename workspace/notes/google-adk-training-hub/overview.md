# Overview of Google ADK Training Hub

## Mental Models for Google ADK Mastery - Complete Guide 2025

### 壹、核心心理模型：代理即系統 (The Agent as a System)

一個 AI 代理（Agent）**並非僅僅是一個大型語言模型 (LLM)**。核心觀點是，它是一個**完整的系統**，被類比為一個**人類辦公室工作人員**。

| 系統組成部分        | 類比                | 功能描述                                                                                    | 來源 |
| :------------------ | :------------------ | :------------------------------------------------------------------------------------------ | :--- |
| **大腦 [BRAIN]**    | LLM 模型            | 負責**推理**、**決策制定**和語言理解。                                                      |      |
| **記憶 [MEM]**      | Context             | 包含短期記憶（**Session State**，即本次對話）和長期記憶（**Memory Service**，即所有對話）。 |      |
| **工具 [TOOLS]**    | Capabilities (雙手) | 執行動作，如網路搜尋、執行程式碼、呼叫 API 和檔案操作。                                     |      |
| **指令 [INSTR]**    | Behavior            | 定義代理的**行為**、**個性**、規則、約束條件和任務指導。                                    |      |
| **工作流程 [FLOW]** | Process             | 結構化的執行過程，如順序步驟、平行任務、迭代迴圈和動態路由。                                |      |
| **回呼 [CALLB]**    | Supervision         | 提供**控制和監督**，例如事前/事後鉤子、**護欄 (guardrails)**、日誌記錄和策略執行。          |      |

---

### 貳、三大類型代理 (The Three Types of Agents)

代理被視為具有不同思維風格的工作人員。選擇代理的類型取決於任務的需求。

1.  **[BRAIN] LLM 代理 (Thinker)**：
    *   **特點：** 由語言模型驅動。具有彈性 (Flexible)、創意性、適應性強。
    *   **用途：** 適用於對話、分析和需要**動態推理**的創意任務。
    *   **使用時機：** 當需要推理、彈性或處理自然語言時。

2.  **[FLOW] 工作流程代理 (Manager)**：
    *   **特點：** 執行**確定性的嚴格流程**。負責協調和編排其他代理。
    *   **類型：** 順序 (Sequential)、平行 (Parallel)、迴圈 (Loop)。
    *   **用途：** 適用於管道 (Pipelines)、協調和需要**可預測、有序執行**的迭代任務。

3.  **[REMOTE] 遠端代理 (External Expert)**：
    *   **特點：** 是一個來自**外部服務的專家**。透過 HTTP 和 A2A (Agent-to-Agent) 協定進行通訊。
    *   **用途：** 適用於微服務和專業領域。
    *   **使用時機：** 當需要呼叫外部服務時。

---

### 參、ADK 開發的十大誡律（關鍵原則）

這些原則是 ADK 開發的最佳實踐和設計指南。

1.  **Agent = 系統，而不僅僅是 LLM**：永遠要考慮 Model + Tools + State + Instructions + Workflows 的組合。
2.  **短期用 State，長期用 Memory**：Session State 用於本次對話，Memory Service 用於所有對話的歷史記錄。
3.  **順序用於有依賴關係，平行用於追求速度**。
4.  **迴圈用於精煉質量，而非核心邏輯**：使用 `LoopAgent` 進行精煉 (refinement)，使用 `SequentialAgent` 進行有序步驟。
5.  **奠基 (Ground) 任何需要為真的內容**：事實應透過 `google_search` 獲取，數據應透過資料庫工具獲取。
6.  **工具是能力，不是事後補充**：設計工具時應考慮到代理，並確保工具回傳**結構化數據 (dicts)** 和清晰的文檔字符串 (docstrings)。
7.  **回呼用於控制，而非核心業務邏輯**：用於護欄 (guardrails)、日誌記錄、監控等。
8.  **先從簡單開始，有需要時再增加複雜度**：從單一代理開始，再轉向多代理；從順序開始，再加入平行。
9.  **盡早評估，經常評估**：從第一天就建立測試集，每次重大變更都要執行評估，並使用 Trace view 進行除錯。
10. **生產環境 ≠ 開發環境**：本地開發時可使用 InMemory 服務；生產環境應使用持久性服務，如 PostgreSQL、GCS 或 Vertex。

---

### 肆、學習導航結構

本指南涵蓋了 ADK 掌握的各個面向，結構化地組織為以下重點部分：

*   **代理架構 (Agent Architecture)**：涵蓋代理層次結構、狀態與記憶管理、會話和使用者上下文處理。
*   **工具與能力 (Tools & Capabilities)**：包括工具生態系統（Function, OpenAPI, MCP, 內建）、工具選擇和**平行工具執行**。
*   **工作流程與編排 (Workflows & Orchestration)**：涵蓋順序、平行、迴圈模式和複雜管道建構。
*   **LLM 整合 (LLM Integration)**：包括提示工程、指令模式、奠基 (Grounding) 和推理框架。
*   **生產與部署 (Production & Deployment)**：關於部署環境、可觀察性、監控和服務配置。
*   **進階模式 (Advanced Patterns)**：例如串流、MCP 協定和**代理間通訊 (Agent-to-agent communication)**。
*   **決策框架 (Decision Frameworks)**：提供模式選擇指南和成本優化策略。
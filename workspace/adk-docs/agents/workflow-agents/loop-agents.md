# 迴圈代理 (Loop agents)
🔔 `更新日期：2026-01-14`

[`ADK 支援`: `Python v0.1.0` | `Typescript v0.2.0` | `Go v0.1.0` | `Java v0.2.0`]

`LoopAgent` 是一種工作流代理，它會以迴圈（即迭代）的方式執行其子代理。它會**重複執行一序列的代理**，直到達到指定的迭代次數或滿足終止條件為止。

當您的工作流涉及重複或迭代優化（例如修改程式碼）時，請使用 `LoopAgent`。

### 範例

* 您想要建立一個可以生成食物圖片的代理，但有時當您想要生成特定數量的項目時（例如 5 根香蕉），它在圖片中生成的數量卻不同，例如生成了 7 根香蕉。您有兩個工具：`生成圖片`、`計算食物項目`。因為您希望持續生成圖片，直到它正確生成指定數量的項目，或達到一定的迭代次數，所以您應該使用 `LoopAgent` 來構建您的代理。

與其他 [工作流代理 (workflow agents)](index.md) 一樣，`LoopAgent` 不是由 LLM 驅動的，因此其執行方式是確定性的。話雖如此，工作流代理僅關注其執行方式（例如迴圈），而不關注其內部邏輯；工作流代理的工具或子代理可能會或可能不會使用 LLM。

### 運作方式

當呼叫 `LoopAgent` 的 `Run Async` 方法時，它會執行以下動作：

1. **子代理執行：** 它會*依序*遍歷子代理列表。對於*每個*子代理，它會呼叫該代理的 `Run Async` 方法。
2. **終止檢查：**

    *關鍵在於*，`LoopAgent` 本身*不會*內在地決定何時停止迴圈。您*必須*實作終止機制以防止無限迴圈。常見的策略包括：

    * **最大迭代次數 (Max Iterations)**：在 `LoopAgent` 中設置最大迭代次數。**迴圈將在達到該迭代次數後終止**。
    * **來自子代理的回報 (Escalation from sub-agent)**：設計一個或多個子代理來評估條件（例如：「文件品質是否足夠好？」、「是否已達成共識？」）。如果滿足條件，子代理可以發出終止訊號（例如：透過引發自定義事件、在共享上下文中設置標誌或回傳特定值）。

![迴圈代理](https://google.github.io/adk-docs/assets/loop-agent.png)

### 完整範例：迭代式文件優化

想像一個您想要迭代改進文件的場景：

* **寫手代理 (Writer Agent)：** 一個 `LlmAgent`，負責生成或完善關於某個主題的草稿。
* **評論代理 (Critic Agent)：** 一個 `LlmAgent`，負責評論草稿並找出需要改進的地方。

    ```py
    # 建立 LoopAgent，包含寫手和評論代理，最多執行 5 次迭代
    LoopAgent(sub_agents=[WriterAgent, CriticAgent], max_iterations=5)
    ```

在此設定中，`LoopAgent` 將管理迭代過程。**評論代理可以被設計為當文件達到滿意的品質水平時回傳「停止 (STOP)」訊號**，從而防止進一步的迭代。或者，可以使用 `max iterations` 參數將過程限制在固定的循環次數內，或者可以實作外部邏輯來做出停止決定。**迴圈最多執行五次**，確保迭代優化不會無限期地繼續下去。

> [!TIP] 完整範例程式碼
> 以下提供各語言的 `LoopAgent` 完整實作，方便參考與實作：
>
> **Python**
> → [查看範例程式碼](https://github.com/google/adk-docs/blob/main/examples/python/snippets/agents/workflow-agents/loop_agent_doc_improv_agent.py)
>
> **TypeScript**
> → [查看範例程式碼](https://github.com/google/adk-docs/blob/main/examples/typescript/snippets/agents/workflow-agents/loop_agent_doc_improv_agent.ts)
>
> **Go**
> → [查看範例程式碼](https://github.com/google/adk-docs/blob/main/examples/go/snippets/agents/workflow-agents/loop/main.go)
>
> **Java**
> → [查看範例程式碼](https://github.com/google/adk-docs/blob/main/examples/java/snippets/src/main/java/agents/workflow/LoopAgentExample.java)

---
### [程式碼] 重點說明 (以 Python 為例)

#### 1. 迴圈代理 (LoopAgent) 的核心架構
程式碼中的 `refinement_loop` 是核心，它體現了文件中提到的「重複執行一序列代理」的特性：
*   **子代理組成**：包含 `critic_agent_in_loop` (評論者) 與 `refiner_agent_in_loop` (精煉者)。
*   **執行順序**：`LoopAgent` 會依序執行子代理。評論者先檢查草稿並產出評論 (`STATE_CRITICISM`)，精煉者再根據評論決定優化文件或結束流程。

#### 2. 終止機制 (Termination Mechanism)
文件強調 `LoopAgent` 本身不會自動停止，必須實作終止機制。本程式碼同時採用了文件中推薦的兩種策略：
*   **最大迭代次數 (Max Iterations)**：
    *   在 `refinement_loop` 中設置了 `max_iterations=5`。這是一個安全閥，確保即使邏輯出錯，迴圈也不會無限執行。
*   **來自子代理的回報 (Escalation from sub-agent)**：
    *   **工具實作**：定義了 `exit_loop` 工具，其關鍵動作為 `tool_context.actions.escalate = True`。這會向 `LoopAgent` 發出終止訊號。
    *   **邏輯判斷**：`refiner_agent_in_loop` 扮演決策者。當評論符合 `COMPLETION_PHRASE` (即「No major issues found.」) 時，它會呼叫 `exit_loop` 工具來跳出迴圈。

#### 3. 狀態管理與資料流 (State & Data Flow)
迭代優化高度依賴共享上下文 (State)，程式碼中使用了 `output_key` 來管理：
*   **資料傳遞**：
    1.  `InitialWriterAgent` 產出最初的 `current_document`。
    2.  `CriticAgent` 讀取 `current_document` 並輸出 `criticism`。
    3.  `RefinerAgent` 讀取這兩者，並將優化後的結果重新寫回 `current_document`。
*   **覆寫機制**：透過 `output_key=STATE_CURRENT_DOC`，每一次循環都會更新文件內容，供下一輪評論使用。

#### 4. 階層式代理設計 (SequentialAgent)
*   程式碼將整個流程包裝在 `root_agent` (`SequentialAgent`) 中。
*   這符合文件的最佳實踐：先執行一次性的 `initial_writer_agent` 建立基礎，再進入持續迭代的 `refinement_loop`。

#### 5. 確定性與 LLM 的結合
*   **確定性流控**：`LoopAgent` 與 `SequentialAgent` 作為工作流代理，其「執行順序」是確定的。
*   **靈活內容**：內部的 `LlmAgent` 則負責非確定性的創意寫作與邏輯判斷，完美結合了流程控制的穩定性與 AI 的靈活性。
# 順序型代理 (Sequential agents)

> 🔔 `更新日期：2026-01-23`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/

[`ADK 支援`: `Python v0.1.0` | `Typescript v0.2.0` | `Go v0.1.0` | `Java v0.2.0`]

`SequentialAgent` 是一種[工作流代理 (workflow agent)](index.md)，它會按照清單中指定的順序執行其子代理。
當您希望執行過程以固定、嚴格的順序發生時，請使用 `SequentialAgent`。

### 範例

* 您想要建立一個可以摘要任何網頁的代理，使用兩個工具：「獲取網頁內容 (Get Page Contents)」和「摘要網頁 (Summarize Page)」。因為代理必須始終在調用「摘要網頁」之前調用「獲取網頁內容」（您無法憑空進行摘要！），所以您應該使用 `SequentialAgent` 來構建您的代理。

與其他[工作流代理 (workflow agent)](index.md)一樣，`SequentialAgent` 並非由 LLM 驅動，因此其執行方式是確定性的。話雖如此，工作流代理僅關注其執行過程（即按順序執行），而不關注其內部邏輯；工作流代理的工具或子代理可能使用也可能不使用 LLM。

### 運作原理

當調用 `SequentialAgent` 的 `Run Async` 方法時，它執行以下操作：

1. **迭代：** 它按照提供的順序迭代子代理清單。
2. **子代理執行：** 對於清單中的每個子代理，它會調用該子代理的 `Run Async` 方法。

![順序型代理](https://google.github.io/adk-docs/assets/sequential-agent.png)

### 完整範例：程式碼開發管線

考慮一個簡化的程式碼開發管線：

* **程式碼撰寫代理 (Code Writer Agent)：** 一個根據規格生成初始程式碼的 LLM 代理。
* **程式碼審查代理 (Code Reviewer Agent)：** 一個審查生成的程式碼是否存在錯誤、風格問題並確保符合最佳實踐的 LLM 代理。它接收程式碼撰寫代理的輸出。
* **程式碼重構代理 (Code Refactorer Agent)：** 一個接收審查後的程式碼（以及審查者的評論）並進行重構以提高質量並解決問題的 LLM 代理。

`SequentialAgent` 非常適合此場景：

```py
# 定義順序執行代理，包含撰寫、審查與重構三個子代理
SequentialAgent(sub_agents=[CodeWriterAgent, CodeReviewerAgent, CodeRefactorerAgent])
```

這確保了程式碼按照嚴格、可靠的順序被撰寫，*然後*進行審查，*最後*進行重構。**每個子代理的輸出會通過[輸出鍵 (Output Key)](../llm-agents.md#結構化數據-input_schema-output_schema-output_key) 存儲在狀態中，從而傳遞給下一個代理**。

> [!NOTE] 共享調用上下文 (Shared Invocation Context)
    `SequentialAgent` 將相同的 `InvocationContext` 傳遞給其每個子代理。這意味著它們都共享相同的會話狀態，包括臨時 (`temp:`) 命名空間，從而可以輕鬆地在單次輪詢中的各個步驟之間傳遞數據。

> [!TIP] 完整範例程式碼
> 以下提供各語言的 `capitsequential_agent_code_development_agent` 完整實作，方便參考與實作：
>
> **Python**
> → [查看範例程式碼](https://github.com/google/adk-docs/blob/main/examples/python/snippets/agents/workflow-agents/sequential_agent_code_development_agent.py)
>
> **TypeScript**
> → [查看範例程式碼](https://github.com/google/adk-docs/blob/main/examples/typescript/snippets/agents/workflow-agents/sequential_agent_code_development_agent.ts)
>
> **Go**
> → [查看範例程式碼](https://github.com/google/adk-docs/blob/main/examples/go/snippets/agents/workflow-agents/sequential/main.go)
>
> **Java**
> → [查看範例程式碼](https://github.com/google/adk-docs/blob/main/examples/java/snippets/src/main/java/agents/workflow/SequentialAgentExample.java)

---
### [程式碼] 重點說明 (以 Python 為例)

#### 1. 順序型代理 (SequentialAgent) 的定序執行
程式碼中的 `code_pipeline_agent` 完美體現了 `SequentialAgent` 的核心價值：**嚴格的順序性**。
*   **執行序列**：`WriterAgent` (撰寫) → `ReviewerAgent` (審查) → `RefactorerAgent` (重構)。
*   **邏輯依賴**：如文件所述，重構代理必須依賴審查評論，而審查代理必須依賴生成的程式碼。這種「無中不能生有」的邏輯，最適合使用 `SequentialAgent` 來確保流程不會跳躍或交錯。

#### 2. 狀態傳遞與輸出鍵 (Output Key) 的運用
這是本程式碼最關鍵的實作細節，與文件提到的「數據傳遞」機制完全一致：
*   **數據流動鏈**：
    1.  `CodeWriterAgent` 執行後，結果存入 `generated_code`。
    2.  `CodeReviewerAgent` 在 `instruction` 中使用 `{generated_code}` 注入前一步的結果。
    3.  `CodeRefactorerAgent` 同時引用 `{generated_code}` 與 `{review_comments}` 來進行最終優化。
*   **共享會話狀態**：透過 `InMemoryRunner` 執行的所有子代理都共享同一個 `InvocationContext`，因此能輕易地在不同步驟間傳遞複雜數據。

#### 3. 工作流代理與 LLM 的職責分離
*   **工作流代理 (SequentialAgent)**：負責「流程控制」。它是確定性的，確保步驟 1、2、3 按順序發生。
*   **子代理 (LlmAgent)**：負責「內容生成」。雖然流程固定，但每個步驟產出的程式碼、評論或重構內容是由 LLM 驅動，具有高度靈活性。

#### 4. 結構化指令 (Structured Instructions)
程式碼展示了如何利用 ADK 的字串注入功能來強化代理：
*   在 `instruction` 中使用大括號格式（如 `{review_comments}`），讓每個代理能精確地獲取它所需的上下文，這也是實作複雜管線時的最佳實踐。

#### 5. 實作細節對應
*   **APP_NAME 與 SESSION_ID**：在 `InMemoryRunner` 中，這些標識符確保了狀態被正確地隔離與存儲在指定的會話中。
*   **root_agent**：程式碼最後將 `code_pipeline_agent` 指定為 `root_agent`，這符合 ADK 框架對單一進入點的命名規範，確保後續工具（如調試或部署）能正確識別。
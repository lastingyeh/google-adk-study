# 使用 AgentOps 進行 Agent 可觀測性

> 🔔 `更新日期：2026-01-29`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/observability/agentops/

**只需兩行程式碼**，[AgentOps](https://www.agentops.ai) 即可為 Agent 提供會話重播、指標和監控。

## 為什麼要在 ADK 中使用 AgentOps？

可觀測性是開發和部署對話式 AI Agent 的關鍵面向。它讓開發者能夠了解其 Agent 的運作效能、如何與使用者互動，以及如何使用外部工具和 API。

透過整合 AgentOps，開發者可以深入了解其 ADK Agent 的行為、LLM 互動和工具使用情況。

Google ADK 包含其自身基於 OpenTelemetry 的追蹤系統，主要旨在為開發者提供一種追蹤 Agent 內部基本執行流程的方法。AgentOps 則透過提供專用且更全面的可觀測性平台來增強此功能，具備以下特色：

*   **統一的追蹤與重播分析：** 整合來自 ADK 和 AI 技術棧其他組件的追蹤。
*   **豐富的可視化：** 直觀的儀表板，可視化 Agent 執行流程、LLM 調用和工具效能。
*   **詳細的除錯：** 深入探究特定的 Span，查看 Prompt、Completion、Token 數量和錯誤。
*   **LLM 成本和延遲追蹤：** 追蹤延遲、成本（透過 Token 使用量），並識別瓶頸。
*   **簡化的設定：** 只需幾行程式碼即可開始使用。

![AgentOps Agent 可觀測性儀表板](https://raw.githubusercontent.com/AgentOps-AI/agentops/refs/heads/main/docs/images/external/app_screenshots/overview.png)

![AgentOps 儀表板顯示具有嵌套 Agent、LLM 和工具 Span 的 ADK 追蹤。](https://google.github.io/adk-docs/assets/agentops-adk-trace-example.jpg)

*AgentOps 儀表板顯示來自多步驟 ADK 應用程式執行的追蹤。您可以看到 Span 的層次結構，包括主 Agent 工作流、各個子 Agent、LLM 調用和工具執行。請注意清晰的層級結構：主工作流 Agent Span 包含各種子 Agent 操作、LLM 調用和工具執行的子 Span。*

## 開始使用 AgentOps 和 ADK

將 AgentOps 整合到您的 ADK 應用程式中非常簡單：

1.  **安裝 AgentOps：**
    ```bash
    # 安裝或更新 AgentOps
    pip install -U agentops
    ```

2. **建立 API 金鑰**
    在此建立使用者 API 金鑰：[建立 API 金鑰](https://app.agentops.ai/settings/projects) 並配置您的環境：

    將您的 API 金鑰添加到環境變數中：
    ```bash
    # 設置 AgentOps API 金鑰
    AGENTOPS_API_KEY=<YOUR_AGENTOPS_API_KEY>
    ```

3.  **初始化 AgentOps：**
    在 ADK 應用程式腳本的開頭（例如，執行 ADK `Runner` 的主要 Python 文件）加入以下程式碼：

    ```python
    import agentops
    # 初始化 AgentOps 會話並自動追蹤 ADK Agent
    agentops.init()
    ```

    這將啟動一個 AgentOps 會話並自動追蹤 ADK Agent。

    詳細範例：

    ```python
    import agentops
    import os
    from dotenv import load_dotenv

    # 加載環境變數（可選，如果您使用 .env 文件來儲存 API 金鑰）
    load_dotenv()

    # 初始化 AgentOps
    agentops.init(
        api_key=os.getenv("AGENTOPS_API_KEY"), # 您的 AgentOps API 金鑰
        trace_name="my-adk-app-trace"  # 可選：為您的追蹤命名
        # 預設為 auto_start_session=True。
        # 如果您想手動控制會話的啟始/結束，請設置為 False。
    )
    ```

    > 🚨 🔑 您可以在註冊後的 [AgentOps 儀表板](https://app.agentops.ai/) 找到您的 AgentOps API 金鑰。建議將其設置為環境變數 (`AGENTOPS_API_KEY`)。

一旦完成初始化，AgentOps 將自動開始對您的 ADK Agent 進行儀器化 (Instrumenting)。

**這就是捕捉 ADK Agent 所有遙測數據所需的一切**

## AgentOps 如何對 ADK 進行儀器化

AgentOps 採用精密的策略來提供無縫的可觀測性，同時不與 ADK 的原生遙測產生衝突：

1.  **中和 ADK 的原生遙測：**
    AgentOps 會偵測 ADK 並智慧地修補 (Patch) ADK 的內部 OpenTelemetry 追蹤器（通常是 `trace.get_tracer('gcp.vertex.agent')`）。它將其替換為 `NoOpTracer`，確保 ADK 自身建立遙測 Span 的嘗試被有效地沉默。這可以防止重複追蹤，並允許 AgentOps 成為可觀測性數據的權威來源。

2.  **AgentOps 控制的 Span 建立：**
    AgentOps 通過包裝關鍵的 ADK 方法來控制並建立邏輯層級的 Span：

    *   **Agent 執行 Span（例如 `adk.agent.MySequentialAgent`）：**
        當 ADK Agent（如 `BaseAgent`、`SequentialAgent` 或 `LlmAgent`）啟動其 `run_async` 方法時，AgentOps 會為該 Agent 的執行啟動一個父 Span。

    *   **LLM 互動 Span（例如 `adk.llm.gemini-pro`）：**
        對於 Agent 向 LLM 發出的調用（透過 ADK 的 `BaseLlmFlow._call_llm_async`），AgentOps 會建立一個專用的子 Span，通常以 LLM 模型命名。此 Span 捕獲請求詳情（Prompt、模型參數），並在完成時（透過 ADK 的 `_finalize_model_response_event`）記錄響應詳情，如 Completion、Token 使用量和結束原因 (Finish Reasons)。

    *   **工具使用 Span（例如 `adk.tool.MyCustomTool`）：**
        當 Agent 使用工具時（透過 ADK 的 `functions.__call_tool_async`），AgentOps 會建立一個以工具命名的單一且全面的子 Span。此 Span 包含工具的輸入參數及其回傳的結果。

3.  **豐富的屬性收集：**
    AgentOps 重用了 ADK 的內部數據提取邏輯。它修補了 ADK 特定的遙測函數（例如 `google.adk.telemetry.trace_tool_call`、`trace_call_llm`）。這些函數的 AgentOps 包裝器獲取 ADK 收集的詳細資訊，並將其作為屬性附加到 *當前活動的 AgentOps Span*。

## 在 AgentOps 中可視化您的 ADK Agent

當您使用 AgentOps 對 ADK 應用程式進行儀器化時，您可以在 AgentOps 儀表板中獲得 Agent 執行的清晰層次視圖。

1.  **初始化：**
    當調用 `agentops.init()` 時（例如 `agentops.init(trace_name="my_adk_application")`），如果初始化參數 `auto_start_session=True`（預設為 true），則會建立一個初始父 Span。此 Span 通常命名為類似 `my_adk_application.session`，將成為該追蹤中所有操作的根節點。

2.  **ADK Runner 執行：**
    當 ADK `Runner` 執行頂層 Agent 時（例如編排工作流的 `SequentialAgent`），AgentOps 會在會話追蹤下建立一個對應的 Agent Span。此 Span 將反映頂層 ADK Agent 的名稱（例如 `adk.agent.YourMainWorkflowAgent`）。

3.  **子 Agent 與 LLM/工具調用：**
    當此主 Agent 執行其邏輯（包括調用子 Agent、LLM 或工具）時：
    *   每個 **子 Agent 執行** 將作為嵌套的子 Span 出現在其父 Agent 之下。
    *   對 **大型語言模型 (LLM)** 的調用將產生進一步嵌套的子 Span（例如 `adk.llm.<model_name>`），捕獲 Prompt 詳情、響應和 Token 使用量。
    *   **工具調用** 也會產生獨立的子 Span（例如 `adk.tool.<your_tool_name>`），顯示其參數和結果。

這建立了一個 Span 的瀑布流，讓您可以查看 ADK 應用程式中每個步驟的順序、持續時間和詳情。所有相關屬性，如 LLM Prompt、Completion、Token 計數、工具輸入/輸出和 Agent 名稱，都會被捕獲並顯示。

如需實際演示，您可以瀏覽範例 Jupyter Notebook，該筆記本展示了使用 Google ADK 和 AgentOps 的真人審核工作流：
[GitHub 上的 Google ADK 真人審核範例](https://github.com/AgentOps-AI/agentops/blob/main/examples/google_adk/human_approval.ipynb)。

此範例展示了具有工具使用的多步驟 Agent 流程如何在 AgentOps 中可視化。

## 優勢

*   **輕鬆設定：** 只需最少的程式碼更改即可獲得全面的 ADK 追蹤。
*   **深度可見性：** 了解複雜 ADK Agent 流程的內部運作方式。
*   **更快的除錯：** 透過詳細的追蹤數據快速定位問題。
*   **效能優化：** 分析延遲和 Token 使用情況。

透過整合 AgentOps，ADK 開發者可以顯著增強建立、除錯和維護穩健 AI Agent 的能力。

## 更多資訊

要開始使用，請[建立 AgentOps 帳戶](http://app.agentops.ai)。如需功能請求或錯誤報告，請透過 [AgentOps 儲存庫](https://github.com/AgentOps-AI/agentops) 與 AgentOps 團隊聯繫。

### 額外連結
- 🐦 [Twitter](http://x.com/agentopsai)
- 📢 [Discord](http://x.com/agentopsai)
- 🖇️ [AgentOps 儀表板](http://app.agentops.ai)
- 📙 [文件](http://docs.agentops.ai)

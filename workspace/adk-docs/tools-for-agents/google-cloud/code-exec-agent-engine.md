# 使用 Agent Engine 的程式碼執行工具

> 🔔 `更新日期：2026-01-26`
>
> 🔗 `資料來源：https://google.github.io/adk-docs/tools/google-cloud/code-exec-agent-engine/`

[`ADK 支援`: `Python v1.17.0` | `Preview`]

Agent Engine 程式碼執行 ADK 工具提供了一種低延遲、高效的方法，使用 [Google Cloud Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview) 服務來執行 AI 生成的程式碼。此工具專為快速執行而設計，量身定制於代理工作流（agentic workflows），並使用沙箱環境以提高安全性。程式碼執行工具允許程式碼和資料在多個請求中持久存在，從而實現複雜的多步驟編碼任務，包括：

-   **程式碼開發與偵錯：** 建立代理任務，在多個請求中測試和迭代程式碼版本。
-   **帶有資料分析的程式碼：** 上傳高達 100MB 的資料檔案，並運行多個基於程式碼的分析，而無需為每次程式碼運行重新載入資料。

此程式碼執行工具是 Agent Engine 套件的一部分，但您不必將代理部署到 Agent Engine 即可使用它。您可以在本地或其他服務上運行您的代理並使用此工具。有關 Agent Engine 中程式碼執行功能的更多資訊，請參閱 [Agent Engine 程式碼執行](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/code-execution/overview) 說明文件。

> [!NOTE] 預覽版本
Agent Engine 程式碼執行功能目前為預覽版本（Preview release）。如需更多資訊，請參閱 [產品發布階段說明](https://cloud.google.com/products#product-launch-stages)。

## 使用工具

使用 Agent Engine 程式碼執行工具要求您在使用 ADK 代理之前，先透過 Google Cloud Agent Engine 建立一個沙箱環境。

要在您的 ADK 代理中使用程式碼執行工具：

1.  按照 Agent Engine [程式碼執行快速入門](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/code-execution/quickstart) 中的說明建立程式碼執行沙箱環境。
2.  建立一個 ADK 代理，並配置設定以存取您建立沙箱環境的 Google Cloud 專案。
3.  以下程式碼範例顯示了配置為使用程式碼執行器工具的代理。請將 `SANDBOX_RESOURCE_NAME` 替換為您建立的沙箱環境資源名稱。

```python
from google.adk.agents.llm_agent import Agent
from google.adk.code_executors.agent_engine_sandbox_code_executor import AgentEngineSandboxCodeExecutor

# 初始化根代理
root_agent = Agent(
    model="gemini-2.5-flash",
    name="agent_engine_code_execution_agent",
    # 設定代理指令，使其能夠編寫並執行程式碼
    instruction="您是一個樂於助人的代理，能撰寫並執行程式碼來回答問題並解決問題。",
    # 配置程式碼執行器，指向特定的 Agent Engine 沙箱
    code_executor=AgentEngineSandboxCodeExecutor(
        sandbox_resource_name="SANDBOX_RESOURCE_NAME",
    ),
)
```

有關 `sandbox_resource_name` 值的預期格式，以及替代的 `agent_engine_resource_name` 參數的詳細資訊，請參閱 [配置參數](#配置參數)。如需更進階的範例（包括工具的建議系統指令），請參閱 [進階範例](#進階範例) 或完整的 [代理程式碼範例](https://github.com/google/adk-python/tree/main/contributing/samples/agent_engine_code_execution)。

## 運作方式

`AgentEngineCodeExecutor` 工具在代理任務期間維護單個沙箱，這意味著沙箱的狀態會在 ADK 工作流工作階段（session）內的所有操作中持久存在。

1.  **沙箱建立：** 對於需要執行程式碼的多步驟任務，Agent Engine 會建立一個具有指定語言和機器配置的沙箱，隔離程式碼執行環境。如果沒有預先建立沙箱，程式碼執行工具將使用預設設定自動建立一個。
2.  **具持久性的程式碼執行：** 工具調用的 AI 生成程式碼會串流傳輸到沙箱，然後在隔離環境中執行。執行後，沙箱在同一工作階段內的後續工具調用中*保持活動狀態*，為來自同一代理的下一次工具調用保留變數、導入的模組和檔案狀態。
3.  **結果檢索：** 收集標準輸出（stdout）和任何擷取的錯誤串流（stderr），並傳回給調用代理。
4.  **沙箱清理：** 一旦代理任務或對話結束，代理可以顯式刪除沙箱，或依賴建立沙箱時指定的沙箱 TTL 功能。

## 主要優勢

-   **持久狀態：** 解決複雜任務，其中資料操作或變數上下文必須在多次工具調用之間傳遞。
-   **與目標隔離：** 提供強大的處理程序層級（process-level）隔離，確保工具程式碼執行安全且保持輕量級。
-   **Agent Engine 整合：** 緊密整合到 Agent Engine 的工具使用和編排層中。
-   **低延遲效能：** 專為速度而設計，允許代理高效執行複雜的工具使用工作流，而不會產生顯著開銷。
-   **靈活的運算配置：** 建立具有特定程式語言、處理能力和記憶體配置的沙箱。

## 系統需求

成功在您的 ADK 代理中使用 Agent Engine 程式碼執行工具必須滿足以下需求：

-   已啟用到 Vertex API 的 Google Cloud 專案。
-   代理的服務帳戶需要 **roles/aiplatform.user** 角色，這允許其：
    -   建立、取得、列出和刪除程式碼執行沙箱。
    -   在程式碼執行沙箱中執行程式碼。

## 配置參數

Agent Engine 程式碼執行工具具有以下參數。您必須設定以下資源參數之一：

-   **`sandbox_resource_name`**：它為每次工具調用所使用的現有沙箱環境的沙箱資源路徑。預期的字串格式如下：
    ```
    projects/{$PROJECT_ID}/locations/{$LOCATION_ID}/reasoningEngines/{$REASONING_ENGINE_ID}/sandboxEnvironments/{$SANDBOX_ENVIRONMENT_ID}

    # 範例：
    projects/my-vertex-agent-project/locations/us-central1/reasoningEngines/6842888880301111172/sandboxEnvironments/6545148888889161728
    ```
-   **`agent_engine_resource_name`**：工具建立沙箱環境的 Agent Engine 資源名稱。預期的字串格式如下：
    ```
    projects/{$PROJECT_ID}/locations/{$LOCATION_ID}/reasoningEngines/{$REASONING_ENGINE_ID}

    # 範例：
    projects/my-vertex-agent-project/locations/us-central1/reasoningEngines/6842888880301111172
    ```

您可以使用 Google Cloud Agent Engine 的 API，透過 Google Cloud 用戶端連線個別配置 Agent Engine 沙箱環境，包括以下設定：

-   **程式語言**，包括 Python 和 JavaScript。
-   **運算環境**，包括 CPU 和記憶體大小。

有關連接到 Google Cloud Agent Engine 並配置沙箱環境的更多資訊，請參閱 Agent Engine [程式碼執行快速入門](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/code-execution/quickstart#create_a_sandbox)。

## 進階範例

以下範例程式碼顯示了如何在 ADK 代理中實現程式碼執行器工具的使用。此範例包含一個 `base_system_instruction` 子句，用於設定程式碼執行的操作指南。此指令子句是選用的，但強烈建議使用，以從此工具獲得最佳結果。

```py
from google.adk.agents.llm_agent import Agent
from google.adk.code_executors.agent_engine_sandbox_code_executor import AgentEngineSandboxCodeExecutor

def base_system_instruction():
  """傳回：數據科學代理系統指令。"""

  return """
  # 指南

  **目標：** 協助使用者達成其數據分析目標，**並強調避免假設並確保準確性。** 達成該目標可能涉及多個步驟。當您需要生成程式碼時，您**不需要**一次性解決目標。每次僅生成下一步。

  **程式碼執行：** 所有提供的程式碼片段都將在沙箱環境中執行。

  **狀態化：** 所有程式碼片段都會執行，且變數會保留在環境中。您永遠不需要重新初始化變數。您永遠不需要重新載入檔案。您永遠不需要重新導入函式庫。

  **輸出可見性：** 務必列印程式碼執行的輸出以視覺化結果，特別是對於數據探索和分析。例如：
    - 要查看 pandas.DataFrame 的形狀，請執行：
      ```tool_code
      print(df.shape)
      ```
      輸出將呈現為：
      ```tool_outputs
      (49, 7)

      ```
    - 顯示數值計算的結果：
      ```tool_code
      x = 10 ** 9 - 12 ** 5
      print(f'{{x=}}')
      ```
      輸出將呈現為：
      ```tool_outputs
      x=999751168

      ```
    - 您**永遠不會**自己生成 ```tool_outputs。
    - 接著您可以使用此輸出來決定後續步驟。
    - 僅列印變數（例如：`print(f'{{variable=}}')`）。

  **不作假設：** **至關重要的是，避免對數據性質或欄位名稱做出假設。** 僅根據數據本身得出發現。務必使用從 `explore_df` 獲得的資訊來指導您的分析。

  **可用檔案：** 僅使用可用檔案清單中指定的可用檔案。

  **提示中的數據：** 某些查詢直接在提示中包含輸入數據。您必須將該數據解析為 pandas DataFrame。務必解析所有數據。永遠不要編輯提供給您的數據。

  **可回答性：** 某些查詢可能無法使用可用數據回答。在這種情況下，請告知使用者為什麼您無法處理其查詢，並建議滿足其請求所需的數據類型。
  """

# 初始化根代理
root_agent = Agent(
    model="gemini-2.5-flash",
    name="agent_engine_code_execution_agent",
    # 組合基礎系統指令與特定任務指令
    instruction=base_system_instruction() + """
    您需要透過查看對話中的數據和上下文來協助使用者處理其查詢。
    您的最終答案應總結與使用者查詢相關的程式碼和程式碼執行。

    您應包含回答使用者查詢的所有數據片段，例如來自程式碼執行結果的表格。
    如果您無法直接回答問題，則應遵循上述指南生成下一個步驟。
    如果可以透過撰寫任何程式碼直接回答問題，則應執行該操作。
    如果您沒有足夠的數據來回答問題，應要求使用者提供澄清。

    您永遠不應自行安裝任何套件，例如 `pip install ...`。
    繪製趨勢圖時，應確保依 x 軸對數據進行排序。
    """,
    code_executor=AgentEngineSandboxCodeExecutor(
        # 如果您已經有一個沙箱資源名稱，請替換它。
        sandbox_resource_name="SANDBOX_RESOURCE_NAME",
        # 如果未設定 sandbox_resource_name，請替換為用於建立沙箱的 agent engine 資源名稱：
        # agent_engine_resource_name="AGENT_ENGINE_RESOURCE_NAME",
    ),
)
```

有關使用此範例程式碼的 ADK 代理的完整版本，請參閱 [agent_engine_code_execution 範例](https://github.com/google/adk-python/tree/main/contributing/samples/agent_engine_code_execution)。

### 實作範例

-   [`Agent Engine Code Execution`](../../../python/agents/agent-engine-code-execution/): 展示如何使用 Agent Engine 程式碼執行工具來執行多步驟程式碼任務的完整代理範例。
# 使用 Agent Config 構建代理

🔔 `更新日期：2026-01-14`

[`ADK 支援`: `Python v1.11.0` | `Experimental`]

ADK Agent Config 功能讓您無需編寫程式碼即可構建 ADK 工作流。Agent Config 使用 YAML 格式的文本文件，包含代理的簡短描述，讓幾乎任何人都能組裝和運行 ADK 代理。以下是一個基本的 Agent Config 定義示例：

```yaml
name: assistant_agent
model: gemini-2.5-flash
description: 一個可以回答使用者問題的輔助代理。
instruction: 你是一個代理，負責協助回答使用者的各種問題。
```

您可以使用 Agent Config 文件構建更複雜的代理，這些代理可以包含函式（Functions）、工具（Tools）、子代理（Sub-Agents）等。本頁面介紹如何使用 Agent Config 功能構建和運行 ADK 工作流。有關 Agent Config 格式支持的語法和設置的詳細資訊，請參閱 [Agent Config 語法參考](https://google.github.io/adk-docs/api-reference/agentconfig/)。

> [!WARNING] 實驗性
    Agent Config 功能目前處於實驗階段，存在一些[已知限制](#已知限制)。我們歡迎您的[回饋](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=agent%20config)！

## 開始使用

本節介紹如何使用 ADK 和 Agent Config 功能設置並開始構建代理，包括安裝設置、構建代理和運行代理。

### 設置

您需要安裝 Google Agent Development Kit 庫，並提供生成式 AI 模型（如 Gemini API）的存取金鑰。本節提供了在運行帶有 Agent Config 文件的代理之前必須安裝和配置的詳細資訊。

> [!NOTE]
    Agent Config 功能目前僅支援 Gemini 模型。有關其他功能限制的更多資訊，請參閱[已知限制](#已知限制)。

要設置 ADK 以配合 Agent Config 使用：

1.  按照[安裝說明](../get-started/installation/python.md)安裝 ADK Python 庫。*目前需要 Python。* 有關更多資訊，請參閱[已知限制](#已知限制)。
2.  在終端機中運行以下命令，驗證是否已安裝 ADK：
    ```
    adk --version
    ```
    此命令應顯示您安裝的 ADK 版本。

> [!TIP]
    如果 `adk` 命令無法運行且未在第 2 步中列出版本，請確保您的 Python 環境已激活。在 Mac 和 Linux 的終端機中執行 `source .venv/bin/activate`。對於其他平台的命令，請參閱[安裝]../get-started/installation/python.md)頁面。

### 構建代理

您可以使用 Agent Config 構建代理，通過 `adk create` 命令創建代理的項目文件，然後編輯為您生成的 `root_agent.yaml` 文件。

要創建用於 Agent Config 的 ADK 項目：

1.  在終端機窗口中，運行以下命令創建一個基於配置的代理：
    ```
    adk create --type=config my_agent
    ```
    此命令會生成一個 `my_agent/` 文件夾，其中包含一個 `root_agent.yaml` 文件和一個 `.env` 文件。

2.  在 `my_agent/.env` 文件中，設置代理存取生成式 AI 模型和其他服務的環境變量：

    a.  對於通過 Google API 存取的 Gemini 模型，在文件中添加一行您的 API 金鑰：
    ```
    GOOGLE_GENAI_USE_VERTEXAI=0
    GOOGLE_API_KEY=<您的-Google-Gemini-API-金鑰>
    ```
    您可以從 Google AI Studio 的 [API Keys](https://aistudio.google.com/app/apikey) 頁面獲取 API 金鑰。

    b.  對於通過 Google Cloud 存取的 Gemini 模型，在文件中添加以下行：
    ```
    GOOGLE_GENAI_USE_VERTEXAI=1
    GOOGLE_CLOUD_PROJECT=<您的_gcp_專案>
    GOOGLE_CLOUD_LOCATION=us-central1
    ```
    有關創建 Cloud 專案的資訊，請參閱 Google Cloud 文檔中的[創建和管理專案](https://cloud.google.com/resource-manager/docs/creating-managing-projects)。

3.  使用文本編輯器編輯 Agent Config 文件 `my_agent/root_agent.yaml`，如下所示：

    ```yaml
    # yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
    name: assistant_agent
    model: gemini-2.5-flash
    description: 一個可以回答使用者問題的輔助代理。
    instruction: 你是一個代理，負責協助回答使用者的各種問題。
    ```

您可以通過參考 ADK [範例存儲庫](https://github.com/search?q=repo%3Agoogle%2Fadk-python+path%3A%2F%5Econtributing%5C%2Fsamples%5C%2F%2F+.yaml&type=code)或 [Agent Config 語法](https://google.github.io/adk-docs/api-reference/agentconfig/)參考來發現 `root_agent.yaml` 代理配置文件的更多配置選項。

### 運行代理

完成 Agent Config 的編輯後，您可以使用 Web 界面、命令行終端執行或 API 伺服器模式運行代理。

要運行由 Agent Config 定義的代理：

1.  在終端機中，導航到包含 `root_agent.yaml` 文件的 `my_agent/` 目錄。
2.  輸入以下命令之一來運行代理：
    -   `adk web` - 為您的代理運行 Web UI 界面。
    -   `adk run` - 在終端機中運行您的代理，不含用戶界面。
    -   `adk api_server` - 將您的代理作為可被其他應用程式使用的服務運行。

有關運行代理方式的更多資訊，請參閱[快速入門](https://google.github.io/adk-docs/get-started/quickstart/#run-your-agent)中的*運行您的代理*主題。有關 ADK 命令行選項的更多資訊，請參閱 [ADK CLI 參考](https://google.github.io/adk-docs/api-reference/cli/)。

## 配置示例

本節顯示了 Agent Config 文件的示例，以幫助您開始構建代理。有關更多且更完整的示例，請參閱 ADK [範例存儲庫](https://github.com/search?q=repo%3Agoogle%2Fadk-python+path%3A%2F%5Econtributing%5C%2Fsamples%5C%2F%2F+root_agent.yaml&type=code)。

### 內置工具示例

以下示例使用內置的 ADK 工具功能進行 Google 搜索，為代理提供功能。該代理會自動使用搜索工具來回應用戶請求。

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
name: search_agent
model: gemini-2.0-flash
description: 一個負責執行 Google 搜尋查詢並根據結果回答問題的代理。
instruction: 你是一個代理，負責執行 Google 搜尋查詢並根據搜尋結果回答問題。
tools:
  - name: google_search
```

有關更多詳細資訊，請參閱 [ADK 範例存儲庫](https://github.com/google/adk-python/blob/main/contributing/samples/tool_builtin_config/root_agent.yaml)中此範例的完整代碼。

### 自定義工具示例

以下示例使用以 Python 代碼構建的自定義工具，並列在配置文件的 `tools:` 部分中。代理使用此工具檢查用戶提供的數字列表是否為質數。

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
agent_class: LlmAgent
model: gemini-2.5-flash
name: prime_agent
description: 負責檢查數字是否為質數。
instruction: |
    你負責檢查數字是否為質數。
    當被要求檢查質數時，必須呼叫 check_prime 工具並傳入整數列表。
    請勿手動判斷質數。
    將質數檢查結果回傳給 root agent。
tools:
  - name: ma_llm.check_prime
```

有關更多詳細資訊，請參閱 [ADK 範例存儲庫](https://github.com/google/adk-python/blob/main/contributing/samples/multi_agent_llm_config/prime_agent.yaml)中此範例的完整代碼。

### 子代理示例

以下示例顯示了在 `sub_agents:` 部分中定義了兩個子代理，並在配置文件的 `tools:` 部分中顯示了一個示例工具。該代理確定用戶的需求，並委派給其中一個子代理來解決請求。子代理使用 Agent Config YAML 文件定義。

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
agent_class: LlmAgent
model: gemini-2.5-flash
name: root_agent
description: 提供程式與數學輔導的學習助理代理。
instruction: |
    你是一個學習助理，協助學生解決程式與數學相關問題。

    你會將程式相關問題委派給 code_tutor_agent，數學相關問題委派給 math_tutor_agent。

    請依照以下步驟執行：
    1. 若使用者詢問程式設計或編碼問題，請委派給 code_tutor_agent。
    2. 若使用者詢問數學概念或題目，請委派給 math_tutor_agent。
    3. 請始終提供清楚的解釋並鼓勵學習。
sub_agents:
  - config_path: code_tutor_agent.yaml
  - config_path: math_tutor_agent.yaml
```

有關更多詳細資訊，請參閱 [ADK 範例存儲庫](https://github.com/google/adk-python/blob/main/contributing/samples/multi_agent_basic_config/root_agent.yaml)中此範例的完整代碼。

## 部署 Agent Config

您可以使用與代碼型代理相同的程序，通過 [Cloud Run](../deployment/cloud-run.md) 和 [Agent Engine](../deployment/agent-engine/index.md) 部署 Agent Config 代理。有關如何準備和部署基於 Agent Config 的代理的更多資訊，請參閱 [Cloud Run](../deployment/cloud-run.md) 和 [Agent Engine](../deployment/agent-engine/index.md) 部署指南。

## 已知限制

Agent Config 功能目前處於實驗階段，包含以下限制：

-   **模型支持：** 目前僅支持 Gemini 模型。與第三方模型的整合正在進行中。
-   **編程語言：** Agent Config 功能目前僅支持用於工具和其他需要編程代碼的功能的 Python 代碼。
-   **ADK 工具支持：** Agent Config 功能支持以下 ADK 工具，但*並非所有工具都得到完全支持*：
    -   `google_search`
    -   `load_artifacts`
    -   `url_context`
    -   `exit_loop`
    -   `preload_memory`
    -   `get_user_choice`
    -   `enterprise_web_search`
    -   `load_web_page`：需要完整路徑來存取網頁。
-   **代理類型支持：** 尚不支持 `LangGraphAgent` 和 `A2aAgent` 類型。
    -   `AgentTool`
    -   `LongRunningFunctionTool`
    -   `VertexAiSearchTool`
    -   `McpToolset`
    -   `ExampleTool`

## 下一步

有關如何以及使用 ADK Agent Config 構建什麼的想法，請參閱 ADK [adk-samples](https://github.com/search?q=repo:google/adk-python+path:/%5Econtributing%5C/samples%5C//+root_agent.yaml&type=code) 存儲庫中基於 YAML 的代理定義。有關 Agent Config 格式支持的語法和設置的詳細資訊，請參閱 [Agent Config 語法參考](https://google.github.io/adk-docs/api-reference/agentconfig/)。

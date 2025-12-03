# Google ADK 訓練中心 - 課程模組

這份文件提供了 Google Agent Development Kit (ADK) 所有訓練模組的概覽。每個模組都旨在引導您學習 ADK 的特定功能，從基礎設定到進階的多代理系統。

| 名稱 | 檔案名稱 | 描述 | 標籤 |
| :--- | :--- | :--- | :--- |
| 設定與驗證 - Google ADK 入門 | [00-setup_authentication.md](./00-setup_authentication.md) | 引導使用者完成 Google ADK 開發環境的設定與驗證，並協助選擇適合的 Google AI 平台 (Vertex AI vs. Gemini API)。 | `setup`, `authentication`, `vertex-ai`, `gemini-api`, `gcloud`, `api-key` |
| Hello World Agent | [01-hello_world_agent.md](./01-hello_world_agent.md) | 從零開始，建立一個能與使用者進行簡單對話的 AI Agent。介紹 ADK 的核心概念與專案結構。 | `hello-world`, `agent`, `adk-basics`, `project-structure`, `dialogue-agent` |
| Function Tools - 賦予你的 Agent 超能力 | [02-function_tools.md](./02-function_tools.md) | 學習如何透過新增 Python 函式作為工具，賦予 Agent 自訂能力，讓 Agent 能根據使用者請求自動決定何時使用這些工具。 | `function-tools`, `python`, `tools`, `custom-abilities`, `parallel-execution` |
| OpenAPI Tools - REST API Integration | [03-openapi_tools.md](./03-openapi_tools.md) | 使用 OpenAPI 工具整合 REST API，讓 AI Agent 能夠自動與網路服務互動，無需手動編寫工具函式。 | `openapi`, `rest-api`, `integration`, `toolset`, `api-automation` |
| 循序工作流程 - Agent Pipelines | [04-sequential_workflows.md](./04-sequential_workflows.md) | 連接多個 agents 以建立一個循序執行的多步驟工作流程，介紹 `SequentialAgent` 與 `output_key` 的使用。 | `sequential-agent`, `workflow`, `pipeline`, `multi-agent`, `state-management` |
| 平行處理 - 同時執行多個代理 | [05-parallel_processing.md](./05-parallel_processing.md) | 學習如何使用 `ParallelAgent` 同時執行多個獨立的代理，並介紹扇出/收集 (fan-out/gather) 模式以提升效率。 | `parallel-agent`, `workflow`, `fan-out-gather`, `multi-agent`, `performance` |
| 多代理系統 - 複雜的協調流程 | [06-multi_agent_systems.md](./06-multi_agent_systems.md) | 結合循序與並行代理，建構能夠處理複雜現實世界任務的精密多代理系統，並使用 `google_search` 工具進行真實研究。 | `multi-agent-systems`, `orchestration`, `nested-workflows`, `google-search` |
| 循環代理 (Loop Agents) - 迭代優化 | [07-loop_agents.md](./07-loop_agents.md) | 使用 `LoopAgent` 來建構能夠自我改進的代理系統，介紹「批評者 → 優化者」模式以進行迭代優化。 | `loop-agent`, `iterative-optimization`, `self-correction`, `critic-refiner` |
| State and Memory - 持久化代理上下文 | [08-state_memory.md](./08-state_memory.md) | 使用會話狀態 (`session.state`) 與長期記憶體 (`MemoryService`) 來建構能夠跨互動記住資訊的代理。 | `state-management`, `memory`, `persistence`, `session-state`, `user-context` |
| Callbacks and Guardrails - 代理安全與監控 | [09-callbacks_guardrails.md](./09-callbacks_guardrails.md) | 使用回呼 (callbacks) 在特定的執行點觀察、客製化和控制代理行為，以實現安全護欄、日誌記錄和監控。 | `callbacks`, `guardrails`, `safety`, `monitoring`, `observability`, `security` |
| 評估與測試 - Agent 品質保證 | [10-evaluation_testing.md](./10-evaluation_testing.md) | 使用 `pytest` 和 `AgentEvaluator` 系統性地測試和評估 AI agents，涵蓋軌跡和回應品質。 | `evaluation`, `testing`, `pytest`, `agent-evaluator`, `quality-assurance` |
| 內建工具與基礎 (Built-in Tools & Grounding) | [11-built_in_tools_grounding.md](./11-built_in_tools_grounding.md) | 使用 Gemini 2.0+ 的內建工具 (`google_search`, `google_maps_grounding`) 進行網路基礎，讓代理程式能夠存取最新資訊。 | `built-in-tools`, `grounding`, `google-search`, `google-maps`, `real-time-data` |
| 規劃器與思維 (Planners and Thinking) | [12-planners_thinking.md](./12-planners_thinking.md) | 掌握使用內建規劃器 (`BuiltInPlanner`, `PlanReActPlanner`) 和思維設定 (`ThinkingConfig`) 的進階推理能力。 | `planners`, `thinking`, `reasoning`, `plan-react`, `strategic-planning` |
| 程式碼執行 - 動態 Python 程式碼生成 | [13-code_execution.md](./13-code_execution.md) | 讓代理程式能夠使用 Gemini 2.0+ 內建的程式碼執行功能，編寫並執行 Python 程式碼以進行精確計算和資料分析。 | `code-execution`, `python`, `dynamic-code`, `computation`, `data-analysis` |
| 串流與伺服器發送事件 (Streaming and SSE) | [14-streaming_sse.md](./14-streaming_sse.md) | 實作使用伺服器發送事件 (SSE) 的串流回應，以提供即時、漸進式的輸出，改善使用者體驗。 | `streaming`, `sse`, `real-time`, `progressive-output`, `ux` |
| Live API 與音訊 - 即時語音互動 | [15-live_api_audio.md](./15-live_api_audio.md) | 使用 Gemini 的 Live API 建立支援語音的代理程式，以進行即時音訊串流和語音對話。 | `live-api`, `audio`, `voice`, `real-time`, `streaming` |
| 模型內容協議 (MCP) 整合 | [16-mcp_integration.md](./16-mcp_integration.md) | 使用模型內容協議 (MCP) 將外部工具和服務 (如檔案系統) 整合到代理程式中，擴展代理程式的功能。 | `mcp`, `integration`, `standard-protocol`, `toolset`, `filesystem` |
| 代理人對代理人通訊 - 分散式系統 | [17-agent_to_agent.md](./17-agent_to_agent.md) | 透過代理人對代理人（agent-to-agent）的通訊、委派和協調，建構分散式代理人系統，以實現複雜的多代理人協同作業。 | `agent-to-agent`, `distributed-systems`, `delegation`, `coordination`, `multi-agent` |
| 事件與可觀察性 - Agent 監控 | [18-events_observability.md](./18-events_observability.md) | 為 Agent 實作全面的可觀察性，包括事件追蹤、指標收集和用於生產系統的監控儀表板。 | `advanced`, `observability`, `monitoring`, `events`, `metrics` |
| Artifacts與檔案 - 內容生成與管理 | [19-artifacts_files.md](./19-artifacts_files.md) | 使用代理程式生成和管理檔案、文件和Artifacts，以應用於內容創建、程式碼生成和檔案處理工作流程。 | `advanced`, `artifacts`, `files`, `content-generation`, `file-management` |
| YAML 代理配置 - 宣告式設定 | [20-yaml_configuration.md](./20-yaml_configuration.md) | 掌握使用 YAML 檔案進行宣告式代理配置，無需編寫 Python 程式碼即可定義代理、工具和行為，實現快速原型設計和配置管理。 | `yaml`, `configuration`, `declarative`, `setup`, `rapid-prototyping` |
| 多模態與影像處理 - 視覺 AI 代理 | [21-multimodal_image.md](./21-multimodal_image.md) | 掌握多模態功能，包括影像輸入/輸出、視覺理解，以及使用 Gemini 模型和 Vertex AI Imagen 進行影像生成。 | `multimodal`, `image-processing`, `vision`, `visual-ai`, `gemini` |
| 模型選擇 - 選擇正確的 AI 模型 | [22-model_selection.md](./22-model_selection.md) | 學習選擇和設定不同的 AI 模型，包括 Gemini 變體、最佳化策略和模型特定設定。 |  `model`, `gemini`, `selection`, `optimization`, `recommendation` |
| 生產部署策略 - 規模化與安全性 | [23-production_deployment.md](./23-production_deployment.md) | 了解 ADK 部署選項，並實作具有自訂驗證、監控和可靠性模式的生產級 Agent。 | `production`, `deployment`, `cloud-run`, `agent-engine`, `gke`, `security`, `monitoring` |
| 進階可觀測性 - 企業級監控 | [24-advanced_observability.md](./24-advanced_observability.md) | 掌握進階可觀測性模式，包括外掛系統、Cloud Trace 整合、自訂指標、分散式追蹤以及生產環境監控儀表板。 | `plugins`, `observability`, `monitoring`, `dashboard`, `tracing` |
| 最佳實務 - 生產級代理開發 | [25-best_practices.md](./25-best_practices.md) | 掌握生產級模式、架構決策、最佳化策略、安全性最佳實務，以及建構強大代理系統的綜合指南。 | `advanced`, `best-practices`, `production`, `security`, `performance` |
| Gemini Enterprise - 企業級代理管理 | [26-google_agentspace.md](./26-google_agentspace.md) | 了解如何使用 Google Cloud 的 Gemini Enterprise (前身為 AgentSpace) 平台來大規模部署、管理和治理企業級 AI 代理。 | `gemini-enterprise`, `agentspace`, `deployment`, `governance`, `enterprise`, `management` |
| 第三方工具 - 外部服務整合 | [27-third_party_tools.md](./27-third_party_tools.md) | 使用 REST API、SDK 和自訂工具集將第三方服務和工具整合到代理中，以擴充功能。 | `third-party`, `integration`, `langchain`, `crewai`, `external-services` |
| 使用其他大型語言模型 - 多模型支援 | [28-using_other_llms.md](./28-using_other_llms.md) | 設定代理程式以使用不同的 LLM 供應商，包括 OpenAI、Anthropic 和本地模型，以實現多樣化的 AI 功能。 | `advanced`, `llms`, `multi-model`, `providers`, `configuration` |
| UI 整合與 AG-UI 協議簡介 | [29-ui_integration_intro.md](./29-ui_integration_intro.md) | 學習如何將 Google ADK 代理與使用者介面整合，涵蓋 AG-UI 協議、多種整合方法 (React/Next.js, Streamlit, Slack) 以及架構模式與最佳實踐。 | `ui-integration`, `ag-ui`, `copilotkit`, `react`, `nextjs`, `frontend` |
| Next.js ADK 整合 - React 聊天介面 | [30-nextjs_adk_integration.md](./30-nextjs_adk_integration.md) | 使用 Next.js 15 和 CopilotKit 建構現代化聊天介面，建立具有即時功能和 AG-UI 協定的 React Agent 互動，包含生成式 UI 與人機協作功能。 | `ui`, `nextjs`, `react`, `copilotkit`, `chat-interface` |
| React Vite ADK 整合 - 自訂 UI 協定 | [31-react_vite_adk_integration.md](./31-react_vite_adk_integration.md) | 使用 React Vite 和 AG-UI 協定建構自訂 UI，不依賴 CopilotKit，實現手動 SSE 串流、TOOL_CALL_RESULT 處理及固定側邊欄圖表功能。 | `ui`, `react`, `vite`, `ag-ui`, `custom-implementation` |
| Streamlit ADK 整合 - Python 數據應用 | [32-streamlit_adk_integration.md](./32-streamlit_adk_integration.md) | 使用 Streamlit 和 ADK 構建純 Python 的數據分析應用程式，整合互動式儀表板、數據分析工具與 ADK Agents，無需前端開發經驗。 | `ui`, `streamlit`, `python`, `data-science`, `dashboard` |
| 進階 01. GEPA 優化 | [36-gepa_optimization_advanced.md](./36-gepa_optimization_advanced.md) | 學習使用基因演化提示詞增強（GEPA）技術，透過遺傳演算法、反思和評估來自動優化大型語言模型的提示詞。 | `advanced`, `gepa`, `prompt-engineering`, `optimization`, `genetic-algorithms` |

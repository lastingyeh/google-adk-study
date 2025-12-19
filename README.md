# Google ADK 學習路線圖

## 概述

此儲存庫包含學習 Google ADK（代理開發工具包）的完整路線圖。此路線圖旨在引導學習者掌握有效使用 Google ADK 構建智能代理所需的重要主題和技能。

## 學習看板

### 🔗 **Dashboard 連結 ➡** [https://lastingyeh.github.io/google-adk-study/](https://lastingyeh.github.io/google-adk-study/)

### 🗓️ 第 1-30 天：ADK 核心基礎

<details>
<summary>第一階段：涵蓋 ADK 核心定義、範例專案實作、工作流程編排 (循序、並行、循環)、狀態管理與測試評估。</summary>

#### 🕗 Day 1

<details>
<summary>
了解 Google ADK 核心定義，在社群資源中匯集了由 Agent Development Kit (ADK) 社群所建立和維護的各類資源。內容涵蓋了入門教學、深度課程、代理程式開發的教學與示範、Java 版本的 ADK 資源，以及多國語言的文件翻譯。此外，頁面也提供了如何貢獻自己資源的指南，鼓勵社群成員參與並豐富 ADK 的生態系。

🏷️ `adk-basics`, `community`, `getting-started`

</summary>

- **詳細說明**：
  - [文件連結](./docs/google-adk-docs-community_summary.md)
- **參考資源**
  - [Google ADK Getting Started ](https://google.github.io/adk-docs/community/#getting-started)
  - [Getting Started with Agent Development Kit Tools (MCP, Google Search, LangChain, etc.)](https://www.youtube.com/watch?v=5ZmaWY7UX6k)
  - [software-bug-assistant](https://github.com/google/adk-samples/tree/main/python/agents/software-bug-assistant)
  - [Tools Make an Agent: From Zero to Assistant with ADK](https://cloud.google.com/blog/topics/developers-practitioners/tools-make-an-agent-from-zero-to-assistant-with-adk?e=48754805?utm_source%3Dtwitter?utm_source%3Dlinkedin)
  - [Tools for Agents: ADK Tools list](https://google.github.io/adk-docs/tools/)

</details>

#### 🕗 Day 2

<details>
<summary>
設計 copilot 互動教學設計模式，取得目標學習專案的相關資源，並設計互動式教學模式以協助學習者更有效地掌握專案內容。

🏷️ `copilot`, `learning-design`, `interactive-tutorial`

</summary>

- **詳細說明**：
  - [文件連結](.github/agents/repo-guiding-learning.chatmode.agent.md)
- **參考資源**
  - [Getting Started with Agent Development Kit Tools (MCP, Google Search, LangChain, etc.)](https://www.youtube.com/watch?v=5ZmaWY7UX6k)
  - [專案相依連結](./workspace/python/agents/software-bug-assistant/README.md)

</details>

#### 🕗 Day 3

<details>
<summary>
實做範例 software-bug-assistant 專案，了解如何使用 Google ADK 建立一個能夠協助識別和修復軟體錯誤的智能代理。此專案展示了 ADK 的強大功能，並提供了實際應用的範例，幫助學習者深入理解代理程式的設計與實作過程。

🏷️ `software`, `bug-assistant`, `implementation`, `postgres`

</summary>

- **詳細說明**：
  - [環境初始化流程](./workspace/python/agents/software-bug-assistant/docs/INSTALLATION_GUIDE.md)
  - [Software Bug Assistant](./workspace/python/agents/software-bug-assistant/)
- **參考資源**
  - [Software Bug Assistant - ADK Python Sample Agent](https://github.com/google/adk-samples/tree/main/python/agents/software-bug-assistant)

</details>

#### 🕗 Day 4

<details>
<summary>
實做範例 youtube-shorts-agent 專案，了解如何使用 Google ADK 建立一個能夠協助生成和管理 YouTube Shorts 內容的智能代理。此專案展示了 ADK 的強大功能，並提供了實際應用的範例，幫助學習者深入理解代理程式的設計與實作過程。

🏷️ `sub-agents`, `youtube-shorts`, `implementation`, `assistant`, `loop-agent`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/python/agents/youtube-shorts-assistant/README.md)
  - [Youtube Shorts Assistant](./workspace/python/agents/youtube-shorts-assistant/)
- **參考資源**
  - [Getting started with Agent Development Kit](https://www.youtube.com/watch?v=44C8u0CDtSo)
  - [Google ADK Training Hub](https://raphaelmansuy.github.io/adk_training/)

</details>

#### 🕗 Day 5

<details>
<summary>
實現範例 finance-assistant 專案，了解如何使用 Google ADK 建立一個能夠協助管理和分析財務數據的智能代理。包含基本 ADK Tools 的應用，並透過 asyncio.gather(*tasks) 平行處理任務與完整 Agent 測試案例實現。

🏷️ `function-tools`, `python`, `tools`, `custom-abilities`, `parallel-execution`

</summary>

- **詳細說明**：

  - [文件連結](./workspace/python/agents/finance-assistant/README.md)
  - [Finance Assistant](./workspace/python/agents/finance-assistant/)

- **參考資源**
  - [Tutorial 02: Function Tools Implementation](https://github.com/raphaelmansuy/adk_training/tree/main/tutorial_implementation/tutorial02)
  - [Tutorial 02: Function Tools - Give Your Agent Superpowers](https://raphaelmansuy.github.io/adk_training/docs/function_tools)

</details>

#### 🕗 Day 6

<details>
<summary>
本教學介紹如何使用 OpenAPI 工具將 AI 代理程式連接到 RESTful Web API。內容涵蓋 OpenAPI 規範基礎、ADK 中的 OpenAPIToolset 使用方法，以及如何配置和調用外部 API。透過實作 Chuck Norris Agent 範例，展示如何利用 OpenAPI 工具擴展代理的功能，實現與外部服務的互動。

🏷️ `openapi`, `rest-api`, `integration`, `toolset`, `api-automation`

</summary>

- **詳細說明**：

  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/03-openapi_tools.md)
  - [Chuck Norris Agent](./workspace/python/agents/chuck-norris-agent/)

- **參考資源**
  - [Tutorial 03: OpenAPI Tools - Connect Your Agent to Web APIs](https://raphaelmansuy.github.io/adk_training/docs/openapi_tools/)
  - [Tutorial 03: Chuck Norris OpenAPI Tools Agent](https://github.com/raphaelmansuy/adk_training/tree/main/tutorial_implementation/tutorial03/)

</details>

#### 🕗 Day 7

<details>
<summary>
本教學介紹 Gemini 2.0+ 的內建工具,包含網路搜尋、地圖定位和企業搜尋功能,讓 AI 代理程式存取即時資訊。核心內容涵蓋:google_search 網路基礎工具、google_maps_grounding 位置服務(需 VertexAI)、enterprise_web_search 企業搜尋、GoogleSearchAgentTool 混合工具解決方案。同時介紹記憶體管理、工作流程控制、上下文載入等進階工具。透過實作研究助理範例,展示如何整合多種工具建立生產級代理程式系統,包含最佳實踐與疑難排解指南。

🏷️ `built-in-tools`, `grounding`, `google-search`, `google-maps`, `real-time-data`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/11-built_in_tools_grounding.md)
  - [Grounding Agent](./workspace/python/agents/grounding-agent/)
- **參考資源**
  - [Tutorial 11: Built-in Tools & Grounding](https://raphaelmansuy.github.io/adk_training/docs/built_in_tools_grounding)

</details>

#### 🕗 Day 8

<details>
<summary>
本教學介紹如何使用模型內容協議 (MCP) 將外部工具和服務整合到 AI 代理程式中。透過 MCPToolset 連接 MCP 伺服器，讓代理程式能夠存取檔案系統、資料庫、API 等外部資源，並支援 OAuth 驗證與人機迴圈審批等進階功能。

🏷️ `mcp`, `integration`, `standard-protocol`, `toolset`, `filesystem`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/16-mcp_integration.md)
  - [MCP Agent](./workspace/python/agents/mcp-agent/)
- **參考資源**
  - [Tutorial 16: Model Context Protocol (MCP) Integration](https://raphaelmansuy.github.io/adk_training/docs/mcp_integration)

</details>

#### 🕗 Day 9

<details>
<summary>
Google ADK 工作流程編排核心-三大模式：順序流程處理依賴任務，並行流程提升執行效率，迴圈流程迭代優化品質。組合策略：透過巢狀工作流程實現複雜代理編排，解決真實世界多步驟問題。

🏷️ `workflow`, `orchestration`, `sequential-agent`, `parallel-agent`, `loop-agent`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/workflows-orchestration.md)
- **參考資源**
  - [Workflows & Orchestration](https://raphaelmansuy.github.io/adk_training/docs/workflows-orchestration)

</details>

#### 🕗 Day 10

<details>
<summary>
根據文件內容，這是一份關於 Google ADK 循序工作流程的教學，說明如何使用 `SequentialAgent` 連接多個 agents 建立部落格文章產生 pipeline。透過研究、寫作、編輯、格式化四個階段，展示如何使用 `output_key` 在 agents 間傳遞資料，適合需要按順序執行的任務流程。

🏷️ `sequential-agent`, `workflow`, `pipeline`, `multi-agent`, `state-management`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/04-sequential_workflows.md)
  - [Blog Creation Pipeline](./workspace/python/agents/blog-pipeline/)
- **參考資源**
  - [Tutorial 04: Sequential Workflows - Build Agent Pipelines](https://raphaelmansuy.github.io/adk_training/docs/sequential_workflows)

</details>

#### 🕗 Day 11

<details>
<summary>
本教學介紹 `ParallelAgent` 同時執行多個獨立代理以提升效率，並運用「扇出/收集」模式：先平行收集資料（航班、飯店、活動），再循序合併結果成完整行程。適用於 I/O 密集型任務與多源資料收集。

🏷️ `parallel-agent`, `workflow`, `fan-out-gather`, `multi-agent`, `performance`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/05-parallel_processing.md)
  - [Travel Planner](./workspace/python/agents/travel-planner/)
- **參考資源**
  - [Tutorial 05: Parallel Processing - Run Multiple Agents Simultaneously](https://raphaelmansuy.github.io/adk_training/docs/parallel_processing)

</details>

#### 🕗 Day 12

<details>
<summary>
本教學示範建構複雜的多代理協調流程，結合並行與循序模式。以內容發布系統為例，採用扇出/收集架構：並行執行新聞、社群、專家三個研究管線，再循序進行內容創作、編輯、格式化，實現速度與品質兼顧的智能協作系統。

🏷️ `multi-agent-systems`, `orchestration`, `nested-workflows`, `google-search`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/06-multi_agent_systems.md)
  - [Content Publisher](./workspace/python/agents/content-publisher/)
  - [Content Publisher Agent Architecture](./workspace/python/agents/content-publisher/agent_architecture.md)
- **參考資源**
  - [Tutorial 06: Multi-Agent Systems - Agents Working Together](https://raphaelmansuy.github.io/adk_training/docs/multi_agent_systems/)

</details>

#### 🕗 Day 13

<details>
<summary>
教學 07：循環代理文章精煉系統 - 使用 LoopAgent 實現自我改進的代理系統，透過評論者-精煉者模式進行迭代品質提升，具備智慧終止機制和完整測試覆蓋（62個測試），展示循環代理的實際應用。

🏷️ `loop-agent`, `iterative-optimization`, `self-correction`, `critic-refiner`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/07-loop_agents.md)
  - [Essay Refiner](./workspace/python/agents/essay-refiner/)
- **參考資源**
  - [Tutorial 07: Loop Agents - Iterative Refinement with Critic/Refiner Patterns](https://raphaelmansuy.github.io/adk_training/docs/loop_agents)

</details>

#### 🕗 Day 14

<details>
<summary>
本系列涵蓋 ADK 核心能力：LLM 整合篇教授提示工程、接地技術（網路/資料/位置）、思維推理框架（內建思考、Plan-ReAct）、多輪對話及性能優化；生產部署篇介紹四種部署環境、可觀測性監控、服務組態與安全實踐；進階模式篇探討即時串流、MCP 協定、A2A 通訊及多模態整合；決策框架篇提供代理類型、工具選擇、部署策略的完整決策矩陣與實施清單，助您從開發到生產全面掌握 Google ADK。

🏷️ `core-concepts`, `deployment`, `advanced-patterns`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/overview.md)
- **參考資源**
  - [LLM Integration](https://raphaelmansuy.github.io/adk_training/docs/llm-integration)
  - [Production & Deployment](https://raphaelmansuy.github.io/adk_training/docs/production-deployment)
  - [Advanced Patterns](https://raphaelmansuy.github.io/adk_training/docs/advanced-patterns)
  - [Decision Frameworks](https://raphaelmansuy.github.io/adk_training/docs/decision-frameworks)

</details>

#### 🕗 Day 15

<details>
<summary>
本資料提供 Google Agent Development Kit (ADK) 完整學習路徑，涵蓋從初學者到專家的 8 階段進程（57+ 天），包括代理建立、工作流程模式（Sequential/Parallel/Loop）、工具整合、狀態管理、生產部署等核心技能。附有快速參考備忘單，提供代碼範例、CLI 指令、最佳實踐與疑難排解，適合 AI 應用開發者系統學習與實作。

🏷️ `learning-path`, `cheat-sheet`, `reference`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/learning-paths.md)
- **參考資源**
  - [Learning Paths](https://raphaelmansuy.github.io/adk_training/docs/learning-paths)
  - [ADK Cheat Sheet - Complete Reference](https://raphaelmansuy.github.io/adk_training/docs/adk-cheat-sheet)

</details>

#### 🕗 Day 16

<details>
<summary>
涵蓋驗證與平台選擇、入門範例建置、代理模式(循序平行迴圈)、工具整合、狀態管理、部署、安全權限、測試監控及最佳實務，並含成本管理、事件追蹤、錯誤處理與常見問題。

🏷️ `setup`, `authentication`, `hello-world`, `agent`, `adk-basics`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/reference-guide.md)
  - [00-setup_authentication](./workspace/notes/google-adk-training-hub/adk_training/00-setup_authentication.md)
  - [01-hello_world_agent](./workspace/notes/google-adk-training-hub/adk_training/01-hello_world_agent.md)
  - [hello-agent](./workspace/python/agents/hello-agent/)
- **參考資源**
  - [reference Guide](https://raphaelmansuy.github.io/adk_training/docs/reference-guide)
  - [Tutorial 00: Setup & Authentication - Getting Started with Google ADK](https://raphaelmansuy.github.io/adk_training/docs/setup_authentication)
  - [Tutorial 01: Hello World Agent - Build Your First AI Agent with Google ADK](https://raphaelmansuy.github.io/adk_training/docs/hello_world_agent)

</details>

#### 🕗 Day 17

<details>
<summary>
教學示範建構個人化導師：利用會話狀態與 user/app/temp 前綴記錄偏好、主題與測驗分數，搜尋過往會話支援進度回顧與自適應教學。

🏷️ `state-management`, `memory`, `persistence`, `session-state`, `user-context`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/08-state_memory.md)
  - [personal tutor](./workspace/python/agents/personal-tutor/)
- **參考資源**
  - [Tutorial 08: State Memory - Managing Conversation Context and Data](https://raphaelmansuy.github.io/adk_training/docs/state_memory)

</details>

#### 🕗 Day 18

<details>
<summary>
教學介紹ADK代理回呼：生命週期、模型、工具六鉤子；可阻擋不當內容、驗證參數、過濾PII、記錄與追蹤指標；示範內容審核助理實作護欄、安全指令、狀態管理與最佳實務。強化安全控制模式與錯誤處理測試範例涵蓋

🏷️ `callbacks`, `guardrails`, `safety`, `monitoring`, `observability`, `security`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/09-callbacks_guardrails.md)
  - [content moderator](./workspace/python/agents/content-moderator/)
- **參考資源**
  - [Tutorial 09: Callbacks & Guardrails - Control Flow and Monitoring](https://raphaelmansuy.github.io/adk_training/docs/callbacks_guardrails)

</details>

#### 🕗 Day 19

<details>
<summary>
本教學介紹如何使用 pytest 和 AgentEvaluator 系統性地測試 AI agents。涵蓋測試金字塔架構:單元測試(77%)驗證工具函式與設定、整合測試(9%)驗證工作流程協調、評估測試(14%)使用 AgentEvaluator 評估軌跡與回應品質。重點在於 AI agents 的非確定性特性需要質化評估而非傳統斷言測試。提供完整實作範例,包含 22 個綜合測試、EvalSet JSON 結構描述,以及生產環境最佳實踐。

🏷️ `evaluation`, `testing`, `pytest`, `agent-evaluator`, `quality-assurance`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/10-evaluation_testing.md)
  - [Support Agent](./workspace/python/agents/support-agent/)
- **參考資源**
  - [Tutorial 10: Evaluation & Testing - Quality Assurance for Agents](https://raphaelmansuy.github.io/adk_training/docs/evaluation_testing)

</details>

#### 🕗 Day 20

<details>
<summary>
本教學介紹 ADK 進階推理能力，包含三種規劃器：BuiltInPlanner 利用 Gemini 2.0+ 原生思維能力進行透明推理；PlanReActPlanner 提供結構化的計畫→推理→行動→觀察→重新規劃流程；BasePlanner 可建立自訂規劃策略。透過 ThinkingConfig 控制思維過程的顯示。規劃器讓代理在行動前先思考，提升複雜問題的推理品質與準確性，適用於多步驟工作流程與策略性問題解決。

🏷️ `planners`, `thinking`, `reasoning`, `plan-react`, `strategic-planning`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/12-planners_thinking.md)
  - [Strategic Solver](./workspace/python/agents/strategic-solver/)
- **參考資源**
  - [Tutorial 12: Planners & Thinking Configuration](https://raphaelmansuy.github.io/adk_training/docs/planners_thinking)

</details>

#### 🕗 Day 21

<details>
<summary>
本教學介紹了如何利用 Gemini 2.0+ 的 BuiltInCodeExecutor 功能，讓 AI 代理能夠動態生成並執行 Python 程式碼。此功能使代理能夠在 Google 安全的沙箱環境中進行精確的數學計算、資料分析和複雜運算，解決了大型語言模型在精確度上的限制。內容涵蓋了基本用法、實際應用（如財務計算機），並強調了與傳統函式工具相比的靈活性與強大功能，同時也說明了其安全考量與最佳實踐。

🏷️ `code-execution`, `python`, `dynamic-code`, `computation`, `data-analysis`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/13-code_execution.md)
  - [Code Calculator](./workspace/python/agents/code-calculator/)
- **參考資源**
  - [Tutorial 13: Code Execution - Dynamic Python Code Generation](https://raphaelmansuy.github.io/adk_training/docs/code_execution/)

</details>

#### 🕗 Day 22

<details>
<summary>
兩大主題說明：

- Google ADK v1.18.0 推出了視覺化代理建構器，一個無程式碼的網頁介面，用於設計、設定和測試複雜的多代理系統。使用者可以透過拖放方式建立工作流程，或利用 Gemini 驅動的 AI 助理，以自然語言描述需求來自動生成完整的代理架構。此工具會產生標準的 ADK YAML 設定檔，加速了原型設計和開發流程，但目前仍處於早期版本，可能存在一些小問題。
- 傳統 MCP 因載入全部工具定義與原始資料而浪費 Token，導致成本高昂且易出錯。新範式「程式碼執行」(MCP 2.0)讓 AI 撰寫程式碼，僅處理必要工具與資料，最終結果才返回上下文，能節省 98% Token，大幅提升效率、可靠性與隱私。

🏷️ `visual-builder`, `no-code`, `mcp`

</summary>

- **詳細說明**：
  - [Building AI Agents Visually with Google ADK Visual Agent Builder 完整內容整理](./workspace/articles/google-adk-visual-agent-builder/building-ai-agents-visually-with-google-adk-visual-agent-builder.md)
  - [ADK Course #8 - NEW Visual Agent Builder | Agent Development Kit (ADK) 影片重點整理](<./workspace/articles/google-adk-visual-agent-builder/theailanguage-No-Code%20Visual%20Agent%20Builder%20(v6).md>)
  - [Code execution with MCP](<./workspace/articles/mcp/1-STOP%20Using%20MCP%20Like%20This,%20Use%20MCP%202.0%20Instead%20(Save%2098%25%20More%20Tokens).md>)
- **參考資源**
  - [Building AI Agents Visually with Google ADK Visual Agent Builder](https://medium.com/google-cloud/building-ai-agents-visually-with-google-adk-visual-agent-builder-bb441e59a78c)
  - [ADK Course #8 - NEW Visual Agent Builder | Agent Development Kit (ADK)](https://www.youtube.com/watch?v=NxjbtiSvCc0)
  - [google-adk-visual-agent-builder-demo](https://github.com/thomas-chong/google-adk-visual-agent-builder-demo)
  - [No-Code Visual Agent Builder (v6)](https://github.com/theailanguage/adk_samples/tree/main/version_6_adk_nocode)
  - [STOP Using MCP Like This, Use MCP 2.0 Instead (Save 98% More Tokens)](https://youtu.be/jJMbz-xziZI?si=H77UrCQDVGYqfHH-)
  - [Code execution with MCP: Building more efficient agents](https://www.anthropic.com/engineering/code-execution-with-mcp)
  </details>

#### 🕗 Day 23

<details>
<summary>
本教學介紹如何透過伺服器發送事件（SSE）與雙向串流 API，在 ADK 中實現即時文字與音訊串流回應，以優化使用者體驗。內容涵蓋音訊處理、SSE 技術，以及將音訊輸入整合到代理工作流程中。透過實作語音助理範例，展示如何實現語音指令識別與回應。

🏷️ `streaming`, `sse`, `live-api`, `audio`, `voice`

</summary>

- **詳細說明**：
  - [文字串流文件](./workspace/notes/google-adk-training-hub/adk_training/14-streaming_sse.md)
  - [音訊串流文件](./workspace/notes/google-adk-training-hub/adk_training/15-live_api_audio.md)
  - [streaming agent](./workspace/python/agents/streaming-agent/)
  - [voice assistant](./workspace/python/agents/voice-assistant/)
- **參考資源**
  - [Tutorial 14: Streaming and Server-Sent Events (SSE) - Real-Time Responses](https://raphaelmansuy.github.io/adk_training/docs/streaming_sse)
  - [Tutorial 15: Live API & Bidirectional Streaming with Audio](https://raphaelmansuy.github.io/adk_training/docs/live_api_audio)

</details>

#### 🕗 Day 24

<details>
<summary>
本教學介紹如何使用 Google ADK 建立多代理通訊系統，實現代理之間的協同工作。內容涵蓋 A2A 通訊架構、訊息傳遞機制、同步與非同步通訊模式，以及錯誤處理與重試策略。透過實作 A2A Orchestrator 範例，展示如何協調多個代理共同完成複雜任務，提升系統的靈活性與擴展性。

🏷️ `agent-to-agent`, `distributed-systems`, `delegation`, `coordination`, `multi-agent`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/17-agent_to_agent.md)
  - [A2A Orchestrator](./workspace/python/agents/a2a-orchestrator/)
- **參考資源**
  - [Tutorial 17: Agent-to-Agent (A2A) Communication](https://raphaelmansuy.github.io/adk_training/docs/agent_to_agent)

</details>

#### 🕗 Day 25

<details>
<summary>
本教學介紹如何在 Google ADK 中實現事件追蹤與可觀測性，涵蓋設定觀察代理、事件日誌記錄、指標收集與監控儀表板建立。透過實作觀察代理範例，展示如何監控代理的運行狀態與性能，並進行故障排除與優化，提升系統的可靠性與可維護性。

🏷️ `advanced`, `observability`, `monitoring`, `events`, `metrics`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/18-events_observability.md)
  - [Observability Agent](./workspace/python/agents/observability-agent/)
- **參考資源**
  - [Tutorial 18: Events and Observability - Agent Monitoring](https://raphaelmansuy.github.io/adk_training/docs/events_observability)

</details>

#### 🕗 Day 26

<details>
<summary>
本教學介紹如何使用 Google ADK 的 Artifact Tool 管理代理程式所需的檔案與資源。內容涵蓋檔案上傳與下載、版本控制、存取權限設定，以及在代理工作流程中整合 Artifact Tool。透過實作 Artifact Agent 範例，展示如何有效地管理和使用檔案，提升代理的功能與靈活性。

🏷️ `advanced`, `artifacts`, `files`, `content-generation`, `file-management`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/19-artifacts_files.md)
  - [Artifact Agent](./workspace/python/agents/artifact-agent/)
- **參考資源**
  - [Tutorial 19: Artifacts & File Management](https://raphaelmansuy.github.io/adk_training/docs/artifacts_files)

</details>

#### 🕗 Day 27

<details>
<summary>
本教學介紹如何使用 YAML 配置文件來定義和管理 Google ADK 代理程式的設定。內容涵蓋 YAML 語法基礎、配置結構、常用設定選項，以及如何在代理工作流程中載入和應用 YAML 配置。透過實作 Customer Support 範例，展示如何利用 YAML 配置快速調整代理行為，提升開發效率與靈活性。

🏷️ `yaml`, `configuration`, `declarative`, `setup`, `rapid-prototyping`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/20-yaml_configuration.md)
  - [Customer Support](./workspace/python/agents/customer-support/)
- **參考資源**
  - [Tutorial 20: Agent Configuration with YAML](https://raphaelmansuy.github.io/adk_training/docs/yaml_configuration)

</details>

#### 🕗 Day 28

<details>
<summary>
本教學介紹如何使用 Google ADK 建立多模態圖像處理代理程式。內容涵蓋圖像輸入與輸出處理、圖像分析與生成技術，以及將圖像處理功能整合到代理工作流程中。透過實作 Vision Catalog 代理範例，展示如何利用多模態能力進行圖像分類、標註和生成，提升代理的視覺理解與互動能力。

🏷️ `multimodal`, `image-processing`, `vision`, `visual-ai`, `gemini`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/21-multimodal_image.md)
  - [Vision Catalog Agent](./workspace/python/agents/vision-catalog-agent/)
- **參考資源**
  - [Tutorial 21: Multimodal & Image Generation](https://raphaelmansuy.github.io/adk_training/docs/multimodal_image)

</details>

#### 🕗 Day 29

<details>
<summary>
本系列文章深入探討如何設計一個由多個智慧代理人（Agent）協同工作的 AI 維運平台。此架構整合了 Google ADK、A2A（Agent-to-Agent）通訊協定、MCP（Model Context Protocol）以及 Kafka 資料串流技術，旨在實現從事件監控、分析、知識查詢到自動化修復的端到端智慧維運流程。

🏷️ `aiops`,`a2a`,`streaming`,`adk`,`mcp`,`kafka`,`sre`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/articles/ops-a2a-cosmos/README.md)
- **參考資源**
  - [A2A, MCP, Kafka and Flink: The New Stack for AI Agents](https://thenewstack.io/a2a-mcp-kafka-and-flink-the-new-stack-for-ai-agents/)
  - [Announcing the Agent2Agent Protocol (A2A)](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)
  - [How to Build a Multi-Agent Orchestrator Using Apache Flink® and Apache Kafka®](https://www.confluent.io/blog/multi-agent-orchestrator-using-flink-and-kafka/)
  - [Shaping the Future of AI: A2A + Data Streaming ft. Sean Falconer | Life Is But A Stream Podcast](https://www.youtube.com/watch?v=LCGck5sUqqw)

</details>

#### 🕗 Day 30

<details>
<summary>
本教學介紹如何在 Google ADK 中進行模型選擇與優化，涵蓋不同模型的特性比較、選擇策略，以及如何根據任務需求調整模型參數以提升性能。透過實作 Model Selector 範例，展示如何根據輸入資料和預期結果動態選擇最適合的模型，實現高效且精確的代理行為。

🏷️ `model`, `gemini`, `selection`, `optimization`, `recommendation`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/22-model_selection.md)
  - [Model Selector](./workspace/python/agents/model-selector/)
- **參考資源**
  - [Tutorial 22: Model Selection & Optimization](https://raphaelmansuy.github.io/adk_training/docs/model_selection)

</details>
</details>

### 🗓️ 第 31 天 ~：進階應用與企業級實踐

<details>
<summary>第二階段：深入探討進階主題，如程式碼執行、視覺化建構、即時串流、A2A 通訊、多模態、生產部署及第三方框架整合。
</summary>

#### 🕗 Day 31

<details>
<summary>
本教學介紹如何將 Google ADK 代理程式部署到生產環境，涵蓋四種主要部署選項：Cloud Run、Agent Engine、GKE 以及本地部署。內容包括部署架構設計、可觀測性與監控實踐、安全性與權限管理，以及最佳實踐與常見挑戰的解決方案。透過實作 Production Agent 範例，展示如何在不同環境中有效部署和管理代理程式，確保其穩定運行與高效性能。

🏷️ `production`, `deployment`, `cloud-run`, `agent-engine`, `gke`, `security`, `monitoring`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/23-production_deployment.md)
  - [Production Agent](./workspace/python/agents/production-agent/)
- **參考資源**
  - [23. Production Deployment Strategies](https://raphaelmansuy.github.io/adk_training/docs/production_deployment)

</details>

#### 🕗 Day 32

<details>
<summary>
本教學介紹如何在 Google ADK 中實現進階的可觀測性與監控功能，涵蓋設定監控代理、收集與分析指標、建立監控儀表板，以及追蹤分散式追蹤系統。透過實作 Observability Plugins 代理範例，展示如何有效監控代理的運行狀態、性能指標和事件日誌，並利用這些數據進行故障排除與系統優化，提升整體可靠性與維護效率。

🏷️ `plugins`, `observability`, `monitoring`, `dashboard`, `tracing`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/24-advanced_observability.md)
  - [Observability Plugins Agent](./workspace/python/agents/observability-plugins-agent/)
- **參考資源**
  - [Tutorial 24: Advanced Observability - Enterprise Monitoring](https://raphaelmansuy.github.io/adk_training/docs/advanced_observability/)

</details>

#### 🕗 Day 34

<details>
<summary>
Gemini Enterprise (原 AgentSpace) 為 Google 企業級代理平台，整合 ADK 與無程式碼開發。具備預建代理、數據連接與安全治理功能，協助企業大規模運營 AI 代理生態系統。

🏷️ `gemini-enterprise`, `agentspace`, `deployment`, `governance`, `enterprise`, `management`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/26-google_agentspace.md)
  - [Enterprise Agent](./workspace/python/agents/enterprise-agent/)
- **參考資源**
  - [Tutorial 26: Gemini Enterprise - Enterprise Agent Management](https://raphaelmansuy.github.io/adk_training/docs/google_agentspace)

</details>

#### 🕗 Day 35

<details>
<summary>
本教學展示如何整合 LangChain 與 CrewAI 工具至 Google ADK。利用包裝器可直接使用搜尋等百種現成工具，無需 API 金鑰即可快速增強代理能力，並支援多框架協作開發。

🏷️ `third-party`, `integration`, `langchain`, `crewai`, `external-services`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/27-third_party_tools.md)
  - [Third Party Agent](./workspace/python/agents/third-party-agent/)
- **參考資源**
  - [Tutorial 27: Third-Party Framework Tools Integration](https://raphaelmansuy.github.io/adk_training/docs/third_party_tools/)

</details>

#### 🕗 Day 36

<details>
<summary>
本教學介紹如何透過 LiteLLM 在 Google ADK 中整合與使用多種大型語言模型 (LLM)。內容涵蓋設定多模型提供者、配置與管理不同模型的 API 金鑰，以及在代理工作流程中動態切換和使用不同的 LLM。透過實作 Multi-LLM 代理範例，展示如何擴展代理的能力，使其能夠利用不同模型的優勢，提升靈活性與性能。

🏷️ `advanced`, `llms`, `multi-model`, `providers`, `configuration`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/28-using_other_llms.md)
  - [Multi LLM Agent](./workspace/python/agents/multi-llm-agent/)
- **參考資源**
  - [Tutorial 28: Using Other LLMs with LiteLLM](https://raphaelmansuy.github.io/adk_training/docs/using_other_llms)

</details>

#### 🕗 Day 37

<details>
<summary>
本文件介紹 GEPA 技術，透過「測試、分析、改進」的演化循環，自動優化 AI 代理人提示詞，解決了手動調整的繁瑣與不確定性。

🏷️ `advanced`, `gepa`, `prompt-engineering`, `optimization`, `genetic-algorithms`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/36-gepa_optimization_advanced.md)
  - [GEPA Optimization Agent](./workspace/python/agents/gepa-optimization-agent/)
- **參考資源**
  - [Advanced Tutorial: GEPA-Based Prompt Optimization for Customer Support Agents](https://raphaelmansuy.github.io/adk_training/docs/gepa_optimization_advanced)

</details>

#### 🕗 Day 38

<details>
<summary>
本教學指南說明如何整合 Google ADK 代理與使用者介面。內容探討了五種整合方法，重點介紹為 React/Next.js 應用設計的官方 AG-UI 協議，並提供決策框架與最佳實踐，以建構生產級 AI 應用。

🏷️ `ui-integration`, `ag-ui`, `copilotkit`, `react`, `nextjs`, `frontend`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/29-ui_integration_intro.md)
  - [UI Integration](./workspace/python/agents/ui-integration/)
- **參考資源**
  - [Tutorial 29: Introduction to UI Integration & AG-UI Protocol](https://raphaelmansuy.github.io/adk_training/docs/ui_integration_intro)

</details>

#### 🕗 Day 39

<details>
<summary>
本教學展示如何使用 Google ADK 與 Next.js 建立前端整合代理應用。透過 AG-UI 協議，實現代理與 React/Next.js 應用的無縫互動，並提供完整範例與代碼說明，助您快速構建生產級 AI 前端應用。

🏷️ `ui-integration`, `ag-ui`, `copilotkit`, `react`, `nextjs`, `frontend`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/30-nextjs_adk_integration.md)
  - [Customer Support Agent](./workspace/python/agents/customer-support-agent/)
- **參考資源**
  - [Tutorial 30: Next.js 15 + ADK Integration (AG-UI Protocol)](https://raphaelmansuy.github.io/adk_training/docs/nextjs_adk_integration)

</details>

#### 🕗 Day 40

<details>
<summary>
本教學介紹 React Vite 與 Google ADK 的整合開發。透過 AG-UI 協定與手動 SSE 串流，實作不依賴 CopilotKit 的客製化數據分析儀表板，具備檔案上傳、Gemini 智慧分析與 Chart.js 互動圖表功能，並提供與 Next.js 的比較及部署指南。

🏷️ `ui`, `react`, `vite`, `ag-ui`, `custom-implementation`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/31-react_vite_adk_integration.md)
  - [Data Analysis Dashboard](./workspace/python/agents/data-analysis-dashboard/)
- **參考資源**
  - [Tutorial 31: React Vite + ADK Integration (AG-UI Protocol)](https://raphaelmansuy.github.io/adk_training/docs/react_vite_adk_integration)

</details>

#### 🕗 Day 41

<details>
<summary>
Streamlit 結合 ADK，用純 Python 打造數據分析 AI。整合 Gemini 2.0 實現檔案分析、圖表生成與對話，免前端開發，快速部署。

🏷️ `ui`, `streamlit`, `python`, `data-science`, `dashboard`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/32-streamlit_adk_integration.md)
  - [Data Analysis Agent](./workspace/python/agents/data-analysis-agent/)
- **參考資源**
  - [Tutorial 32: Streamlit + ADK - Build Data Analysis Apps in Pure Python](https://raphaelmansuy.github.io/adk_training/docs/streamlit_adk_integration)

</details>

#### 🕗 Day 42

<details>
<summary>
使用 Google ADK 建立 Slack 機器人，實現文件查詢與對話功能。整合 Gemini 2.0 提供智慧回應，並展示部署與擴展方法。

🏷️ `ui`, `slack`, `python`, `bot`, `messaging`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/33-slack_adk_integration.md)
  - [Support Bot](./workspace/python/agents/support-bot/)
- **參考資源**
  - [Tutorial 33: Slack Bot Integration with ADK](https://raphaelmansuy.github.io/adk_training/docs/slack_adk_integration)

</details>

#### 🕗 Day 43

<details>
<summary>
本教學整合 Pub/Sub 與 ADK 建構事件驅動文件處理系統。透過協調者路由至專家代理，並以 Pydantic 確保結構化輸出，實現高效非同步的自動化分析架構。

🏷️ `gcp cloud`, `pubsub`, `event-driven`, `python`, `agents`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/34-pubsub_adk_integration.md)
  - [Pubsub Agent](./workspace/python/agents/pubsub-agent/)
- **參考資源**
  - [Tutorial 34: Google Cloud Pub/Sub + Event-Driven Agents](https://raphaelmansuy.github.io/adk_training/docs/pubsub_adk_integration)

</details>

#### 🕗 Day 44

<details>
<summary>
建構一個具備 Grounding、多用戶對話隔離、SQLite 持久性以及綜合測試的生產級商務代理。

🏷️ `advanced`, `e2e`, `production`, `sessions`, `commerce`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/35-commerce_agent_e2e.md)
  - [Commerce Agent E2E](./workspace/python/agents/commerce-agent-e2e/)
- **參考資源**
  - [End-to-End Implementation 01: Production Commerce Agent with Session Persistence](https://raphaelmansuy.github.io/adk_training/docs/commerce_agent_e2e)

</details>

#### 🕗 Day 45

<details>
<summary>
教程 37 利用 Gemini File Search 構建 RAG。具自動引用與多代理功能，低成本高效解決企業政策查詢，大幅提升人資效率。

🏷️ `advanced`, `file-search`, `rag`, `multi-agent`, `production`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/37-file_search_policy_navigator.md)
  - [Policy Navigator](./workspace/python/agents/policy-navigator/)
- **參考資源**
  - [Tutorial 37: Native RAG with File Search - Policy Navigator](https://raphaelmansuy.github.io/adk_training/docs/file_search_policy_navigator)

</details>

#### 🕗 Day 46

<details>
<summary>
本專案教學如何從零建構多代理系統,使用 MCP 協定進行服務發現、A2A 協定實現代理間通訊,透過 Host Agent 協調任務委派,整合可串流 HTTP 與 Stdio 伺服器,建立可擴展的 AI 代理架構。

🏷️ `mcp`, `a2a`, `multi-agent`, `jsonrpc2`

</summary>

- **詳細說明**：
  - [MCP A2A Master](./workspace/python/agents/mcp-a2a-master/)
- **參考資源**
  - [a2a_samples-version_7_mcp_a2a_master-mcp_a2a_master](https://github.com/theailanguage/a2a_samples/tree/main/version_7_mcp_a2a_master/mcp_a2a_master)
  - [MCP & A2A - Model Context Protocol & Agent to Agent Protocol](https://www.udemy.com/course/modelcontextprotocol)

</details>

#### 🕗 Day 47

<details>
<summary>
本文介紹如何使用 OpenTelemetry 與 Jaeger 追蹤 Google ADK 代理的執行細節。重點說明 TracerProvider 衝突問題及解決方案：使用環境變數配置（適用 adk web）或手動設定（獨立腳本）。同時涵蓋本地開發與 Google Cloud Trace 生產環境部署。

🏷️ `adk`, `opentelemetry`, `jaeger`, `observability`, `tracing`, `debugging`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/blog/2025-11-18-opentelemetry-adk-jaeger.md)
  - [Math Agent Otel](./workspace/python/agents/math-agent-otel/)
- **參考資源**
  - [Observing ADK Agents: OpenTelemetry Tracing with Jaeger](https://raphaelmansuy.github.io/adk_training/blog/opentelemetry-adk-jaeger)
  - [Instrument ADK applications with OpenTelemetry](https://docs.cloud.google.com/stackdriver/docs/instrumentation/ai-agent-adk)
  - [OpenTelemetry + ADK + Jaeger](https://github.com/raphaelmansuy/adk_training/tree/main/til_implementation/til_opentelemetry_jaeger_20251118)

</details>

#### 🕗 Day 48

<details>
<summary>
Gemini Enterprise 取代 Agentspace，提供企業級合規、安全與資料主權。結合 SLA 保證與完整稽核，解決標準 API 風險，協助企業安心部署生產級 AI 代理。

🏷️ `gemini`, `enterprise`, `ai-agents`, `agent-engine`, `deployment`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/blog/2025-10-21-gemini-enterprise.md)
- **參考資源**
  - [Gemini Enterprise: Why Your AI Agents Need Enterprise-Grade Capabilities](https://github.com/raphaelmansuy/adk_training/blob/main/docs/blog/2025-10-21-gemini-enterprise.md)

</details>

#### 🕗 Day 49

<details>
<summary>
深入解析 Google Cloud Agent Starter Pack，這是一套全面的工具包，旨在讓您在幾分鐘內於 Google Cloud Platform (GCP) 上啟動已準備好投入生產的生成式 AI 代理。

🏷️ `agent-starter-pack`, `gcp`, `genai`, `observability`, `production`, `vertex`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/blog/2025-12-01-fast-track-agent-starter-pack.md)
  - [Pack ADK A2A Agent](./workspace/python/agents/pack-adk-a2a-agent/)
- **參考資源**
  - [Fast-track Your GenAI Agents: Deep Dive into the Google Cloud Agent Starter Pack](https://raphaelmansuy.github.io/adk_training/blog/2025/12/01/fast-track-agent-starter-pack)
  - [GoogleCloudPlatform/agent-starter-pack](https://github.com/GoogleCloudPlatform/agent-starter-pack)
  - [Agent Starter Pack Production-Ready Agents on Google Cloud, faster](https://googlecloudplatform.github.io/agent-starter-pack/)
  - [Generative AI on Google Cloud](https://github.com/GoogleCloudPlatform/generative-ai)

</details>

#### 🕗 Day 50

<details>
<summary>
本文深入探討 Google ADK 中的 Context Engineering，揭示 Google 用於生產 AI 代理的架構。涵蓋多代理系統設計、狀態管理、觀察性實踐，以及如何利用上下文提升代理性能與可靠性。

🏷️ `adk`, `context-engineering`, `architecture`, `production`, `multi-agent`, `observability`, `state-management`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/blog/2025-12-08-context-engineering-google-adk-architecture.md)
- **參考資源**
  - [Context Engineering: Inside Google's Architecture for Production AI Agents](https://raphaelmansuy.github.io/adk_training/blog/2025/12/08/context-engineering-google-adk-architecture)

</details>

#### 🕗 Day 51

<details>
<summary>
本教學介紹如何使用 eBPF 技術強化 GKE 上的 Google ADK 代理安全性與監控能力。涵蓋 eBPF 基礎、GKE 整合方法，以及實作數據平面監控與網路安全範例，提升代理在生產環境中的可視性與防護。

🏷️ `adk`, `ebpf`, `gke`, `security`, `a2a`, `monitoring`, `dataplane-v2`,`networking`

</summary>

- **詳細說明**：
  - [文件連結](./workspace/articles/ebpf/README.md)
- **參考資源**
  - [EBPF 文章參考文獻 References](./workspace/articles/ebpf/README.md#-參考文獻-references)

</details>

#### 🕗 Day 52

<details>
<summary>
探討多代理模式如何透過「分而治之」來管理系統複雜性與認知負載。分析了單一代理與多代理的權衡、委派中的上下文遺失問題，並介紹了階層式、市場式等進階架構，以及在 ADK 中實作清晰邊界與錯誤處理的最佳實踐。

🏷️ `multi-agent`, `architecture`, `complexity-management`, `adk`, `patterns`

</summary>

- **詳細說明**：

  - [文件連結](./workspace/notes/google-adk-training-hub/blog/2025-10-14-multi-agent-pattern.md)

- **參考資源**
  - [The Multi-Agent Pattern: Managing Complexity Through Divide and Conquer](https://raphaelmansuy.github.io/adk_training/blog/multi-agent-pattern-complexity-management)

</details>

#### 🕗 Day 53

<details>
<summary>
Google 全新的 Interactions API 是一個統一的閘道，可同時存取 Gemini 模型與 Deep Research Agent。它透過伺服器端狀態管理和背景執行功能，簡化了複雜、有狀態的 AI 應用程式開發，特別適合需要長時間運行的代理工作流程，是 `generateContent` API 的重要演進。

🏷️ `adk`, `gemini`, `interactions-api`, `deep-research`, `ai-agents`, `tutorial`, `genai`

</summary>

- **詳細說明**：

  - [文件連結](./workspace/notes/google-adk-training-hub/blog/2025-12-12-interactions-api-deep-research.md)

- **參考資源**
  - [Mastering Google's Interactions API: A Unified Gateway to Gemini Models and Deep Research Agent](https://raphaelmansuy.github.io/adk_training/blog/interactions-api-deep-research)

</details>

#### 🕗 Day 54

<details>
<summary>
展示 Interactions API 核心功能：與 Gemini 有狀態對話、串流回應、函式呼叫，透過 previous_interaction_id 維護狀態，適合多輪對話應用。

🏷️ `interactions api`, `gemini`, `stateful`, `streaming`

</summary>

- **詳細說明**：

  - [Interactions API Basic](./workspace/python/agents/interactions-api-basic/)

- **參考資源**
  - [Mastering Google's Interactions API: A Unified Gateway to Gemini Models and Deep Research Agent](https://raphaelmansuy.github.io/adk_training/blog/interactions-api-deep-research)
  - [Interactions API Basic Example](https://github.com/raphaelmansuy/adk_training/tree/main/tutorial_blog_implementation/interactions_api_basic)

</details>

#### 🕗 Day 55

<details>
<summary>
AI 代理部署與優化指南：部署 AI 代理比想像簡單，平台已處理安全性。Cloud Run 適合新創（約 $40/月），Agent Engine 適合企業合規（$50/月），GKE 適合 Kubernetes 環境。上下文壓縮技術透過 LLM 自動摘要舊對話，可減少 80% Token 使用，大幅降低長時間對話成本，非常適合客戶支援、研究助理等場景。

🏷️ `context-compaction`, `token-optimization`, `deployment`, `cloud-run`, `agent-engine`, `production`, `architecture`

</summary>

- **詳細說明**：

  - [文件連結：deploy ai agents](./workspace/notes/google-adk-training-hub/blog/2025-10-17-deploy-ai-agents.md)
  - [文件連結：context compaction](./workspace/notes/google-adk-training-hub/blog/2025-10-19-til-context-compaction.md)
  - [Context Compaction Agent](./workspace/python/agents/context-compaction-agent/)

- **參考資源**
  - [Deploy Your AI Agent in 5 Minutes (Seriously)](https://raphaelmansuy.github.io/adk_training/blog/deploy-ai-agents-5-minutes)
  - [TIL: Context Compaction with Google ADK 1.16](https://raphaelmansuy.github.io/adk_training/blog/til-context-compaction)

</details>

#### 🕗 Day 56

<details>
<summary>
ADK 1.16 暫停與恢復調用功能：Agent 可在關鍵點建立狀態檢查點並恢復執行，支援容錯、人機互動與長時間任務，透過 ResumabilityConfig 啟用自動狀態管理。

🏷️ `pause-resume`, `adk`, `fault-tolerance`, `state`, `context`

</summary>

- **詳細說明**：

  - [文件連結](./workspace/notes/google-adk-training-hub/blog/2025-10-20-til-pause-resume.md)

  - [Pause Resume Agent](./workspace/python/agents/pause-resume-agent/)

- **參考資源**
  - [TIL: Context Compaction with Google ADK 1.16](https://raphaelmansuy.github.io/adk_training/blog/til-pause-resume)

</details>
</details>

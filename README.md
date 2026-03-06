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

- **詳細說明**
  - [文件連結](./docs/google-adk-docs-community_summary.md)

- **參考資源**
  - [[ADK-Docs] 官方文件-Google ADK Getting Started](https://google.github.io/adk-docs/community/#getting-started)
  - [Getting Started with Agent Development Kit Tools (MCP, Google Search, LangChain, etc.)](https://www.youtube.com/watch?v=5ZmaWY7UX6k)
  - [software-bug-assistant](https://github.com/google/adk-samples/tree/main/python/agents/software-bug-assistant)
  - [Tools Make an Agent: From Zero to Assistant with ADK](https://cloud.google.com/blog/topics/developers-practitioners/tools-make-an-agent-from-zero-to-assistant-with-adk?e=48754805?utm_source%3Dtwitter?utm_source%3Dlinkedin)
  - [[ADK-Docs] 官方文件-Tools for Agents: ADK Tools list](https://google.github.io/adk-docs/tools/)

</details>

#### 🕗 Day 2

<details>
<summary>
設計 copilot 互動教學設計模式，取得目標學習專案的相關資源，並設計互動式教學模式以協助學習者更有效地掌握專案內容。

🏷️ `copilot`, `learning-design`, `interactive-tutorial`

</summary>

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**

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

- **詳細說明**

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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/22-model_selection.md)
  - [Model Selector](./workspace/python/agents/model-selector/)
- **參考資源**
  - [Tutorial 22: Model Selection & Optimization](https://raphaelmansuy.github.io/adk_training/docs/model_selection)

</details>
</details>

### 🗓️ 第 31-60 天：進階功能延伸整合

<details>
<summary>第二階段：深入探討進階主題，如程式碼執行、視覺化建構、即時串流、A2A 通訊、多模態、生產部署及第三方框架整合。
</summary>

#### 🕗 Day 31

<details>
<summary>
本教學介紹如何將 Google ADK 代理程式部署到生產環境，涵蓋四種主要部署選項：Cloud Run、Agent Engine、GKE 以及本地部署。內容包括部署架構設計、可觀測性與監控實踐、安全性與權限管理，以及最佳實踐與常見挑戰的解決方案。透過實作 Production Agent 範例，展示如何在不同環境中有效部署和管理代理程式，確保其穩定運行與高效性能。

🏷️ `production`, `deployment`, `cloud-run`, `agent-engine`, `gke`, `security`, `monitoring`

</summary>

- **詳細說明**
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

- **詳細說明**
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/24-advanced_observability.md)
  - [Observability Plugins Agent](./workspace/python/agents/observability-plugins-agent/)
- **參考資源**
  - [Tutorial 24: Advanced Observability - Enterprise Monitoring](https://raphaelmansuy.github.io/adk_training/docs/advanced_observability/)

</details>

#### 🕗 Day 33

<details>
<summary>
本教學介紹 Google ADK 的最佳實踐與生產模式，涵蓋代理設計原則、工具與工作流程選擇、性能優化、安全性強化，以及生產環境部署策略。透過實作 Best Practices 代理範例，展示如何應用這些最佳實踐來構建高效、可靠且安全的 AI 代理系統，確保其在生產環境中的穩定運行與持續改進。

🏷️ `advanced`, `best-practices`, `production`, `security`, `performance`

</summary>

- **詳細說明**
  - [文件連結](./workspace/notes/google-adk-training-hub/adk_training/25-best_practices.md)
  - [Best Practices Agent](./workspace/python/agents/best-practices-agent/)
- **參考資源**
  - [Tutorial 25: Best Practices & Production Patterns](https://raphaelmansuy.github.io/adk_training/docs/best_practices/)

</details>

#### 🕗 Day 34

<details>
<summary>
Gemini Enterprise (原 AgentSpace) 為 Google 企業級代理平台，整合 ADK 與無程式碼開發。具備預建代理、數據連接與安全治理功能，協助企業大規模運營 AI 代理生態系統。

🏷️ `gemini-enterprise`, `agentspace`, `deployment`, `governance`, `enterprise`, `management`

</summary>

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**
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

- **詳細說明**

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

- **詳細說明**

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

- **詳細說明**

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

- **詳細說明**

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

- **詳細說明**

  - [文件連結](./workspace/notes/google-adk-training-hub/blog/2025-10-20-til-pause-resume.md)
  - [Pause Resume Agent](./workspace/python/agents/pause-resume-agent/)

- **參考資源**
  - [TIL: Context Compaction with Google ADK 1.16](https://raphaelmansuy.github.io/adk_training/blog/til-pause-resume)

</details>

#### 🕗 Day 57

<details>
<summary>
本文介紹如何使用 Google ADK 1.16 評估 AI 代理的工具使用品質，分析其選擇、順序與效率，而不只看最終結果。

🏷️ `evaluation`, `adk`, `tool-use-quality`, `quality-assurance`

</summary>

- **詳細說明**

  - [文件連結](./workspace/notes/google-adk-training-hub/blog/2025-10-21-til-tool-use-quality.md)
  - [Tool Use Evaluator](./workspace/python/agents/tool-use-evaluator/)

- **參考資源**
  - [TIL: Evaluating Tool Use Quality with Google ADK 1.16](https://raphaelmansuy.github.io/adk_training/blog/til-tool-use-quality)

</details>

#### 🕗 Day 58

<details>
<summary>
Google ADK 1.17 支援自定義對話存儲（如 Redis），解決持久化與分散式部署問題。開發者只需繼承 `BaseSessionService` 並註冊服務，即可實現生產級別的對話狀態管理，無需修改核心代碼。

🏷️ `custom-session-services`, `adk`, `storage-backends`, `redis`

</summary>

- **詳細說明**

  - [文件連結](./workspace/notes/google-adk-training-hub/blog/2025-10-23-til-custom-session-services.md)
  - [Custom Session Agent](./workspace/python/agents/custom-session-agent/)

- **參考資源**
  - [TIL: Registering Custom Session Services in Google ADK 1.17](https://raphaelmansuy.github.io/adk_training/blog/til-custom-session-services)

</details>

#### 🕗 Day 59

<details>
<summary>
彙整 Google ADK、A2A Protocol 與 Model Context Protocol (MCP) 的官方網站地圖，提供完整的文檔結構視圖。這些資源涵蓋了 API 參考、教學指南、規範文件與最佳實踐，協助開發者快速定位所需資訊並建立宏觀的技術視野。

🏷️ `sitemap`, `documentation`, `resources`, `adk`, `a2a`, `mcp`

</summary>

- **詳細說明**

  - [Google ADK Site Map](./docs/sitemaps/adk-sitemap.md)
  - [A2A Protocol Site Map](./docs/sitemaps/a2a-sitemap.md)
  - [Model Context Protocol Site Map](./docs/sitemaps/mcp-sitemap.md)

- **參考資源**
  - [[ADK-Docs] 官方文件](https://google.github.io/adk-docs/)
  - [A2A Protocol](https://a2a-protocol.org/)
  - [Model Context Protocol](https://modelcontextprotocol.io/)

</details>

#### 🕗 Day 60

<details>
<summary>
本指南介紹 Google Deep Research Agent 與 Interactions API 的整合應用。透過 ADK 框架，開發者可實現長時程背景研究、伺服器端狀態管理及串流思考摘要。這不僅降低了對話負載，更能無縫委派複雜任務，顯著提升 AI 代理的自主研究與分析能力。

🏷️ `deep-search`, `interactions-api`, `gemini`, `state`, `vertex-ai`, `streaming`, `genai`

</summary>

- **詳細說明**

  - [Deep Research Agent](./workspace/python/agents/deep-research-agent/)
  - [ADK Interactions Integration](./workspace/python/agents/adk-interactions-integration/)

- **參考資源**
  - [Mastering Google's Interactions API: A Unified Gateway to Gemini Models and Deep Research Agent
    ](https://raphaelmansuy.github.io/adk_training/blog/interactions-api-deep-research)
  - [[ADK-Docs] 官方文件](https://google.github.io/adk-docs/)
  - [[Code Wiki] adk-python](https://codewiki.google/github.com/google/adk-python)

</details>
</details>

### 🗓️ 第 61-90 天：Agent Marketplace 整合與官方文件 (ADK Docs) 學習整理

<details>
<summary>第三階段：檢視前60天所學內容，進行標準化設計與實作。
</summary>

#### 🕗 Day 61

<details>
<summary>
參考官方 Visual Builder 規格定義，定義 YAML 格式的規範設計與範本提供 `Agent Marketplace` 頁面功能整合與未來支援 `Visual Builder` 標準化。

```
已完成進度 (4/49)
- A2a Orchestrator
- ADK Interactions Agent
- Artifact Agent
- Best Practices Agent
```

🏷️ `yaml`, `visual-builder`, `template`, `marketplace`, `agents`

</summary>

- **詳細說明**
  - [Agent 規格標準化範本](./docs/agents/agents-template.yaml)
  - [agents.yaml 連結](./docs/agents/agents.yaml)

- **參考資源**
  - [[ADK-Docs] 官方文件-Visual Builder](https://google.github.io/adk-docs/visual-builder/)

</details>

#### 🕗 Day 62

<details>
<summary>
努力更新 agents.yaml (➕ 6) 🏃🏻。

```
已完成進度 (10/49)
- Blog Creation Pipeline
- Chuck Norris Agent
- Financial Calculator
- Commerce Agent
- Content Moderator
- Content Publishing System
```

🏷️ `yaml`, `visual-builder`, `template`, `marketplace`, `agents`

</summary>

- **詳細說明**
  - [Agent 規格標準化範本](./docs/agents/agents-template.yaml)
  - [agents.yaml 連結](./docs/agents/agents.yaml)
- **參考資源**
  - [[ADK-Docs] 官方文件-Visual Builder](https://google.github.io/adk-docs/visual-builder/)

</details>

#### 🕗 Day 63

<details>
<summary>
努力更新 agents.yaml (➕ 10) 🏃🏻。

```
已完成進度 (20/49)
- Context Compaction Agent
- Custom Session Agent
- Customer Support
- Customer Support Agent (AG-UI)
- Data Analysis Agent
- Data Analysis Dashboard
- Deep Research Agent
- Enterprise Lead Qualifier
- Essay Refinement System
- Finance Assistant
```

🏷️ `yaml`, `visual-builder`, `template`, `marketplace`, `agents`

</summary>

- **詳細說明**
  - [Agent 規格標準化範本](./docs/agents/agents-template.yaml)
  - [agents.yaml 連結](./docs/agents/agents.yaml)
- **參考資源**
  - [[ADK-Docs] 官方文件-Visual Builder](https://google.github.io/adk-docs/visual-builder/)

</details>

#### 🕗 Day 64

<details>
<summary>
努力更新 agents.yaml (➕ 10) 🏃🏻。

```
已完成進度 (30/49)
- GEPA Optimization Agent
- Grounding Agent
- Hello Agent
- Interactions API Basic Agent
- Math Agent (OTel)
- Host Agent (MCP/A2A)
- MCP File Assistant
- Model Selector Agent
- Multi-LLM Agent
- Observability Agent
```

🏷️ `yaml`, `visual-builder`, `template`, `marketplace`, `agents`

</summary>

- **詳細說明**
  - [Agent 規格標準化範本](./docs/agents/agents-template.yaml)
  - [agents.yaml 連結](./docs/agents/agents.yaml)
- **參考資源**
  - [[ADK-Docs] 官方文件-Visual Builder](https://google.github.io/adk-docs/visual-builder/)

</details>

#### 🕗 Day 65

<details>
<summary>
努力更新 agents.yaml (➕ 9) 🏃🏻。

```
已完成進度 (39/49)
- Observability Plugins Agent
- Pack ADK A2A Agent
- Pause Resume Agent
- Personal Tutor
- Policy Navigator
- Production Agent
- Pub/Sub Document Processor
- Software Bug Assistant
- Strategic Solver
  - Strategic Problem Solver (BuiltInPlanner)
  - Strategic Problem Solver (PlanReActPlanner)
  - Strategic Problem Solver (Custom StrategicPlanner)
```

🏷️ `yaml`, `visual-builder`, `template`, `marketplace`, `agents`

</summary>

- **詳細說明**
  - [Agent 規格標準化範本](./docs/agents/agents-template.yaml)
  - [agents.yaml 連結](./docs/agents/agents.yaml)
- **參考資源**
  - [[ADK-Docs] 官方文件-Visual Builder](https://google.github.io/adk-docs/visual-builder/)

</details>

#### 🕗 Day 66

<details>
<summary>
努力更新 agents.yaml (完成 ✅) 🏃🏻。

```
已完成進度 (49/49)
- Streaming Agent
- Support Agent
- Support Bot
- Third-Party Integration Agent
- Tool Use Evaluator
- Travel Planner
- UI Integration Quickstart Agent
- Vision Catalog Coordinator
- Voice Assistant
- YouTube Shorts Agent
```

🏷️ `yaml`, `visual-builder`, `template`, `marketplace`, `agents`

</summary>

- **詳細說明**
  - [Agent 規格標準化範本](./docs/agents/agents-template.yaml)
  - [agents.yaml 連結](./docs/agents/agents.yaml)
- **參考資源**
  - [[ADK-Docs] 官方文件-Visual Builder](https://google.github.io/adk-docs/visual-builder/)

</details>

#### 🕗 Day 67

<details>
<summary>
這是一個使用 Google Cloud ADK 入門包建立的 RAG 代理專案，用於文件檢索與問答。它整合了 Vertex AI Search，並包含完整的資料擷取管道、Terraform 部署腳本及可觀測性設定，讓開發者能快速建構、測試與部署生成式 AI 應用。

🏷️ `rag`, `agent-starter-pack`, `gcp`, `vertex-ai`, `terraform`, `logging`, `cloud-sql`, `knowledge-management`, `monitoring`, `cicd`

</summary>

- **詳細說明**

  - [RAG KM Agent](./workspace/python/agents/rag-km-agents/)

- **參考資源**
  - [Agent Starter Pack 文件](https://googlecloudplatform.github.io/agent-starter-pack/)
  - [ADK GitHub 儲存庫](https://github.com/GoogleCloudPlatform/agent-starter-pack)

</details>

#### 🕗 Day 68

<details>
<summary>
此專案是一個使用 ADK 和 Gemini Live API 建立的即時多模態代理，能實現低延遲的語音和視訊互動。它基於 agent-starter-pack，提供完整的 FastAPI 後端、CI/CD 管線和部署腳本，並透過 make 指令簡化本機測試與 Cloud Run 部署流程。

🏷️ `multimodal`, `gemini-live-api`, `gcp`, `real-time`, `fastapi`, `uvicorn`, `agent-starter-Pack`, `logging`, `monitoring`, `cicd`

</summary>

- **詳細說明**

  - [Live Interact Agent](./workspace/python/agents/live-interact-agent/)

- **參考資源**
  - [Agent Starter Pack 文件](https://googlecloudplatform.github.io/agent-starter-pack/)
  - [ADK GitHub 儲存庫](https://github.com/GoogleCloudPlatform/agent-starter-pack)

</details>

#### 🕗 Day 69

<details>
<summary>
Part 1/2：基於 Google ADK 的多代理系統，利用 Web Browser Agent 與 BigQuery 整合，透過自動化瀏覽器爬取分析零售網站搜尋結果，為商品資料（標題、描述、屬性）產生優化建議，解決搜尋查詢低回收率問題，改善商品可發現性。

🏷️ `web-crawling`, `bigquery`, `search-enhancement`, `poetry`, `agent route`, `selenium, dynamic-prompt, artifact`

</summary>

- **詳細說明**

  - [Brand Search Optimization](./workspace/python/agents/brand-search-optimization/)

- **參考資源**
  - [Brand Search Optimization - Web Browser Agent for Search Optimization](https://github.com/google/adk-samples/tree/main/python/agents/brand-search-optimization)
  - [Build a Browser Use Agent with ADK and Selenium](https://www.youtube.com/watch?v=hPzjkQFV5yI)

</details>

#### 🕗 Day 70

<details>
<summary>
Part 2/2：基於 Google ADK 的多代理系統，利用 Web Browser Agent 與 BigQuery 整合，透過自動化瀏覽器爬取分析零售網站搜尋結果，為商品資料（標題、描述、屬性）產生優化建議，解決搜尋查詢低回收率問題，改善商品可發現性。

🏷️ `web-crawling`, `bigquery`, `search-enhancement`, `poetry`, `agent route`, `selenium, dynamic-prompt, artifact`

</summary>

- **詳細說明**

  - [Brand Search Optimization](./workspace/python/agents/brand-search-optimization/)

- **參考資源**
  - [Brand Search Optimization - Web Browser Agent for Search Optimization](https://github.com/google/adk-samples/tree/main/python/agents/brand-search-optimization)
  - [Build a Browser Use Agent with ADK and Selenium](https://www.youtube.com/watch?v=hPzjkQFV5yI)

</details>

#### 🕗 Day 71

<details>
<summary>
本專案實作了一個為園藝零售商「Cymbal Home & Garden」設計的 AI 客戶服務 Agent。此 Agent 運用 Gemini 模型，透過多模態互動（文字與影像）提供個人化產品推薦、訂單管理及服務預約。專案基於 Google ADK 範例，並整合 Agent Starter Pack，作為一個學習與實作的參考。

🏷️ `agent-starter-pack`, `customer`, `opentelemetry`, `poetry`, `global-instruction`, `fastapi`, `cloud-logging`, `uvicorn`

</summary>

- **詳細說明**

  - [Pack Customer Service](./workspace/python/agents/pack-customer-service/)

- **參考資源**
  - [[ADK-Samples] customer-service](https://github.com/google/adk-samples/tree/main/python/agents/customer-service)
  - [Agent Starter Pack](https://goo.gle/agent-starter-pack)

</details>

#### 🕗 Day 72

<details>
<summary>
以官方 adk-docs 為主，彙整 Google ADK 多語言快速入門：安裝、建立 Agent、設定 Gemini API 金鑰、註冊工具並以 CLI/Web 測試執行。

🏷️ `adk-docs`, `ai-agent`, `dev-tools`, `get-started`, `adk-python`, `adk-js`, `adk-java`, `adk-go`

</summary>

- **詳細說明**

  - [[ADK-Docs] 學習文件-Get Started](./workspace/adk-docs/get-started/about.md)

- **參考資源**
  - [[ADK-Docs] 官方文件](https://google.github.io/adk-docs/)
  - [Google AI Studio](https://aistudio.google.com/app/api-keys)
  - [Gemini API Models](https://ai.google.dev/gemini-api/docs/models)

</details>

#### 🕗 Day 73

<details>
<summary>
ADK 的 Sessions/State/Memory 框架，讓 AI Agent 能管理短期對話狀態與長期跨會話知識，並提供快速模式方便開發。

🏷️ `sessions`, `context`, `state`, `memory`, `rewind`, `agent-engine`, `vertex-ai`

</summary>

- **詳細說明**

  - [[ADK-Docs] 學習文件-Session & Memory](./workspace/adk-docs/sessions&memory/index.md)

- **參考資源**
  - [[ADK-Docs] 官方文件-Sessions](https://google.github.io/adk-docs/sessions/)
  - [[ADK-Docs] 官方文件-VertexAiSessionService](https://google.github.io/adk-docs/sessions/session/#sessionservice-implementations)
  - [[ADK-Docs] 官方文件-VertexAiMemoryBankService](https://google.github.io/adk-docs/sessions/memory/#vertex-ai-memory-bank)
  - [Google AI Studio](https://aistudio.google.com/app/api-keys)
  - [Gemini API Models](https://ai.google.dev/gemini-api/docs/models)
  - [GCP Express Mode](https://console.cloud.google.com/expressmode)
  - [Vertex AI Memory Bank](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview)
  - [免費試用 Session 與 Memory](https://google.github.io/adk-docs/sessions/express-mode/)

</details>

#### 🕗 Day 74

<details>
<summary>
[整合 1/3] 這是一個由生成式 AI 驅動的代理，用於在 Google Cloud 上自動化數據治理。它能將自然語言政策轉換為在 Dataplex 和 BigQuery 上運行的程式碼，並具備記憶、學習與雙模式操作能力，以確保數據合規性。

🏷️ `cloudsql`, `memory`, `session`, `firestore`, `code-policy`, `mcp`, `fastapi`, `uvicorn`, `embedding`, `bigquery`, `cicd`

</summary>

- **詳細說明**

  - [Pack Policy As Code](./workspace/python/agents/pack-policy-as-code/)

- **參考資源**

  - [adk-samples 存儲庫 (policy as code)](https://github.com/google/adk-samples/tree/3d9fe35ce097760c5dceb7136a2c72802c3c6021/python/agents/policy-as-code)
  - [agent-starter-pack 官方文件](https://github.com/GoogleCloudPlatform/agent-starter-pack)

</details>

#### 🕗 Day 75

<details>
<summary>
[整合 2/3] 這是一個由生成式 AI 驅動的代理，用於在 Google Cloud 上自動化數據治理。它能將自然語言政策轉換為在 Dataplex 和 BigQuery 上運行的程式碼，並具備記憶、學習與雙模式操作能力，以確保數據合規性。

🏷️ `cloudsql`, `memory`, `session`, `firestore`, `code-policy`, `mcp`, `fastapi`, `uvicorn`, `embedding`, `bigquery`, `cicd`

</summary>

- **詳細說明**

  - [Pack Policy As Code](./workspace/python/agents/pack-policy-as-code/)

- **參考資源**

  - [adk-samples 存儲庫 (policy as code)](https://github.com/google/adk-samples/tree/3d9fe35ce097760c5dceb7136a2c72802c3c6021/python/agents/policy-as-code)
  - [agent-starter-pack 官方文件](https://github.com/GoogleCloudPlatform/agent-starter-pack)

</details>

#### 🕗 Day 76

<details>
<summary>
[整合 3/3] 這是一個由生成式 AI 驅動的代理，用於在 Google Cloud 上自動化數據治理。它能將自然語言政策轉換為在 Dataplex 和 BigQuery 上運行的程式碼，並具備記憶、學習與雙模式操作能力，以確保數據合規性與完成 [adk docs] 官方 deployment 相關參考文件整理。

🏷️ `cloudsql`, `memory`, `session`, `firestore`, `code-policy`, `mcp`, `fastapi`, `uvicorn`, `embedding`, `bigquery`, `cicd`,`gke`, `cloudrun`, `vertexai-engine`

</summary>

- **詳細說明**

  - [[ADK-Docs] 學習文件-Deployment](./workspace/adk-docs/deployment/deploy.md)
  - [Pack Policy As Code](./workspace/python/agents/pack-policy-as-code/)

- **參考資源**

  - [adk-samples 存儲庫 (policy as code)](https://github.com/google/adk-samples/tree/3d9fe35ce097760c5dceb7136a2c72802c3c6021/python/agents/policy-as-code)
  - [agent-starter-pack 官方文件](https://github.com/GoogleCloudPlatform/agent-starter-pack)
  - [[ADK-Docs] 官方文件-Deployment](https://google.github.io/adk-docs/deploy/)

</details>


#### 🕗 Day 77

<details>
<summary>
ADK 代理執行核心 (Runtime) 透過事件迴圈驅動代理程式。您可以使用 API 伺服器進行本地測試，並透過 RunConfig 客製化執行行為，如串流與呼叫限制。它還支援從中斷點恢復工作流程，確保執行的穩健性。

🏷️ `runtime`, `event-loop`, `api-server`, `fastapi`, `run-config`, `resume`, `workflow`, `async`, `streaming`

</summary>

- **詳細說明**

  - [[ADK-Docs] 學習文件-Runtime](./workspace/adk-docs/agent-runtime/index.md)

- **參考資源**

  - [[ADK-Docs] 官方文件-Runtime](https://google.github.io/adk-docs/runtime/)

</details>

#### 🕗 Day 78

<details>
<summary>
介紹 ADK 上下文管理，涵蓋多種上下文類型，並透過內容快取減少成本及事件壓縮優化長對話，顯著提升代理效能與回應速度。

🏷️ `context`, `compaction`, `caching`, `token`, `events-compacting-config`

</summary>

- **詳細說明**

  - [[ADK-Docs] 學習文件-Context](./workspace/adk-docs/context/index.md)
  - [[整理 adk-python 官方範例]: caching 使用的 Agent 範例-[cache-analysis]](./workspace/python/agents/cache-analysis/)
  - [[整理 adk-python 官方範例]: caching 使用的 Agent 範例-[static-instruction]](./workspace/python/agents/static-instruction/)
  - [[整理 adk-python 官方範例]: compaction 使用的 Agent 範例-[hello-world-app]](./workspace/python/agents/hello-world-app/)

- **參考資源**

  - [[ADK-Docs] 官方文件-Context](https://google.github.io/adk-docs/context/)
  - [adk-python 官方範例位置](https://github.com/google/adk-python)
  - [[adk-python] cache_analysis 範例](https://github.com/google/adk-python/tree/main/contributing/samples/cache_analysis)
  - [[adk-python] static_instruction 範例](https://github.com/google/adk-python/tree/main/contributing/samples/static_instruction)
  - [[adk-python] hello_world_app](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world_app)

</details>

#### 🕗 Day 79

<details>
<summary>
[整合 1/2] Google ADK 自定義工具文件涵蓋函數工具、MCP工具、OpenAPI工具與身份驗證機制。詳細說明工具定義、並行執行、人機確認流程，包含Python、TypeScript、Go、Java多語言實作範例，支援代理程式透過結構化函數呼叫擴展能力與外部系統互動。

🏷️ `function-tools`, `mcp`, `confirmation`, `custom-tools`, `human-in-loop`, `async-parallel`, `performance`, `openapi`, `authentication`

</summary>

- **詳細說明**

  - [[ADK-Docs] 學習文件-Custom Tools](./workspace/adk-docs/custom-tools/index.md)
  - [[整理 adk-python 官方範例]: confirmation 使用的 Agent 範例-[human-tool-confirmation]](./workspace/python/agents/human-tool-confirmation/)

- **參考資源**

  - [[ADK-Docs] 官方文件-Custom Tools](https://google.github.io/adk-docs/tools-custom/)
  - [adk-python 官方範例位置](https://github.com/google/adk-python)
  - [[adk-python] human_tool_confirmation 範例](https://github.com/google/adk-python/tree/main/contributing/samples/human_tool_confirmation)

</details>

#### 🕗 Day 80

<details>
<summary>
[整合 2/2] Google ADK 自定義工具文件涵蓋函數工具、MCP工具、OpenAPI工具與身份驗證機制。詳細說明工具定義、並行執行、人機確認流程，包含Python、TypeScript、Go、Java多語言實作範例，支援代理程式透過結構化函數呼叫擴展能力與外部系統互動 / 整合 Medium 關於 AI Agent Memory 應用文章。

🏷️ `function-tools`, `mcp`, `confirmation`, `custom-tools`, `human-in-loop`, `async-parallel`, `performance`, `openapi`, `authentication`, `memory`

</summary>

- **詳細說明**

  - [[ADK-Docs] 學習文件-Custom Tools](./workspace/adk-docs/custom-tools/index.md)
  - [[整理 adk-python 官方範例]: confirmation 使用的 Agent 範例-[human-tool-confirmation]](./workspace/python/agents/human-tool-confirmation/)
  - [[Articles] AI 代理 (AI Agent) 記憶優化技術指南](./workspace/articles/memory/implementing-9-techniques-to-optimize-ai-agent-memory.md)

- **參考資源**

  - [[ADK-Docs] 官方文件-Custom Tools](https://google.github.io/adk-docs/tools-custom/)
  - [adk-python 官方範例位置](https://github.com/google/adk-python)
  - [[adk-python] human_tool_confirmation 範例](https://github.com/google/adk-python/tree/main/contributing/samples/human_tool_confirmation)
  - [Implementing 9 Techniques to Optimize AI Agent Memory](https://medium.com/@fareedkhandev/67d813e3d796?sk=14ccc929e8d9c64b0ca7c4c80fe79b45)

</details>

#### 🕗 Day 81

<details>
<summary>
ADK 提供三大核心代理類別：LLM 代理用於智慧推理、工作流代理 (順序/平行/迴圈) 管理執行流程、自訂代理實現特殊邏輯。支援多代理協作架構，可透過 Agent Config 以 YAML 配置構建無程式碼工作流。

🏷️ `agents`, `workflow`, `sequential`, `loop`, `parallel`, `custom-agent`, `config`, `pattern`, `multi-agents`

</summary>

- **詳細說明**

  - [[ADK-Docs] 學習文件-Agents](./workspace/adk-docs/agents/index.md)

- **參考資源**

  - [[ADK-Docs] 官方文件-Agents](https://google.github.io/adk-docs/agents/)

</details>

#### 🕗 Day 82

<details>
<summary>
[Adk Docs 官方 A2A 協定文件整理]
此目錄文件解釋了如何在 ADK (Agent Development Kit) 中使用 Agent2Agent (A2A) 協定來建構複雜的多代理系統。內容包含 A2A 的基本介紹、使用時機，並提供 Python 和 Go 語言的快速入門指南，說明如何「公開」自己的代理服務以及如何「取用」遠端的代理服務。

🏷️  `a2a`, `multi-agent`, `example-tool`, `agent-card`, `exposing`, `consuming`, `to_a2a`, `api_server`

</summary>

- **詳細說明**

  - [[ADK-Docs] 學習文件-A2A](./workspace/adk-docs/a2a-protocol/index.md)
  - [A2A Basic](./workspace/python/agents/a2a-basic/)

- **參考資源**

  - [[ADK-Docs] 官方文件-A2A](https://google.github.io/adk-docs/a2a/)
  - [A2A Protocol 官方網站](https://a2a-protocol.org/)
  - [[Code Wiki] a2a-protocol](https://codewiki.google/github.com/google/adk-python)
  - [[adk-python] a2a_basic](https://github.com/google/adk-python/tree/main/contributing/samples/a2a_basic)

</details>

#### 🕗 Day 83

<details>
<summary>
介紹 Google ADK 深層搜尋代理開發套件，展示如何使用 Gemini 建構具備人機協作的全端研究代理系統，包含多代理協作、函式調用與迭代搜尋循環，支援本地與雲端部署。

🏷️ `deep-search`, `planner`, `vite-react`, `ui`, `human-in-loop`, `sequential`, `loop`, `custom-agent`, `callback`, `fastapi`, `uvicorn`

</summary>

- **詳細說明**

  - [Pack Deep Search](./workspace/python/agents/pack-deep-search/)

- **參考資源**
  - [[ADK-Samples] deep-search](https://github.com/google/adk-samples/tree/main/python/agents/deep-search)
  - [Agent Starter Pack](https://goo.gle/agent-starter-pack)

</details>

#### 🕗 Day 84

<details>
<summary>
介紹 Artifacts 如何管理與工作階段或使用者相關的具名、版本化二進位資料 (如檔案、圖片)，並說明其在 ADK 中的表示與操作方式。

🏷️ `artifacts`, `binary`, `mine-type`, `gcs`, `artifact-service`, `version`, `namespace`
</summary>

- **詳細說明**
  - [[ADK-Docs] 學習文件-Artifacts](./workspace/adk-docs/artifacts/index.md)

- **參考資源**
  - [[ADK-Docs] 官方文件-Artifacts](https://google.github.io/adk-docs/artifacts/)

</details>

#### 🕗 Day 85

<details>
<summary>
說明 App 與 Plugin 在 ADK 代理工作流程中的角色與功能。

- 介紹 **App** 類別作為代理工作流程的頂層容器，用於管理代理集合的生命週期、配置和狀態，並簡化如情境快取、恢復和外掛程式等功能的設定。
- 介紹 **ADK 外掛程式 (Plugin)** 的概念，它如何使用回呼掛鉤在代理工作流的生命週期中執行，以及其常見應用，如日誌記錄、原則強制執行和回應快取。

🏷️ `apps`, `callback-hooks`, `plugins`, `logging-tracing`, `monitoring-metrics`, `caching`, `policy`, `reflect-retry`
</summary>

- **詳細說明**
  - [[ADK-Docs] 學習文件-Apps](./workspace/adk-docs/apps/index.md)
  - [[ADK-Docs] 學習文件-Plugins](./workspace/adk-docs/plugins/index.md)

- **參考資源**
  - [[ADK-Docs] 官方文件-Apps](https://google.github.io/adk-docs/apps/)
  - [[ADK-Docs] 官方文件-Plugins](https://google.github.io/adk-docs/plugins/)

</details>

#### 🕗 Day 86

<details>
<summary>
說明代理評估的必要性、評估目標與成功標準，以及如何用測試檔/評估集 (EvalSet) 建立自動化評估流程。

🏷️ `evaluate`, `user-simulation`, `event-config`, `criteria`, `quality`, `judgement`, `trajectory`
</summary>

- **詳細說明**
  - [[ADK-Docs] 學習文件-Evaluation](./workspace/adk-docs/evaluation/index.md)

- **參考資源**
  - [[ADK-Docs] 官方文件-Evaluation](https://google.github.io/adk-docs/evaluate/)

</details>

#### 🕗 Day 87

<details>
<summary>
介紹 Callbacks 如何掛鉤到代理執行過程，提供觀察、自訂與控制代理行為的機制，包括代理前後、LLM 前後與工具執行前後的回呼。

🏷️ `callbacks`, `best-practices`, `types-of-callbacks`, `design-pattern`, `agent-callbacks`, `model-callbacks`, `tool-callbacks`
</summary>

- **詳細說明**
  - [[ADK-Docs] 學習文件-Callbacks](./workspace/adk-docs/callbacks/index.md)

- **參考資源**
  - [[ADK-Docs] 官方文件-Callbacks](https://google.github.io/adk-docs/callbacks/)

</details>

#### 🕗 Day 88

<details>
<summary>
說明 Events 與 MCP 在 ADK 代理工作流程中的角色與功能。

- 介紹 **Events** 的概念、用途，以及如何使用事件來追蹤代理的執行歷程與狀態變化。
- **MCP** 是模型上下文協定 (MCP) 是開放標準，標準化 LLM 與外部系統的通訊。ADK 支援使用與提供 MCP 工具，包含用於資料庫的 MCP 工具箱（支援 BigQuery、PostgreSQL、MongoDB 等多種資料來源）、FastMCP 伺服器整合，以及 Google Cloud 生成式媒體服務的 MCP 工具。

🏷️ `events`, `mcp`, `artifact`, `session-service`, `transfer`, `streamable`, `llm-response`, `gcp`, `toolbox`, `database`, `genmedia`
</summary>

- **詳細說明**
  - [[ADK-Docs] 學習文件-Events](./workspace/adk-docs/events/index.md)
  - [[ADK-Docs] 學習文件-MCP](./workspace/adk-docs/mcp/index.md)
  - [Genmedia Agent](./workspace/python/agents/genmedia-agent/)

- **參考資源**
  - [[ADK-Docs] 官方文件-Events](https://google.github.io/adk-docs/events/)
  - [[ADK-Docs] 官方文件-MCP](https://google.github.io/adk-docs/mcp/)
  - [[vertex-ai-creative-studio] genmedia_agent](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia/sample-agents/adk)
  - [MCP Servers for Genmedia: Go Implementations](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/blob/main/experiments/mcp-genmedia/mcp-genmedia-go/README.md)

</details>

#### 🕗 Day 89

<details>
<summary>
ADK 提供靈活機制整合多樣 LLM，支援 Gemini、Claude 等模型。可透過註冊表直接介接 Google 模型，或利用 LiteLLM、Apigee 等連接器擴展至第三方或本地模型（Ollama、vLLM）。結合企業級驗證與流量治理，簡化代理程式開發並確保安全與效能。

🏷️ `llm`, `gemini`, `claude`, `vertex-ai`, `litellm`, `apigee`, `ollama`, `vllm`, `model-integration`

</summary>

- **詳細說明**
  - [[ADK-Docs] 學習文件-Models](./workspace/adk-docs/models-for-agents/index.md)
  - [Pack Auto Insurance Agent](./workspace/python/agents/pack-auto-insurance-agent/)

- **參考資源**
  - [[ADK-Docs] 官方文件-Models](https://google.github.io/adk-docs/agents/models/)
  - [[ADK-Samples] auto-insurance-agent](https://github.com/google/adk-samples/tree/main/python/agents/auto-insurance-agent)

</details>

#### 🕗 Day 90

<details>
<summary>
更新 [ADK Docs] Get Started & Agent Runtime 相關文件內容，並補充 LLM 整合說明。

🏷️ `get-started`, `runtime`, `event-loop`, `api-server`, `fastapi`, `run-config`, `resume`, `workflow`, `async`, `streaming`

</summary>

- **詳細說明**

  - [[ADK-Docs] 學習文件-Get Started](./workspace/adk-docs/get-started/index.md)
  - [[ADK-Docs] 學習文件-Runtime](./workspace/adk-docs/agent-runtime/index.md)

- **參考資源**

  - [[ADK-Docs] 官方文件-Get Started](https://google.github.io/adk-docs/get-started/)
  - [[ADK-Docs] 官方文件-Runtime](https://google.github.io/adk-docs/runtime/)

</details>

</details>

### 🗓️ 第 91 天開始 ~：官方文件 (ADK Docs) 學習整理與完整實踐

<details>
<summary>第四階段： 官方文件 (ADK Docs) 持續更新，完整實踐 Agent 實作與範例整理
</summary>

#### 🕗 Day 91

<details>
<summary>
[整合 1/4] [Gemini API 系列] 整合 ADK 所提供的多種預建工具，涵蓋 Gemini API、Google Cloud 與多種第三方工具（如 GitHub, Notion, Stripe 等）。

🏷️  `agent-tools`,`google-search`,`code-execution`,`computer-use`,`agent-tools`,`playwright`

</summary>

- **詳細說明**
  - [[ADK-Docs] 學習文件-Tools for Agents [Gemini API 系列]](./workspace/adk-docs/tools-for-agents/gemini-api/index.md)

- **參考資源**
  - [[ADK-Docs] 官方文件-Tools for Agents [Gemini API 系列]](https://google.github.io/adk-docs/tools/)

</details>

#### 🕗 Day 92

<details>
<summary>
[整合 2/4] [Google Cloud 系列] 整合 ADK 所提供的多種預建工具，涵蓋 Gemini API、Google Cloud 與多種第三方工具（如 GitHub, Notion, Stripe 等）。

🏷️  `agent-tools`,`bigquery`,`connector`,`api-registry`,`apigee-api``application-integration`

</summary>

- **詳細說明**
  - [[ADK-Docs] 學習文件-Tools for Agents [Google Cloud 系列]](./workspace/adk-docs/tools-for-agents/google-cloud/index.md)
  - [API Registry Agent](./workspace/python/agents/api-registry-agent/)

- **參考資源**
  - [[ADK-Docs] 官方文件-Tools for Agents [Google Cloud 系列]](https://google.github.io/adk-docs/tools/google-cloud/)
  - [[adk-python] api_registry_agent 範例](https://github.com/google/adk-python/tree/main/contributing/samples/api_registry_agent/)

</details>

#### 🕗 Day 93

<details>
<summary>
[整合 3/4] [Google Cloud 系列] 整合 ADK 所提供的多種預建工具，涵蓋 Gemini API、Google Cloud 與多種第三方工具（如 GitHub, Notion, Stripe 等）。

🏷️ `bigquery`, `bigtable`, `data-agent`, `express-mode`, `gke-code-executor`, `mcp-toolbox`, `pubsub`, `spanner`, `vertex-ai-rag-engine`, `vertext-ai-search`

</summary>

- **詳細說明**
  - [[ADK-Docs] 學習文件-Tools for Agents [Google Cloud 系列]](./workspace/adk-docs/tools-for-agents/google-cloud/index.md)
  - [Agent Engine Code Execution](./workspace/python/agents/agent-engine-code-execution/)

- **參考資源**
  - [[ADK-Docs] 官方文件-Tools for Agents [Google Cloud 系列]](https://google.github.io/adk-docs/tools/google-cloud/)
  - [[adk-python] agent_engine_code_execution 範例](https://github.com/google/adk-python/tree/main/contributing/samples/agent_engine_code_execution)

</details>

#### 🕗 Day 94

<details>
<summary>
[整合 4/4] [Third Party 系列] 整合 ADK 所提供的多種預建工具，涵蓋 Gemini API、Google Cloud 與多種第三方工具（如 GitHub, Notion, Stripe 等）。

🏷️ `notion`, `github`, `mcp`, `streamable`, `stdio`, `postman`, `paypal`, `hugging-face`, `ag-ui`, `strip`, `n8n`, `strip`, `qdrant`

</summary>

- **詳細說明**
  - [[ADK-Docs] 學習文件-Tools for Agents [Third Party 系列]](./workspace/adk-docs/tools-for-agents/third-party/index.md)

- **參考資源**
  - [[ADK-Docs] 官方文件-Tools for Agents [Third Party 系列]](https://google.github.io/adk-docs/tools/third-party/)

</details>

#### 🕗 Day 95

<details>
<summary>
[整合 1/2] [Observability] ADK 整合觀察性與可觀測性工具與實作指南，涵蓋日誌、追蹤、模型監控與分析，包含 BigQuery、Cloud Trace、MLflow、Arize、Weave 等整合案例，適合作為開發與運維建立可觀測性流程的參考資源。

🏷️ `observability`, `logging`, `tracing`, `model-monitoring`, `bigquery-analytics`, `cloud-trace`, `mlflow`, `arize`, `weave`, `monocle`, `phoenix`, `agentops`, `bigquery-agent-analytics`, `freeplay`

</summary>

- **詳細說明**
  - [[ADK-Docs] 學習文件-Logging [Observability 系列]](./workspace/adk-docs/observability/logging.md)
  - [[ADK-Docs] 學習文件-Cloud Trace [Observability 系列]](./workspace/adk-docs/observability/cloud-trace.md)
  - [[ADK-Docs] 學習文件-BigQuery Agent Analytics [Observability 系列]](./workspace/adk-docs/observability/bigquery-agent-analytics.md)
  - [Short Movie Agents](./workspace/python/agents/short-movie-agents/)

- **參考資源**
  - [[ADK-Docs] 官方文件-Logging [Observability 系列]](https://google.github.io/adk-docs/observability/logging/)
  - [[ADK-Docs] 官方文件-Cloud Trace [Observability 系列]](https://google.github.io/adk-docs/observability/cloud-trace/)
  - [[ADK-Docs] 官方文件-BigQuery Agent Analytics [Observability 系列]](https://google.github.io/adk-docs/observability/bigquery-agent-analytics/)
  - [[ADK-Samples] Short Movie Agents](https://github.com/google/adk-samples/tree/main/python/agents/short-movie-agents)

</details>

#### 🕗 Day 96

<details>
<summary>
[整合 2/2] [Observability] ADK 整合觀察性與可觀測性工具與實作指南，涵蓋日誌、追蹤、模型監控與分析，包含 BigQuery、Cloud Trace、MLflow、Arize、Weave 等整合案例，適合作為開發與運維建立可觀測性流程的參考資源。

🏷️ `observability`, `logging`, `tracing`, `model-monitoring`, `bigquery-analytics`, `cloud-trace`, `mlflow`, `arize`, `weave`, `monocle`, `phoenix`, `agentops`, `bigquery-agent-analytics`, `freeplay`

</summary>

- **詳細說明**
  - [[ADK-Docs] 學習文件-觀測性總覽 [Observability 系列]](./workspace/adk-docs/observability/index.md)
  - [[ADK-Docs] 學習文件-AgentOps [Observability 系列]](./workspace/adk-docs/observability/agentops.md)
  - [[ADK-Docs] 學習文件-Arize AX [Observability 系列]](./workspace/adk-docs/observability/arize-ax.md)
  - [[ADK-Docs] 學習文件-Freeplay [Observability 系列]](./workspace/adk-docs/observability/freeplay.md)
  - [[ADK-Docs] 學習文件-MLflow [Observability 系列]](./workspace/adk-docs/observability/mlflow.md)
  - [[ADK-Docs] 學習文件-Monocle [Observability 系列]](./workspace/adk-docs/observability/monocle.md)
  - [[ADK-Docs] 學習文件-Phoenix [Observability 系列]](./workspace/adk-docs/observability/phoenix.md)
  - [[ADK-Docs] 學習文件-Weave (by WandB) [Observability 系列]](./workspace/adk-docs/observability/weave.md)

- **參考資源**
  - [[ADK-Docs] 官方文件-AgentOps [Observability 系列]](https://google.github.io/adk-docs/observability/agentops/)
  - [[ADK-Docs] 官方文件-Arize AX [Observability 系列]](https://google.github.io/adk-docs/observability/arize-ax/)
  - [[ADK-Docs] 官方文件-Freeplay [Observability 系列]](https://google.github.io/adk-docs/observability/freeplay/)
  - [[ADK-Docs] 官方文件-MLflow [Observability 系列]](https://google.github.io/adk-docs/observability/mlflow/)
  - [[ADK-Docs] 官方文件-Monocle [Observability 系列]](https://google.github.io/adk-docs/observability/monocle/)
  - [[ADK-Docs] 官方文件-Phoenix [Observability 系列]](https://google.github.io/adk-docs/observability/phoenix/)
  - [[ADK-Docs] 官方文件-Weave (by WandB) [Observability 系列]](https://google.github.io/adk-docs/observability/weave/)

</details>

#### 🕗 Day 97

<details>
<summary>
[Safety and Security] 探討 AI 系統的安全與保護措施，涵蓋風險評估、資料隱私、權限控管、異常偵測與回應機制。強調設計時需考量潛在威脅，並持續監控與更新安全策略，以確保系統穩定運作並保護用戶資料，降低外部攻擊與內部濫用風險。

🏷️ `safety`, `security`, `callback`, `policy`, `auth`, `guardrails`, `plugins`, `sandbox`, `evaluation`

</summary>

- **詳細說明**
  - [[ADK-Docs] 學習文件-安全性 [Safety and Security]](./workspace/adk-docs/safety-and-security/index.md)

- **參考資源**
  - [[ADK-Docs] 官方文件 [Safety and Security]](https://google.github.io/adk-docs/safety/)

</details>

#### 🕗 Day 98

<details>
<summary>
[BIDI Streaming Live] Google ADK 支援 Gemini Live API，實現低延遲的雙向串流（Bidi-streaming）互動。開發者可透過 RunConfig 設定語音配置、自動 VAD 與逐字稿。核心組件如 LiveRequestQueue 負責傳送多模態輸入，run_live() 則處理包含中斷偵測與工具調用的即時事件，支援多代理程式協作與串流工具開發。

🏷️ `bidi-streaming`, `live-api`, `gemini-live-api`, `vertex-ai-live-api`, `liverequestqueue`, `runconfig`, `multimodal`, `native-audio`, `interruption-detection`, `vad`, `websockets`

</summary>

- **詳細說明**
  - [[ADK-Docs] 學習文件-即時雙向串流 [Bidi-streaming (live)]](./workspace/adk-docs/bidi-streaming-live/index.md)

- **參考資源**
  - [[ADK-Docs] 官方文件 [Bidi-streaming (live)]](https://google.github.io/adk-docs/streaming/)

</details>

#### 🕗 Day 99

<details>
<summary>
[整合 1/2] 以 [BIDI Streaming Live] 官方文件，透過 NotebookLM 工具整合知識庫深入解析 ADK 的雙向串流核心。我們將傳統的「請求-等待」模式革新為「即時對話」體驗，實現了可中斷、多模態的互動。藉由官方範例 (bidi-demo) 與 agent-starter-pack 的整合，我們不僅實作了視覺感知、語音情感等進階功能，更涵蓋了從開發、測試到 Cloud Run 部署的完整生產級流程，助您打造次世代 AI 應用。

🏷️ `bidi-streaming`, `live-api`, `gemini-live-api`, `vertex-ai-live-api`, `liverequestqueue`, `runconfig`, `multimodal`, `native-audio`, `interruption-detection`, `vad`, `websockets`, `affective`, `proactively`

</summary>

- **詳細說明**
  - [雙向串流 (Bidi-streaming) 深度實作指南](./workspace/articles/bidi-streaming/README.md)
  - [Pack Bidi Streaming](./workspace/python/agents/pack-bidi-streaming/)

- **參考資源**
  - [[ADK-Docs] 官方文件 [Bidi-streaming (live)]](https://google.github.io/adk-docs/streaming/)
  - [[ADK-Samples] bidi-demo](https://github.com/google/adk-samples/tree/main/python/agents/bidi-demo)
  - [Agent Starter Pack](https://googlecloudplatform.github.io/agent-starter-pack/)

</details>

#### 🕗 Day 100

<details>
<summary>
[整合 2/2] 以 [BIDI Streaming Live] 官方文件，透過 NotebookLM 工具整合知識庫深入解析 ADK 的雙向串流核心。我們將傳統的「請求-等待」模式革新為「即時對話」體驗，實現了可中斷、多模態的互動。藉由官方範例 (bidi-demo) 與 agent-starter-pack 的整合，我們不僅實作了視覺感知、語音情感等進階功能，更涵蓋了從開發、測試到 Cloud Run 部署的完整生產級流程，助您打造次世代 AI 應用。

🏷️ `bidi-streaming`, `live-api`, `gemini-live-api`, `vertex-ai-live-api`, `liverequestqueue`, `runconfig`, `multimodal`, `native-audio`, `interruption-detection`, `vad`, `websockets`, `affective`, `proactively`

</summary>

- **詳細說明**
  - [雙向串流 (Bidi-streaming) 深度實作指南](./workspace/articles/bidi-streaming/README.md)
  - [Pack Bidi Streaming](./workspace/python/agents/pack-bidi-streaming/)

- **參考資源**
  - [[ADK-Docs] 官方文件 [Bidi-streaming (live)]](https://google.github.io/adk-docs/streaming/)
  - [[ADK-Samples] bidi-demo](https://github.com/google/adk-samples/tree/main/python/agents/bidi-demo)
  - [Agent Starter Pack](https://googlecloudplatform.github.io/agent-starter-pack/)

</details>

#### 🕗 Day 101

<details>
<summary>
[Grounding] Grounding 是將代理的回應建立並取得在外部資料服務的完整流程，用於降低幻覺、提高即時性，並讓答案可被來源驗證。本文件整理官方文件資料夾中與 Grounding 相關的主題與延伸資源。

🏷️ `grounding`, `google-search-grounding`, `vertex-ai-search-grounding`, `user-query`, `tool-calling`, `rag`, `context-injection`

</summary>

- **詳細說明**
  - [[ADK-Docs] 學習文件-Grounding](./workspace/adk-docs/grounding/index.md)

- **參考資源**
  - [[ADK-Docs] 官方文件 [Grounding]](https://google.github.io/adk-docs/grounding/)

</details>

#### 🕗 Day 102

<details>
<summary>
承接 Day 101 的 Grounding 主題，參考 ADK Samples 官方範例 (RAG) 搭配 Agent-starter-pack，實作具備 Grounding `Vertex AI Search Grounding`功能，展示如何將外部資料注入代理上下文，提升回應的準確性與可靠性，並涵蓋從開發、測試到 Cloud Run 部署的完整生產級流程。

🏷️ `grounding`, `vertex-ai-search-grounding`, `rag`, `agent-starter-pack`, `fastapi`, `uvicorn`, `ask_vertex_retrieval`

</summary>

- **詳細說明**
  - [Pack RAG](./workspace/python/agents/pack-rag/)

- **參考資源**
  - [[ADK-Samples] RAG]](https://github.com/google/adk-samples/tree/main/python/agents/RAG)

</details>

#### 🕗 Day 103

<details>
<summary>
[Build your Agent] 透過實踐指南系列，開始使用 ADK 構建各種類型的智慧代理。這些教學以循序漸進的方式設計，從基礎概念到進階的代理開發技術。

🏷️ `agent-team`, `coding-with-ai`, `safety-guardrails-callbacks`, `tutorials`, `session-state-memory`, `multi-llm`, `mcp`, `ide`

</summary>

- **詳細說明**
  - [[ADK-Docs] 學習文件-Build your Agent](./workspace/adk-docs/build-your-agent/tutorials/index.md)

- **參考資源**
  - [[ADK-Docs] 官方文件 [Build your Agent]](https://google.github.io/adk-docs/tutorials/)

</details>

#### 🕗 Day 104

<details>
<summary>
[整合 1/7] 本學習透過 105 (根據內容整合調整) 個情境主題分成七大類型，整合學習路徑聚焦於將生成式 AI 轉化為生產力實體。學習者需先掌握代理人的 Sense-Reason-Plan-Act 基本解剖結構，並結合 RAG 解決數據新鮮度問題。技術實踐層面，強調透過 asyncio 非同步編程 與 FastAPI 解決 AI 推論中的 I/O 瓶頸，提升系統併發效能。最終目標是運用多代理人協作模式（MAS）拆解複雜任務，並落實 AgentOps 的監控與評估機制。透過循序漸進的成熟度模型，你將具備從簡單 Prompt 工程轉向建構可解釋、安全且具備自主學習能力的企業級 AI 架構之專業職能。

🏷️ `generative-ai`, `ai-agent`, `asyncio`, `fastapi`, `rag`, `ml-ops`, `design-pattern`, `effective-style`, `multi-agent`, `mcp`, `a2a`

</summary>

- **詳細說明**
  - [[文章 Part 1] 有效學習生成式 AI 技術的關鍵主題 (Key Topics for Effective GenAI Learning)](./workspace/articles/effective-genai-learning/README.md#️-主題-1python-非同步與並發基礎-python-concurrency--async)

- **參考資源**
  - [Asynchronous Programming in Python (Packt)](https://www.packtpub.com/en-tw/product/asynchronous-programming-in-python-9781836646600)
  - [Agentic Architectural Patterns for Building Multi-Agent Systems (Packt)](https://www.packtpub.com/en-tw/product/agentic-architectural-patterns-for-building-multi-agent-systems-9781806029563)
  - [Generative AI Design Patterns (O'Reilly)](https://oreil.ly/genAI-design-patterns)
  - [Building Generative AI Services with FastAPI (O'Reilly)](https://oreil.ly/building-gen-ai-fastAPI)
  - [GenAI on Google Cloud (O'Reilly)](https://oreil.ly/GenAI_on_Google)
  - [Python Concurrency with asyncio (Manning)](https://www.manning.com/books/python-concurrency-with-asyncio)

</details>

#### 🕗 Day 105

<details>
<summary>
[整合 2/7] 本學習透過 105 (根據內容整合調整) 個情境主題分成七大類型，整合學習路徑聚焦於將生成式 AI 轉化為生產力實體。學習者需先掌握代理人的 Sense-Reason-Plan-Act 基本解剖結構，並結合 RAG 解決數據新鮮度問題。技術實踐層面，強調透過 asyncio 非同步編程 與 FastAPI 解決 AI 推論中的 I/O 瓶頸，提升系統併發效能。最終目標是運用多代理人協作模式（MAS）拆解複雜任務，並落實 AgentOps 的監控與評估機制。透過循序漸進的成熟度模型，你將具備從簡單 Prompt 工程轉向建構可解釋、安全且具備自主學習能力的企業級 AI 架構之專業職能。

🏷️ `generative-ai`, `ai-agent`, `asyncio`, `fastapi`, `rag`, `ml-ops`, `design-pattern`, `effective-style`, `multi-agent`, `mcp`, `a2a`

</summary>

- **詳細說明**
  - [[文章 Part 2] 有效學習生成式 AI 技術的關鍵主題 (Key Topics for Effective GenAI Learning)](./workspace/articles/effective-genai-learning/README.md#️-主題-2ai-agent-核心概念與解剖-agent-anatomy--foundations)

- **參考資源**
  - [Asynchronous Programming in Python (Packt)](https://www.packtpub.com/en-tw/product/asynchronous-programming-in-python-9781836646600)
  - [Agentic Architectural Patterns for Building Multi-Agent Systems (Packt)](https://www.packtpub.com/en-tw/product/agentic-architectural-patterns-for-building-multi-agent-systems-9781806029563)
  - [Generative AI Design Patterns (O'Reilly)](https://oreil.ly/genAI-design-patterns)
  - [Building Generative AI Services with FastAPI (O'Reilly)](https://oreil.ly/building-gen-ai-fastAPI)
  - [GenAI on Google Cloud (O'Reilly)](https://oreil.ly/GenAI_on_Google)
  - [Python Concurrency with asyncio (Manning)](https://www.manning.com/books/python-concurrency-with-asyncio)

</details>

#### 🕗 Day 106

<details>
<summary>
[整合 3/7] 本學習透過 105 (根據內容整合調整) 個情境主題分成七大類型，整合學習路徑聚焦於將生成式 AI 轉化為生產力實體。學習者需先掌握代理人的 Sense-Reason-Plan-Act 基本解剖結構，並結合 RAG 解決數據新鮮度問題。技術實踐層面，強調透過 asyncio 非同步編程 與 FastAPI 解決 AI 推論中的 I/O 瓶頸，提升系統併發效能。最終目標是運用多代理人協作模式（MAS）拆解複雜任務，並落實 AgentOps 的監控與評估機制。透過循序漸進的成熟度模型，你將具備從簡單 Prompt 工程轉向建構可解釋、安全且具備自主學習能力的企業級 AI 架構之專業職能。

🏷️ `generative-ai`, `ai-agent`, `asyncio`, `fastapi`, `rag`, `ml-ops`, `design-pattern`, `effective-style`, `multi-agent`, `mcp`, `a2a`

</summary>

- **詳細說明**
  - [[文章 Part 3] 多代理人協作架構 (Multi-Agent Architectures)](./workspace/articles/effective-genai-learning/README.md#️-主題-3多代理人協作架構-multi-agent-architectures)

- **參考資源**
  - [Asynchronous Programming in Python (Packt)](https://www.packtpub.com/en-tw/product/asynchronous-programming-in-python-9781836646600)
  - [Agentic Architectural Patterns for Building Multi-Agent Systems (Packt)](https://www.packtpub.com/en-tw/product/agentic-architectural-patterns-for-building-multi-agent-systems-9781806029563)
  - [Generative AI Design Patterns (O'Reilly)](https://oreil.ly/genAI-design-patterns)
  - [Building Generative AI Services with FastAPI (O'Reilly)](https://oreil.ly/building-gen-ai-fastAPI)
  - [GenAI on Google Cloud (O'Reilly)](https://oreil.ly/GenAI_on_Google)
  - [Python Concurrency with asyncio (Manning)](https://www.manning.com/books/python-concurrency-with-asyncio)

</details>

#### 🕗 Day 107

<details>
<summary>
[整合 4/7] 本學習透過 104 (根據內容整合調整) 個情境主題分成七大類型，整合學習路徑聚焦於將生成式 AI 轉化為生產力實體。學習者需先掌握代理人的 Sense-Reason-Plan-Act 基本解剖結構，並結合 RAG 解決數據新鮮度問題。技術實踐層面，強調透過 asyncio 非同步編程 與 FastAPI 解決 AI 推論中的 I/O 瓶頸，提升系統併發效能。最終目標是運用多代理人協作模式（MAS）拆解複雜任務，並落實 AgentOps 的監控與評估機制。透過循序漸進的成熟度模型，你將具備從簡單 Prompt 工程轉向建構可解釋、安全且具備自主學習能力的企業級 AI 架構之專業職能。

🏷️ `generative-ai`, `ai-agent`, `asyncio`, `fastapi`, `rag`, `ml-ops`, `design-pattern`, `effective-style`, `multi-agent`, `mcp`, `a2a`

</summary>

- **詳細說明**
  - [[文章 Part 4] RAG 與外部知識整合模式 (RAG & Knowledge Patterns)](./workspace/articles/effective-genai-learning/README.md#️-主題-4rag-與外部知識整合模式-rag--knowledge-patterns)

- **參考資源**
  - [Asynchronous Programming in Python (Packt)](https://www.packtpub.com/en-tw/product/asynchronous-programming-in-python-9781836646600)
  - [Agentic Architectural Patterns for Building Multi-Agent Systems (Packt)](https://www.packtpub.com/en-tw/product/agentic-architectural-patterns-for-building-multi-agent-systems-9781806029563)
  - [Generative AI Design Patterns (O'Reilly)](https://oreil.ly/genAI-design-patterns)
  - [Building Generative AI Services with FastAPI (O'Reilly)](https://oreil.ly/building-gen-ai-fastAPI)
  - [GenAI on Google Cloud (O'Reilly)](https://oreil.ly/GenAI_on_Google)
  - [Python Concurrency with asyncio (Manning)](https://www.manning.com/books/python-concurrency-with-asyncio)

</details>

#### 🕗 Day 108

<details>
<summary>
[整合 5/7] 本學習透過 104 (根據內容整合調整) 個情境主題分成七大類型，整合學習路徑聚焦於將生成式 AI 轉化為生產力實體。學習者需先掌握代理人的 Sense-Reason-Plan-Act 基本解剖結構，並結合 RAG 解決數據新鮮度問題。技術實踐層面，強調透過 asyncio 非同步編程 與 FastAPI 解決 AI 推論中的 I/O 瓶頸，提升系統併發效能。最終目標是運用多代理人協作模式（MAS）拆解複雜任務，並落實 AgentOps 的監控與評估機制。透過循序漸進的成熟度模型，你將具備從簡單 Prompt 工程轉向建構可解釋、安全且具備自主學習能力的企業級 AI 架構之專業職能。

🏷️ `generative-ai`, `ai-agent`, `asyncio`, `fastapi`, `rag`, `ml-ops`, `design-pattern`, `effective-style`, `multi-agent`, `mcp`, `a2a`

</summary>

- **詳細說明**
  - [[文章 Part 5] 推理優化與生成控制 (Reasoning & Design Patterns)](./workspace/articles/effective-genai-learning/README.md#️-主題-5推理優化與生成控制-reasoning--design-patterns)

- **參考資源**
  - [Asynchronous Programming in Python (Packt)](https://www.packtpub.com/en-tw/product/asynchronous-programming-in-python-9781836646600)
  - [Agentic Architectural Patterns for Building Multi-Agent Systems (Packt)](https://www.packtpub.com/en-tw/product/agentic-architectural-patterns-for-building-multi-agent-systems-9781806029563)
  - [Generative AI Design Patterns (O'Reilly)](https://oreil.ly/genAI-design-patterns)
  - [Building Generative AI Services with FastAPI (O'Reilly)](https://oreil.ly/building-gen-ai-fastAPI)
  - [GenAI on Google Cloud (O'Reilly)](https://oreil.ly/GenAI_on_Google)
  - [Python Concurrency with asyncio (Manning)](https://www.manning.com/books/python-concurrency-with-asyncio)

</details>

#### 🕗 Day 109

<details>
<summary>
[整合 6/7] 本學習透過 104 (根據內容整合調整) 個情境主題分成七大類型，整合學習路徑聚焦於將生成式 AI 轉化為生產力實體。學習者需先掌握代理人的 Sense-Reason-Plan-Act 基本解剖結構，並結合 RAG 解決數據新鮮度問題。技術實踐層面，強調透過 asyncio 非同步編程 與 FastAPI 解決 AI 推論中的 I/O 瓶頸，提升系統併發效能。最終目標是運用多代理人協作模式（MAS）拆解複雜任務，並落實 AgentOps 的監控與評估機制。透過循序漸進的成熟度模型，你將具備從簡單 Prompt 工程轉向建構可解釋、安全且具備自主學習能力的企業級 AI 架構之專業職能。

🏷️ `generative-ai`, `ai-agent`, `asyncio`, `fastapi`, `rag`, `ml-ops`, `design-pattern`, `effective-style`, `multi-agent`, `mcp`, `a2a`

</summary>

- **詳細說明**
  - [[文章 Part 6] 服務架構、部署與 MLOps (Service Architecture & Ops)](./workspace/articles/effective-genai-learning/README.md#️-主題-6服務架構部署與-mlops-service-architecture--ops)

- **參考資源**
  - [Asynchronous Programming in Python (Packt)](https://www.packtpub.com/en-tw/product/asynchronous-programming-in-python-9781836646600)
  - [Agentic Architectural Patterns for Building Multi-Agent Systems (Packt)](https://www.packtpub.com/en-tw/product/agentic-architectural-patterns-for-building-multi-agent-systems-9781806029563)
  - [Generative AI Design Patterns (O'Reilly)](https://oreil.ly/genAI-design-patterns)
  - [Building Generative AI Services with FastAPI (O'Reilly)](https://oreil.ly/building-gen-ai-fastAPI)
  - [GenAI on Google Cloud (O'Reilly)](https://oreil.ly/GenAI_on_Google)
  - [Python Concurrency with asyncio (Manning)](https://www.manning.com/books/python-concurrency-with-asyncio)

</details>

#### 🕗 Day 110

<details>
<summary>
[整合 7/7] 本學習透過 104 (根據內容整合調整) 個情境主題分成七大類型，整合學習路徑聚焦於將生成式 AI 轉化為生產力實體。學習者需先掌握代理人的 Sense-Reason-Plan-Act 基本解剖結構，並結合 RAG 解決數據新鮮度問題。技術實踐層面，強調透過 asyncio 非同步編程 與 FastAPI 解決 AI 推論中的 I/O 瓶頸，提升系統併發效能。最終目標是運用多代理人協作模式（MAS）拆解複雜任務，並落實 AgentOps 的監控與評估機制。透過循序漸進的成熟度模型，你將具備從簡單 Prompt 工程轉向建構可解釋、安全且具備自主學習能力的企業級 AI 架構之專業職能。

🏷️ `generative-ai`, `ai-agent`, `asyncio`, `fastapi`, `rag`, `ml-ops`, `design-pattern`, `effective-style`, `multi-agent`, `mcp`, `a2a`

</summary>

- **詳細說明**
  - [[文章 Part 7] 主題 7：系統可靠性、安全與合規 (Reliability & Safety)](./workspace/articles/effective-genai-learning/README.md#️-主題-7系統可靠性安全與合規-reliability--safety)

- **參考資源**
  - [Asynchronous Programming in Python (Packt)](https://www.packtpub.com/en-tw/product/asynchronous-programming-in-python-9781836646600)
  - [Agentic Architectural Patterns for Building Multi-Agent Systems (Packt)](https://www.packtpub.com/en-tw/product/agentic-architectural-patterns-for-building-multi-agent-systems-9781806029563)
  - [Generative AI Design Patterns (O'Reilly)](https://oreil.ly/genAI-design-patterns)
  - [Building Generative AI Services with FastAPI (O'Reilly)](https://oreil.ly/building-gen-ai-fastAPI)
  - [GenAI on Google Cloud (O'Reilly)](https://oreil.ly/GenAI_on_Google)
  - [Python Concurrency with asyncio (Manning)](https://www.manning.com/books/python-concurrency-with-asyncio)

</details>

#### 🕗 Day 111

<details>
<summary>
本文件詳細介紹如何在 Google ADK 框架下建立與運用「技能代理人（Skills Agent）」。內容涵蓋技能（Skill）的核心概念、優勢、設計原則與命名慣例，並說明如何以 Python 3.11+ 實作內嵌技能與目錄型技能，並透過 SkillToolset 組合多項技能。文件提供從安裝、環境設定、技能開發、測試到常見問題的完整流程，強調技能的模組化、可重複使用、易維護與團隊協作特性。最後，附上進階應用、最佳實務與資源連結，協助開發者快速上手並擴展技能系統。

🏷️ `skills`, `skill-toolset`, `inline-skills`, `markdown`, `libraries`, `experimental`

</summary>

- **詳細說明**
  - [[ADK-Docs] 學習文件-Skills for ADK agents](./workspace/adk-docs/skills-for-agents/index.md)
  - [Skills Agent](./workspace/python/agents/skills-agent/)

- **參考資源**
  - [[ADK-Docs] 官方文件 [Skills for ADK agents]](https://google.github.io/adk-docs/skills/)
  - [[ADK-Samples] skills_agent](https://github.com/google/adk-python/tree/main/contributing/samples/skills_agent)

</details>

#### 🕗 Day 112

<details>
<summary>
[整合 1/5] 本文件彙整 Google ADK 支援的各類代理工具與整合，依「所有項目」、「程式碼」、「連接器」、「資料」、「Google」、「MCP」、「可觀測性」、「搜尋」等分類，詳細列出每項工具名稱、功能說明及連結。涵蓋 Google 服務、第三方平台、資料庫、API、可觀測性、工作流自動化等，協助代理程式擴充能力、串接外部資源與提升開發效率。另提供自訂工具與整合貢獻指南，方便開發者查找、比較與導入所需工具。

🏷️ `tools`, `code`, `connectors`, `data`, `google`, `mcp`, `observability`, `search`

</summary>

- **詳細說明**
  - [[ADK-Docs] 學習文件-Tools and Integrations](./workspace/adk-docs/tools-and-integrations/index.md)

- **參考資源**
  - [[ADK-Docs] 官方文件 [Tools and Integrations]](https://google.github.io/adk-docs/integrations/)

</details>

#### 🕗 Day 113

<details>
<summary>
[整合 2/5] 本文件彙整 Google ADK 支援的各類代理工具與整合，依「所有項目」、「程式碼」、「連接器」、「資料」、「Google」、「MCP」、「可觀測性」、「搜尋」等分類，詳細列出每項工具名稱、功能說明及連結。涵蓋 Google 服務、第三方平台、資料庫、API、可觀測性、工作流自動化等，協助代理程式擴充能力、串接外部資源與提升開發效率。另提供自訂工具與整合貢獻指南，方便開發者查找、比較與導入所需工具。

🏷️ `tools`, `code`, `connectors`, `data`, `google`, `mcp`, `observability`, `search`

</summary>

- **詳細說明**
  - [[ADK-Docs] 學習文件-Tools and Integrations](./workspace/adk-docs/tools-and-integrations/index.md)

- **參考資源**
  - [[ADK-Docs] 官方文件 [Tools and Integrations]](https://google.github.io/adk-docs/integrations/)

</details>

#### 🕗 Day 114

<details>
<summary>
[整合 3/5] 本文件彙整 Google ADK 支援的各類代理工具與整合，依「所有項目」、「程式碼」、「連接器」、「資料」、「Google」、「MCP」、「可觀測性」、「搜尋」等分類，詳細列出每項工具名稱、功能說明及連結。涵蓋 Google 服務、第三方平台、資料庫、API、可觀測性、工作流自動化等，協助代理程式擴充能力、串接外部資源與提升開發效率。另提供自訂工具與整合貢獻指南，方便開發者查找、比較與導入所需工具。

🏷️ `tools`, `code`, `connectors`, `data`, `google`, `mcp`, `observability`, `search`

</summary>

- **詳細說明**
  - [[ADK-Docs] 學習文件-Tools and Integrations](./workspace/adk-docs/tools-and-integrations/index.md)

- **參考資源**
  - [[ADK-Docs] 官方文件 [Tools and Integrations]](https://google.github.io/adk-docs/integrations/)

</details>

</details>

</details>
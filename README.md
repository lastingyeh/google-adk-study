# Google ADK 學習路線圖

## 概述

此儲存庫包含學習 Google ADK（代理開發工具包）的完整路線圖。此路線圖旨在引導學習者掌握有效使用 Google ADK 構建智能代理所需的重要主題和技能。

### 🕗 Day 1

<details>

<summary>
了解 Google ADK 核心定義，在社群資源中匯集了由 Agent Development Kit (ADK) 社群所建立和維護的各類資源。內容涵蓋了入門教學、深度課程、代理程式開發的教學與示範、Java 版本的 ADK 資源，以及多國語言的文件翻譯。此外，頁面也提供了如何貢獻自己資源的指南，鼓勵社群成員參與並豐富 ADK 的生態系。
</summary>

#### **詳細說明**：

- [文件連結](./docs/google-adk-docs-community_summary.md)
- [Google ADK Getting Started ](https://google.github.io/adk-docs/community/#getting-started)
- [Getting Started with Agent Development Kit Tools (MCP, Google Search, LangChain, etc.)](https://www.youtube.com/watch?v=5ZmaWY7UX6k)
- [software-bug-assistant](https://github.com/google/adk-samples/tree/main/python/agents/software-bug-assistant)
- [Tools Make an Agent: From Zero to Assistant with ADK](https://cloud.google.com/blog/topics/developers-practitioners/tools-make-an-agent-from-zero-to-assistant-with-adk?e=48754805?utm_source%3Dtwitter?utm_source%3Dlinkedin)
- [Tools for Agents: ADK Tools list](https://google.github.io/adk-docs/tools/)

</details>

### 🕗 Day 2

<details>
<summary>
設計 copilot 互動教學設計模式(未完成)，取得目標學習專案的相關資源，並設計互動式教學模式以協助學習者更有效地掌握專案內容。
</summary>

#### **詳細說明**：

- [文件連結](.github/chatmodes/repo-guiding-learning.chatmode.md)

#### **參考資源**
- [專案相依連結](./workspace/python/agents/software-bug-assistant/README.md)

</details>

### 🕗 Day 3

<details>
<summary>
實做範例 software-bug-assistant 專案，了解如何使用 Google ADK 建立一個能夠協助識別和修復軟體錯誤的智能代理。此專案展示了 ADK 的強大功能，並提供了實際應用的範例，幫助學習者深入理解代理程式的設計與實作過程。
</summary>

#### **詳細說明**：

- [環境初始化流程](./workspace/python/agents/software-bug-assistant/docs/INSTALLATION_GUIDE.md)
- [文件連結](./workspace/python/agents/software-bug-assistant/README.md)

#### **參考資源**
- [software-bug-assistant](./workspace/python/agents/software-bug-assistant/)

</details>

### 🕗 Day 4

<details>
<summary>
實做範例 youtube-shorts-agent 專案，了解如何使用 Google ADK 建立一個能夠協助生成和管理 YouTube Shorts 內容的智能代理。此專案展示了 ADK 的強大功能，並提供了實際應用的範例，幫助學習者深入理解代理程式的設計與實作過程。
</summary>

#### **詳細說明**：

- [文件連結](./workspace/python/agents/youtube-shorts-assistant/README.md)
- [學習訓練指引筆記](./workspace/notes/google-adk-training-hub/README.md)

#### **參考資源**
- [Getting started with Agent Development Kit](https://www.youtube.com/watch?v=44C8u0CDtSo)
- [youtube-shorts-assistant 專案 Repo](./workspace/python/agents/youtube-shorts-assistant/)
- [Google ADK Training Hub](https://raphaelmansuy.github.io/adk_training/)

</details>

### 🕗 Day 5

<details>
<summary>
實現範例 finance-assistant 專案，了解如何使用 Google ADK 建立一個能夠協助管理和分析財務數據的智能代理。包含基本 ADK Tools 的應用，並透過 asyncio.gather(*tasks) 平行處理任務與完整 Agent 測試案例實現。
</summary>

#### **詳細說明**：

- [文件連結](./workspace/python/agents/finance-assistant/README.md)

#### **參考資源**
- [Tutorial 02: Function Tools Implementation](https://github.com/raphaelmansuy/adk_training/tree/main/tutorial_implementation/tutorial02)
- [finance-assistant](./workspace/python/agents/finance-assistant/)
- [Tutorial 02: Function Tools - Give Your Agent Superpowers](https://raphaelmansuy.github.io/adk_training/docs/function_tools)

</details>

### 🕗 Day 6

<details>
<summary>
實現範例 chuck-norris-agent 專案，學習如何從 OpenAPI 規範中自動產生工具，使您的代理程式能夠與 REST API 互動，而無需手動編寫工具函式。
</summary>

#### **詳細說明**：

- [文件連結](./workspace/python/agents/chuck-norris-agent/README.md)

#### **參考資源**
- [Tutorial 03: OpenAPI Tools - Connect Your Agent to Web APIs](https://raphaelmansuy.github.io/adk_training/docs/openapi_tools/)
- [教學 03：OpenAPI 工具 - REST API 整合](./workspace/notes/google-adk-training-hub/adk_training/03-openapi_tools.md)
- [chuck-norris-agent](./workspace/python/agents/chuck-norris-agent/)
- [Tutorial 03: Chuck Norris OpenAPI Tools Agent](https://github.com/raphaelmansuy/adk_training/tree/main/tutorial_implementation/tutorial03/)

</details>

### 🕗 Day 7

<details>
<summary>
本教學介紹 Gemini 2.0+ 的內建工具,包含網路搜尋、地圖定位和企業搜尋功能,讓 AI 代理程式存取即時資訊。核心內容涵蓋:google_search 網路基礎工具、google_maps_grounding 位置服務(需 VertexAI)、enterprise_web_search 企業搜尋、GoogleSearchAgentTool 混合工具解決方案。同時介紹記憶體管理、工作流程控制、上下文載入等進階工具。透過實作研究助理範例,展示如何整合多種工具建立生產級代理程式系統,包含最佳實踐與疑難排解指南。
</summary>

#### **詳細說明**：

- [文件連結](./workspace/python/agents/chuck-norris-agent/README.md)

#### **參考資源**
- [教學 11：內建工具與基礎 (Built-in Tools & Grounding)](./workspace/notes/google-adk-training-hub/adk_training/11-built_in_tools_grounding.md)
- [Grounding Agent](./workspace/python/agents/grounding-agent/)

</details>

### 🕗 Day 8

<details>
<summary>
本教學介紹如何使用模型內容協議 (MCP) 將外部工具和服務整合到 AI 代理程式中。透過 MCPToolset 連接 MCP 伺服器，讓代理程式能夠存取檔案系統、資料庫、API 等外部資源，並支援 OAuth 驗證與人機迴圈審批等進階功能。
</summary>

#### **詳細說明**：

- [文件連結](./workspace/python/agents/mcp-agent/README.md)

#### **參考資源**
- [教學 16: 模型內容協議 (MCP) 整合 - 標準化工具協議](./workspace/notes/google-adk-training-hub/adk_training/16-mcp_integration.md)
- [MCP Agent](./workspace/python/agents/mcp-agent/)

</details>

### 🕗 Day 9

<details>
<summary>
Google ADK 工作流程編排核心-三大模式：順序流程處理依賴任務，並行流程提升執行效率，迴圈流程迭代優化品質。組合策略：透過巢狀工作流程實現複雜代理編排，解決真實世界多步驟問題。
</summary>

#### **詳細說明**：

- [文件連結](./workspace/notes/google-adk-training-hub/workflows-orchestration.md)

#### **參考資源**
- [Workflows & Orchestration](https://raphaelmansuy.github.io/adk_training/docs/workflows-orchestration)

</details>

### 🕗 Day 10

<details>
<summary>
根據文件內容，這是一份關於 Google ADK 循序工作流程的教學，說明如何使用 `SequentialAgent` 連接多個 agents 建立部落格文章產生 pipeline。透過研究、寫作、編輯、格式化四個階段，展示如何使用 `output_key` 在 agents 間傳遞資料，適合需要按順序執行的任務流程。
</summary>

#### **詳細說明**：

- [文件連結](./workspace/notes/google-adk-training-hub/adk_training/04-sequential_workflows.md)

#### **參考資源**
- [教學 04：循序工作流程 - Agent Pipelines 重點說明](./workspace/python/agents/blog-pipeline/README.md)
- [Blog Creation Pipeline](./workspace/python/agents/blog-pipeline/)
- [Tutorial 04: Sequential Workflows - Build Agent Pipelines](https://raphaelmansuy.github.io/adk_training/docs/sequential_workflows)

</details>

### 🕗 Day 11

<details>
<summary>
本教學介紹 `ParallelAgent` 同時執行多個獨立代理以提升效率，並運用「扇出/收集」模式：先平行收集資料（航班、飯店、活動），再循序合併結果成完整行程。適用於 I/O 密集型任務與多源資料收集。
</summary>

#### **詳細說明**：

- [文件連結](./workspace/notes/google-adk-training-hub/adk_training/05-parallel_processing.md)

#### **參考資源**
- [教學 05：平行處理 - 旅遊規劃系統](./workspace/python/agents/travel-planner/README.md)
- [Travel Planner](./workspace/python/agents/travel-planner/)
- [Tutorial 05: Parallel Processing - Run Multiple Agents Simultaneously](https://raphaelmansuy.github.io/adk_training/docs/parallel_processing)

</details>

### 🕗 Day 12

<details>
<summary>
本教學示範建構複雜的多代理協調流程，結合並行與循序模式。以內容發布系統為例，採用扇出/收集架構：並行執行新聞、社群、專家三個研究管線，再循序進行內容創作、編輯、格式化，實現速度與品質兼顧的智能協作系統。
</summary>

#### **詳細說明**：

- [文件連結](./workspace/notes/google-adk-training-hub/adk_training/06-multi_agent_systems.md)

#### **參考資源**
- [教學 06：多代理系統 - 內容發布系統](./workspace/python/agents/content-publisher/README.md)
- [Content Publisher](./workspace/python/agents/content-publisher/)
- [Content Publisher Agent Architecture](./workspace/python/agents/content-publisher/agent_architecture.md)
- [Tutorial 06: Multi-Agent Systems - Agents Working Together](https://raphaelmansuy.github.io/adk_training/docs/multi_agent_systems/)

</details>

### 🕗 Day 13

<details>
<summary>
教學 07：循環代理文章精煉系統 - 使用 LoopAgent 實現自我改進的代理系統，透過評論者-精煉者模式進行迭代品質提升，具備智慧終止機制和完整測試覆蓋（62個測試），展示循環代理的實際應用。
</summary>

#### **詳細說明**：

- [文件連結](./workspace/notes/google-adk-training-hub/adk_training/07-loop_agents.md)

#### **參考資源**
- [教學 07：循環代理（Loop Agents）- 文章精煉系統](./workspace/python/agents/essay-refiner/README.md)
- [Essay Refiner](./workspace/python/agents/essay-refiner/)
- [Tutorial 07: Loop Agents - Iterative Refinement with Critic/Refiner Patterns](https://raphaelmansuy.github.io/adk_training/docs/loop_agents)

</details>

### 🕗 Day 14

<details>
<summary>
本系列涵蓋 ADK 核心能力：LLM 整合篇教授提示工程、接地技術（網路/資料/位置）、思維推理框架（內建思考、Plan-ReAct）、多輪對話及性能優化；生產部署篇介紹四種部署環境、可觀測性監控、服務組態與安全實踐；進階模式篇探討即時串流、MCP 協定、A2A 通訊及多模態整合；決策框架篇提供代理類型、工具選擇、部署策略的完整決策矩陣與實施清單，助您從開發到生產全面掌握 Google ADK。
</summary>

#### **詳細說明**：

- [文件連結](./workspace/notes/google-adk-training-hub/README.md)

#### **參考資源**
- [LLM Integration](https://raphaelmansuy.github.io/adk_training/docs/llm-integration)
- [Production & Deployment](https://raphaelmansuy.github.io/adk_training/docs/production-deployment)
- [Advanced Patterns](https://raphaelmansuy.github.io/adk_training/docs/advanced-patterns)
- [Decision Frameworks](https://raphaelmansuy.github.io/adk_training/docs/decision-frameworks)

</details>

### 🕗 Day 15

<details>
<summary>
本資料提供 Google Agent Development Kit (ADK) 完整學習路徑，涵蓋從初學者到專家的 8 階段進程（57+ 天），包括代理建立、工作流程模式（Sequential/Parallel/Loop）、工具整合、狀態管理、生產部署等核心技能。附有快速參考備忘單，提供代碼範例、CLI 指令、最佳實踐與疑難排解，適合 AI 應用開發者系統學習與實作。
</summary>

#### **詳細說明**：

- [文件連結](./workspace/notes/google-adk-training-hub/README.md)

#### **參考資源**
- [Learning Paths](https://raphaelmansuy.github.io/adk_training/docs/learning-paths)
- [ADK Cheat Sheet - Complete Reference](https://raphaelmansuy.github.io/adk_training/docs/adk-cheat-sheet)

</details>

### 🕗 Day 16

<details>
<summary>
涵蓋驗證與平台選擇、入門範例建置、代理模式(循序平行迴圈)、工具整合、狀態管理、部署、安全權限、測試監控及最佳實務，並含成本管理、事件追蹤、錯誤處理與常見問題。
</summary>

#### **詳細說明**：

- [文件連結](./workspace/notes/google-adk-training-hub/README.md#六資源與支援)
- [00-setup_authentication](./workspace/notes/google-adk-training-hub/adk_training/00-setup_authentication.md)
- [01-hello_world_agent](./workspace/notes/google-adk-training-hub/adk_training/01-hello_world_agent.md)
- [hello-agent](./workspace/python/agents/hello-agent/)

#### **參考資源**
- [reference Guide](https://raphaelmansuy.github.io/adk_training/docs/reference-guide)
- [Tutorial 00: Setup & Authentication - Getting Started with Google ADK](https://raphaelmansuy.github.io/adk_training/docs/setup_authentication)
- [Tutorial 01: Hello World Agent - Build Your First AI Agent with Google ADK](https://raphaelmansuy.github.io/adk_training/docs/hello_world_agent)

</details>

### 🕗 Day 17

<details>
<summary>
教學示範建構個人化導師：利用會話狀態與 user/app/temp 前綴記錄偏好、主題與測驗分數，搜尋過往會話支援進度回顧與自適應教學。
</summary>

#### **詳細說明**：

- [文件連結](./workspace/notes/google-adk-training-hub/adk_training/08-state_memory.md)
- [personal tutor](./workspace/python/agents/personal-tutor/)

#### **參考資源**
- [Tutorial 08: State Memory - Managing Conversation Context and Data](https://raphaelmansuy.github.io/adk_training/docs/state_memory)

</details>

### 🕗 Day 18

<details>
<summary>
教學介紹ADK代理回呼：生命週期、模型、工具六鉤子；可阻擋不當內容、驗證參數、過濾PII、記錄與追蹤指標；示範內容審核助理實作護欄、安全指令、狀態管理與最佳實務。強化安全控制模式與錯誤處理測試範例涵蓋
</summary>

#### **詳細說明**：

- [文件連結](./workspace/notes/google-adk-training-hub/adk_training/09-callbacks_guardrails.md)
- [content moderator](./workspace/python/agents/content-moderator/)

#### **參考資源**
- [Tutorial 09: Callbacks & Guardrails - Control Flow and Monitoring](https://raphaelmansuy.github.io/adk_training/docs/callbacks_guardrails)

</details>

### 🕗 Day 19

<details>
<summary>
本教學介紹如何使用 pytest 和 AgentEvaluator 系統性地測試 AI agents。涵蓋測試金字塔架構:單元測試(77%)驗證工具函式與設定、整合測試(9%)驗證工作流程協調、評估測試(14%)使用 AgentEvaluator 評估軌跡與回應品質。重點在於 AI agents 的非確定性特性需要質化評估而非傳統斷言測試。提供完整實作範例,包含 22 個綜合測試、EvalSet JSON 結構描述,以及生產環境最佳實踐。
</summary>

#### **詳細說明**：

- [文件連結](./workspace/notes/google-adk-training-hub/adk_training/10-evaluation_testing.md)
- [content moderator](./workspace/python/agents/support-agent/)

#### **參考資源**
- [Tutorial 10: Evaluation & Testing - Quality Assurance for Agents](https://raphaelmansuy.github.io/adk_training/docs/evaluation_testing)

</details>

### 🕗 Day 20

<details>
<summary>
本教學介紹 ADK 進階推理能力，包含三種規劃器：BuiltInPlanner 利用 Gemini 2.0+ 原生思維能力進行透明推理；PlanReActPlanner 提供結構化的計畫→推理→行動→觀察→重新規劃流程；BasePlanner 可建立自訂規劃策略。透過 ThinkingConfig 控制思維過程的顯示。規劃器讓代理在行動前先思考，提升複雜問題的推理品質與準確性，適用於多步驟工作流程與策略性問題解決。
</summary>

#### **詳細說明**：

- [文件連結](./workspace/notes/google-adk-training-hub/adk_training/12-planners_thinking.md)
- [content moderator](./workspace/python/agents/strategic-solver/)

#### **參考資源**
- [Tutorial 12: Planners & Thinking Configuration](https://raphaelmansuy.github.io/adk_training/docs/planners_thinking)

</details>
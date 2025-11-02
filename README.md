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

#### **參考資源**
  - [Google ADK Getting Started ](https://google.github.io/adk-docs/community/#getting-started)
  - [Getting Started with Agent Development Kit Tools (MCP, Google Search, LangChain, etc.)
    ](https://www.youtube.com/watch?v=5ZmaWY7UX6k)
  - [software-bug-assistant](https://github.com/google/adk-samples/tree/main/python/agents/software-bug-assistant)
  - [Tools Make an Agent: From Zero to Assistant with ADK](https://cloud.google.com/blog/topics/developers-practitioners/tools-make-an-agent-from-zero-to-assistant-with-adk?e=48754805?utm_source%3Dtwitter?utm_source%3Dlinkedin)
  - [Tools for Agents: ADK Tools list](https://google.github.io/adk-docs/tools/)
</details>

### 🕗 Day 2
<details>
<summary>
設計 copilot 互動教學設計模式(未完成)，取得目標學習專案的相關資源，並設計互動式教學模式以協助學習者更有效地掌握專案內容。
</summary>

- **詳細說明**：
  - [文件連結](.github/chatmodes/repo-guiding-learning.chatmode.md)

- **參考資源**
  - [專案相依連結](./workspace/python/agents/software-bug-assistant/README.md)
</details>

### 🕗 Day 3
<details>
<summary>
實做範例 software-bug-assistant 專案，了解如何使用 Google ADK 建立一個能夠協助識別和修復軟體錯誤的智能代理。此專案展示了 ADK 的強大功能，並提供了實際應用的範例，幫助學習者深入理解代理程式的設計與實作過程。
</summary>

- **詳細說明**：
  - [環境初始化流程](./workspace/python/agents/software-bug-assistant/docs/INSTALLATION_GUIDE.md)
  - [文件連結](./workspace/python/agents/software-bug-assistant/README.md)

- **參考資源**
  - [software-bug-assistant](./workspace/python/agents/software-bug-assistant/)
</details>

### 🕗 Day 4
<details>
<summary>
實做範例 youtube-shorts-agent 專案，了解如何使用 Google ADK 建立一個能夠協助生成和管理 YouTube Shorts 內容的智能代理。此專案展示了 ADK 的強大功能，並提供了實際應用的範例，幫助學習者深入理解代理程式的設計與實作過程。
</summary>

- **詳細說明**：
  - [文件連結](./workspace/python/agents/youtube-shorts-assistant/README.md)
  - [學習訓練指引筆記](./workspace/notes/google-adk-training-hub/README.md)

- **參考資源**
  - [Getting started with Agent Development Kit](https://www.youtube.com/watch?v=44C8u0CDtSo)
  - [youtube-shorts-assistant 專案Repo](./workspace/python/agents/youtube-shorts-assistant/)
  - [Google ADK Training Hub](https://raphaelmansuy.github.io/adk_training/)
</details>


### 🕗 Day 5
<details>
<summary>
實現範例 finance-assistant 專案，了解如何使用 Google ADK 建立一個能夠協助管理和分析財務數據的智能代理。包含基本 ADK Tools 的應用，並透過 asyncio.gather(*tasks) 平行處理任務與完整 Agent 測試案例實現。
</summary>

- **詳細說明**：
  - [文件連結](./workspace/python/agents/finance-assistant/README.md)

- **參考資源**
  - [Tutorial 02: Function Tools Implementation](https://github.com/raphaelmansuy/adk_training/tree/main/tutorial_implementation/tutorial02)
  - [finance-assistant](./workspace/python/agents/finance-assistant/)
  - [Tutorial 02: Function Tools - Give Your Agent Superpowers](https://raphaelmansuy.github.io/adk_training/docs/function_tools)
</details>

### 🕗 Day 6
<details>
<summary>
實現範例 chuck-norris-agent 專案，學習如何從 OpenAPI 規範中自動產生工具，使您的代理程式能夠與 REST API 互動，而無需手動編寫工具函式。。
</summary>

- **詳細說明**：
  - [文件連結](./workspace/python/agents/chuck-norris-agent/README.md)

- **參考資源**
  - [Tutorial 03: OpenAPI Tools - Connect Your Agent to Web APIs](https://raphaelmansuy.github.io/adk_training/docs/openapi_tools/)
  - [# 教學 03：OpenAPI 工具 - REST API 整合](./workspace/notes/google-adk-training-hub/hands-on/openapi_tools.md)
  - [chuck-norris-agent](./workspace/python/agents/chuck-norris-agent/)
  - [Tutorial 03: Chuck Norris OpenAPI Tools Agent](https://github.com/raphaelmansuy/adk_training/tree/main/tutorial_implementation/tutorial03/)
</details>

### 🕗 Day 7
<details>
<summary>
本教學介紹 Gemini 2.0+ 的內建工具,包含網路搜尋、地圖定位和企業搜尋功能,讓 AI 代理程式存取即時資訊。核心內容涵蓋:google_search 網路基礎工具、google_maps_grounding 位置服務(需 VertexAI)、enterprise_web_search 企業搜尋、GoogleSearchAgentTool 混合工具解決方案。同時介紹記憶體管理、工作流程控制、上下文載入等進階工具。透過實作研究助理範例,展示如何整合多種工具建立生產級代理程式系統,包含最佳實踐與疑難排解指南。
</summary>

- **詳細說明**：
  - [文件連結](./workspace/python/agents/chuck-norris-agent/README.md)

- **參考資源**
  [# 教學 11：內建工具與基礎 (Built-in Tools & Grounding)](./workspace/notes/google-adk-training-hub/hands-on/built_in_tools_grounding.md)
  [Grounding Agent](./workspace/python/agents/grounding-agent/)
</details>

### 🕗 Day 8
<details>
<summary>
本教學介紹如何使用模型內容協議 (MCP) 將外部工具和服務整合到 AI 代理程式中。透過 MCPToolset 連接 MCP 伺服器，讓代理程式能夠存取檔案系統、資料庫、API 等外部資源，並支援 OAuth 驗證與人機迴圈審批等進階功能。
</summary>

- **詳細說明**：
  - [文件連結](./workspace/python/agents/mcp-agent/README.md)

- **參考資源**
  [# 教學 16: 模型內容協議 (MCP) 整合 - 標準化工具協議](./workspace/notes/google-adk-training-hub/hands-on/mcp_integration.md)
  [MCP Agent](./workspace/python/agents/mcp-agent/)
</details>

### 🕗 Day 9
<details>
<summary>
Google ADK 工作流程編排核心-三大模式：順序流程處理依賴任務，並行流程提升執行效率，迴圈流程迭代優化品質。組合策略：透過巢狀工作流程實現複雜代理編排，解決真實世界多步驟問題。
</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/04_workflows-orchestration.md)

- **參考資源**
  - [Workflows & Orchestration]([./workspace/notes/google-adk-training-hub/hands-on/mcp_integration.md](https://raphaelmansuy.github.io/adk_training/docs/workflows-orchestration))
</details>

### 🕗 Day 10
<details>
<summary>
根據文件內容，這是一份關於 Google ADK 循序工作流程的教學，說明如何使用 `SequentialAgent` 連接多個 agents 建立部落格文章產生 pipeline。透過研究、寫作、編輯、格式化四個階段，展示如何使用 `output_key` 在 agents 間傳遞資料，適合需要按順序執行的任務流程。
</summary>

- **詳細說明**：
  - [文件連結](./workspace/notes/google-adk-training-hub/hands-on/sequential_workflows.md)

- **參考資源**
  - [教學 04：循序工作流程 - Agent Pipelines 重點說明](./workspace/notes/google-adk-training-hub/hands-on/sequential_workflows.md)
  - [Blog Creation Pipeline](./workspace/python/agents/blog-pipeline/)
  - [Tutorial 04: Sequential Workflows - Build Agent Pipelines](https://raphaelmansuy.github.io/adk_training/docs/sequential_workflows)
</details>
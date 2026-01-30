# 關於 Agent Development Kit (ADK)

> 🔔 `更新日期：2026-01-30`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/get-started/about/

**無縫地建置、評估與部署代理程式！**

ADK 旨在賦予開發者建置、管理、評估與部署 AI 驅動代理程式的能力。它為建立對話型與非對話型代理程式提供了一個強大且靈活的環境，能夠處理複雜的任務與工作流。

![intro_components.png](https://google.github.io/adk-docs/assets/adk-components.png)

## 核心概念

ADK 圍繞著幾個關鍵的原語 (primitives) 與概念建構，使其強大且靈活。以下是基本要素：

| 原語 (Primitive)                   | 說明 (Description)                                                                                      | 相關 API/概念 (Related API/Concept)                         |
| :--------------------------------- | :------------------------------------------------------------------------------------------------------ | :---------------------------------------------------------- |
| **Agent (代理程式)**               | 設計用於特定任務的基本工作單元。                                                                        | `LlmAgent`, `SequentialAgent`, `ParallelAgent`, `LoopAgent` |
| **Tool (工具)**                    | 賦予代理程式對話以外的能力，讓它們與外部 API 互動、搜尋資訊、執行程式碼或呼叫其他服務。                 | `FunctionTool`, `AgentTool`                                 |
| **Callbacks (回呼)**               | 在代理程式處理過程中的特定點執行的自定義程式碼片段，用於檢查、日誌記錄或行為修改。                      | -                                                           |
| **Session Management (會話管理)**  | 處理單個對話 (`Session`) 的上下文，包括其歷史記錄 (`Events`) 和代理程式在該對話中的工作記憶 (`State`)。 | `Session`, `State`, `Events`                                |
| **Memory (記憶)**                  | 使代理程式能夠跨 _多個_ 會話記住有關使用者的資訊，提供長期上下文。                                      | `MemoryService`                                             |
| **Artifact Management (產物管理)** | 允許代理程式儲存、載入與管理與會話或使用者相關的檔案或二進位數據（如圖像、PDF）。                       | `Artifact`, `ArtifactService`                               |
| **Code Execution (程式碼執行)**    | 代理程式（通常透過工具）產生並執行程式碼以執行複雜計算或動作的能力。                                    | -                                                           |
| **Planning (規劃)**                | 一種進階能力，代理程式可以將複雜目標拆解為較小的步驟，並規劃如何達成。                                  | `ReAct`                                                     |
| **Models (模型)**                  | 驅動 `LlmAgent` 的底層 LLM，賦予其推理與語言理解能力。                                                  | `BaseLlm`                                                   |
| **Event (事件)**                   | 會話期間發生的基本通信單元（使用者訊息、代理程式回覆、工具使用），構成對話歷史。                        | -                                                           |
| **Runner (執行器)**                | 管理執行流程的引擎，根據事件協調代理程式互動，並與後端服務配合。                                        | -                                                           |

**_備註：_** 多模態串流、評估、部署、偵錯與追蹤等功能也是廣泛 ADK 生態系統的一部分，支援即時互動與開發生命週期。

## 關鍵能力

ADK 為建置代理型應用程式的開發者提供了幾個關鍵優勢：

| # | 能力 (Capability)      | 說明 (Description)                                                                                                                                                                                                                                                                                          |
| :- | :--------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | **多代理程式系統設計 (Multi-Agent)** | 輕鬆建置由多個階層排列的專門代理程式組成的應用程式。代理程式可以協調複雜任務，使用 LLM 驅動的轉移或顯式的 `AgentTool` 調用來委派子任務，實現模組化與可擴展的解決方案。                                                                                                                                      |
| 2 | **豐富的工具生態系統 (Rich Tool)** | 為代理程式配備多樣化的能力。ADK 支援整合自定義函數 (`FunctionTool`)、將其他代理程式作為工具使用 (`AgentTool`)、利用內建功能（如程式碼執行），以及與外部數據源和 API（如搜尋、資料庫）互動。支援長時間運行的工具，可有效處理非同步操作。                                                                     |
| 3 | **靈活的編排 (Flexible Orchestration)**         | 使用內建的工作流代理程式（`SequentialAgent`, `ParallelAgent`, `LoopAgent`）以及 LLM 驅動的動態路由來定義複雜的代理程式工作流。這允許預測性的流水線與自適應的代理程式行為。                                                                                                                                  |
| 4 | **整合的開發者工具 (Developer Tooling)**   | 輕鬆進行本地開發與迭代。ADK 包含命令行介面 (CLI) 和開發者 UI，用於運行代理程式、檢查執行步驟（事件、狀態更改）、偵錯互動以及視覺化代理程式定義。                                                                                                                                                            |
| 5 | **原生串流支援 (Streaming Support)**       | 透過原生支援雙向串流（文字與音訊）建置即時、互動式的體驗。這與 [Gemini Developer API 的 Multimodal Live API](https://ai.google.dev/gemini-api/docs/live) (或 [Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/multimodal-live)) 無縫整合，通常只需簡單的配置更改即可啟用。 |
| 6 | **內建代理程式評估 (Built-in Agent Evaluation)**   | 系統地評估代理程式性能。該框架包含建立多輪評估數據集並在本地運行評估（透過 CLI 或開發者 UI）的工具，以衡量品質並指導改進。                                                                                                                                                                                  |
| 7 | **廣泛的 LLM 支援 (Broad LLM Support)**    | 雖然針對 Google 的 Gemini 模型進行了優化，但該框架設計靈活，允許透過其 `BaseLlm` 介面整合各種 LLM（可能包括開源或微調模型）。                                                                                                                                                                               |
| 8 | **Artifact 管理 (Artifact Management)**           | 使代理程式能夠處理檔案與二進位數據。框架提供了機制（`ArtifactService`, 上下文方法），供代理程式在執行期間儲存、載入與管理具備版本的產物（如圖像、文件或產生的報告）。                                                                                                                                       |
| 9 | **擴展性與互通性 (Extensibility and Interoperability)**     | ADK 促進開放生態系統。在提供核心工具的同時，它允許開發者輕鬆整合與重用第三方工具與數據連接器。                                                                                                                                                                                                              |
| 10 | **狀態與記憶管理 (State and Memory Management)**     | 自動處理由 `SessionService` 管理的短對話記憶（會話內的 `State`）。提供長期 `Memory` 服務的整合點，允許代理程式跨多個會話回憶使用者資訊。                                                                                                                                                                    |

![intro_components.png](https://google.github.io/adk-docs/assets/adk-lifecycle.png)

## 如何開始使用 ADK
- 準備建立您的第一個代理程式？請參閱我們的 [快速入門指南](index.md)。

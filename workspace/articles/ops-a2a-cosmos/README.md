# AI 維運宇宙：一個基於多 Agent 協作的 A2A 資料串流設計

本系列文章深入探討如何設計一個由多個智慧代理人（Agent）協同工作的 AI 維運平台。此架構整合了 Google ADK、A2A（Agent-to-Agent）通訊協定、MCP（Model Context Protocol）以及 Kafka 資料串流技術，旨在實現從事件監控、分析、知識查詢到自動化修復的端到端智慧維運流程。

## 核心設計理念

我們將維運任務拆解給不同職責的 Agent，讓它們透過標準化的 A2A 協定進行溝通，形成一個高效、可擴展的「維運大腦」。

- **資料驅動**：以 Kafka 作為系統的資料血管，傳遞所有監控事件、日誌與指標。
- **工具賦能**：透過 MCP 讓 Agent 能安全地存取內部系統與工具（如 K8s、ITSM、Confluence）。
- **任務協作**：利用 A2A 讓 Agent 之間可以互相委派任務、回報結果，實現複雜的維運工作流。
- **人機共駕**：設計 SRE Copilot Agent 作為人類工程師與 AI Agent Mesh 的互動介面，確保系統的可控性與透明度。


## 完整設計目錄

### 第一部分：總體設計與概念

| 章節 | 主題 | 內容摘要 |
| :--- | :--- | :--- |
| 1. | [維運多 Agent 協作宇宙 (Ops Flow Design)](./01_ops-flow-design.md) | 介紹維運多 Agent 協作的核心概念，並透過 P1 事故處理時序圖展示整體工作流程。 |
| 2. | [A2A Agent 職責表 (Agents)](./02_agents.md) | 詳細定義 Monitoring, Triage, Runbook, Execution, SRE Copilot 等五個 Agent 的角色與功能。 |
| 3. | [技術棧選型考量 (Tech Stacks)](./03_tech-stacks.md) | 盤點此架構中使用的各層技術，包含 Agent 框架、資料串流、監控、知識庫、自動化與協作平台。 |
| 4. | [整合視圖 (Integrated View)](./04_integrated.md) | 透過 Matrix 圖表，清晰呈現每個 Agent 如何與不同技術層次對應與互動。 |
| 5. | [設計與開發計畫 (Design Plan)](./05_design-plan.md) | 提供一份可作為開發任務參考的完整設計目錄，涵蓋從需求、架構、模組設計到維運部署的各個環節。 |

### 第二部分：各 Agent 模組深度設計

| 章節 | Agent 模組 | 內容摘要 |
| :--- | :--- | :--- |
| 6. | [**Monitoring Agent 設計**](./06_monitoring-agent.md) | 設計維運事件的「前線偵測與降噪者」，負責從 Kafka 吸收事件並產出可分析的候選事件。 |
| 7. | [**Incident Triage Agent 設計**](./07_Incident-triage-agent.md) | 深度剖析指揮中心 Agent 的模組設計，包含狀態機、決策邏輯、MCP/A2A 介面規格與審計需求。 |
| 8. | [**Runbook/Knowledge Agent 設計**](./08_runbook-knowledge-agent.md) | 設計維運知識中樞，說明如何透過 MCP 整合 Confluence, ITSM, Vector DB，並以 A2A 提供知識服務。 |
| 9. | [**Execution/Automation Agent 設計**](./09_execution-agent.md) | 設計「會動手」的自動化代理人，包含其安全白名單、MCP 工具集（K8s, CI/CD）與風險控制。 |
| 10. | [**SRE Copilot Agent 設計**](./10_sre-copilot-agent.md) | 設計面向人類的互動介面，處理 ChatOps 指令解析、通知升級，並協助產出 Postmortem。 |

### 第三部分：總結

| 章節 | 主題 | 內容摘要 |
| :--- | :--- | :--- |
| 11. | [總結 (Summary)](./11_summary.md) | 以一張完整的架構圖總覽全局，並回顧整個設計的核心重點。 |

# 完整開發設計藍圖 (Design Plan)

>可列為開發任務參考

## 1. 文件說明（Document Overview）

1.1 文件目的與讀者對象
1.2 系統範圍（In Scope / Out of Scope）
1.3 名詞與縮寫說明（ADK、A2A、MCP、RAG…）
1.4 參考文件與連結（現有監控設計、SRE 手冊、雲平台標準…）

## 2. 背景與需求（Background & Requirements）

2.1 現行維運痛點說明
2.2 導入多 Agent 維運平台之目標

* 降低 Alert 噪音
* 縮短 MTTR
* 提升自動化比例
  2.3 功能性需求（FR）總表
  2.4 非功能性需求（NFR）總表
* 可用性、延遲、擴充性、審計、合規（金融業重要）

## 3. 整體架構概觀（High-Level Architecture）

3.1 系統高階架構圖（Agents + Kafka + Observability + Infra + ChatOps）
3.2 分層架構說明（技術層分層：Framework / Data Streaming / Observability / Knowledge / Infra / Collaboration）
3.3 多 Agent Mesh 概念與角色說明
3.4 與既有系統 / 平台的關係（ESB、現有監控、ITSM、K8s 平台等）

## 4. 模組總覽與分層（Module Overview & Layering）

4.1 模組清單（Module Inventory）

* Agent 模組
* 平台 / 協定模組
* 觀測性模組
* 資料流模組
* 自動化執行模組
* 協作與通報模組

4.2 模組分層圖（以技術層為 Y 軸 / Agent 為 X 軸）
4.3 模組邊界與責任界定原則（Do / Don’t）

## 5. Agent 模組設計（Agent Layer Design）

> 每個 Agent 一個小節，結構一致，方便對比與治理。

5.1 Monitoring Agent 模組設計

* 5.1.1 職責與行為描述
* 5.1.2 主要輸入 / 輸出（Input/Output）
* 5.1.3 依賴技術棧

  * ADK / A2A
  * Kafka / Kafka Streams
  * Observability（metrics/logs/alerts）
* 5.1.4 關聯 MCP Tools（如有）
* 5.1.5 A2A 介面設計（對 Triage Agent）
* 5.1.6 錯誤處理與降噪策略

5.2 Incident Triage Agent 模組設計

* 5.2.1 職責與行為描述（事件分級 / 影響分析 / 指揮中樞）
* 5.2.2 事件處理流程（狀態機 / Flow 圖）
* 5.2.3 依賴技術棧

  * ADK / A2A / MCP
  * Kafka 事件 context
  * Metrics / Logs / Traces
  * CMDB / Deploy History / ITSM
* 5.2.4 MCP Tools 使用設計（cmdb_lookup、deploy_history、metrics_query、log_query…）
* 5.2.5 A2A 介面設計

  * 從 Monitoring 接案
  * 對 Runbook 發問
  * 對 Execution 下達行動
  * 對 SRE Copilot 報告
* 5.2.6 決策策略與風險控管（何時自動？何時必須人類 confirm？）

5.3 Runbook / Knowledge Agent 模組設計

* 5.3.1 職責與行為描述（知識檢索 / 類似事件比對 / 建議生成）
* 5.3.2 RAG & 檢索流程說明
* 5.3.3 依賴技術棧

  * ADK / A2A / MCP
  * Confluence / Wiki / SharePoint
  * ITSM / Ticket
  * Git Docs
  * Vector DB
* 5.3.4 MCP Tools 設計（confluence_search、itsm_ticket_search、git_doc_search、vector_search）
* 5.3.5 A2A 介面設計（RunbookQuery / RunbookResponse）
* 5.3.6 知識新鮮度與版本治理策略

5.4 Execution / Automation Agent 模組設計

* 5.4.1 職責與行為描述（負責實際執行自動化修復）
* 5.4.2 行動流程設計（含前置檢查 / 後置驗證）
* 5.4.3 依賴技術棧

  * ADK / A2A / MCP
  * Kubernetes / Service Mesh
  * CI/CD Pipeline
  * Feature Flags
* 5.4.4 MCP Tools 設計（k8s_scaling、k8s_restart、mesh_route_update、cd_rollback、flag_toggle…）
* 5.4.5 A2A 介面設計（ActionRequest / ActionResult）
* 5.4.6 安全控制與白名單策略（可執行操作範圍 / 審計需求）

5.5 SRE Copilot Agent 模組設計

* 5.5.1 職責與行為描述（人機介面 / ChatOps / 說明與建議）
* 5.5.2 User Journey（On-call 工程師體驗流程）
* 5.5.3 依賴技術棧

  * ADK / A2A / MCP
  * ChatOps（Slack / Teams）
  * PagerDuty / Opsgenie
  * ITSM / Dashboard（Grafana / Kibana）
* 5.5.4 MCP Tools 設計（chatops_post、pagerduty_trigger、itsm_open_ticket、postmortem_builder 等）
* 5.5.5 A2A 介面設計（匯總其他 Agent 結果 + 轉換人類指令為 A2A 任務）
* 5.5.6 UX 與溝通語氣設計（金融業合規用語 / 風險提示方式）

## 6. 平台與協定模組設計（ADK / A2A / MCP）

6.1 Google ADK 平台設計

* Agent 生命週期管理
* Agent 部署模式（集中 / 分散）

6.2 A2A Protocol 模組設計

* 訊息型態（Task、Response、Event）
* 通訊模式（同步 / 非同步 / 超時處理）
* Security & Auth（Agent 間的身份驗證 / 授權）

6.3 MCP 模組設計

* MCP Server 佈署架構
* MCP Tool 生命週期與維運策略
* 共用錯誤格式與重試策略

## 7. 資料流與事件模組設計（Kafka & Streaming）

7.1 Kafka Cluster 與 Topic 規劃

* metrics / logs / alerts / incident_candidate
  7.2 Streaming Job 設計（Kafka Streams / Flink）
* 降噪規則 / window / join
  7.3 事件 Schema 設計（Avro / Protobuf）
* MonitoringEvent / IncidentCandidate / HealthSummary

## 8. Observability 模組設計

8.1 Metrics 架構

* 指標命名規範
* 與 Agent 相關的 metrics（Agent latency、成功率、決策數量）

8.2 Logs & Tracing 設計

* Agent log 格式
* 追蹤一個 incident 的 trace id / correlation id 策略

8.3 Alerting 策略

* 哪些仍由傳統規則發 Alert
* 哪些改由 Agent 推薦 / 組合判斷

## 9. 知識與文件模組設計（Knowledge Layer）

9.1 知識來源盤點（Confluence / ITSM / Git / PDF…）
9.2 向量化與 Index 建置流程（RAG Pipeline）
9.3 知識更新與過期治理（Data Freshness Policy）

## 10. 自動化執行與平台模組設計（Infra Automation）

10.1 K8s / Mesh / CI/CD / Feature Flag 集成架構圖
10.2 可自動化動作清單與風險等級
10.3 回滾與保護機制（Manual Override / Kill Switch）

## 11. 協作與人機介面模組設計（Collaboration）

11.1 ChatOps Flow（Slack / Teams Bot）
11.2 On-call 通知流程（PagerDuty / Opsgenie）
11.3 Dashboard 整合（Grafana / Kibana 顯示 AI 分析結果）

## 12. 資安與權限設計（Security & Permission）

12.1 Agent 身份與權限模型（Which Agent can call which Tool）
12.2 MCP Tool 權限控管（只讀 / 可寫 / 高風險操作）
12.3 審計與 Log 留存（for 監理 / 稽核）

## 13. 非功能需求與 SRE 指標（NFR & SLO）

13.1 各 Agent 延遲 / 可用性 SLO
13.2 事件處理全鏈路 SLO（Alert → Decision → Action → Recover）
13.3 容錯、備援與 DR 策略

## 14. 開發與部署流程（DevOps & Lifecycle）

14.1 多 Agent 開發流程（分 repo / monorepo / 共用 library）
14.2 測試策略（Unit / Integration / E2E / Chaos）
14.3 環境規劃（DEV / STG / PROD）
14.4 部署策略（滾動升級 / 金絲雀配置）

## 15. PoC 與導入 Roadmap

15.1 PoC 範圍（先從哪幾個 Agent / 哪個場景開始）
15.2 成功指標（KPI：MTTR 降低、Alert 噪音降低、自動化比例…）
15.3 分階段導入計畫（Phase 1~3）

***
[<< 上一篇：整合視圖](./04_integrated.md) | [返回目錄](./README.md) | [下一篇：Monitoring Agent 設計 >>](./06_monitoring-agent.md)

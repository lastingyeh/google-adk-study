# 整合技術棧 (Tech Stacks)

## 一、總覽：Agent × 技術類別

先用「類別」對齊（避免把表弄得超爆大），你看大方向：

| Agent \ 技術類別                  | ADK / A2A / MCP   | Kafka / Streaming       | Observability（Metrics/Logs/Tracing） | 知識&文件（Confluence/ITSM/Git/RAG）      | 自動化&平台（K8s/Mesh/CI/CD/Flag）             | 協作&介面（ChatOps/On-call）                 |
| ----------------------------- | ----------------- | ----------------------- | ----------------------------------- | ----------------------------------- | --------------------------------------- | -------------------------------------- |
| **Monitoring Agent**          | ✅ ADK / A2A       | ✅ 主要讀 Kafka / Streaming | ✅（吃告警/metrics 輸出）                   | ❌ 不直接查                              | ❌ 不直接操作                                 | ❌（通常不直接跟人互動）                           |
| **Incident Triage Agent**     | ✅ ADK / A2A / MCP | ✅（可用事件 context）         | ✅（用 MCP 補查 metrics/logs/traces）     | ⚠️（可少量查歷史 incident）                 | ❌（不下指令，只做決策）                            | ⚠️（部分輸出交給 SRE Copilot）                 |
| **Runbook / Knowledge Agent** | ✅ ADK / A2A / MCP | ❌（多半不直接讀 Kafka）         | ⚠️（可從 log/metrics 系統取樣）             | ✅（主力：Confluence/ITSM/Git/Vector DB） | ❌（不直接下指令）                               | ❌（不直接對人）                               |
| **Execution Agent**           | ✅ ADK / A2A / MCP | ❌（一般不直接讀 event）         | ⚠️（可在執行前後查 health）                  | ❌                                   | ✅（主力：K8s / Mesh / CI/CD / Feature Flag） | ❌（執行報告交給 Triage/SRE Copilot）           |
| **SRE Copilot Agent**         | ✅ ADK / A2A / MCP | ❌（通常不直接訂閱 Kafka）        | ⚠️（顯示摘要）                            | ⚠️（顯示摘要）                            | ⚠️（代表人類送 A2A 給 Execution）               | ✅（Slack/Teams + PagerDuty + Dashboard） |

---

## 二、細部 Mapping：每個 Agent 對應哪些技術

### 1️⃣ Monitoring Agent

| 項目             | 對應技術                                                     |
| -------------- | -------------------------------------------------------- |
| Framework / 協議 | Google ADK、A2A Protocol                                  |
| 主要資料來源         | Kafka、Kafka Streams（處理後的事件流）                             |
| Observability  | Prometheus / Alertmanager → 透過 Exporter / Bridge 丟 Kafka |
| MCP Tools      | （可選）metrics_query_tool、log_query_tool（通常非必要）             |
| 不負責            | K8s 操作、CI/CD、Feature Flags、ChatOps、ITSM                  |

👉 定位：**維運事件的「前置清洗 / 降噪器」**。

---

### 2️⃣ Incident Triage Agent

| 項目             | 對應技術                                                                                                               |
| -------------- | ------------------------------------------------------------------------------------------------------------------ |
| Framework / 協議 | Google ADK、A2A Protocol、MCP                                                                                        |
| 資料來源           | - Kafka（事件 context）<br>- MCP：metrics_query_tool（Prometheus）、log_query_tool（Loki/ELK）、trace_query_tool（Jaeger/OTel） |
| 系統知識           | MCP：cmdb_lookup_tool、deploy_history_tool、incident_lookup_tool                                                      |
| 不直接碰           | K8s / CI/CD / Feature Flag（交給 Execution Agent）、人類 ChatOps（交給 SRE Copilot）                                          |

👉 定位：**維運 AI 中樞 / 指揮官**

* 善用 Observability + CMDB + Deploy History
* 把 Runbook Agent 知識 + Execution Agent 能力串起來。

---

### 3️⃣ Runbook / Knowledge Agent

| 項目                | 對應技術                                                                                                                                                                       |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Framework / 協議    | Google ADK、A2A Protocol、MCP                                                                                                                                                |
| 知識來源（MCP Tools）   | - Confluence / Wiki / SharePoint search<br>- ITSM ticket search（ServiceNow / Jira SM）<br>- Git repo doc search（README, docs, infra）<br>- Vector DB（RAG 搜尋相似事件與 Runbook 段落） |
| Observability（選用） | log_sample_tool（取少量 log 當 prompt context）                                                                                                                                  |
| 不負責               | Kafka 訂閱、K8s & CI/CD 操作、ChatOps 互動                                                                                                                                         |

👉 定位：**維運世界的「百科＋歷史事件顧問」**

* 所有「去查文件、看以前怎麼做」的事情，都集中在這個 Agent。

---

### 4️⃣ Execution / Automation Agent

| 項目                | 對應技術                                                                                                                                                                                                                          |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Framework / 協議    | Google ADK、A2A Protocol、MCP                                                                                                                                                                                                   |
| 執行工具（MCP）         | - K8s API（rollout restart, scale, drain node）<br>- Service Mesh API（traffic route / canary rollback）<br>- CI/CD API（rollback pipeline, redeploy）<br>- Feature Flag API（enable/disable feature）<br>- Script Runner（白名單 Script） |
| Observability（選用） | 執行前後透過 MCP 查 health（Prometheus、ELK）                                                                                                                                                                                           |
| 不負責               | 查知識（交給 Runbook Agent）、開票/通知（交給 SRE Copilot）、事件分級（交給 Triage Agent）                                                                                                                                                             |

👉 定位：**「會真的動手」的 Agent**，所有動作都要有 audit log、白名單、權限控管。

---

### 5️⃣ SRE Copilot Agent

| 項目             | 對應技術                                                                                                                          |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Framework / 協議 | Google ADK、A2A Protocol、MCP                                                                                                   |
| 協作工具（MCP）      | - ChatOps：Slack / MS Teams Bot API<br>- On-call：PagerDuty / Opsgenie API<br>- Ticket：ITSM（ServiceNow / Jira）create/update API |
| 顯示資料           | 從 Triage / Runbook / Execution Agents 收到 A2A 結果，整理成自然語言摘要，必要時附 link 至 Grafana / Kibana / ITSM。                                |
| 不負責            | 直接讀 Kafka、直接操作 K8s / CI/CD（它只「替人類發話」，真正操作交給 Execution Agent）。                                                                 |

👉 定位：**人類入口 / 窗口**，把所有背後的 AI 決策包裝成人類看得懂又能掌控的對話與通知。

---

## 三、Agent × 技術層分類

| **Agent \ 技術層**               | **Framework / Protocols**<br>(ADK / A2A / MCP)                         | **Data Streaming 層**<br>(Kafka / Streaming) | **Observability 層**<br>(Metrics / Logs / Traces)              | **Knowledge 層**<br>(Docs / ITSM / Vector DB)                    | **Infra 自動化層**<br>(K8s / Mesh / CI/CD / Flags)                        | **Collaboration 層**<br>(ChatOps / On-call)                         |
| ----------------------------- | ---------------------------------------------------------------------- | ------------------------------------------- | ------------------------------------------------------------- | --------------------------------------------------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------ |
| **Monitoring Agent**          | Google ADK<br>A2A Protocol                                             | Kafka 訂閱<br>Kafka Streams                   | Prometheus Metrics<br>Loki / ELK Logs<br>Alertmanager         | （不使用知識庫）                                                        | （不使用 Infra）                                                           | （不與人互動）                                                            |
| **Incident Triage Agent**     | Google ADK<br>A2A Protocol<br>MCP（cmdb / deploy / metrics / logs）      | Kafka（作為事件 context）                         | Metrics（Prometheus）<br>Logs（Loki/ELK）<br>Tracing（Jaeger/OTel） | ITSM 查詢（歷史事件）                                                   | （不執行動作）                                                               | 與 SRE Copilot 協作                                                   |
| **Runbook / Knowledge Agent** | Google ADK<br>A2A Protocol<br>MCP（Confluence / ITSM / Git / Vector DB） | （不直接使用 Kafka）                               | Logs（少量 log sample 查詢）                                        | Confluence / Wiki<br>ITSM Tickets<br>Git Docs<br>Vector DB（RAG） | （不執行 Infra）                                                           | （不與人互動）                                                            |
| **Execution Agent**           | Google ADK<br>A2A Protocol<br>MCP（K8s / Mesh / CI/CD / Flags）          | （不使用 Kafka 事件流）                             | Metrics（健康檢查）                                                 | （不查知識庫）                                                         | Kubernetes 操作<br>Service Mesh 控制<br>CI/CD Rollback<br>Feature Flag 切換 | （不直接互動）<br>結果回傳由 Triage/SRE Copilot 轉給人                            |
| **SRE Copilot Agent**         | Google ADK<br>A2A Protocol<br>MCP（ChatOps / ITSM / PagerDuty）          | （不訂閱 Kafka）                                 | 顯示摘要<br>不直接查 Metrics/Logs                                     | 顯示 Runbook/Triage 摘要                                            | （不直接操作）<br>可代理人類下指令給 Execution Agent                                  | Slack / Teams<br>PagerDuty / Opsgenie<br>Dashboard（Grafana/Kibana） |

***
[<< 上一篇：技術棧選型考量](./03_tech-stacks.md) | [返回目錄](./README.md) | [下一篇：設計與開發計畫 >>](./05_design-plan.md)

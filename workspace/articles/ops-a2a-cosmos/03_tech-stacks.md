# 技術棧應用說明

## 一、Agent & 協議層技術棧

| 技術項目                            | 類型 / 所屬層級            | 使用功能                                                | 在本架構中的目的與說明                                                                                                                |
| ------------------------------- | -------------------- | --------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| **Google ADK**                  | Agent 平台 / Framework | 建立、管理多個 LLM Agent；定義每個 Agent 的 role、tools、workflow。 | 作為整個「維運多 Agent Mesh」的底層框架，每個 Monitoring/Triage/Runbook/Execution/SRE Copilot 都是一個 ADK Agent。                               |
| **A2A Protocol（Agent2Agent）**   | Agent 通訊協定           | 定義 Agent 與 Agent 之間如何互相發任務、回覆結果、傳遞 context。         | 讓 Incident Triage Agent 可以以標準化方式「詢問」Runbook Agent、「委派」Execution Agent，形成可擴充的 Agent Mesh。                                   |
| **MCP（Model Context Protocol）** | Agent ↔ 工具通訊協定       | 讓 Agent 可以透過標準介面呼叫各種「工具」：API、DB、搜尋、內部系統。            | Runbook Agent 透過 MCP 查 Confluence/ITSM/Git/向量庫；Triage Agent 用 MCP 查 CMDB、deploy history；Execution Agent 用 MCP 控制 K8s/CD 等。 |

---

## 二、資料流 / 事件 / Streaming 層

| 技術項目                                   | 類型 / 所層級               | 使用功能                                        | 在本架構中的目的與說明                                                                |
| -------------------------------------- | ---------------------- | ------------------------------------------- | -------------------------------------------------------------------------- |
| **Apache Kafka**                       | 訊息中介 / 事件總線            | 高吞吐、可持久化的事件傳輸（metrics、logs、alerts、應用事件）。    | 收集各監控系統與應用的事件，透過 topic 統一輸送給 Streaming Job 與 Monitoring Agent，形成維運資料的「血管」。 |
| **Kafka Streams**                      | Streaming library      | 直接在 Kafka 上做 window、聚合、join 等 streaming 分析。 | 將原始 metrics/alerts 聚合成 IncidentCandidate（事件候選），減少噪音，供 Monitoring Agent 使用。 |
| **Apache Flink / Beam / Dataflow（擇一）** | Streaming / Batch 處理引擎 | 做更複雜的 real-time 分析、pattern 偵測、跨多來源資料處理。     | 若需要更複雜的維運事件偵測邏輯（例如結合 business event + infra event），可用來產生高階維運特徵流。           |
| **事件 Schema（Avro / Protobuf）**         | 資料契約 / Schema 定義       | 定義 Kafka 訊息的欄位與版本，避免 schema 演進失控。           | 確保 Monitoring/Triage/其他 agent 在解析 Kafka 事件時有一致結構，方便擴充與治理。                  |

---

## 三、監控 & Observability 層

| 技術項目                                              | 類型 / 所層級            | 使用功能                          | 在本架構中的目的與說明                                                              |
| ------------------------------------------------- | ------------------- | ----------------------------- | ------------------------------------------------------------------------ |
| **Prometheus / 雲端 Metrics 服務**                    | Metrics 監控          | 收集服務 CPU、記憶體、延遲、錯誤率等 metrics。 | 提供維運基礎指標，經由 Exporter / Bridge 推送到 Kafka，或由 Triage Agent 透過 MCP 查詢。       |
| **Loki / ELK（Elasticsearch + Logstash + Kibana）** | Log 監控 / 搜尋         | 集中、查詢、分析應用與系統 log。            | Runbook Agent/Triage Agent 可透過 MCP 的 log 搜尋工具查歷史 log 範例，協助定位 root cause。 |
| **Alertmanager / 監控告警系統**                         | Alert 管理            | 根據 metrics 規則產生告警並通知。         | 告警可經由 Kafka 或 API 提供給 Monitoring Agent，作為「事件候選」輸入來源之一。                   |
| **Tracing 系統（Jaeger / OpenTelemetry Collector）**  | Distributed tracing | 跟蹤跨服務請求鏈路，查看瓶頸與錯誤來源。          | Triage Agent 可透過 MCP 存取 tracing 資訊，輔助判斷是哪個 service 或哪個 hop 出問題。          |

---

## 四、知識 / 文件 / 歷史事件層

| 技術項目                                                              | 類型 / 所層級     | 使用功能                                        | 在本架構中的目的與說明                                                                                                |
| ----------------------------------------------------------------- | ------------ | ------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| **Confluence / Wiki / Notion / SharePoint**                       | 內部知識庫 / 文件系統 | 存放架構設計、維運手冊、Runbook、FAQ。                    | Runbook Agent 透過 MCP 工具搜尋關鍵字、標題、標籤，找出與目前 incident 相關的文件並給出摘要。                                              |
| **ITSM / Ticket 系統（ServiceNow / Jira Service Management / 自家系統）** | 事件 & 服務管理    | 記錄 incident、change、problem、request 等。       | Runbook Agent 透過 MCP 查找歷史 incident（例如相同 service、相同 error pattern），並產生相似案例建議；SRE Copilot Agent 亦可開新 ticket。 |
| **Git / Repo（含 README / infra docs）**                             | 原始碼 & 設計文件   | 存放服務程式碼與相關技術文件。                             | Runbook Agent 可透過 MCP 查詢 repo 中的 `docs/`、`README`、`/infra` 等資料夾內容，找與服務直接相關的技術說明。                           |
| **向量資料庫（Vector DB，例如：Pinecone、Weaviate、pgvector…）**               | RAG 知識庫      | 以 embedding 方式儲存技術文件、postmortem、Runbook 段落。 | Runbook Agent 透過 MCP 的 vector search 工具依「錯誤描述 / log pattern」做相似度搜尋，快速找出類似事件與處置方式。                          |

---

## 五、自動化執行 & 基礎設施層

| 技術項目                                                                     | 類型 / 所層級  | 使用功能                           | 在本架構中的目的與說明                                                                                             |
| ------------------------------------------------------------------------ | --------- | ------------------------------ | ------------------------------------------------------------------------------------------------------- |
| **Kubernetes（K8s / OCP / EKS / GKE 等）**                                  | 容器編排平台    | 部署微服務、調度 pod、滾動更新、自動 scaling。  | Execution Agent 透過 MCP 工具操作 K8s（重啟 deployment、調整 replicas 數、標記 node unschedulable 等），實際執行 remediations。 |
| **Service Mesh（Istio / Linkerd 等）**                                      | 服務間通訊管理   | 控制流量路由、timeout、retry、熔斷、金絲雀發布。 | Execution Agent 可以透過 MCP 工具呼叫 Service Mesh API，切流量到備援、進行金絲雀 rollback 等。                                 |
| **CI/CD Pipeline（Jenkins / GitLab CI / Argo CD / Spinnaker 等）**          | 持續交付 / 部署 | 建置、測試、部署服務版本。                  | Execution Agent 可透過 MCP 的 CD 工具觸發 rollback 或 re-deploy；Triage Agent 查 deploy history 理解「事故是否與近期部署相關」。   |
| **Feature Flag 平台（LaunchDarkly / Unleash / 自建）**                         | 行為開關控制    | 控制功能開關，避免直接推 code rollback。    | Execution Agent 透過 MCP 修改 feature flag 狀態，快速降風險（例如關閉某個高風險新功能）。                                          |
| **Config 管理（Consul / Config Server / Parameter Store / Secret Manager）** | 設定與機密管理   | 集中管理系統設定、憑證、密鑰。                | Triage Agent 可查近期 config 變更；Execution Agent 在必要情況下調整設定值（僅限白名單項目）。                                       |

---

## 六、協作 / 人機介面層

| 技術項目                                                  | 類型 / 所層級       | 使用功能                      | 在本架構中的目的與說明                                                                                       |
| ----------------------------------------------------- | -------------- | ------------------------- | ------------------------------------------------------------------------------------------------- |
| **ChatOps 平台（Slack / Microsoft Teams / Mattermost…）** | 協作 / 通訊平台      | 即時對話、通知、Bot 互動。           | SRE Copilot Agent 透過 MCP 的 ChatOps 工具，把事件摘要 & 建議推送給 on-call，並接收人類文字指令（例如「先不要自動修復」、「同意 rollback」）。 |
| **Incident Management 工具（PagerDuty / Opsgenie 等）**    | On-call / 通知管理 | 管理值班輪值、打電話 / 簡訊 / App 推播。 | 可以由 SRE Copilot Agent 透過 MCP 觸發 PagerDuty 事件，確保 P1 事故有人被叫醒。                                       |
| **Dashboard / 報表（Grafana / Kibana / 自建 Console）**     | 視覺化介面          | 展示服務健康狀態、事件列表、歷史趨勢。       | 雖然不是直接由 Agent 操作，但 Triage Agent/Runbook Agent 的分析結果可以寫入某個索引，供這些 dashboard 顯示「AI 分析結論」。            |
***
[<< 上一篇：A2A Agent 職責表](./02_agents.md) | [返回目錄](./README.md) | [下一篇：整合視圖 >>](./04_integrated.md)

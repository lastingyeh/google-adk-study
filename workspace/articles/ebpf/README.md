# eBPF 增強型 AI Agent 安全導入 GKE 雲端平台應用 (eBPF-Enhanced AI Agent Security Platform For GKE)

## **介紹 (Introduction)**
基於 GKE 的次世代 AI Agent 安全防禦體系。彙整了從高層戰略、技術架構、實作藍圖到部署手冊的所有關鍵文件，為企業構建「Kernel 層級可觀測與防禦」平台提供一站式指引。

---

## 📖 摘要 (Abstract)

隨著企業大規模導入 AI Agent 與微服務架構，傳統基於應用層 (Application Layer) 的安全監控已無法有效防禦針對 Runtime 的深層威脅。Agent 的自主性帶來了不可預測的系統呼叫 (Syscalls) 與網絡行為，這要求我們必須將安全邊界下沈至作業系統核心。

本文章主要詳細闡述如何利用 **eBPF (Extended Berkeley Packet Filter)** 技術，結合 **Google Kubernetes Engine (GKE) Dataplane V2**、**Cilium** 與 **Tetragon**，構建一個具備「核心級可觀測性」與「實時阻斷能力」的安全平台。我們將從戰略價值、技術架構到實作部署，提供一套完整的落地指南。

---

## 📂 目錄 (Table of Contents)

主要分為六個章節，涵蓋從概念驗證到工程實作的完整生命週期：

### **Chapter 1: 執行摘要與核心概念**
*   📄 **[01-executive-summary.md](./01-executive-summary.md)**
    *   **5W1H 分析**: 定義專案背景、核心痛點 (Why) 與解決方案 (What)。
    *   **角色與職責**: 釐清 SRE、Security 與開發團隊在 eBPF 平台中的角色。
    *   **核心價值**: 闡述 Kernel 層級防禦相較於傳統 Sidecar 模式的優勢。

### **Chapter 2: 技術架構與運作流程**
*   📄 **[02-technical-architecture.md](./02-technical-architecture.md)**
    *   **系統時序圖**: 解析從 Client Request 到 Agent Response 的完整流量路徑。
    *   **觀測深度**: 詳解 eBPF 在 Ingress (Cilium)、Pod Runtime (Tetragon) 與 Kernel 的介入點。
    *   **數據流向**: 說明 Network Flow Logs 與 Security Events 的收集與分析架構。

### **Chapter 3: 導入策略與評估**
*   📄 **[03-strategic-planning.md](./03-strategic-planning.md)**
    *   **決策流程樹**: 提供企業評估導入 eBPF 的判斷依據（環境需求、Kernel 版本、團隊能力）。
    *   **元件選擇**: 根據「純觀測」或「主動防禦」需求，建議適合的工具組合。

### **Chapter 4: 實施路線圖**
*   📄 **[04-implementation-roadmap.md](./04-implementation-roadmap.md)**
    *   **三階段計畫**: 準備期 (Preparation) → 觀測期 (Observability) → 防禦期 (Enforcement)。
    *   **KPI 與指標**: 定義專案成功的關鍵績效指標（如：Syscall 覆蓋率、攻擊阻斷時間）。
    *   **風險管理**: 識別潛在的 Kernel 相容性與效能風險及應對策略。

### **Chapter 5: 部署實戰手冊**
*   📄 **[05-deployment-handbook.md](./05-deployment-handbook.md)**
    *   **Infrastructure as Code**: GKE (Terraform) 與 Cilium/Tetragon (Helm) 的完整部署代碼。
    *   **Policy 範例**: 實作 `TracingPolicy` 以監控敏感檔案存取 (`/etc/shadow`) 與異常網路連線。

### **Appendix: 內部推廣素材**
*   📄 **[06-presentation-materials.md](./06-presentation-materials.md)**
    *   **Pitch Deck 大綱**: 用於向管理層或技術團隊推廣 eBPF 概念的簡報架構。
    *   **關鍵溝通點**: 協助建立「安全下沈至 Kernel」的團隊共識。

---

## 🏗 架構藍圖 (Architecture Blueprints)

### 1. eBPF AI Agent Security Platform Overview
![eBPF Security Architecture](./assets/archi-blueprint-ai-agent-driven.png)
---
### 架構圖說明 (Architecture Explanation)

1️⃣ Layer 1｜Kernel & eBPF 感知層

| 架構元件                    | GKE / K8s 對應元件                             | 建議做法                                                         |
| --------------------------- | ---------------------------------------------- | ---------------------------------------------------------------- |
| Linux Kernel                | GKE Node（COS/Ubuntu）                         | 優先使用 Google 建議的 Node OS；確保可支援 eBPF                  |
| eBPF Layer                  | **Cilium** / **Tetragon**（以 DaemonSet 部署） | 每個 node 一個 agent，負責抓 syscall / network / security events |
| Syscall / Network / IO 事件 | Tetragon Policies / Cilium Observability       | 用 policy 控制收集範圍，避免全量造成成本與噪音                   |

---

2️⃣ Layer 2｜Observability 資料管線層（Logs / Traces / Metrics）

| 資料類型            | 架構元件             | GKE 對應元件                                                                  | 建議做法                                                                |
| ------------------- | -------------------- | ----------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| Logs                | Loki / ELK           | **Cloud Logging**（可替代）或自建 Loki/ELK                                    | 若走 GCP 原生：直接導 Cloud Logging；若走自管：用 Fluent Bit / Promtail |
| Traces              | OpenTelemetry        | **OpenTelemetry Collector**（Deployment/DaemonSet）＋ **Cloud Trace**（可選） | 以 OTEL 統一收集，再輸出到 Cloud Trace / Jaeger / Tempo                 |
| Metrics             | Prometheus           | **Managed Service for Prometheus**（GMP）或自建 Prometheus                    | 推薦 GMP（省維運），搭配 Alertmanager                                   |
| Observability Stack | Processing & Storage | **Cloud Monitoring + Cloud Logging + Cloud Trace** 或 Grafana Stack           | 依治理需求決定「全 GCP 原生」或「可移植」方案                           |

---

3️⃣ Layer 3｜AI Agent 應用層（Agent Runtime / A2A / MCP）

| 架構元件                               | GKE 對應元件                                          | 建議做法                                      |
| -------------------------------------- | ----------------------------------------------------- | --------------------------------------------- |
| Chat UI / API Gateway（Entry Point）   | **API Gateway** 或 **Cloud Load Balancing + Ingress** | 對外入口統一控管、加上 WAF / rate limit       |
| Planner / Executor / RAG / Tool Agents | **Deployments**（多個微服務）                         | 每個 Agent 一個 Deployment；用 HPA 做彈性伸縮 |
| A2A Protocol（Agent 溝通）             | **K8s Service + gRPC/HTTP**                           | 服務內通訊走 ClusterIP；必要時加 mTLS         |
| MCP Tools（工具呼叫）                  | Tool Server Pod + RBAC + Workload Identity            | 工具要做權限分層：只給必要的 K8s / GCP 權限   |
| 任務佇列 / 工作流（可選）              | Pub/Sub / Kafka / Cloud Tasks / Workflows             | 若需要可靠編排：引入 Pub/Sub 或 Workflow      |

---

⚠️ Layer 3.5｜RAG / Knowledge（資料與索引層，建議新增到架構圖上）

| 架構需求        | GKE / GCP 常見選擇                                           | 建議做法                                               |
| --------------- | ------------------------------------------------------------ | ------------------------------------------------------ |
| 文件/知識庫儲存 | **Cloud Storage** / Filestore                                | 文件、log 摘要、runbook 放 GCS                         |
| 向量資料庫      | **Vertex AI Vector Search** / AlloyDB pgvector / 自建 Milvus | 若要 GCP 託管優先：Vertex；要可控可攜：pgvector/Milvus |
| 內容索引 / ETL  | Cloud Run Jobs / Dataflow / GKE CronJob                      | 批次索引用 CronJob 或 Cloud Run Jobs                   |

---

4️⃣ Layer 4｜AI Governance & Optimization（SRE / Security / FinOps）

| Governance Agent | GKE / GCP 對應元件                                         | 輸入資料         | 主要輸出                              |
| ---------------- | ---------------------------------------------------------- | ---------------- | ------------------------------------- |
| SRE Copilot      | 服務（Deployment）+ Cloud Monitoring Alerts                | Metrics / Traces | SLO、告警、修復建議、auto-remediation |
| Security Agent   | Tetragon + Cloud Logging + Security Command Center（可選） | Syscall/Logs     | 異常偵測、風險事件、告警與封鎖建議    |
| FinOps Agent     | Cloud Billing Export + Metrics                             | 資源用量 / 成本  | 省錢建議、rightsizing、token 成本治理 |
| Knowledge Agent  | RAG Pipeline + Vector DB                                   | Logs/Traces 摘要 | 事件回顧、Runbook 生成、知識沉澱      |

---

5️⃣ Layer 5｜Feedback Loop（閉環）

| 閉環步驟       | GKE / GCP 元件                   | 實作提示                                       |
| -------------- | -------------------------------- | ---------------------------------------------- |
| 行為收集       | Cilium/Tetragon + OTEL + GMP     | 先定義「收什麼」避免噪音                       |
| 分析與決策     | Governance Agents（Deployments） | 用 policy/規則引擎或 prompt guardrail 控制輸出 |
| 回寫知識       | GCS + Vector DB                  | 事件摘要、根因、處置步驟結構化                 |
| 影響下一次推理 | RAG Agent + Planner              | 讓 Planner 吃「過去案例」做更快拆解            |

---

### 總覽

| 分層     | 圖上的概念                | GKE/GCP 最常見對應                         |
| -------- | ------------------------- | ------------------------------------------ |
| 感知層   | eBPF                      | Cilium / Tetragon（DaemonSet）             |
| 資料層   | Logs/Metrics/Traces       | Cloud Logging / GMP / OTEL(+Cloud Trace)   |
| Agent 層 | Planner/Executor/RAG/Tool | Deployments + Services + Workload Identity |
| 治理層   | SRE/Sec/FinOps            | Monitoring/Logging + 專用 Agents           |
| 閉環     | Feedback Loop             | GCS + Vector DB + RAG                      |
---

### 2. Scalable AI Agent Security with GKE Platform
![eBPF Security Components](./assets/archi-scalable-ai-agent-gke.png)

---

### 架構圖說明 (Architecture Explanation)

---

1️⃣ Request Ingress & Edge Security（請求入口與邊界防護層）

| 架構面向 | GCP 元件                     | 主要職責             | 設計重點             |
| -------- | ---------------------------- | -------------------- | -------------------- |
| DNS 入口 | Cloud DNS                    | 將使用者請求導向 GCP | 高可用、全球解析     |
| 流量入口 | Cloud Load Balancing (HTTPS) | L7 流量分流與 HA     | TLS 終結、全球負載   |
| Web 防護 | Cloud Armor                  | WAF / DDoS 防護      | 第一層資安防線       |
| API 管理 | API Gateway / Apigee（選用） | API 存取控管、配額   | 非必要不過度複雜     |
| 叢集入口 | GKE Ingress / Gateway        | 將流量導入 GKE       | 建議使用 Gateway API |

👉 **這一層的本質**：

> 把「不可信的 Internet 流量」轉成「可控的內部請求」

---

2️⃣ GKE Cluster（AI Agent Core 核心）

> 2-1｜AI Agent Application Layer（Agent 應用層）

| Agent 元件     | 功能定位       | 說明                  |
| -------------- | -------------- | --------------------- |
| Chat UI / API  | 使用者互動入口 | 提供對話 / 任務請求   |
| Planner Agent  | 任務拆解       | 將需求轉為可執行步驟  |
| Executor Agent | 任務執行       | 編排並執行 Agent 行為 |
| RAG Agent      | 知識檢索       | 查詢文件、事件、紀錄  |
| Tool Agent     | 工具操作       | 呼叫外部系統 / API    |

👉 **關鍵設計原則**：

* 一個 Agent = 一個 Deployment
* 可水平擴展（HPA）

---

> 2-2｜Agent Framework & Protocol Layer（Agent 框架層）

| 元件          | 技術         | 職責                    |
| ------------- | ------------ | ----------------------- |
| Agent Runtime | Google ADK   | Agent 生命週期管理      |
| Agent 通訊    | A2A Protocol | Agent-to-Agent 協作     |
| 工具調用      | MCP          | 控制 Agent 使用外部工具 |

👉 **這一層讓 AI「會合作、會做事」**

---

> 2-3｜Platform & Governance Agents（平台治理 Agent）

| Governance Agent      | 分析資料              | 治理目標     |
| --------------------- | --------------------- | ------------ |
| Monitoring Agent      | Metrics               | 系統健康狀態 |
| SRE Copilot Agent     | Metrics / Traces      | 穩定性、SLO  |
| Security Agent        | Logs / Runtime Events | 行為型資安   |
| FinOps Agent          | Metrics / Billing     | 成本最佳化   |
| Knowledge / RAG Agent | Logs / Traces         | 知識沉澱     |

---

> 2-4｜Optional eBPF Runtime Layer（深度系統感知）

| 元件             | 角色             | 價值                  |
| ---------------- | ---------------- | --------------------- |
| GKE Dataplane v2 | eBPF 基礎        | 提供 kernel 可觀測性  |
| Cilium           | Networking       | L7 Network Visibility |
| Tetragon         | Runtime Security | Syscall / 行為偵測    |

👉 **這一層是「看見真實行為」的能力來源**

---

3️⃣ Backend AI & Data Services（後端 AI 與資料層）

> 3-1｜AI / 模型服務

| 類型     | GCP 服務           | 用途            |
| -------- | ------------------ | --------------- |
| 基礎模型 | Vertex AI (Gemini) | LLM / Embedding |
| 推論管理 | Vertex AI Endpoint | 模型治理        |

---

> 3-2｜RAG / 向量資料庫

| 資料類型     | 服務                           | 說明           |
| ------------ | ------------------------------ | -------------- |
| 非結構化資料 | Cloud Storage                  | 文件、log 摘要 |
| 向量搜尋     | Vertex AI Vector Search        | 託管 RAG       |
| 向量資料庫   | AlloyDB / Cloud SQL (pgvector) | 可控型 RAG     |

---

> 3-3｜核心資料服務

| 服務                | 功能           |
| ------------------- | -------------- |
| BigQuery            | 分析、歷史資料 |
| Memorystore (Redis) | 快取 / Session |
| Pub/Sub             | 非同步事件     |
| Cloud Tasks         | 背景任務       |

---

4️⃣ Observability & Governance（集中可觀測與治理）

| 類型      | GCP 服務                      | 功能              |
| --------- | ----------------------------- | ----------------- |
| Logs      | Cloud Logging                 | 行為紀錄          |
| Metrics   | Cloud Monitoring (Prometheus) | 效能 / SLO        |
| Traces    | Cloud Trace (OTel)            | Request 鏈路      |
| Profiling | Cloud Profiler                | CPU / Memory 分析 |

👉 **這一層是所有 Governance Agent 的「資料來源」**

---

5️⃣ Multi-Layered Security Framework（多層資安架構）

> 5-1｜供應鏈安全（Supply Chain）

| 項目       | 服務                 | 說明           |
| ---------- | -------------------- | -------------- |
| Image Scan | Artifact Analysis    | 掃描惡意程式   |
| Image 信任 | Binary Authorization | 僅允許可信映像 |

---

> 5-2｜執行期安全（Runtime）

| 項目     | 服務                  | 功能         |
| -------- | --------------------- | ------------ |
| 政策控管 | GKE Policy Controller | 強制設定     |
| 機密管理 | Secret Manager        | 憑證保護     |
| 稽核     | Cloud Audit Logs      | 不可竄改紀錄 |

---

6️⃣ Secure Egress（安全對外連線）

| 元件                    | 功能              |
| ----------------------- | ----------------- |
| Cloud NAT               | 控制對外流量      |
| Private Service Connect | 私有存取 GCP 服務 |

---

### 總覽

| 分層           | 核心價值    |
| -------------- | ----------- |
| Ingress        | 安全接入    |
| GKE Agent Core | AI 任務執行 |
| Data & AI      | 模型與知識  |
| Observability  | 事實資料    |
| Governance     | 智能治理    |
| Security       | 全面防護    |

---

## 📚 參考文獻 (References)

*   **基礎概念 (Concepts)**
    *   [Wikipedia: eBPF](https://en.wikipedia.org/wiki/EBPF)
    *   [eBPF.io: Applications & Use Cases](https://ebpf.io/zh-hant/applications/)
    *   [Wikipedia: Cilium](https://en.wikipedia.org/wiki/Cilium_%28computing%29)

*   **Google Cloud & GKE**
    *   [Google Cloud Blog: Bringing eBPF and Cilium to GKE](https://cloud.google.com/blog/products/containers-kubernetes/bringing-ebpf-and-cilium-to-google-kubernetes-engine)
    *   [GKE Documentation: Dataplane V2 Networking](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/dataplane-v2)
    *   [GKE Documentation: Dataplane V2 Observability](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/about-dpv2-observability)
    *   [Google Cloud Blog: Using Hubble for GKE Observability](https://cloud.google.com/blog/products/containers-kubernetes/using-hubble-for-gke-dataplane-v2-observability)

*   **Tetragon & Security**
    *   [Tetragon: Security Observability & Runtime Enforcement](https://tetragon.io/)
    *   [Tetragon Docs: Kubernetes Install Guide](https://tetragon.io/docs/getting-started/install-k8s/)
    *   [Is It Observable: Master Kubernetes Security with Tetragon](https://isitobservable.io/observability/kubernetes/master-kubernetes-security-with-tetragon)
    *   [Medium: Cilium Tetragon - Next-Gen Runtime Security](https://medium.com/@nonickedgr/cilium-tetragon-next-generation-runtime-security-for-kubernetes-41cfee727503)

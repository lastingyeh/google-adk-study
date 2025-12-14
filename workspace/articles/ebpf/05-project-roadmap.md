# 📘 平台設計計劃書

## **GKE eBPF AI Agent Security 平台**

---

## 1️⃣ **專案背景與動機**

### 🔹 雲原生架構複雜度提升

AI Agents 與微服務架構在 GKE 上大量採用，帶來工作負載暴增、跨 Pod 通訊頻繁與高敏感數據處理。傳統的安全觀測工具（如 sidecar/agent）受到可見性侷限與效能影響。

而 **eBPF（Extended Berkeley Packet Filter）** 作為 Linux 核心技術，能安全地在內核中執行程式，捕捉系統與網路行為，無需修改應用程式或側車代理，大幅降低額外負載並提升可觀測性與安全防護深度。 ([Wikipedia][1])

---

## 2️⃣ **目標與價值（Why）**

### 🔸 **核心目標**

建立一個可在 GKE 上運行、具備以下能力的 **eBPF AI Agent Security 平台**：

✔ **實時觀測與安全事件捕捉**
✔ **跨 Agent 行為分析與稽核**
✔ **內核層級策略阻斷與執行時防禦**
✔ **低效能負載、安全可控**

---

### 🔸 **核心價值指標**

| 能力領域  | 具體價值                        |
| ----- | --------------------------- |
| 可觀測性  | 深層度網路/系統行為透視                |
| 安全防禦  | 運行時阻止惡意行為                   |
| 效能    | 輕量且無需修改應用程式                 |
| 可擴展性  | 適用各種 Kubernetes 工作負載        |
| 稽核與治理 | 可導出事件至 SIEM / Cloud Logging |

---

## 3️⃣ **概念架構（綜覽圖）**

平台主要由以下模組組成：

```
Client → Ingress (LB) → GKE Pod (ADK + AI Agents)
                   ↘ eBPF Net (Cilium) → Tetragon (Security)
Logging & Monitoring ← Cloud Logging
```

---

## 4️⃣ **平台設計細節（深入說明 / What）**

---

### 🔹 4.1 eBPF 核心技術定位

**eBPF 核心程序運行在 Linux Kernel 中**，可 attaches kernel hook points，進行網路、系統呼叫追蹤與安全策略 enforcement，且無需變更應用程式。 ([Wikipedia][1])

---

### 🔹 4.2 GKE Networking & eBPF 支援

GKE 新版 dataplane V2 支援內建 eBPF datapath，相比傳統 iptables 能更高效且 granular 執行網路 policies、流量觀測與 routing。 ([Google Cloud Documentation][2])

---

### 🔹 4.3 Cilium + Hubble（網路觀測）

Cilium 是基於 eBPF 的 CNI，用於實現 Kubernetes Pod 的高效能網路與可觀測性。
其 observability 組件 Hubble 提供 service map、flow logs 與 metrics，幫助 SRE/DevOps 追蹤 Pod 間通訊與異常網路行為。 ([CSDN Blog][3])

---

### 🔹 4.4 Tetragon（運行時 Security）

Tetragon 是 eBPF-based Kubernetes-aware security observability & runtime enforcement 工具，可檢測：

* Process execution events
* SysCall activity
* File & I/O activity
* Privilege escalation
  並進行 policy 阻斷。 ([Tetragon][4])

---

## 5️⃣ **部署規劃（How / When / Where）**

---

### 🟢 **階段 0 — 準備與研究**

| 目標         | 內容                          |
| ---------- | --------------------------- |
| 技術試驗       | 評估 GKE 支援 eBPF Dataplane V2 |
| 需求整理       | Value points/觀測深度/安全需求      |
| Kernel 兼容性 | Workspace nodes 可執行 eBPF    |

📌 建議在非正式環境先測試 eBPF datapath 與安全工具行為。

---

### 🟡 **階段 1 — 基礎觀測能力**

| 目標         | 內容                 |
| ---------- | ------------------ |
| 安裝 Cilium  | 取代 default CNI     |
| 啟用 Hubble  | 收集流量觀測             |
| 導出 Logging | 導事件至 Cloud Logging |

📌 此階段重點是建立 **可觀測性與網路安全基礎**。

---

### 🔴 **階段 2 — 安全執行階段**

| 目標          | 內容                                           |
| ----------- | -------------------------------------------- |
| 安裝 Tetragon | 導入 Kernel-level security                     |
| 定義 Policy   | Syscalls / file access / network enforcement |
| SIEM 整合     | 導至 Cloud Logging/BigQuery                    |

📌 此階段是 **真正把 eBPF 用於防禦**。

---

## 6️⃣ **策略規範與治理**

---

### 📌 **Policy 類型範例**

| 類別   | 示例策略                    |
| ---- | ----------------------- |
| 系統呼叫 | 阻止未授權 execve            |
| 檔案存取 | 監控敏感文件修改                |
| 進程行為 | 阻止 privilege escalation |

📌 這些策略可透過 Kubernetes CRD 或 OPA 配合 Tetragon 進行管理。

---

## 7️⃣ **整體流程時序與執行（How）**

📌 在 Client 發出請求 → GKE LoadBalancer → eBPF Datapath → Cilium Hubble 觀測 → AI Agent 服務 → Tetragon 安全事件監控 → Logging / SIEM。
此過程在 **Kernel 層即可進行安全與觀測**，遠比傳統 User Space tools 更精準。 ([Google Cloud Documentation][2])

---

## 8️⃣ **整合 Cloud 服務與 DevOps / SecOps**

---

### 🧠 **Logging/Alerting**

建議將事件與 metrics 導入：

✔ **Cloud Logging**（標準化存儲與查詢）
✔ **BigQuery**（長期分析）
✔ **Alerting**（SIEM / AI Security Copilot）

---

### 🧠 **Policy Governance**

可結合：

✔ **OPA/Gatekeeper + GitOps**（Policy as Code）
✔ **ArgoCD/Flux**（Policy Lifecycle Management）

---

## 9️⃣ **評估與成功指標（KPIs）**

---

### 📊 指標範例

| 領域   | KPI                                |
| ---- | ---------------------------------- |
| 觀測性  | 網路 flow 完整度、syscall 追蹤 coverage    |
| 安全防護 | 攻擊偵測率、偽陽性比率                        |
| 反應速度 | 事件檢出到警報時間                          |
| 資安可視 | Policy 命中紀錄、Security dashboard 活躍率 |

---

## 10️⃣ **風險與應對**

---

### ⚠ 風險

✔ Kernel 版本不支援特定 eBPF hook
✔ 大量事件需處理性能與存儲成本
✔ 安全策略誤阻正常行為

---

### 🛠 應對策略

✔ 逐步滾動部署與版本控管
✔ 先在 Stage Mode 試行策略
✔ 設定事件分級與回饋流程

---

## 11️⃣ **後續演進方向**

---

### 🚀 進階能力

📌 AI 驅動 Security Analytic
📌 自動化 Policy 推薦
📌 多集群聯邦觀測

---

## 12️⃣ **結語**

eBPF 在 GKE 上不只是「可觀測」，更是「安全防禦的下一代基礎技術」，能填補傳統工具無法深入 kernel 行為的缺口，使 AI Agent 平台具備更全面、即時且性能友好的安全能力。 ([SUSE][5])

---

## 參考資料

[1]: https://en.wikipedia.org/wiki/EBPF?utm_source=chatgpt.com "EBPF"
[2]: https://docs.cloud.google.com/kubernetes-engine/docs/best-practices/networking?utm_source=chatgpt.com "Best practices for GKE networking"
[3]: https://blog.csdn.net/weixin_39145568/article/details/147960141?utm_source=chatgpt.com "eBPF 开源项目Cilium 深入分析原创"
[4]: https://tetragon.io/?utm_source=chatgpt.com "Tetragon - eBPF-based Security Observability and Runtime ..."
[5]: https://www.suse.com/c/ebpf-kubernetes/?utm_source=chatgpt.com "Using eBPF in Kubernetes for Improved Observability and ..."

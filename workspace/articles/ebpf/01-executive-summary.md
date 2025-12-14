# 📌 5W1H 全面設計：eBPF AI Agent Security 平台（基於 Google ADK / GKE）

## 📖 摘要 (Abstract)
本文件為專案的執行摘要（Executive Summary），旨在以非技術語言向決策者與利害關係人說明 eBPF 安全平台的導入價值。內容涵蓋專案背景（Why）、解決方案定義（What）、角色職責（Who）、時程規劃（When）、部署位置（Where）以及實作方法（How），提供高層次的戰略視角。

---

## **WHY — 為什麼要做？（背景與痛點）**

在 AI Agent 平台（如 Google ADK + A2A）中：

* Agent 對內 **程式行為與系統調用不可見**
* 傳統安全觀察（log / sidecar）容易漏失 syscall、文件系統使用、進程行為
* 容器逃逸、惡意執行、API 濫用、網路攻擊等威脅仍難即時偵測
* 更高安全與合規需求（稽核 / 政策證據 / 實時阻斷）

👉 **eBPF 提供一個安全、低開銷、核心層級的可觀測與執行時防禦引擎**
它可以在核心層捕捉 Syscall、Network Packet、Process Event、File I/O 等行為，而不需要修改應用程式程式碼或容器映像。([Wikipedia](https://en.wikipedia.org/wiki/EBPF?utm_source=chatgpt.com))

---

## **WHAT — 什麼是 eBPF Security 平台？**

一個在 **GKE 上運行、整合 eBPF 的 AI Agent Runtime 安全平台**，成分包括：

### 🔹 eBPF 核心能力

* **Syscall / 系統行為監控**
* **網路行為與封包流量可見性**
* **執行時政策阻斷 / 行為防禦**
* **事件稽核與安全警報**

這類能力是 Cilium / Tetragon 這些 eBPF 工具的核心特性。([Tetragon](https://tetragon.io/?utm_source=chatgpt.com))

### 🔹 主要安全防禦能力

| 能力 | 說明 |
| :--- | :--- |
| 進程 & 執行監控 | 追蹤容器內部系統呼叫與流程 |
| 文件存取監控 | 防止非法存取敏感文件 |
| 網路行為策略 | 強制 Pod-to-Pod / Egress 安全策略 |
| 可執行檔與行為阻斷 | 實時執行策略阻擋行為 |

👉 這些都可以透過 eBPF 直接在核心層觀察與防止，而不是 Application 層。([Tetragon](https://tetragon.io/?utm_source=chatgpt.com))

---

## **WHO — 誰來用與誰來建？（角色與責任）**

### 🎯 使用者角色

| 角色 | 職責 |
| :--- | :--- |
| 平台安全團隊 | 設計 & 管理安全政策 |
| SRE / DevOps | 部署與監控 eBPF 觀測與安全事件 |
| 開發者 | 透過 ADK Agent 與 Observability 儀表板分析問題 |
| 合規 / Audit Team | 查看稽核日誌、事件報告 |

---

## **WHEN — 什麼時候開始建置？（階段式路線）**

可分為三個階段：

### 🟢 Stage 0 — 準備與規劃

✔ 確認 GKE 架構
✔ 確定安全監控目標
✔ 決定使用 eBPF 工具（例如 Cilium / Tetragon）

### 🟡 Stage 1 — 基礎可觀測

✔ 啟用 eBPF CNI（GKE Dataplane V2 / Cilium）
✔ 收集網路與系統指標
✔ 導向 Cloud Logging / Monitoring

### 🔴 Stage 2 — 安全策略與防禦

✔ 定義安全策略（Syscall、Exec、Network Policy）
✔ 部署 eBPF Runtime Enforcement
✔ 整合告警與策略阻斷
✔ 加入 Policy 規則與 Governance

---

## **WHERE — 部署與整合位置**

### ▶ 平台層級（GKE Node + Cluster）

* eBPF 程式注入到 Linux Kernel
* GKE Dataplane V2 或 **Cilium** 運行於每個 Node 上收集觀測資料
* **Tetragon** 進一步提供運行時安全執行與策略 enforcement（可視情況選用）([Google Cloud](https://cloud.google.com/blog/products/containers-kubernetes/bringing-ebpf-and-cilium-to-google-kubernetes-engine?utm_source=chatgpt.com))

### ▶ 控制層 / 平台服務

* **Cloud Logging / Monitoring** 用於統一存儲與搜尋安全事件
* **Vertex AI / BigQuery** 可用於更深度關聯分析

---

## **HOW — 如何從 0 到 1 實作（步驟與建議）**

### 🛠 Step 0 — 技術準備

**先學習 eBPF 與相關工具**

* eBPF 本質：在 Linux 核心中執行安全 sandboxed 程式，不需重編 Kernel。([Wikipedia](https://en.wikipedia.org/wiki/EBPF?utm_source=chatgpt.com))
* 了解 Cilium 和 Tetragon 在 Kubernetes 中是如何使用 eBPF 提供可觀察與安全功能的。([eBPF](https://ebpf.io/zh-hant/applications/?utm_source=chatgpt.com))

---

### 🛠 Step 1 — 啟用 eBPF 支援於 GKE

#### 1) 啟用 GKE Dataplane V2

```bash
gcloud beta container clusters create <cluster-name> \
  --enable-dataplane-v2 \
  --enable-ip-alias --release-channel rapid
```

這樣 GKE 就會在 Node 上啟用 eBPF datapath，提升網路可觀察與效率。([Google Cloud](https://cloud.google.com/blog/products/containers-kubernetes/bringing-ebpf-and-cilium-to-google-kubernetes-engine?utm_source=chatgpt.com))

---

### 🛠 Step 2 — 部署 eBPF Cilium & Hubble（網路觀察 + Policy）

1. 安裝 Cilium Operator
2. 啟用網路策略與 L3/L4/L7 Policy
3. Collect Flow logs → 導入 Cloud Logging
4. 整合 Prometheus 指標到 Cloud Monitoring

Cilium 具備 Identity-Aware Policies、Flow Logs、透明加密等安全功能。([Wikipedia](https://en.wikipedia.org/wiki/Cilium_%28computing%29?utm_source=chatgpt.com))

---

### 🛠 Step 3 — 加入 **Runtime Security Enforcement**

這是 **核心向安全運行邁進的重要一步**：

🔹 使用工具如 **Tetragon**

* 能監控 Pod 內執行、Syscall、Network 行為
* 可執行策略（例如阻止可疑執行）
* Kubernetes aware（Policy via CRD / OPA）

例如：

* 監控未授權進程執行
* 防止異常網路連線
* File integrity 事件

這些都是 Tetragon 的典型能力。([Tetragon](https://tetragon.io/?utm_source=chatgpt.com))

---

### 🛠 Step 4 — 安全 Policy 定義與 Enforcement Loop

建立典型策略，例如：

| 類型 | 範例 |
| :--- | :--- |
| 進程控制 | "禁止 Pod 執行 /tmp 以外的可執行檔" |
| Syscall Filtering | "禁止 fork/execve 未授權進程" |
| File Integrity | "監控 /etc/shadow 修改" |
| Egress Controls | "阻止 Pod 連出未經授權端點" |

這些政策可以用 Tetragon、OPA、CRD 方式定義，eBPF 則實際在 Kernel 層監控與 enforce。([Tetragon](https://tetragon.io/?utm_source=chatgpt.com))

---

### 🛠 Step 5 — 集中稽核與回饋

🔹 收集所有安全事件到 **Cloud Logging / BigQuery**

🔹 用 **AI Agent + RAG** 建立 Security Copilot

* 透過已標註事件回答「哪個 Agent 嘗試非法行為？」
* 生成報告幫助安全團隊決策

---

## 🟡 Nice-to-have（進階整合）

🔸 **攻擊模擬與安全回測**

* 定期測試 eBPF Policy
* 使用 CI 流程觸發策略測試

🔸 **AI Agent 自動策略生成**

* 將觀察到的行為 feeding RAG/LLM
* 自動建議安全政策

---

## 🧠 總結

這份方案實現了一個：

👉 **可量產、低 overhead、可觀測與可防禦的 Runtime Security 平台**
搭配 Google ADK + GKE + eBPF 工具（Cilium/Tetragon）
能在 **Kernel 核心階段捕捉、分析、阻斷安全相關行為**。([Google Cloud](https://cloud.google.com/blog/products/containers-kubernetes/bringing-ebpf-and-cilium-to-google-kubernetes-engine?utm_source=chatgpt.com))

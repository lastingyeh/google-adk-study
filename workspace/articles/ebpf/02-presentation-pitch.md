# 🧩 Slide 1｜為什麼 AI Agent Security 需要「重新想一次」

### 🎯 本頁目的

打破新人的既有安全認知，建立「傳統方法不夠」的共識。

### 📌 重點內容

* AI Agent ≠ 傳統 API / Microservice
* Agent 會：

  * 執行系統指令
  * 開檔案 / socket
  * 呼叫外部工具
* **多數風險發生在 Runtime，不在程式碼**

### 💬 互動提問

> 「如果 Agent 偷偷對外連線，你現在會怎麼知道？」

### 🧠 新人記住一句話

> **AI Agent 的風險，不只在 Prompt，而是在系統行為**

---

# 🧩 Slide 2｜GKE + AI Agent 的真實攻擊面在哪？

### 🎯 本頁目的

讓新人理解「安全邊界不在 LB / API，而在 Pod 與 Node」。

### 📌 重點內容

* Client → LB → GKE → Pod → Agent → Tool
* 真正危險的地方：

  * Pod Runtime
  * Tool Execution
  * External Egress
* Application Log 的可視範圍有限

### 💬 互動提問

> 「哪一段最容易被忽略，但風險最大？」

### 🧠 新人記住一句話

> **看得到 API，不代表看得到系統**

---

# 🧩 Slide 3｜eBPF 是什麼？（給工程師的版本）

### 🎯 本頁目的

建立 eBPF 的正確定位，不陷入名詞恐懼。

### 📌 重點內容

* eBPF 是：

  * 跑在 Linux Kernel 的安全小程式
  * 有 verifier，不會亂來
* 可以看到：

  * Syscall
  * Network
  * File / Process
* 不用改程式、不用 sidecar

### 💬 互動提問

> 「為什麼不用直接寫 Kernel module？」

### 🧠 新人記住一句話

> **eBPF 是 Kernel 的觀察窗，不是駭客工具**

---

# 🧩 Slide 4｜eBPF 在 GKE 裡「住在哪一層？」

### 🎯 本頁目的

釐清 Pod / Node / Kernel 的層次關係。

### 📌 重點內容

* eBPF 不在 Pod
* eBPF 在 Node 的 Linux Kernel
* Pod 刪掉，eBPF 還在
* 適合短生命週期與大量 Agent

### 💬 互動提問

> 「Pod scale 到 100 個，eBPF 會怎樣？」

### 🧠 新人記住一句話

> **Pod 來來去去，eBPF 一直在**

---

# 🧩 Slide 5｜Cilium 與 Tetragon 各自負責什麼？

### 🎯 本頁目的

避免工具混用、定位錯誤。

### 📌 重點內容（角色化說明）

* **Cilium**：

  * eBPF 網路 dataplane
  * 看「誰跟誰說話」
* **Hubble**：

  * 網路 flow 的時間軸
* **Tetragon**：

  * 看「系統做了什麼」
  * 可阻斷危險行為

### 💬 互動提問

> 「execve 是誰看得到？」

### 🧠 新人記住一句話

> **Cilium 看流量，Tetragon 看行為**

---

# 🧩 Slide 6｜Client → Response 的完整安全時序

### 🎯 本頁目的

讓新人「走過一次完整請求流程」。

### 📌 重點內容

1. Client 發送請求
2. LB / Ingress
3. eBPF dataplane 觀察流量
4. Pod / Agent 執行
5. Tool 呼叫 → syscall
6. Tetragon 判斷是否阻斷
7. Response 回 Client

### 💬 互動提問

> 「哪幾步是 Application log 看不到的？」

### 🧠 新人記住一句話

> **真正的安全證據，在 Kernel 層**

---

# 🧩 Slide 7｜從「只看」到「能擋」的落地策略

### 🎯 本頁目的

教新人「不要一次做太重」。

### 📌 重點內容

* 第一階段：

  * Cilium + Logging
  * 不開 enforcement
* 第二階段：

  * Tetragon
  * Policy as Code
* 第三階段：

  * GitOps / SIEM / AI Copilot

### 💬 互動提問

> 「你會在哪一階段開始阻斷？」

### 🧠 新人記住一句話

> **先看清楚，再決定要不要擋**

---

# 🧩 Slide 8｜你身為平台工程師，該記住的三件事

### 🎯 本頁目的

把技術收斂成「角色責任」。

### 📌 重點內容

1. eBPF 是平台能力，不是應用能力
2. AI Agent Security 必須做到 Runtime
3. 安全不是一次完成，是逐步演進

### 💬 互動提問

> 「如果明天有 Agent 出事，你會先查哪一層？」

### 🧠 最終收斂金句

> **eBPF 讓平台第一次真正看見系統在幹嘛**

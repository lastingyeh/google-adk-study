# Policy-as-Code Agent 學習路徑與完整教學大綱

本文件旨在將現有的專案文檔結構化，整理為一套由淺入深的學習教程。透過本大綱，開發者可以按部就班地掌握 Policy-as-Code Agent 的設計理念、實作細節、部署運維等全方位知識。

## 學習路徑規劃

建議的學習順序分為五大階段：

1.  **概念認知階段 (Concept)**：理解專案目標、價值與高階架構。
2.  **環境準備階段 (Setup)**：配置開發環境、依賴管理與容器化基礎。
3.  **核心開發階段 (Core Development)**：深入程式碼實作、ADK 框架應用與記憶體設計。
4.  **品質保證階段 (Quality Assurance)**：程式碼規範、測試與最佳實踐。
5.  **部署運維階段 (Deployment & Ops)**：基礎設施即程式碼 (IaC)、CI/CD 與生產環境部署。

---

## 詳細教學大綱

### 第一階段：專案導論與高階架構

本階段目標是建立對專案的全盤了解，不涉及過多程式碼細節，著重於「為什麼要做」以及「如何運作」。

*   **1.1 專案總覽與設計理念**
    *   **核心文件**：[`README.md`](README.md)
    *   **學習重點**：
        *   專案的核心價值（消除幻覺、治理民主化）。
        *   Agentic AI 與混合執行模式的概念。
        *   系統架構圖（使用者查詢 -> 記憶體/生成 -> 執行）。
*   **1.2 業務價值與功能詳解**
    *   **核心文件**：[`HIGH_LEVEL_DETAILS.md`](HIGH_LEVEL_DETAILS.md)
    *   **學習重點**：
        *   針對技術人員 (CEs/SAs) 與業務人員 (Sales) 的價值主張。
        *   六大運作流程（搜尋、理解、生成、執行、建議、回饋）。
        *   關鍵技術堆疊（Gemini Flash/Pro 分工、AST 安全檢查）。

### 第二階段：環境建置與基礎工具

本階段目標是讓開發者能夠在本地端成功執行專案，並理解專案的基礎配置。

*   **2.1 快速上手指南**
    *   **核心文件**：[`STARTER_PACK.md`](STARTER_PACK.md)
    *   **學習重點**：
        *   專案目錄結構解析。
        *   必要工具安裝（uv, gcloud, terraform, make）。
        *   使用 `make playground` 進行本地測試。
*   **2.2 Python 專案配置與依賴管理**
    *   **核心文件**：[`PYPROJECT.md`](PYPROJECT.md)
    *   **學習重點**：
        *   理解 `pyproject.toml` 的結構與用途。
        *   依賴分組（核心 vs 開發）。
        *   Setuptools 與套件打包設定。
*   **2.3 容器化基礎**
    *   **核心文件**：[`DOCKER.md`](DOCKER.md)
    *   **學習重點**：
        *   Dockerfile 架構（多階段建置）。
        *   本地建置與執行 Docker 映像檔。
        *   Artifact Registry 基礎操作。

### 第三階段：核心實作與框架深入

本階段是學習曲線最陡峭的部分，將深入程式碼邏輯、框架使用以及獨特的記憶體架構。

*   **3.1 Google ADK 框架速查與應用**
    *   **核心文件**：[`GEMINI.md`](GEMINI.md)
    *   **學習重點**：
        *   Agent 定義與 LlmAgent 設定。
        *   多代理（Multi-agent）協作模式。
        *   工具（Tools）與回呼（Callbacks）機制。
*   **3.2 Agent 核心邏輯與實作流程**
    *   **核心文件**：[`AGENT.md`](AGENT.md)
    *   **學習重點**：
        *   詳細程式碼架構 (`agent.py`, `mcp.py`, `simulation.py`)。
        *   16 步驟實作流程詳解（從初始化到部署）。
        *   核心工具實作（GCS, Dataplex, LLM 工具）。
*   **3.3 底層架構細節**
    *   **核心文件**：[`LOW_LEVEL_DETAILS.md`](LOW_LEVEL_DETAILS.md)
    *   **學習重點**：
        *   記憶體優先（Memory-First）架構的資料流。
        *   GCS 與 Dataplex 工作流的差異。
        *   安全性模擬（Simulation）與 AST 分析實作。
*   **3.4 混合記憶體系統設計**
    *   **核心文件**：[`MEMORY_IMPLEMENTATION.md`](MEMORY_IMPLEMENTATION.md), [`MEMORY_INTEGRATION.md`](MEMORY_INTEGRATION.md)
    *   **學習重點**：
        *   雙層記憶體架構：Agent Engine（對話上下文） vs Firestore（領域知識）。
        *   向量搜尋（Vector Search）的整合與應用。
        *   Firestore Schema 設計與資料流。

### 第四階段：程式碼品質與測試

本階段關注如何維護程式碼的健康度與可維護性。

*   **4.1 程式碼品質控制 (Linting)**
    *   **核心文件**：[`LINT.md`](LINT.md)
    *   **學習重點**：
        *   使用 `ruff` 進行風格檢查與格式化。
        *   使用 `mypy` 進行靜態型別檢查。
        *   使用 `codespell` 檢查拼字錯誤。
*   **4.2 任務與測試追蹤**
    *   **核心文件**：[`TASKS.md`](TASKS.md)
    *   **學習重點**：
        *   了解開發過程中的任務清單與完成狀況。
        *   單元測試與整合測試的執行 (`make test`)。

### 第五階段：部署與自動化運維

最後階段是將開發好的 Agent 部署到生產環境，並建立自動化流程。

*   **5.1 基礎設施即程式碼 (Infrastructure as Code)**
    *   **核心文件**：[`DEPLOY.md`](DEPLOY.md)
    *   **學習重點**：
        *   Terraform 模組結構與環境變數。
        *   多環境部署策略（Dev/Staging/Prod）。
        *   Google Cloud 服務組件（Cloud Run, Cloud SQL, Vertex AI 等）。
*   **5.2 CI/CD 持續整合與部署**
    *   **核心文件**：[`CICD.md`](CICD.md)
    *   **學習重點**：
        *   Cloud Build 觸發器設定。
        *   完整 CI/CD 流程圖（PR Checks -> Staging -> Prod）。
        *   自動化測試與負載測試整合。

### 附錄：其他資源與參考

*   **程式碼說明**
    *   **核心文件**：[`CODE.md`](CODE.md)
    *   **學習重點**：
        *   主要模組與函式說明。
        *   程式碼註解與文件化最佳實踐。
*   **常見問題集 (FAQ)**
    *   **核心文件**：[`FAQ.md`](FAQ.md)
    *   **學習重點**：
        *   常見問題與解決方案彙整。
---

## 總結

1.  **入門**：`README.md` -> `HIGH_LEVEL_DETAILS.md` -> `starter_pack_README.md`
2.  **基礎**：`PYPROJECT.md` -> `DOCKER.md` -> `GEMINI.md`
3.  **核心**：`LOW_LEVEL_DETAILS.md` -> `AGENT.md` -> `MEMORY_IMPLEMENTATION.md`
4.  **進階**：`LINT.md` -> `DEPLOY.md` -> `CICD.md`

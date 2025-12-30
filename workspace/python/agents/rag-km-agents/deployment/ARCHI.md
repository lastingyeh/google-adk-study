# 架構說明 (Architecture Description)

本文件根據 `deployment/terraform` 目錄下的 Terraform 設定檔，詳細說明本專案所使用的 Google Cloud 服務架構與分類。

## 1. 運算服務 (Compute Services)
相關檔案：`service.tf`

*   **Cloud Run**:
    *   主要應用程式託管於 Cloud Run 服務。
    *   配置了自動擴展 (Autoscaling) 與負載平衡。
    *   透過環境變數連接至 Cloud SQL、Discovery Engine 與其他服務。
    *   掛載 Cloud SQL 連線以存取資料庫。

## 2. 資料儲存 (Data Storage)
相關檔案：`service.tf`, `storage.tf`

*   **Cloud SQL (PostgreSQL)**:
    *   使用 PostgreSQL 15 版本。
    *   用於儲存應用程式的對話 Session 資料與其他結構化數據。
    *   啟用 IAM 驗證與每日自動備份。
*   **Cloud Storage (GCS)**:
    *   **Logs Bucket**: 用於儲存應用程式日誌。
    *   **RAG Bucket**: 用於儲存 RAG (Retrieval-Augmented Generation) 流程所需的原始文件與資料。
*   **Secret Manager**:
    *   安全地儲存敏感資訊，例如資料庫密碼 (DB Password)，並供 Cloud Run 應用程式讀取。
*   **Artifact Registry**:
    *   儲存應用程式的 Docker映像檔 (Container Images)。

## 3. 人工智慧與搜尋 (AI & Search)
相關檔案：`storage.tf`, `apis.tf`

*   **Vertex AI Agent Builder (Discovery Engine)**:
    *   **Data Store**: 建立資料儲存庫 (Datastore) 以索引非結構化資料。
    *   **Search Engine**: 建立搜尋引擎應用程式，提供企業級搜尋能力。
*   **Vertex AI**:
    *   啟用相關 API 以支援生成式 AI 模型的使用。

## 4. 身分驗證與安全 (Identity & Security)
相關檔案：`iam.tf`, `wif.tf`, `service_accounts.tf`

*   **IAM (Identity and Access Management)**:
    *   配置多個服務帳戶 (Service Accounts) 以遵循最小權限原則：
        *   **CICD Runner SA**: 用於執行 CI/CD 流程。
        *   **App SA**: 應用程式執行時使用的身分。
        *   **Vertex AI Pipeline SA**: 用於執行資料攝取管道。
    *   設定詳細的 IAM 角色綁定 (Role Bindings) 以授權服務存取資源。
*   **Workload Identity Federation (WIF)**:
    *   建立 Workload Identity Pool 與 Provider。
    *   允許 GitHub Actions 安全地模擬 Google Cloud 服務帳戶，無需管理長期金鑰 (Service Account Keys)。

## 5. 監控與遙測 (Observability & Telemetry)
相關檔案：`telemetry.tf`

*   **Cloud Logging**:
    *   建立專用的 Log Bucket 以儲存 GenAI 相關的遙測數據，並設定長達 10 年的保留期。
    *   配置 Log Sink 將特定日誌 (如 GenAI 操作與使用者回饋) 路由至專用 Bucket。
*   **BigQuery**:
    *   **Telemetry Dataset**: 用於分析遙測數據的資料集。
    *   **External Table**: 透過 BigQuery Connection 直接查詢 GCS 中的 Completions 資料。
    *   **Completions View**: 建立視圖 (View) 以關聯分析 Cloud Logging 中的日誌與 GCS 中的詳細數據。
*   **Cloud Trace**:
    *   啟用分散式追蹤以監控應用程式效能。

## 6. 持續整合與部署 (CI/CD)
相關檔案：`github.tf`, `apis.tf`

*   **GitHub Integration**:
    *   自動配置 GitHub Repository (可選)。
    *   設定 GitHub Actions 所需的 Secrets 與 Variables (如專案 ID、服務帳戶 Email、WIF 設定等)。
    *   建立 Production Environment 以控管部署流程。
*   **APIs**:
    *   自動啟用專案所需的各項 Google Cloud API (如 Cloud Build API, Compute API 等)。

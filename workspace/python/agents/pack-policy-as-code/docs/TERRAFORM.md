# Terraform 從零到一百建置指南

本文件旨在提供一個深入的技術指南，說明如何從零開始建構 `pack-policy-as-code` 的基礎設施。我們將不只是告訴您如何執行指令，而是會帶您瀏覽每個 Terraform 檔案的用途、內容邏輯以及它們如何共同協作，構建出一個企業級的 Google Cloud 架構。

## 1. 架構設計思維

在開始寫程式碼之前，我們先理解這個架構解決了什麼問題：
1.  **環境隔離**：區分 CI/CD (建構)、Staging (測試) 和 Production (生產) 環境。
2.  **自動化**：透過 Terraform 管理基礎設施 (IaC)，確保環境一致性。
3.  **安全性**：最小權限原則 (Least Privilege)，只啟用必要的 API 和授予必要的 IAM 角色。

我們的 Terraform 代碼結構如下：

```
deployment/terraform/
├── providers.tf        # 定義 Provider 與版本
├── variables.tf        # 輸入變數定義
├── locals.tf           # 區域變數與常數
├── apis.tf             # 啟用 Google Cloud API
├── service_accounts.tf # 建立服務帳戶身分
├── iam.tf              # 權限與角色綁定
├── storage.tf          # GCS Bucket 與 Artifact Registry
├── service.tf          # 核心服務 (Cloud Run, SQL, Secrets)
├── github.tf           # GitHub 連接設定
└── build_triggers.tf   # Cloud Build CI/CD 觸發器
```

---

## Phase 1: 基礎配置 (Foundation)

一切從定義「我們是誰」以及「我們需要什麼」開始。

### 1. `providers.tf`: 定義工具與版本
此檔案告訴 Terraform 我們需要哪些插件 (Providers) 來與外部系統互動。
*   **Google Provider**: 用於管理 GCP 資源。特別注意我們定義了 `staging_billing_override` 和 `prod_billing_override`，這是為了確保在操作特定專案資源時，計費與配額能正確歸屬到該專案。
*   **GitHub Provider**: 用於管理 GitHub 儲存庫資源。

### 2. `variables.tf`: 定義輸入變數
這是 Terraform 的介面。我們定義了如 `project_name`、`prod_project_id`、`cicd_runner_project_id` 等變數。這讓同一份代碼可以被不同的使用者重複使用，只需改變變數值 (透過 `terraform.tfvars`)。

### 3. `locals.tf`: 邏輯與常數
我們使用 `locals` 來處理一些資料轉換邏輯，避免在資源定義中重複寫死。
*   **`deploy_project_ids`**: 建立一個 Map `test -> ID` 和 `prod -> ID`，這讓我們後續可以使用 `for_each` 迴圈一次性部署兩個環境。
*   **`cicd_services` & `deploy_project_services`**: 列出需要啟用的 API 列表。

---

## Phase 2: 啟用能力 (Enabling Capabilities)

在 GCP 上建立資源前，必須先啟用對應的 API。

### `apis.tf`
此檔案負責 API 的啟用管理。
*   **CI/CD 專案 API**: 啟用 `cloudbuild`, `artifactregistry` 等建構相關服務。
*   **部署專案 API (Staging/Prod)**: 這是此檔案最精華的部分。我們使用了 `setproduct` 函數：
    ```hcl
    # 邏輯示意：
    # 專案列表 x 服務列表 = 所有需要在各個專案啟用的服務組合
    for pair in setproduct(keys(local.deploy_project_ids), local.deploy_project_services)
    ```
    這段程式碼確保了 Staging 和 Production 兩個專案都啟用了相同的 API 集合 (如 `run`, `sqladmin`, `secretmanager`)，保證了環境的一致性。

---

## Phase 3: 身分與存取 (Identity & Access)

定義「誰」可以做「什麼」。

### 1. `service_accounts.tf`: 建立身分
我們建立了兩種主要的服務帳戶 (Service Accounts)：
*   **`cicd_runner_sa`**: 在 CI/CD 專案中建立。它是流水線的執行者，負責建構映像檔、執行部署。
*   **`app_sa`**: 使用 `for_each` 在 Staging 和 Prod 專案中各建立一個。這是應用程式 (Agent) 運行時的身分。

### 2. `iam.tf`: 授權
這是最複雜也最重要的部分，處理跨專案權限。
*   **CI/CD 權限**:
    *   在 CI/CD 專案本身：賦予 `cloudbuild.builds.builder` 等權限。
    *   **跨專案部署權限**: 這是關鍵。我們賦予 `cicd_runner_sa` 能夠操作 Staging/Prod 專案的權限 (如 `run.developer`)。這樣 CI/CD 流水線才能將服務部署到目標專案。
*   **App 權限**: 賦予 `app_sa` 存取 DB、寫入 Log、讀取 Secret 的權限。
*   **Artifact Registry 讀取權限**: 授予 Staging/Prod 的 Cloud Run Robot 帳戶從 CI/CD 專案拉取映像檔的權限 (`roles/artifactregistry.reader`)。

---

## Phase 4: 資料與儲存 (Data & Storage)

### 1. `storage.tf`: 靜態儲存
*   **Logs Bucket**: 為每個環境建立 GCS Bucket，用於集中儲存應用程式日誌與遙測資料。
*   **Artifact Registry**: 在 CI/CD 專案建立 Docker 映像檔儲存庫 (`repo-artifacts-genai`)。所有建構好的映像檔都存在這裡。

### 2. `service.tf` (Part 1): 資料庫與機密
*   **Cloud SQL**: 建立 PostgreSQL 實例。
    *   使用 `random_password` 產生高強度密碼。
    *   建立資料庫與使用者。
*   **Secret Manager**: 將生成的資料庫密碼存入 Secret Manager。這體現了安全性最佳實踐——**密碼不落地**，應用程式啟動時才從 Secret Manager 讀取。

---

## Phase 5: 觀測與遙測 (Observability & Telemetry)

為了構建企業級的 GenAI 應用，我们需要詳細的日誌與分析能力。

### `telemetry.tf`: BigQuery 與 Logging 整合
此檔案展示了高級的 GCP 觀測架構。
*   **BigQuery Dataset**: 建立資料集用於存放遙測資料。
*   **Log Buckets**: 建立專用的 Logging Bucket (`google_logging_project_bucket_config`)，設定長達 10 年的保留期，專門儲存 GenAI 相關日誌。
*   **Log Sinks**: 設定路由器 (`google_logging_project_sink`)，將特定的 GenAI 推論日誌和使用者回饋日誌導向上述的 Log Bucket。
*   **BigQuery Linked Dataset**: 建立連結 (`google_logging_linked_dataset`)，允許直接從 BigQuery 查詢 Log Bucket 中的資料，無需搬移資料。
*   **外部表 (External Table)**: 建立指向 GCS Bucket 的外部表，用於分析原始的 Completion 資料。
*   **整合視圖 (View)**: 透過 SQL (`completions.sql`) 將 Log 中的 metadata 與 GCS 中的 payload 結合，提供完整的對話分析視圖。

---

## Phase 6: 應用程式 (The Application)

### `service.tf` (Part 2): Cloud Run 服務
這是我們最終要部署的應用程式。
*   **資源定義**: 設定 CPU/Memory 限制。
*   **環境變數注入**: 透過 Terraform 將基礎設施資訊 (如 DB 連線名稱、Bucket 名稱) 注入到容器環境變數中。
*   **Secret 整合**: 設定環境變數 `DB_PASS` 從 Secret Manager 讀取值。
*   **Lifecycle**: 設定 `ignore_changes = [template[0].containers[0].image]`。這很重要，因為初次部署後，CI/CD 流水線會更新映像檔版本。我們不希望 Terraform 下次執行時把版本退回初始狀態。

---

## Phase 7: 自動化流水線 (CI/CD Pipeline)

最後，我們將 Git 操作與基礎設施連接起來。

### 1. `github.tf`: 連接代碼庫
*   **Cloud Build Connection**: 使用 Gen2 Repository 連接方式，建立 GCP 與 GitHub 的安全連結。
*   **GitHub Repository**: (可選) 如果設定 `create_repository = true`，Terraform 甚至可以幫您建立 GitHub Repo。

### 2. `build_triggers.tf`: 定義觸發規則
建立了三個自動化觸發器：
1.  **PR Checks**: 當有人發 PR 到 `main` 分支時觸發。執行測試，確保程式碼品質。
2.  **CD Pipeline**: 當程式碼合併進 `main` 分支時觸發。自動建構並部署到 **Staging** 環境。
3.  **Deploy to Prod**: 手動觸發。將已驗證的版本推送到 **Production** 環境。

---

## 開發環境 (Dev Environment)

除了上述的標準架構，`deployment/terraform/dev/` 目錄提供了一個簡化版本。
*   它將所有上述邏輯濃縮到單一專案中。
*   省略了複雜的 Cloud Build 觸發器和跨專案 IAM 設定。
*   適合開發者在個人沙箱環境快速迭代。

---

## 執行部署 (Execution)

理解了檔案結構後，實際部署就變得直觀了：

1.  **準備 `terraform.tfvars`**: 填入專案 ID 等變數。
2.  **`terraform init`**: 下載 Providers。
3.  **`terraform plan`**: Terraform 會讀取所有 `.tf` 檔，計算出依賴圖 (Dependency Graph)，並告訴您它打算建立什麼。您會看到它計畫按順序啟用 API -> 建立 SA -> 建立 Bucket/Repo -> 建立 DB -> 部署 Cloud Run。
4.  **`terraform apply`**: 執行計畫。

透過這個流程，您不僅是在執行指令，而是在編排一場精密的基礎設施交響樂。
執行 Plan 以預覽 Terraform 將要建立的資源。這是一個安全檢查步驟，不會實際更動任何資源。

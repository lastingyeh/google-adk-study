# 部署 (Deployment)

此目錄包含用於為您的 Agent 配置必要 Google Cloud 基礎架構的 Terraform 設定。

### 建議部署方式
部署基礎架構並設置 CI/CD 流水的推薦方式是在專案根目錄執行 `agent-starter-pack setup-cicd` 命令。

### 手動部署
如果您偏好動手操作，隨時可以手動套用 Terraform 設定進行 DIY 設置。

### 部署重點說明：
- **Terraform**: 用於自動化建立 Google Cloud 資源（如 Vertex AI、Cloud Storage 等）。
- **CI/CD**: 確保程式碼變更能自動測試並部署到雲端環境。

## 部署環境分類

本專案支援三種部署環境，每個環境具有獨立的 Google Cloud Project 和資源配置：

| 環境             | Project 變數             | 配置位置              | 用途                                       |
| ---------------- | ------------------------ | --------------------- | ------------------------------------------ |
| **Development**  | `dev_project_id`         | `terraform/dev/`      | 開發環境，供開發者本地測試和快速迭代使用   |
| **Staging**      | `staging_project_id`     | `terraform/` (根目錄) | 預發布環境，用於整合測試和 QA 驗證         |
| **Production**   | `prod_project_id`        | `terraform/` (根目錄) | 正式生產環境，服務實際用戶                 |
| **CI/CD Runner** | `cicd_runner_project_id` | `terraform/` (根目錄) | CI/CD 流水線執行環境，負責自動化建構和部署 |

## Google Cloud 服務部署環境對照表

| 服務類別       | 服務名稱          | API / 資源                            | Dev | Staging | Prod | CI/CD | 對應檔案                                                                               | 說明                                             |
| -------------- | ----------------- | ------------------------------------- | --- | ------- | ---- | ----- | -------------------------------------------------------------------------------------- | ------------------------------------------------ |
| **運算與部署** | Cloud Run         | `run.googleapis.com`                  | ✅   | ✅       | ✅    | -     | [service.tf](terraform/service.tf), [dev/service.tf](terraform/dev/service.tf)         | 容器化應用程式部署平台，運行 Agent 服務          |
| **運算與部署** | Cloud Build       | `cloudbuild.googleapis.com`           | -   | -       | -    | ✅     | [apis.tf](terraform/apis.tf), [build_triggers.tf](terraform/build_triggers.tf)         | 自動化建構和部署流水線                           |
| **運算與部署** | Artifact Registry | Docker Repository                     | -   | -       | -    | ✅     | [storage.tf](terraform/storage.tf)                                                     | Docker 映像檔儲存庫                              |
| **AI/ML 服務** | Vertex AI         | `aiplatform.googleapis.com`           | ✅   | ✅       | ✅    | ✅     | [apis.tf](terraform/apis.tf), [dev/apis.tf](terraform/dev/apis.tf)                     | 提供 LLM 模型和 AI Agent 功能                    |
| **AI/ML 服務** | Discovery Engine  | `discoveryengine.googleapis.com`      | ✅   | ✅       | ✅    | ✅     | [apis.tf](terraform/apis.tf), [dev/apis.tf](terraform/dev/apis.tf)                     | 企業級搜尋和推薦引擎                             |
| **儲存與資料** | Cloud Storage     | Storage Buckets                       | ✅   | ✅       | ✅    | ✅     | [storage.tf](terraform/storage.tf), [dev/storage.tf](terraform/dev/storage.tf)         | 日誌資料儲存 (logs bucket)                       |
| **儲存與資料** | BigQuery          | `bigquery.googleapis.com`             | ✅   | ✅       | ✅    | ✅     | [apis.tf](terraform/apis.tf), [log_sinks.tf](terraform/log_sinks.tf)                   | 遙測資料和使用者回饋資料倉儲                     |
| **監控與日誌** | Cloud Logging     | `logging.googleapis.com`              | ✅   | ✅       | ✅    | -     | [apis.tf](terraform/apis.tf), [dev/apis.tf](terraform/dev/apis.tf)                     | 集中式日誌管理                                   |
| **監控與日誌** | Cloud Trace       | `cloudtrace.googleapis.com`           | ✅   | ✅       | ✅    | ✅     | [apis.tf](terraform/apis.tf), [dev/apis.tf](terraform/dev/apis.tf)                     | 分散式追蹤和效能監控                             |
| **監控與日誌** | Log Sinks         | Logging Export                        | ✅   | ✅       | ✅    | -     | [log_sinks.tf](terraform/log_sinks.tf), [dev/log_sinks.tf](terraform/dev/log_sinks.tf) | 將特定日誌匯出至 BigQuery (telemetry & feedback) |
| **身份與權限** | IAM               | `iam.googleapis.com`                  | ✅   | ✅       | ✅    | -     | [iam.tf](terraform/iam.tf), [dev/iam.tf](terraform/dev/iam.tf)                         | 身份和存取管理                                   |
| **身份與權限** | Service Accounts  | IAM Service Accounts                  | ✅   | ✅       | ✅    | ✅     | [service_accounts.tf](terraform/service_accounts.tf)                                   | Agent 應用和 CI/CD 流水線的服務帳戶              |
| **基礎設施**   | Resource Manager  | `cloudresourcemanager.googleapis.com` | ✅   | ✅       | ✅    | ✅     | [apis.tf](terraform/apis.tf), [dev/apis.tf](terraform/dev/apis.tf)                     | 專案和資源層級管理                               |
| **基礎設施**   | Service Usage     | `serviceusage.googleapis.com`         | ✅   | ✅       | ✅    | ✅     | [apis.tf](terraform/apis.tf), [dev/apis.tf](terraform/dev/apis.tf)                     | API 啟用和配額管理                               |

## 環境特定配置

### Development 環境
- **特點**: 簡化配置，無 CI/CD 整合
- **資源**: Cloud Run (單一服務)、Service Account、Log Sinks、BigQuery
- **適用場景**: 本地開發、功能驗證

### Staging 環境
- **特點**: 完整 CI/CD 整合、自動部署
- **觸發器**: `cd-pipeline` (main branch push)
- **資源**: 與 Production 相同架構但獨立專案

### Production 環境
- **特點**: 手動觸發部署、嚴格的存取控制
- **觸發器**: `deploy-to-prod` (手動觸發)
- **資源配置**:
  - CPU: 4 cores
  - Memory: 8Gi
  - Scaling: 1-10 instances

### CI/CD Runner 環境
- **職責**:
  - 執行 PR 檢查 (`pr-checks`)
  - 建構 Docker 映像
  - 部署至 Staging 和 Production
- **整合**: GitHub repository 連結 (Cloud Build 2nd gen)

## 主要 Terraform 模組說明

| 檔案                  | 功能                                                    |
| --------------------- | ------------------------------------------------------- |
| `apis.tf`             | 啟用所需的 Google Cloud APIs                            |
| `service.tf`          | 建立 Cloud Run 服務 (Staging & Production)              |
| `storage.tf`          | 建立 Storage Buckets 和 Artifact Registry               |
| `iam.tf`              | 配置 IAM 角色綁定                                       |
| `service_accounts.tf` | 建立應用和 CI/CD 服務帳戶                               |
| `log_sinks.tf`        | 設定日誌匯出到 BigQuery                                 |
| `build_triggers.tf`   | 配置 Cloud Build 觸發器 (PR checks, CD, Deploy to Prod) |
| `github.tf`           | 設定 GitHub 儲存庫連結                                  |

關於部署流程、基礎架構和 CI/CD 流水的詳細資訊，請參考官方文件：

**[Agent Starter Pack 部署指南](https://googlecloudplatform.github.io/agent-starter-pack/guide/deployment.html)**

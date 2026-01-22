# Copyright 2025 Google LLC
#
# 根據 Apache License 2.0 版本（「本授權」）授權；
# 除非遵守本授權，否則您不得使用此檔案。
# 您可以在以下網址獲得本授權的副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據本授權分發的軟體
# 是按「現狀」基礎分發的，無任何明示或暗示的保證或條件。
# 請參閱本授權以了解管理權限和限制的特定語言。

/*
## 重點摘要
- **核心概念**：定義 Terraform 配置中使用的本地常數 (Locals)，以簡化資源引用。
- **關鍵技術**：Terraform `locals` 區塊，GCP 服務清單與專案 ID 映射。
- **重要結論**：集中定義服務清單與專案 ID，提高配置的可維護性與可讀性。
- **行動項目**：當新增相依服務時，請在此更新對應的清單。
*/

locals {
  # CI/CD 專案需要啟用的服務清單
  cicd_services = [
    "cloudbuild.googleapis.com",
    "discoveryengine.googleapis.com",
    "aiplatform.googleapis.com",
    "serviceusage.googleapis.com",
    "bigquery.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "cloudtrace.googleapis.com",
    "telemetry.googleapis.com",
    "sqladmin.googleapis.com",
  ]

  # 部署專案 (Staging/Prod) 需要啟用的服務清單
  deploy_project_services = [
    "aiplatform.googleapis.com",
    "run.googleapis.com",
    "discoveryengine.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "bigquery.googleapis.com",
    "serviceusage.googleapis.com",
    "logging.googleapis.com",
    "cloudtrace.googleapis.com",
    "telemetry.googleapis.com",
    "sqladmin.googleapis.com",
    "secretmanager.googleapis.com"
  ]

  # 部署專案的 ID 對照表
  deploy_project_ids = {
    prod    = var.prod_project_id
    staging = var.staging_project_id
  }

  # 涉及的所有專案 ID 清單
  all_project_ids = [
    var.cicd_runner_project_id,
    var.prod_project_id,
    var.staging_project_id
  ]
}

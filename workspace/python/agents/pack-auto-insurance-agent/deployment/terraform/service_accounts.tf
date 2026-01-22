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
- **核心概念**：建立用於 CI/CD 流程與應用程式運行的專用服務帳號。
- **關鍵技術**：Terraform `google_service_account`, `for_each` 迴圈。
- **重要結論**：實現了權限最小化原則，通過獨立的服務帳號分別處理部署工作與應用程式運行時的權限需求。
- **行動項目**：在 IAM 設定中確保這些服務帳號已被授予正確的角色。
*/

# CI/CD 執行器服務帳號
resource "google_service_account" "cicd_runner_sa" {
  account_id   = "${var.project_name}-cb"
  display_name = "CICD 執行器服務帳號"
  project      = var.cicd_runner_project_id
  depends_on   = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 代理應用程式服務帳號
resource "google_service_account" "app_sa" {
  for_each = local.deploy_project_ids

  account_id   = "${var.project_name}-app"
  display_name = "${var.project_name} 代理服務帳號"
  project      = each.value
  depends_on   = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

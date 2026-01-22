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
- **核心概念**：管理開發 (Dev) 環境中的 IAM 權限，包括應用程式服務帳號的建立與權限分配。
- **關鍵技術**：Terraform `google_project_iam_member`, `google_service_account`, `setproduct`。
- **重要結論**：為開發環境建立了獨立的服務帳號並授予了運行代理程式所需的各項權限。
- **行動項目**：確認開發專案編號正確無誤。
*/

locals {
  project_ids = {
    dev = var.dev_project_id
  }
}

# 獲取開發專案的專案編號
data "google_project" "dev_project" {
  project_id = var.dev_project_id
}

# 授予預設 Compute 服務帳號 Cloud Build 建置者角色
resource "google_project_iam_member" "default_compute_sa_storage_object_creator" {
  project    = var.dev_project_id
  role       = "roles/cloudbuild.builds.builder"
  member     = "serviceAccount:${data.google_project.dev_project.number}-compute@developer.gserviceaccount.com"
  depends_on = [resource.google_project_service.services]
}

# 代理服務帳號
resource "google_service_account" "app_sa" {
  account_id   = "${var.project_name}-app"
  display_name = "${var.project_name} 代理服務帳號"
  project      = var.dev_project_id
  depends_on   = [resource.google_project_service.services]
}

# 授予應用程式服務帳號執行應用程式所需的權限
resource "google_project_iam_member" "app_sa_roles" {
  for_each = {
    for pair in setproduct(keys(local.project_ids), var.app_sa_roles) :
    join(",", pair) => {
      project = local.project_ids[pair[0]]
      role    = pair[1]
    }
  }

  project    = each.value.project
  role       = each.value.role
  member     = "serviceAccount:${google_service_account.app_sa.email}"
  depends_on = [resource.google_project_service.services]
}

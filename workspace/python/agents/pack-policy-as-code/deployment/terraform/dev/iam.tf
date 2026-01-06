

locals {
  project_ids = {
    dev = var.dev_project_id
  }
}


# 獲取 Dev 專案的詳細資訊 (包括專案編號)
data "google_project" "dev_project" {
  project_id = var.dev_project_id
}

# 賦予預設 Compute Engine Service Account 建構權限
# 允許其執行 Cloud Build 建構任務
resource "google_project_iam_member" "default_compute_sa_storage_object_creator" {
  project    = var.dev_project_id
  role       = "roles/cloudbuild.builds.builder"
  member     = "serviceAccount:${data.google_project.dev_project.number}-compute@developer.gserviceaccount.com"
  depends_on = [resource.google_project_service.services]
}

# 建立 Agent 應用程式 Service Account (Dev 環境)
resource "google_service_account" "app_sa" {
  account_id   = "${var.project_name}-app"
  display_name = "${var.project_name} Agent 服務帳戶"
  project      = var.dev_project_id
  depends_on   = [resource.google_project_service.services]
}

# 授予應用程式 Service Account 運行所需的 IAM 權限
# 使用 setproduct 迭代賦予角色
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

locals {
  # 專案 ID 對照表，這裡只有開發環境
  project_ids = {
    dev = var.dev_project_id
  }
}


# 獲取開發專案的專案編號
data "google_project" "dev_project" {
  project_id = var.dev_project_id
}

# 賦予預設 Compute Engine 服務帳戶 Cloud Build 建置者角色
# 注意：原始註解提及 Storage Object Creator，但程式碼使用的是 cloudbuild.builds.builder
resource "google_project_iam_member" "default_compute_sa_storage_object_creator" {
  project    = var.dev_project_id
  role       = "roles/cloudbuild.builds.builder"
  member     = "serviceAccount:${data.google_project.dev_project.number}-compute@developer.gserviceaccount.com"
  depends_on = [resource.google_project_service.services]
}

# 建立應用程式代理服務帳戶
# 用於開發環境的應用程式執行
resource "google_service_account" "app_sa" {
  account_id   = "${var.project_name}-app"
  display_name = "${var.project_name} Agent Service Account"
  project      = var.dev_project_id
  depends_on   = [resource.google_project_service.services]
}

# 賦予應用程式服務帳戶執行應用程式所需的權限
# 使用 setproduct 組合專案和角色列表
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

# Terraform 設定：身分與存取管理 (IAM)
# 此檔案定義了 CI/CD 流水線、應用程式服務帳戶以及各專案間的權限配置

# 獲取專案編號的資料來源
data "google_project" "projects" {
  for_each   = local.deploy_project_ids
  project_id = each.value
}

# 1. 為 CI/CD 專案指派角色
resource "google_project_iam_member" "cicd_project_roles" {
  for_each = toset(var.cicd_roles)

  project    = var.cicd_runner_project_id
  role       = each.value
  member     = "serviceAccount:${resource.google_service_account.cicd_runner_sa.email}"
  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 2. 為其他專案 (生產環境 Prod 與 測試環境 Staging) 指派 CI/CD 所需的角色
resource "google_project_iam_member" "other_projects_roles" {
  for_each = {
    for pair in setproduct(keys(local.deploy_project_ids), var.cicd_sa_deployment_required_roles) :
    "${pair[0]}-${pair[1]}" => {
      project_id = local.deploy_project_ids[pair[0]]
      role       = pair[1]
    }
  }

  project    = each.value.project_id
  role       = each.value.role
  member     = "serviceAccount:${resource.google_service_account.cicd_runner_sa.email}"
  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 3. 授予應用程式服務帳戶 (App SA) 執行所需的權限
resource "google_project_iam_member" "app_sa_roles" {
  for_each = {
    for pair in setproduct(keys(local.deploy_project_ids), var.app_sa_roles) :
    join(",", pair) => {
      project = local.deploy_project_ids[pair[0]]
      role    = pair[1]
    }
  }

  project    = each.value.project
  role       = each.value.role
  member     = "serviceAccount:${google_service_account.app_sa[split(",", each.key)[0]].email}"
  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 允許 GKE 節點從 CI/CD 專案的 Artifact Registry 拉取容器映像檔
resource "google_project_iam_member" "cicd_gke_artifact_registry_reader" {
  for_each = local.deploy_project_ids
  project  = var.cicd_runner_project_id

  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${data.google_project.projects[each.key].number}-compute@developer.gserviceaccount.com"
  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 允許 Kubernetes 服務帳戶透過 Workload Identity 模擬 GCP 應用程式服務帳戶
resource "google_service_account_iam_member" "workload_identity_binding" {
  for_each           = local.deploy_project_ids
  service_account_id = google_service_account.app_sa[each.key].name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${each.value}.svc.id.goog[${var.project_name}/${var.project_name}]"
}

# 特別指派：允許 CI/CD SA 建立權杖 (Token Creator)
resource "google_service_account_iam_member" "cicd_run_invoker_token_creator" {
  service_account_id = google_service_account.cicd_runner_sa.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:${resource.google_service_account.cicd_runner_sa.email}"
  depends_on         = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 特別指派：允許 CI/CD SA 模擬自身以建立觸發器 (Service Account User)
resource "google_service_account_iam_member" "cicd_run_invoker_account_user" {
  service_account_id = google_service_account.cicd_runner_sa.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${resource.google_service_account.cicd_runner_sa.email}"
  depends_on         = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}
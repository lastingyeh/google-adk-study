# 用於獲取 Project Number 的 Data source
data "google_project" "projects" {
  for_each   = local.deploy_project_ids
  project_id = each.value
}

# 1. 為 CI/CD Runner 專案指派角色
# 賦予 CI/CD Service Account 在 CI/CD 專案中的權限 (如 Cloud Build, Storage, Logging 等)
resource "google_project_iam_member" "cicd_project_roles" {
  for_each = toset(var.cicd_roles)

  project    = var.cicd_runner_project_id
  role       = each.value
  member     = "serviceAccount:${resource.google_service_account.cicd_runner_sa.email}"
  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]

}

# 2. 為其他兩個專案 (Staging 和 Production) 指派角色
# 賦予 CI/CD Service Account 在目標部署專案中的權限 (如部署 Cloud Run, 寫入 Storage 等)
# 使用 setproduct 產生 (專案, 角色) 的所有組合
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
# 3. 授予應用程式 Service Account 運行所需的權限
# 賦予 Agent 應用程式在各環境中運行所需的 IAM 角色 (如讀取 Secrets, 寫入 Log, 連接 DB 等)
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


# 4. 允許 Cloud Run 服務 Service Account 從 CI/CD 專案拉取容器映像檔
# 跨專案權限：部署專案 (Staging/Prod) 的 Cloud Run 需要讀取 CI/CD 專案中的 Artifact Registry
resource "google_project_iam_member" "cicd_run_invoker_artifact_registry_reader" {
  for_each = local.deploy_project_ids
  project  = var.cicd_runner_project_id

  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:service-${data.google_project.projects[each.key].number}@serverless-robot-prod.iam.gserviceaccount.com"
  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]

}




# 特殊指派：允許 CI/CD SA 建立 Token
# 這是為了讓 Cloud Build 能以 Service Account 身份執行某些需要 Token 的操作
resource "google_service_account_iam_member" "cicd_run_invoker_token_creator" {
  service_account_id = google_service_account.cicd_runner_sa.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:${resource.google_service_account.cicd_runner_sa.email}"
  depends_on         = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}
# 特殊指派：允許 CI/CD SA 模擬自身以建立觸發器
# 這是 Cloud Build 觸發器配置所需的權限
resource "google_service_account_iam_member" "cicd_run_invoker_account_user" {
  service_account_id = google_service_account.cicd_runner_sa.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${resource.google_service_account.cicd_runner_sa.email}"
  depends_on         = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

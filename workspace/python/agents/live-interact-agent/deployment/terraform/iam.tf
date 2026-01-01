# 獲取專案編號的資料來源
data "google_project" "projects" {
  for_each   = local.deploy_project_ids
  project_id = each.value
}

# 1. 為 CI/CD 專案指派角色
# 賦予 CI/CD 執行器服務帳戶在 CI/CD 專案中所需的權限
resource "google_project_iam_member" "cicd_project_roles" {
  for_each = toset(var.cicd_roles)

  project    = var.cicd_runner_project_id
  role       = each.value
  member     = "serviceAccount:${resource.google_service_account.cicd_runner_sa.email}"
  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]

}

# 2. 為其他兩個專案 (生產環境和測試環境) 指派角色
# 賦予 CI/CD 執行器服務帳戶在部署目標專案中所需的權限
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

# 3. 賦予應用程式服務帳戶執行應用程式所需的權限
# 這包括存取 Cloud Storage, Vertex AI 等服務的權限
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


# 4. 允許 Cloud Run 服務帳戶從 CI/CD 專案拉取容器映像檔
# 賦予 Artifact Registry 讀取權限
resource "google_project_iam_member" "cicd_run_invoker_artifact_registry_reader" {
  for_each = local.deploy_project_ids
  project  = var.cicd_runner_project_id

  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:service-${data.google_project.projects[each.key].number}@serverless-robot-prod.iam.gserviceaccount.com"
  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]

}

# 特殊指派：允許 CI/CD 服務帳戶建立權杖
# 這對於某些自動化任務是必需的
resource "google_service_account_iam_member" "cicd_run_invoker_token_creator" {
  service_account_id = google_service_account.cicd_runner_sa.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:${resource.google_service_account.cicd_runner_sa.email}"
  depends_on         = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 特殊指派：允許 CI/CD 服務帳戶模擬自己
# 用於建立觸發器時指定服務帳戶
resource "google_service_account_iam_member" "cicd_run_invoker_account_user" {
  service_account_id = google_service_account.cicd_runner_sa.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${resource.google_service_account.cicd_runner_sa.email}"
  depends_on         = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

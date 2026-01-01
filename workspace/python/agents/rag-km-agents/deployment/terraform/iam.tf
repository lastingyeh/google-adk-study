# 獲取專案編號的資料來源
# 用於後續 IAM 綁定中需要專案編號的地方
data "google_project" "projects" {
  for_each   = local.deploy_project_ids
  project_id = each.value
}

# 1. 為 CI/CD 專案分配權限角色
# 授予 CI/CD 執行服務帳號在 CI/CD 專案中的必要權限
resource "google_project_iam_member" "cicd_project_roles" {
  for_each = toset(var.cicd_roles)

  project    = var.cicd_runner_project_id
  role       = each.value
  member     = "serviceAccount:${resource.google_service_account.cicd_runner_sa.email}"
  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]

}

# 2. 為其他兩個專案 (Prod 和 Staging) 分配權限角色
# 授予 CI/CD 執行服務帳號在部署目標專案中的必要權限
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

# 3. 授予應用程式服務帳號執行應用程式所需的權限
# 應用程式服務帳號需要訪問 AI Platform, Discovery Engine, Logging 等服務
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


# 4. 允許 Cloud Run 服務帳號拉取存儲在 CI/CD 專案中的容器映像
# 這是因為容器映像存儲在 CI/CD 專案的 Artifact Registry 中
resource "google_project_iam_member" "cicd_run_invoker_artifact_registry_reader" {
  for_each = local.deploy_project_ids
  project  = var.cicd_runner_project_id

  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:service-${data.google_project.projects[each.key].number}@serverless-robot-prod.iam.gserviceaccount.com"
  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]

}


# 特殊授權：允許 CI/CD 服務帳號建立權杖 (Tokens)
# 這對於某些自動化操作是必需的
resource "google_service_account_iam_member" "cicd_run_invoker_token_creator" {
  service_account_id = google_service_account.cicd_runner_sa.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:${resource.google_service_account.cicd_runner_sa.email}"
  depends_on         = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 特殊授權：允許 CI/CD 服務帳號模擬自身以建立觸發器
# 在建立 Cloud Build 觸發器時可能需要此權限
resource "google_service_account_iam_member" "cicd_run_invoker_account_user" {
  service_account_id = google_service_account.cicd_runner_sa.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${resource.google_service_account.cicd_runner_sa.email}"
  depends_on         = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 授予 Vertex AI 服務帳號執行資料攝取所需的權限
# Pipeline 服務帳號需要訪問 Storage, BigQuery, Discovery Engine 等
resource "google_project_iam_member" "vertexai_pipeline_sa_roles" {
  for_each = {
    for pair in setproduct(keys(local.deploy_project_ids), var.pipelines_roles) :
    join(",", pair) => {
      project = local.deploy_project_ids[pair[0]]
      role    = pair[1]
    }
  }

  project    = each.value.project
  role       = each.value.role
  member     = "serviceAccount:${google_service_account.vertexai_pipeline_app_sa[split(",", each.key)[0]].email}"
  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 建立 CI/CD Runner 服務帳號
# 此服務帳號用於執行 Cloud Build 構建和部署任務
resource "google_service_account" "cicd_runner_sa" {
  account_id   = "${var.project_name}-cb"
  display_name = "CICD Runner SA"
  project      = var.cicd_runner_project_id
  depends_on   = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 建立 Agent 應用程式服務帳號
# 此服務帳號將被 Cloud Run 服務使用，擁有應用程式執行所需的權限
resource "google_service_account" "app_sa" {
  for_each = local.deploy_project_ids

  account_id   = "${var.project_name}-app"
  display_name = "${var.project_name} Agent Service Account"
  project      = each.value
  depends_on   = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}


# 建立 Vertex AI Pipeline 服務帳號
# 此服務帳號用於執行資料攝取 (RAG) 的 Pipeline 任務
resource "google_service_account" "vertexai_pipeline_app_sa" {
  for_each = local.deploy_project_ids

  account_id   = "${var.project_name}-rag"
  display_name = "Vertex AI Pipeline app SA"
  project      = each.value
  depends_on   = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

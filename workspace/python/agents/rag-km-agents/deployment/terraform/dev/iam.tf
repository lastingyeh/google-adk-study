locals {
  project_ids = {
    dev = var.dev_project_id
  }
}


# 獲取開發環境專案的資訊
# 用於取得專案編號
data "google_project" "dev_project" {
  project_id = var.dev_project_id
}

# 授予預設計算服務帳號 (Compute SA) Cloud Build 建構者角色
# 這允許預設的計算服務帳號執行構建任務
resource "google_project_iam_member" "default_compute_sa_storage_object_creator" {
  project    = var.dev_project_id
  role       = "roles/cloudbuild.builds.builder"
  member     = "serviceAccount:${data.google_project.dev_project.number}-compute@developer.gserviceaccount.com"
  depends_on = [resource.google_project_service.services]
}

# 建立 Agent 應用程式服務帳號
# 用於開發環境的應用程式運行
resource "google_service_account" "app_sa" {
  account_id   = "${var.project_name}-app"
  display_name = "${var.project_name} Agent Service Account"
  project      = var.dev_project_id
  depends_on   = [resource.google_project_service.services]
}

# 授予應用程式服務帳號執行應用程式所需的權限
# 使用 setproduct 組合專案 ID 和角色列表進行賦權
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



# 建立 Vertex AI Pipeline 服務帳號
# 用於執行開發環境的資料攝取 Pipeline
resource "google_service_account" "vertexai_pipeline_app_sa" {
  for_each = local.project_ids

  account_id   = "${var.project_name}-rag"
  display_name = "Vertex AI Pipeline app SA"
  project      = each.value
  depends_on   = [resource.google_project_service.services]
}

# 授予 Vertex AI Pipeline 服務帳號所需的權限
# 包括 Storage Admin, BigQuery Editor, Vertex AI User 等
resource "google_project_iam_member" "vertexai_pipeline_sa_roles" {
  for_each = {
    for pair in setproduct(keys(local.project_ids), var.pipelines_roles) :
    join(",", pair) => {
      project = local.project_ids[pair[0]]
      role    = pair[1]
    }
  }

  project    = each.value.project
  role       = each.value.role
  member     = "serviceAccount:${google_service_account.vertexai_pipeline_app_sa[split(",", each.key)[0]].email}"
  depends_on = [resource.google_project_service.services]
}

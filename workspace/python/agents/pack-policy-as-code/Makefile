# ==============================================================================
# 安裝與設定
# ==============================================================================

# 使用 uv 套件管理器安裝相依性
install:
	@command -v uv >/dev/null 2>&1 || { echo "uv 尚未安裝。正在安裝 uv..."; curl -LsSf https://astral.sh/uv/0.8.13/install.sh | sh; source $HOME/.local/bin/env; }
	uv sync

# ==============================================================================
# Playground 目標
# ==============================================================================

# 啟動本地開發 Playground
playground:
	@echo "==============================================================================="
	@echo "| 🚀 啟動您的代理 Playground...                                        |"
	@echo "|                                                                             |"
	@echo "| 💡 嘗試詢問：所有表格必須有 DATA_OWNER 標籤。                     |"
	@echo "|                                                                             |"
	@echo "| 🔍 重要：選擇 'policy_as_code_agent' 資料夾以與您的代理互動。          |"
	@echo "==============================================================================="
	uv run adk web . --port 8501 --reload_agents

# ==============================================================================
# 本地開發命令
# ==============================================================================

# 啟動具有熱重載功能的本地開發伺服器
local-backend:
	uv run uvicorn policy_as_code_agent.fast_api_app:app --host localhost --port 8000 --reload

# 啟動具有 debug 模式的本地後端伺服器
# 用法：make debug-backend [PORT=8000] - 以 debug 模式啟動後端，可指定埠號
debug-backend:
	@echo "==============================================================================="
	@echo "| 🐛 啟動後端 Debug 模式...                                             |"
	@echo "| 📍 伺服器位址：http://localhost:$(or $(PORT),8000)                           |"
	@echo "| 🔍 Debugger 監聽：5678                                                   |"
	@echo "| 🔄 熱重載：啟用                                                            |"
	@echo "==============================================================================="
	uv run --with debugpy python -m debugpy --listen 5678 --wait-for-client -m uvicorn policy_as_code_agent.fast_api_app:app --host localhost --port $(or $(PORT),8000) --reload

# 啟動 debug 模式的本地開發伺服器
# 用法：make debug [PORT=8501] - 以 debug 模式啟動，可指定埠號
debug-playground:
	@echo "==============================================================================="
	@echo "| 🐛 啟動 Debug 模式...                                                  |"
	@echo "| 📍 伺服器位址：http://localhost:$(or $(PORT),8501)                           |"
	@echo "| 🔍 日誌級別：DEBUG                                                        |"
	@echo "| 🔄 熱重載：啟用                                                            |"
	@echo "==============================================================================="
	uv run --with debugpy python -m debugpy --listen 5678 --wait-for-client -m google.adk.cli web . --port $(or $(PORT),8501) --reload_agents

# ==============================================================================
# 後端部署目標
# ==============================================================================

# 遠端部署代理
# 用法：make deploy [IAP=true] [PORT=8080] - 設定 IAP=true 啟用 Identity-Aware Proxy，PORT 指定容器埠
deploy:
	PROJECT_ID=$$(gcloud config get-value project) && \
	gcloud beta run deploy pack-policy-as-code \
		--source . \
		--memory "4Gi" \
		--project $$PROJECT_ID \
		--region "us-central1" \
		--no-allow-unauthenticated \
		--no-cpu-throttling \
		--labels "created-by=adk" \
		--update-build-env-vars "AGENT_VERSION=$(shell awk -F'"' '/^version = / {print $$2}' pyproject.toml || echo '0.0.0')" \
		--update-env-vars \
		"COMMIT_SHA=$(shell git rev-parse HEAD)" \
		$(if $(IAP),--iap) \
		$(if $(PORT),--port=$(PORT))

# 與 'make deploy' 的別名，提供向後相容性
backend: deploy

# ==============================================================================
# Docker 映像管理
# ==============================================================================

# 建置 Docker 映像
# 用法：make docker-build [TAG=custom-tag] - 建置 Docker 映像，可指定自訂標籤
docker-build:
	@echo "==============================================================================="
	@echo "| 🐳 建置 Docker 映像...                                                |"
	@echo "==============================================================================="
	PROJECT_ID=$$(gcloud config get-value project) && \
	REGION="us-central1" && \
	REPOSITORY_NAME="pack-policy-as-code-repo" && \
	CONTAINER_NAME="pack-policy-as-code" && \
	AGENT_VERSION=$$(awk -F'"' '/^version = / {print $$2}' pyproject.toml || echo '0.0.1') && \
	COMMIT_SHA=$$(git rev-parse HEAD) && \
	IMAGE_TAG="$${REGION}-docker.pkg.dev/$${PROJECT_ID}/$${REPOSITORY_NAME}/$${CONTAINER_NAME}:$${COMMIT_SHA}" && \
	IMAGE_LATEST="$${REGION}-docker.pkg.dev/$${PROJECT_ID}/$${REPOSITORY_NAME}/$${CONTAINER_NAME}:latest" && \
	docker build \
		--build-arg COMMIT_SHA=$${COMMIT_SHA} \
		--build-arg AGENT_VERSION=$${AGENT_VERSION} \
		-t $(or $(TAG),$$CONTAINER_NAME:local) \
		-t $${IMAGE_TAG} \
		-t $${IMAGE_LATEST} \
		.

# 推送 Docker 映像至 Artifact Registry
# 用法：make docker-push - 推送映像到 Artifact Registry
docker-push:
	@echo "==============================================================================="
	@echo "| 📤 推送 Docker 映像至 Artifact Registry...                           |"
	@echo "==============================================================================="
	PROJECT_ID=$$(gcloud config get-value project) && \
	REGION="us-central1" && \
	REPOSITORY_NAME="pack-policy-as-code-repo" && \
	CONTAINER_NAME="pack-policy-as-code" && \
	COMMIT_SHA=$$(git rev-parse HEAD) && \
	IMAGE_TAG="$${REGION}-docker.pkg.dev/$${PROJECT_ID}/$${REPOSITORY_NAME}/$${CONTAINER_NAME}:$${COMMIT_SHA}" && \
	IMAGE_LATEST="$${REGION}-docker.pkg.dev/$${PROJECT_ID}/$${REPOSITORY_NAME}/$${CONTAINER_NAME}:latest" && \
	docker push $${IMAGE_TAG} && \
	docker push $${IMAGE_LATEST}

# 本地測試 Docker 映像
# 用法：make docker-run [PORT=8080] [TAG=image-tag] - 在本地啟動 Docker 容器
docker-run:
	@echo "==============================================================================="
	@echo "| 🚀 啟動 Docker 容器...                                                 |"
	@echo "| 📍 服務位址：http://localhost:$(or $(PORT),8080)                           |"
	@echo "==============================================================================="
	PROJECT_ID=$$(gcloud config get-value project) && \
	REGION="us-central1" && \
	CONTAINER_NAME="pack-policy-as-code" && \
	docker run -p $(or $(PORT),8080):8080 \
		-e GOOGLE_CLOUD_PROJECT=$${PROJECT_ID} \
		-e GOOGLE_CLOUD_LOCATION=$${REGION} \
		-v ~/.config/gcloud:/root/.config/gcloud:ro \
		$(or $(TAG),$${CONTAINER_NAME}:local)

# 停止並清理 Docker 容器
# 用法：make docker-clean - 停止所有容器並清理映像
docker-clean:
	@echo "==============================================================================="
	@echo "| 🧹 清理 Docker 容器與映像...                                          |"
	@echo "==============================================================================="
	CONTAINER_NAME="pack-policy-as-code" && \
	docker stop $$(docker ps -q --filter ancestor=$${CONTAINER_NAME}:local) 2>/dev/null || true && \
	docker rm $$(docker ps -aq --filter ancestor=$${CONTAINER_NAME}:local) 2>/dev/null || true && \
	echo "✅ 清理完成"

# 建置並推送 Docker 映像（組合指令）
# 用法：make docker-publish - 建置並推送映像到 Artifact Registry
docker-publish: docker-build docker-push
	@echo "✅ Docker 映像已成功建置並推送至 Artifact Registry"

# ==============================================================================
# Artifact Registry 管理
# ==============================================================================

# 建立 Artifact Registry 儲存庫
# 用法：make create-artifact-repo [REGION=us-central1] [REPO_NAME=pack-policy-as-code-repo]
create-artifact-repo:
	@echo "==============================================================================="
	@echo "| 📦 建立 Artifact Registry 儲存庫...                                   |"
	@echo "==============================================================================="
	PROJECT_ID=$$(gcloud config get-value project) && \
	REGION="$(or $(REGION),us-central1)" && \
	REPOSITORY_NAME="$(or $(REPO_NAME),pack-policy-as-code-repo)" && \
	gcloud artifacts repositories create $${REPOSITORY_NAME} \
		--repository-format=docker \
		--location=$${REGION} \
		--description="Policy as Code Agent 容器儲存庫" \
		--project=$${PROJECT_ID} && \
	echo "✅ 儲存庫 $${REPOSITORY_NAME} 已建立於 $${REGION}"

# 列出 Artifact Registry 映像
# 用法：make list-artifact-images [REGION=us-central1] [REPO_NAME=pack-policy-as-code-repo]
list-artifact-images:
	PROJECT_ID=$$(gcloud config get-value project) && \
	REGION="$(or $(REGION),us-central1)" && \
	REPOSITORY_NAME="$(or $(REPO_NAME),pack-policy-as-code-repo)" && \
	gcloud artifacts docker images list \
		$${REGION}-docker.pkg.dev/$${PROJECT_ID}/$${REPOSITORY_NAME} \
		--project=$${PROJECT_ID}

# 設定 Docker 認證
# 用法：make docker-auth [REGION=us-central1]
docker-auth:
	@echo "==============================================================================="
	@echo "| 🔐 設定 Docker 認證...                                                 |"
	@echo "==============================================================================="
	REGION="$(or $(REGION),us-central1)" && \
	gcloud auth configure-docker $${REGION}-docker.pkg.dev && \
	echo "✅ Docker 認證已設定完成"

# ==============================================================================
# 基礎設施設定
# ==============================================================================

# 使用 Terraform 設定開發環境資源
setup-dev-env:
	PROJECT_ID=$$(gcloud config get-value project) && \
	(cd deployment/terraform/dev && terraform init && terraform apply --var-file vars/env.tfvars --var dev_project_id=$$PROJECT_ID --auto-approve)

# 使用 Terraform 銷毀開發環境資源
# 用法：make destroy-dev-env - 銷毀開發環境中由 Terraform 建立的所有資源
destroy-dev-env:
	@echo "==============================================================================="
	@echo "| ⚠️  警告：即將銷毀開發環境資源                                          |"
	@echo "| 此操作將刪除所有由 Terraform 管理的資源                                   |"
	@echo "==============================================================================="
	@read -p "確定要繼續嗎？(yes/no): " confirm && [ "$$confirm" = "yes" ] || (echo "已取消操作" && exit 1)
	PROJECT_ID=$$(gcloud config get-value project) && \
	(cd deployment/terraform/dev && terraform init && terraform destroy --var-file vars/env.tfvars --var dev_project_id=$$PROJECT_ID --auto-approve)

# 使用 Terraform 設定正式環境資源（包含 CI/CD、Staging、Production）
# 用法：make setup-prod-env - 設定完整的正式環境基礎設施
setup-prod-env:
	@echo "==============================================================================="
	@echo "| 🏗️  設定正式環境基礎設施...                                            |"
	@echo "| 包含：CI/CD Pipeline、Staging 環境、Production 環境                      |"
	@echo "==============================================================================="
	(cd deployment/terraform && terraform init && terraform apply --var-file vars/env.tfvars)

# 使用 Terraform 銷毀正式環境資源
# 用法：make destroy-prod-env - 銷毀正式環境中由 Terraform 建立的所有資源
destroy-prod-env:
	@echo "==============================================================================="
	@echo "| ⚠️  警告：即將銷毀正式環境資源                                          |"
	@echo "| 此操作將刪除 CI/CD、Staging、Production 所有資源                         |"
	@echo "==============================================================================="
	@read -p "確定要繼續嗎？輸入專案 ID 以確認: " project_confirm && \
	CURRENT_PROJECT=$$(gcloud config get-value project) && \
	[ "$$project_confirm" = "$$CURRENT_PROJECT" ] || (echo "❌ 專案 ID 不符，已取消操作" && exit 1) && \
	(cd deployment/terraform && terraform init && terraform destroy --var-file vars/env.tfvars)

# 檢視 Terraform 執行計劃（開發環境）
# 用法：make terraform-plan-dev - 檢視開發環境的 Terraform 變更計劃
terraform-plan-dev:
	PROJECT_ID=$$(gcloud config get-value project) && \
	(cd deployment/terraform/dev && terraform init && terraform plan --var-file vars/env.tfvars --var dev_project_id=$$PROJECT_ID)

# 檢視 Terraform 執行計劃（正式環境）
# 用法：make terraform-plan-prod - 檢視正式環境的 Terraform 變更計劃
terraform-plan-prod:
	(cd deployment/terraform && terraform init && terraform plan --var-file vars/env.tfvars)

# ==============================================================================
# 測試與程式碼品質
# ==============================================================================

# 執行單元與整合測試
test:
	uv sync --dev
	uv run pytest tests/unit && uv run pytest tests/integration

# 執行程式碼品質檢查 (codespell, ruff, mypy)
lint:
	uv sync --dev --extra lint
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run mypy .
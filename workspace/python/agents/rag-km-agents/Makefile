# ==============================================================================
# 安裝與設定
# ==============================================================================

# 使用 uv 套件管理器安裝依賴項
install:
	@command -v uv >/dev/null 2>&1 || { echo "uv 尚未安裝。正在安裝 uv..."; curl -LsSf https://astral.sh/uv/0.8.13/install.sh | sh; source $HOME/.local/bin/env; }
	uv sync

# ==============================================================================
# Playground 目標
# ==============================================================================

# 啟動本地開發 playground
playground:
	@echo "==============================================================================="
	@echo "| 🚀 正在啟動您的 agent playground...                                         |"
	@echo "|                                                                             |"
	@echo "| 💡 試著問：如何將 pandas dataframe 儲存為 CSV？                            |"
	@echo "|                                                                             |"
	@echo "| 🔍 重要：選擇 'app' 資料夾以與您的 agent 互動。                           |"
	@echo "==============================================================================="
	uv run adk web . --port 8501 --reload_agents

# ==============================================================================
# 本地開發指令
# ==============================================================================

# 啟動具有熱重載功能的本地開發伺服器
local-backend:
	uv run uvicorn app.fast_api_app:app --host localhost --port 8000 --reload

# ==============================================================================
# 後端部署目標
# ==============================================================================

# 遠端部署 agent
# 用法：make deploy [IAP=true] [PORT=8080] - 設定 IAP=true 以啟用 Identity-Aware Proxy，PORT 用於指定容器埠號
deploy:
	PROJECT_ID=$$(gcloud config get-value project) && \
	gcloud beta run deploy rag-km-agents \
		--source . \
		--memory "4Gi" \
		--project $$PROJECT_ID \
		--region "us-central1" \
		--no-allow-unauthenticated \
		--no-cpu-throttling \
		--labels "created-by=adk" \
		--update-build-env-vars "AGENT_VERSION=$(shell awk -F'"' '/^version = / {print $$2}' pyproject.toml || echo '0.0.0')" \
		--update-env-vars \
		"COMMIT_SHA=$(shell git rev-parse HEAD),DATA_STORE_ID=rag-km-agents-datastore,DATA_STORE_REGION=us" \
		$(if $(IAP),--iap) \
		$(if $(PORT),--port=$(PORT))

# 'make deploy' 的別名，用於向後相容
backend: deploy

# ==============================================================================
# 基礎設施設定
# ==============================================================================

# 使用 Terraform 設定開發環境資源
setup-dev-env:
	PROJECT_ID=$$(gcloud config get-value project) && \
	(cd deployment/terraform/dev && terraform init && terraform apply --var-file vars/env.tfvars --var dev_project_id=$$PROJECT_ID --auto-approve)

# ==============================================================================
# 資料擷取 (RAG 功能)
# ==============================================================================

# 執行資料擷取管線以啟用 RAG 功能
data-ingestion:
	PROJECT_ID=$$(gcloud config get-value project) && \
	(cd data_ingestion && uv run data_ingestion_pipeline/submit_pipeline.py \
		--project-id=$$PROJECT_ID \
		--region="us-central1" \
		--data-store-id="rag-km-agents-datastore" \
		--data-store-region="us" \
		--service-account="rag-km-agents-rag@$$PROJECT_ID.iam.gserviceaccount.com" \
		--pipeline-root="gs://$$PROJECT_ID-rag-km-agents-rag" \
		--pipeline-name="data-ingestion-pipeline")

# ==============================================================================
# 測試與程式碼品質
# ==============================================================================

# 執行單元測試和整合測試
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
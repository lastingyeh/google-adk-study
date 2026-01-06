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
# 基礎設施設定
# ==============================================================================

# 使用 Terraform 設定開發環境資源
setup-dev-env:
	PROJECT_ID=$$(gcloud config get-value project) && \
	(cd deployment/terraform/dev && terraform init && terraform apply --var-file vars/env.tfvars --var dev_project_id=$$PROJECT_ID --auto-approve)

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
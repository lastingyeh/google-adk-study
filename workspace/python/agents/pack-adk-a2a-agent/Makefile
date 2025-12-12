# ==============================================================================
# 安裝與設定
# ==============================================================================

# 使用 uv 套件管理器安裝依賴
install:
	@command -v uv >/dev/null 2>&1 || { echo "uv 未安裝。正在安裝 uv..."; curl -LsSf https://astral.sh/uv/0.8.13/install.sh | sh; source $HOME/.local/bin/env; }
	uv sync

# ==============================================================================
# 遊樂場目標
# ==============================================================================

# 啟動本地開發遊樂場
playground:
	@echo "==============================================================================="
	@echo "| 🚀 正在啟動您的代理程式遊樂場...                                           |"
	@echo "|                                                                             |"
	@echo "| 💡 試著問：舊金山的天氣如何？                                               |"
	@echo "|                                                                             |"
	@echo "| 🔍 重要：選擇 'app' 資料夾以與您的代理程式互動。                            |"
	@echo "==============================================================================="
	uv run adk web . --port 8501 --reload_agents

# ==============================================================================
# 本地開發指令
# ==============================================================================

# 啟動具有熱重載功能的本地開發伺服器
local-backend:
	uv run uvicorn app.fast_api_app:app --host localhost --port 8000 --reload

# ==============================================================================
# A2A 協議檢查器
# ==============================================================================

# 啟動 A2A 協議檢查器以測試您的代理程式實作
inspector: setup-inspector-if-needed build-inspector-if-needed
	@echo "==============================================================================="
	@echo "| 🔍 A2A 協議檢查器                                                          |"
	@echo "==============================================================================="
	@echo "| 🌐 檢查器 UI：http://localhost:5001                                        |"
	@echo "|                                                                             |"
	@echo "| 💡 本地測試：                                                               |"
	@echo "|    將此 URL 貼上到檢查器中：                                                |"
	@echo "|    http://localhost:8000/a2a/app/.well-known/agent-card.json              |"
	@echo "|                                                                             |"
	@echo "| 💡 遠端部署測試：                                                           |"
	@echo "|    連線至您部署的 Cloud Run URL                                             |"
	@echo "|    🔐 請參閱 README 了解驗證設定                                            |"
	@echo "==============================================================================="
	@echo ""
	cd tools/a2a-inspector/backend && uv run app.py

# 內部使用：如果尚未存在，則設定檢查器（執行一次）
# TODO: 當 a2a-inspector 發布版本時更新為 --branch v1.0.0
setup-inspector-if-needed:
	@if [ ! -d "tools/a2a-inspector" ]; then \
		echo "" && \
		echo "📦 首次設定：正在安裝 A2A 檢查器..." && \
		echo "" && \
		mkdir -p tools && \
		git clone --quiet https://github.com/a2aproject/a2a-inspector.git tools/a2a-inspector && \
		(cd tools/a2a-inspector && git -c advice.detachedHead=false checkout --quiet 893e4062f6fbd85a8369228ce862ebbf4a025694) && \
		echo "📥 正在安裝 Python 依賴..." && \
		(cd tools/a2a-inspector && uv sync --quiet) && \
		echo "📥 正在安裝 Node.js 依賴..." && \
		(cd tools/a2a-inspector/frontend && npm install --silent) && \
		echo "🔨 正在建置前端..." && \
		(cd tools/a2a-inspector/frontend && npm run build --silent) && \
		echo "" && \
		echo "✅ A2A 檢查器設定完成！" && \
		echo ""; \
	fi

# 內部使用：如果需要，建置檢查器前端
build-inspector-if-needed:
	@if [ -d "tools/a2a-inspector" ] && [ ! -f "tools/a2a-inspector/frontend/public/script.js" ]; then \
		echo "🔨 正在建置檢查器前端..."; \
		cd tools/a2a-inspector/frontend && npm run build; \
	fi

# ==============================================================================
# 後端部署目標
# ==============================================================================

# 遠端部署代理程式
# 用法：make deploy [IAP=true] [PORT=8080] - 設定 IAP=true 以啟用 Identity-Aware Proxy，PORT 指定容器連接埠
deploy:
	PROJECT_ID=$$(gcloud config get-value project) && \
	PROJECT_NUMBER=$$(gcloud projects describe $$PROJECT_ID --format="value(projectNumber)") && \
	gcloud beta run deploy pack-adk-a2a-agent \
		--source . \
		--memory "4Gi" \
		--project $$PROJECT_ID \
		--region "us-central1" \
		--no-allow-unauthenticated \
		--no-cpu-throttling \
		--labels "created-by=adk" \
		--update-build-env-vars "AGENT_VERSION=$(shell awk -F'"' '/^version = / {print $$2}' pyproject.toml || echo '0.0.0')" \
		--update-env-vars \
		"COMMIT_SHA=$(shell git rev-parse HEAD),APP_URL=https://pack-adk-a2a-agent-$$PROJECT_NUMBER.us-central1.run.app" \
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

# ==============================================================================
# Gemini Enterprise 整合
# ==============================================================================

# 將已部署的代理程式註冊到 Gemini Enterprise
# 用法：make register-gemini-enterprise (互動式 - 將提示輸入所需詳細資訊)
# 對於非互動式使用，設定環境變數：ID 或 GEMINI_ENTERPRISE_APP_ID (完整的 GE 資源名稱)
# 可選環境變數：GEMINI_DISPLAY_NAME, GEMINI_DESCRIPTION, AGENT_CARD_URL
register-gemini-enterprise:
	@PROJECT_ID=$$(gcloud config get-value project 2>/dev/null) && \
	PROJECT_NUMBER=$$(gcloud projects describe $$PROJECT_ID --format="value(projectNumber)" 2>/dev/null) && \
	uvx agent-starter-pack@0.27.0 register-gemini-enterprise \
		--agent-card-url="https://pack-adk-a2a-agent-$$PROJECT_NUMBER.us-central1.run.app/a2a/app/.well-known/agent-card.json" \
		--deployment-target="cloud_run" \
		--project-number="$$PROJECT_NUMBER"

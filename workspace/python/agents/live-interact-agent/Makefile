# ==============================================================================
# 安裝與設定 (Installation & Setup)
# ==============================================================================

# 使用 uv 套件管理器安裝依賴項目
# 這個目標會先檢查 'uv' 指令是否存在。如果不存在，它會自動下載並安裝 uv。
# 接著，它會使用 'uv sync' 來同步 Python 虛擬環境中的依賴項目，
# 然後進入 'frontend' 目錄並執行 'npm install' 來安裝前端的 Node.js 依賴項目。
install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/0.8.13/install.sh | sh; source $HOME/.local/bin/env; }
	uv sync && (cd frontend && npm install)

# ==============================================================================
# 遊樂場目標 (Playground Targets)
# ==============================================================================

# 啟動本地開發遊樂場
# 這個目標會先執行 'build-frontend-if-needed' 來確保前端已經被建置。
# 接著，它會印出一個歡迎橫幅，提供訪問 URL 和使用提示。
# 最後，它使用 'uv run' 啟動 uvicorn 伺服器來運行 FastAPI 應用程式，
# 並開啟 --reload 選項，以便在程式碼變更時自動重啟伺服器。
playground: build-frontend-if-needed
	@echo "==============================================================================="
	@echo "| 🚀 正在啟動您的代理遊樂場...                                        |"
	@echo "|                                                                             |"
	@echo "| 🌐 請由此訪問您的應用程式: http://localhost:8000                               |"
	@echo "| 💡 試著問問: What's the weather in San Francisco?                         |"
	@echo "|                                                                             |"
	@echo "| 🔍 重要提示: 請選擇 'app' 資料夾與您的代理互動。          |"
	@echo "==============================================================================="
	uv run uvicorn app.fast_api_app:app --host localhost --port 8000 --reload

# ==============================================================================
# 本地開發指令 (Local Development Commands)
# ==============================================================================

# 啟動具有熱重載功能的本地開發伺服器
# 這個目標專門用於啟動後端 API 伺服器，並啟用熱重載功能。
# 當您只專注於後端開發時，這非常有用。
local-backend:
	uv run uvicorn app.fast_api_app:app --host localhost --port 8000 --reload

# ==============================================================================
# ADK Live 指令 (ADK Live Commands)
# ==============================================================================

# 為生產環境建置前端
# 這個目標會進入 'frontend' 目錄並執行 'npm run build' 指令，
# 這通常會將 React/Vue/etc. 專案打包成靜態的 HTML/CSS/JS 檔案。
build-frontend:
	(cd frontend && npm run build)

# 僅在需要時建置前端 (條件式建置)
# 這是一個優化過的目標，它會檢查幾種情況來決定是否需要重新建置前端：
# 1. 如果 'frontend/build' 目錄或 'frontend/build/index.html' 檔案不存在，則進行建置。
# 2. 如果 'frontend/package.json' (依賴定義檔) 或任何 'frontend/src' 下的原始碼檔案比建置好的 'index.html' 還要新，則重新建置。
# 3. 如果以上條件都不滿足，則跳過建置，因為目前的建置是最新版本。
build-frontend-if-needed:
	@if [ ! -d "frontend/build" ] || [ ! -f "frontend/build/index.html" ]; then \
		echo "未找到或不完整的前端建置目錄。正在建置..."; \
		$(MAKE) build-frontend; \
	elif [ "frontend/package.json" -nt "frontend/build/index.html" ] || \
		 find frontend/src -newer frontend/build/index.html 2>/dev/null | head -1 | grep -q .; then \
		echo "前端原始碼檔案比建置版本新。正在重新建置..."; \
		$(MAKE) build-frontend; \
	else \
		echo "前端建置已是最新版本。跳過建置..."; \
	fi

# ==============================================================================
# 後端部署目標 (Backend Deployment Targets)
# ==============================================================================

# 遠端部署代理
# 使用方式: make deploy [IAP=true] [PORT=8080] - 設定 IAP=true 以啟用 Identity-Aware Proxy，PORT 用於指定容器端口
# 這個目標會執行一系列 'gcloud' 指令來將應用程式部署到 Google Cloud Run。
# - PROJECT_ID: 從 gcloud 設定中獲取當前的專案 ID。
# - gcloud beta run deploy: 部署服務，名稱為 'live-interact-agent'。
# - --source .: 使用當前目錄作為原始碼進行建置。
# - --memory, --region, --no-allow-unauthenticated, --no-cpu-throttling, --labels: 設定 Cloud Run 服務的各種配置。
# - --update-build-env-vars: 在建置階段設定環境變數，例如從 pyproject.toml 讀取 AGENT_VERSION。
# - --update-env-vars: 在運行階段設定環境變數，例如目前的 git COMMIT_SHA。
# - $(if $(IAP),--iap): 如果執行 make 時傳入了 IAP=true，則添加 --iap 旗標。
# - $(if $(PORT),--port=$(PORT)): 如果執行 make 時傳入了 PORT 變數，則設定容器端口。
deploy:
	PROJECT_ID=$$(gcloud config get-value project) && \
	gcloud beta run deploy live-interact-agent \
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

# 'make deploy' 的別名，用於向後相容
backend: deploy

# ==============================================================================
# 基礎設施設定 (Infrastructure Setup)
# ==============================================================================

# 使用 Terraform 設定開發環境資源
# 這個目標會進入 'deployment/terraform/dev' 目錄，
# 初始化 Terraform ('terraform init')，然後應用配置 ('terraform apply') 來建立或更新 Google Cloud 上的基礎設施。
# 它會將當前的 gcloud 專案 ID 作為變數傳遞給 Terraform。
setup-dev-env:
	PROJECT_ID=$$(gcloud config get-value project) && \
	(cd deployment/terraform/dev && terraform init && terraform apply --var-file vars/env.tfvars --var dev_project_id=$$PROJECT_ID --auto-approve)

# ==============================================================================
# 測試與程式碼品質 (Testing & Code Quality)
# ==============================================================================

# 執行單元測試和整合測試
# 這個目標會先使用 'uv sync --dev' 安裝開發用的依賴項目。
# 然後，它會分別執行 'tests/unit' 和 'tests/integration' 目錄下的 pytest 測試。
test:
	uv sync --dev
	uv run pytest tests/unit && uv run pytest tests/integration

# 執行程式碼品質檢查 (codespell, ruff, mypy)
# 這個目標會安裝 'lint' 相關的依賴項目。
# 接著，它會依序執行：
# - codespell: 檢查程式碼中的拼寫錯誤。
# - ruff check: 檢查程式碼風格和常見錯誤，並顯示差異。
# - ruff format: 檢查程式碼格式是否符合規範，並顯示差異。
# - mypy: 進行靜態類型檢查。
lint:
	uv sync --dev --extra lint
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run mypy .
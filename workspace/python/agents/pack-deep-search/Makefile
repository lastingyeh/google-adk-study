# 安裝相關指令
install:
	@command -v uv >/dev/null 2>&1 || { echo "未安裝 uv。正在安裝 uv..."; curl -LsSf https://astral.sh/uv/0.6.12/install.sh | sh; source $HOME/.local/bin/env; }
	uv sync && npm --prefix frontend install
	# 檢查 uv 是否安裝，若未安裝則自動安裝，然後同步 Python 依賴並安裝前端 npm 套件

# 啟動開發模式（同時啟動後端與前端）
dev:
	make dev-backend & make dev-frontend
	# 並行啟動後端與前端開發伺服器

# 啟動後端開發伺服器
dev-backend:
	uv run adk api_server app --allow_origins="*"
	# 啟動後端 API 伺服器，允許所有來源

# 啟動前端開發伺服器
dev-frontend:
	npm --prefix frontend run dev
	# 啟動前端開發伺服器

# 啟動 playground（互動式網頁）
playground:
	uv run adk web --port 8501
	# 啟動 web playground，監聽 8501 埠口

# 程式碼檢查與格式化
lint:
	uv sync --dev --extra lint
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run mypy .
	# 安裝開發與 lint 相關依賴，執行拼字檢查、程式碼風格檢查、格式檢查與型別檢查

# 清除建置 cache 與 ignore 檔案
clean:
	@echo "正在清除 Python cache 與建置檔案..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.pyd" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".adk" -exec rm -rf {} + 2>/dev/null || true

	@echo "正在清除前端 cache 與建置檔案..."
	rm -rf frontend/node_modules/ frontend/dist/ frontend/.vite/ 2>/dev/null || true
	@echo "清除完成！"
	# 清除 Python __pycache__、*.pyc、測試 cache、型別檢查 cache、建置目錄與前端 node_modules/dist

# --- 來自 Agent Starter Pack 的指令 ---

# 部署後端（預設指向 deploy）
backend: deploy

# 雲端部署
deploy:
	PROJECT_ID=$$(gcloud config get-value project) && \
	gcloud beta run deploy pack-deep-search \
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
	# 取得 GCP 專案 ID，並使用 gcloud 部署 Cloud Run，設定記憶體、專案、區域、標籤、環境變數等

# 本地啟動後端伺服器
local-backend:
	uv run uvicorn app.fast_api_app:app --host localhost --port 8000 --reload
	# 使用 uvicorn 啟動 FastAPI 應用，監聽本地 8000 埠口，支援熱重載

# 設定開發環境（Terraform）
setup-dev-env:
	PROJECT_ID=$$(gcloud config get-value project) && \
	(cd deployment/terraform/dev && terraform init && terraform apply --var-file vars/env.tfvars --var dev_project_id=$$PROJECT_ID --auto-approve)
	# 取得 GCP 專案 ID，初始化並套用 Terraform 腳本，自動建立開發環境

# 執行測試
test:
	uv sync --dev
	uv run pytest tests/unit && uv run pytest tests/integration
	# 安裝開發依賴，執行單元測試與整合測試

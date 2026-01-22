# ==============================================================================
# 安裝與設定 (Installation & Setup)
# ==============================================================================

# 使用 uv 套件管理器安裝依賴項
# 流程說明：
# 1. 檢查系統是否已安裝 uv，若無則自動下載並安裝
# 2. 執行 uv sync 同步專案依賴
install:
	@command -v uv >/dev/null 2>&1 || { echo "未安裝 uv。正在安裝 uv..."; curl -LsSf https://astral.sh/uv/0.8.13/install.sh | sh; source $$HOME/.local/bin/env; }
	uv sync

# ==============================================================================
# 遊樂場目標 (Playground Targets)
# ==============================================================================

# 啟動本地開發遊樂場 (Playground)
# 流程說明：
# 1. 顯示啟動資訊與提示
# 2. 使用 adk CLI 在 8501 埠啟動網頁介面
playground:
	@echo "==============================================================================="
	@echo "| 🚀 正在啟動您的代理人 (Agent) 遊樂場...                                     |"
	@echo "|                                                                             |"
	@echo "| 💡 嘗試詢問：舊金山的天氣如何？                                             |"
	@echo "|                                                                             |"
	@echo "| 🔍 重要：請選擇 'auto_insurance_agent' 資料夾與您的代理人互動。             |"
	@echo "==============================================================================="
	uv run adk web . --port 8501 --reload_agents

# ==============================================================================
# 本地開發命令 (Local Development Commands)
# ==============================================================================

# 啟動支援熱重載 (Hot-reload) 的本地開發伺服器
# 流程說明：
# 1. 使用 uvicorn 啟動 Fast API 應用程式
# 2. 監聽 localhost:8000 並啟用自動重載
local-backend:
	uv run uvicorn auto_insurance_agent.fast_api_app:app --host localhost --port 8000 --reload

# ==============================================================================
# 後端部署目標 (Backend Deployment Targets)
# ==============================================================================

# 遠端部署代理人
# 使用方法：make deploy [IAP=true] [PORT=8080]
# - 設定 IAP=true 以啟用身分識別檢查 Proxy (Identity-Aware Proxy)
# - 設定 PORT 以指定容器連接埠
# 流程說明：
# 1. 取得目前的 Google Cloud 專案 ID
# 2. 使用 gcloud beta run deploy 部署至 Cloud Run
# 3. 設定記憶體 (4Gi)、區域 (us-central1) 及環境變數
deploy:
	PROJECT_ID=$$(gcloud config get-value project) && \
	gcloud beta run deploy pack-auto-insurance-agent \
		--source . \
		--memory "4Gi" \
		--project $$PROJECT_ID \
		--region "us-central1" \
		--no-allow-unauthenticated \
		--no-cpu-throttling \
		--labels "created-by=adk" \
		--update-build-env-vars "AGENT_VERSION=$(shell awk -F'\"' '/^version = / {print $$2}' pyproject.toml || echo '0.0.0')" \
		--update-env-vars \
		"" \
		$(if $(IAP),--iap) \
		$(if $(PORT),--port=$(PORT))

# 'make deploy' 的別名，用於向後相容
backend: deploy

# ==============================================================================
# 基礎架構設定 (Infrastructure Setup)
# ==============================================================================

# 使用 Terraform 設定開發環境資源
# 流程說明：
# 1. 進入 terraform 開發目錄
# 2. 執行 terraform init 初始化
# 3. 執行 terraform apply 自動套用設定
setup-dev-env:
	PROJECT_ID=$$(gcloud config get-value project) && \
	(cd deployment/terraform/dev && terraform init && terraform apply --var-file vars/env.tfvars --var dev_project_id=$$PROJECT_ID --auto-approve)

# ==============================================================================
# 測試與程式碼品質 (Testing & Code Quality)
# ==============================================================================

# 執行單元測試與整合測試
# 流程說明：
# 1. 同步開發環境依賴
# 2. 依序執行 pytest 單元測試與整合測試
test:
	uv sync --dev
	uv run pytest tests/unit && uv run pytest tests/integration

# 執行程式碼品質檢查 (codespell, ruff, ty)
# 流程說明：
# 1. 安裝 lint 相關依賴
# 2. 執行拼字檢查、程式碼風格檢查與型別檢查
lint:
	uv sync --dev --extra lint
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run ty check .

# ==============================================================================
# 清理目標 (Clean Targets)
# ==============================================================================

# 清除所有 make 指令執行產生的檔案與快取
# 流程說明：
# 1. 移除 Python 快取檔案 (__pycache__, *.pyc, *.pyo)
# 2. 移除測試相關檔案 (.pytest_cache, .coverage, htmlcov)
# 3. 移除程式碼檢查快取 (.ruff_cache, .mypy_cache)
# 4. 移除建置檔案 (*.egg-info, dist, build)
# 5. 移除 Terraform 狀態檔與快取
# 注意：此指令不會刪除虛擬環境 (.venv)，如需清除請手動執行 rm -rf .venv
clean:
	@echo "🧹 正在清理專案檔案..."
	@echo "移除 Python 快取檔案..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name "*.pyd" -delete 2>/dev/null || true
	@echo "移除測試相關檔案..."
	@rm -rf .pytest_cache 2>/dev/null || true
	@rm -rf .coverage 2>/dev/null || true
	@rm -rf htmlcov 2>/dev/null || true
	@rm -rf .tox 2>/dev/null || true
	@echo "移除程式碼檢查快取..."
	@rm -rf .ruff_cache 2>/dev/null || true
	@rm -rf .mypy_cache 2>/dev/null || true
	@echo "移除建置檔案..."
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf dist 2>/dev/null || true
	@rm -rf build 2>/dev/null || true
	@echo "移除 Terraform 狀態檔..."
	@find deployment/terraform -type d -name ".terraform" -exec rm -rf {} + 2>/dev/null || true
	@find deployment/terraform -type f -name "terraform.tfstate*" -delete 2>/dev/null || true
	@find deployment/terraform -type f -name ".terraform.lock.hcl" -delete 2>/dev/null || true
	@echo "✅ 清理完成！"
	@echo "💡 提示：虛擬環境 (.venv) 未被刪除。如需清除請執行：rm -rf .venv"

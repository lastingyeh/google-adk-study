

# ==============================================================================
# 安裝與設定
# ==============================================================================

# 使用 uv 套件管理器安裝相依套件
install:
	@command -v uv >/dev/null 2>&1 || { echo "未安裝 uv，正在安裝 uv..."; curl -LsSf https://astral.sh/uv/0.8.13/install.sh | sh; source $HOME/.local/bin/env; }
	uv sync

# ==============================================================================
# Playground 目標
# ==============================================================================

# 啟動本地開發 Playground
playground:
	@echo "==============================================================================="
	@echo "| 🚀 啟動你的代理人 Playground...                                             |"
	@echo "|                                                                             |"
	@echo "| 💡 試著問：舊金山的天氣如何？                                              |"
	@echo "|                                                                             |"
	@echo "| 🔍 重要：請選擇 'bidi_demo' 資料夾來與你的代理人互動。                      |"
	@echo "==============================================================================="
	uv run adk web . --port 8501 --reload_agents

# ==============================================================================
# 本地開發指令
# ==============================================================================

# 啟動本地開發伺服器（支援熱重載）
local-backend:
	uv run uvicorn bidi_demo.fast_api_app:app --host localhost --port 8000 --reload

# 啟動具有 debug 模式的本地後端伺服器
# 用法：make debug-backend [PORT=8000] - 以 debug 模式啟動後端，可指定埠號
debug-backend:
	@echo "==============================================================================="
	@echo "| 🐛 啟動後端 Debug 模式...                                             |"
	@echo "| 📍 伺服器位址：http://localhost:$(or $(PORT),8000)                           |"
	@echo "| 🔍 Debugger 監聽：5678                                                   |"
	@echo "| 🔄 熱重載：啟用                                                            |"
	@echo "==============================================================================="
	uv run --with debugpy python -m debugpy --listen 5678 --wait-for-client -m uvicorn bidi_demo.fast_api_app:app --host localhost --port $(or $(PORT),8000) --reload

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

# 遠端部署代理人
# 用法：make deploy [IAP=true] [PORT=8080] - 設定 IAP=true 啟用 Identity-Aware Proxy，PORT 指定容器埠口
deploy:
	PROJECT_ID=$$(gcloud config get-value project) && \
	gcloud beta run deploy pack-bidi-streaming \
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

# 'make deploy' 的別名，為相容舊指令
backend: deploy

# ==============================================================================
# 基礎設施設定
# ==============================================================================

# 使用 Terraform 建立開發環境資源
setup-dev-env:
	PROJECT_ID=$$(gcloud config get-value project) && \
	(cd deployment/terraform/dev && terraform init && terraform apply --var-file vars/env.tfvars --var dev_project_id=$$PROJECT_ID --auto-approve)

# ==============================================================================
# 測試與程式碼品質
# ==============================================================================

# 執行單元測試與整合測試
test:
	uv sync --dev
	uv run pytest tests/unit && uv run pytest tests/integration

# 執行程式碼品質檢查（codespell, ruff, ty）
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
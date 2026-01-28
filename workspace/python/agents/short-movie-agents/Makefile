# 使用 uv 套件管理器安裝依賴項
install:
	@command -v uv >/dev/null 2>&1 || { echo "未安裝 uv。正在安裝 uv..."; curl -LsSf https://astral.sh/uv/0.6.12/install.sh | sh; source $HOME/.local/bin/env; }
	uv sync --dev

# 啟動本地開發測試場 (Playground)
playground:
	@echo "==============================================================================="
	@echo "| 🚀 正在啟動您的代理測試場...                                                |"
	@echo "|                                                                             |"
	@echo "| 🔍 重要提示：請選擇 'app' 資料夾以與您的代理互動。                           |"
	@echo "==============================================================================="
	uv run adk web . --port 8501 --reload_agents

# 遠端部署代理
# 用法：make backend [PORT=8080] - PORT 用於指定容器端口
backend:
	PROJECT_ID=$$(gcloud config get-value project) && \
	gcloud beta run deploy short-movie-agents \
		--source . \
		--memory "4Gi" \
		--project $$PROJECT_ID \
		--region "europe-west4" \
		--no-cpu-throttling \
		--labels "created-by=adk,dev-tutorial=sample-short-movie-agents" \
		--allow-unauthenticated \
		--env-vars-file .env \
		$(if $(PORT),--port=$(PORT))

# 啟動具有熱重載功能的本地開發伺服器
local-backend:
	uv run uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload

# 執行單元測試和整合測試
test:
	uv run pytest tests/unit && uv run pytest tests/integration

# 執行程式碼品質檢查 (codespell, ruff, mypy)
lint:
	uv sync --dev --extra lint
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run mypy .

# 建立 clean 指令，刪除所有在執行時產生的檔案
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage
	rm -rf build/ dist/ *.egg-info

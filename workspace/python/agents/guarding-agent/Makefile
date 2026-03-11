
# ==============================================================================
# 安裝與設定
# ==============================================================================

# 使用 uv 套件管理器安裝依賴
install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/0.8.13/install.sh | sh; source $HOME/.local/bin/env; }
	uv sync

# ==============================================================================
# 遊樂場目標
# ==============================================================================

# 啟動本地開發遊樂場
playground:
	@echo "==============================================================================="
	@echo "| 🚀 啟動代理遊樂場...                                                         |"
	@echo "|                                                                             |"
	@echo "| 💡 試試看: 舊金山的天氣如何?                                                 |"
	@echo "|                                                                             |"
	@echo "| 🔍 重點: 選擇 'guarding_agent' 資料夾與代理互動                              |"
	@echo "==============================================================================="
	uv run adk web . --port 8501 --reload_agents

# ==============================================================================
# 本地開發指令
# ==============================================================================

# 啟動本地開發伺服器，支援熱重載
# 用法: make local-backend [PORT=8000] - 指定埠號用於平行情景測試
local-backend:
	uv run uvicorn guarding_agent.fast_api_app:app --host localhost --port $(or $(PORT),8000) --reload

# 啟動具有 debug 模式的本地後端伺服器
# 用法：make debug-backend [PORT=8000] - 以 debug 模式啟動後端，可指定埠號
debug-backend:
	@echo "==============================================================================="
	@echo "| 🐛 啟動後端 Debug 模式...                                             |"
	@echo "| 📍 伺服器位址：http://localhost:$(or $(PORT),8000)                           |"
	@echo "| 🔍 Debugger 監聽：5678                                                   |"
	@echo "| 🔄 熱重載：啟用                                                            |"
	@echo "==============================================================================="
	uv run --with debugpy python -m debugpy --listen 5678 --wait-for-client -m uvicorn guarding_agent.fast_api_app:app --host localhost --port $(or $(PORT),8000) --reload

# 啟動 debug 模式的本地開發伺服器
# 用法：make debug [PORT=8501] - 以 debug 模式啟動，可指定埠號
debug-playground:
	@echo "==============================================================================="
	@echo "| 🐛 啟動 Debug 模式...                                                  |"
	@echo "| 📍 伺服器位址：http://localhost:$(or $(PORT),8501)                           |"
	@echo "| 🔍 日誌級別：DEBUG                                                        |"
	@echo "| 🔄 熱重載：啟用                                                            |"
	@echo "==============================================================================="
	uv run --with debugpy python -m debugpy --listen 5678 --wait-for-client -m google.adk.cli web . --port $(or $(PORT),8501) --reload_agents --extra_plugins "guarding_agent.plugins.ContentFilterPlugin" --extra_plugins "guarding_agent.plugins.PIIDetectionPlugin"

# ==============================================================================
# 後端部署目標
# ==============================================================================

# 遠端部署代理
# 用法: make deploy [IMAGE_TAG=mytag] - 構建並部署到 GKE 叢集
deploy:
	@PROJECT_ID=$$(gcloud config get-value project) && \
	echo "透過 Terraform 配置基礎設施..." && \
	(cd deployment/terraform/dev && terraform init && \
	terraform apply --var-file vars/env.tfvars --var dev_project_id=$$PROJECT_ID --auto-approve) && \
	echo "配置 kubectl 認證..." && \
	gcloud container clusters get-credentials guarding-agent-dev --region us-central1 --project $$PROJECT_ID && \
	IMAGE_TAG=$${IMAGE_TAG:-$$(date +%Y%m%d%H%M%S)} && \
	IMAGE=us-central1-docker.pkg.dev/$$PROJECT_ID/guarding-agent/guarding-agent:$$IMAGE_TAG && \
	echo "構建並推送 Docker 映像..." && \
	gcloud builds submit --tag $$IMAGE && \
	echo "部署容器映像..." && \
	kubectl apply -f deployment/k8s/deployment.yaml && \
	kubectl set image deployment/guarding-agent \
		guarding-agent=$$IMAGE \
		-n guarding-agent && \
	echo "等待 Rollout 完成..." && \
	kubectl rollout status deployment/guarding-agent -n guarding-agent --timeout=300s && \
	EXTERNAL_IP=$$(kubectl get svc guarding-agent -n guarding-agent -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null) && \
	if [ -n "$$EXTERNAL_IP" ]; then \
		kubectl set env deployment/guarding-agent APP_URL=http://$$EXTERNAL_IP:8080 -n guarding-agent; \
		echo ""; \
		echo "==============================================================================="; \
		echo "  服務 URL: http://$$EXTERNAL_IP:8080"; \
		echo "==============================================================================="; \
	else \
		echo "外部 IP 仍在配置中。檢查:"; \
		echo "  kubectl get svc guarding-agent -n guarding-agent"; \
	fi

# 'make deploy' 的別名，用於向後相容性
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

# ==============================================================================
# 代理評估
# ==============================================================================

# 使用 ADK eval 執行代理評估
# 用法: make eval [EVALSET=tests/eval/evalsets/basic.evalset.json] [EVAL_CONFIG=tests/eval/eval_config.json]
eval:
	@echo "==============================================================================="
	@echo "| 執行代理評估                                                                |"
	@echo "==============================================================================="
	uv sync --dev --extra eval
	uv run adk eval ./guarding_agent $${EVALSET:-tests/eval/evalsets/basic.evalset.json} \
		$(if $(EVAL_CONFIG),--config_file_path=$(EVAL_CONFIG),$(if $(wildcard tests/eval/eval_config.json),--config_file_path=tests/eval/eval_config.json,))

# 執行所有評估集合
eval-all:
	@echo "==============================================================================="
	@echo "| 執行所有評估集合                                                            |"
	@echo "==============================================================================="
	@for evalset in tests/eval/evalsets/*.evalset.json; do \
		echo ""; \
		echo "▶ 執行: $$evalset"; \
		$(MAKE) eval EVALSET=$$evalset || exit 1; \
	done
	@echo ""
	@echo "✅ 所有評估集合已完成"

# 執行程式碼品質檢查 (codespell, ruff, ty)
lint:
	uv sync --dev --extra lint
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run ty check .
.PHONY: help install setup test eval run clean format lint all deploy

# 默认目标
.DEFAULT_GOAL := help

# 颜色输出
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

# ============================================================================
# 帮助信息
# ============================================================================

help:
	@echo "$(BLUE)=== 品牌搜尋優化 (Brand Search Optimization) ===$(NC)"
	@echo ""
	@echo "$(GREEN)可用命令:$(NC)"
	@echo "  $(YELLOW)make install$(NC)         - 安裝專案依賴（使用 Poetry）"
	@echo "  $(YELLOW)make setup$(NC)           - 完整設定：安裝依賴 + 填入 BigQuery 資料"
	@echo "  $(YELLOW)make test$(NC)            - 執行單元測試"
	@echo "  $(YELLOW)make eval$(NC)            - 執行評估測試（需要 adk 工具）"
	@echo "  $(YELLOW)make run$(NC)             - 執行主程式"
	@echo "  $(YELLOW)make deploy-create$(NC)   - 建立並部署新的遠端代理程式"
	@echo "  $(YELLOW)make deploy-delete$(NC)   - 刪除現有的遠端代理程式"
	@echo "  $(YELLOW)make lint$(NC)            - 執行程式碼檢查（需要安裝 lint 工具）"
	@echo "  $(YELLOW)make format$(NC)          - 格式化程式碼（需要安裝 format 工具）"
	@echo "  $(YELLOW)make clean$(NC)           - 清理編譯檔案和快取"
	@echo "  $(YELLOW)make all$(NC)             - 完整流程：安裝 + 設定 + 測試"
	@echo ""
	@echo "$(GREEN)環境設定:$(NC)"
	@echo "  - 複製 env.example 並建立 .env 檔案"
	@echo "  - 執行 'gcloud auth application-default login' 進行 Google Cloud 認證"
	@echo "  - 設定 GOOGLE_CLOUD_PROJECT 和 GOOGLE_CLOUD_LOCATION"
	@echo ""

# ============================================================================
# 安裝與設定
# ============================================================================

install:
	@echo "$(BLUE)📦 安裝專案依賴...$(NC)"
	poetry install

setup:
	@echo "$(BLUE)⚙️  執行完整設定...$(NC)"
	sh deployment/run.sh

# ============================================================================
# 測試與評估
# ============================================================================

test:
	@echo "$(BLUE)🧪 執行單元測試...$(NC)"
	sh deployment/test.sh

eval:
	@echo "$(BLUE)📊 執行評估測試...$(NC)"
	sh deployment/eval.sh

# ============================================================================
# 執行
# ============================================================================

run:
	@echo "$(BLUE)▶️  執行主程式...$(NC)"
	poetry run python main.py

# ============================================================================
# 部署
# ============================================================================

deploy-create:
	@echo "$(BLUE)🚀 建立並部署遠端代理程式...$(NC)"
	@if [ -z "$(PROJECT)" ]; then \
		echo "$(YELLOW)錯誤: 未提供 PROJECT ID$(NC)"; \
		echo "用法: make deploy-create PROJECT=<your-project-id> LOCATION=<location> BUCKET=<bucket-name>"; \
		exit 1; \
	fi
	@if [ -z "$(LOCATION)" ]; then \
		echo "$(YELLOW)錯誤: 未提供 LOCATION$(NC)"; \
		echo "用法: make deploy-create PROJECT=<your-project-id> LOCATION=<location> BUCKET=<bucket-name>"; \
		exit 1; \
	fi
	@if [ -z "$(BUCKET)" ]; then \
		echo "$(YELLOW)錯誤: 未提供 BUCKET$(NC)"; \
		echo "用法: make deploy-create PROJECT=<your-project-id> LOCATION=<location> BUCKET=<bucket-name>"; \
		exit 1; \
	fi
	poetry run python -m deployment.deploy \
		--project_id=$(PROJECT) \
		--location=$(LOCATION) \
		--bucket=$(BUCKET) \
		--create

deploy-delete:
	@echo "$(BLUE)🗑️  刪除遠端代理程式...$(NC)"
	@if [ -z "$(PROJECT)" ]; then \
		echo "$(YELLOW)錯誤: 未提供 PROJECT ID$(NC)"; \
		echo "用法: make deploy-delete PROJECT=<your-project-id> LOCATION=<location> RESOURCE_ID=<resource-id>"; \
		exit 1; \
	fi
	@if [ -z "$(LOCATION)" ]; then \
		echo "$(YELLOW)錯誤: 未提供 LOCATION$(NC)"; \
		echo "用法: make deploy-delete PROJECT=<your-project-id> LOCATION=<location> RESOURCE_ID=<resource-id>"; \
		exit 1; \
	fi
	@if [ -z "$(RESOURCE_ID)" ]; then \
		echo "$(YELLOW)錯誤: 未提供 RESOURCE_ID$(NC)"; \
		echo "用法: make deploy-delete PROJECT=<your-project-id> LOCATION=<location> RESOURCE_ID=<resource-id>"; \
		exit 1; \
	fi
	poetry run python -m deployment.deploy \
		--project_id=$(PROJECT) \
		--location=$(LOCATION) \
		--resource_id=$(RESOURCE_ID) \
		--delete

# ============================================================================
# 程式碼品質
# ============================================================================

lint:
	@echo "$(BLUE)🔍 執行程式碼檢查...$(NC)"
	@command -v pylint >/dev/null 2>&1 || { echo "$(YELLOW)pylint 未安裝，請執行: pip install pylint$(NC)"; exit 1; }
	pylint brand_search_optimization/

format:
	@echo "$(BLUE)✨ 格式化程式碼...$(NC)"
	@command -v black >/dev/null 2>&1 || { echo "$(YELLOW)black 未安裝，請執行: pip install black$(NC)"; exit 1; }
	black brand_search_optimization/ tests/

# ============================================================================
# 清理
# ============================================================================

clean:
	@echo "$(BLUE)🧹 清理編譯檔案和快取...$(NC)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".DS_Store" -delete
	rm -rf dist/ build/ *.egg-info/
	@echo "$(GREEN)✓ 清理完成$(NC)"

# ============================================================================
# 綜合目標
# ============================================================================

all: clean install setup test
	@echo ""
	@echo "$(GREEN)✓ 所有步驟完成！$(NC)"
	@echo "$(BLUE)可以執行以下命令:$(NC)"
	@echo "  - make run     # 執行主程式"
	@echo "  - make eval    # 執行評估測試"
	@echo "  - make test    # 執行單元測試"

# ============================================================================
# 環境檢查
# ============================================================================

check-env:
	@echo "$(BLUE)🔐 檢查環境設定...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)⚠️  未找到 .env 檔案，複製 env.example...$(NC)"; \
		cp env.example .env; \
		echo "$(YELLOW)請編輯 .env 檔案並填入相關配置$(NC)"; \
	else \
		echo "$(GREEN)✓ .env 檔案存在$(NC)"; \
	fi
	@if command -v gcloud &> /dev/null; then \
		echo "$(GREEN)✓ gcloud 已安裝$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  gcloud 未安裝，請參照 README.md 進行安裝$(NC)"; \
	fi
	@if command -v poetry &> /dev/null; then \
		echo "$(GREEN)✓ Poetry 已安裝$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  Poetry 未安裝，請參照 README.md 進行安裝$(NC)"; \
	fi

# ============================================================================
# 開發輔助
# ============================================================================

.PHONY: shell
shell:
	@echo "$(BLUE)🐚 啟動 Poetry shell...$(NC)"
	poetry shell

.PHONY: update
update:
	@echo "$(BLUE)🔄 更新依賴...$(NC)"
	poetry update

.PHONY: show-deps
show-deps:
	@echo "$(BLUE)📋 顯示依賴列表...$(NC)"
	poetry show

.PHONY: add-dev-pkg
add-dev-pkg:
	@echo "$(BLUE)➕ 新增開發依賴$(NC)"
	@echo "用法: make add-dev-pkg PKG=<package-name>"
	@if [ -z "$(PKG)" ]; then \
		echo "$(YELLOW)請指定套件名稱: make add-dev-pkg PKG=pytest-cov$(NC)"; \
	else \
		poetry add --group dev $(PKG); \
	fi

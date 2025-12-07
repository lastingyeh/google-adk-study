.PHONY: help setup install dev test clean demo docs lint format
.PHONY: test-unit test-int clean-stores demo-upload demo-search demo-workflow

# 輸出顏色
BOLD := \033[1m
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RESET := \033[0m

help:
	@printf "\n$(BOLD)$(BLUE)Policy Navigator - 教學 37$(RESET)\n"
	@printf "$(BOLD)File Search Store 管理系統$(RESET)\n\n"

	@printf "$(BOLD)🚀 開始使用$(RESET)\n"
	@printf "  $(GREEN)setup$(RESET)              安裝相依套件並設定環境\n"
	@printf "  $(GREEN)dev$(RESET)                啟動互動式 ADK 網頁介面\n\n"

	@printf "$(BOLD)📦 開發$(RESET)\n"
	@printf "  $(GREEN)install$(RESET)            以開發模式安裝套件\n"
	@printf "  $(GREEN)lint$(RESET)               執行程式碼品質檢查 (ruff + black + mypy)\n"
	@printf "  $(GREEN)format$(RESET)             使用 black 和 ruff 自動格式化程式碼\n"
	@printf "  $(GREEN)test$(RESET)               執行所有測試並計算覆蓋率\n"
	@printf "  $(GREEN)test-unit$(RESET)          僅執行單元測試\n"
	@printf "  $(GREEN)test-int$(RESET)           僅執行整合測試\n\n"

	@printf "$(BOLD)🎯 展示 (Demos)$(RESET)\n"
	@printf "  $(GREEN)demo$(RESET)               執行所有展示 (上傳 → 搜尋)\n"
	@printf "  $(GREEN)demo-upload$(RESET)        展示：上傳政策到 File Search Store\n"
	@printf "  $(GREEN)demo-search$(RESET)        展示：搜尋並檢索政策\n"
	@printf "  $(GREEN)demo-workflow$(RESET)      展示：完整端對端工作流程\n\n"

	@printf "$(BOLD)🧹 清理$(RESET)\n"
	@printf "  $(GREEN)clean$(RESET)              移除快取、__pycache__、覆蓋率報告\n"
	@printf "  $(GREEN)clean-stores$(RESET)       刪除所有 File Search Store (⚠️  重新開始)\n\n"

	@printf "$(BOLD)📚 參考資料$(RESET)\n"
	@printf "  $(GREEN)docs$(RESET)               檢視文件\n"
	@printf "  $(GREEN)help$(RESET)               顯示此說明訊息\n\n"

setup: install
	@printf "\n$(GREEN)✓ 環境設定完成$(RESET)\n\n"
	@printf "$(BOLD)下一步：$(RESET)\n"
	@printf "  1. 複製 .env.example 到 .env\n"
	@printf "       $(BLUE)cp .env.example .env$(RESET)\n\n"
	@printf "  2. 將您的 GOOGLE_API_KEY 新增到 .env\n\n"
	@printf "  3. 執行互動式網頁介面\n"
	@printf "       $(BLUE)make dev$(RESET)\n\n"
	@printf "$(BOLD)第一次設定？$(RESET)\n"
	@printf "  執行上傳展示以建立並填入 File Search Store：\n"
	@printf "       $(BLUE)make demo-upload$(RESET)\n\n"

install:
	@printf "$(BOLD)正在安裝相依套件...$(RESET)\n"
	pip install -e . > /dev/null 2>&1
	pip install -r requirements.txt > /dev/null 2>&1
	@printf "$(GREEN)✓ 安裝完成$(RESET)\n"

dev:
	@printf "\n$(BOLD)🚀 正在啟動 ADK 網頁介面...$(RESET)\n\n"
	@printf "$(BLUE)http://localhost:8000$(RESET)\n\n"
	@printf "介面即將在您的瀏覽器中開啟。\n"
	@printf "按 Ctrl+C 停止伺服器。\n\n"
	adk web

test:
	@printf "\n$(BOLD)正在執行測試並計算覆蓋率...$(RESET)\n\n"
	pytest tests/ -v --cov=policy_navigator --cov-report=html
	@printf "\n$(GREEN)✓ 所有測試通過！$(RESET)\n"
	@printf "$(BLUE)覆蓋率報告：htmlcov/index.html$(RESET)\n\n"

test-unit:
	@printf "$(BOLD)正在執行單元測試...$(RESET)\n\n"
	pytest tests/ -v -k "not integration" --cov=policy_navigator
	@printf "\n$(GREEN)✓ 單元測試完成$(RESET)\n\n"

test-int:
	@printf "$(BOLD)正在執行整合測試...$(RESET)\n\n"
	pytest tests/ -v -k "integration" --cov=policy_navigator
	@printf "\n$(GREEN)✓ 整合測試完成$(RESET)\n\n"

clean:
	@printf "$(BOLD)正在清理 artifacts...$(RESET)\n"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	@printf "$(GREEN)✓ 清理完成$(RESET)\n"
	@printf "  已移除：__pycache__, *.pyc, .egg-info, .pytest_cache, coverage reports\n\n"

clean-stores:
	@printf "\n$(BOLD)$(YELLOW)⚠️  警告：正在刪除所有 File Search Store...$(RESET)\n"
	@printf "這將讓您從完全乾淨的狀態重新開始。\n\n"
	@read -p "您確定嗎？(輸入 'yes' 確認)： " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		printf "$(YELLOW)正在刪除 File Search Store...$(RESET)\n"; \
		python scripts/cleanup_stores.py; \
		printf "$(GREEN)✓ 清理完成$(RESET)\n\n"; \
	else \
		printf "$(BLUE)已取消$(RESET)\n\n"; \
	fi

demo: demo-upload demo-search
	@printf "$(GREEN)✓ 所有展示完成！$(RESET)\n"
	@printf "下一步：嘗試 $(BLUE)make demo-workflow$(RESET) 進行完整端對端工作流程\n\n"

demo-upload:
	@printf "\n$(BOLD)📤 展示：上傳政策到 File Search$(RESET)\n"
	@printf "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)\n\n"
	python demos/demo_upload.py
	@printf "\n$(GREEN)✓ 上傳展示完成$(RESET)\n\n"

demo-search:
	@printf "\n$(BOLD)🔍 展示：搜尋並檢索政策$(RESET)\n"
	@printf "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)\n\n"
	python demos/demo_search.py
	@printf "\n$(GREEN)✓ 搜尋展示完成$(RESET)\n\n"

demo-workflow:
	@printf "\n$(BOLD)🔄 展示：完整端對端工作流程$(RESET)\n"
	@printf "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)\n\n"
	python demos/demo_full_workflow.py
	@printf "\n$(GREEN)✓ 工作流程展示完成$(RESET)\n\n"

lint:
	@printf "$(BOLD)正在執行程式碼品質檢查...$(RESET)\n\n"
	@printf "$(YELLOW)正在使用 ruff 檢查...$(RESET)\n"
	ruff check policy_navigator tests
	@printf "$(GREEN)✓ Ruff 通過$(RESET)\n\n"
	@printf "$(YELLOW)正在使用 black 檢查格式...$(RESET)\n"
	black --check policy_navigator tests
	@printf "$(GREEN)✓ Black 檢查通過$(RESET)\n\n"
	@printf "$(YELLOW)正在使用 mypy 進行型別檢查...$(RESET)\n"
	mypy policy_navigator --ignore-missing-imports
	@printf "$(GREEN)✓ MyPy 通過$(RESET)\n\n"
	@printf "$(GREEN)✓ 所有品質檢查通過！$(RESET)\n\n"

format:
	@printf "$(BOLD)正在自動格式化程式碼...$(RESET)\n\n"
	black policy_navigator tests
	ruff check --fix policy_navigator tests
	@printf "$(GREEN)✓ 格式化完成$(RESET)\n\n"

docs:
	@printf "\n$(BOLD)📚 文件$(RESET)\n\n"
	@printf "$(YELLOW)可用文件：$(RESET)\n"
	@printf "  • $(BLUE)README.md$(RESET) - 專案概覽與快速入門\n"
	@printf "  • $(BLUE)docs/architecture.md$(RESET) - 系統設計與元件\n"
	@printf "  • $(BLUE)docs/roi_calculator.md$(RESET) - 企業 ROI 分析\n"
	@printf "  • $(BLUE)docs/deployment_guide.md$(RESET) - 生產環境部署\n\n"
	@printf "$(YELLOW)正在開啟 README.md...$(RESET)\n\n"
	open README.md || xdg-open README.md

.DEFAULT_GOAL := help

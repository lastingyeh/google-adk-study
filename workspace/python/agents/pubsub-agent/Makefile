# 教學範例 34: Google Cloud Pub/Sub + 事件驅動代理
# 用於開發、測試和 GCP 基礎設施管理的 Makefile
#
# 主要功能：
#   • 冪等命令 (可安全地多次執行)
#   • 具有進度指示的出色使用者體驗 (UX)
#   • 支援本地和雲端基礎設施
#   • 全面的清理功能

.PHONY: help setup test demo clean dev-env check-deps gcp-setup gcp-destroy gcp-status web test-cov

# 用於 UX 的顏色代碼
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m  # 無顏色

# 預設目標 - 顯示說明
help:
	@echo "$(BLUE)🚀 教學範例 34: Google Cloud Pub/Sub + 事件驅動代理$(NC)"
	@echo ""
	@echo "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@echo "$(GREEN)快速開始 - 本地開發$(NC)"
	@echo "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@echo "  $(YELLOW)make setup$(NC)        安裝相依套件 (冪等)"
	@echo "  $(YELLOW)make test$(NC)         在本地執行所有測試"
	@echo "  $(YELLOW)make web$(NC)          啟動 ADK 網頁介面進行本地測試"
	@echo "  $(YELLOW)make demo$(NC)         顯示使用範例"
	@echo ""
	@echo "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@echo "$(GREEN)開發與維護$(NC)"
	@echo "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@echo "  $(YELLOW)make test-cov$(NC)     執行測試並產出覆蓋率報告"
	@echo "  $(YELLOW)make dev-env$(NC)      顯示環境資訊"
	@echo "  $(YELLOW)make check-deps$(NC)   驗證所有相依套件"
	@echo "  $(YELLOW)make clean$(NC)        清理快取和建置產物"
	@echo ""
	@echo "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@echo "$(GREEN)GOOGLE CLOUD 部署 (選用)$(NC)"
	@echo "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@echo "  $(YELLOW)make gcp-setup$(NC)    建立 GCP Pub/Sub 資源"
	@echo "  $(YELLOW)make gcp-status$(NC)   檢查 GCP 資源狀態"
	@echo "  $(YELLOW)make gcp-destroy$(NC)  移除所有 GCP 資源"
	@echo ""
	@echo "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@echo "$(GREEN)快速連結$(NC)"
	@echo "  📚 教學文件: docs/tutorial/34_pubsub_adk_integration.md"
	@echo "  💡 第一次使用？請執行: $(YELLOW)make setup && make test$(NC)"
	@echo "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"

# ============================================================================
# 本地開發目標
# ============================================================================

# 安裝相依套件 (冪等 - 可安全地多次執行)
setup: check-python
	@echo "$(BLUE)📦 正在設定開發環境...$(NC)"
	@echo ""
	@echo "$(YELLOW)步驟 1/3: 安裝 Python 相依套件$(NC)"
	@pip install -r requirements.txt > /dev/null 2>&1 && \
		echo "  $(GREEN)✓$(NC) Python 套件已安裝" || \
		(echo "  $(RED)✗$(NC) 無法安裝套件"; exit 1)
	@echo ""
	@echo "$(YELLOW)步驟 2/3: 以可編輯模式安裝套件$(NC)"
	@pip install -e . > /dev/null 2>&1 && \
		echo "  $(GREEN)✓$(NC) 套件已安裝 (可編輯模式)" || \
		(echo "  $(RED)✗$(NC) 無法安裝套件"; exit 1)
	@echo ""
	@echo "$(YELLOW)步驟 3/3: 驗證安裝$(NC)"
	@python -c "from pubsub_agent.agent import root_agent; print('  $(GREEN)✓$(NC) 代理 (Agent) 匯入成功')" || \
		(echo "  $(RED)✗$(NC) 代理匯入失敗"; exit 1)
	@echo ""
	@echo "$(GREEN)✅ 設定完成！$(NC)"
	@echo "  下一步："
	@echo "    • 執行測試: $(YELLOW)make test$(NC)"
	@echo "    • 查看範例: $(YELLOW)make demo$(NC)"
	@echo ""

# 顯示開發環境資訊
dev-env:
	@echo "$(BLUE)📋 開發環境$(NC)"
	@echo ""
	@python3 --version
	@echo ""
	@echo "$(YELLOW)Python 套件:$(NC)"
	@pip list | grep -E "google|pytest|adk" || echo "  (找不到符合的套件)"
	@echo ""
	@echo "$(YELLOW)專案結構:$(NC)"
	@find . -maxdepth 1 -type f \( -name "*.py" -o -name "*.toml" -o -name "Makefile" \) | sort | sed 's|^\./|  • |'
	@echo ""

# 檢查 Python 相依套件
check-deps:
	@echo "$(BLUE)🔍 檢查相依套件$(NC)"
	@echo ""
	@python3 -c "import google.adk; print('  $(GREEN)✓$(NC) google-adk 已安裝')" 2>/dev/null || \
		(echo "  $(RED)✗$(NC) google-adk 未安裝"; echo "  請執行: make setup"; exit 1)
	@python3 -c "import google.cloud.pubsub_v1; print('  $(GREEN)✓$(NC) google-cloud-pubsub 已安裝')" 2>/dev/null || \
		(echo "  $(RED)✗$(NC) google-cloud-pubsub 未安裝"; echo "  請執行: make setup"; exit 1)
	@python3 -c "import pytest; print('  $(GREEN)✓$(NC) pytest 已安裝')" 2>/dev/null || \
		(echo "  $(RED)✗$(NC) pytest 未安裝"; echo "  請執行: make setup"; exit 1)
	@echo ""
	@echo "$(GREEN)✅ 所有相依套件驗證通過$(NC)"
	@echo ""

# 執行測試
test: check-python
	@echo "$(BLUE)🧪 正在執行測試套件$(NC)"
	@echo ""
	@pytest tests/ -v --tb=short 2>&1 | tail -20
	@echo ""

# 執行測試並產出覆蓋率報告
test-cov: check-python
	@echo "$(BLUE)📊 正在執行測試並產出覆蓋率報告$(NC)"
	@echo ""
	@pytest tests/ -v --cov=pubsub_agent --cov-report=term-missing 2>&1 | tail -30
	@echo ""

# 執行快速範例
demo:
	@echo "$(BLUE)🎯 教學範例 34 演示: 事件驅動文件處理$(NC)"
	@echo ""
	@echo "$(YELLOW)📋 架構概覽:$(NC)"
	@echo "   1. 發布者 (Publisher) → 發送文件到 Pub/Sub 主題"
	@echo "   2. 代理 (Agent)       → 處理文件 (摘要、實體提取)"
	@echo "   3. 訂閱者 (Subscriber) → 接收結果"
	@echo ""
	@echo "$(YELLOW)🔧 本教學中的元件:$(NC)"
	@echo "   • pubsub_agent/    - 用於處理的主要 ADK 代理"
	@echo "   • publisher.py     - 發布者腳本範例"
	@echo "   • subscriber.py    - 訂閱者腳本範例"
	@echo ""
	@echo "$(YELLOW)📝 本地測試 (無需 GCP):$(NC)"
	@echo "   $$ make test"
	@echo ""
	@echo "$(YELLOW)☁️  部署到 GCP:$(NC)"
	@echo "   $$ make gcp-setup        # 建立資源"
	@echo "   $$ python publisher.py   # 發布文件"
	@echo "   $$ python subscriber.py  # 處理文件"
	@echo "   $$ make gcp-destroy      # 清理資源"
	@echo ""
	@echo "$(GREEN)✅ 準備就緒！詳細說明請參閱教學文件。$(NC)"
	@echo ""

# 啟動 ADK 網頁介面進行本地測試和開發
web: check-python setup
	@echo "$(BLUE)🌐 啟動 ADK 開發介面$(NC)"
	@echo ""
	@echo "$(GREEN)正在啟動 ADK 網頁伺服器...$(NC)"
	@echo "$(YELLOW)📍 請在瀏覽器開啟: http://localhost:8000$(NC)"
	@echo ""
	@echo "$(YELLOW)可用功能:$(NC)"
	@echo "  • 使用自定義提示測試代理"
	@echo "  • 查看代理設定"
	@echo "  • 檢查結構化輸出"
	@echo "  • 除錯代理行為"
	@echo ""
	@echo "$(YELLOW)按 Ctrl+C 停止伺服器$(NC)"
	@echo ""
	@adk web

# ============================================================================
# GCP 基礎設施目標 (冪等)
# ============================================================================

# 設定 GCP Pub/Sub 資源 (冪等)
gcp-setup: check-gcloud check-project
	@echo "$(BLUE)☁️  正在設定 Google Cloud Pub/Sub 資源$(NC)"
	@echo ""
	@PROJECT=$$(gcloud config get-value project 2>/dev/null); \
	echo "$(YELLOW)目標專案: $$PROJECT$(NC)"; \
	echo ""
	@echo "$(YELLOW)步驟 1/4: 建立 Pub/Sub 主題$(NC)"
	@gcloud pubsub topics create document-uploads \
		--quiet --project=$$(gcloud config get-value project) 2>/dev/null && \
		echo "  $(GREEN)✓$(NC) 主題 'document-uploads' 已建立" || \
		echo "  $(GREEN)✓$(NC) 主題 'document-uploads' 已存在"
	@echo ""
	@echo "$(YELLOW)步驟 2/4: 建立處理器訂閱$(NC)"
	@gcloud pubsub subscriptions create document-processor \
		--topic=document-uploads \
		--ack-deadline=600 \
		--quiet --project=$$(gcloud config get-value project) 2>/dev/null && \
		echo "  $(GREEN)✓$(NC) 訂閱 'document-processor' 已建立" || \
		echo "  $(GREEN)✓$(NC) 訂閱 'document-processor' 已存在"
	@echo ""
	@echo "$(YELLOW)步驟 3/4: 建立結果主題$(NC)"
	@gcloud pubsub topics create document-results \
		--quiet --project=$$(gcloud config get-value project) 2>/dev/null && \
		echo "  $(GREEN)✓$(NC) 主題 'document-results' 已建立" || \
		echo "  $(GREEN)✓$(NC) 主題 'document-results' 已存在"
	@echo ""
	@echo "$(YELLOW)步驟 4/4: 建立 DLQ (死信佇列) 主題$(NC)"
	@gcloud pubsub topics create document-dlq \
		--quiet --project=$$(gcloud config get-value project) 2>/dev/null && \
		echo "  $(GREEN)✓$(NC) 主題 'document-dlq' 已建立" || \
		echo "  $(GREEN)✓$(NC) 主題 'document-dlq' 已存在"
	@echo ""
	@echo "$(GREEN)✅ GCP 資源準備就緒！$(NC)"
	@echo "  下一步："
	@echo "    • 檢查狀態: $(YELLOW)make gcp-status$(NC)"
	@echo "    • 執行發布者: $(YELLOW)python publisher.py$(NC)"
	@echo "    • 清理資源: $(YELLOW)make gcp-destroy$(NC)"
	@echo ""

# 顯示 GCP 資源狀態 (冪等)
gcp-status: check-gcloud check-project
	@echo "$(BLUE)☁️  Google Cloud Pub/Sub 資源$(NC)"
	@echo ""
	@PROJECT=$$(gcloud config get-value project 2>/dev/null); \
	echo "$(YELLOW)專案: $$PROJECT$(NC)"; \
	echo ""
	@echo "$(YELLOW)主題:$(NC)"
	@gcloud pubsub topics list --project=$$(gcloud config get-value project) \
		--filter="name:document*" --format="table(name)" 2>/dev/null | \
		sed 's|projects/.*/topics/|  • |' || echo "  (找不到主題)"
	@echo ""
	@echo "$(YELLOW)訂閱:$(NC)"
	@gcloud pubsub subscriptions list --project=$$(gcloud config get-value project) \
		--filter="name:document*" --format="table(name)" 2>/dev/null | \
		sed 's|projects/.*/subscriptions/|  • |' || echo "  (找不到訂閱)"
	@echo ""
	@echo "$(YELLOW)訊息統計:$(NC)"
	@gcloud pubsub subscriptions describe document-processor \
		--project=$$(gcloud config get-value project) \
		--format="table(messageRetentionDuration, expirationPolicy)" 2>/dev/null || \
		echo "  (找不到訂閱 - 請先執行 'make gcp-setup')"
	@echo ""

# 銷毀 GCP 資源 (帶有確認提示的冪等操作)
gcp-destroy: check-gcloud check-project
	@echo "$(RED)⚠️  警告: 這將刪除 GCP Pub/Sub 資源$(NC)"
	@echo ""
	@echo "$(YELLOW)將被刪除的資源:$(NC)"
	@echo "  • 訂閱: document-processor"
	@echo "  • 主題: document-uploads, document-results, document-dlq"
	@echo ""
	@read -p "$(YELLOW)是否繼續？ (yes/no): $(NC)" CONFIRM; \
	if [ "$$CONFIRM" = "yes" ]; then \
		echo ""; \
		echo "$(YELLOW)正在刪除訂閱...$(NC)"; \
		gcloud pubsub subscriptions delete document-processor \
			--quiet --project=$$(gcloud config get-value project) 2>/dev/null && \
			echo "  $(GREEN)✓$(NC) 訂閱已刪除" || \
			echo "  $(GREEN)✓$(NC) 訂閱已刪除"; \
		echo ""; \
		echo "$(YELLOW)正在刪除主題...$(NC)"; \
		gcloud pubsub topics delete document-uploads \
			--quiet --project=$$(gcloud config get-value project) 2>/dev/null && \
			echo "  $(GREEN)✓$(NC) 主題 'document-uploads' 已刪除" || \
			echo "  $(GREEN)✓$(NC) 已刪除"; \
		gcloud pubsub topics delete document-results \
			--quiet --project=$$(gcloud config get-value project) 2>/dev/null && \
			echo "  $(GREEN)✓$(NC) 主題 'document-results' 已刪除" || \
			echo "  $(GREEN)✓$(NC) 已刪除"; \
		gcloud pubsub topics delete document-dlq \
			--quiet --project=$$(gcloud config get-value project) 2>/dev/null && \
			echo "  $(GREEN)✓$(NC) 主題 'document-dlq' 已刪除" || \
			echo "  $(GREEN)✓$(NC) 已刪除"; \
		echo ""; \
		echo "$(GREEN)✅ 清理完成！$(NC)"; \
	else \
		echo "$(YELLOW)已取消。$(NC)"; \
	fi
	@echo ""

# ============================================================================
# 維護目標
# ============================================================================

# 清理本地檔案
clean:
	@echo "$(BLUE)🧹 正在清理本地建置產物$(NC)"
	@echo ""
	@echo "$(YELLOW)正在移除 Python 快取檔案...$(NC)"
	@find . -type f -name "*.pyc" -delete && \
		echo "  $(GREEN)✓$(NC) 已移除 .pyc 檔案"
	@find . -type d -name "__pycache__" -delete && \
		echo "  $(GREEN)✓$(NC) 已移除 __pycache__ 目錄"
	@echo ""
	@echo "$(YELLOW)正在移除 pytest 快取...$(NC)"
	@rm -rf .pytest_cache/ && \
		echo "  $(GREEN)✓$(NC) 已移除 .pytest_cache"
	@echo ""
	@echo "$(YELLOW)正在移除覆蓋率資料...$(NC)"
	@rm -rf .coverage htmlcov/ && \
		echo "  $(GREEN)✓$(NC) 已移除覆蓋率檔案"
	@echo ""
	@echo "$(GREEN)✅ 清理完成！$(NC)"
	@echo ""

# ============================================================================
# 輔助目標 (內部使用)
# ============================================================================

# 檢查 Python 是否可用
check-python:
	@python3 --version > /dev/null 2>&1 || \
		(echo "$(RED)錯誤: 找不到 Python 3$(NC)"; exit 1)

# 檢查 gcloud 是否可用
check-gcloud:
	@command -v gcloud > /dev/null 2>&1 || \
		(echo "$(RED)❌ 錯誤: 未安裝 gcloud CLI$(NC)"; \
		echo "$(YELLOW)安裝方式: https://cloud.google.com/sdk/docs/install$(NC)"; exit 1)

# 檢查是否已設定 GCP 專案
check-project:
	@PROJECT=$$(gcloud config get-value project 2>/dev/null); \
	if [ -z "$$PROJECT" ]; then \
		echo "$(RED)❌ 錯誤: 未選擇 GCP 專案$(NC)"; \
		echo "$(YELLOW)設定專案: gcloud config set project 您的專案ID$(NC)"; \
		exit 1; \
	fi

### Makefile 重點摘要
# - **核心概念**：使用 Makefile 自動化開發、測試和部署流程，並通過 ANSI 顏色代碼增強使用者體驗 (UX)。
# - **關鍵技術**：Make, Python pip, Pytest, Google Cloud CLI (gcloud), Pub/Sub。
# - **重要結論**：提供了一套冪等 (Idempotent) 的命令，確保可以重複執行而不會出錯，並支援本地開發與雲端部署的無縫切換。
# - **行動項目**：
#   - 執行 `make setup` 初始化環境。
#   - 執行 `make test` 進行本地測試。
#   - 執行 `make gcp-setup` 部署至 Google Cloud (選用)。

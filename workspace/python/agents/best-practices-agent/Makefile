# 教學 25：最佳實踐 - 生產就緒代理 (Production-Ready Agent)
# 展示生產模式、安全性與最佳化

.PHONY: help setup dev test test-cov clean demo

# 預設目標 - 顯示說明
help:
	@echo "🚀 教學 25：最佳實踐 - 生產就緒代理 (Production-Ready Agent)"
	@echo ""
	@echo "快速開始指令："
	@echo "  make setup     - 安裝依賴項目"
	@echo "  make dev       - 啟動最佳實踐代理"
	@echo "  make demo      - 顯示示範提示詞與用法"
	@echo ""
	@echo "進階指令："
	@echo "  make test      - 執行所有測試"
	@echo "  make test-cov  - 執行測試並產生覆蓋率報告"
	@echo "  make clean     - 清理產生的檔案"
	@echo ""
	@echo "💡 第一次使用？請執行：make setup && make dev"

# 設定環境
setup:
	@echo "📦 正在安裝依賴項目..."
	pip install -r requirements.txt
	pip install -e .
	@echo "✅ 設定完成！執行 'make dev' 以啟動代理。"

# 啟動開發伺服器
dev: check-env
	@echo "🤖 正在啟動最佳實踐代理..."
	@echo "📱 請在瀏覽器中開啟 http://localhost:8000"
	@echo "🎯 從下拉選單中選擇 'best_practices_agent'"
	@echo ""
	@echo "💡 嘗試這些生產情境："
	@echo "   • '驗證此電子郵件：user@example.com' (Validate this email: user@example.com)"
	@echo "   • '使用重試邏輯處理訂單：ORD-123' (Process order with retry logic: ORD-123)"
	@echo "   • '顯示系統健康指標' (Show me the system health metrics)"
	@echo "   • '展示故障服務的斷路器機制' (Demonstrate circuit breaker with failing service)"
	@echo "   • '批次處理這些項目：A, B, C' (Batch process these items: A, B, C)"
	@echo ""
	adk web

# 執行所有測試
test: check-env
	@echo "🧪 正在執行測試..."
	pytest tests/ -v --tb=short

# 執行含覆蓋率的測試
test-cov: check-env
	@echo "📊 正在執行含覆蓋率的測試..."
	pytest tests/ --cov=best_practices_agent --cov-report=html --cov-report=term
	@echo "📈 覆蓋率報告已產生於 htmlcov/"

# 顯示示範提示詞
demo:
	@echo "🎯 最佳實踐代理示範"
	@echo ""
	@echo "生產模式示範："
	@echo ""
	@echo "1. 輸入驗證 (Input Validation)："
	@echo "   'Validate this email: user@example.com'"
	@echo "   'Validate this email: invalid-email'"
	@echo ""
	@echo "2. 錯誤處理與重試 (Error Handling & Retry)："
	@echo "   'Process order with retry: ORD-123'"
	@echo "   'Handle failing service call gracefully'"
	@echo ""
	@echo "3. 斷路器 (Circuit Breaker)："
	@echo "   'Call external service with circuit breaker'"
	@echo "   'Check circuit breaker status'"
	@echo ""
	@echo "4. 效能最佳化 (Performance Optimization)："
	@echo "   'Cache this data: user preferences'"
	@echo "   'Batch process: item1, item2, item3'"
	@echo ""
	@echo "5. 監控與健康 (Monitoring & Health)："
	@echo "   'Show system health metrics'"
	@echo "   'Display performance statistics'"
	@echo ""
	@echo "💡 執行：make dev"

# 清理快取檔案
clean:
	@echo "🧹 正在清理..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .coverage -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ 清理完成！"

# 檢查環境 (內部使用)
check-env:
	@if [ -z "$$GOOGLE_API_KEY" ] && [ -z "$$GOOGLE_APPLICATION_CREDENTIALS" ]; then \
		echo "❌ 錯誤：未設定驗證"; \
		echo ""; \
		echo "請選擇以下其中一種驗證方式："; \
		echo ""; \
		echo "🔑 方法 1 - API 金鑰 (Gemini API)："; \
		echo "   export GOOGLE_API_KEY=your_api_key_here"; \
		echo "   於此處取得免費金鑰：https://aistudio.google.com/app/apikey"; \
		echo ""; \
		echo "🔐 方法 2 - 服務帳戶 (VertexAI)："; \
		echo "   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json"; \
		echo "   export GOOGLE_CLOUD_PROJECT=your_project_id"; \
		echo "   於此處建立憑證：https://console.cloud.google.com/iam-admin/serviceaccounts"; \
		echo ""; \
		exit 1; \
	fi

# 重點摘要
# - **核心概念**：自動化腳本管理專案的建置、測試與執行流程。
# - **關鍵技術**：Makefile, pip, pytest, adk CLI。
# - **重要結論**：提供標準化的指令介面，簡化開發者的操作步驟。
# - **行動項目**：確保環境變數 GOOGLE_API_KEY 或 GOOGLE_APPLICATION_CREDENTIALS 已正確設定。

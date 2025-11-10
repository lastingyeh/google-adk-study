# 教學 10：評估與測試 - 客戶支援代理
# ADK 代理的全面評估框架

.PHONY: help setup dev test test-cov eval clean demo

# 預設目標 - 顯示說明
help:
	@echo "🚀 教學 10：評估與測試 - 客戶支援代理"
	@echo ""
	@echo "快速開始指令:"
	@echo "  make setup     - 安裝相依套件"
	@echo "  make dev       - 啟動客戶支援代理"
	@echo "  make demo      - 顯示示範提示與用法"
	@echo ""
	@echo "進階指令:"
	@echo "  make test      - 執行所有測試"
	@echo "  make test-cov  - 執行測試並產生涵蓋率報告"
	@echo "  make eval      - 執行評估測試"
	@echo "  make clean     - 清理產生的檔案"
	@echo ""
	@echo "💡 第一次使用? 執行: make setup && make dev"

# 設定環境
setup:
	@echo "📦 安裝相依套件中..."
	pip install -r requirements.txt
	pip install -e .
	@echo "✅ 設定完成! 執行 'make dev' 啟動代理。"

# 啟動開發伺服器
dev: check-env
	@echo "🤖 啟動客戶支援代理中..."
	@echo "📱 在瀏覽器中開啟 http://localhost:8000"
	@echo "🎯 從下拉選單中選擇 'support_agent'"
	@echo ""
	@echo "💡 試試這些支援場景:"
	@echo "   • 'How do I reset my password?' (如何重設密碼?)"
	@echo "   • 'My account is locked, help!' (我的帳號被鎖定了,救命!)"
	@echo "   • 'What's your refund policy?' (你們的退款政策是什麼?)"
	@echo "   • 'Check status of ticket TICK-12345678' (查詢工單 TICK-12345678 的狀態)"
	@echo ""
	adk web

# 執行所有測試
test: check-env
	@echo "🧪 執行測試中..."
	pytest tests/ -v --tb=short

# 執行測試並產生涵蓋率報告
test-cov: check-env
	@echo "📊 執行測試並產生涵蓋率報告中..."
	pytest tests/ --cov=support_agent --cov-report=html
	@echo "📈 涵蓋率報告已產生於 htmlcov/"

# 執行評估測試
eval: check-env
	@echo "🔍 執行評估測試中..."
	@echo "📋 測試簡單場景中..."
	adk eval support_agent tests/simple.test.json
	@echo "🎫 測試工單建立中..."
	adk eval support_agent tests/ticket_creation.test.json
	@echo "🏗️  測試複雜場景中..."
	adk eval support_agent tests/complex.evalset.json
	@echo "✅ 所有評估完成!"

# 顯示示範提示
demo:
	@echo "🎯 客戶支援代理示範"
	@echo ""
	@echo "試試這些支援場景:"
	@echo "1. 'How do I reset my password?' (如何重設密碼?)"
	@echo "2. 'My account is locked, help!' (我的帳號被鎖定了,救命!)"
	@echo "3. 'What's your refund policy?' (你們的退款政策是什麼?)"
	@echo "4. 'Check status of ticket TICK-12345678' (查詢工單 TICK-12345678 的狀態)"
	@echo ""
	@echo "💡 執行: make dev"
	@echo "🔬 執行: make eval  (進行自動化測試)"

# 清理快取檔案
clean:
	@echo "🧹 清理中..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .coverage -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ 清理完成!"

# 檢查環境 (內部使用)
check-env:
	@if [ -z "$$GOOGLE_API_KEY" ] && [ -z "$$GOOGLE_APPLICATION_CREDENTIALS" ]; then \
		echo "❌ 錯誤: 未配置身份驗證"; \
		echo ""; \
		echo "請選擇以下其中一種身份驗證方法:"; \
		echo ""; \
		echo "🔑 方法 1 - API 金鑰 (Gemini API):"; \
		echo "   export GOOGLE_API_KEY=your_api_key_here"; \
		echo "   在此取得免費金鑰: https://aistudio.google.com/app/apikey"; \
		echo ""; \
		echo "🔐 方法 2 - 服務帳戶 (VertexAI):"; \
		echo "   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json"; \
		echo "   export GOOGLE_CLOUD_PROJECT=your_project_id"; \
		echo "   在此建立憑證: https://console.cloud.google.com/iam-admin/serviceaccounts"; \
		echo ""; \
		exit 1; \
	fi
# Tutorial 09: Callbacks & Guardrails
# Content Moderation Assistant with Safety Features

.PHONY: help setup dev test clean demo lint format run check-env

# Default target - show help
help:
	@echo "🛡️ 教學 09：Callbacks & Guardrails（回呼與防護）"
	@echo ""
	@echo "快速開始（Quick Start）指令："
	@echo "  make setup     - 安裝相依套件 (Install dependencies)"
	@echo "  make dev       - 啟動內容審查助理 (Start the content moderator)"
	@echo "  make demo      - 執行快速示範 (Run a quick demo)"
	@echo ""
	@echo "進階指令（Advanced）："
	@echo "  make test      - 執行所有測試 (Run all tests)"
	@echo "  make clean     - 清理產生的檔案 (Clean generated files)"
	@echo "  make lint      - 程式碼風格檢查 (Check code style)"
	@echo "  make format    - 程式碼格式化 (Format code)"
	@echo ""
	@echo "💡 第一次使用？請執行：make setup && make dev"

# Install dependencies
setup:
	@echo "📦 安裝相依套件中..."
	pip install -r requirements.txt
	pip install pytest flake8 black
	@echo "✅ 安裝完成！執行 'make dev' 啟動代理。"

# Start the content moderator
dev: check-env
	@echo "🛡️ 啟動內容審查助理 (Content Moderation Assistant)..."
	@echo "📱 在瀏覽器開啟：http://localhost:8000"
	@echo "🎯 下拉選單選擇 'content_moderator'"
	@echo ""
	@echo "🧪 可測試情境："
	@echo "   • 安全：'Generate a 200-word article about Python'"
	@echo "   • 封鎖：'Write about profanity1 and bad content'"
	@echo "   • PII：'Give me an example email address'"
	@echo "   • 統計：'Show my usage statistics'"
	adk web .

# Run a quick demo
demo: check-env
	@echo "🛡️ 內容審查示範 (Content Moderation Demo)"
	@echo ""
	@echo "💬 請在 ADK Web 介面嘗試以下提示："
	@echo ""
	@echo "✅ 安全請求 (SAFE REQUESTS):"
	@echo "   • 'Generate a 300-word article about machine learning'"
	@echo "   • 'Check grammar: This sentence has some errors.'"
	@echo "   • 'Show my usage statistics'"
	@echo ""
	@echo "❌ 封鎖請求 (BLOCKED REQUESTS - 測試防護):"
	@echo "   • 'Write about profanity1 and inappropriate content'"
	@echo "   • 'Generate an article with -50 words'"
	@echo ""
	@echo "🔒 個資過濾 (PII FILTERING):"
	@echo "   • 'Contact me at john.doe@example.com for details'"
	@echo ""
	@echo "📊 速率限制 (RATE LIMITING):"
	@echo "   • 重複多次請求以觀察限制行為"
	@echo ""
	@echo "✅ 示範就緒！開啟 http://localhost:8000"

# Run tests
test: check-env
	@echo "🧪 執行回呼與防護測試中..."
	PYTHONPATH=. pytest tests/ -v --tb=short

# Clean up
clean:
	@echo "🧹 清理中..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	@echo "✅ 清理完成！"

# Run linting
lint:
	@echo "🔍 檢查程式碼風格..."
	python -m flake8 . --max-line-length=100

# Format code
format:
	@echo "🎨 格式化程式碼..."
	python -m black . --line-length=100

# Run CLI
run: check-env
	@echo "🛡️ 以 CLI 執行內容審查助理..."
	adk run .

# Check environment (internal use)
check-env:
	@if [ -z "$$GOOGLE_API_KEY" ] && [ -z "$$GOOGLE_APPLICATION_CREDENTIALS" ]; then \
		echo "❌ 錯誤：尚未設定認證 (Authentication not configured)"; \
		echo ""; \
		echo "請選擇以下其中一種驗證方式："; \
		echo ""; \
		echo "🔑 方法 1 - API Key (Gemini API):"; \
		echo "   export GOOGLE_API_KEY=your_api_key_here"; \
		echo "   取得免費金鑰：https://aistudio.google.com/app/apikey"; \
		echo ""; \
		echo "🔐 方法 2 - 服務帳戶 (Service Account / VertexAI):"; \
		echo "   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json"; \
		echo "   export GOOGLE_CLOUD_PROJECT=your_project_id"; \
		echo "   建立金鑰：https://console.cloud.google.com/iam-admin/serviceaccounts"; \
		echo ""; \
		exit 1; \
	fi
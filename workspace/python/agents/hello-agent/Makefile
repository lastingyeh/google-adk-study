# Tutorial 01: Hello World Agent
# Simple Makefile for getting started quickly

.PHONY: help setup dev test clean demo

# Default target - show help
help:
	@echo "🚀 教學 01：Hello World Agent"
	@echo ""
	@echo "快速開始指令 (Quick Start):"
	@echo "  make setup     - 安裝相依套件 (Install dependencies)"
	@echo "  make dev       - 啟動 hello 代理 (Start the hello agent)"
	@echo "  make demo      - 執行簡易示範 (Run a quick demo)"
	@echo ""
	@echo "進階指令 (Advanced):"
	@echo "  make test      - 執行所有測試 (Run all tests)"
	@echo "  make clean     - 清理產生檔案 (Clean up generated files)"
	@echo ""
	@echo "💡 第一次使用？請依序執行: make setup && make dev"

# Install dependencies
setup:
	@echo "📦 安裝相依套件中..."
	pip install -r requirements.txt
	pip install -e .
	@echo "✅ 安裝完成！執行 'make dev' 啟動代理。"

# Start the hello agent
dev: check-env
	@echo "🤖 正在啟動 Hello World Agent..."
	@echo "📱 請在瀏覽器開啟 http://localhost:8000"
	@echo "🎯 下拉選單選擇 'hello_agent'"
	adk web

# Run a quick demo
demo: check-env
	@echo "🧪 執行 Hello World 示範..."
	@echo ""
	@echo "💬 可在 ADK Web 介面嘗試以下提示詞："
	@echo "   • 'Hello! Who are you?' (你是誰)"
	@echo "   • 'What can you do?' (你能做什麼)"
	@echo "   • 'Tell me a fun fact' (給我一個有趣事實)"
	@echo ""
	@echo "✅ 示範已就緒！瀏覽 http://localhost:8000"

# Run tests
test: check-env
	@echo "🧪 執行測試中..."
	pytest tests/ -v --tb=short

# Clean up
clean:
	@echo "🧹 清理中..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	@echo "✅ 清理完成！"

# Check environment (internal use)
check-env:
	@if [ -z "$$GOOGLE_API_KEY" ] && [ -z "$$GOOGLE_APPLICATION_CREDENTIALS" ]; then \
		echo "❌ 錯誤：尚未設定驗證資訊 (Authentication not configured)"; \
		echo ""; \
		echo "請選擇以下其中一種驗證方式："; \
		echo ""; \
		echo "🔑 方式 1 - API Key (Gemini API)："; \
		echo "   export GOOGLE_API_KEY=你的_API_Key"; \
		echo "   申請金鑰：https://aistudio.google.com/app/apikey"; \
		echo ""; \
		echo "🔐 方式 2 - Service Account (VertexAI)："; \
		echo "   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json"; \
		echo "   export GOOGLE_CLOUD_PROJECT=your_project_id"; \
		echo "   建立憑證：https://console.cloud.google.com/iam-admin/serviceaccounts"; \
		echo ""; \
		exit 1; \
	fi
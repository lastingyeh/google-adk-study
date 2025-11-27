# 教學 27：第三方工具整合
# 示範 LangChain 和 CrewAI 工具與 ADK 的整合

.PHONY: help setup dev test clean demo

# 預設目標 - 顯示說明
help:
	@echo "🚀 教學 27：第三方工具整合"
	@echo ""
	@echo "快速開始指令："
	@echo "  make setup     - 安裝相依套件"
	@echo "  make dev       - 啟動代理程式"
	@echo "  make demo      - 顯示範例提示和用法"
	@echo ""
	@echo "進階指令："
	@echo "  make test      - 執行所有測試"
	@echo "  make clean     - 清理產生的檔案"
	@echo ""
	@echo "💡 第一次使用？執行：make setup && make dev"

# 設定環境
setup:
	@echo "📦 正在安裝相依套件..."
	pip install -r requirements.txt
	pip install -e .
	@echo "✅ 設定完成！執行 'make dev' 啟動代理程式。"

# 啟動開發伺服器
dev: check-env
	@echo "🤖 正在啟動第三方工具代理程式..."
	@echo "📱 在瀏覽器中開啟 http://localhost:8000"
	@echo "🎯 從下拉選單中選擇 'third_party_agent'"
	@echo ""
	@echo "💡 試試這些研究查詢："
	@echo "   • 'What is quantum computing?' (Wikipedia)"
	@echo "   • 'Latest AI developments this year' (Web search)"
	@echo "   • 'Tell me about Ada Lovelace' (Wikipedia)"
	@echo "   • 'Current news about space exploration' (Web search)"
	@echo "   • 'Show me the project structure' (Directory read)"
	@echo "   • 'Read the README file' (File read)"
	@echo ""
	adk web

# 執行所有測試
test: check-env
	@echo "🧪 正在執行測試..."
	pytest tests/ -v --tb=short

# 顯示範例提示
demo:
	@echo "🎯 第三方工具整合範例"
	@echo ""
	@echo "本教學示範："
	@echo "  ✅ LangChain Wikipedia 工具整合"
	@echo "  ✅ LangChain DuckDuckGo 網頁搜尋工具"
	@echo "  ✅ CrewAI DirectoryReadTool 整合"
	@echo "  ✅ CrewAI FileReadTool 整合"
	@echo "  ✅ 正確的匯入路徑 (google.adk.tools.langchain_tool)"
	@echo "  ✅ 使用 LangchainTool 和自訂函式進行工具包裝"
	@echo "  ✅ 任何工具都不需要 API 金鑰"
	@echo ""
	@echo "試試這些研究查詢："
	@echo "1. 'What is quantum computing?' (Wikipedia)"
	@echo "2. 'Latest AI developments this year' (Web search)"
	@echo "3. 'Tell me about Ada Lovelace' (Wikipedia)"
	@echo "4. 'Current news about space exploration' (Web search)"
	@echo "5. 'Show me the project structure' (Directory read)"
	@echo "6. 'Read the README file' (File read)"
	@echo ""
	@echo "💡 執行：make dev"
	@echo "🔬 執行：make test"

# 清理快取檔案
clean:
	@echo "🧹 正在清理..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .coverage -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ 清理完成！"

# 檢查環境 (內部使用)
check-env:
	@if [ -z "$$GOOGLE_API_KEY" ] && [ -z "$$GOOGLE_APPLICATION_CREDENTIALS" ]; then \
		echo "❌ 錯誤：未設定驗證"; \
		echo ""; \
		echo "選擇以下其中一種驗證方式："; \
		echo ""; \
		echo "🔑 方法 1 - API 金鑰 (Gemini API)："; \
		echo "   export GOOGLE_API_KEY=your_api_key_here"; \
		echo "   取得免費金鑰：https://aistudio.google.com/app/apikey"; \
		echo ""; \
		echo "🔐 方法 2 - 服務帳戶 (VertexAI)："; \
		echo "   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json"; \
		echo "   export GOOGLE_CLOUD_PROJECT=your_project_id"; \
		echo "   建立憑證：https://console.cloud.google.com/iam-admin/serviceaccounts"; \
		echo ""; \
		exit 1; \
	fi

# 重點摘要 (程式碼除外)
# - **核心概念**：自動化專案管理工具，簡化開發流程。
# - **關鍵技術**：Make, Shell Scripting, pip, adk CLI, pytest。
# - **重要結論**：提供標準化的指令介面 (`make setup`, `make dev`, `make test`)，降低開發門檻並確保環境一致性。
# - **行動項目**：執行 `make setup` 初始化專案，使用 `make dev` 啟動代理程式。

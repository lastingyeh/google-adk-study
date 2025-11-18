# 教學 19：成品與檔案管理
# 具備成品儲存功能的文件處理代理

.PHONY: help setup dev test clean demo

# 預設目標 - 顯示說明
help:
	@echo "🚀 教學 19：成品與檔案管理"
	@echo ""
	@echo "快速入門指令："
	@echo "  make setup     - 安裝依賴套件"
	@echo "  make dev       - 啟動成品代理"
	@echo "  make demo      - 執行文件處理演示"
	@echo ""
	@echo "進階指令："
	@echo "  make test      - 執行所有測試"
	@echo "  make clean     - 清理生成的檔案"
	@echo ""
	@echo "💡 第一次使用？請執行：make setup && make dev"

# 安裝依賴套件
setup:
	@echo "📦 正在安裝依賴套件..."
	pip install -r requirements.txt
	pip install -e .
	@echo "✅ 設定完成！請執行 'make dev' 啟動代理。"

# 啟動成品代理
dev: check-env
	@echo "🤖 正在啟動成品代理..."
	@echo "📱 在您的瀏覽器中開啟 http://localhost:8000"
	@echo "🎯 從下拉選單中選擇 'artifact_agent'"
	@echo "📄 嘗試以下提示："
	@echo "   • '處理此文件：[貼上文字]'"
	@echo "   • '顯示所有已儲存的成品'"
	@echo "   • '總結我剛儲存的文件'"
	adk web

# 執行文件處理演示
demo: check-env
	@echo "📄 正在執行文件處理演示..."
	@echo ""
	@echo "💬 在 ADK 網頁介面中嘗試以下提示："
	@echo "   1. '處理此文件：敏捷的棕色狐狸跳過懶惰的狗。這是一個用於測試成品儲存的範例文件。'"
	@echo "   2. '列出所有成品'"
	@echo "   3. '總結提取的文字'"
	@echo "   4. '將總結翻譯成西班牙文'"
	@echo "   5. '創建一份結合所有成品的最終報告'"
	@echo ""
	@echo "✅ 演示準備就緒！請開啟 http://localhost:8000"

# 執行測試
test: check-env
	@echo "🧪 正在執行測試..."
	pytest tests/ -v --tb=short --cov=artifact_agent --cov-report=term-missing

# 清理
clean:
	@echo "🧹 正在清理..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	rm -rf .coverage
	@echo "✅ 清理完成！"

# 檢查環境（內部使用）
check-env:
	@if [ -z "$$GOOGLE_API_KEY" ] && [ -z "$$GOOGLE_APPLICATION_CREDENTIALS" ]; then \
		echo "❌ 錯誤：未設定驗證"; \
		echo ""; \
		echo "請選擇以下其中一種驗證方法："; \
		echo ""; \
		echo "🔑 方法 1 - API 金鑰 (Gemini API):"; \
		echo "   export GOOGLE_API_KEY=your_api_key_here"; \
		echo "   請至此處獲取免費金鑰：https://aistudio.google.com/app/apikey"; \
		echo ""; \
		echo "🔐 方法 2 - 服務帳號 (VertexAI):"; \
		echo "   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json"; \
		echo "   export GOOGLE_CLOUD_PROJECT=your_project_id"; \
		echo "   請至此處創建憑證：https://console.cloud.google.com/iam-admin/serviceaccounts"; \
		echo ""; \
		exit 1; \
	fi

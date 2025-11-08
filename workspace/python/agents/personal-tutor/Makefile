# 教學 08: 狀態與記憶管理
# 具備完整狀態管理功能的個人學習導師

.PHONY: help setup dev test clean demo

# 預設目標 - 顯示說明
help:
	@echo "🚀 教學 08: 狀態與記憶管理"
	@echo ""
	@echo "快速開始指令:"
	@echo "  make setup     - 安裝相依套件"
	@echo "  make dev       - 啟動個人導師代理"
	@echo "  make demo      - 執行快速示範"
	@echo ""
	@echo "進階指令:"
	@echo "  make test      - 執行所有測試"
	@echo "  make clean     - 清理產生的檔案"
	@echo ""
	@echo "💡 第一次使用? 執行: make setup && make dev"

# 安裝相依套件
setup:
	@echo "📦 正在安裝相依套件..."
	pip install -r requirements.txt
	pip install -e .
	@echo "✅ 設定完成! 執行 'make dev' 啟動代理。"

# 啟動個人導師代理
dev: check-env
	@echo "🤖 正在啟動個人學習導師..."
	@echo "📱 在瀏覽器中開啟 http://localhost:8000"
	@echo "🎯 從下拉選單中選擇 'personal_tutor'"
	@echo ""
	@echo "💡 試試這些提示:"
	@echo "   • '將我的語言設為西班牙文,難度設為中級'"
	@echo "   • '開始學習 Python 類別'"
	@echo "   • '我的測驗得了 8 分,滿分 10 分'"
	@echo "   • '顯示我的學習進度'"
	@echo "   • '我學過哪些 Python 相關的內容?'"
	adk web

# 執行快速示範
demo: check-env
	@echo "🎓 正在執行個人導師示範..."
	@echo ""
	@echo "💬 在 ADK 網頁介面試試這些對話流程:"
	@echo ""
	@echo "1️⃣  設定偏好:"
	@echo "   '將我的語言設為繁體中文,難度設為初學者'"
	@echo ""
	@echo "2️⃣  開始學習:"
	@echo "   '開始學習 Python 基礎'"
	@echo ""
	@echo "3️⃣  完成測驗:"
	@echo "   '我在 Python 測驗中得了 9 分,滿分 10 分'"
	@echo ""
	@echo "4️⃣  查看進度:"
	@echo "   '顯示我的學習進度'"
	@echo ""
	@echo "5️⃣  搜尋記憶:"
	@echo "   '我學過哪些 Python 相關的內容?'"
	@echo ""
	@echo "✅ 示範準備就緒! 開啟 http://localhost:8000"

# 執行測試
test: check-env
	@echo "🧪 正在執行完整測試套件..."
	pytest tests/ -v --tb=short

# 清理
clean:
	@echo "🧹 正在清理..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	@echo "✅ 清理完成!"

# 檢查環境 (內部使用)
check-env:
	@if [ -z "$$GOOGLE_API_KEY" ] && [ -z "$$GOOGLE_APPLICATION_CREDENTIALS" ]; then \
		echo "❌ 錯誤: 尚未設定驗證"; \
		echo ""; \
		echo "請選擇以下其中一種驗證方式:"; \
		echo ""; \
		echo "🔑 方法 1 - API 金鑰 (Gemini API):"; \
		echo "   export GOOGLE_API_KEY=your_api_key_here"; \
		echo "   免費取得金鑰: https://aistudio.google.com/app/apikey"; \
		echo ""; \
		echo "🔐 方法 2 - 服務帳戶 (VertexAI):"; \
		echo "   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json"; \
		echo "   export GOOGLE_CLOUD_PROJECT=your_project_id"; \
		echo "   建立憑證: https://console.cloud.google.com/iam-admin/serviceaccounts"; \
		echo ""; \
		exit 1; \
	fi
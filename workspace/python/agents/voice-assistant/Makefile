# 教學 15：Live API 與音訊 - 即時語音互動
# 用於開發、測試和語音助理示範的 Makefile

.PHONY: help setup dev test clean
.PHONY: lint format validate
.PHONY: live_env_check live_smoke live_models_doc live_access_help

# 預設環境變數，指定託管 Gemini Live 預覽版的區域。
# 對於 Vertex AI：gemini-2.0-flash-live-preview-04-09 (來自官方 ADK 範例)
export VOICE_ASSISTANT_LIVE_MODEL ?= gemini-2.0-flash-live-preview-04-09
export GOOGLE_CLOUD_PROJECT ?= saas-app-001
export GOOGLE_GENAI_USE_VERTEXAI ?= 1
export GOOGLE_CLOUD_LOCATION ?= us-central1
export GOOGLE_GENAI_VERTEXAI_LOCATION ?= $(GOOGLE_CLOUD_LOCATION)

# 預設目標 - 顯示說明
help:
	@echo "🎙️  教學 15：Live API 與音訊 - 即時語音互動"
	@echo ""
	@echo "📋 快速入門："
	@echo "  make setup    # 安裝依賴套件"
	@echo "  make dev      # 啟動 ADK 網頁介面 (✅ 建議用於 Live API)"
	@echo "  make test     # 執行完整的測試套件"
	@echo ""
	@echo "🔧 診斷與設定："
	@echo "  make live_env_check    # 驗證 Vertex AI Live API 設定"
	@echo "  make live_models_list  # 列出您專案中可用的 Live API 模型"
	@echo "  make check_audio       # 檢查音訊裝置是否可用"
	@echo "  make live_smoke        # 快速的 Vertex Live 連線煙霧測試"
	@echo "  make live_models_doc   # 顯示支援的 Live API 模型文件"
	@echo "  make live_access_help  # 請求啟用 Gemini Live API 的步驟"
	@echo ""
	@echo "🧹 維護："
	@echo "  make clean    # 移除快取檔案和產物"
	@echo "  make lint     # 檢查程式碼品質"
	@echo "  make format   # 使用 black 格式化程式碼"
	@echo "  make validate # 執行完整的驗證套件"
	@echo ""
	@echo "📖 教學：https://github.com/raphaelmansuy/adk_training/tree/main/tutorial_implementation/tutorial15"

# 設定環境
setup:
	@echo "📦 正在設定教學 15 的環境..."
	pip install -r requirements.txt
	pip install -e .
	@echo "✅ 設定完成！"
	@echo "💡 後續步驟："
	@echo "   1. 將 .env.example 複製為 .env：cp .env.example .env"
	@echo "   2. 設定 Vertex AI 憑證："
	@echo "      export GOOGLE_GENAI_USE_VERTEXAI=1"
	@echo "      export GOOGLE_CLOUD_PROJECT=your-project"
	@echo "      export GOOGLE_CLOUD_LOCATION=us-central1"
	@echo "      export VOICE_ASSISTANT_LIVE_MODEL=gemini-2.0-flash-live-preview-04-09"
	@echo "   3. 執行 'make dev' 啟動 ADK 網頁介面"
	@echo "   4. 開啟 http://localhost:8000 並選擇 'voice_assistant'"

# 啟動 ADK 網頁介面 (建議用於 Live API)
dev:
	@echo "🌐 正在啟動 ADK 網頁介面..."
	@echo "✅ 這是 Live API 雙向串流的有效方法"
	@echo ""
	@echo "📋 先決條件："
	@echo "   • Vertex AI：設定 GOOGLE_GENAI_USE_VERTEXAI=1"
	@echo "   • 專案：設定 GOOGLE_CLOUD_PROJECT=your-project"
	@echo "   • 區域：設定 GOOGLE_CLOUD_LOCATION=us-central1"
	@echo "   • 模型：設定 VOICE_ASSISTANT_LIVE_MODEL=gemini-2.0-flash-live-preview-04-09"
	@echo ""
	@echo "🎯 使用方式："
	@echo "   1. 在瀏覽器中開啟 http://localhost:8000"
	@echo "   2. 從下拉選單中選擇 'voice_assistant'"
	@echo "   3. 點擊音訊/麥克風按鈕 (🎤)"
	@echo "   4. 開始輸入或說話"
	@echo ""
	@echo "🚀 正在啟動伺服器..."
	adk web

# 執行測試
test:
	@echo "🧪 正在執行完整的測試套件..."
	pytest tests/ -v --cov=voice_assistant --cov-report=term-missing
	@echo "✅ 所有測試完成！"

# 用於 Live API 診斷的環境輔助工具
live_env_check:
	@echo "🩺 正在驗證 Vertex Live 環境..."
	@if [ -z "$$GOOGLE_GENAI_USE_VERTEXAI" ]; then \
		echo "   ❌ GOOGLE_GENAI_USE_VERTEXAI 未設定。請將其匯出 (值為 1) 以使用 Live API。"; \
		echo "   👉 範例：export GOOGLE_GENAI_USE_VERTEXAI=1"; \
		exit 1; \
	fi
	@if [ -z "$$GOOGLE_CLOUD_PROJECT" ]; then \
		echo "   ❌ GOOGLE_CLOUD_PROJECT 缺少。請設定您的 Vertex 專案 ID。"; \
		echo "   👉 範例：export GOOGLE_CLOUD_PROJECT=your-project"; \
		exit 1; \
	fi
	@if [ -z "$$GOOGLE_CLOUD_LOCATION" ]; then \
		echo "   ℹ️  GOOGLE_CLOUD_LOCATION 未設定。預設為 us-central1。"; \
	fi
	@if [ -z "$$VOICE_ASSISTANT_LIVE_MODEL" ]; then \
		echo "   ❌ VOICE_ASSISTANT_LIVE_MODEL 未設定。請選擇支援的 Live API 模型。"; \
		echo "   👉 文件：https://ai.google.dev/gemini-api/docs/live#before_you_begin_building"; \
		exit 1; \
	fi
	@echo "   • Live 模型：$$VOICE_ASSISTANT_LIVE_MODEL"
	@python -m scripts.validate_live_model
	@echo "   ✅ 偵測到 Vertex Live 的先決條件。"

audio_deps_check:
	@echo "🎧 正在檢查本機音訊依賴套件..."
	@python scripts/check_audio_deps.py

live_smoke: live_env_check
	@echo "🧪 正在執行 Vertex Live 煙霧測試 (文字備援)..."
	@python scripts/smoke_test.py

live_models_doc:
	@echo "📚 支援的 Live API 模型 (官方文件)："
	@echo "   半級聯 (Half-cascade)：gemini-live-2.5-flash-preview, gemini-2.0-flash-live-001"
	@echo "   原生音訊 (預設)：gemini-live-2.5-flash-preview-native-audio,"
	@echo "                gemini-2.5-flash-native-audio-preview-09-2025, gemini-2.5-flash-preview-native-audio-dialog,"
	@echo "                gemini-2.5-flash-exp-native-audio-thinking-dialog"
	@echo "   文件：https://ai.google.dev/gemini-api/docs/live#before_you_begin_building"
	@echo "   區域可用性各不相同；請參閱 https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-flash-live-api"

live_access_help:
	@python -m scripts.live_access_help

live_models_list:
	@echo "📡 正在查詢 Vertex AI 以取得可存取的 Live API 模型..."
	@if [ -z "$$GOOGLE_GENAI_USE_VERTEXAI" ]; then \
		echo "   ❌ GOOGLE_GENAI_USE_VERTEXAI 未設定。請將其匯出以使用 Vertex AI。"; \
		echo "   👉 範例：export GOOGLE_GENAI_USE_VERTEXAI=1"; \
		exit 1; \
	fi
	@if [ -z "$$GOOGLE_CLOUD_PROJECT" ]; then \
		echo "   ❌ GOOGLE_CLOUD_PROJECT 缺少。請設定您的 Vertex 專案 ID。"; \
		echo "   👉 範例：export GOOGLE_CLOUD_PROJECT=your-project"; \
		exit 1; \
	fi
	@python -m scripts.list_live_models

# 程式碼品質
lint:
	@echo "🔍 正在執行程式碼品質檢查..."
	@command -v ruff >/dev/null 2>&1 && ruff check voice_assistant/ tests/ || echo "⚠️  ruff 未安裝 (可選)"
	@command -v mypy >/dev/null 2>&1 && mypy voice_assistant/ || echo "⚠️  mypy 未安裝 (可選)"
	@command -v flake8 >/dev/null 2>&1 && flake8 voice_assistant/ tests/ || echo "⚠️  flake8 未安裝 (可選)"
	@echo "✅ Lint 檢查完成！"

format:
	@echo "🎨 正在格式化程式碼..."
	@command -v black >/dev/null 2>&1 && black voice_assistant/ tests/ || echo "⚠️  black 未安裝 (可選)"
	@echo "✅ 程式碼格式化完成！"

# 全面驗證
validate: lint test
	@echo "✅ 完整驗證完成！"

# 清理
clean:
	@echo "🧹 正在清理快取檔案和產物..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete
	@echo "✅ 清理完成！"

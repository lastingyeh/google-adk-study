# 教學 24: 進階可觀測性與監控
# 具有自訂外掛程式的生產環境監控 Agent

.PHONY: help setup dev test clean demo deploy auth

# 預設目標 - 顯示說明
help:
	@echo "🚀 教學 24: 進階可觀測性與監控"
	@echo ""
	@echo "快速入門指令:"
	@echo "  make setup     - 安裝依賴項"
	@echo "  make dev       - 啟動可觀測性 Agent"
	@echo "  make demo      - 顯示示範提示和用法"
	@echo ""
	@echo "進階指令:"
	@echo "  make test      - 執行所有測試"
	@echo "  make deploy    - 部署到 Cloud Run 並啟用追蹤"
	@echo "  make auth      - 使用 Google Cloud 進行驗證"
	@echo "  make clean     - 清理生成的檔案"
	@echo ""
	@echo "💡 第一次使用? 執行: make setup && make auth && make dev"

# 安裝依賴項
setup:
	@echo "📦 正在安裝依賴項..."
	pip install -r requirements.txt
	pip install -e .
	@echo "✅ 設定完成! 執行 'make dev' 啟動 Agent。"

# 啟動可觀測性 Agent
dev: check-env
	@echo "🤖 正在啟動具有 Cloud Tracing 的可觀測性 Agent..."
	@echo "📱 在瀏覽器中打開 http://localhost:8000"
	@echo "🎯 從下拉選單中選擇 'observability_plugins_agent'"
	@echo "📊 嘗試以下提示:"
	@echo "   • '什麼是人工智慧?'"
	@echo "   • '解釋機器學習'"
	@echo "   • '什麼是神經網路?'"
	@echo "💡 檢查控制台以獲取即時指標和監控數據"
	@echo ""
	@echo "🔍 在 Google Cloud Console 中查看追蹤:"
	@echo "   https://console.cloud.google.com/traces?project=saas-app-001"
	@echo ""
	@echo "📋 在 Google Cloud Console 中查看日誌:"
	@echo "   https://console.cloud.google.com/logs/query?project=saas-app-001"
	@echo "   過濾條件: resource.type=\"cloud_run_revision\" OR resource.type=\"agent_engine\""
	adk web --trace_to_cloud

# 執行監控示範
demo: check-env
	@echo "📊 進階可觀測性示範"
	@echo ""
	@echo "💬 在 ADK 網頁 UI 中嘗試這些提示:"
	@echo "   1. '什麼是人工智慧?'"
	@echo "   2. '用簡單的術語解釋機器學習'"
	@echo "   3. 'AI 的應用有哪些?'"
	@echo "   4. '深度學習如何運作?'"
	@echo "   5. 'AI 的未來是什麼?'"
	@echo ""
	@echo "📈 示範功能:"
	@echo "   • SaveFilesAsArtifactsPlugin - 自動儲存檔案"
	@echo "   • MetricsCollectorPlugin - 請求/回應指標"
	@echo "   • AlertingPlugin - 錯誤檢測和警報"
	@echo "   • PerformanceProfilerPlugin - 詳細效能分析"
	@echo ""
	@echo "🔍 觀察控制台輸出:"
	@echo "   • 請求開始/完成事件"
	@echo "   • 延遲測量"
	@echo "   • Token 計數"
	@echo "   • 成功/錯誤追蹤"
	@echo ""
	@echo "✅ 示範準備就緒! 打開 http://localhost:8000"

# 使用 Google Cloud 進行驗證
auth:
	@echo "🔐 正在使用 Google Cloud 進行驗證..."
	@echo "📋 這將打開瀏覽器進行驗證"
	@echo "🔑 選擇您的 Google 帳戶並授予權限"
	@echo ""
	gcloud auth application-default login
	@echo ""
	@echo "✅ 驗證完成!"
	@echo "💡 下一步:"
	@echo "   1. 設定您的專案: export GOOGLE_CLOUD_PROJECT=your-project-id"
	@echo "   2. 設定您的區域: export GOOGLE_CLOUD_LOCATION=us-central1"
	@echo "   3. 執行: make deploy"

# 部署到 Cloud Run 並啟用追蹤
deploy: check-env
	@echo "🚀 正在將可觀測性 Agent 部署到 Cloud Run 並啟用追蹤..."
	@echo "🔍 追蹤將在以下位置可用:"
	@echo "   https://console.cloud.google.com/traces?project=saas-app-001"
	@echo ""
	@echo "📋 日誌將在以下位置可用:"
	@echo "   https://console.cloud.google.com/logs/query?project=saas-app-001"
	@echo "   過濾條件: resource.type=\"cloud_run_revision\""
	adk deploy cloud_run --project saas-app-001 --region us-central1 --trace_to_cloud observability_plugins_agent

# 執行測試
test: check-env
	@echo "🧪 正在執行測試..."
	pytest tests/ -v --tb=short --cov=observability_plugins_agent --cov-report=term-missing

# 清理
clean:
	@echo "🧹 正在清理..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf *.egg-info/
	@echo "✅ 清理完成!"

# 檢查環境 (內部使用)
check-env:
	@if [ -z "$$GOOGLE_API_KEY" ] && [ -z "$$GOOGLE_APPLICATION_CREDENTIALS" ] && [ -z "$$GOOGLE_CLOUD_PROJECT" ]; then \
		echo "❌ 錯誤: 未設定驗證"; \
		echo ""; \
		echo "選擇以下驗證方法之一:"; \
		echo ""; \
		echo "🔑 方法 1 - API Key (Gemini API):"; \
		echo "   export GOOGLE_API_KEY=your_api_key_here"; \
		echo "   在以下位置獲取免費金鑰: https://aistudio.google.com/app/apikey"; \
		echo ""; \
		echo "🔐 方法 2 - Service Account (VertexAI):"; \
		echo "   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json"; \
		echo "   export GOOGLE_CLOUD_PROJECT=your_project_id"; \
		echo "   export GOOGLE_CLOUD_LOCATION=us-central1"; \
		echo "   在以下位置建立憑證: https://console.cloud.google.com/iam-admin/serviceaccounts"; \
		echo ""; \
		echo "🔑 方法 3 - Application Default Credentials (VertexAI):"; \
		echo "   gcloud auth application-default login"; \
		echo "   export GOOGLE_CLOUD_PROJECT=your_project_id"; \
		echo "   export GOOGLE_CLOUD_LOCATION=us-central1"; \
		echo ""; \
		exit 1; \
	fi

# 重點摘要
# - **核心概念**: 自動化構建與管理腳本
# - **關鍵技術**: Make, CLI 自動化, 雲端部署 (Cloud Run), 測試 (pytest)
# - **行動項目**: 使用 `make setup` 初始化專案，`make dev` 進行開發測試，`make deploy` 部署至生產環境

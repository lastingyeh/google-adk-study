# 教學 23：生產部署實作
# 用於開發、測試和部署指南的 Makefile

.PHONY: help setup dev test demo clean check-env server server-docs
.PHONY: demo-info demo-scenarios demo-deployment

# 預設目標 - 顯示說明
help:
	@echo "🚀 教學 23：生產部署實作"
	@echo ""
	@echo "📋 快速開始："
	@echo "  make setup    # 安裝相依套件"
	@echo "  make demo     # 顯示部署策略"
	@echo ""
	@echo "🎯 開發指令："
	@echo "  make setup    # 安裝相依套件和套件"
	@echo "  make dev      # 啟動 ADK 網頁介面（需要 GOOGLE_API_KEY）"
	@echo "  make test     # 執行全面測試套件"
	@echo ""
	@echo "🎪 演示指令："
	@echo "  make demo               # 顯示所有部署資訊（預設）"
	@echo "  make demo-info          # 部署概念與最佳實務"
	@echo "  make demo-scenarios     # 真實世界部署情境"
	@echo "  make demo-deployment    # 部署指令參考"
	@echo ""
	@echo "🌐 伺服器指令："
	@echo "  make server             # 啟動自訂 FastAPI 伺服器"
	@echo "  make server-docs        # 顯示 FastAPI 文件資訊"
	@echo ""
	@echo "🧹 維護："
	@echo "  make clean    # 移除快取檔案和產物"
	@echo ""
	@echo "📖 了解更多：https://github.com/raphaelmansuy/adk_training/tree/main/docs/tutorial/23_production_deployment.md"

# 設定環境
setup:
	@echo "📦 設定教學 23 環境..."
	pip install -r requirements.txt
	pip install -e .
	@echo "✅ 設定完成！"
	@echo ""
	@echo "💡 下一步："
	@echo "   1. 設定您的 API 金鑰：export GOOGLE_API_KEY=your_api_key"
	@echo "   2. 嘗試演示：        make demo"
	@echo "   3. 執行測試：        make test"
	@echo "   4. 啟動開發：        make dev"
	@echo ""
	@echo "🔑 在此取得免費 API 金鑰：https://aistudio.google.com/app/apikey"

# 啟動 ADK 網頁介面
dev: check-env
	@echo "🤖 啟動生產部署代理..."
	@echo "🌐 在瀏覽器中開啟 http://localhost:8000"
	@echo "🎯 從下拉式選單選擇 'production_deployment_agent'"
	@echo ""
	@echo "💬 嘗試這些提示："
	@echo "   • 'What deployment options are available?' (有哪些部署選項？)"
	@echo "   • 'How do I deploy to Cloud Run?' (如何部署到 Cloud Run？)"
	@echo "   • 'What are best practices for production?' (生產環境的最佳實務是什麼？)"
	@echo "   • 'Show me health check configuration' (顯示健康檢查設定)"
	@echo ""
	adk web

# 執行測試
test: check-env
	@echo "🧪 執行全面測試套件..."
	pytest tests/ -v --cov=production_agent --cov-report=term-missing
	@echo ""
	@echo "✅ 所有測試完成！"

# 主要演示 - 顯示所有部署資訊
demo: demo-info demo-deployment demo-scenarios

# 演示：部署概念與最佳實務
demo-info:
	@echo ""
	@echo "═══════════════════════════════════════════════════════════════"
	@echo "📚 生產部署概念"
	@echo "═══════════════════════════════════════════════════════════════"
	@echo ""
	@echo "🎯 部署策略："
	@echo "   • 本地開發 (Local Development)：快速測試與迭代"
	@echo "   • API 伺服器 (API Server)：將代理公開為 REST 端點"
	@echo "   • Cloud Run：無伺服器容器部署"
	@echo "   • Agent Engine：託管企業級部署"
	@echo "   • GKE：用於可擴展部署的 Kubernetes"
	@echo ""
	@echo "🔒 最佳實務："
	@echo "   • 安全性：使用服務帳戶，而非 API 金鑰"
	@echo "   • 監控：追蹤指標與錯誤"
	@echo "   • 健康檢查：實作存活探針 (liveness probes)"
	@echo "   • 可擴展性：針對負載使用自動擴展"
	@echo "   • 可靠性：實作重試與逾時"
	@echo ""
	@echo "📊 關鍵指標："
	@echo "   • 請求延遲與吞吐量"
	@echo "   • 錯誤率與類型"
	@echo "   • 資源使用量（CPU、記憶體、網路）"
	@echo "   • 正常運行時間與可用性"
	@echo ""

# 演示：真實世界部署情境
demo-scenarios:
	@echo "═══════════════════════════════════════════════════════════════"
	@echo "🎬 部署情境"
	@echo "═══════════════════════════════════════════════════════════════"
	@echo ""
	@echo "📝 情境 1：初始開發"
	@echo "   目標：快速迭代代理邏輯"
	@echo "   指令：make dev"
	@echo "   工具：ADK Web UI 進行測試"
	@echo ""
	@echo "📝 情境 2：本地測試"
	@echo "   目標：將代理作為 REST API 進行測試"
	@echo "   指令：make server"
	@echo "   端點：http://localhost:8000/invoke"
	@echo ""
	@echo "📝 情境 3：Cloud Run 上的生產環境"
	@echo "   目標：部署到無伺服器環境"
	@echo "   步驟："
	@echo "      1. 建立 Docker 映像檔"
	@echo "      2. 推送到 Google Container Registry"
	@echo "      3. 使用以下指令部署：adk deploy cloud_run"
	@echo ""
	@echo "📝 情境 4：企業級部署"
	@echo "   目標：使用 Google 的託管 Agent Engine"
	@echo "   指令：adk deploy agent_engine"
	@echo "   功能：完整監控、擴展、安全性"
	@echo ""

# 演示：部署指令參考
demo-deployment:
	@echo "═══════════════════════════════════════════════════════════════"
	@echo "⚙️  部署指令參考"
	@echo "═══════════════════════════════════════════════════════════════"
	@echo ""
	@echo "🏠 本地開發："
	@echo "   adk web                           # 啟動 ADK 網頁 UI"
	@echo "   adk api_server                    # 在本地啟動 API 伺服器"
	@echo ""
	@echo "☁️  雲端部署："
	@echo "   adk deploy cloud_run --project PROJECT --region REGION"
	@echo "      部署到 Google Cloud Run（無伺服器）"
	@echo ""
	@echo "🤖 託管部署："
	@echo "   adk deploy agent_engine --project PROJECT --region REGION"
	@echo "      部署到 Google 的託管 Agent Engine"
	@echo ""
	@echo "🐳 Kubernetes 部署："
	@echo "   adk deploy gke                    # 部署到 GKE 叢集"
	@echo ""
	@echo "💡 範例：部署到 us-central1 的 Cloud Run"
	@echo "   adk deploy cloud_run --project my-project --region us-central1"
	@echo ""

# 啟動自訂 FastAPI 伺服器
server: check-env
	@echo "🚀 啟動生產部署 FastAPI 伺服器..."
	@echo ""
	@echo "📍 伺服器詳細資訊："
	@echo "   • URL：http://localhost:8000"
	@echo "   • 文件：http://localhost:8000/docs"
	@echo "   • 健康狀態：http://localhost:8000/health"
	@echo ""
	@echo "🎯 範例請求："
	@echo "   # 健康檢查"
	@echo "   curl http://localhost:8000/health"
	@echo ""
	@echo "   # 調用代理"
	@echo "   curl -X POST http://localhost:8000/invoke \\  "
	@echo "     -H 'Content-Type: application/json' \\"
	@echo "     -d '{\"query\": \"What are deployment options?\"}'"
	@echo ""
	@echo "按 Ctrl+C 停止伺服器"
	@echo ""
	python -m uvicorn production_agent.server:app --reload

# 顯示 FastAPI 文件資訊
server-docs:
	@echo ""
	@echo "═══════════════════════════════════════════════════════════════"
	@echo "📚 FASTAPI 伺服器文件"
	@echo "═══════════════════════════════════════════════════════════════"
	@echo ""
	@echo "🚀 啟動伺服器："
	@echo "   make server"
	@echo ""
	@echo "📖 存取文件："
	@echo "   • Swagger UI：http://localhost:8000/docs"
	@echo "   • ReDoc：http://localhost:8000/redoc"
	@echo ""
	@echo "🔌 API 端點："
	@echo ""
	@echo "   GET /health"
	@echo "      檢查伺服器健康狀態與運行時間"
	@echo "      傳回：uptime (秒), request_count, status"
	@echo ""
	@echo "   POST /invoke"
	@echo "      調用生產部署代理"
	@echo "      Body: { \"query\": \"your prompt here\" }"
	@echo "      傳回：{ \"response\": \"...\", \"status\": \"success\" }"
	@echo ""
	@echo "   GET /"
	@echo "      API 根目錄資訊"
	@echo ""
	@echo "💡 Python 範例："
	@echo "   import requests"
	@echo "   response = requests.post("
	@echo "       'http://localhost:8000/invoke',"
	@echo "       json={'query': 'What deployment options are available?'}"
	@echo "   )"
	@echo "   print(response.json()['response'])"
	@echo ""

# 清理快取檔案
clean:
	@echo "🧹 清理快取檔案和產物..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.pyd" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .coverage -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name .coverage -delete 2>/dev/null || true
	find . -type f -name coverage.xml -delete 2>/dev/null || true
	@echo "✅ 清理完成！"

# 檢查環境（內部使用）
check-env:
	@if [ -z "$$GOOGLE_API_KEY" ] && [ -z "$$GOOGLE_APPLICATION_CREDENTIALS" ]; then \
		echo "❌ 錯誤：未設定驗證"; \
		echo ""; \
		echo "請選擇以下一種驗證方式："; \
		echo ""; \
		echo "🔑 方法 1 - API 金鑰 (Gemini API)："; \
		echo "   export GOOGLE_API_KEY=your_api_key_here"; \
		echo "   在此取得免費金鑰：https://aistudio.google.com/app/apikey"; \
		echo ""; \
		echo "🔐 方法 2 - 服務帳戶 (VertexAI)："; \
		echo "   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json"; \
		echo "   export GOOGLE_CLOUD_PROJECT=your_project_id"; \
		echo "   在此建立憑證：https://console.cloud.google.com/iam-admin/serviceaccounts"; \
		echo ""; \
		exit 1; \
	fi

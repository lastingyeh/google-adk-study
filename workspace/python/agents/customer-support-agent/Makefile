# 教學 30：Next.js ADK 整合
# 用於管理後端和前端的 Makefile

.PHONY: help setup setup-backend setup-frontend dev dev-backend dev-frontend test clean demo

# 預設目標 - 顯示說明
help:
	@echo "🚀 教學 30：Next.js ADK 整合"
	@echo ""
	@echo "快速入門指令："
	@echo "  make setup          - 安裝所有相依套件 (後端 + 前端)"
	@echo "  make dev            - 啟動後端和前端伺服器"
	@echo "  make dev-backend    - 僅啟動後端伺服器"
	@echo "  make dev-frontend   - 僅啟動前端伺服器"
	@echo "  make demo           - 顯示示範提示和用法"
	@echo ""
	@echo "進階指令："
	@echo "  make test           - 執行所有測試"
	@echo "  make clean          - 清理產生的檔案"
	@echo ""
	@echo "💡 第一次使用？請執行：make setup && make dev"
	@echo ""
	@echo "架構："
	@echo "  後端：Python FastAPI + ADK agent (埠號 8000)"
	@echo "  前端：Next.js 15 + CopilotKit (埠號 3000)"

# 安裝所有相依套件
setup: setup-backend setup-frontend
	@echo "✅ 設定完成！"
	@echo ""
	@echo "後續步驟："
	@echo "  1. 設定 API 金鑰：cp agent/.env.example agent/.env"
	@echo "  2. 編輯 agent/.env 並加入您的 GOOGLE_API_KEY"
	@echo "  3. 執行：make dev"

# 安裝後端相依套件
setup-backend:
	@echo "📦 正在安裝後端相依套件..."
	pip install -r requirements.txt
	pip install -e .
	@echo "✅ 後端設定完成！"

# 安裝前端相依套件
setup-frontend:
	@echo "📦 正在安裝前端相依套件..."
	@if [ ! -d "nextjs_frontend/node_modules" ]; then \
		cd nextjs_frontend && npm install; \
	else \
		echo "前端相依套件已安裝。執行 'make clean' 以重新安裝。"; \
	fi
	@echo "✅ 前端設定完成！"

# 同時啟動後端和前端
dev:
	@echo "🚀 正在啟動後端和前端伺服器..."
	@echo ""
	@echo "這將開啟兩個終端機："
	@echo "  終端機 1：後端 (http://localhost:8000)"
	@echo "  終端機 2：前端 (http://localhost:3000)"
	@echo ""
	@echo "按 Ctrl+C 停止兩個伺服器"
	@echo ""
	@$(MAKE) dev-parallel

# 平行啟動後端和前端 (內部使用)
dev-parallel: check-env
	@trap 'kill 0' EXIT; \
	(cd agent && python agent.py) & \
	(cd nextjs_frontend && npm run dev) & \
	wait

# 僅啟動後端伺服器
dev-backend: check-env
	@echo "🤖 正在啟動後端伺服器..."
	@echo "📱 伺服器：http://localhost:8000"
	@echo "📚 API 文件：http://localhost:8000/docs"
	@echo "💬 CopilotKit 端點：http://localhost:8000/api/copilotkit"
	@echo ""
	cd agent && python agent.py

# 僅啟動前端伺服器
dev-frontend:
	@echo "🌐 正在啟動前端伺服器..."
	@echo "📱 在瀏覽器中開啟 http://localhost:3000"
	@echo ""
	@echo "⚠️  請確認後端正在埠號 8000 執行"
	@echo "    在另一個終端機執行：make dev-backend"
	@echo ""
	cd nextjs_frontend && npm run dev

# 執行測試
test: check-env
	@echo "🧪 正在執行測試..."
	pytest tests/ -v --tb=short

# 執行示範
demo: check-env
	@echo "💬 示範：客戶支援代理人 (Customer Support Agent)"
	@echo ""
	@echo "=================================="
	@echo "在聊天介面中嘗試這些提示："
	@echo "=================================="
	@echo ""
	@echo "📚 知識庫查詢："
	@echo "  • '你的退款政策是什麼？ (What is your refund policy?)'"
	@echo "  • '運送需要多久？ (How long does shipping take?)'"
	@echo "  • '告訴我關於保固的資訊 (Tell me about your warranty)'"
	@echo "  • '我要如何重設密碼？ (How do I reset my password?)'"
	@echo ""
	@echo "📦 訂單狀態："
	@echo "  • '檢查訂單 ORD-12345 的狀態'"
	@echo "  • '訂單 ORD-67890 的狀態如何？'"
	@echo "  • '追蹤我的訂單 ORD-11111'"
	@echo ""
	@echo "🎫 支援工單："
	@echo "  • '我的產品在 2 個月後停止運作'"
	@echo "  • '我需要協助解決帳單問題'"
	@echo "  • '為帳戶存取問題建立工單'"
	@echo ""
	@echo "=================================="
	@echo ""
	@echo "使用說明："
	@echo "  1. 啟動伺服器：make dev"
	@echo "  2. 開啟 http://localhost:3000"
	@echo "  3. 輸入上述任何提示"
	@echo "  4. 觀看代理人自動使用工具！"
	@echo ""
	@echo "架構："
	@echo "  使用者 → Next.js (埠號 3000) → FastAPI (埠號 8000) → ADK Agent → Gemini"

# 清理
clean:
	@echo "🧹 正在清理..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache/
	cd nextjs_frontend && rm -rf .next/ node_modules/.cache/ || true
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
		echo "   在以下網址取得免費金鑰：https://aistudio.google.com/app/apikey"; \
		echo ""; \
		echo "🔐 方法 2 - 服務帳戶 (VertexAI)："; \
		echo "   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json"; \
		echo "   export GOOGLE_CLOUD_PROJECT=your_project_id"; \
		echo "   在以下網址建立憑證：https://console.cloud.google.com/iam-admin/serviceaccounts"; \
		echo ""; \
		exit 1; \
	fi

# 重點摘要
# - **核心概念**：用於管理後端 (FastAPI) 和前端 (Next.js) 伺服器的 Makefile，支援客戶支援代理人教學專案。
# - **關鍵技術**：Make, Python (pip), Node.js (npm), FastAPI, Next.js。
# - **重要結論**：提供了一組標準化指令來簡化安裝 (`make setup`)、開發 (`make dev`)、測試 (`make test`) 和清理 (`make clean`) 流程。
# - **行動項目**：無。

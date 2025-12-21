.PHONY: setup clean test dev help docker-up docker-down

help:
	@echo ""
	@echo "╔════════════════════════════════════════════════════════════════╗"
	@echo "║  自定義會話服務 (Custom Session Services) - Redis 存儲演示    ║"
	@echo "╚════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "🎯 快速開始 (QUICK START):"
	@echo "   make setup          安裝依賴 (Install dependencies)"
	@echo "   make dev            啟動帶有 Redis 會話的 ADK 網頁介面"
	@echo "   make test           執行單元測試 (Run unit tests)"
	@echo ""
	@echo "🐳 DOCKER:"
	@echo "   make docker-up      啟動 Redis 容器 (連接埠 6379)"
	@echo "   make docker-down    停止容器 (Stop containers)"
	@echo ""
	@echo "🧹 清理 (CLEANUP):"
	@echo "   make clean          移除快取檔案 (Remove cache files)"
	@echo ""
	@echo "📖 完整指南 (FULL GUIDE):"
	@echo "   1. make setup"
	@echo "   2. make docker-up"
	@echo "   3. make dev"
	@echo "   4. 開啟 http://127.0.0.1:8000"
	@echo "   5. 選擇: custom_session_agent"
	@echo ""
	@echo "✨ 試著發送: 'Write me a poem'"
	@echo "   然後重新整理瀏覽器來測試持久化性 (Persistence)！"
	@echo ""

setup:
	@echo "📦 正在安裝依賴..."
	pip install -r requirements.txt
	pip install -e .
	@echo "✅ 完成！"

docker-up:
	@echo "🐳 正在啟動 Redis..."
	docker-compose up -d redis
	@echo "⏳ 等待 Redis 就緒..."
	sleep 2
	redis-cli ping 2>/dev/null || sleep 2
	@echo "✅ Redis 已就緒，網址：redis://localhost:6379"

docker-down:
	@echo "🛑 正在停止 Redis..."
	docker-compose down
	@echo "✅ 已停止"

dev: docker-up
	@echo ""
	@echo "🚀 正在啟動 ADK 網頁介面..."
	@echo "   Agent: custom_session_agent"
	@echo "   後端 (Backend): Redis (redis://localhost:6379)"
	@echo "   URL: http://127.0.0.1:8000"
	@echo ""
	python -m custom_session_agent web --session_service_uri=redis://localhost:6379

test:
	@echo "🧪 正在執行測試..."
	pytest tests/ -v --tb=short
	@echo "✅ 測試完成！"

clean:
	@echo "🧹 正在清理..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name "*.egg-info" -delete
	@echo "✅ 清理完畢！"

### 重點摘要
- **核心概念**：自動化工作流指令。
- **關鍵技術**：GNU Make, Docker Compose, Python pip, Redis。
- **重要結論**：Makefile 簡化了開發環境的建置、服務啟動與清理流程。
- **行動項目**：開發者應使用 `make help` 檢視所有可用指令，並按指南順序操作。

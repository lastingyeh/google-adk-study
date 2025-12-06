# Commerce Agent E2E - 端到端實作教學
# 具備生產力等級、包含會話持久性的多用戶商務助理

.PHONY: help setup dev dev-sqlite test test-guide demo demo-sqlite clean check-env setup-vertex-ai

# 預設目標
help:
	@echo "🛍️  Commerce Agent E2E - 端到端實作"
	@echo ""
	@echo "快速開始指令："
	@echo "  make setup              - 安裝相依套件並設定套件"
	@echo "  make setup-vertex-ai    - 設定 Vertex AI 驗證"
	@echo "  make test               - 執行完整的測試套件 (單元、整合、e2e)"
	@echo "  make test-guide         - 查看使用使用者身分進行測試的指南"
	@echo "  make dev                - 啟動帶有 ADK 狀態的開發 UI (預設)"
	@echo "  make dev-sqlite         - 啟動帶有 SQLite 持久性的開發 UI"
	@echo "  make demo               - 顯示展示情境"
	@echo "  make demo-sqlite        - 執行 SQLite 持久性展示腳本"
	@echo ""
	@echo "進階指令："
	@echo "  make clean              - 清理產生的檔案"
	@echo ""
	@echo "💡 第一次使用？請執行：make setup-vertex-ai && make setup && make dev"
	@echo ""
	@echo "會話持久性選項："
	@echo "  • ADK 狀態 (預設)：        簡單，開箱即用"
	@echo "  • SQLite (dev-sqlite)：   持久性，重啟後仍存在"

# 安裝相依套件
setup: check-env
	@echo "📦 安裝相依套件中..."
	pip install -r requirements.txt
	pip install -e .
	@echo ""
	@echo "初始化資料庫..."
	python3 -c "from commerce_agent import init_database; init_database(); print('✅ 資料庫已初始化')"
	@echo ""
	@echo "✅ 設定完成！"
	@echo ""
	@echo "下一步："
	@echo "  1. 執行測試：make test"
	@echo "  2. 啟動代理人：make dev"
	@echo "  3. 打開瀏覽器：http://localhost:8000"

# 設定 Vertex AI 驗證 (在 setup 之前執行)
setup-vertex-ai:
	@bash scripts/setup-vertex-ai.sh

# 執行所有測試
test: check-env
	@echo "🧪 執行完整的測試套件..."
	@echo ""
	pytest tests/ -v \
		--tb=short \
		--cov=commerce_agent \
		--cov-report=html \
		--cov-report=term
	@echo ""
	@echo "✅ 測試完成！覆蓋率報告：htmlcov/index.html"

# 顯示使用者身分測試指南
test-guide:
	@echo ""
	@echo "📖 使用特定使用者身分進行測試"
	@echo ""
	@echo "⚠️  重要：'adk web' UI 沒有 User ID/Session ID 的面板"
	@echo "    瀏覽器介面使用固定的預設使用者 ID：'user'"
	@echo ""
	@echo "要使用特定使用者 (alice, bob 等) 進行測試，請使用 API 端點："
	@echo ""
	@echo "1️⃣  為 Alice 建立會話："
	@echo "  curl -X POST http://localhost:8000/apps/commerce_agent/users/alice/sessions/s1 \\"
	@echo "    -H 'Content-Type: application/json' -d '{\"state\": {}}'"
	@echo ""
	@echo "2️⃣  以 Alice 身分發送訊息："
	@echo "  curl -X POST http://localhost:8000/run -H 'Content-Type: application/json' -d '{"
	@echo "    \"app_name\": \"commerce_agent\","
	@echo "    \"user_id\": \"alice\","
	@echo "    \"session_id\": \"s1\","
	@echo "    \"new_message\": {"
	@echo "      \"role\": \"user\","
	@echo "      \"parts\": [{\"text\": \"I want running shoes under 150 euros\"}]"
	@echo "    }"
	@echo "  }'"
	@echo ""
	@echo "3️⃣  為 Bob 建立會話："
	@echo "  curl -X POST http://localhost:8000/apps/commerce_agent/users/bob/sessions/s2 \\"
	@echo "    -H 'Content-Type: application/json' -d '{\"state\": {}}'"
	@echo ""
	@echo "4️⃣  以 Bob 身分發送訊息："
	@echo "  curl -X POST http://localhost:8000/run -H 'Content-Type: application/json' -d '{"
	@echo "    \"app_name\": \"commerce_agent\","
	@echo "    \"user_id\": \"bob\","
	@echo "    \"session_id\": \"s2\","
	@echo "    \"new_message\": {"
	@echo "      \"role\": \"user\","
	@echo "      \"parts\": [{\"text\": \"I am into cycling. Budget 200 euros\"}]"
	@echo "    }"
	@echo "  }'"
	@echo ""
	@echo "5️⃣  驗證隔離 - 檢查 Alice 的偏好："
	@echo "  curl -X POST http://localhost:8000/run -H 'Content-Type: application/json' -d '{"
	@echo "    \"app_name\": \"commerce_agent\","
	@echo "    \"user_id\": \"alice\","
	@echo "    \"session_id\": \"s1\","
	@echo "    \"new_message\": {"
	@echo "      \"role\": \"user\","
	@echo "      \"parts\": [{\"text\": \"What are my preferences?\"}]"
	@echo "    }"
	@echo "  }'"
	@echo ""
	@echo "預期：代理人顯示跑步 (而不是騎行) ✅"
	@echo ""
	@echo "📄 完整文件："
	@echo "   docs/TESTING_WITH_USER_IDENTITIES.md"
	@echo ""
	@echo "或打開指南："
	@if command -v less >/dev/null 2>&1; then \
		less docs/TESTING_WITH_USER_IDENTITIES.md; \
	elif command -v more >/dev/null 2>&1; then \
		more docs/TESTING_WITH_USER_IDENTITIES.md; \
	else \
		cat docs/TESTING_WITH_USER_IDENTITIES.md; \
	fi

# 啟動開發 UI (預設 - 使用 ADK 狀態)
dev: check-env
	@echo "🤖 正在啟動商務代理人..."
	@echo ""
	@if [ ! -z "$$GOOGLE_API_KEY" ]; then \
		echo "⚠️  取消設定 GOOGLE_API_KEY 以使用 Vertex AI..."; \
		unset GOOGLE_API_KEY; \
	fi
	@if [ ! -z "$$GEMINI_API_KEY" ]; then \
		echo "⚠️  取消設定 GEMINI_API_KEY 以使用 Vertex AI..."; \
		unset GEMINI_API_KEY; \
	fi
	@echo ""
	@echo "📱 在瀏覽器中打開 http://localhost:8000"
	@echo "🎯 從代理人下拉選單中選擇 'commerce_agent'"
	@echo ""
	@echo "💾 會話持久性：ADK 狀態 (user: 前綴)"
	@echo "   - 偏好在不同調用間持續存在"
	@echo "   - 應用程式重啟時會話遺失"
	@echo ""
	@echo "💡 想要跨重啟的持久性？請使用：make dev-sqlite"
	@echo ""
	@echo "測試情境："
	@echo "  • 使用者 'alice', 運動：'running' → 尋找慢跑鞋"
	@echo "  • 使用者 'bob', 運動：'cycling' → 推薦騎行裝備"
	@echo "  • 昂貴物品測試 → 嘗試超過 €100 的產品"
	@echo ""
	unset GOOGLE_API_KEY GEMINI_API_KEY; adk web

# 啟動帶有 SQLite 會話持久性的開發 UI
dev-sqlite: check-env
	@echo "🤖 正在啟動帶有 SQLite 會話持久性的商務代理人"
	@echo ""
	@if [ ! -z "$$GOOGLE_API_KEY" ]; then \
		echo "⚠️  取消設定 GOOGLE_API_KEY 以使用 Vertex AI..."; \
		unset GOOGLE_API_KEY; \
	fi
	@if [ ! -z "$$GEMINI_API_KEY" ]; then \
		echo "⚠️  取消設定 GEMINI_API_KEY 以使用 Vertex AI..."; \
		unset GEMINI_API_KEY; \
	fi
	@echo ""
	@echo "📱 在瀏覽器中打開 http://localhost:8000"
	@echo "🎯 從代理人下拉選單中選擇 'commerce_agent'"
	@echo ""
	@echo "💾 會話持久性：SQLite 資料庫"
	@echo "   - 保留完整的對話歷史記錄"
	@echo "   - 會話在應用程式重啟後仍然存在 ✅"
	@echo "   - 資料庫：./commerce_sessions.db"
	@echo ""
	@echo "🔍 檢查資料庫："
	@echo "   sqlite3 commerce_sessions.db"
	@echo "   > .tables"
	@echo "   > SELECT * FROM sessions;"
	@echo ""
	@echo "測試情境："
	@echo "  1. 與代理人聊天"
	@echo "  2. 停止伺服器 (Ctrl+C)"
	@echo "  3. 重啟：make dev-sqlite"
	@echo "  4. 您的會話資料仍然存在！ ✅"
	@echo ""
	unset GOOGLE_API_KEY GEMINI_API_KEY; adk web --session_service_uri "sqlite:///./commerce_sessions.db?mode=wal"

# 顯示展示情境
demo:
	@echo ""
	@echo "📋 商務代理人 E2E 展示情境"
	@echo ""
	@echo "在使用 make dev (或 make dev-sqlite) 啟動後執行這些"
	@echo ""
	@echo "------- 情境 1：新用戶設定 -------"
	@echo "User ID: athlete_1"
	@echo "Session ID: session_1"
	@echo ""
	@echo "1. 輸入：'My favorite sport is running' (我最喜歡的運動是跑步)"
	@echo "   → 代理人學習您的偏好"
	@echo ""
	@echo "2. 輸入：'Find running shoes under €100' (尋找 100 歐元以下的慢跑鞋)"
	@echo "   → 代理人搜尋 Decathlon"
	@echo ""
	@echo "3. 輸入：'Add the Kalenji shoes to my favorites' (將 Kalenji 鞋加入我的最愛)"
	@echo "   → 代理人儲存至您的個人資料"
	@echo ""
	@echo "------- 情境 2：回訪客戶 -------"
	@echo "User ID: athlete_1 (同一位使用者)"
	@echo "Session ID: session_2 (新會話，同一位使用者)"
	@echo ""
	@echo "1. 輸入：'What do you know about me?' (你對我有什麼了解？)"
	@echo "   → 代理人召回偏好 (跑步)"
	@echo ""
	@echo "2. 輸入：'Recommend something based on my history' (根據我的歷史記錄推薦一些東西)"
	@echo "   → 代理人建議與跑步相關的產品"
	@echo ""
	@echo "------- 情境 3：多用戶隔離 -------"
	@echo "User ID: cyclist_1"
	@echo "Session ID: session_1"
	@echo ""
	@echo "1. 輸入：'I'm into cycling' (我喜歡騎行)"
	@echo "2. 輸入：'Find cycling gear' (尋找騎行裝備)"
	@echo ""
	@echo "然後切換："
	@echo "User ID: athlete_1 (回到跑者)"
	@echo ""
	@echo "3. 輸入：'What are my preferences?' (我的偏好是什麼？)"
	@echo "   → 代理人顯示 RUNNING (跑步) (騎行被隱藏)"
	@echo ""
	@echo "------- 情境 4：昂貴物品確認 -------"
	@echo "輸入：'Find high-end running shoes over €200' (尋找超過 200 歐元的高級慢跑鞋)"
	@echo "   → 代理人應要求確認"
	@echo ""
	@echo "✅ 所有情境皆展示了關鍵功能！"
	@echo ""

# 執行 SQLite 持久性展示 (程式化)
demo-sqlite: check-env
	@echo "🚀 執行 SQLite 會話持久性展示"
	@echo ""
	@echo "此腳本展示："
	@echo "  ✅ 使用 SQLite 的 DatabaseSessionService"
	@echo "  ✅ 會話建立與檢索"
	@echo "  ✅ 跨 '重啟' 的狀態持久性"
	@echo "  ✅ 多用戶隔離"
	@echo "  ✅ 對話歷史記錄保存"
	@echo ""
	@echo "按 Ctrl+C 隨時停止"
	@echo ""
	python runner_with_sqlite.py

# 清理
clean:
	@echo "🧹 清理中..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name ".coverage" -delete
	find . -type d -name "htmlcov" -delete
	find . -type d -name "*.egg-info" -delete
	rm -f .coverage
	rm -f commerce_agent_sessions.db
	@echo "✅ 清理完成！"

# 檢查環境 (內部使用)
check-env:
	@if [ -z "$$GOOGLE_API_KEY" ] && [ -z "$$GOOGLE_APPLICATION_CREDENTIALS" ]; then \
		echo "❌ 錯誤：驗證未設定"; \
		echo ""; \
		echo "此代理人需要以下其中一種驗證方式："; \
		echo ""; \
		echo "✅ 推薦 - Vertex AI (Service Account):"; \
		echo "   export GOOGLE_CLOUD_PROJECT=your_project_id"; \
		echo "   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json"; \
		echo "   設定指南：log/20250124_173000_vertex_ai_setup_guide.md"; \
		echo ""; \
		echo "⚠️  不推薦 - Gemini API (搜尋受限):"; \
		echo "   export GOOGLE_API_KEY=your_api_key_here"; \
		echo "   在此獲取金鑰：https://aistudio.google.com/app/apikey"; \
		echo ""; \
		exit 1; \
	fi

.PHONY: help setup dev test clean demo lint install slack-dev slack-deploy slack-test

help:
	@echo "📚 課程 33: Slack 機器人與 ADK 整合"
	@echo ""
	@echo "核心指令:"
	@echo "  make setup              - 安裝依賴並設定環境"
	@echo "  make dev                - 啟動 ADK 網頁介面進行開發"
	@echo "  make test               - 執行測試套件"
	@echo "  make test-coverage      - 執行測試並產生覆蓋率報告"
	@echo "  make demo               - 顯示範例提示與使用方式"
	@echo "  make lint               - 執行程式碼檢查 (linting)"
	@echo "  make clean              - 清除快取檔案與產物"
	@echo ""
	@echo "Slack 整合指令:"
	@echo "  make slack-dev          - 以 Socket Mode 執行機器人 (開發模式)"
	@echo "  make slack-deploy       - 部署至 Cloud Run (生產環境)"
	@echo "  make slack-test         - 測試 Slack 整合"
	@echo ""

setup:
	@echo "🔧 正在設定課程 33..."
	pip install -r requirements.txt
	pip install -e .
	@echo "✅ 設定完成！"
	@echo ""
	@echo "📝 下一步："
	@echo "   1. 複製 support_bot/.env.example 到 support_bot/.env"
	@echo "   2. 將您的 Slack token 和 Google API key 新增至 support_bot/.env"
	@echo "   3. 執行 'make dev' 開始開發"

dev:
	@echo "🚀 正在啟動 ADK 網頁開發介面..."
	@echo "📌 請在瀏覽器中開啟 http://localhost:8000"
	@echo ""
	adk web

test:
	@echo "🧪 正在執行測試..."
	pytest tests/ -v --tb=short

test-coverage:
	@echo "📊 正在執行測試與覆蓋率報告..."
	pytest tests/ -v --cov=support_bot --cov-report=term-missing

demo:
	@echo "📖 Support Bot - 使用範例"
	@echo ""
	@echo "支援機器人提供以下功能："
	@echo ""
	@echo "1. 🔍 知識庫搜尋"
	@echo "   - 搜尋公司政策"
	@echo "   - 尋找 IT 支援資訊"
	@echo "   - 取得休假與遠端工作政策"
	@echo ""
	@echo "2. 🎫 支援工單建立"
	@echo "   - 為複雜問題建立工單"
	@echo "   - 設定優先順序 (低, 一般, 高, 緊急)"
	@echo "   - 透過唯一 ID 追蹤工單"
	@echo ""
	@echo "範例查詢："
	@echo "  • 'How do I reset my password?' (如何重設密碼？)"
	@echo "  • 'What is the vacation policy?' (休假政策是什麼？)"
	@echo "  • 'I need help with VPN setup' (我需要 VPN 設定協助)"
	@echo "  • 'Create a ticket for my laptop issue' (為我的筆電問題建立工單)"
	@echo ""
	@echo "執行 'make dev' 在 ADK 網頁介面測試這些查詢！"
	@echo ""

lint:
	@echo "🔍 正在執行程式碼檢查..."
	python -m pylint support_bot/ || true
	python -m flake8 support_bot/ || true
	@echo "✅ 檢查完成"

clean:
	@echo "🧹 正在清理..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .eggs -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	rm -rf build/ dist/ *.egg-info/
	@echo "✅ 清理完成！"

slack-dev:
	@echo "🚀 以 Socket Mode 啟動 Support Bot (開發模式)..."
	@echo ""
	@if [ ! -f support_bot/.env ]; then \
		echo "❌ 錯誤：找不到 support_bot/.env 檔案！"; \
		echo ""; \
		echo "📝 若要設定您的機器人："; \
		echo "   1. 複製環境變數範本："; \
		echo "      cp support_bot/.env.example support_bot/.env"; \
		echo ""; \
		echo "   2. 編輯 support_bot/.env 並填入您的 Slack token："; \
		echo "      SLACK_BOT_TOKEN=xoxb-..."; \
		echo "      SLACK_APP_TOKEN=xapp-..."; \
		echo "      GOOGLE_API_KEY=..."; \
		echo ""; \
		echo "   3. 從 https://api.slack.com/apps 取得 token"; \
		echo ""; \
		exit 1; \
	fi
	@echo "📋 已從 support_bot/.env 載入設定"
	@echo ""
	@echo "🔗 正在以 Socket Mode 連線至 Slack..."
	@echo "💡 機器人運作中！試著在 Slack 輸入："
	@echo ""
	@echo "   @Support Bot help"
	@echo "   @Support Bot What is the password reset procedure?"
	@echo "   @Support Bot Create a ticket for my issue"
	@echo ""
	@echo "⏹️  按 Ctrl+C 停止"
	@echo ""
	python -m support_bot.bot_dev

slack-deploy:
	@echo "🚀 Cloud Run 生產環境部署 (預設安全模式)"
	@echo ""
	@echo "📋 預演模式 (Dry-run)：僅列印步驟。"
	@echo ""
	@echo "先決條件："
	@echo "  • gcloud CLI 已驗證 (gcloud auth login)"
	@echo "  • Docker 已安裝並運作中"
	@echo "  • PROJECT 和 REGION 環境變數已設定"
	@echo ""
	@echo "步驟："
	@echo "  1. 建置：docker build -t gcr.io/[PROJECT]/support-bot:latest ."
	@echo "  2. 推送：docker push gcr.io/[PROJECT]/support-bot:latest"
	@echo "  3. 部署：gcloud run deploy (包含映像檔與 secrets)"
	@echo "  4. Slack：更新 Event Subscription URL 至 https://[SERVICE_URL]/slack/events"
	@echo ""
	@echo "若要安全地執行此部署："
	@echo "  • 設定 PROJECT 和 REGION："
	@echo "      export PROJECT=your-gcp-project"
	@echo "      export REGION=us-central1"
	@echo "  • 建立 secrets (一次性)："
	@echo "      echo -n $$SLACK_BOT_TOKEN | gcloud secrets create SLACK_BOT_TOKEN --data-file=-"
	@echo "      echo -n $$SLACK_APP_TOKEN | gcloud secrets create SLACK_APP_TOKEN --data-file=-"
	@echo "  • 執行部署腳本："
	@echo "      bash scripts/deploy_cloud_run.sh"
	@echo ""
	@echo "或手動依照 README.md 中的生產環境部署章節操作"

slack-test:
	@echo "🧪 正在測試 Slack 整合..."
	@echo ""
	@echo "測試項目："
	@echo "   ✓ Agent imports"
	@echo "   ✓ Tool functionality"
	@echo "   ✓ Slack compatibility"
	@echo ""
	@echo "正在執行測試..."
	pytest tests/ -v -k "test_" --tb=short
	@echo ""
	@echo "✅ 所有測試通過！"

# 重點摘要 (Makefile)
# - 核心概念：自動化管理開發、測試與部署流程的腳本。
# - 關鍵技術：Make, pip, pytest, Docker, Google Cloud SDK。
# - 重要結論：透過標準化指令簡化了重複性任務，確保開發環境與部署流程的一致性。
# - 行動項目：開發者應優先使用 make 指令來執行任務，而非手動輸入複雜指令。

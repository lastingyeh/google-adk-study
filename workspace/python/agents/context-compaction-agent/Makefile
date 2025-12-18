.PHONY: help setup clean test demo dev

help:
	@echo "Context Compaction TIL - 可用指令"
	@echo "==========================================="
	@echo ""
	@echo "make setup       安裝依賴並準備環境"
	@echo "make test        執行單元測試 (驗證配置)"
	@echo "make dev         啟動 ADK 網頁介面以查看壓縮運作情形"
	@echo "make demo        不透過網頁介面的快速驗證"
	@echo "make clean       移除快取檔案與產物"
	@echo ""

setup:
	pip install -r requirements.txt
	pip install -e .
	cp context_compaction_agent/.env.example context_compaction_agent/.env
	@echo ""
	@echo "✅ 設定完成！"
	@echo ""
	@echo "下一步："
	@echo "1. 新增您的 GOOGLE_API_KEY 到 context_compaction_agent/.env"
	@echo "2. 執行 'make test' 以驗證實作"
	@echo "3. 執行 'make dev' 以啟動網頁介面並測試壓縮功能"
	@echo ""

dev:
	@echo ""
	@echo "🚀 正在啟動 ADK 網頁介面..."
	@echo ""
	@echo "📝 如何測試上下文壓縮 (Context Compaction)："
	@echo "   1. 開啟 http://localhost:8000"
	@echo "   2. 選擇 'context_compaction_agent'"
	@echo "   3. 傳送 5 則以上的訊息以觸發壓縮"
	@echo "   4. 在回應中檢查每個回應的 token 計數"
	@echo ""
	@echo "💡 Token 增長模式："
	@echo "   • 無壓縮：每次互動約 180 tokens"
	@echo "   • 有壓縮：每次互動約 50-60 tokens"
	@echo "   • 觀察 5 次互動後的穩定情況 ✅"
	@echo ""
	@echo "🎯 預期 Token 進程："
	@echo "   訊息 1: ~180 | 訊息 2: ~243 | 訊息 3: ~295"
	@echo "   訊息 4: ~347 | 訊息 5: ~405 ← 觸發壓縮！"
	@echo ""
	adk web

test:
	@echo ""
	@echo "🧪 正在執行上下文壓縮測試..."
	@echo ""
	@pytest tests/ -v --tb=short
	@echo ""
	@echo "✅ 測試驗證項目："
	@echo "   • 代理配置 (7 項測試)"
	@echo "   • 工具功能 (5 項測試)"
	@echo "   • 匯入路徑 (3 項測試)"
	@echo "   • 應用程式與壓縮設定 (4 項測試)"
	@echo ""

demo:
	@echo ""
	@echo "🔍 快速驗證..."
	python -c "from context_compaction_agent import root_agent; from app import app; print('✅ 代理已載入:', root_agent.name); print('✅ 應用程式已配置:', app.name); print('✅ 壓縮已啟用:', app.events_compaction_config is not None)"
	@echo ""
	@echo "🎯 實作已就緒！"
	@echo ""

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov build dist *.egg-info
	@echo "✅ 已清除快取檔案"

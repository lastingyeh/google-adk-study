# 策略問題解決器 - 教學 12：規劃器與思考配置
# 用於開發、測試和部署的 Makefile

.PHONY: help setup dev test demo examples clean lint format

# 預設目標
help:
	@echo "策略問題解決器 - 教學 12"
	@echo ""
	@echo "可用指令："
	@echo "  setup     安裝相依套件並以開發模式安裝套件"
	@echo "  dev       啟動 ADK 網頁介面 (http://localhost:8000)"
	@echo "  test      執行完整測試套件 (60+ 個測試)"
	@echo "  demo      執行自動化策略問題解決範例"
	@echo "  examples  顯示可測試的範例查詢"
	@echo "  clean     移除快取檔案和產出物"
	@echo "  lint      使用 flake8 檢查程式碼風格"
	@echo "  format    使用 black 格式化程式碼"

# 設定環境
setup:
	pip install -r requirements.txt
	pip install -e .[dev]

# 啟動開發伺服器
dev:
	@echo "正在啟動 ADK 網頁介面..."
	@echo "在瀏覽器開啟 http://localhost:8000"
	@echo "從代理下拉選單選擇 'strategic_solver'"
	adk web

# 執行測試
test:
	pytest tests/ -v --cov=strategic_solver --cov-report=term-missing

# 執行示範範例
demo:
	@echo "執行策略問題解決範例..."
	@echo "這將展示三種規劃器類型 (BuiltInPlanner, PlanReActPlanner, StrategicPlanner)"
	@echo "處理不同的商業場景。"
	@echo ""
	python -c "import asyncio; from strategic_solver.agent import demo_strategic_planning; asyncio.run(demo_strategic_planning())"

# 顯示測試範例查詢
examples:
	@echo "策略問題解決器 - 測試範例查詢"
	@echo "=================================================="
	@echo ""
	@echo "在 ADK 網頁介面 (make dev) 或代理中嘗試這些查詢："
	@echo ""
	@echo "📊 市場分析查詢："
	@echo "  • 我們應該擴展到亞洲醫療保健市場嗎？"
	@echo "  • 歐洲金融科技領域值得進入嗎？"
	@echo "  • 分析 AI 諮詢服務的市場機會"
	@echo ""
	@echo "💰 財務分析查詢："
	@echo '  • 我們應該投資 200 萬美元在再生能源新創公司嗎？'
	@echo '  • 這項 50 萬美元的 AI 技術投資值得冒險嗎？'
	@echo "  • 計算 3 年期投資 15% 年報酬率的 ROI"
	@echo ""
	@echo "⚠️  風險評估查詢："
	@echo "  • 我們應該如何減輕金融科技新創公司的網路安全威脅？"
	@echo "  • 進入歐洲市場有哪些風險？"
	@echo "  • 評估新產品發布的商業風險"
	@echo ""
	@echo "🎯 策略規劃查詢："
	@echo '  • 我們有 100 萬美元可投資 - 應該擴展現有業務還是進入新市場？'
	@echo "  • 為我們的 SaaS 公司設計 5 年成長策略"
	@echo "  • 我們應該如何應對日益激烈的市場競爭？"
	@echo ""
	@echo "🤖 規劃器比較："
	@echo "  每個代理使用不同的規劃方法："
	@echo "  • BuiltInPlanner: 顯示透明的思考過程"
	@echo "  • PlanReActPlanner: 使用結構化的 計劃→推理→行動→觀察→重新規劃"
	@echo "  • StrategicPlanner: 特定領域的商業策略工作流程"
	@echo ""
	@echo "💡 提示："
	@echo "  • 複雜查詢比簡單查詢更適合使用規劃器"
	@echo "  • BuiltInPlanner 顯示推理過程 - 非常適合學習"
	@echo "  • PlanReActPlanner 系統化且徹底"
	@echo "  • StrategicPlanner 遵循商業諮詢方法論"

# 清理
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

# 程式碼品質
lint:
	flake8 strategic_solver/ tests/
	black --check strategic_solver/ tests/

format:
	black strategic_solver/ tests/
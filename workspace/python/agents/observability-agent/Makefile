.PHONY: setup dev test demo clean coverage help

help:
	@echo "教學 18：事件與可觀測性"
	@echo ""
	@echo "可用指令："
	@echo "  make setup    - 安裝依賴套件"
	@echo "  make dev      - 使用 ADK 網站介面執行代理程式"
	@echo "  make test     - 執行所有測試"
	@echo "  make demo     - 執行示範情境"
	@echo "  make coverage - 執行測試並產出覆蓋率報告"
	@echo "  make clean    - 移除快取檔案與產物"
	@echo ""
	@echo "先決條件："
	@echo "  - Python 3.10 或更高版本"
	@echo "  - 已設定 GOOGLE_API_KEY 環境變數"
	@echo ""
	@echo "快速入門："
	@echo "  1. make setup"
	@echo "  2. export GOOGLE_API_KEY=your_key"
	@echo "  3. make dev"

setup:
	@echo "正在安裝依賴套件..."
	pip install -r requirements.txt
	pip install -e .
	@echo ""
	@echo "✅ 設定完成！"
	@echo ""
	@echo "後續步驟："
	@echo "  1. 設定 GOOGLE_API_KEY: export GOOGLE_API_KEY=your_key"
	@echo "  2. 執行測試: make test"
	@echo "  3. 啟動代理程式: make dev"

dev:
	@echo "正在啟動 ADK 網站介面..."
	@echo ""
	@echo "📊 事件追蹤功能："
	@echo ""
	@echo "1. 訂單狀態追蹤"
	@echo "   嘗試：'我的訂單 ORD-001 的狀態是什麼？'"
	@echo "   - 追蹤客戶查詢"
	@echo "   - 記錄工具呼叫 (check_order_status)"
	@echo "   - 記錄代理程式回應"
	@echo ""
	@echo "2. 退款處理 (自動批准)"
	@echo "   嘗試：'我想要為訂單 ORD-002 申請 50 美元的退款'"
	@echo "   - 事件：查詢 → 工具呼叫 → 回應"
	@echo "   - 無需上報 (金額 < 100 美元)"
	@echo ""
	@echo "3. 退款處理 (上報)"
	@echo "   嘗試：'我需要為訂單 ORD-003 申請 150 美元的退款'"
	@echo "   - 事件：查詢 → 工具呼叫 → 上報 → 回應"
	@echo "   - 觸發上報 (金額 > 100 美元)"
	@echo ""
	@echo "4. 庫存檢查"
	@echo "   嘗試：'產品 PROD-B 有庫存嗎？'"
	@echo "   - 產品可用性追蹤"
	@echo "   - 庫存水平報告"
	@echo ""
	@echo "5. 事件報告"
	@echo "   嘗試：'顯示所有互動的摘要'"
	@echo "   - 事件統計"
	@echo "   - 工具使用分析"
	@echo "   - 上報追蹤"
	@echo ""
	@echo "🔍 可觀測性功能："
	@echo "  - 事件時間軸追蹤"
	@echo "  - 帶有參數的工具呼叫記錄"
	@echo "  - 上報偵測與記錄"
	@echo "  - 指標收集 (延遲、錯誤)"
	@echo "  - 即時警報模式"
	@echo ""
	@echo "正在開啟 http://localhost:8000..."
	@echo "從下拉式選單中選擇 'observability_agent'"
	@echo ""
	adk web

test:
	@echo "正在執行測試..."
	pytest tests/ -v

demo:
	@echo "正在執行可觀測性示範..."
	@echo ""
	@echo "此示範將："
	@echo "  1. 處理 4 個客戶服務情境"
	@echo "  2. 追蹤所有事件 (查詢、工具呼叫、回應)"
	@echo "  3. 偵測並記錄上報"
	@echo "  4. 產生綜合報告"
	@echo ""
	@echo "情境："
	@echo "  - 訂單狀態查詢 (ORD-001)"
	@echo "  - 小額退款請求 (50 美元 - 已批准)"
	@echo "  - 大額退款請求 (150 美元 - 已上報)"
	@echo "  - 庫存檢查 (PROD-B)"
	@echo ""
	@echo "正在開始示範..."
	@echo ""
	python -m observability_agent.agent

coverage:
	@echo "正在執行測試並計算覆蓋率..."
	pytest tests/ --cov=observability_agent --cov-report=html --cov-report=term

clean:
	@echo "正在清理..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ 清理完成！"

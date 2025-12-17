# .PHONY 宣告這些目標為 "偽目標"，確保即使存在同名檔案，make 也會執行指令
.PHONY: help setup clean test demo dev

# help 目標：顯示所有可用的指令說明
help:
	@echo "Interactions API 基礎 - 可用指令"
	@echo "============================================"
	@echo ""
	@echo "make setup       安裝依賴並準備環境"
	@echo "make test        執行單元測試"
	@echo "make demo        執行互動式示範"
	@echo "make clean       移除快取檔案和建置產物"
	@echo ""

# setup 目標：安裝專案所需的依賴套件並設定環境
setup:
	# 從 requirements.txt 安裝 Python 依賴
	pip install -r requirements.txt
	# 以可編輯模式安裝目前專案，使其可被匯入
	pip install -e .
	# 複製 .env.example 檔案為 .env，如果 .env 已存在則忽略
	cp interactions_basic_agent/.env.example interactions_basic_agent/.env 2>/dev/null || true
	@echo ""
	@echo "✅ 設定完成！"
	@echo ""
	@echo "後續步驟："
	@echo "1. 將您的 GOOGLE_API_KEY 加入到 interactions_basic_agent/.env 檔案中"
	@echo "   或設定環境變數： export GOOGLE_API_KEY='your-key-here'"
	@echo "2. 執行 'make test' 來驗證實作"
	@echo "3. 執行 'make demo' 來查看 Interactions API 的實際運作"
	@echo ""

# test 目標：執行單元測試
test:
	@echo ""
	@echo "🧪 正在執行 Interactions API 測試..."
	@echo ""
	# 使用 pytest 執行 tests/ 目錄下的所有測試，並顯示詳細資訊
	@pytest tests/ -v --tb=short
	@echo ""
	@echo "✅ 測試驗證了："
	@echo "   • API 客戶端設定"
	@echo "   • 工具定義"
	@echo "   • 匯入路徑"
	@echo ""

# demo 目標：執行互動式示範程式
demo:
	@echo ""
	@echo "🚀 正在執行 Interactions API 示範..."
	@echo ""
	@echo "此示範將展示："
	@echo "  1. 基本的文字互動"
	@echo "  2. 使用 previous_interaction_id 的有狀態對話"
	@echo "  3. 串流式回應 (Streaming responses)"
	@echo "  4. 函式呼叫 (Function calling)"
	@echo ""
	# 執行 demo 主程式
	python -m interactions_basic_agent.demo
	@echo ""

# clean 目標：清除專案中產生的快取和建置檔案
clean:
	# 尋找並刪除所有 __pycache__ 目錄
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	# 尋找並刪除 .pytest_cache 目錄
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	# 尋找並刪除所有 .pyc 檔案
	find . -type f -name "*.pyc" -delete
	# 刪除其他建置產物和暫存檔案
	rm -rf .coverage htmlcov build dist *.egg-info
	@echo "✅ 已清除快取檔案"

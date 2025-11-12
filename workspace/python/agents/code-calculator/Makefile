.PHONY: setup install dev run test test-verbose test-cov demo validate check clean reset help

# ===== 安裝指令 =====

setup: ## 安裝 Python 依賴套件
	@echo "📦 正在安裝依賴套件..."
	@pip install -r requirements.txt
	@pip install -e .
	@echo "✅ 設定完成！請將 code_calculator/.env.example 複製為 code_calculator/.env 並加入您的 API 金鑰。"

install: setup  ## setup 的別名

# ===== 開發指令 =====

dev: ## 啟動 ADK 開發伺服器 (網頁介面)
	@echo "🚀 正在啟動 ADK 網頁介面..."
	@echo "📍 在您的瀏覽器中開啟 http://localhost:8000"
	@echo "💡 從代理程式下拉選單中選擇 'code_calculator'"
	@echo ""
	@adk web

run: dev  ## dev 的別名

# ===== 測試指令 =====

test: ## 執行所有測試
	@echo "🧪 正在執行測試..."
	@pytest tests/ -v

test-verbose: ## 執行詳細輸出的測試
	@echo "🧪 正在以詳細輸出執行測試..."
	@pytest tests/ -vv -s

test-cov: ## 執行並產出覆蓋率報告的測試
	@echo "🧪 正在執行測試並檢查覆蓋率..."
	@pytest tests/ -v --cov=code_calculator --cov-report=term-missing

# ===== 範例指令 =====

demo: ## 顯示範例提示和快速驗證
	@echo "💡 金融計算機範例提示："
	@echo ""
	@echo "📊 基本計算："
	@echo "  • '計算 50 的階乘'"
	@echo "  • '計算 [23, 25, 28, 30, 29, 27, 26, 24, 31, 28] 的標準差'"
	@echo ""
	@echo "💰 複利："
	@echo "  • '如果我投資 \$10,000，年利率 7%，每月複利一次，30 年後我會有多少錢？'"
	@echo "  • '計算複利：本金 \$5,000，年利率 6%，15 年，每季複利'"
	@echo ""
	@echo "🏠 貸款計算："
	@echo "  • '計算一筆 \$300,000 的抵押貸款，年利率 6.5%，為期 30 年的月付金'"
	@echo "  • '一筆 \$25,000 的汽車貸款，利率 4.5%，為期 5 年的月付金是多少？'"
	@echo ""
	@echo "🎯 退休規劃："
	@echo "  • '我今年 30 歲，希望在 65 歲時退休，並擁有 \$200 萬。如果我每年能賺取 8% 的報酬，我需要每月存多少錢？'"
	@echo "  • '在 20 年內，以 7% 的年報酬率，我需要每月存多少錢才能達到 \$100 萬？'"
	@echo ""
	@echo "📈 投資分析："
	@echo "  • '比較：A) 初始投資 \$50,000，利率 6%，20 年 vs B) 初始投資 \$30,000 + 每月 \$200，利率 8%，20 年'"
	@echo "  • '計算一項投資在 8 年內從 \$100,000 增長到 \$175,000 的年複合成長率 (CAGR)'"
	@echo ""
	@echo "⚖️ 損益平衡分析："
	@echo "  • '固定成本 \$50,000/月，變動成本 \$25/單位，售價 \$75/單位。損益平衡點在哪？'"
	@echo ""
	@echo "🔬 演算法實作："
	@echo "  • '實作二元搜尋，並在 [1, 5, 12, 23, 42, 67, 89, 99] 中尋找 42'"
	@echo "  • '撰寫程式碼找出 1 到 100 之間的所有質數'"
	@echo ""
	@echo "📊 資料分析："
	@echo "  • '分析銷售數據：一月 15000，二月 18000，三月 16500，四月 22000，五月 21000，六月 25000'"
	@echo ""
	@echo "若要測試：執行 make dev (然後在網頁介面中使用以上提示)"

validate: test ## 執行全面驗證
	@echo "✅ 驗證完成！"

check: test  ## validate 的別名

# ===== 清理指令 =====

clean: ## 清理快取檔案和產物
	@echo "🧹 正在清理快取檔案..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@echo "✅ 清理完成！"

reset: clean  ## 重設至乾淨狀態
	@echo "🔄 正在重設至乾淨狀態..."
	@echo "✅ 重設完成！"

# ===== 說明 =====

help: ## 顯示此說明訊息
	@echo "教學 13：程式碼執行 - 金融計算機"
	@echo ""
	@echo "可用指令："
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
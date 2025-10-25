# 教學 02：函式工具 - 財務助理代理
# 用於快速入門的簡易 Makefile

# .PHONY 用於宣告偽目標，避免與同名檔案衝突
.PHONY: help setup dev parallel-demo test clean demo

# 預設目標 - 顯示幫助訊息
# 當直接執行 `make` 時，會執行此目標
help:
	@echo "🚀 教學 02：函式工具 - 財務助理代理"
	@echo ""
	@echo "快速入門指令:"
	@echo "  make setup     - 安裝專案所需的依賴套件"
	@echo "  make dev       - 啟動財務助理代理"
	@echo "  make demo      - 執行一個快速的計算展示"
	@echo ""
	@echo "進階指令:"
	@echo "  make parallel-demo  - 啟動平行執行展示"
	@echo "  make test           - 執行所有測試"
	@echo "  make clean          - 清理生成的暫存檔案"
	@echo ""
	@echo "💡 第一次使用？ 請執行: make setup && make dev"

# 安裝依賴套件
# 讀取 requirements.txt 檔案並安裝其中定義的 Python 套件
setup:
	@echo "📦 正在安裝依賴套件..."
	pip install -r requirements.txt
	pip install -e .
	@echo "✅ 安裝完成！ 請執行 'make dev' 來啟動代理。"

# 啟動主要的財務助理
# `check-env` 是一個依賴，會先檢查環境變數是否設定
dev: check-env
	@echo "🤖 正在啟動財務助理..."
	@echo "可用的代理: finance_assistant, parallel_finance_assistant"
	@echo "請在瀏覽器中開啟 http://localhost:8000"
	adk web

# 啟動平行執行展示
# 這個展示會示範 ADK 如何同時執行多個工具
parallel-demo: check-env
	@echo "⚡ 正在啟動平行執行展示..."
	@echo "此展示將示範 ADK 如何同時執行多個工具"
	@echo "請在瀏覽器中開啟 http://localhost:8000"
	adk web

# 執行一個快速的財務計算展示
# 這個目標會直接呼叫 Python 腳本來執行三個財務計算範例
demo: check-env
	@echo "🧮 正在執行財務計算展示..."
	@echo ""
	@echo "💰 複利計算：本金 $$10,000，年利率 6%，為期 5 年"
	@python -c "from finance_assistant.agent import calculate_compound_interest; result = calculate_compound_interest(10000, 0.06, 5); print(result['report'])"
	@echo ""
	@echo "🏠 貸款月付金計算：貸款 $$300,000，年利率 4.5%，為期 30 年"
	@python -c "from finance_assistant.agent import calculate_loan_payment; result = calculate_loan_payment(300000, 0.045, 30); print(result['report'])"
	@echo ""
	@echo "🎯 每月儲蓄目標計算：目標 $$50,000，3 年內達成，年利率 5%"
	@python -c "from finance_assistant.agent import calculate_monthly_savings; result = calculate_monthly_savings(50000, 3, 0.05); print(result['report'])"
	@echo ""
	@echo "✅ 展示完成！ 現在您可以嘗試執行: make dev"

# 執行測試
# 使用 pytest 工具來執行 tests/ 目錄下的所有測試案例
test: check-env
	@echo "🧪 正在執行測試..."
	pytest tests/ -v --tb=short

# 清理專案目錄
# 刪除 Python 編譯產生的 .pyc 檔案、__pycache__ 目錄以及 pytest 的快取
clean:
	@echo "🧹 正在清理..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	@echo "✅ 清理完成！"

# 檢查環境變數 (內部使用)
# 這個目標用於確認 Google API 的認證資訊是否已設定
# 如果 GOOGLE_API_KEY 或 GOOGLE_APPLICATION_CREDENTIALS 未設定，將會顯示錯誤訊息並中止執行
check-env:
	@if [ -z "$$GOOGLE_API_KEY" ] && [ -z "$$GOOGLE_APPLICATION_CREDENTIALS" ]; then \
		echo "❌ 錯誤：認證未設定"; \
		echo ""; \
		echo "請選擇以下其中一種認證方式："; \
		echo ""; \
		echo "🔑 方法 1 - API 金鑰 (Gemini API):"; \
		echo "   export GOOGLE_API_KEY=your_api_key_here"; \
		echo "   請至此處取得免費金鑰: https://aistudio.google.com/app/apikey"; \
		echo ""; \
		echo "🔐 方法 2 - 服務帳戶 (VertexAI):"; \
		echo "   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json"; \
		echo "   export GOOGLE_CLOUD_PROJECT=your_project_id"; \
		echo "   請至此處建立憑證: https://console.cloud.google.com/iam-admin/serviceaccounts"; \
		echo ""; \
		exit 1; \
	fi
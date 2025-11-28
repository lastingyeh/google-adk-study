# 教學：GEPA (遺傳演算法-帕雷托提示最佳化)
# 用於管理此教學的 Makefile

.PHONY: help setup dev test demo real-demo clean check

# 預設目標 - 顯示說明
help:
	@echo "🧬 GEPA 最佳化教學"
	@echo ""
	@echo "快速入門指令："
	@echo "  make setup          - 安裝依賴套件"
	@echo "  make dev            - 啟動 ADK 網站介面"
	@echo "  make demo           - 顯示模擬的 GEPA 展示 (2 分鐘)"
	@echo "  make real-demo      - 執行帶有 LLM 反思的真實 GEPA"
	@echo ""
	@echo "開發指令："
	@echo "  make test           - 執行測試"
	@echo "  make check          - 執行程式碼品質檢查"
	@echo ""
	@echo "清理："
	@echo "  make clean          - 移除生成的檔案"
	@echo ""
	@echo "💡 第一次使用？請執行：make setup && make demo"
	@echo "🚀 需要進行真實最佳化？請執行：make real-demo"

# 安裝依賴套件
setup:
	@echo "📦 安裝依賴套件中..."
	pip install -r requirements.txt
	pip install -e .
	@echo "✅ 設定完成！"
	@echo ""
	@echo "後續步驟："
	@echo "  1. 設定 API 金鑰：cp gepa_agent/.env.example gepa_agent/.env"
	@echo "  2. 編輯 gepa_agent/.env 並加入您的 GOOGLE_API_KEY"
	@echo "  3. 執行：make dev"

# 啟動 ADK 網站介面
dev: check-env
	@echo "🚀 啟動 ADK 網站介面中..."
	@echo "📱 開啟 http://localhost:8000 並選擇 'gepa_agent'"
	@echo "按下 Ctrl+C 以停止"
	@echo ""
	adk web

# 執行測試
test:
	@echo "🧪 執行測試中..."
	pytest tests/ -v --tb=short -x

# 執行包含覆蓋率的測試
test-coverage:
	@echo "📊 執行包含覆蓋率的測試中..."
	pytest tests/ -v --cov=gepa_agent --cov-report=html --cov-report=term
	@echo ""
	@echo "📈 覆蓋率報告已生成於 htmlcov/index.html"

# 顯示 GEPA 演化過程的展示提示
demo:
	@echo "🧬 執行 GEPA 演化展示中..."
	@echo ""
	python gepa_demo.py

# 執行帶有實際 LLM 反思和演化的真實 GEPA
real-demo: check-env
	@echo "🧬 執行真實 GEPA 演化展示中..."
	@echo ""
	@echo "此展示使用實際的 LLM 呼叫進行反思與演化。"
	@echo "您將會被收取 API 呼叫費用 (每次執行約 $0.05-$0.10)。"
	@echo ""
	python gepa_real_demo.py

# 執行程式碼品質檢查
check:
	@echo "🔍 執行程式碼品質檢查中..."
	@echo ""
	@echo "執行 ruff..."
	ruff check gepa_agent tests
	@echo "✓ ruff 通過"
	@echo ""
	@echo "執行 black..."
	black --check gepa_agent tests
	@echo "✓ black 通過"
	@echo ""
	@echo "執行 mypy..."
	mypy gepa_agent
	@echo "✓ mypy 通過"
	@echo ""
	@echo "✅ 所有檢查皆已通過！"

# 格式化程式碼
format:
	@echo "🎨 格式化程式碼中..."
	black gepa_agent tests
	ruff check --fix gepa_agent tests
	@echo "✅ 格式化完成！"

# 清理
clean:
	@echo "🧹 清理中..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	@echo "✅ 清理完成！"

# 檢查環境變數
check-env:
	@if [ -z "$$GOOGLE_API_KEY" ] && [ -z "$$GOOGLE_APPLICATION_CREDENTIALS" ]; then \
		echo "❌ 錯誤：未設定驗證"; \
		echo ""; \
		echo "請選擇以下其中一種驗證方式："; \
		echo ""; \
		echo "🔑 方式 1 - API 金鑰 (Gemini API)："; \
		echo "   export GOOGLE_API_KEY=your_api_key_here"; \
		echo "   請至此處取得免費金鑰：https://aistudio.google.com/app/apikey"; \
		echo ""; \
		echo "🔐 方式 2 - 服務帳號 (VertexAI)："; \
		echo "   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json"; \
		echo "   export GOOGLE_CLOUD_PROJECT=your_project_id"; \
		echo ""; \
		exit 1; \
	fi

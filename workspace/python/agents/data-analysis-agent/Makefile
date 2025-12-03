# 重點摘要
# - 核心概念：自動化管理專案任務的 Makefile。
# - 關鍵技術：Make, Python venv/pip 管理。
# - 重要結論：簡化了安裝、開發、測試和清理的流程。
# - 行動項目：使用 make setup 安裝，make dev 啟動。

.PHONY: help setup dev demo test clean lint format

help:
	@echo "資料分析代理 (Streamlit 版) - 可用指令"
	@echo ""
	@echo "設定與安裝:"
	@echo "  make setup              安裝依賴項與套件"
	@echo ""
	@echo "開發:"
	@echo "  make dev                執行 Streamlit 應用程式 (localhost:8501)"
	@echo "  make demo               顯示範例提示詞與用法範例"
	@echo ""
	@echo "測試與品質:"
	@echo "  make test               執行所有測試並包含覆蓋率報告"
	@echo "  make lint               檢查程式碼品質"
	@echo "  make format             使用 black 和 isort 格式化程式碼"
	@echo ""
	@echo "清理:"
	@echo "  make clean              移除快取與生成的檔案"

setup:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -e .
	@echo "✅ 設定完成！接下來的步驟："
	@echo "   1. 複製 .env.example 到 .env"
	@echo "   2. 將您的 GOOGLE_API_KEY 新增至 .env"
	@echo "   3. 執行: make dev"

dev:
	@if [ ! -f .env ]; then \
		echo "❌ 找不到 .env 檔案！"; \
		echo "請從 .env.example 建立 .env 並新增您的 GOOGLE_API_KEY"; \
		exit 1; \
	fi
	streamlit run app.py

demo:
	@echo "📊 資料分析代理展示"
	@echo ""
	@echo "本教學展示："
	@echo "  • 用於互動式資料分析的 Streamlit UI"
	@echo "  • 直接 ADK 代理整合（無 HTTP 開銷）"
	@echo "  • CSV 檔案上傳與資料探索"
	@echo "  • 與 Gemini 2.0 Flash 進行即時聊天"
	@echo ""
	@echo "📁 範例資料："
	@echo "  建立一個簡單的 CSV 如下："
	@echo "    name,age,salary,department"
	@echo "    Alice,30,75000,Engineering"
	@echo "    Bob,28,68000,Engineering"
	@echo "    Carol,35,82000,Sales"
	@echo ""
	@echo "💬 嘗試這些問題："
	@echo "  1. '這份資料的主要見解是什麼？'"
	@echo "  2. '各部門的平均薪資是多少？'"
	@echo "  3. '顯示資料的摘要統計'"
	@echo "  4. '有任何模式或趨勢嗎？'"
	@echo ""
	@echo "🚀 開始使用："
	@echo "  1. 執行: make dev"
	@echo "  2. 上傳 CSV 檔案"
	@echo "  3. 詢問有關您資料的問題"

test:
	pytest tests/ -v --tb=short --cov=data_analysis_agent --cov-report=term-missing | cat

lint:
	flake8 data_analysis_agent/ app.py tests/ --max-line-length=100 --count --statistics | cat

format:
	black data_analysis_agent/ app.py tests/
	isort data_analysis_agent/ app.py tests/ --profile black

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .coverage -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage*" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .cache/ .pytest_cache/ htmlcov/ .tox/ *.egg-info/
	@echo "✅ 已清理快取與生成的檔案"

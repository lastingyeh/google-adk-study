# Deep Research Agent Makefile
# 此 Makefile 用於管理專案的建置、測試和執行任務

.PHONY: help setup clean test demo research

help:
	@echo "深度研究代理 (Deep Research Agent) - 可用指令"
	@echo "========================================="
	@echo ""
	@echo "make setup       安裝依賴並準備環境"
	@echo "make test        執行單元測試"
	@echo "make demo        執行快速演示 (模擬模式)"
	@echo "make research    執行實際研究任務 (需要 API 金鑰)"
	@echo "make clean       移除快取檔案和產物"
	@echo ""

setup:
	# 安裝需求套件
	pip install -r requirements.txt
	# 以可編輯模式安裝當前專案
	pip install -e .
	# 複製環境變數範例檔 (如果不存則忽略錯誤)
	cp research_agent/.env.example research_agent/.env 2>/dev/null || true
	@echo ""
	@echo "✅ 設定完成！"
	@echo ""
	@echo "後續步驟："
	@echo "1. 將您的 GOOGLE_API_KEY 新增至 research_agent/.env"
	@echo "   或設定：export GOOGLE_API_KEY='your-key-here'"
	@echo "2. 執行 'make test' 以驗證實作"
	@echo "3. 執行 'make demo' 查看模擬演示"
	@echo "4. 執行 'make research' 進行實際研究 (會消耗 Token！)"
	@echo ""

test:
	@echo ""
	@echo "🧪 正在執行深度研究代理測試..."
	@echo ""
	# 執行 pytest，顯示詳細資訊與簡短的回溯
	@pytest tests/ -v --tb=short
	@echo ""
	@echo "✅ 測試驗證項目："
	@echo "   • 代理設定 (Agent configuration)"
	@echo "   • 研究任務建立 (Research task creation)"
	@echo "   • 串流工具 (Streaming utilities)"
	@echo "   • 錯誤處理 (Error handling)"
	@echo ""

demo:
	@echo ""
	@echo "🔬 深度研究代理演示 (模擬模式)"
	@echo "========================================"
	@echo ""
	@echo "這展示了無需 API 呼叫的深度研究結構。"
	@echo "使用 'make research' 進行實際研究。"
	@echo ""
	# 執行演示模組，使用 --mock 參數
	python -m research_agent.demo --mock
	@echo ""

research:
	@echo ""
	@echo "🔬 正在執行深度研究任務"
	@echo "=============================="
	@echo ""
	@echo "⚠️  這將進行實際的 API 呼叫並消耗 Token！"
	@echo ""
	# 執行演示模組 (實際模式)
	python -m research_agent.demo
	@echo ""

clean:
	# 清理 __pycache__ 目錄
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	# 清理 .pytest_cache 目錄
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	# 清理 .pyc 檔案
	find . -type f -name "*.pyc" -delete
	# 清理建置產物
	rm -rf .coverage htmlcov build dist *.egg-info
	@echo "✅ 已清理快取檔案"

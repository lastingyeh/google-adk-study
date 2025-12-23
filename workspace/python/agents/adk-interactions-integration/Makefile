.PHONY: help setup clean test demo dev

help:
	@echo "ADK Interactions Integration - 可用指令"
	@echo "=================================================="
	@echo ""
	@echo "make setup       安裝依賴套件並準備環境"
	@echo "make test        執行單元測試"
	@echo "make dev         啟動 ADK 網頁介面"
	@echo "make demo        執行演示"
	@echo "make clean       移除快取檔案與產物"
	@echo ""

setup:
	pip install -r requirements.txt
	pip install -e .
	cp adk_interactions_agent/.env.example adk_interactions_agent/.env 2>/dev/null || true
	@echo ""
	@echo "✅ 設定完成！"
	@echo ""
	@echo "下一步："
	@echo "1. 新增您的 GOOGLE_API_KEY 至 adk_interactions_agent/.env"
	@echo "   或設定：export GOOGLE_API_KEY='your-key-here'"
	@echo "2. 執行 'make test' 以驗證實作"
	@echo "3. 執行 'make dev' 以啟動 ADK 網頁介面"
	@echo ""

dev:
	@echo ""
	@echo "🚀 正在啟動 ADK 網頁介面..."
	@echo ""
	@echo "📝 此代理展示了："
	@echo "   • 具備 Interactions API 後端的 ADK"
	@echo "   • 伺服器端狀態管理"
	@echo "   • 工具協調 (Tool orchestration)"
	@echo ""
	@echo "開啟 http://localhost:8000 並選擇 'adk_interactions_agent'"
	@echo ""
	adk web

test:
	@echo ""
	@echo "🧪 正在執行 ADK Interactions Integration 測試..."
	@echo ""
	@pytest tests/ -v --tb=short
	@echo ""
	@echo "✅ 測試驗證項目："
	@echo "   • 代理 (Agent) 設定"
	@echo "   • 工具 (Tool) 定義"
	@echo "   • ADK 整合模式"
	@echo ""

demo:
	@echo ""
	@echo "🔬 ADK Interactions Integration 演示"
	@echo "====================================="
	@echo ""
	python -m adk_interactions_agent.demo
	@echo ""

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov build dist *.egg-info
	@echo "✅ 已清除快取檔案"

# 重點摘要
#
# - **核心概念**：自動化專案管理腳本，簡化開發、測試與部署流程。
# - **關鍵技術**：Make, pip, pytest, ADK CLI。
# - **重要結論**：透過標準化指令確保環境一致性與操作便利性。
# - **行動項目**：初次使用請務必執行 `make setup` 並設定 API Key。
#
# 流程圖 (Setup 流程)
# ```mermaid
# graph TD
#     A[開始 make setup] --> B[安裝 requirements.txt]
#     B --> C[安裝當前套件 (editable mode)]
#     C --> D{檢查 .env 是否存在}
#     D -->|否| E[複製 .env.example 到 .env]
#     D -->|是| F[跳過複製]
#     E --> G[顯示完成訊息與下一步驟]
#     F --> G
# ```

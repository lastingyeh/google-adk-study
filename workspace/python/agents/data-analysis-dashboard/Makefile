.PHONY: help setup setup-agent setup-frontend dev dev-agent dev-frontend test demo clean

help:
	@echo "數據分析儀表板 - 可用指令："
	@echo ""
	@echo "安裝指令："
	@echo "  make setup          - 安裝所有相依套件（Agent + Frontend）"
	@echo "  make setup-agent    - 僅安裝 Agent 相依套件"
	@echo "  make setup-frontend - 僅安裝 Frontend 相依套件"
	@echo ""
	@echo "開發指令："
	@echo "  make dev            - 同時執行 Agent 和 Frontend"
	@echo "  make dev-agent      - 執行 Agent 後端伺服器（port 8000）"
	@echo "  make dev-frontend   - 執行 Frontend 開發伺服器（port 5173）"
	@echo ""
	@echo "測試指令："
	@echo "  make test           - 執行所有測試並產出覆蓋率報告"
	@echo ""
	@echo "演示指令："
	@echo "  make demo           - 顯示演示提示和使用範例"
	@echo ""
	@echo "清理指令："
	@echo "  make clean          - 移除快取檔案和建置產物"
	@echo ""
	@echo "完整工作流程："
	@echo "  1. make setup       - 安裝相依套件"
	@echo "  2. 設定 .env        - 加入您的 GOOGLE_API_KEY"
	@echo "  3. make dev         - 啟動後端和前端"
	@echo "  4. 在瀏覽器中開啟 http://localhost:5173"

setup: setup-agent setup-frontend
	@echo "✅ 完整安裝完成！"
	@echo ""
	@echo "下一步："
	@echo "  1. 複製 agent/.env.example 到 agent/.env"
	@echo "  2. 將您的 GOOGLE_API_KEY 加入 agent/.env"
	@echo "  3. 在一個終端機執行 'make dev-agent'"
	@echo "  4. 在另一個終端機執行 'make dev-frontend'"

setup-agent:
	@echo "📦 安裝 Agent 相依套件..."
	cd agent && python -m venv venv || true
	cd agent && . venv/bin/activate && pip install --upgrade pip
	cd agent && . venv/bin/activate && pip install -r requirements.txt
	pip install -e .
	@echo "✅ Agent 安裝完成！"

setup-frontend:
	@echo "📦 安裝 Frontend 相依套件..."
	cd frontend && npm install
	@echo "✅ Frontend 安裝完成！"

dev:
	@echo "🚀 啟動 Agent 後端和 Frontend 伺服器..."
	@echo ""
	@echo "將會啟動："
	@echo "  後端：http://localhost:8000 (ADK agent)"
	@echo "  前端：http://localhost:5173 (Data Analysis Dashboard)"
	@echo ""
	@echo "按 Ctrl+C 停止兩個伺服器"
	@echo ""
	@$(MAKE) dev-parallel

dev-agent:
	@echo "🚀 啟動 Agent 後端伺服器..."
	@echo "後端將在以下位置可用：http://localhost:8000"
	@echo "健康檢查：http://localhost:8000/health"
	@echo ""
	cd agent && . venv/bin/activate && python agent.py

dev-frontend:
	@echo "🚀 啟動 Frontend 開發伺服器..."
	@echo "前端將在以下位置可用：http://localhost:5173"
	@echo ""
	cd frontend && npm run dev

# 平行啟動後端和前端（內部使用）
dev-parallel:
	@trap 'kill 0' EXIT; \
	(cd agent && . venv/bin/activate && python agent.py) & \
	(cd frontend && npm run dev) & \
	wait

test:
	@echo "🧪 執行測試並產出覆蓋率報告..."
	. agent/venv/bin/activate && pytest tests/ -v --cov=agent --cov-report=term-missing --cov-report=html
	@echo ""
	@echo "✅ 測試完成！覆蓋率報告已生成於 htmlcov/"

demo:
	@echo "📊 數據分析儀表板 - 演示指南"
	@echo "========================================"
	@echo ""
	@echo "先決條件："
	@echo "  - 後端執行於 http://localhost:8000"
	@echo "  - 前端執行於 http://localhost:5173"
	@echo ""
	@echo "範例工作流程："
	@echo "  1. 在瀏覽器中開啟 http://localhost:5173"
	@echo "  2. 上傳 CSV 檔案（銷售數據、客戶數據等）"
	@echo "  3. 嘗試這些提示："
	@echo ""
	@echo "範例提示："
	@echo "  • '幫我總結這些數據'"
	@echo "  • '關鍵統計數據是什麼？'"
	@echo "  • '顯示銷售隨時間變化的折線圖'"
	@echo "  • '建立比較產品的長條圖'"
	@echo "  • '數據中有什麼相關性？'"
	@echo "  • '分析數據集中的趨勢'"
	@echo ""
	@echo "範例 CSV 數據："
	@echo "  month,sales,expenses"
	@echo "  Jan,10000,7000"
	@echo "  Feb,12000,7500"
	@echo "  Mar,11500,7200"
	@echo "  Apr,13000,7800"
	@echo ""
	@echo "功能："
	@echo "  ✓ CSV 數據載入與解析"
	@echo "  ✓ 統計分析（摘要、相關性、趨勢）"
	@echo "  ✓ 互動式圖表生成（折線圖、長條圖、散佈圖）"
	@echo "  ✓ 自然語言查詢"
	@echo "  ✓ 即時 Agent 回應"

clean:
	@echo "🧹 清理中..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	cd frontend && rm -rf dist node_modules 2>/dev/null || true
	@echo "✅ 清理完成！"

#### 重點摘要 (程式碼除外)
# - **核心概念**：自動化專案設置、開發、測試和清理流程的 Makefile。
# - **關鍵技術**：Make, Shell Scripting, Python venv, npm。
# - **重要結論**：提供了一鍵式的指令來管理專案生命週期，包括後端 (Python/FastAPI) 和前端 (Node/React) 的相依性管理與執行。
# - **行動項目**：使用者需設定 `.env` 中的 `GOOGLE_API_KEY` 才能完整使用功能。

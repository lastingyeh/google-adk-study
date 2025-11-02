# 教學 05：平行處理 - 旅遊規劃系統
# 用於開發、測試和部署的 Makefile

.PHONY: help setup dev test clean demo

# 預設目標
help:
	@echo "教學 05：平行處理 - 旅遊規劃系統"
	@echo ""
	@echo "可用指令："
	@echo "  setup    安裝相依套件並建立開發環境"
	@echo "  dev      啟動開發伺服器 (ADK 網頁介面)"
	@echo "  test     執行完整測試套件"
	@echo "  demo     執行旅遊規劃器快速展示"
	@echo "  clean    清理暫存檔案和快取"
	@echo "  help     顯示此說明訊息"

# 建立開發環境
setup:
	@echo "正在建立教學 05 開發環境..."
	pip install -r requirements.txt
	pip install -e .
	@echo "建立完成！請複製 travel_planner/.env.example 到 travel_planner/.env 並新增您的 API 金鑰。"

# 啟動開發伺服器 (★ 主要開發指令)
dev: check-env
	@echo "正在啟動 ADK 開發伺服器..."
	@echo "在瀏覽器開啟 http://localhost:8000"
	@echo "從代理程式清單中選擇 'travel_planner'"
	@echo ""
	@echo "可嘗試的範例提示："
	@echo "  - '規劃巴黎 3 日遊'"
	@echo "  - '紐約週末旅遊'"
	@echo "  - '2 人東京 5 日遊'"
	@echo ""
	adk web

# 執行測試 (★ 品質檢查指令)
test:
	@echo "正在執行完整測試套件..."
	pytest tests/ -v --tb=short

# 快速展示 (★ 驗證安裝指令)
demo:
	@echo "正在執行旅遊規劃器展示..."
	@echo "這將測試基本功能"
	@python -c "from travel_planner.agent import root_agent; print('✅ 旅遊規劃器載入成功！'); print(f'代理程式名稱：{root_agent.name}'); print(f'管線階段數量：{len(root_agent.sub_agents)}'); print('第一階段（平行搜尋）有', len(root_agent.sub_agents[0].sub_agents), '個並行代理程式'); print('✅ 展示完成！')"

# 清理 (★ 維護指令)
clean:
	@echo "正在清理暫存檔案..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "清理完成！"

# 檢查環境變數 (內部使用) (★ 身份驗證檢查)
check-env:
	@if [ -z "$$GOOGLE_API_KEY" ] && [ -z "$$GOOGLE_APPLICATION_CREDENTIALS" ]; then \
		echo "❌ 錯誤：未設定身份驗證"; \
		echo ""; \
		echo "請選擇以下其中一種身份驗證方法："; \
		echo ""; \
		echo "🔑 方法 1 - API 金鑰 (Gemini API)："; \
		echo "   export GOOGLE_API_KEY=your_api_key_here"; \
		echo "   在此取得免費金鑰：https://aistudio.google.com/app/apikey"; \
		echo ""; \
		echo "🔐 方法 2 - 服務帳戶 (VertexAI)："; \
		echo "   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json"; \
		echo "   export GOOGLE_CLOUD_PROJECT=your_project_id"; \
		echo "   在此建立憑證：https://console.cloud.google.com/iam-admin/serviceaccounts"; \
		echo ""; \
		exit 1; \
	fi
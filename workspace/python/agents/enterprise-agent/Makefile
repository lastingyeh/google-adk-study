# enterprise-agent: Gemini Enterprise - 企業級 Agent 平台
# 用於開發、測試和部署的 Makefile

.PHONY: help setup dev test clean demo

# 預設目標
help:
	@echo "enterprise-agent: Gemini Enterprise - 企業級 Agent 平台"
	@echo ""
	@echo "可用指令:"
	@echo "  setup    安裝依賴並設定開發環境"
	@echo "  dev      啟動開發伺服器 (ADK 網頁介面)"
	@echo "  test     執行完整的測試套件"
	@echo "  demo     執行企業潛在客戶資格審查員的快速演示"
	@echo "  clean    清理暫存檔案和快取"
	@echo "  help     顯示此說明訊息"

# 設定開發環境
setup:
	@echo "正在設定 enterprise-agent 開發環境..."
	pip install -r requirements.txt
	pip install -e .
	@echo "設定完成！請將 enterprise_agent/.env.example 複製到 enterprise_agent/.env 並加入您的 API 金鑰。"

# 啟動開發伺服器
dev: check-env
	@echo "正在啟動 ADK 開發伺服器..."
	@echo "在瀏覽器中開啟 http://localhost:8000"
	@echo "從 agent 列表中選擇 'lead_qualifier'"
	@echo ""
	@echo "可嘗試的提示範例:"
	@echo "  - 'Qualify TechCorp as a sales lead with enterprise budget' (評估 TechCorp 是否為具有企業預算的銷售潛在客戶)"
	@echo "  - 'Score FinanceGlobal with business budget tier' (以商業預算層級為 FinanceGlobal 評分)"
	@echo "  - 'Check if HealthPlus qualifies for our enterprise tier' (檢查 HealthPlus 是否符合我們的企業層級資格)"
	@echo "  - 'Compare us to CompetitorX for the TechCorp opportunity' (針對 TechCorp 的機會，將我們與 CompetitorX 進行比較)"
	@echo ""
	adk web

# 執行測試
test:
	@echo "正在執行完整的測試套件..."
	pytest tests/ -v --tb=short

# 快速演示
demo:
	@echo "正在執行企業潛在客戶資格審查員演示..."
	@echo ""
	@python -c "from enterprise_agent.agent import root_agent, check_company_size, score_lead; print('✅ Enterprise agent 載入成功！'); print(f'Agent 名稱: {root_agent.name}'); print(f'工具數量: {len(root_agent.tools)}'); print(''); print('測試資格審查工作流程:'); result = check_company_size('TechCorp'); print(f'  公司查詢: {result[\"report\"]}'); score = score_lead(250, 'technology', 'enterprise'); print(f'  潛在客戶評分: {score[\"report\"]}'); print(''); print('✅ 演示完成！')"

# 清理
clean:
	@echo "正在清理暫存檔案..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "清理完成！"

# 檢查環境 (內部使用)
check-env:
	@if [ -z "$$GOOGLE_API_KEY" ] && [ -z "$$GOOGLE_APPLICATION_CREDENTIALS" ]; then \
		echo "❌ 錯誤: 未設定身份驗證"; \
		echo ""; \
		echo "請選擇以下一種身份驗證方法:"; \
		echo ""; \
		echo "🔑 方法 1 - API 金鑰 (Gemini API):"; \
		echo "   export GOOGLE_API_KEY=your_api_key_here"; \
		echo "   在以下網址獲取免費金鑰: https://aistudio.google.com/app/apikey"; \
		echo ""; \
		echo "🔐 方法 2 - 服務帳戶 (VertexAI):"; \
		echo "   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json"; \
		echo "   export GOOGLE_CLOUD_PROJECT=your_project_id"; \
		echo "   在以下網址建立憑證: https://console.cloud.google.com/iam-admin/serviceaccounts"; \
		echo ""; \
		exit 1; \
	fi

## 重點摘要 (程式碼除外)
# - **核心概念**：自動化開發任務管理
# - **關鍵技術**：Make, Python, pip, pytest, adk cli
# - **重要結論**：提供了一組標準的指令來簡化安裝、測試、開發和演示流程。
# - **行動項目**：無

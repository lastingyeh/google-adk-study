# 教學 06：多代理系統 - 內容發布系統
# 用於開發、測試和部署的 Makefile

.PHONY: help setup dev test clean demo

# 預設目標
help:
	@echo "教學 06：多代理系統 - 內容發布系統"
	@echo ""
	@echo "可用命令："
	@echo "  setup    安裝依賴項並設置開發環境"
	@echo "  dev      啟動開發伺服器（ADK 網頁介面）"
	@echo "  test     執行完整測試套件"
	@echo "  demo     執行內容發布系統的快速示範"
	@echo "  clean    清理暫存檔案和快取"
	@echo "  help     顯示此幫助訊息"

# 設置開發環境
setup:
	@echo "正在設置教學 06 開發環境..."
	pip install -r requirements.txt
	pip install -e .
	@echo "設置完成！複製 content_publisher/.env.example 到 content_publisher/.env 並添加您的 API 金鑰。"

# 啟動開發伺服器
dev: check-env
	@echo "正在啟動 ADK 開發伺服器..."
	@echo "在瀏覽器中打開 http://localhost:8000"
	@echo "從代理列表中選擇 'content_publisher'"
	@echo ""
	@echo "可嘗試的範例提示："
	@echo "  - '撰寫一篇關於人工智慧在醫療保健中應用的文章'"
	@echo "  - '創建一篇關於再生能源採用的文章'"
	@echo "  - '撰寫關於遠程工作未來的文章'"
	@echo "  - '創建一篇解釋量子計算突破的文章'"
	@echo ""
	adk web

# 執行測試
test:
	@echo "正在執行完整測試套件..."
	pytest tests/ -v --tb=short

# 快速示範
demo:
	@echo "正在執行內容發布系統示範..."
	@echo "這將測試基本功能"
	@python -c "from content_publisher.agent import root_agent; print('✅ 內容發布系統載入成功！'); print(f'代理名稱：{root_agent.name}'); print(f'管道階段數量：{len(root_agent.sub_agents)}'); print('階段 1（並行研究）有', len(root_agent.sub_agents[0].sub_agents), '個併發管道'); print('✅ 示範完成！')"

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

# 檢查環境（內部使用）
check-env:
	@if [ -z "$$GOOGLE_API_KEY" ] && [ -z "$$GOOGLE_APPLICATION_CREDENTIALS" ]; then \
		echo "❌ 錯誤：未配置身份驗證"; \
		echo ""; \
		echo "請選擇以下身份驗證方法之一："; \
		echo ""; \
		echo "🔑 方法 1 - API 金鑰（Gemini API）："; \
		echo "   export GOOGLE_API_KEY=your_api_key_here"; \
		echo "   在此獲取免費金鑰：https://aistudio.google.com/app/apikey"; \
		echo ""; \
		echo "🔐 方法 2 - 服務帳戶（VertexAI）："; \
		echo "   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json"; \
		echo "   export GOOGLE_CLOUD_PROJECT=your_project_id"; \
		echo "   在此創建憑證：https://console.cloud.google.com/iam-admin/serviceaccounts"; \
		echo ""; \
		exit 1; \
	fi
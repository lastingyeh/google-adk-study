# 教學 20：YAML 設定 - 宣告式代理人設定
# 用於 YAML 基礎代理人設定的 Makefile

.PHONY: help setup dev test clean demo validate-config

# 預設目標 - 顯示幫助
help:
	@echo "🚀 教學 20：YAML 設定"
	@echo ""
	@echo "快速開始指令："
	@echo "  make setup          - 安裝依賴項"
	@echo "  make validate-config - 驗證 YAML 設定"
	@echo "  make dev            - 啟動 YAML 設定的代理人"
	@echo "  make demo           - 執行快速演示"
	@echo ""
	@echo "進階指令："
	@echo "  make test           - 執行所有測試"
	@echo "  make clean          - 清理產生的檔案"
	@echo ""
	@echo "💡 第一次使用？請執行：make setup && make validate-config && make dev"

# 安裝依賴項
setup:
	@echo "📦 正在安裝依賴項..."
	pip install -r requirements.txt
	pip install -e .
	@echo "✅ 設定完成！執行 'make validate-config' 來檢查 YAML。"

# 驗證 YAML 設定
validate-config:
	@echo "🔍 正在驗證 YAML 設定..."
	python -c "import yaml; from google.adk.agents import config_agent_utils; agent = config_agent_utils.from_config('customer_support/root_agent.yaml'); print(f'✅ 設定有效：{agent.name}'); print(f'   子代理人：{len(agent.sub_agents) if hasattr(agent, \"sub_agents\") else 0}'); print(f'   工具：{len(agent.tools) if hasattr(agent, \"tools\") else 0}')"

# 啟動 YAML 設定的代理人
dev: check-env validate-config
	@echo "🤖 正在啟動 YAML 設定的客戶支援代理人..."
	@echo ""
	@echo "🔧 代理人功能："
	@echo "   • 客戶狀態檢查 (高級/標準)"
	@echo "   • 訂單追蹤與運送資訊"
	@echo "   • 包含診斷的技術支援"
	@echo "   • 帳單歷史記錄與退款處理"
	@echo "   • 支援工單建立與管理"
	@echo ""
	@echo "📱 網頁介面：http://localhost:8000"
	@echo "🎯 代理人：從下拉選單選擇 'customer_support'"
	@echo ""
	@echo "💬 試試這些範例提示："
	@echo "   • '檢查客戶 CUST-001 的狀態'"
	@echo "   • '訂單 ORD-001 的狀態為何？'"
	@echo "   • '我需要協助解決登入錯誤'"
	@echo "   • '顯示客戶 CUST-001 的帳單歷史記錄'"
	@echo ""
	@echo "⚡ 伺服器將啟動並在下方顯示連線詳情..."
	@echo "   按 Ctrl+C 停止伺服器"
	@echo ""
	adk web

# 執行快速演示
demo: check-env validate-config
	@echo "🎯 正在執行客戶支援演示..."
	@echo ""
	@echo "💬 在 ADK 網頁 UI 中試試這些範例提示："
	@echo ""
	@echo "📋 客戶狀態與訂單："
	@echo "   • '檢查客戶 CUST-001 的狀態'"
	@echo "   • '訂單 ORD-001 的狀態為何？'"
	@echo "   • '你能追蹤訂單 ORD-001 的運送狀況嗎？'"
	@echo ""
	@echo "🔧 技術支援："
	@echo "   • '我需要協助解決登入錯誤'"
	@echo "   • '我的應用程式一直崩潰 - 你能執行診斷嗎？'"
	@echo "   • '我該如何重設密碼？'"
	@echo ""
	@echo "💰 帳單與退款："
	@echo "   • '顯示客戶 CUST-001 的帳單歷史記錄'"
	@echo "   • '我想要訂單 ORD-002 的退款 $75'"
	@echo "   • '我想要將付款方式更新為 PayPal'"
	@echo ""
	@echo "🎫 支援工單："
	@echo "   • '我需要取消訂單 ORD-002，因為我改變主意了'"
	@echo "   • '為我的連線問題建立一個支援工單'"
	@echo ""
	@echo "✅ 演示準備就緒！開啟 http://localhost:8000 並選擇 'customer_support'"

# 執行測試
test: check-env validate-config
	@echo "🧪 正在執行測試..."
	pytest tests/ -v --tb=short

# 清理
clean:
	@echo "🧹 正在清理..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	@echo "✅ 清理完成！"

# 檢查環境 (內部使用)
check-env:
	@if [ -z "$$GOOGLE_API_KEY" ] && [ -z "$$GOOGLE_APPLICATION_CREDENTIALS" ]; then \
		echo "❌ 錯誤：未設定驗證"; \
		echo ""; \
		echo "請選擇以下其中一種驗證方式："; \
		echo ""; \
		echo "🔑 方式 1 - API 金鑰 (Gemini API)："; \
		echo "   export GOOGLE_API_KEY=您的_api_key"; \
		echo "   在此獲取免費金鑰：https://aistudio.google.com/app/apikey"; \
		echo ""; \
		echo "🔐 方式 2 - 服務帳戶 (VertexAI)："; \
		echo "   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json"; \
		echo "   export GOOGLE_CLOUD_PROJECT=您的_project_id"; \
		echo "   在此建立憑證：https://console.cloud.google.com/iam-admin/serviceaccounts"; \
		echo ""; \
		exit 1; \
	fi

# 重點摘要
# - **核心概念**：使用 Makefile 自動化專案設定、驗證、開發伺服器啟動和測試流程。
# - **關鍵技術**：Make、Shell Scripting、Python CLI、ADK CLI (adk web)。
# - **重要結論**：提供了標準化的開發工作流程，簡化了依賴安裝 (`setup`)、配置驗證 (`validate-config`) 和應用啟動 (`dev`, `demo`) 的步驟。
# - **行動項目**：確保在使用 `make dev` 或 `make demo` 前已設定好 Google API 認證環境變數。

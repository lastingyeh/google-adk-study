# 教學 28: 透過 LiteLLM 使用其他大型語言模型 (LLM)
# 用於管理 multi-LLM agent 的 Makefile

.PHONY: help setup dev test clean demo

# 預設目標 - 顯示說明
help:
	@echo "🚀 教學 28: 透過 LiteLLM 使用其他 LLM"
	@echo ""
	@echo "快速入門指令:"
	@echo "  make setup     - 安裝依賴套件"
	@echo "  make dev       - 啟動 multi-LLM agent"
	@echo "  make demo      - 執行互動式 multi-LLM 範例"
	@echo ""
	@echo "進階指令:"
	@echo "  make test      - 執行所有測試"
	@echo "  make clean     - 清理生成的檔案"
	@echo ""
	@echo "💡 第一次使用？請執行: make setup && make dev"
	@echo ""
	@echo "⚠️  先決條件:"
	@echo "  - OpenAI API 金鑰: export OPENAI_API_KEY='sk-...'"
	@echo "  - Anthropic API 金鑰: export ANTHROPIC_API_KEY='sk-ant-...'"
	@echo "  - 可選: 安裝 Ollama 以使用本地的 Granite 4 模型 (請參考 https://ollama.com)"

# 安裝依賴套件
setup:
	@echo "📦 正在安裝依賴套件..."
	pip install -r requirements.txt
	pip install -e .
	@echo "✅ 設定完成！請執行 'make dev' 來啟動 agent。"

# 啟動 multi-LLM agent
dev: check-env
	@echo "🤖 正在啟動 Multi-LLM Agent 範例..."
	@echo "📱 在您的瀏覽器中開啟 http://localhost:8000"
	@echo "🎯 從下拉選單中選擇 'multi_llm_agent'"
	@echo ""
	@echo "🎬 這個範例的功能："
	@echo "   • 測試 4 種不同的 AI 模型：OpenAI GPT-4o-mini, Claude 3.7 Sonnet,"
	@echo "     Ollama Granite 4 (本地), 以及另一個 GPT-4o-mini 設定"
	@echo "   • 所有 agent 都使用相同的工具：數學計算機、天氣資訊、情緒分析"
	@echo "   • 比較不同模型對於相同提示的回應"
	@echo ""
	@echo "💬 可以嘗試的範例問題："
	@echo "   • '15 的平方是多少？' (使用 calculate_square 工具)"
	@echo "   • '舊金山的天氣如何？' (使用 get_weather 工具)"
	@echo "   • '分析這段文字：我喜歡這個令人驚嘆的新技術！' (情緒分析)"
	@echo "   • '用簡單的詞彙解釋量子計算' (一般推理)"
	@echo "   • '比較 OpenAI、Claude 和本地模型' (元討論)"
	@echo ""
	@echo "🔄 在不同的 agent 之間切換，查看不同模型的回應！"
	adk web

# 執行範例
demo:
	@echo "🎬 正在執行 Multi-LLM 範例..."
	@echo ""
	@echo "🤖 這個範例將用樣本查詢測試不同的 LLM"
	@echo "💡 請確保您已為想要測試的模型設定了 API 金鑰"
	@echo ""
	python -m multi_llm_agent.examples.demo

# 執行測試
test: check-env
	@echo "🧪 正在執行測試..."
	pytest tests/ -v --tb=short

# 清理
clean:
	@echo "🧹 正在清理..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	rm -rf *.egg-info
	@echo "✅ 清理完成！"

# 檢查環境 (內部使用)
check-env:
	@if [ -z "$$GOOGLE_API_KEY" ] && [ -z "$$GOOGLE_APPLICATION_CREDENTIALS" ]; then \
		echo "❌ 錯誤：Google 驗證未設定"; \
		echo ""; \
		echo "請選擇以下其中一種驗證方式："; \
		echo ""; \
		echo "🔑 方法 1 - API 金鑰 (Gemini API):"; \
		echo "   export GOOGLE_API_KEY=your_api_key_here"; \
		echo "   請至此處獲取免費金鑰: https://aistudio.google.com/app/apikey"; \
		echo ""; \
		echo "🔐 方法 2 - 服務帳號 (VertexAI):"; \
		echo "   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json"; \
		echo "   export GOOGLE_CLOUD_PROJECT=your_project_id"; \
		echo "   請至此處建立憑證: https://console.cloud.google.com/iam-admin/serviceaccounts"; \
		echo ""; \
		exit 1; \
	fi
	@echo "⚠️  注意：對於 OpenAI 範例，也請設定 OPENAI_API_KEY"
	@echo "⚠️  注意：對於 Claude 範例，也請設定 ANTHROPIC_API_KEY"

# 教學 17：Agent-to-Agent 通訊 - ADK 官方實作
# 用於設定、開發、測試與展示的 Makefile
# 已更新為使用 Google ADK 官方模式與 adk api_server 指令

.PHONY: help setup dev test demo clean lint format start-agents stop-agents check-agents

# 預設目標
help:
	@printf "\n🚀 教學 17：Agent-to-Agent 通訊 (官方 ADK)\n\n"
	@printf "可用指令：\n"
	@printf "  %-15s %s\n" "setup" "安裝依賴套件並設定環境"
	@printf "  %-15s %s\n" "start-agents" "啟動所有遠端 A2A agents (官方 ADK)"
	@printf "  %-15s %s\n" "stop-agents" "停止所有執行中的 agents (清除)"
	@printf "  %-15s %s\n" "check-agents" "檢查 agent 狀態與可用性"
	@printf "  %-15s %s\n" "dev" "啟動 ADK 網站介面"
	@printf "  %-15s %s\n" "test" "執行所有測試"
	@printf "  %-15s %s\n" "demo" "顯示教學總覽與範例"
	@printf "  %-15s %s\n" "clean" "清除快取檔案與產物"
	@printf "  %-15s %s\n" "lint" "執行程式碼風格檢查"
	@printf "  %-15s %s\n" "format" "使用 black 與 isort 格式化程式碼"
	@printf "\n"

# 設定環境
setup:
	@printf "📦 正在設定教學 17 環境...\n"
	@pip install -r requirements.txt || { printf "❌ 安裝 requirements 失敗\n"; exit 1; }
	@pip install -e . || { printf "❌ 安裝主要套件失敗\n"; exit 1; }
	@printf "✅ 設定完成！\n"
	@printf "📋 Google ADK 版本：$(shell pip show google-adk | grep Version | cut -d' ' -f2)\n"
	@printf "💡 請將 a2a_orchestrator/.env.example 複製為 .env 並加入您的 API 金鑰。\n"

# 開發模式 - 啟動 ADK 網站介面
dev:
	@printf "🌐 正在啟動 ADK 網站介面...\n"
	@printf "   開啟：http://localhost:8000\n"
	@printf "   從 agent 下拉選單中選擇：'a2a_orchestrator'\n\n"
	@adk web

# 執行測試
test:
	@printf "🧪 正在執行測試...\n"
	@pytest tests/ -v --tb=short

# 展示 - 顯示範例用法
demo:
	@printf "\n🎯 教學 17：Agent-to-Agent 通訊 (官方 ADK)\n\n"
	@printf "本教學展示使用官方 Google ADK 進行分散式 agent 的協調作業。\n\n"
	@printf "🔧 主要功能：\n"
	@printf "  • 用於 A2A 通訊的官方 RemoteA2aAgent\n"
	@printf "  • 透過 .well-known/agent-card.json 進行 Agent 探索\n"
	@printf "  • 具有自動委派功能的子 agent 模式\n"
	@printf "  • 三個使用官方 ADK 模式的特化遠端 agents\n\n"
	@printf "🤖 遠端 Agents：\n"
	@printf "  📚 研究：http://localhost:8001 (網路搜尋、事實查核)\n"
	@printf "  📊 分析：http://localhost:8002 (資料分析、洞察)\n"
	@printf "  ✍️  內容：http://localhost:8003 (內容創作、格式化)\n\n"
	@printf "💡 範例查詢：\n"
	@printf "  • '研究量子計算的發展並建立摘要'\n"
	@printf "  • '分析電動車市場趨勢'\n"
	@printf "  • '為我們的人工智慧平台建立技術文件'\n\n"
	@printf "🚀 快速入門：\n"
	@printf "  1. make setup\n"
	@printf "  2. 將 .env.example 複製為 .env + 加入 GOOGLE_API_KEY\n"
	@printf "  3. make start-agents  (啟動官方 ADK A2A 伺服器)\n"
	@printf "  4. make check-agents  (驗證通訊是否正常)\n"
	@printf "  5. make dev          (啟動 ADK 網站介面)\n\n"
	@printf "🔧 管理指令：\n"
	@printf "  • make check-agents  (驗證所有 agents 是否正在執行)\n"
	@printf "  • make stop-agents   (清除並關機)\n"
	@printf "  • ./start_a2a_servers.sh  (直接使用腳本)\n"
	@printf "  • ./stop_a2a_servers.sh   (直接清除)\n\n"
	@printf "✨ 官方 ADK 實作：\n"
	@printf "  • 使用 google.adk.agents 的 RemoteA2aAgent 類別\n"
	@printf "  • 用於公開 agents 的官方 to_a2a() 函式\n"
	@printf "  • 自動產生的 .well-known/agent-card.json\n"
	@printf "  • 用於 A2A 伺服器的 uvicorn + to_a2a() 模式\n\n"

# 清理
clean:
	@printf "🧹 正在清理...\n"
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".adk_cache" -exec rm -rf {} + 2>/dev/null || true
	@rm -f .agent_pids 2>/dev/null || true
	@printf "✅ 清理完成。\n"

# 程式碼風格檢查
lint:
	@printf "🔍 正在執行程式碼風格檢查...\n"
	@flake8 a2a_orchestrator tests --max-line-length=100 || { printf "❌ 程式碼風格檢查失敗\n"; exit 1; }
	@printf "✅ 程式碼風格檢查通過 (格式可能需要注意)。\n"

# 程式碼格式化
format:
	@printf "🎨 正在格式化程式碼...\n"
	@isort a2a_orchestrator tests || { printf "❌ 匯入排序失敗\n"; exit 1; }
	@black a2a_orchestrator tests || { printf "❌ Black 格式化失敗\n"; exit 1; }
	@printf "✅ 程式碼格式化完成。\n"

# 使用官方 ADK 指令啟動遠端 A2A agents
start-agents:
	@printf "🚀 正在使用官方 ADK 伺服器啟動遠端 A2A agents...\n"
	@./start_a2a_servers.sh

# 使用官方 ADK 清理功能停止遠端 agents
stop-agents:
	@printf "🛑 正在以清除並關機的方式停止遠端 A2A agents...\n"
	@./stop_a2a_servers.sh

# 檢查 agent 狀態與可用性
check-agents:
	@printf "🔍 正在檢查 A2A agent 狀態...\n\n"
	@printf "🔬 研究 Agent (8001): "
	@curl -s http://localhost:8001/.well-known/agent-card.json | jq -r '.name' 2>/dev/null || printf "❌ 無回應\n"
	@printf "📊 分析 Agent (8002): "
	@curl -s http://localhost:8002/.well-known/agent-card.json | jq -r '.name' 2>/dev/null || printf "❌ 無回應\n"
	@printf "✍️  內容 Agent (8003):  "
	@curl -s http://localhost:8003/.well-known/agent-card.json | jq -r '.name' 2>/dev/null || printf "❌ 無回應\n"
	@printf "\n💡 如果 agents 沒有回應，請執行 'make start-agents'\n"

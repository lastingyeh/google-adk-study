# =============================================================================
# Conversation Agent 開發環境設定 (使用 uv)
# =============================================================================

.PHONY: help install dev dev-web dev-main debug test clean sync lock add remove init redis-up redis-down

# 預設目標
.DEFAULT_GOAL := help

# 協助資訊
help:
	@echo "==============================================================================="
	@echo "| Conversation Agent 開發指令 (使用 uv)                                     |"
	@echo "==============================================================================="
	@echo "| make init       - 初始化 uv 專案                                         |"
	@echo "| make install    - 安裝專案依賴 (基於 pyproject.toml)                    |"
	@echo "| make sync       - 同步依賴到虛擬環境                                     |"
	@echo "| make lock       - 更新依賴鎖定檔案                                       |"
	@echo "| make add PKG    - 新增依賴套件                                           |"
	@echo "| make remove PKG - 移除依賴套件                                           |"
	@echo "| make dev        - 啟動 CLI 對話模式 (adk run)                           |"
	@echo "| make dev-web    - 啟動 Web 開發伺服器 (adk web)                         |"
	@echo "| make dev-main   - 使用 Redis Session 啟動 Web 模式                      |"
	@echo "| make debug      - 啟動偵錯模式（支援 VS Code 附加偵錯）                  |"
	@echo "| make redis-up   - 啟動 Redis 服務                                        |"
	@echo "| make redis-down - 停止 Redis 服務                                        |"
	@echo "| make test       - 執行測試                                               |"
	@echo "| make clean      - 清理暫存檔案                                           |"
	@echo "==============================================================================="

# 初始化 uv 專案
init:
	@echo "🚀 初始化 uv 專案..."
	uv init --no-readme --no-workspace
	@echo "✅ uv 專案初始化完成"

# 安裝依賴（使用 uv）
install:
	@echo "📦 使用 uv 安裝專案依賴..."
	uv add google-adk
	@echo "✅ 依賴安裝完成"

# 同步依賴到虛擬環境
sync:
	@echo "🔄 同步依賴到虛擬環境..."
	uv sync
	@echo "✅ 依賴同步完成"

# 更新依賴鎖定檔案
lock:
	@echo "🔒 更新依賴鎖定檔案..."
	uv lock
	@echo "✅ 鎖定檔案更新完成"

# 新增依賴套件
add:
	@echo "➕ 新增依賴套件..."
	@if [ -z "$(PKG)" ]; then \
		echo "❌ 請指定套件名稱：make add PKG=package-name"; \
		exit 1; \
	fi
	uv add $(PKG)
	@echo "✅ 套件 $(PKG) 已新增"

# 移除依賴套件
remove:
	@echo "➖ 移除依賴套件..."
	@if [ -z "$(PKG)" ]; then \
		echo "❌ 請指定套件名稱：make remove PKG=package-name"; \
		exit 1; \
	fi
	uv remove $(PKG)
	@echo "✅ 套件 $(PKG) 已移除"

# 啟動 CLI 對話模式
dev:
	@echo "🚀 啟動 ADK CLI 對話模式..."
	@echo "💬 直接在終端機中與 Agent 對話"
	@echo "📝 測試項目：基本對話、狀態記憶、模式切換 (#think)、安全防護"
	@echo "🛑 輸入 'exit' 或按 Ctrl+C 退出"
	@echo ""
	uv run adk run backend/agents

# 啟動 Web 開發伺服器
dev-web:
	@echo "🚀 啟動 ADK Web 開發伺服器..."
	@echo "📱 開啟 http://localhost:8000 並選擇 'agents'"
	@echo "🛑 按下 Ctrl+C 停止伺服器"
	@echo ""
	uv run adk web backend

# 使用 Redis Session 啟動 Web 開發伺服器
dev-main:
	@echo "🚀 啟動 ADK Web 開發伺服器 (使用 Redis Session)..."
	@echo "📱 開啟 http://localhost:8000 並選擇 'agents'"
	@echo "💾 會話資料將儲存在 Redis (24小時 TTL)"
	@echo "🛑 按下 Ctrl+C 停止伺服器"
	@echo ""
	uv run python backend/main.py web backend --session_service_uri=redis://localhost:6379/0

# 啟動偵錯模式
debug:
	@echo "==============================================================================="
	@echo "| 🐛 啟動偵錯模式                                                          |"
	@echo "==============================================================================="
	@echo "| 📍 伺服器位址：http://localhost:8000                                      |"
	@echo "| 🔍 Debugger 監聽：5678                                                   |"
	@echo "| 🔗 VS Code 連接：按 F5 選擇 'Debug ADK Web'                            |"
	@echo "| 🔄 熱重載：啟用                                                          |"
	@echo "| 💡 提示：在 VS Code 中設定中斷點後開始偵錯                              |"
	@echo "==============================================================================="
	uv run python -m debugpy --listen 5678 --wait-for-client -m google.adk.cli web backend --port 8000

# 執行測試
test:
	@echo "🧪 執行測試..."
	@echo "⚠️  注意：請先建立測試檔案"
	uv run pytest tests/ -v --tb=short

# 安裝開發依賴
install-dev:
	@echo "🔧 安裝開發依賴..."
	uv add --dev pytest debugpy
	@echo "✅ 開發依賴安裝完成"

# 啟動 Redis 服務
redis-up:
	@echo "🔴 啟動 Redis 服務..."
	docker-compose up -d redis-adk-not-chat-gpt
	@echo "✅ Redis 已啟動在 localhost:6379"

# 停止 Redis 服務
redis-down:
	@echo "🛑 停止 Redis 服務..."
	docker-compose stop redis-adk-not-chat-gpt
	@echo "✅ Redis 已停止"

# 清理暫存檔案
clean:
	@echo "🧹 清理暫存檔案..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".uv" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ 清理完成"

# 顯示專案資訊
info:
	@echo "📊 專案資訊："
	@echo "Python 版本：$(shell uv python version 2>/dev/null || echo '未安裝')"
	@echo "uv 版本：$(shell uv --version 2>/dev/null || echo '未安裝')"
	@echo "虛擬環境：$(shell uv venv list 2>/dev/null || echo '未建立')"

# 開發模式的別名
run: dev
setup: init install-dev
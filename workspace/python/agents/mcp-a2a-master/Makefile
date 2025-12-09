# MCP A2A Master Project
# Makefile for managing MCP Server and A2A Agents

.PHONY: help setup dev start stop clean test test-unit test-integration test-coverage test-watch demo kill-ports start-mcp start-host start-builder

# Default target - show help
help:
	@echo "🚀 MCP A2A Master 專案管理"
	@echo ""
	@echo "快速開始指令 (Quick Start):"
	@echo "  make setup        - 安裝相依套件 (Install dependencies)"
	@echo "  make start        - 啟動所有服務 (Start all services)"
	@echo "  make stop         - 停止所有服務 (Stop all services)"
	@echo "  make dev          - 開發模式：啟動所有服務 (Development mode)"
	@echo ""
	@echo "個別服務控制 (Individual Services):"
	@echo "  make start-mcp    - 僅啟動 MCP Server (port 3000)"
	@echo "  make start-host   - 僅啟動 Host Agent (port 10000)"
	@echo "  make start-builder - 僅啟動 Website Builder (port 10001)"
	@echo "  make cmd          - 啟動命令列介面 (Start CLI interface)"
	@echo ""
	@echo "進階指令 (Advanced):"
	@echo "  make kill-ports   - 清理占用的端口 (Clean up ports: 3000, 10000, 10001)"
	@echo "  make test         - 執行所有測試 (Run all tests)"
	@echo "  make test-unit    - 執行單元測試 (Run unit tests)"
	@echo "  make test-integration - 執行整合測試 (Run integration tests)"
	@echo "  make test-coverage - 執行測試涵蓋率分析 (Run test coverage)"
	@echo "  make demo         - 執行示範 (Run demo)"
	@echo "  make clean        - 清理產生檔案 (Clean up generated files)"
	@echo ""
	@echo "💡 第一次使用？請依序執行: make setup && make start"

# Install dependencies using uv
setup:
	@echo "📦 安裝相依套件中..."
	@if ! command -v uv &> /dev/null; then \
		echo "❌ 錯誤：找不到 uv 指令"; \
		echo "請先安裝 uv: https://github.com/astral-sh/uv"; \
		exit 1; \
	fi
	uv sync
	uv sync --extra dev
	@echo "✅ 安裝完成！執行 'make start' 啟動所有服務。"

# Kill processes on specific ports
kill-ports:
	@echo "🧹 清理占用的端口..."
	@if lsof -ti:10000 > /dev/null 2>&1; then \
		echo "正在關閉 port 10000 (Host Agent)..."; \
		lsof -ti:10000 | xargs kill -9; \
		echo "✅ Port 10000 已釋放"; \
	else \
		echo "✓ Port 10000 未被占用"; \
	fi
	@if lsof -ti:10001 > /dev/null 2>&1; then \
		echo "正在關閉 port 10001 (Website Builder)..."; \
		lsof -ti:10001 | xargs kill -9; \
		echo "✅ Port 10001 已釋放"; \
	else \
		echo "✓ Port 10001 未被占用"; \
	fi
	@if lsof -ti:3000 > /dev/null 2>&1; then \
		echo "正在關閉 port 3000 (MCP Server)..."; \
		lsof -ti:3000 | xargs kill -9; \
		echo "✅ Port 3000 已釋放"; \
	else \
		echo "✓ Port 3000 未被占用"; \
	fi
	@echo "✅ 所有端口清理完成！"

# Stop all services
stop: kill-ports
	@echo "🛑 所有服務已停止"

# Start MCP Server only
start-mcp: check-env
	@echo "🔧 啟動 MCP Server (port 3000)..."
	@uv run ./mcp/servers/streamable_http_server.py &
	@echo "✅ MCP Server 已啟動"
	@sleep 2

# Start Host Agent only
start-host: check-env
	@echo "🤖 啟動 Host Agent (port 10000)..."
	@uv run python3 -m agents.host_agent &
	@echo "✅ Host Agent 已啟動"
	@sleep 2

# Start Website Builder only
start-builder: check-env
	@echo "🌐 啟動 Website Builder (port 10001)..."
	@uv run python3 -m agents.website_builder_simple &
	@echo "✅ Website Builder 已啟動"
	@sleep 2

# Start CLI interface
cmd: check-env
	@echo "💻 啟動命令列介面..."
	@uv run python3 -m app.cmd.cmd

# Start all services
start: check-env kill-ports
	@echo "========================================="
	@echo "🚀 啟動所有服務 (Starting All Services)"
	@echo "========================================="
	@echo ""
	@echo "[1/3] 啟動 MCP Server..."
	@uv run ./mcp/servers/streamable_http_server.py &
	@echo "MCP Server PID: $$!"
	@sleep 5
	@echo ""
	@echo "[2/3] 啟動 Host Agent Server..."
	@uv run python3 -m agents.host_agent &
	@echo "Host Agent Server PID: $$!"
	@sleep 5
	@echo ""
	@echo "[3/3] 啟動 Website Builder Simple..."
	@uv run python3 -m agents.website_builder_simple &
	@echo "Website Builder Simple PID: $$!"
	@sleep 3
	@echo ""
	@echo "========================================="
	@echo "✅ 所有服務已啟動！"
	@echo "========================================="
	@echo ""
	@echo "📱 服務端口資訊："
	@echo "  • MCP Server:        http://localhost:3000"
	@echo "  • Host Agent:        http://localhost:10000"
	@echo "  • Website Builder:   http://localhost:10001"
	@echo ""
	@echo "🛑 停止服務請執行: make stop"

# Development mode (alias for start)
dev: start

# Run a demo
demo: check-env
	@echo "🧪 執行 MCP A2A 示範..."
	@echo ""
	@echo "💬 可嘗試以下操作："
	@echo "   • 連接到 Host Agent (port 10000)"
	@echo "   • 呼叫 Website Builder 建立網站"
	@echo "   • 透過 MCP Server 存取工具"
	@echo ""
	@echo "✅ 示範已就緒！"
	@echo "   MCP Server:      http://localhost:3000"
	@echo "   Host Agent:      http://localhost:10000"
	@echo "   Website Builder: http://localhost:10001"

# Run tests
test:
	@echo "🧪 執行所有測試..."
	@uv run pytest tests/ -v --tb=short

# Run unit tests only
test-unit:
	@echo "🧪 執行單元測試..."
	@uv run pytest tests/ -v -m unit --tb=short

# Run integration tests only
test-integration:
	@echo "🧪 執行整合測試..."
	@uv run pytest tests/ -v -m integration --tb=short

# Run tests with coverage
test-coverage:
	@echo "📊 執行測試涵蓋率分析..."
	@uv run pytest tests/ \
		--cov=agents \
		--cov=utilities \
		--cov-report=html \
		--cov-report=term \
		--cov-report=term-missing \
		-v
	@echo ""
	@echo "✅ 涵蓋率報告已產生！"
	@echo "📁 HTML 報告：htmlcov/index.html"
	@echo ""
	@echo "💡 開啟報告："
	@echo "   open htmlcov/index.html"

# Watch mode for tests (requires pytest-watch)
test-watch:
	@echo "👀 測試監看模式..."
	@uv run ptw tests/ -- -v --tb=short

# Clean up generated files
clean:
	@echo "🧹 清理中..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ 清理完成！"

# Check environment variables
check-env:
	@if [ -z "$$GOOGLE_API_KEY" ] && [ -z "$$GOOGLE_APPLICATION_CREDENTIALS" ]; then \
		echo "❌ 錯誤：尚未設定驗證資訊 (Authentication not configured)"; \
		echo ""; \
		echo "請選擇以下其中一種驗證方式："; \
		echo ""; \
		echo "🔑 方式 1 - API Key (Gemini API)："; \
		echo "   export GOOGLE_API_KEY=你的_API_Key"; \
		echo "   申請金鑰：https://aistudio.google.com/app/apikey"; \
		echo ""; \
		echo "🔐 方式 2 - Service Account (VertexAI)："; \
		echo "   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json"; \
		echo "   export GOOGLE_CLOUD_PROJECT=your_project_id"; \
		echo "   建立憑證：https://console.cloud.google.com/iam-admin/serviceaccounts"; \
		echo ""; \
		echo "💡 提示：可以複製 .env.example 為 .env 並填入相關設定"; \
		echo ""; \
		exit 1; \
	fi

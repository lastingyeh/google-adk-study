# Makefile for genmedia-agent ADK project
# 根據 README.md 生成的自動化構建和執行腳本

.PHONY: help install-mcp setup sync dev debug server-imagen clean check-env

# 預設目標：顯示幫助訊息
help:
	@echo "可用的 Make 目標："
	@echo "  make install-mcp    - 安裝 MCP Servers for Genmedia 工具"
	@echo "  make setup          - 初始化專案環境 (uv sync)"
	@echo "  make check-env      - 檢查 .env 檔案是否存在"
	@echo "  make dev            - 啟動 ADK Developer UI (adk web)"
	@echo "  make debug          - 啟動 VSCode 除錯模式"
	@echo "  make server-imagen  - 在背景啟動 Imagen MCP Server (SSE)"
	@echo "  make sync           - 同步 Go workspace 依賴"
	@echo "  make clean          - 清理臨時檔案"
	@echo "  make all            - 完整設定並啟動 (install-mcp + setup + dev)"

# MCP 伺服器相關路徑
MCP_GO_DIR := vertex-ai-creative-studio/experiments/mcp-genmedia/mcp-genmedia-go
GO_BIN := $(shell go env GOPATH)/bin

# 安裝 MCP Servers for Genmedia 工具
install-mcp:
	@echo "📦 安裝 MCP Servers for Genmedia..."
	@if ! command -v go > /dev/null 2>&1; then \
		echo "❌ 錯誤: 找不到 Go，請先安裝 Go"; \
		exit 1; \
	fi
	@cd $(MCP_GO_DIR) && go work sync
	@cd $(MCP_GO_DIR) && go install ./mcp-imagen-go ./mcp-veo-go ./mcp-chirp3-go ./mcp-avtool-go ./mcp-gemini-go ./mcp-lyria-go
	@echo "✅ MCP 伺服器已安裝至: $(GO_BIN)"
	@echo "💡 提示: 請確保 $(GO_BIN) 在您的 PATH 中"
	@echo "   執行: export PATH=\"$(GO_BIN):\$$PATH\""

# 同步 Go workspace 依賴
sync:
	@echo "🔄 同步 Go workspace 依賴..."
	@cd $(MCP_GO_DIR) && go work sync
	@echo "✅ 依賴同步完成"

# 檢查 .env 檔案
check-env:
	@if [ ! -f genmedia_agent/.env ]; then \
		echo "⚠️  警告: 找不到 .env 檔案"; \
		echo ""; \
		echo "請在 genmedia_agent/.env 建立環境變數檔案，包含:"; \
		echo "  GOOGLE_CLOUD_PROJECT=\"your-project-id\""; \
		echo "  GOOGLE_CLOUD_LOCATION=\"us-central1\""; \
		echo "  GOOGLE_GENAI_USE_VERTEXAI=\"True\""; \
		echo ""; \
		exit 1; \
	else \
		echo "✅ .env 檔案存在"; \
	fi

# 初始化專案環境
setup: check-env
	@echo "🔧 初始化專案環境..."
	@uv sync
	@echo "✅ 專案環境設定完成"

# 啟動 ADK Developer UI
dev: check-env
	@echo "🚀 啟動 ADK Developer UI..."
	@uv sync
	@. .venv/bin/activate && adk web

# 啟動 VSCode 除錯模式
debug: check-env
	@echo "🐛 啟動 VSCode 除錯模式 (監聽埠: 5678)..."
	@uv run --with debugpy python -m debugpy --listen 5678 --wait-for-client -m google.adk.cli web . --port 8000 --reload_agents

# 在背景啟動 Imagen MCP Server (SSE 協定)
server-imagen:
	@echo "🖼️  啟動 Imagen MCP Server (SSE)..."
	@export PROJECT_ID=$$(gcloud config get project 2>/dev/null || echo "das-idp-lab") && \
	if [ -z "$$PROJECT_ID" ]; then \
		echo "❌ 錯誤: 無法取得 Google Cloud 專案 ID"; \
		exit 1; \
	fi; \
	echo "使用專案 ID: $$PROJECT_ID"; \
	$(GO_BIN)/mcp-imagen-go --transport sse

# 清理臨時檔案
clean:
	@echo "🧹 清理臨時檔案..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ 清理完成"

# 完整設定流程
all: install-mcp setup
	@echo ""
	@echo "✨ 設定完成！"
	@echo ""
	@echo "下一步："
	@echo "  1. 執行 'make server-imagen' 在另一個終端啟動 Imagen 伺服器"
	@echo "  2. 執行 'make dev' 啟動 ADK Developer UI"
	@echo "  或"
	@echo "  執行 'make debug' 啟動除錯模式"

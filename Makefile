.PHONY: help build test clean install sitemap sitemap-all sitemap-adk sitemap-a2a sitemap-mcp

# 默認目標
.DEFAULT_GOAL := help

# 顏色定義
CYAN := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RESET := \033[0m

# 幫助信息
help: ## 顯示此幫助信息
	@echo "$(CYAN)Google ADK Study - Makefile 命令$(RESET)"
	@echo ""
	@echo "$(GREEN)可用命令:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""

# 安裝依賴
install: ## 安裝 npm 依賴
	@echo "$(CYAN)正在安裝依賴...$(RESET)"
	npm install

# 構建項目
build: ## 編譯 TypeScript 代碼
	@echo "$(CYAN)正在構建項目...$(RESET)"
	npm run build

# 運行測試
test: ## 運行測試
	@echo "$(CYAN)正在運行測試...$(RESET)"
	npm run test

# 清理構建產物
clean: ## 清理構建產物和臨時文件
	@echo "$(CYAN)正在清理...$(RESET)"
	rm -rf node_modules
	rm -rf dist
	rm -f *.log

# Sitemap 相關命令

sitemap: ## 運行基本 sitemap 生成
	@echo "$(CYAN)正在生成 sitemap...$(RESET)"
	npm run sitemap

sitemap-all: sitemap-adk sitemap-a2a sitemap-mcp ## 生成所有 sitemap（ADK、A2A、MCP）
	@echo "$(GREEN)所有 sitemap 已生成完成$(RESET)"

# Google ADK Sitemap
sitemap-adk: ## 生成 Google ADK 所有格式的 sitemap
	@echo "$(CYAN)正在生成 Google ADK sitemap...$(RESET)"
	npm run sitemap:adk
	npm run sitemap:adk:csv
	npm run sitemap:adk:md

sitemap-adk-yaml: ## 生成 Google ADK YAML sitemap
	npm run sitemap:adk

sitemap-adk-csv: ## 生成 Google ADK CSV sitemap
	npm run sitemap:adk:csv

sitemap-adk-md: ## 生成 Google ADK Markdown sitemap
	npm run sitemap:adk:md

# A2A Protocol Sitemap
sitemap-a2a: ## 生成 A2A Protocol 所有格式的 sitemap
	@echo "$(CYAN)正在生成 A2A Protocol sitemap...$(RESET)"
	npm run sitemap:a2a
	npm run sitemap:a2a:csv
	npm run sitemap:a2a:md

sitemap-a2a-yaml: ## 生成 A2A Protocol YAML sitemap
	npm run sitemap:a2a

sitemap-a2a-csv: ## 生成 A2A Protocol CSV sitemap
	npm run sitemap:a2a:csv

sitemap-a2a-md: ## 生成 A2A Protocol Markdown sitemap
	npm run sitemap:a2a:md

# Model Context Protocol Sitemap
sitemap-mcp: ## 生成 MCP 所有格式的 sitemap
	@echo "$(CYAN)正在生成 Model Context Protocol sitemap...$(RESET)"
	npm run sitemap:mcp
	npm run sitemap:mcp:csv
	npm run sitemap:mcp:md

sitemap-mcp-yaml: ## 生成 MCP YAML sitemap
	npm run sitemap:mcp

sitemap-mcp-csv: ## 生成 MCP CSV sitemap
	npm run sitemap:mcp:csv

sitemap-mcp-md: ## 生成 MCP Markdown sitemap
	npm run sitemap:mcp:md

# 開發工作流
dev: install build ## 初始化開發環境（安裝依賴並構建）
	@echo "$(GREEN)開發環境已就緒$(RESET)"

# 完整工作流
all: clean install build test sitemap-all ## 執行完整工作流（清理、安裝、構建、測試、生成 sitemap）
	@echo "$(GREEN)所有任務已完成$(RESET)"

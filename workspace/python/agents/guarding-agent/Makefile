# Makefile for Guarding Agent System

.PHONY: help install test lint format clean run

help:  ## 顯示此幫助訊息
	@echo "AI 代理防護系統 - 可用命令："
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## 安裝依賴（開發模式）
	pip install -e ".[dev]"

install-prod:  ## 安裝生產依賴
	pip install -e .

test:  ## 執行所有測試
	pytest -v

test-cov:  ## 執行測試並生成覆蓋率報告
	pytest --cov=guarding_agent --cov-report=html --cov-report=term
	@echo "覆蓋率報告已生成至: htmlcov/index.html"

test-watch:  ## 監視檔案變更並自動執行測試
	pytest-watch

lint:  ## 執行程式碼檢查
	ruff check guarding_agent tests

format:  ## 格式化程式碼
	black guarding_agent tests
	ruff check --fix guarding_agent tests

clean:  ## 清理暫存檔案
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete

run:  ## 執行範例測試
	python -m guarding_agent.agent

run-demo:  ## 執行互動式演示
	python -c "from guarding_agent.agent import run_demo; import asyncio; asyncio.run(run_demo())"

stats:  ## 顯示防護統計
	python -c "from guarding_agent.agent import get_default_runner, get_stats; runner = get_default_runner(); print(get_stats(runner))"

config-check:  ## 檢查配置檔案
	python -c "import yaml; yaml.safe_load(open('config/security_config.yaml'))"
	@echo "✅ 配置檔案格式正確"

build:  ## 建立套件
	python -m build

docker-build:  ## 建立 Docker 映像（未來）
	@echo "Docker 支援將在階段二實作"

deploy:  ## 部署到生產環境（未來）
	@echo "部署流程將在階段二實作"

# 開發工作流程快捷鍵
dev: clean install lint test  ## 開發流程：清理、安裝、檢查、測試

ci: lint test-cov  ## CI 流程：檢查和測試（含覆蓋率）

all: clean install lint test-cov  ## 執行所有檢查

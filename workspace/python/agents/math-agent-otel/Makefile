.PHONY: help setup test demo web jaeger-up jaeger-down clean

# Color output
BOLD := \033[1m
GREEN := \033[32m
BLUE := \033[34m
YELLOW := \033[33m
RESET := \033[0m

help:
	@echo ""
	@echo "$(BOLD)🚀 OpenTelemetry + ADK + Jaeger$(RESET)"
	@echo ""
	@echo "$(BOLD)快速開始 (3 步驟):$(RESET)"
	@echo "  1. $(GREEN)make setup$(RESET)      — 安裝相依套件"
	@echo "  2. $(GREEN)make jaeger-up$(RESET)  — 啟動 Jaeger (觀察追蹤)"
	@echo "  3. $(GREEN)make web$(RESET)        — 在 $(BLUE)http://localhost:8000$(RESET) 啟動互動式聊天"
	@echo ""
	@echo "$(BOLD)然後:$(RESET)"
	@echo "  • 在 Web UI 中詢問代理數學問題"
	@echo "  • 在 $(BLUE)http://localhost:16686$(RESET) 的 Jaeger 中檢視追蹤"
	@echo "  • 使用 $(GREEN)make jaeger-down$(RESET) 停止 Jaeger"
	@echo ""
	@echo "$(BOLD)其他指令:$(RESET)"
	@echo "  $(GREEN)make demo$(RESET)          — 執行帶有範例查詢的示範"
	@echo "  $(GREEN)make test$(RESET)          — 執行 42 個單元測試"
	@echo "  $(GREEN)make clean$(RESET)         — 移除快取檔案"
	@echo ""

setup:
	@echo "$(BOLD)📦 安裝相依套件中...$(RESET)"
	pip install -r requirements.txt
	pip install -e .
	@echo "$(GREEN)✅ 完成$(RESET)"
	@echo ""

test:
	@echo "$(BOLD)🧪 執行測試中...$(RESET)"
	pytest tests/ -v --cov=math_agent --cov-report=term-missing
	@echo ""

demo:
	@echo "$(BOLD)🤖 執行示範中...$(RESET)"
	@echo ""
	python -m math_agent.agent
	@echo ""

web:
	@echo "$(BOLD)🌐 正在 http://localhost:8000 啟動 Web UI$(RESET)"
	@echo "$(BOLD)📊 透過 OTEL 將追蹤匯出至 http://localhost:16686 的 Jaeger$(RESET)"
	@echo ""
	OTEL_SERVICE_NAME=google-adk-math-agent \
	OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318 \
	OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf \
	OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true \
	adk web .

jaeger-up:
	@echo "$(BOLD)🚀 啟動 Jaeger 中...$(RESET)"
	docker run -d --name jaeger \
		-e COLLECTOR_OTLP_ENABLED=true \
		-p 16686:16686 -p 4318:4318 \
		jaegertracing/all-in-one:latest > /dev/null 2>&1
	@echo "$(GREEN)✅ Jaeger 正在 http://localhost:16686 執行$(RESET)"
	@echo ""

jaeger-down:
	@echo "$(BOLD)🛑 停止 Jaeger 中...$(RESET)"
	@docker stop jaeger > /dev/null 2>&1 && docker rm jaeger > /dev/null 2>&1 || true
	@echo "$(GREEN)✅ Jaeger 已停止$(RESET)"
	@echo ""

clean:
	@echo "$(BOLD)🧹 清理中...$(RESET)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	@echo "$(GREEN)✅ 完成$(RESET)"
	@echo ""

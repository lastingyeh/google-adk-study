# 教學 14：使用 Server-Sent Events (SSE) 的串流代理
# 用於開發、測試和展示指令的 Makefile

.PHONY: setup dev test demo clean help
.PHONY: basic_demo modes_demo chat_demo advanced_demo aggregator_demo
.PHONY: fastapi_demo client_demo all_demos

# 預設目標 - 顯示幫助
help:
	@echo "🚀 教學 14：使用 Server-Sent Events (SSE) 的串流代理"
	@echo ""
	@echo "📋 快速入門："
	@echo "  make setup    # 安裝依賴"
	@echo "  make demo     # 執行主要展示"
	@echo ""
	@echo "🎯 開發指令："
	@echo "  make setup    # 安裝依賴與套件"
	@echo "  make dev      # 啟動 ADK 網頁介面 (需要 GOOGLE_API_KEY)"
	@echo "  make test     # 執行綜合測試套件"
	@echo ""
	@echo "🎪 展示指令："
	@echo "  make demo           # 執行主要串流展示"
	@echo "  make basic_demo     # 基本串流實作"
	@echo "  make modes_demo     # StreamingMode 設定"
	@echo "  make chat_demo      # 互動式聊天應用程式"
	@echo "  make advanced_demo  # 進階串流模式"
	@echo "  make aggregator_demo # 回應聚合展示"
	@echo "  make fastapi_demo   # FastAPI SSE 伺服器資訊"
	@echo "  make client_demo    # SSE 客戶端展示資訊"
	@echo "  make all_demos      # 依序執行所有展示"
	@echo ""
	@echo "🧹 維護："
	@echo "  make clean    # 移除快取檔案與產物"
	@echo ""
	@echo "📖 教學：https://github.com/raphaelmansuy/adk_training/tree/main/tutorial_implementation/tutorial14"

# 設定環境
setup:
	@echo "📦 正在設定教學 14 環境..."
	pip install -r requirements.txt
	pip install -e .
	@echo "✅ 設定完成！"
	@echo "💡 後續步驟："
	@echo "   1. 將 streaming_agent/.env.example 複製為 .env"
	@echo "   2. 在 .env 中加入您的 GOOGLE_API_KEY"
	@echo "   3. 執行 'make demo' 來觀看串流的實際運作！"

# 啟動 ADK 網頁介面
dev:
	@echo "🌐 正在啟動 ADK 網頁介面..."
	@echo "🔑 請確保您已在環境中設定 GOOGLE_API_KEY"
	@echo "📱 在您的瀏覽器中訪問 http://localhost:8000"
	adk web streaming_agent

# 執行測試
test:
	@echo "🧪 正在執行綜合測試套件..."
	pytest tests/ -v --cov=streaming_agent --cov-report=term-missing
	@echo "✅ 所有測試完成！"

# 主要展示 (基本串流)
demo:
	@echo "🎬 正在執行主要串流展示..."
	python demos/basic_streaming_demo.py
	@echo "✅ 展示完成！"

# 個別展示指令
basic_demo:
	@echo "🎯 正在執行基本串流展示..."
	@echo "   展示使用 Runner.run_async() 的基本串流"
	python demos/basic_streaming_demo.py
	@echo "✅ 基本展示完成！"

modes_demo:
	@echo "🔄 正在執行串流模式展示..."
	@echo "   顯示不同的 StreamingMode 設定 (SSE, NONE)"
	python demos/streaming_modes_demo.py
	@echo "✅ 模式展示完成！"

chat_demo:
	@echo "💬 正在執行串流聊天應用程式..."
	@echo "   具有即時串流回應的互動式聊天"
	@echo "   按 Ctrl+C 退出"
	python demos/streaming_chat_app.py
	@echo "✅ 聊天展示完成！"

advanced_demo:
	@echo "⚡ 正在執行進階串流模式展示..."
	@echo "   展示：聚合、進度指示器、多重輸出、超時"
	python demos/advanced_patterns_demo.py
	@echo "✅ 進階展示完成！"

aggregator_demo:
	@echo "📊 正在執行串流聚合器展示..."
	@echo "   顯示回應聚合與區塊分析"
	python demos/streaming_aggregator_demo.py
	@echo "✅ 聚合器展示完成！"

fastapi_demo:
	@echo "🚀 FastAPI SSE 展示設定說明"
	@echo "======================================"
	@echo "此展示說明如何使用串流 SSE 建立 Web API。"
	@echo ""
	@echo "📦 安裝額外依賴："
	@echo "   pip install fastapi uvicorn"
	@echo ""
	@echo "🚀 啟動 FastAPI 伺服器："
	@echo "   python -m uvicorn demos.fastapi_sse_demo:app --reload --host 0.0.0.0 --port 8000"
	@echo ""
	@echo "🌐 在瀏覽器中開啟："
	@echo "   http://localhost:8000/docs     - 互動式 API 文件"
	@echo "   http://localhost:8000/client   - 內建測試客戶端"
	@echo ""
	@echo "🧪 測試串流端點："
	@echo "   curl \"http://localhost:8000/chat/stream?query=Hello%20world\""
	@echo ""
	@echo "💡 伺服器包含："
	@echo "   • RESTful 聊天端點"
	@echo "   • Server-Sent Events 串流"
	@echo "   • 內建 HTML 測試客戶端"
	@echo "   • 用於 Web 應用程式的 CORS 標頭"

client_demo:
	@echo "🌐 SSE 客戶端展示設定說明"
	@echo "===================================="
	@echo "此展示顯示用於 SSE 連線的客戶端 JavaScript。"
	@echo ""
	@echo "📋 需求："
	@echo "   • FastAPI 伺服器正在執行 (請參閱 'make fastapi_demo')"
	@echo "   • 現代網頁瀏覽器"
	@echo ""
	@echo "🚀 啟動本地網頁伺服器："
	@echo "   python -m http.server 8080"
	@echo ""
	@echo "🌐 在瀏覽器中開啟："
	@echo "   http://localhost:8080/demos/sse_client.html"
	@echo ""
	@echo "💡 功能："
	@echo "   • 即時 SSE 連線"
	@echo "   • 漸進式訊息顯示"
	@echo "   • 錯誤處理與重新連線"
	@echo "   • 簡潔、響應式的 UI"
	@echo "   • 輸入指示器"

# 依序執行所有展示
all_demos:
	@echo "🎪 正在執行所有串流展示..."
	@echo "=================================="
	$(MAKE) basic_demo
	@echo ""
	$(MAKE) modes_demo
	@echo ""
	$(MAKE) advanced_demo
	@echo ""
	$(MAKE) aggregator_demo
	@echo ""
	$(MAKE) fastapi_demo
	@echo ""
	$(MAKE) client_demo
	@echo ""
	@echo "🎉 所有展示完成！"
	@echo "💡 專業提示：使用 'make <demo_name>' 執行個別展示"

# 清理
clean:
	@echo "🧹 正在清理快取檔案與產物..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete
	find . -type f -name "streaming_output.txt" -delete
	@echo "✅ 清理完成！"

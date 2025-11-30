### 翻譯內容
```makefile
# 教學 29：UI 整合快速入門
# 用於管理後端與前端的 Makefile

.PHONY: help setup setup-backend setup-frontend dev dev-backend dev-frontend test clean demo

# 預設目標 - 顯示幫助訊息
help:
	@echo "🚀 教學 29：UI 整合快速入門"
	@echo ""
	@echo "快速入門指令："
	@echo "  make setup          - 安裝所有依賴項 (後端 + 前端)"
	@echo "  make dev            - 啟動後端與前端伺服器"
	@echo "  make dev-backend    - 僅啟動後端伺服器"
	@echo "  make dev-frontend   - 僅啟動前端伺服器"
	@echo "  make demo           - 顯示範例提示與用法"
	@echo ""
	@echo "進階指令："
	@echo "  make test           - 執行所有測試"
	@echo "  make clean          - 清理生成的檔案"
	@echo ""
	@echo "💡 第一次使用？請執行：make setup && make dev"
	@echo ""
	@echo "架構："
	@echo "  後端： Python FastAPI + ADK agent (埠號 8000)"
	@echo "  前端： React + Vite + CopilotKit (埠號 5173)"

# 安裝所有依賴項
setup: setup-backend setup-frontend
	@echo "✅ 設定完成！"
	@echo ""
	@echo "後續步驟："
	@echo "  1. 設定 API 金鑰： cp agent/.env.example agent/.env"
	@echo "  2. 編輯 agent/.env 並加入您的 GOOGLE_API_KEY"
	@echo "  3. 執行：make dev"

# 安裝後端依賴項
setup-backend:
	@echo "📦 正在安裝後端依賴項..."
	pip install -r requirements.txt
	pip install -e .
	@echo "✅ 後端設定完成！"

# 安裝前端依賴項
setup-frontend:
	@echo "📦 正在安裝前端依賴項..."
	@if [ ! -d "frontend/node_modules" ]; then \
		cd frontend && npm install; \
	else \
		echo "前端依賴項已安裝。若要重新安裝，請執行 'make clean'。"; \
	fi
	@echo "✅ 前端設定完成！"

# 同時啟動後端與前端
dev:
	@echo "🚀 正在啟動後端與前端伺服器..."
	@echo ""
	@echo "這將會開啟兩個終端機："
	@echo "  終端機 1：後端 (http://localhost:8000)"
	@echo "  終端機 2：前端 (http://localhost:5173)"
	@echo ""
	@echo "按下 Ctrl+C 來停止兩個伺服器"
	@echo ""
	@$(MAKE) dev-parallel

# 平行啟動後端與前端 (內部使用)
dev-parallel: check-env
	@trap 'kill 0' EXIT; \
	(cd agent && python agent.py) & \
	(cd frontend && npm run dev) & \
	wait

# 僅啟動後端伺服器
dev-backend: check-env
	@echo "🤖 正在啟動後端伺服器..."
	@echo "📱 伺服器： http://localhost:8000"
	@echo "📚 API 文件： http://localhost:8000/docs"
	@echo "💬 CopilotKit 端點： http://localhost:8000/api/copilotkit"
	@echo ""
	cd agent && python agent.py

# 僅啟動前端伺服器
dev-frontend:
	@echo "🌐 正在啟動前端伺服器..."
	@echo "📱 在您的瀏覽器中開啟 http://localhost:5173"
	@echo ""
	@echo "⚠️  請確保後端正在埠號 8000 上運行"
	@echo "    在另一個終端機中執行：make dev-backend"
	@echo ""
	cd frontend && npm run dev

# 執行測試
test: check-env
	@echo "🧪 正在執行測試..."
	pytest tests/ -v --tb=short

# 執行範例
demo: check-env
	@echo "💬 範例：教學 29 - UI 整合快速入門"
	@echo ""
	@echo "=================================="
	@echo "在聊天 UI 中嘗試這些提示："
	@echo "=================================="
	@echo ""
	@echo "🤖 一般問題："
	@echo "  • '什麼是 Google ADK？'"
	@echo "  • 'AG-UI 協定如何運作？'"
	@echo "  • '解釋 UI 整合的優點'"
	@echo "  • '你能幫我做什麼？'"
	@echo ""
	@echo "📚 學習："
	@echo "  • '告訴我不同的 UI 整合方法'"
	@echo "  • '我應該何時使用 CopilotKit 而不是原生 API？'"
	@echo "  • '如何部署 ADK 代理？'"
	@echo ""
	@echo "=================================="
	@echo ""
	@echo "使用說明："
	@echo "  1. 啟動伺服器：make dev"
	@echo "  2. 開啟 http://localhost:5173"
	@echo "  3. 輸入以上任何提示"
	@echo "  4. 代理將使用 Gemini 回應！"
	@echo ""
	@echo "架構："
	@echo "  使用者 → React/Vite (埠號 5173) → FastAPI (埠號 8000) → ADK 代理 → Gemini"

# 清理
clean:
	@echo "🧹 正在清理..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache/
	cd frontend && rm -rf dist/ node_modules/.cache/ || true
	@echo "✅ 清理完成！"

# 檢查環境 (內部使用)
check-env:
	@if [ -z "$$GOOGLE_API_KEY" ] && [ -z "$$GOOGLE_APPLICATION_CREDENTIALS" ]; then \
		echo "❌ 錯誤：未設定驗證"; \
		echo ""; \
		echo "請選擇以下其中一種驗證方法："; \
		echo ""; \
		echo "🔑 方法 1 - API 金鑰 (Gemini API)："; \
		echo "   export GOOGLE_API_KEY=your_api_key_here"; \
		echo "   在此取得免費金鑰： https://aistudio.google.com/app/apikey"; \
		echo ""; \
		echo "🔐 方法 2 - 服務帳號 (VertexAI)："; \
		echo "   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json"; \
		echo "   export GOOGLE_CLOUD_PROJECT=your_project_id"; \
		echo "   在此建立憑證： https://console.cloud.google.com/iam-admin/serviceaccounts"; \
		echo ""; \
		exit 1; \
	fi
```

### 重點摘要
- **核心概念**：此 `Makefile` 提供了一組指令，用於自動化管理一個包含 Python 後端和 React 前端的專案。它簡化了依賴項安裝、啟動開發伺服器、執行測試和清理專案等流程。
- **關鍵技術**：
    - `make`: 用於定義與執行任務的建置自動化工具。
    - `pip`: Python 的套件安裝器，用於管理後端依賴項。
    - `npm`: Node.js 的套件管理器，用於管理前端依賴項。
    - `trap`: Shell 指令，用於在腳本結束時捕捉信號並執行清理動作 (例如，終止所有背景進程)。
- **重要指令**：
    - `make setup`: 一次性安裝前後端所有依賴項。
    - `make dev`: 同時啟動後端 (FastAPI) 和前端 (Vite) 的開發伺服器。
    - `make test`: 執行 `pytest` 測試套件。
    - `make clean`: 刪除所有 Python 快取檔案 (`.pyc`, `__pycache__`) 和前端建置檔案。
    - `make demo`: 顯示可在應用程式中使用的範例提示。
- **環境設定**：`check-env` 目標會在使用伺服器或執行測試前，驗證 `GOOGLE_API_KEY` 或 `GOOGLE_APPLICATION_CREDENTIALS` 是否已設定，以確保 Google API 的驗證成功。

### Mermaid 流程圖
```mermaid
graph TD
    subgraph 開發流程
        A[開發者] -- "執行 'make setup'" --> B{安裝依賴項};
        B -- "成功" --> C{執行 'make dev'};
        C -- "啟動後端" --> D[Python FastAPI 伺服器 (Port 8000)];
        C -- "啟動前端" --> E[React Vite 伺服器 (Port 5173)];
        A -- "瀏覽 http://localhost:5173" --> E;
    end

    subgraph 其他指令
        A -- "執行 'make test'" --> F[運行 Pytest 測試];
        A -- "執行 'make clean'" --> G[清理專案檔案];
        A -- "執行 'make demo'" --> H[顯示範例提示];
    end

    subgraph 環境檢查
        I{執行 dev/test 指令} --> J[check-env];
        J -- "驗證 GOOGLE_API_KEY" --> K{驗證成功?};
        K -- "是" --> L[繼續執行];
        K -- "否" --> M[顯示錯誤並終止];
    end

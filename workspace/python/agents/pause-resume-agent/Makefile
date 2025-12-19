.PHONY: help setup clean test demo dev

# 顯示說明訊息
help:
	@echo "暫停/恢復調用 (Pause/Resume Invocations) TIL - 可用指令"
	@echo "=================================================="
	@echo ""
	@echo "make setup       安裝依賴並準備環境"
	@echo "make test        執行單元測試（驗證設定）"
	@echo "make dev         啟動 ADK 網頁介面以測試暫停/恢復功能"
	@echo "make demo        不使用網頁介面的快速驗證"
	@echo "make clean       移除快取檔案與產出物"
	@echo ""

# 環境設定
setup:
	pip install -r requirements.txt
	pip install -e .
	cp pause_resume_agent/.env.example pause_resume_agent/.env
	@echo ""
	@echo "✅ 設定完成！"
	@echo ""
	@echo "後續步驟："
	@echo "1. 將您的 GOOGLE_API_KEY 新增至 pause_resume_agent/.env"
	@echo "2. 執行 'make test' 以驗證實作"
	@echo "3. 執行 'make dev' 啟動網頁介面並測試暫停/恢復功能"
	@echo ""

# 開發模式：啟動 ADK UI
dev:
	@echo ""
	@echo "🚀 正在啟動 ADK 網頁介面..."
	@echo ""
	@echo "📝 如何測試暫停/恢復調用 (Pause/Resume Invocations)："
	@echo "   1. 開啟 http://localhost:8000"
	@echo "   2. 選擇 'pause_resume_agent'"
	@echo "   3. 開始長對話或資料處理任務"
	@echo "   4. 查看 Events 分頁以觀察檢查點 (checkpoint) 事件"
	@echo ""
	@echo "💡 觀察重點："
	@echo "   • 'end_of_agent' 事件標記檢查點"
	@echo "   • 檢查點事件中的 'agent_state' 欄位"
	@echo "   • 跨調用後的狀態保留情形"
	@echo "   • 使用檢查點資料執行的工具 (Tool)"
	@echo ""
	@echo "🎯 嘗試這些測試模式："
	@echo "   1. 處理資料：'Please process this data: <text>'"
	@echo "   2. 詢問提示：'What checkpoint should I use?'"
	@echo "   3. 驗證：'Can you validate this checkpoint?'"
	@echo ""
	@echo "⏸️  測試暫停與恢復流程："
	@echo "   步驟 1: 發送初始訊息"
	@echo "     → Agent 處理並建立檢查點"
	@echo "     → 從 Events 分頁複製 invocation_id"
	@echo ""
	@echo "   步驟 2: [暫停] 記錄 invocation_id 與 agent_state"
	@echo "     → 檢查 Events 分頁中的 'end_of_agent: true'"
	@echo "     → 觀察序列化後的 agent_state 欄位"
	@echo ""
	@echo "   步驟 3: [稍後] 使用相同的 invocation_id 恢復"
	@echo "     → 發送新訊息或使用該 Session"
	@echo "     → 狀態將自動恢復"
	@echo ""
	@echo "   步驟 4: 驗證狀態恢復"
	@echo "     → Agent 從最後一個檢查點繼續執行"
	@echo "     → 比較新事件與先前狀態"
	@echo ""
	@echo "📊 需檢查的事件："
	@echo "   • 尋找 'end_of_agent' = true 的事件"
	@echo "   • 檢查 'agent_state' 是否包含您的檢查點資料"
	@echo "   • 驗證 'actions' 欄位包含狀態資訊"
	@echo "   • 追蹤用於恢復的 'invocation_id'"
	@echo ""
	adk web

# 執行測試
test:
	@echo ""
	@echo "🧪 正在執行暫停/恢復調用測試..."
	@echo ""
	@pytest tests/ -v --tb=short
	@echo ""
	@echo "✅ 測試驗證項目："
	@echo "   • Agent 設定 (6 個測試)"
	@echo "   • 工具功能 (8 個測試)"
	@echo "   • 匯入路徑 (3 個測試)"
	@echo "   • App 與可恢復性設定 (2 個測試)"
	@echo ""
	@echo "📋 測試涵蓋範圍："
	@echo "   ✓ Agent 名稱、模型、描述、指令"
	@echo "   ✓ Agent 已設定工具 (3 個工具)"
	@echo "   ✓ process_data_chunk() 處理有效/空資料"
	@echo "   ✓ validate_checkpoint() 處理有效/空資料"
	@echo "   ✓ get_resumption_hint() 處理不同上下文"
	@echo "   ✓ Agent 正確導出以供探索"
	@echo "   ✓ App 名稱與 root_agent 正確"
	@echo "   ✓ 可恢復性配置已啟用 (is_resumable: true)"
	@echo ""
	@echo "🔍 每個測試驗證的內容："
	@echo "   Agent 設定測試："
	@echo "     - Agent 載入正確名稱：pause_resume_agent"
	@echo "     - 模型設定為：gemini-2.0-flash"
	@echo "     - 描述與指令存在"
	@echo "     - 3 個工具皆可用"
	@echo ""
	@echo "   工具功能測試："
	@echo "     - process_data_chunk 處理成功/錯誤案例"
	@echo "     - validate_checkpoint 驗證狀態完整性"
	@echo "     - get_resumption_hint 提供上下文感知提示"
	@echo ""
	@echo "   匯入與配置測試："
	@echo "     - 可從套件匯入 Agent"
	@echo "     - App 配置正確"
	@echo "     - ResumabilityConfig 已正確啟用"
	@echo ""
	@echo "💡 執行特定測試："
	@echo "   pytest tests/test_agent.py::TestAgentConfiguration -v"
	@echo "   pytest tests/test_agent.py::TestAgentTools -v"
	@echo ""
	@echo "📊 查看測試涵蓋率："
	@echo "   pytest tests/ --cov=pause_resume_agent --cov-report=html"
	@echo ""

# 快速示範
demo:
	@echo ""
	@echo "🔍 快速驗證..."
	python -c "from pause_resume_agent import root_agent; from app import app; print('✅ Agent 載入:', root_agent.name); print('✅ App 配置:', app.name); print('✅ 可恢復性已啟用:', app.resumability_config.is_resumable if app.resumability_config else False)"
	@echo ""
	@echo "🎯 實作已就緒！"
	@echo ""

# 清理環境
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov build dist *.egg-info
	@echo "✅ 已清理快取檔案"

### 重點摘要
- **核心概念**：提供自動化開發與測試流程的指令集。
- **關鍵技術**：使用 `make` 管理環境設定 (`setup`)、測試 (`test`)、開發伺服器 (`dev`) 及清理 (`clean`)。
- **重要結論**：開發者應優先執行 `make setup` 初始化，並透過 `make dev` 在 ADK UI 中觀察檢查點行為。
- **行動項目**：
  1. 執行 `make setup`。
  2. 於 `.env` 設定 API 金鑰。
  3. 執行 `make test` 確保一切正常。

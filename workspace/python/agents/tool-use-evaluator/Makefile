.PHONY: help setup clean test demo dev evaluate

help:
	@echo "Tool Use Quality (工具使用品質) Evaluation TIL - 可用指令"
	@echo "====================================================="
	@echo ""
	@echo "make setup       安裝依賴並準備環境"
	@echo "make test        執行單元測試 (驗證配置)"
	@echo "make evaluate    展示使用 RUBRIC_BASED_TOOL_USE_QUALITY_V1 的 LlmAsJudge"
	@echo "make dev         啟動 ADK 網頁介面以測試工具使用"
	@echo "make demo        快速驗證 (無需網頁介面)"
	@echo "make clean       移除快取檔案和產物"
	@echo ""

setup:
	pip install -r requirements.txt
	pip install -e .
	cp tool_use_evaluator/.env.example tool_use_evaluator/.env
	@echo ""
	@echo "✅ 設定完成！"
	@echo ""
	@echo "下一步："
	@echo "1. 將您的 GOOGLE_API_KEY 新增至 tool_use_evaluator/.env"
	@echo "2. 執行 'make test' 以驗證實作"
	@echo "3. 執行 'make dev' 以啟動網頁介面"
	@echo ""

dev:
	@echo ""
	@echo "🚀 正在啟動 ADK 網頁介面..."
	@echo ""
	@echo "📝 如何測試工具使用品質 (Tool Use Quality)："
	@echo "   1. 開啟 http://localhost:8000"
	@echo "   2. 選擇 'tool_use_evaluator'"
	@echo "   3. 嘗試以下提示詞 (Prompts)："
	@echo ""
	@echo "   ✅ 良好的工具使用 (GOOD TOOL USAGE)："
	@echo "   '分析 customer_data，提取特徵，驗證品質，然後應用 random_forest 模型'"
	@echo ""
	@echo "   ❌ 不良的工具使用 (順序錯誤) (BAD TOOL USAGE)："
	@echo "   '先應用模型，然後分析數據，再提取特徵'"
	@echo ""
	@echo "   ✅ 良好的工具順序 (GOOD TOOL SEQUENCE)："
	@echo "   '分析 sales_data，提取重要特徵，驗證它們，應用 gradient_boosting'"
	@echo ""
	@echo "💡 觀察重點："
	@echo "   • Events 標籤頁中的工具呼叫順序"
	@echo "   • 工具是否按邏輯順序呼叫"
	@echo "   • 相依工具之前是否已滿足先決條件"
	@echo "   • 工具被誤用時的錯誤處理"
	@echo ""
	@echo "🎯 評估重點："
	@echo "   此代理 (Agent) 展示了工具使用品質的概念："
	@echo "   - 工具排序 (分析 → 提取 → 驗證 → 應用)"
	@echo "   - 工具依賴性 (每個步驟都建立在前一個步驟之上)"
	@echo "   - 錯誤處理 (適當的驗證)"
	@echo "   - 效率 (無跳過或多餘的步驟)"
	@echo ""
	adk web

test:
	@echo ""
	@echo "🧪 正在執行工具使用品質評估測試..."
	@echo ""
	@pytest tests/ -v --tb=short
	@echo ""
	@echo "✅ 測試驗證項目："
	@echo "   • 代理配置 (6 個測試)"
	@echo "   • 工具功能 (8 個測試)"
	@echo "   • 匯入路徑 (3 個測試)"
	@echo "   • 應用程式結構 (3 個測試)"
	@echo ""
	@echo "📋 測試覆蓋率："
	@echo "   ✓ 代理名稱、模型、描述、指令"
	@echo "   ✓ 代理擁有全部 4 個工具：分析 (analyze)、提取 (extract)、驗證 (validate)、應用 (apply)"
	@echo "   ✓ 代理已配置 output_key"
	@echo "   ✓ 工具成功和錯誤案例"
	@echo "   ✓ 模組匯入和匯出"
	@echo "   ✓ 應用程式配置和初始化"
	@echo ""
	@echo "🔍 每個測試驗證的內容："
	@echo "   代理配置測試："
	@echo "     - 代理名稱：tool_use_evaluator"
	@echo "     - 模型：gemini-2.0-flash"
	@echo "     - 指令強調正確的工具排序"
	@echo "     - 所有 4 個工具皆可用"
	@echo ""
	@echo "   工具功能測試："
	@echo "     - analyze_data 處理成功和錯誤情況"
	@echo "     - extract_features 驗證輸入"
	@echo "     - validate_quality 檢查先決條件"
	@echo "     - apply_model 需要特徵和模型兩者"
	@echo ""
	@echo "   匯入與結構測試："
	@echo "     - 代理可以從套件匯入"
	@echo "     - 應用程式配置正確"
	@echo "     - 模組匯出已正確設定"
	@echo ""
	@echo "💡 若要執行特定測試："
	@echo "   pytest tests/test_agent.py::TestAgentConfiguration -v"
	@echo "   pytest tests/test_agent.py::TestToolFunctionality -v"
	@echo ""
	@echo "📊 查看測試覆蓋率："
	@echo "   pytest tests/ --cov=tool_use_evaluator --cov-report=html"
	@echo ""

demo:
	@echo ""
	@echo "🔍 快速驗證..."
	python -c "from tool_use_evaluator import root_agent; from app import app; print('✅ 代理 (Agent) 已載入:', root_agent.name); print('✅ 應用程式 (App) 已配置:', app.name); print('✅ 工具數量:', len(root_agent.tools)); print('✅ 實作已就緒！')"
	@echo ""
	@echo "🎯 實作已準備好進行評估！"
	@echo ""

evaluate:
	@echo ""
	@echo "📊 展示使用 RUBRIC_BASED_TOOL_USE_QUALITY_V1 的 LlmAsJudge"
	@echo ""
	python evaluate_tool_use.py
	@echo ""

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov build dist *.egg-info
	@echo "✅ 已清除快取檔案"

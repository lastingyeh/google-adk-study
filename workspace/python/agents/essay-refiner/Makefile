# 教學 07：循環代理 (Loop Agents) - 論文精煉系統 (Essay Refinement System)
# 用於開發、測試和部署的 Makefile

# 定義所有偽目標，確保這些命令不會與同名文件衝突
.PHONY: help setup install test test-verbose test-coverage dev run demo validate check clean reset

# 預設目標：顯示使用說明
help:
	@echo "教學 07：循環代理 - 論文精煉系統"
	@echo ""
	@echo "開發命令："
	@echo "  make setup         安裝 Python 依賴套件"
	@echo "  make test          執行完整測試套件 (62 個測試)"
	@echo "  make dev           啟動 ADK 開發伺服器"
	@echo "  make demo          快速系統驗證"
	@echo "  make validate      全面驗證"
	@echo ""
	@echo "測試命令："
	@echo "  make test-verbose  執行測試並顯示詳細輸出"
	@echo "  make test-coverage 執行測試並生成覆蓋率報告"
	@echo "  make check         程式碼檢查與格式化檢查"
	@echo ""
	@echo "清理命令："
	@echo "  make clean         移除快取檔案和產物"
	@echo "  make reset         重置到乾淨狀態"

# ============================================================
# 安裝與環境設定
# ============================================================
# 此區段負責安裝專案所需的所有依賴套件

# setup: 主要安裝目標，委派給 install
setup: install

# install: 安裝所有必要的 Python 套件
# - google-adk: Google Agent Development Kit
# - pytest/pytest-cov: 測試框架與覆蓋率工具
# - black/flake8: 程式碼格式化與檢查工具
install:
	@echo "📦 正在安裝依賴套件..."
	pip install google-adk pytest pytest-cov black flake8
	pip install -e .

# ============================================================
# 測試命令
# ============================================================
# 提供多種測試執行方式，包含基本測試、詳細輸出、覆蓋率報告

# test: 執行基本測試套件
# - 切換到 tests 目錄並執行 pytest
# - 使用 -v (verbose) 顯示詳細資訊
# - 使用 --tb=short 簡化錯誤追蹤輸出
test:
	@echo "🧪 正在執行測試套件..."
	cd tests && python -m pytest test_agent.py -v --tb=short
	@echo "✅ 測試套件執行完成"

# test-verbose: 執行測試並顯示所有輸出
# - 加上 -s 參數以顯示 print() 語句
test-verbose:
	@echo "🧪 正在執行測試（詳細輸出）..."
	cd tests && python -m pytest test_agent.py -v -s

# test-coverage: 執行測試並生成覆蓋率報告
# - 生成 HTML 格式的覆蓋率報告
# - 顯示未覆蓋的程式碼行
test-coverage:
	@echo "🧪 正在執行測試並計算覆蓋率..."
	cd tests && python -m pytest test_agent.py --cov=../essay_refiner --cov-report=html --cov-report=term-missing

# ============================================================
# 開發與執行
# ============================================================
# 啟動 ADK 開發伺服器以進行互動式開發與測試

# dev: 開發模式的別名，委派給 run
dev: run

# run: 啟動 ADK Web 伺服器
# - 首先檢查環境變數是否正確設定
# - 啟動後可在 http://localhost:8000 存取
run: check-env
	@echo "🚀 正在啟動 ADK 開發伺服器..."
	@echo "請開啟 http://localhost:8000 並選擇 'essay_refiner'"
	adk web

# ============================================================
# 驗證與示範
# ============================================================
# 提供快速驗證和全面測試功能

# demo: 快速系統驗證
# - 載入 root_agent 並檢查基本配置
# - 驗證代理階段數量和迭代設定
demo:
	@echo "🎯 正在執行快速系統驗證..."
	python -c "from essay_refiner.agent import root_agent; print(f'✅ Root agent 已載入: {root_agent.name}'); print(f'✅ 擁有 {len(root_agent.sub_agents)} 個階段'); print(f'✅ 精煉循環最多迭代 {root_agent.sub_agents[1].max_iterations} 次'); print('✅ 論文精煉系統準備就緒！')"

# validate: 全面驗證系統
# - 測試所有模組匯入
# - 驗證代理配置正確性
# - 檢查循環結構
# - 確認工具整合
# - 執行完整測試套件
validate:
	@echo "🔍 正在執行全面驗證..."
	@echo "1. 測試模組匯入..."
	python -c "from essay_refiner.agent import root_agent, essay_refinement_system, refinement_loop, initial_writer, critic, refiner, exit_loop; print('✅ 所有匯入成功')"
	@echo "2. 測試代理配置..."
	python -c "from essay_refiner.agent import root_agent; assert root_agent.name == 'EssayRefinementSystem'; assert len(root_agent.sub_agents) == 2; print('✅ 代理配置有效')"
	@echo "3. 測試循環結構..."
	python -c "from essay_refiner.agent import refinement_loop; assert refinement_loop.max_iterations == 5; assert len(refinement_loop.sub_agents) == 2; print('✅ 循環結構有效')"
	@echo "4. 測試工具整合..."
	python -c "from essay_refiner.agent import refiner, exit_loop; assert len(refiner.tools) == 1; assert refiner.tools[0] == exit_loop; print('✅ 工具整合有效')"
	@echo "5. 執行測試套件..."
	make test
	@echo "🎉 所有驗證通過！"

# ============================================================
# 程式碼品質檢查
# ============================================================
# 使用 flake8 和 black 進行程式碼品質與格式檢查

# check: 執行 linting 和格式檢查
# - flake8: 檢查程式碼風格和潛在錯誤
# - black: 驗證程式碼格式是否符合標準
check:
	@echo "🔍 正在執行程式碼檢查與格式驗證..."
	flake8 essay_refiner tests --max-line-length=100 --ignore=E203,W503
	black --check essay_refiner tests

# ============================================================
# 清理命令
# ============================================================
# 移除暫存檔案、快取和編譯產物

# clean: 清理快取檔案和產物
# - 移除 __pycache__ 目錄
# - 移除 .pytest_cache 目錄
# - 移除覆蓋率相關檔案
# - 移除 .pyc 編譯檔案
clean:
	@echo "🧹 正在清理快取檔案和產物..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .coverage -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete

# reset: 重置到乾淨狀態
# - 執行 clean 清理所有產物
# - 保留原始碼不受影響
reset: clean
	@echo "🔄 正在重置到乾淨狀態..."
	@echo "注意：此操作會移除所有生成的檔案，但保留原始碼"
	# 如需要，可在此處加入額外的重置邏輯

# ============================================================
# 環境檢查（內部使用）
# ============================================================
# 驗證必要的環境變數是否已正確設定
# 支援兩種認證方式：API Key 或 Service Account

# check-env: 檢查 Google API 認證配置
# - 方法 1: GOOGLE_API_KEY（適用於 Gemini API）
# - 方法 2: GOOGLE_APPLICATION_CREDENTIALS（適用於 VertexAI）
check-env:
	@if [ -z "$$GOOGLE_API_KEY" ] && [ -z "$$GOOGLE_APPLICATION_CREDENTIALS" ]; then \
		echo "❌ 錯誤：未配置身份驗證"; \
		echo ""; \
		echo "請選擇以下其中一種身份驗證方式："; \
		echo ""; \
		echo "🔑 方法 1 - API Key（Gemini API）："; \
		echo "   export GOOGLE_API_KEY=your_api_key_here"; \
		echo "   在此處取得免費金鑰：https://aistudio.google.com/app/apikey"; \
		echo ""; \
		echo "🔐 方法 2 - Service Account（VertexAI）："; \
		echo "   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json"; \
		echo "   export GOOGLE_CLOUD_PROJECT=your_project_id"; \
		echo "   在此處建立憑證：https://console.cloud.google.com/iam-admin/serviceaccounts"; \
		echo ""; \
		exit 1; \
	fi
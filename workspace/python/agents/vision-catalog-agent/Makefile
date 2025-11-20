# 教學 21：多模態與影像處理
# 使用合成影像生成的視覺化產品目錄分析器

.PHONY: help setup dev test demo clean lint download-images analyze generate coverage

# 預設目標 - 顯示說明
help:
	@echo "🚀 教學 21：多模態與影像處理"
	@echo ""
	@echo "快速入門指令："
	@echo "  make setup          - 安裝依賴套件"
	@echo "  make download-images - 取得範例產品圖片"
	@echo "  make dev            - 啟動視覺目錄代理"
	@echo "  make demo           - 顯示範例提示"
	@echo ""
	@echo "影像分析指令："
	@echo "  make analyze        - 分析所有範例圖片 (批次)"
	@echo "  make generate       - 生成合成產品模型 ⭐"
	@echo ""
	@echo "進階指令："
	@echo "  make test           - 執行所有測試"
	@echo "  make coverage       - 執行測試並產出覆蓋率報告"
	@echo "  make lint           - 執行程式碼檢查工具"
	@echo "  make clean          - 清除生成的檔案"
	@echo ""
	@echo "💡 第一次使用？請執行：make setup && make download-images && make dev"

# 安裝依賴套件
setup:
	@echo "📦 正在安裝依賴套件..."
	pip install -r requirements.txt
	pip install -e .
	@echo "✅ 設定完成！"
	@echo ""
	@echo "後續步驟："
	@echo "  1. 設定您的 API 金鑰：export GOOGLE_API_KEY=your_key"
	@echo "  2. 下載範例：make download-images"
	@echo "  3. 啟動代理：make dev"

# 下載範例產品圖片
download-images:
	@echo "📸 正在從 Unsplash 下載範例產品圖片..."
	@echo ""
	python3 download_images.py
	@echo ""
	@echo "✅ 範例圖片已下載至 _sample_images/"
	@echo "   • laptop.jpg"
	@echo "   • headphones.jpg"
	@echo "   • smartwatch.jpg"

# 分析所有範例圖片
analyze: check-env
	@echo "🔍 正在分析所有範例產品圖片..."
	@echo ""
	@echo "此操作將會："
	@echo "  • 載入每個範例圖片"
	@echo "  • 使用視覺模型進行分析"
	@echo "  • 生成專業的產品目錄條目"
	@echo ""
	python3 analyze_samples.py

# 生成合成產品模型
generate: check-env
	@echo "🎨 正在生成合成產品模型..."
	@echo ""
	@echo "此操作將會："
	@echo "  • 生成 3 張合成產品圖片"
	@echo "  • 分析每張生成的圖片"
	@echo "  • 建立專業的產品目錄條目"
	@echo ""
	@echo "產品：桌燈、皮革錢包、電競滑鼠"
	@echo ""
	python3 generate_mockups.py

# 啟動視覺目錄代理
dev: check-env
	@echo "🤖 正在啟動視覺目錄代理..."
	@echo ""
	@echo "🎯 代理功能："
	@echo "   • 列出可用的範例圖片"
	@echo "   • 生成合成產品模型 ⭐ 新功能"
	@echo "   • 分析上傳的圖片 (拖放)"
	@echo "   • 從檔案路徑分析圖片"
	@echo "   • 比較多張產品圖片"
	@echo ""
	@echo "📱 網站介面：http://localhost:8000"
	@echo "🎯 代理：從下拉選單中選擇 'vision_catalog_agent'"
	@echo ""
	@echo "💬 試試這些範例提示："
	@echo "   • '你有什麼範例圖片？'"
	@echo "   • '生成一個極簡風格桌燈的模型'"
	@echo "   • [上傳圖片] '分析這個產品'"
	@echo "   • '分析 _sample_images/laptop.jpg'"
	@echo "   • '比較筆記型電腦和耳機的圖片'"
	@echo ""
	@echo "⚡ 伺服器將在下方啟動。按 Ctrl+C 停止。"
	@echo ""
	adk web

# 執行所有測試
test: check-env
	@echo "🧪 正在執行測試..."
	pytest tests/ -v --tb=short

# 執行測試並產出覆蓋率報告
coverage: check-env
	@echo "🧪 正在執行測試並計算覆蓋率..."
	pytest tests/ --cov=vision_catalog_agent --cov-report=html --cov-report=term
	@echo ""
	@echo "✅ 覆蓋率報告已生成！"
	@echo "📊 開啟 htmlcov/index.html 查看詳細報告"

# 顯示示範提示與使用範例
demo:
	@echo "=== 教學 21：多模態與影像處理示範 ==="
	@echo ""
	@echo "本教學示範："
	@echo "  • 使用 Gemini 視覺模型處理圖片"
	@echo "  • 使用 types.Part 處理多模態內容"
	@echo "  • 建立基於視覺的產品目錄分析器"
	@echo "  • 處理多個圖片輸入"
	@echo "  • 產品目錄條目的成品管理"
	@echo ""
	@echo "🎯 建議：直接上傳圖片 (ADK 網站介面)"
	@echo ""
	@echo "1. 執行：make dev"
	@echo "2. 開啟：http://localhost:8000"
	@echo "3. 選擇：從下拉選單中選擇 'vision_catalog_agent'"
	@echo "4. 將圖片拖放或貼到聊天室中"
	@echo "5. 試試這些搭配上傳圖片的提示："
	@echo "   • '分析此產品並建立一個目錄條目'"
	@echo "   • '比較這兩張產品圖片'"
	@echo "   • '這個產品有什麼特色？'"
	@echo ""
	@echo "📁 替代方案：基於檔案的影像分析"
	@echo ""
	@echo "1. 基本影像分析："
	@echo "   '分析範例筆記型電腦圖片並描述你看到了什麼'"
	@echo ""
	@echo "2. 產品目錄條目："
	@echo "   '分析 _sample_images/laptop.jpg 並建立一個目錄條目'"
	@echo ""
	@echo "3. 多張圖片："
	@echo "   '比較筆記型電腦和耳機的圖片'"
	@echo ""
	@echo "4. 批次處理："
	@echo "   '分析 _sample_images 目錄中的所有圖片'"
	@echo ""
	@echo "🤖 自動化分析：以程式化方式分析所有範例"
	@echo ""
	@echo "執行 'make analyze' 來一次分析所有三張範例圖片"
	@echo "這將為每個產品生成專業的目錄條目"
	@echo ""
	@echo "🎨 合成影像生成：建立產品模型"
	@echo ""
	@echo "執行 'make generate' 來建立合成產品圖片"
	@echo "當你還沒有真實照片時，這是製作原型的好方法！"
	@echo "範例：桌燈、皮革錢包、電競滑鼠等"
	@echo ""
	@echo "執行 'make dev' 來啟動 ADK 網站介面"
	@echo ""

# 執行程式碼檢查工具
lint:
	@echo "🔍 正在執行檢查工具..."
	@echo "正在檢查代理程式碼..."
	python -m py_compile vision_catalog_agent/*.py
	@echo "正在檢查測試程式碼..."
	python -m py_compile tests/*.py
	@echo "✅ 所有程式碼都通過語法檢查！"

# 清除生成的檔案
clean:
	@echo "🧹 正在清除..."
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	rm -rf vision_catalog_agent/__pycache__ tests/__pycache__
	rm -rf *.egg-info dist build
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "✅ 清除完成！"

# 檢查環境 (內部使用)
check-env:
	@if [ -z "$$GOOGLE_API_KEY" ] && [ -z "$$GOOGLE_APPLICATION_CREDENTIALS" ]; then \
		echo "❌ 錯誤：未設定驗證"; \
		echo ""; \
		echo "請選擇以下其中一種驗證方式："; \
		echo ""; \
		echo "🔑 方式 1 - API 金鑰 (Gemini API)："; \
		echo "   export GOOGLE_API_KEY=your_api_key_here"; \
		echo "   在此取得免費金鑰：https://aistudio.google.com/app/apikey"; \
		echo ""; \
		echo "🔐 方式 2 - 服務帳戶 (VertexAI)："; \
		echo "   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json"; \
		echo "   export GOOGLE_CLOUD_PROJECT=your_project_id"; \
		echo "   在此建立憑證：https://console.cloud.google.com/iam-admin/serviceaccounts"; \
		echo ""; \
		exit 1; \
	fi

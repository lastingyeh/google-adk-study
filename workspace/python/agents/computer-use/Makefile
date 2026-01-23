# 定義偽標靶，防止與同名檔案衝突
.PHONY: install dev

# 安裝所有必要的相依套件，包括 Python 套件與 Playwright 瀏覽器環境
install:
	# 安裝 requirements.txt 中定義的 Python 套件
	uv pip install -r requirements.txt
	# 安裝 Playwright 所需的系統相依項目 (Chromium)
	playwright install-deps chromium
	# 安裝 Chromium 瀏覽器
	playwright install chromium

# 啟動 ADK 網頁介面以與電腦使用代理互動
dev:
	adk web

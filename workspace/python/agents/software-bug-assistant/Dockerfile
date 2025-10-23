# 使用已預裝 uv 的 Python 映像檔
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# 將專案安裝到 `/app` 目錄
WORKDIR /app

# 從快取複製而不是連結，因為這是掛載的卷
ENV UV_LINK_MODE=copy
# 設定 Python 輸出不緩衝
ENV PYTHONUNBUFFERED=1

# 將當前目錄所有檔案加入到 /app
ADD . /app

# 使用鎖定檔安裝專案的依賴項（不安裝專案本身，不安裝開發依賴）
RUN uv sync --locked --no-install-project --no-dev

# 然後加入專案其餘的原始碼並安裝
# 將依賴項與專案分開安裝可以優化層快取
RUN uv sync --locked --no-dev

# 將環境中的可執行檔放在路徑的前面
ENV PATH="/app/.venv/bin:$PATH"

# 暴露端口
EXPOSE 8080

# 預設執行 adk web，如果需要也可以執行 api_server
ENTRYPOINT ["uv", "run", "adk", "web", "--host", "0.0.0.0", "--port", "8080"]
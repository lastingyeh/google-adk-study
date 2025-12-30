# 使用官方的 Python 3.11-slim 作為基礎映像。slim 版本是一個輕量化的版本，有助於減小最終映像的大小。
FROM python:3.11-slim

# 安裝 uv，一個快速的 Python 套件安裝器與解析器。
# --no-cache-dir 選項可以防止 pip 儲存快取，進一步減小映像體積。
RUN pip install --no-cache-dir uv==0.8.13

# 設定容器內的工作目錄為 /code。後續的指令都會在這個目錄下執行。
WORKDIR /code

# 複製專案設定檔、README 和 uv 的鎖定檔到工作目錄。
# uv.lock* 包含了依賴項的精確版本，確保可重現的建置。
COPY ./pyproject.toml ./README.md ./uv.lock* ./

# 複製應用程式的原始碼 (app 資料夾) 到容器的 /code/app 目錄。
COPY ./app ./app

# 使用 uv sync --frozen 指令來安裝鎖定檔中指定的依賴項。
# --frozen 確保安裝與鎖定檔完全相同的版本。
RUN uv sync --frozen

# 定義一個建置時參數 COMMIT_SHA，用於傳入 Git 的 commit SHA。
ARG COMMIT_SHA=""
# 將建置時參數 COMMIT_SHA 的值設定為環境變數，使其在容器執行時可用。
ENV COMMIT_SHA=${COMMIT_SHA}

# 定義一個建置時參數 AGENT_VERSION，用於傳入代理程式的版本號。
ARG AGENT_VERSION=0.0.0
# 將建置時參數 AGENT_VERSION 的值設定為環境變數。
ENV AGENT_VERSION=${AGENT_VERSION}

# 聲明容器在執行時會監聽 8080 連接埠。
EXPOSE 8080

# 設定容器啟動時要執行的預設指令。
# 使用 "uv run" 啟動 uvicorn ASGI 伺服器來運行 app.fast_api_app 中的 FastAPI 應用程式。
# --host 0.0.0.0 讓伺服器可以從容器外部存取。
# --port 8080 指定伺服器監聽的連接埠。
CMD ["uv", "run", "uvicorn", "app.fast_api_app:app", "--host", "0.0.0.0", "--port", "8080"]
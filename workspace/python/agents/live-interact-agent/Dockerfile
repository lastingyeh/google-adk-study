# 版權 2025 Google LLC
#
# 根據 Apache 授權條款 2.0 版（「本授權」）授權；
# 除非符合本授權，否則您不得使用此檔案。
# 您可以在以下網址取得本授權的副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據本授權分發的軟體
# 是基於「原樣」的基礎分發，不附帶任何明示或暗示的保證或條件。
# 有關管理本授權下特定語言的權限和限制，請參閱本授權。

# 使用官方的 Python 3.11-slim 作為基礎映像檔。slim 版本是一個輕量化的版本，有助於減小最終映像檔的大小。
FROM python:3.11-slim

# 安裝 uv 0.8.13 版本。uv 是一個極快的 Python 套件安裝器與解析器。
# --no-cache-dir 選項可以防止 pip 儲存快取，進一步減小映像檔大小。
RUN pip install --no-cache-dir uv==0.8.13

# 為了建置前端專案，需要安裝 Node.js。
# 這是一個多步驟的命令，使用 '&&' 串連以確保它們在同一個映像層中執行，有助於最佳化。
RUN apt-get update && apt-get install -y \
    curl \
    # 使用 curl 從 nodesource 下載 Node.js 18.x 的安裝腳本並執行。
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    # 安裝 Node.js。
    && apt-get install -y nodejs \
    # 清理 apt 套件管理器的快取，刪除不再需要的檔案，以減小映像檔大小。
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 在容器內設定工作目錄為 /code。後續的指令都會在這個目錄下執行。
WORKDIR /code

# 複製專案設定檔、README 和 uv 的相依性鎖定檔到工作目錄。
# 'uv.lock*' 使用萬用字元以匹配可能的不同平台鎖定檔。
# 優先複製這些檔案可以利用 Docker 的快取機制，當程式碼變更但相依性不變時，不需重新安裝相依套件。
COPY ./pyproject.toml ./README.md ./uv.lock* ./

# 複製後端應用程式的原始碼到容器的 /code/app 目錄。
COPY ./app ./app
# 複製前端專案的原始碼到容器的 /code/frontend 目錄。
COPY ./frontend ./frontend
# 進入 frontend 目錄，使用 'npm ci' 進行乾淨的安裝（根據 package-lock.json），然後執行 'npm run build' 來建置前端專案。
RUN cd frontend && npm ci && npm run build

# 使用 uv 根據 uv.lock 鎖定檔來同步（安裝）Python 的相依套件。
# --frozen 參數確保安裝的套件版本與鎖定檔完全一致。
RUN uv sync --frozen

# 定義一個建置時參數 COMMIT_SHA，用於傳入 Git 的 commit SHA。
ARG COMMIT_SHA=""
# 將建置時傳入的 COMMIT_SHA 參數設定為環境變數，讓應用程式在執行時可以讀取。
ENV COMMIT_SHA=${COMMIT_SHA}

# 定義一個建置時參數 AGENT_VERSION，用於傳入代理程式的版本號。
ARG AGENT_VERSION=0.0.0
# 將建置時傳入的 AGENT_VERSION 參數設定為環境變數。
ENV AGENT_VERSION=${AGENT_VERSION}

# 向 Docker 聲明容器在執行時會監聽 8080 連接埠。這是一個文件性質的指令，本身不會發布連接埠。
EXPOSE 8080

# 設定容器啟動時要執行的預設命令。
# 使用 'uv run' 來執行 uvicorn 伺服器，以啟動位於 app.fast_api_app 模組中的 app 物件（一個 FastAPI 應用）。
# --host 0.0.0.0 讓伺服器監聽所有網路介面，使其可以從容器外部存取。
# --port 8080 指定伺服器監聽的連接埠。
CMD ["uv", "run", "uvicorn", "app.fast_api_app:app", "--host", "0.0.0.0", "--port", "8080"]
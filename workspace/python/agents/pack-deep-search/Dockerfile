# 版權所有 2025 Google LLC
#
# 根據 Apache 授權條款第 2.0 版（以下簡稱「授權條款」）授權，
# 除非符合授權條款，否則您不得使用此檔案。
# 您可以在下列網址取得授權條款副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據授權條款分發的軟體
# 係以「現狀」方式提供，不附帶任何明示或默示之擔保或條件。
# 請參閱授權條款以瞭解特定語言下的權限與限制。
#

FROM python:3.11-slim
# 使用 Python 3.11 精簡版作為基底映像

RUN pip install --no-cache-dir uv==0.8.13
# 安裝 uv 0.8.13，並且不快取安裝檔案以減少映像大小

WORKDIR /code
# 設定工作目錄為 /code

COPY ./pyproject.toml ./README.md ./uv.lock* ./
# 複製 pyproject.toml、README.md 及所有 uv.lock 開頭的檔案到容器工作目錄

COPY ./app ./app
# 複製 app 目錄到容器內的 app 目錄

RUN uv sync --frozen
# 使用 uv 工具根據鎖定檔安裝所有相依套件，--frozen 確保完全依照鎖定檔

ARG COMMIT_SHA=""
ENV COMMIT_SHA=${COMMIT_SHA}
# 設定可選的建置參數 COMMIT_SHA，並設為環境變數

ARG AGENT_VERSION=0.0.0
ENV AGENT_VERSION=${AGENT_VERSION}
# 設定可選的建置參數 AGENT_VERSION，並設為環境變數

EXPOSE 8080
# 開放 8080 埠供外部連線

CMD ["uv", "run", "uvicorn", "app.fast_api_app:app", "--host", "0.0.0.0", "--port", "8080"]
# 預設執行指令：使用 uv 執行 uvicorn 啟動 FastAPI 應用，監聽 0.0.0.0:8080
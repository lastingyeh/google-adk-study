# 使用 Python 3.11 的精簡版映像檔
FROM python:3.11-slim
# 安裝 uv 套件，版本為 0.8.13，不使用快取
RUN pip install --no-cache-dir uv==0.8.13
# 設定工作目錄為 /code
WORKDIR /code
# 複製 pyproject.toml、README.md 及 uv.lock* 到容器工作目錄
COPY ./pyproject.toml ./README.md ./uv.lock* ./
# 複製 policy_as_code_agent 資料夾到容器
COPY ./policy_as_code_agent ./policy_as_code_agent
# 使用 uv 套件同步安裝依賴，並鎖定版本
RUN uv sync --frozen
# 宣告 COMMIT_SHA 參數，預設為空字串
ARG COMMIT_SHA=""
# 設定環境變數 COMMIT_SHA 為參數值
ENV COMMIT_SHA=${COMMIT_SHA}
# 宣告 AGENT_VERSION 參數，預設為 0.0.0
ARG AGENT_VERSION=0.0.0
# 設定環境變數 AGENT_VERSION
ENV AGENT_VERSION=${AGENT_VERSION}
# 開放 8080 埠口給外部存取
EXPOSE 8080
# 啟動 uvicorn 伺服器，監聽 0.0.0.0:8080，執行 policy_as_code_agent.fast_api_app:app
CMD ["uv", "run", "uvicorn", "policy_as_code_agent.fast_api_app:app", "--host", "0.0.0.0", "--port", "8080"] 
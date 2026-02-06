# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# 使用 Python 3.11 slim 版本作為基礎映像檔
FROM python:3.11-slim

# 安裝 uv 套件管理器，不使用快取以減小映像檔大小
RUN pip install --no-cache-dir uv==0.8.13

# 設定工作目錄為 /code
WORKDIR /code

# 複製專案設定檔與依賴鎖定檔
COPY ./pyproject.toml ./README.md ./uv.lock* ./

# 複製 RAG 應用程式程式碼
COPY ./rag ./rag

# 使用 uv 同步依賴套件 (frozen 模式確保版本一致)
RUN uv sync --frozen

# 定義建置參數 COMMIT_SHA，預設為空字串
ARG COMMIT_SHA=""
# 設定環境變數 COMMIT_SHA
ENV COMMIT_SHA=${COMMIT_SHA}

# 定義建置參數 AGENT_VERSION，預設為 0.0.0
ARG AGENT_VERSION=0.0.0
# 設定環境變數 AGENT_VERSION
ENV AGENT_VERSION=${AGENT_VERSION}

# 宣告容器監聽埠號 8080
EXPOSE 8080

# 啟動應用程式命令：使用 uv 執行 uvicorn 伺服器
CMD ["uv", "run", "uvicorn", "rag.fast_api_app:app", "--host", "0.0.0.0", "--port", "8080"]

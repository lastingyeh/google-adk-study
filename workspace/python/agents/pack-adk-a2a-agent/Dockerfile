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

# 使用 Python 3.11 slim 版本作為基底映像檔
FROM python:3.11-slim

# 安裝 uv 套件管理器
RUN pip install --no-cache-dir uv==0.8.13

# 設定工作目錄
WORKDIR /code

# 複製專案設定檔與依賴鎖定檔
COPY ./pyproject.toml ./README.md ./uv.lock* ./

# 複製應用程式程式碼
COPY ./app ./app

# 同步依賴套件 (凍結版本)
RUN uv sync --frozen

# 設定 Commit SHA 環境變數
ARG COMMIT_SHA=""
ENV COMMIT_SHA=${COMMIT_SHA}

# 設定代理程式版本環境變數
ARG AGENT_VERSION=0.0.0
ENV AGENT_VERSION=${AGENT_VERSION}

# 暴露 8080 連接埠
EXPOSE 8080

# 啟動應用程式
CMD ["uv", "run", "uvicorn", "app.fast_api_app:app", "--host", "0.0.0.0", "--port", "8080"]

# 重點摘要
# - **核心概念**：容器化、環境配置。
# - **關鍵技術**：Docker, Python 3.11, uv。
# - **重要結論**：定義了應用程式的建置與執行環境，使用 uv 進行依賴管理。
# - **行動項目**：使用此檔案建置 Docker 映像檔。

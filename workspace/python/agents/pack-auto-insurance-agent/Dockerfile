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

# 使用 Python 3.11 輕量版作為基礎映像檔
FROM python:3.11-slim

# 安裝 uv 封裝管理工具
RUN pip install --no-cache-dir uv==0.8.13

# 設定工作目錄
WORKDIR /code

# 複製設定檔與說明文件
COPY ./pyproject.toml ./README.md ./uv.lock* ./

# 複製代理人原始碼
COPY ./auto_insurance_agent ./auto_insurance_agent

# 使用 uv 同步依賴（保持版本鎖定）
RUN uv sync --frozen

# 設定 Git Commit SHA 參數
ARG COMMIT_SHA=""
ENV COMMIT_SHA=${COMMIT_SHA}

# 設定代理人版本參數
ARG AGENT_VERSION=0.0.0
ENV AGENT_VERSION=${AGENT_VERSION}

# 開放 8080 埠位
EXPOSE 8080

# 啟動應用程式（使用 uvicorn 執行 FastAPI 應用）
CMD ["uv", "run", "uvicorn", "auto_insurance_agent.fast_api_app:app", "--host", "0.0.0.0", "--port", "8080"]

# ==========================================
# 重點摘要
# ==========================================
# - 核心概念：此 Dockerfile 定義了如何將汽車保險代理人打包成容器化映像檔，以便在雲端環境（如 Cloud Run 或 GKE）中部署。
# - 關鍵技術：
#     - uv: 現代化且極速的 Python 套件與環境管理工具。
#     - FastAPI + Uvicorn: 用於提供 RESTful API 介面，讓代理人能透過網路被訪問。
#     - Docker Multi-stage Concept: 雖此處為單一階段，但採用了輕量級基礎映像檔並清理快取以減少體積。
# - 重要結論：該設定確保了開發與生產環境的一致性，並預留了版本控制與 Commit 追蹤的環境變數。
# - 行動項目：
#     - 建置映像檔：`docker build -t auto-insurance-agent .`
#     - 本地運行測試：`docker run -p 8080:8080 auto-insurance-agent`

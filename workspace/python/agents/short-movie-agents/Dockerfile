# 版權所有 2025 Google LLC
#
# 根據 Apache 許可證 2.0 版（「許可證」）授權；
# 除非遵守許可證，否則您不得使用此檔案。
# 您可以在以下網址獲得許可證副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據許可證分發的軟體
# 是按「原樣」分發的，不附帶任何形式的明示或暗示的保證或條件。
# 請參閱許可證以瞭解管理權限和限制的特定語言。

# 使用輕量級的 Python 3.13 鏡像作為基礎
FROM python:3.13-slim

# 安裝指定版本的 uv 套件管理器
RUN pip install --no-cache-dir uv==0.6.12

# 設定容器內的工作目錄
WORKDIR /code

# 複製專案配置文件和說明文件
COPY ./pyproject.toml ./README.md ./uv.lock* ./

# 複製應用程式核心程式碼
COPY ./app ./app

# 使用 uv 同步依賴項，確保版本一致性
RUN uv sync --frozen

# 開放 8080 端口供外部存取
EXPOSE 8080

# 啟動命令：使用 uv 執行 uvicorn 伺服器
CMD ["uv", "run", "uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8080"]

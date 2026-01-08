# 程式碼說明文件

## 本文件目的
本文件旨在詳細說明專案中的關鍵程式碼片段及其功能，幫助開發者理解專案的內部運作機制。

### 關鍵程式碼說明
#### Q: 為什麼在 adk web & fastapi 啟動時會預設生成 `.adk/session.db`

  A: **說明**:
  在 `policy_as_code_agent/fast_api_app.py` 檔案中的 `get_fast_api_app` 函式呼叫區塊觸發建立的。

  ##### 詳細分析如下：

  1. **關鍵程式碼區塊**： 在 `policy_as_code_agent/fast_api_app.py` 第 64-72 行左右：

     ```python
     # 使用 get_fast_api_app 建立 FastAPI 應用程式實例
     app: FastAPI = get_fast_api_app(
         agents_dir=AGENT_DIR,  # 代理程式目錄
         web=True,  # 啟用 Web 介面
         artifact_service_uri=artifact_service_uri,  # 產物服務 URI
         allow_origins=allow_origins,  # 允許的來源網域
         session_service_uri=session_service_uri,  # session 服務 URI
         otel_to_cloud=True,  # 將 OpenTelemetry 資料傳送到 Cloud
     )
     ```

  2. **建立機制**：
     - 在該檔案的前半部，程式碼會嘗試從環境變數（如 `INSTANCE_CONNECTION_NAME` 和 `DB_PASS`）讀取 Cloud SQL 的設定。
     - 如果這些環境變數未設定（常見於本地開發環境），變數 `session_service_uri` 將保持為 `None`。
     - 當 `session_service_uri` 為 `None` 並傳遞給 `get_fast_api_app` 時，Google ADK 框架內部的 `service_factory` 會預設使用本地 SQLite 存儲。
     - 根據 ADK 框架的慣例，它會在 `agents_dir` 下的代理程式目錄中建立一個 `.adk` 資料夾，並在其中生成 `session.db` 檔案用來儲存會話資訊。
     -
  3. **參考程式碼**：
      - [[adk-python] `local-storage.py`](https://github.com/google/adk-python/blob/main/src/google/adk/cli/utils/local_storage.py)
      - [[adk-python] `service_factory.py`](https://github.com/google/adk-python/blob/main/src/google/adk/cli/utils/service_factory.py)
      - [[adk-python] `cli.py`](https://github.com/google/adk-python/blob/main/src/google/adk/cli/cli.py)
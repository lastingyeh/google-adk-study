# 生成式 AI 應用程式的強大負載測試

本目錄提供了一個針對生成式 AI 應用程式的完整負載測試框架，利用領先的開源負載測試工具 [Locust](http://locust.io) 的強大功能。

## 本地負載測試

按照以下步驟在本機上執行負載測試：

**1. 啟動 FastAPI 伺服器：**

在另一個終端中啟動 FastAPI 伺服器：

```bash
uv run uvicorn rag.fast_api_app:app --host 0.0.0.0 --port 8000 --reload
```

**2. （在另一個分頁中）建立包含 Locust 的虛擬環境**
使用另一個終端分頁。建議這樣做以避免與現有應用程式 Python 環境發生衝突。

```bash
python3 -m venv .locust_env && source .locust_env/bin/activate && pip install locust==2.31.1
```

**3. 執行負載測試：**
使用以下命令觸發 Locust 負載測試：

```bash
locust -f tests/load_test/load_test.py \
-H http://127.0.0.1:8000 \
--headless \
-t 30s -u 10 -r 2 \
--csv=tests/load_test/.results/results \
--html=tests/load_test/.results/report.html
```

此命令啟動 30 秒的負載測試，模擬每秒產生 2 個使用者，最多達到 60 個並行使用者。

**結果：**

詳細的 CSV 和 HTML 報告將在 `tests/load_test/.results` 目錄中生成並保存。

## 遠端負載測試（以 Cloud Run 為目標）

此框架也支援針對遠端目標（例如預備環境 Cloud Run 執行個體）進行負載測試。此程序已無縫整合到持續部署 (CD) 管道中。

**先決條件：**

- **依賴項：** 確保您的環境有本地測試所需的相同依賴項。
- **Cloud Run 叫用者角色：** 您需要 `roles/run.invoker` 角色來叫用 Cloud Run 服務。

**步驟：**

**1. 取得 Cloud Run 服務 URL：**

導覽至 Cloud Run 主控台，選取您的服務，並複製頂部顯示的 URL。將此 URL 設定為環境變數：

```bash
export RUN_SERVICE_URL=https://your-cloud-run-service-url.run.app
```

**2. 取得 ID 權杖：**

取得驗證所需的 ID 權杖：

```bash
export _ID_TOKEN=$(gcloud auth print-identity-token -q)
```

**3. 執行負載測試：**
建立包含 Locust 的虛擬環境：
```bash
python3 -m venv .locust_env && source .locust_env/bin/activate && pip install locust==2.31.1
```

執行負載測試。以下命令執行與本地測試相同的負載測試參數，但以遠端 Cloud Run 執行個體為目標。
```bash
locust -f tests/load_test/load_test.py \
-H $RUN_SERVICE_URL \
--headless \
-t 30s -u 60 -r 2 \
--csv=tests/load_test/.results/results \
--html=tests/load_test/.results/report.html
```

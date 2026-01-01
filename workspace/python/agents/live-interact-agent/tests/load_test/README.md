# 生成式 AI 應用程式的穩健性負載測試

此目錄提供了一個全面的負載測試框架，專為您的生成式 AI 應用程式設計，並利用了領先的開源負載測試工具 [Locust](http://locust.io) 的強大功能。

## 本地負載測試

請依照以下步驟在您的本機電腦上執行負載測試：

**1. 啟動 FastAPI 伺服器：**

在一個獨立的終端機中啟動 FastAPI 伺服器：

```bash
# 使用 uv 執行 uvicorn 來啟動 FastAPI 應用程式
# app.fast_api_app:app 指定了應用程式實例的位置
# --host 0.0.0.0 讓伺服器可以從任何網路介面存取
# --port 8000 指定伺服器監聽的埠號
# --reload 啟用自動重載功能，當程式碼變更時會自動重啟伺服器
uv run uvicorn app.fast_api_app:app --host 0.0.0.0 --port 8000 --reload
```

**2. (在另一個分頁) 建立帶有 Locust 的虛擬環境**
建議在另一個終端機分頁中執行此操作，以避免與現有應用程式的 Python 環境發生衝突。

```bash
# python3 -m venv .locust_env：建立一個名為 .locust_env 的新 Python 虛擬環境
# source .locust_env/bin/activate：啟用剛剛建立的虛擬環境
# pip install locust==2.31.1 websockets：在此虛擬環境中安裝指定版本的 Locust 和 websockets 函式庫
python3 -m venv .locust_env && source .locust_env/bin/activate && pip install locust==2.31.1 websockets
```

**3. 執行負載測試：**
使用以下指令觸發 Locust 負載測試：

```bash
# locust：執行 Locust 負載測試工具
# -f tests/load_test/load_test.py：指定要執行的 Locust 測試腳本檔案
# -H http://127.0.0.1:8000：設定測試目標主機的 URL
# --headless：以無頭模式執行，不在網頁介面中顯示即時統計數據
# -t 30s：設定測試的總執行時間為 30 秒
# -u 2：設定要模擬的並行使用者總數為 2
# -r 2：設定每秒產生的使用者數量（spawn rate）為 2
# --csv=tests/load_test/.results/results：將測試結果以 CSV 格式儲存到指定路徑
# --html=tests/load_test/.results/report.html：將測試報告以 HTML 格式儲存到指定路徑
locust -f tests/load_test/load_test.py \
-H http://127.0.0.1:8000 \
--headless \
-t 30s -u 2 -r 2 \
--csv=tests/load_test/.results/results \
--html=tests/load_test/.results/report.html
```

此指令將啟動一個為時 30 秒的負載測試，模擬 2 個並行使用者，每秒產生 2 個使用者。

**結果：**

詳細說明負載測試性能的完整 CSV 和 HTML 報告將會產生並儲存在 `tests/load_test/.results` 目錄中。

## 遠端負載測試 (針對 Cloud Run)

此框架也支援對遠端目標進行負載測試，例如預備環境（staging）的 Cloud Run 實例。此過程已無縫整合到持續交付 (CD) 流程中。

**先決條件：**

- **依賴套件：** 確保您的環境已安裝與本地測試相同的依賴套件。
- **Cloud Run Invoker 角色：** 您需要 `roles/run.invoker` 角色才能呼叫 Cloud Run 服務。

**步驟：**

**1. 啟動 Cloud Run Proxy：**

在一個獨立的終端機中啟動代理，將您的 Cloud Run 服務暴露於本地主機上。代理會自動處理 IAM 身份驗證：

```bash
# gcloud run services proxy：啟動一個本地代理，將流量轉發到指定的 Cloud Run 服務
# YOUR_SERVICE_NAME：您在 Cloud Run 上的服務名稱
# --port=8080：指定本地代理監聽的埠號
# --region us-central1：指定 Cloud Run 服務所在的區域
# --quiet：自動批准元件安裝提示
gcloud run services proxy YOUR_SERVICE_NAME --port=8080 --region us-central1 --quiet
```

請將 `YOUR_SERVICE_NAME` 替換為您的 Cloud Run 服務名稱。`--quiet` 旗標會自動批准元件安裝提示。您也可以選擇性地指定 `--tag` 來針對特定的流量標籤。

**2. (在另一個分頁) 建立帶有 Locust 的虛擬環境：**

在另一個終端機分頁中執行：

```bash
# python3 -m venv .locust_env：建立一個名為 .locust_env 的新 Python 虛擬環境
# source .locust_env/bin/activate：啟用剛剛建立的虛擬環境
# pip install locust==2.31.1 websockets：在此虛擬環境中安裝指定版本的 Locust 和 websockets 函式庫
python3 -m venv .locust_env && source .locust_env/bin/activate && pip install locust==2.31.1 websockets
```

**3. 執行負載測試：**

對代理的服務執行負載測試。代理會自動處理身份驗證：

```bash
# locust：執行 Locust 負載測試工具
# -f tests/load_test/load_test.py：指定要執行的 Locust 測試腳本檔案
# -H http://127.0.0.1:8080：設定測試目標主機的 URL（指向本地 Cloud Run 代理）
# --headless：以無頭模式執行，不在網頁介面中顯示即時統計數據
# -t 30s：設定測試的總執行時間為 30 秒
# -u 2：設定要模擬的並行使用者總數為 2
# -r 2：設定每秒產生的使用者數量（spawn rate）為 2
# --csv=tests/load_test/.results/results：將測試結果以 CSV 格式儲存到指定路徑
# --html=tests/load_test/.results/report.html：將測試報告以 HTML 格式儲存到指定路徑
locust -f tests/load_test/load_test.py \
-H http://127.0.0.1:8080 \
--headless \
-t 30s -u 2 -r 2 \
--csv=tests/load_test/.results/results \
--html=tests/load_test/.results/report.html
```

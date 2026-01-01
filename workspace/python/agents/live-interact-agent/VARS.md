## 環境變數

| 變數名稱 | 說明 | 預設值/範例 | 設定位置 |
| :--- | :--- | :--- | :--- |
| `LOGS_BUCKET_NAME` | 指定用於儲存遙測日誌的 Google Cloud Storage (GCS) 儲存桶名稱。這是啟用遙測功能的關鍵變數。 | **範例**: `gs://your-log-bucket` | `app/fast_api_app.py`<br>`app/app_utils/telemetry.py` |
| `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` | 控制是否捕獲 GenAI 的訊息內容。程式碼會檢查此變數，如果其值不是 `"false"`，則會強制將其設定為 `"NO_CONTENT"`，表示只記錄元數據，不記錄實際的提示和回應內容。 | `"false"` | `app/app_utils/telemetry.py` |
| `OTEL_INSTRUMENTATION_GENAI_UPLOAD_FORMAT` | 設定遙測數據上傳到 GCS 的檔案格式。 | `"jsonl"` | `app/app_utils/telemetry.py` |
| `OTEL_INSTRUMENTATION_GENAI_COMPLETION_HOOK` | 設定完成追蹤後的掛鉤（hook）動作。 | `"upload"` (表示完成後自動上傳) | `app/app_utils/telemetry.py` |
| `OTEL_SEMCONV_STABILITY_OPT_IN` | 選擇加入 OpenTelemetry 最新的 GenAI 實驗性語義慣例。 | `"gen_ai_latest_experimental"` | `app/app_utils/telemetry.py` |
| `COMMIT_SHA` | 用於標記服務版本的 Git commit SHA。如果未設定，會用作 `OTEL_RESOURCE_ATTRIBUTES` 的一部分。 | `"dev"` | `app/app_utils/telemetry.py` |
| `OTEL_RESOURCE_ATTRIBUTES` | 設定 OpenTelemetry 的資源屬性，用於在遙測數據中識別服務。 | `service.namespace=live-interact-agent,service.version={COMMIT_SHA}` | `app/app_utils/telemetry.py` |
| `GENAI_TELEMETRY_PATH` | 指定在 GCS 儲存桶中存放遙測數據的路徑。 | `"completions"` | `app/app_utils/telemetry.py` |
| `OTEL_INSTRUMENTATION_GENAI_UPLOAD_BASE_PATH` | 設定遙測數據上傳的完整 GCS 基本路徑。此變數由 `LOGS_BUCKET_NAME` 和 `GENAI_TELEMETRY_PATH` 組成。 | `gs://{LOGS_BUCKET_NAME}/{GENAI_TELEMETRY_PATH}` | `app/app_utils/telemetry.py` |
| `GOOGLE_CLOUD_PROJECT` | Google Cloud 專案 ID。腳本會透過 `google.auth.default()` 自動獲取並設定環境變數。 | (自動偵測) | `app/agent.py` |
| `GOOGLE_CLOUD_LOCATION` | 指定 Google Cloud 區域。 | `"us-central1"` | `app/agent.py` |
| `GOOGLE_GENAI_USE_VERTEXAI` | 啟動 Google VertexAI 作為 LLM 模式。 | `"True"` | `app/agent.py` |
| `PROJECT_ID` | 指定執行資料擷取管道的 Google Cloud 專案 ID。 | (無預設值) | `data_ingestion/data_ingestion_pipeline/submit_pipeline.py` |
| `REGION` | 指定 Vertex AI Pipelines 所在的區域。 | (無預設值) | `data_ingestion/data_ingestion_pipeline/submit_pipeline.py` |
| `PIPELINE_ROOT` | 指定用於存放 Vertex AI Pipeline 中繼產物的 GCS 路徑。 | (無預設值) | `data_ingestion/data_ingestion_pipeline/submit_pipeline.py` |
| `PIPELINE_NAME` | 指定 Vertex AI Pipeline 的名稱。 | (無預設值) | `data_ingestion/data_ingestion_pipeline/submit_pipeline.py` |
| `SERVICE_ACCOUNT` | 指定執行 Vertex AI Pipeline 所使用的服務帳號。 | (無預設值) | `data_ingestion/data_ingestion_pipeline/submit_pipeline.py` |
| `DISABLE_CACHING` | 如果設定為 `"true"`，則會停用 Vertex AI Pipeline 的快取功能。 | `"false"` | `data_ingestion/data_ingestion_pipeline/submit_pipeline.py` |
| `CRON_SCHEDULE` | 設定 Vertex AI Pipeline 的 Cron 排程表達式，用於定期執行。 | (無預設值) | `data_ingestion/data_ingestion_pipeline/submit_pipeline.py` |
| `SCHEDULE_ONLY` | 如果設定為 `"true"`，則僅建立或更新排程，而不立即執行 pipeline。 | `"false"` | `data_ingestion/data_ingestion_pipeline/submit_pipeline.py` |

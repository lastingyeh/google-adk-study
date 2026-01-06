# 匯入 logging 模組，用於記錄應用程式事件
import logging

# 匯入 os 模組，用於與作業系統互動，特別是讀取環境變數
import os


def setup_telemetry() -> str | None:
    """設定 OpenTelemetry 和 GenAI 遙測，並將資料上傳到 Google Cloud Storage (GCS)。"""

    # 從環境變數中獲取用於儲存日誌的 GCS 儲存桶名稱
    bucket = os.environ.get("LOGS_BUCKET_NAME")
    # 從環境變數中獲取是否要擷取 GenAI 訊息內容的設定
    capture_content = os.environ.get(
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "false"
    )
    # 檢查是否已設定儲存桶名稱且 capture_content 不為 "false"
    if bucket and capture_content != "false":
        # 如果條件成立，表示已啟用遙測記錄
        logging.info(
            "提示-回應記錄已啟用 - 模式: NO_CONTENT (僅中繼資料，無提示/回應內容)"
        )
        # 強制設定為 "NO_CONTENT"，確保不記錄敏感的提示和回應內容
        os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "NO_CONTENT"
        # 設定遙測資料的上傳格式為 jsonl (JSON Lines)
        os.environ.setdefault("OTEL_INSTRUMENTATION_GENAI_UPLOAD_FORMAT", "jsonl")
        # 設定完成掛鉤為 "upload"，表示完成時自動上傳
        os.environ.setdefault("OTEL_INSTRUMENTATION_GENAI_COMPLETION_HOOK", "upload")
        # 選擇加入最新的實驗性 GenAI 語意慣例
        os.environ.setdefault(
            "OTEL_SEMCONV_STABILITY_OPT_IN", "gen_ai_latest_experimental"
        )
        # 獲取程式碼的版本（commit SHA），如果沒有則預設為 "dev"
        commit_sha = os.environ.get("COMMIT_SHA", "dev")
        # 設定 OpenTelemetry 的資源屬性，包含服務命名空間和版本
        os.environ.setdefault(
            "OTEL_RESOURCE_ATTRIBUTES",
            f"service.namespace=pack-policy-as-code,service.version={commit_sha}",
        )
        # 獲取 GenAI 遙測資料在 GCS 儲存桶中的路徑，預設為 "completions"
        path = os.environ.get("GENAI_TELEMETRY_PATH", "completions")
        # 設定 GenAI 遙測資料上傳的基礎路徑
        os.environ.setdefault(
            "OTEL_INSTRUMENTATION_GENAI_UPLOAD_BASE_PATH",
            f"gs://{bucket}/{path}",
        )
    else:
        # 如果未設定儲存桶或 capture_content 為 "false"，則停用遙測記錄
        logging.info(
            "提示-回應記錄已停用 (請設定 LOGS_BUCKET_NAME=gs://your-bucket 和 OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=NO_CONTENT 來啟用)"
        )

    # 返回儲存桶名稱，如果未設定則返回 None
    return bucket

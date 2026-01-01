import logging
import os


def setup_telemetry() -> str | None:
    """設定 OpenTelemetry 和 GenAI 遙測，並上傳至 GCS。"""

    # 重點：從環境變數中獲取日誌 GCS 儲存桶名稱。這是啟用遙測的關鍵。
    bucket = os.environ.get("LOGS_BUCKET_NAME")
    # 重點：獲取是否捕獲 GenAI 訊息內容的設定，預設為 "false"。
    capture_content = os.environ.get(
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "false"
    )
    # 重點：檢查是否已設定儲存桶且啟用內容捕獲，以決定是否啟用遙測。
    if bucket and capture_content != "false":
        logging.info(
            "提示-回應日誌記錄已啟用 - 模式: NO_CONTENT (僅元數據，不含提示/回應)"
        )
        # 強制設定捕獲模式為 NO_CONTENT，僅記錄元數據，不記錄實際的提示和回應內容，以保護隱私。
        os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "NO_CONTENT"
        # 設定上傳格式為 jsonl (JSON Lines)。setdefault 表示如果未設定，則使用此預設值。
        os.environ.setdefault("OTEL_INSTRUMENTATION_GENAI_UPLOAD_FORMAT", "jsonl")
        # 設定完成時的掛鉤 (hook) 為 "upload"，表示完成後自動上傳。
        os.environ.setdefault("OTEL_INSTRUMENTATION_GENAI_COMPLETION_HOOK", "upload")
        # 選擇加入最新的 GenAI 實驗性語義慣例。
        os.environ.setdefault(
            "OTEL_SEMCONV_STABILITY_OPT_IN", "gen_ai_latest_experimental"
        )
        # 獲取 Git 的 commit SHA，用於標記服務版本，若無則為 "dev"。
        commit_sha = os.environ.get("COMMIT_SHA", "dev")
        # 設定 OpenTelemetry 資源屬性，包含服務命名空間和版本，方便追蹤。
        os.environ.setdefault(
            "OTEL_RESOURCE_ATTRIBUTES",
            f"service.namespace=rag-km-agents,service.version={commit_sha}",
        )
        # 獲取遙測數據在儲存桶中的路徑，預設為 "completions"。
        path = os.environ.get("GENAI_TELEMETRY_PATH", "completions")
        # 重點：設定遙測數據上傳的完整 GCS 路徑。
        os.environ.setdefault(
            "OTEL_INSTRUMENTATION_GENAI_UPLOAD_BASE_PATH",
            f"gs://{bucket}/{path}",
        )
    else:
        # 如果未設定儲存桶或內容捕獲，則記錄日誌表示遙測已停用。
        logging.info(
            "提示-回應日誌記錄已停用 (設定 LOGS_BUCKET_NAME=gs://your-bucket 和 OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=NO_CONTENT 以啟用)"
        )

    # 返回儲存桶名稱，如果未設定則返回 None。
    return bucket

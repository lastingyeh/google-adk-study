import logging
import os


def setup_telemetry() -> str | None:
    """設定 OpenTelemetry 和 GenAI 遙測，並啟用 GCS 上傳功能。

    此函式會檢查環境變數 `LOGS_BUCKET_NAME` 和 `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT`。
    如果兩者都已設定且 `CAPTURE_MESSAGE_CONTENT` 不為 "false"，則會設定相關的 OpenTelemetry 環境變數，
    以便將 GenAI 的提示和回應資料上傳到指定的 GCS 儲存桶。

    Returns:
        如果啟用了遙測，則傳回日誌儲存桶名稱，否則傳回 None。
    """

    bucket = os.environ.get("LOGS_BUCKET_NAME")
    capture_content = os.environ.get(
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "false"
    )
    if bucket and capture_content != "false":
        logging.info(
            "提示-回應日誌記錄已啟用 - 模式: NO_CONTENT (僅記錄中繼資料，不包含提示/回應內容)"
        )
        # 設定訊息內容捕捉模式為 NO_CONTENT，即不直接在 Trace 中包含內容，而是上傳到 GCS
        os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "NO_CONTENT"
        # 設定上傳格式為 JSONL (JSON Lines)
        os.environ.setdefault("OTEL_INSTRUMENTATION_GENAI_UPLOAD_FORMAT", "jsonl")
        # 設定完成掛鉤為 upload，表示完成時執行上傳
        os.environ.setdefault("OTEL_INSTRUMENTATION_GENAI_COMPLETION_HOOK", "upload")
        # 選擇加入最新的 GenAI 語義慣例實驗功能
        os.environ.setdefault(
            "OTEL_SEMCONV_STABILITY_OPT_IN", "gen_ai_latest_experimental"
        )
        # 設定服務版本，預設為 'dev' 或從 COMMIT_SHA 環境變數獲取
        commit_sha = os.environ.get("COMMIT_SHA", "dev")
        os.environ.setdefault(
            "OTEL_RESOURCE_ATTRIBUTES",
            f"service.namespace=live-interact-agent,service.version={commit_sha}",
        )
        # 設定遙測資料在 GCS 中的路徑，預設為 'completions'
        path = os.environ.get("GENAI_TELEMETRY_PATH", "completions")
        # 設定 OpenTelemetry 上傳的基礎路徑 (GCS URI)
        os.environ.setdefault(
            "OTEL_INSTRUMENTATION_GENAI_UPLOAD_BASE_PATH",
            f"gs://{bucket}/{path}",
        )
    else:
        logging.info(
            "提示-回應日誌記錄已停用 (設定 LOGS_BUCKET_NAME=gs://your-bucket 和 OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=NO_CONTENT 以啟用)"
        )

    return bucket

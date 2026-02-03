# 版權所有 2026 Google LLC
#
# 根據 Apache License, Version 2.0（以下簡稱「授權」）授權；
# 除非遵守授權，否則您不得使用此檔案。
# 您可以在下列網址取得授權副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據授權分發的軟體是以「現狀」方式提供，
# 不附帶任何明示或暗示的擔保或條件。
# 請參閱授權以瞭解授權下的特定語言及限制。


# 匯入日誌與作業系統模組
import logging
import os


# 設定 OpenTelemetry 與 GenAI 遙測，並支援上傳至 GCS。
def setup_telemetry() -> str | None:
    """
    設定 OpenTelemetry 與 GenAI 遙測，並支援上傳至 GCS。
    回傳 bucket 名稱或 None。
    """

    # 取得 bucket 名稱與是否擷取訊息內容的設定
    bucket = os.environ.get("LOGS_BUCKET_NAME")
    capture_content = os.environ.get(
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "false"
    )

    if bucket and capture_content != "false":
        # 啟用提示-回應日誌（僅記錄中繼資料，不含提示/回應內容）
        logging.info(
            "已啟用提示-回應日誌 - 模式：NO_CONTENT（僅中繼資料，不含提示/回應內容）"
        )
        os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "NO_CONTENT"
        os.environ.setdefault("OTEL_INSTRUMENTATION_GENAI_UPLOAD_FORMAT", "jsonl")
        os.environ.setdefault("OTEL_INSTRUMENTATION_GENAI_COMPLETION_HOOK", "upload")
        os.environ.setdefault(
            "OTEL_SEMCONV_STABILITY_OPT_IN", "gen_ai_latest_experimental"
        )
        # 取得 commit SHA，預設為 dev
        commit_sha = os.environ.get("COMMIT_SHA", "dev")
        os.environ.setdefault(
            "OTEL_RESOURCE_ATTRIBUTES",
            f"service.namespace=pack-bidi-streaming,service.version={commit_sha}",
        )
        # 取得遙測資料路徑，預設為 completions
        path = os.environ.get("GENAI_TELEMETRY_PATH", "completions")
        os.environ.setdefault(
            "OTEL_INSTRUMENTATION_GENAI_UPLOAD_BASE_PATH",
            f"gs://{bucket}/{path}",
        )
    else:
        # 未啟用提示-回應日誌
        logging.info(
            "已停用提示-回應日誌（請設定 LOGS_BUCKET_NAME=gs://your-bucket 並將 OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT 設為 NO_CONTENT 以啟用）"
        )

    # 回傳 bucket 名稱（若未設定則為 None）
    return bucket

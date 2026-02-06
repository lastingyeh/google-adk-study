# 版權所有 2025 Google LLC
#
# 根據 Apache 許可證 2.0 版（「許可證」）授權；
# 除非遵守許可證，否則您不得使用此檔案。
# 您可以在以下網址獲得許可證副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據許可證分發的軟體
# 是按「原樣」分發的，無任何明示或暗示的保證或條件。
# 請參閱許可證以了解管理權限和許可證下的限制。

"""
### 摘要
本檔案負責設定 OpenTelemetry 與 GenAI 遙測資料，並支援將日誌上傳至 Google Cloud Storage (GCS)。

### 核心重點
- **核心概念**：GenAI 遙測與日誌管理。
- **關鍵技術**：OpenTelemetry, Google Cloud Storage (GCS), JSONL 格式。
- **重要結論**：預設設定為 `NO_CONTENT` 模式，僅記錄中繼資料而不記錄實際提示與回答內容，以確保隱私與安全。
"""

import logging
import os


def setup_telemetry() -> str | None:
    """設定 OpenTelemetry 與 GenAI 遙測，支援 GCS 上傳功能。"""

    # 獲取存儲桶名稱與內容擷取設定
    bucket = os.environ.get("LOGS_BUCKET_NAME")
    capture_content = os.environ.get(
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "false"
    )

    if bucket and capture_content != "false":
        logging.info(
            "提示-回應日誌記錄已啟用 - 模式：NO_CONTENT（僅中繼資料，不含提示/回應內容）"
        )

        # 強制設定為 NO_CONTENT 模式
        os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "NO_CONTENT"

        # 設定預設上傳格式與勾點 (Hook)
        os.environ.setdefault("OTEL_INSTRUMENTATION_GENAI_UPLOAD_FORMAT", "jsonl")
        os.environ.setdefault("OTEL_INSTRUMENTATION_GENAI_COMPLETION_HOOK", "upload")

        # 啟用最新的 GenAI 實驗性語義慣例
        os.environ.setdefault(
            "OTEL_SEMCONV_STABILITY_OPT_IN", "gen_ai_latest_experimental"
        )

        # 設定資源屬性，如服務名稱與版本
        commit_sha = os.environ.get("COMMIT_SHA", "dev")
        os.environ.setdefault(
            "OTEL_RESOURCE_ATTRIBUTES",
            f"service.namespace=pack-rag,service.version={commit_sha}",
        )

        # 設定 GCS 上傳基礎路徑
        path = os.environ.get("GENAI_TELEMETRY_PATH", "completions")
        os.environ.setdefault(
            "OTEL_INSTRUMENTATION_GENAI_UPLOAD_BASE_PATH",
            f"gs://{bucket}/{path}",
        )
    else:
        logging.info(
            "提示-回應日誌記錄已停用 (若要啟用，請設定 LOGS_BUCKET_NAME=gs://your-bucket 並將 OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT 設為 NO_CONTENT)"
        )
        return None

    return bucket

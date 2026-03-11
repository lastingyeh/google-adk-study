# 版權所有 2026 Google LLC
#
# 根據 Apache License 2.0 版本（「授權」）授權；
# 除非遵守授權，否則您不得使用此檔案。
# 您可以在以下網址取得授權副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據授權散佈的軟體
# 是按「原樣」散佈的，不附任何明示或暗示的保證或條件。
# 請參閱授權以了解管理授權下權限和限制的特定語言。

"""
### 模組說明
此模組負責設定 OpenTelemetry 與 GenAI 的遙測系統，並支援將日誌上傳至 Google Cloud Storage (GCS)。

### 重點摘要
- **核心概念**：自動化配置遙測環境，以監控 AI 代理的效能與行為。
- **關鍵技術**：OpenTelemetry (OTEL), Google Cloud Storage (GCS), 環境變數驅動配置。
- **重要結論**：透過環境變數可以靈活切換日誌記錄模式，並確保敏感內容（如 Prompts）在傳輸過程中的隱私處理。
- **行動項目**：確保 `LOGS_BUCKET_NAME` 已正確設定以啟用上傳功能。
"""

import logging
import os


def setup_telemetry() -> str | None:
    """配置 OpenTelemetry 與 GenAI 遙測，並設定 GCS 上傳功能。"""

    # 從環境變數獲取儲存桶名稱
    bucket = os.environ.get("LOGS_BUCKET_NAME")

    # 檢查是否啟用內容擷取（預設為 false）
    capture_content = os.environ.get(
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "false"
    )

    # 如果設定了儲存桶且 capture_content 不為 "false"，則啟用日誌記錄
    if bucket and capture_content != "false":
        logging.info(
            "提示詞-回應 (Prompt-response) 日誌記錄已啟用 - 模式：NO_CONTENT（僅限元數據，不含提示詞/回應）"
        )

        # 設定 OTEL 相關環境變數
        os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "NO_CONTENT"
        os.environ.setdefault("OTEL_INSTRUMENTATION_GENAI_UPLOAD_FORMAT", "jsonl")
        os.environ.setdefault("OTEL_INSTRUMENTATION_GENAI_COMPLETION_HOOK", "upload")
        os.environ.setdefault(
            "OTEL_SEMCONV_STABILITY_OPT_IN", "gen_ai_latest_experimental"
        )

        # 設定服務版本資訊
        commit_sha = os.environ.get("COMMIT_SHA", "dev")
        os.environ.setdefault(
            "OTEL_RESOURCE_ATTRIBUTES",
            f"service.namespace=guarding-agent,service.version={commit_sha}",
        )

        # 設定 GCS 上傳路徑
        path = os.environ.get("GENAI_TELEMETRY_PATH", "completions")
        os.environ.setdefault(
            "OTEL_INSTRUMENTATION_GENAI_UPLOAD_BASE_PATH",
            f"gs://{bucket}/{path}",
        )
    else:
        # 若未滿足條件，則提示如何啟用日誌記錄
        logging.info(
            "提示詞-回應 (Prompt-response) 日誌記錄已停用 (請設定 LOGS_BUCKET_NAME=gs://您的儲存桶 並將 OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=NO_CONTENT 以啟用)"
        )

    return bucket

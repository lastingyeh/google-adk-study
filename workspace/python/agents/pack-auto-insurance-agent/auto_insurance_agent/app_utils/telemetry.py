# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
### 重點摘要 (程式碼除外)
- **核心概念**：配置 OpenTelemetry (開放遙測) 以監控生成式 AI 代理的行為，並將遙測數據自動上傳至 Google Cloud Storage (GCS)。
- **關鍵技術**：
    - **OpenTelemetry**：用於收集、處理和導出遙測數據。
    - **GCS (Google Cloud Storage)**：作為日誌和遙測數據的後端儲存中心。
    - **環境變數驅動配置**：透過 `os.environ` 動態調整遙測行為（如 `LOGS_BUCKET_NAME`、`COMMIT_SHA`）。
- **重要結論**：該模組確保了在生產環境中對 AI 提示與回應的追蹤，同時透過 `NO_CONTENT` 模式保護敏感內容。
- **行動項目**：
    - 確保部署環境中已設置 `LOGS_BUCKET_NAME` 環境變數。
    - 若需自定義路徑，可設置 `GENAI_TELEMETRY_PATH`。
"""

import logging
import os


def setup_telemetry() -> str | None:
    """
    配置 OpenTelemetry (開放遙測) 與 GenAI 遙測，並上傳至 GCS。
    """

    # 從環境變數獲取日誌儲存桶名稱 (LOGS_BUCKET_NAME)
    bucket = os.environ.get("LOGS_BUCKET_NAME")
    # 檢查是否擷取訊息內容 (OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT)
    capture_content = os.environ.get(
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "false"
    )

    # 如果設定了儲存桶且 capture_content 不為 false，則啟用遙測上傳
    if bucket and capture_content != "false":
        logging.info(
            "提示詞-回應日誌記錄已啟用 - 模式：NO_CONTENT (僅元數據，不包含提示詞/回應內容)"
        )
        # 設定遙測擷取模式為 NO_CONTENT，以符合隱私過度合規要求
        os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "NO_CONTENT"
        # 設定上傳格式為 jsonl
        os.environ.setdefault("OTEL_INSTRUMENTATION_GENAI_UPLOAD_FORMAT", "jsonl")
        # 設定完成勾子 (hook) 為上傳模式
        os.environ.setdefault("OTEL_INSTRUMENTATION_GENAI_COMPLETION_HOOK", "upload")
        # 啟用最新的生成式 AI 實驗性語義慣例 (Semantic Conventions)
        os.environ.setdefault(
            "OTEL_SEMCONV_STABILITY_OPT_IN", "gen_ai_latest_experimental"
        )

        # 獲取提交雜湊 (Commit SHA)，預設為 dev
        commit_sha = os.environ.get("COMMIT_SHA", "dev")
        # 配置 OpenTelemetry 資源屬性，標記服務命名空間與版本
        os.environ.setdefault(
            "OTEL_RESOURCE_ATTRIBUTES",
            f"service.namespace=pack-auto-insurance-agent,service.version={commit_sha}",
        )

        # 獲取遙測路徑，預設為 completions
        path = os.environ.get("GENAI_TELEMETRY_PATH", "completions")
        # 設定 OpenTelemetry 生成式 AI 上傳的基礎路徑 (GCS URL)
        os.environ.setdefault(
            "OTEL_INSTRUMENTATION_GENAI_UPLOAD_BASE_PATH",
            f"gs://{bucket}/{path}",
        )
    else:
        # 如果未滿足條件，則記錄日誌說明如何啟用遙測
        logging.info(
            "提示詞-回應日誌記錄已停用 (請設置 LOGS_BUCKET_NAME=gs://your-bucket 並將 OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=NO_CONTENT 以啟用)"
        )

    return bucket

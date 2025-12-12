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

import logging
import os

import google.auth
from google.adk.cli.adk_web_server import _setup_instrumentation_lib_if_installed
from google.adk.telemetry.google_cloud import get_gcp_exporters, get_gcp_resource
from google.adk.telemetry.setup import maybe_set_otel_providers


def setup_telemetry() -> str | None:
    """配置 OpenTelemetry 和 GenAI 遙測並上傳至 GCS。"""

    bucket = os.environ.get("LOGS_BUCKET_NAME")
    capture_content = os.environ.get(
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "false"
    )
    if bucket and capture_content != "false":
        logging.info(
            "提示-回應記錄已啟用 - 模式：NO_CONTENT (僅詮釋資料，無提示/回應)"
        )
        os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "NO_CONTENT"
        os.environ.setdefault("OTEL_INSTRUMENTATION_GENAI_UPLOAD_FORMAT", "jsonl")
        os.environ.setdefault("OTEL_INSTRUMENTATION_GENAI_COMPLETION_HOOK", "upload")
        os.environ.setdefault(
            "OTEL_SEMCONV_STABILITY_OPT_IN", "gen_ai_latest_experimental"
        )
        commit_sha = os.environ.get("COMMIT_SHA", "dev")
        os.environ.setdefault(
            "OTEL_RESOURCE_ATTRIBUTES",
            f"service.namespace=pack-adk-a2a-agent,service.version={commit_sha}",
        )
        path = os.environ.get("GENAI_TELEMETRY_PATH", "completions")
        os.environ.setdefault(
            "OTEL_INSTRUMENTATION_GENAI_UPLOAD_BASE_PATH",
            f"gs://{bucket}/{path}",
        )
    else:
        logging.info(
            "提示-回應記錄已停用 (設定 LOGS_BUCKET_NAME=gs://your-bucket 和 OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=NO_CONTENT 以啟用)"
        )

    # 設定 OpenTelemetry 導出器以用於 Cloud Trace 和 Cloud Logging
    credentials, project_id = google.auth.default()
    otel_hooks = get_gcp_exporters(
        enable_cloud_tracing=True,
        enable_cloud_metrics=False,
        enable_cloud_logging=True,
        google_auth=(credentials, project_id),
    )
    otel_resource = get_gcp_resource(project_id)
    maybe_set_otel_providers(
        otel_hooks_to_setup=[otel_hooks],
        otel_resource=otel_resource,
    )

    # 設定 GenAI SDK 儀器
    _setup_instrumentation_lib_if_installed()

    return bucket

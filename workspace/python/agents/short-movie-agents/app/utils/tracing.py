# 版權所有 2025 Google LLC
#
# 根據 Apache 許可證 2.0 版（「許可證」）授權；
# 除非遵守許可證，否則您不得使用此檔案。
# 您可以在以下網址獲得許可證副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據許可證分發的軟體
# 是按「原樣」分發的，不附帶任何形式的明示或暗示的保證或條件。
# 請參閱許可證以瞭解管理權限和限制的特定語言。

import json
import logging
from collections.abc import Sequence
from typing import Any

from google.cloud import logging as google_cloud_logging
from google.cloud import storage
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExportResult


class CloudTraceLoggingSpanExporter(CloudTraceSpanExporter):
    """
    擴充版的 CloudTraceSpanExporter，將追蹤點 (Span) 數據記錄到 Google Cloud Logging，
    並透過將大型屬性值存儲在 Google Cloud Storage (GCS) 來處理大型負載。

    此類別有助於繞過 Cloud Trace 對屬性值 256 字元的限制，
    利用 Cloud Logging（限制為 256KB）和 Cloud Storage 來處理更大的數據負載。
    """

    def __init__(
        self,
        logging_client: google_cloud_logging.Client | None = None,
        storage_client: storage.Client | None = None,
        bucket_name: str | None = None,
        debug: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        使用 Google Cloud 客戶端和配置初始化匯出器。

        :param logging_client: Google Cloud Logging 客戶端
        :param storage_client: Google Cloud Storage 客戶端
        :param bucket_name: 用於存儲大型負載的 GCS 儲存桶名稱
        :param debug: 啟用偵錯模式以獲取額外日誌
        :param kwargs: 傳遞給父類別的其他參數
        """
        super().__init__(**kwargs)
        self.debug = debug
        self.logging_client = logging_client or google_cloud_logging.Client(
            project=self.project_id
        )
        self.logger = self.logging_client.logger(__name__)
        self.storage_client = storage_client or storage.Client(
            project=self.project_id
        )
        self.bucket_name = (
            bucket_name or f"{self.project_id}-test-agent-logs-data"
        )
        self.bucket = self.storage_client.bucket(self.bucket_name)

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """
        將追蹤點匯出至 Google Cloud Logging 和 Cloud Trace。

        :param spans: 要匯出的追蹤點序列
        :return: 匯出操作的結果
        """
        for span in spans:
            span_context = span.get_span_context()
            trace_id = format(span_context.trace_id, "x")
            span_id = format(span_context.span_id, "x")
            span_dict = json.loads(span.to_json())

            span_dict["trace"] = f"projects/{self.project_id}/traces/{trace_id}"
            span_dict["span_id"] = span_id

            # 處理可能過大的屬性
            span_dict = self._process_large_attributes(
                span_dict=span_dict, span_id=span_id
            )

            if self.debug:
                print(span_dict)

            # 將追蹤點數據記錄到 Google Cloud Logging
            self.logger.log_struct(
                span_dict,
                labels={
                    "type": "agent_telemetry",
                    "service_name": "test-agent",
                },
                severity="INFO",
            )
        # 使用父類別方法將追蹤點匯出至 Google Cloud Trace
        return super().export(spans)

    def store_in_gcs(self, content: str, span_id: str) -> str:
        """
        將大型內容存儲在 Google Cloud Storage 中。

        :param content: 要存儲的內容
        :param span_id: 追蹤點的 ID
        :return: 存儲內容的 GCS URI
        """
        if not self.storage_client.bucket(self.bucket_name).exists():
            logging.warning(
                f"找不到儲存桶 {self.bucket_name}。無法在 GCS 中存儲追蹤屬性。"
            )
            return "找不到 GCS 儲存桶"

        blob_name = f"spans/{span_id}.json"
        blob = self.bucket.blob(blob_name)

        # 將內容以上傳字串形式存儲為 JSON 格式
        blob.upload_from_string(content, "application/json")
        return f"gs://{self.bucket_name}/{blob_name}"

    def _process_large_attributes(self, span_dict: dict, span_id: str) -> dict:
        """
        處理大型屬性值，如果超過 Google Cloud Logging 的大小限制，則將其存儲在 GCS 中。

        :param span_dict: 追蹤點數據字典
        :param span_id: 追蹤點 ID
        :return: 更新後的追蹤點字典
        """
        attributes = span_dict["attributes"]
        # 如果屬性編碼後超過 250 KB
        if len(json.dumps(attributes).encode()) > 255 * 1024:  # 250 KB
            # 將大型負載與其他屬性分離
            attributes_payload = dict(attributes.items())
            attributes_retain = dict(attributes.items())

            # 在 GCS 中存儲大型負載
            gcs_uri = self.store_in_gcs(json.dumps(attributes_payload), span_id)
            attributes_retain["uri_payload"] = gcs_uri
            attributes_retain["url_payload"] = (
                f"https://storage.mtls.cloud.google.com/"
                f"{self.bucket_name}/spans/{span_id}.json"
            )

            span_dict["attributes"] = attributes_retain
            logging.info(
                "追蹤負載長度超過 250 KB，正在將屬性存儲於 GCS 以避免大型日誌條目錯誤"
            )

        return span_dict

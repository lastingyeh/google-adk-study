import json
import logging
from collections.abc import Sequence
from typing import Any

import google.cloud.storage as storage
from google.cloud import logging as google_cloud_logging
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExportResult


class CloudTraceLoggingSpanExporter(CloudTraceSpanExporter):
    """
    自定義匯出器，將追蹤數據同時輸出至 Cloud Trace 與 Cloud Logging，並自動處理大型負載。
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
        初始化匯出器。

        :param logging_client: Google Cloud Logging 客戶端
        :param storage_client: Google Cloud Storage 客戶端
        :param bucket_name: 用於存儲大型負載的 GCS 儲存桶名稱
        :param debug: 啟用偵錯模式
        """
        super().__init__(**kwargs)
        self.debug = debug
        # 初始化日誌客戶端
        self.logging_client = logging_client or google_cloud_logging.Client(
            project=self.project_id
        )
        self.logger = self.logging_client.logger(__name__)
        # 初始化存儲客戶端
        self.storage_client = storage_client or storage.Client(project=self.project_id)
        # 設定儲存桶名稱，預設為 {project_id}-pack-customer-service-logs
        self.bucket_name = (
            bucket_name or f"{self.project_id}-pack-customer-service-logs"
        )
        self.bucket = self.storage_client.bucket(self.bucket_name)

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """
        將跨度匯出到 Google Cloud Logging 和 Cloud Trace。

        1. 遍歷所有跨度。
        2. 格式化追蹤與跨度 ID。
        3. 處理可能過大的屬性（轉存至 GCS）。
        4. 寫入結構化日誌。
        5. 調用父類別匯出至 Cloud Trace。
        """
        for span in spans:
            span_context = span.get_span_context()
            trace_id = format(span_context.trace_id, "x")
            span_id = format(span_context.span_id, "x")
            span_dict = json.loads(span.to_json())

            # 設定追蹤 ID 與跨度 ID 格式
            span_dict["trace"] = f"projects/{self.project_id}/traces/{trace_id}"
            span_dict["span_id"] = span_id

            # 處理大型屬性（防止超過 Logging 限制）
            span_dict = self._process_large_attributes(
                span_dict=span_dict, span_id=span_id
            )

            if self.debug:
                print(span_dict)

            # 將跨度數據以結構化形式記錄到 Google Cloud Logging
            self.logger.log_struct(
                span_dict,
                labels={
                    "type": "agent_telemetry",
                    "service_name": "pack-customer-service",
                },
                severity="INFO",
            )
        # 最終匯出至 Cloud Trace
        return super().export(spans)

    def store_in_gcs(self, content: str, span_id: str) -> str:
        """
        將內容上傳至 Google Cloud Storage。

        :param content: JSON 字串內容
        :param span_id: 跨度 ID，作為檔案名稱的一部分
        :return: GCS URI (gs://...)
        """
        if not self.storage_client.bucket(self.bucket_name).exists():
            logging.warning(
                f"找不到儲存桶 {self.bucket_name}。無法在 GCS 中存儲跨度屬性。"
            )
            return "找不到 GCS 儲存桶"

        # 定義路徑並上傳
        blob_name = f"spans/{span_id}.json"
        blob = self.bucket.blob(blob_name)

        blob.upload_from_string(content, "application/json")
        return f"gs://{self.bucket_name}/{blob_name}"

    def _process_large_attributes(self, span_dict: dict, span_id: str) -> dict:
        """
        檢查屬性大小，若超過 250KB 則將其移動至 GCS。

        :param span_dict: 包含屬性的原始跨度字典
        :param span_id: 跨度 ID
        :return: 更新後的跨度字典
        """
        attributes = span_dict["attributes"]
        # 判斷 JSON 編碼後的位元組大小
        if len(json.dumps(attributes).encode()) > 255 * 1024:  # 250 KB
            attributes_payload = dict(attributes.items())
            attributes_retain = dict(attributes.items())

            # 執行 GCS 儲存
            gcs_uri = self.store_in_gcs(json.dumps(attributes_payload), span_id)

            # 在日誌中保留連結而非原始大量數據
            attributes_retain["uri_payload"] = gcs_uri
            attributes_retain["url_payload"] = (
                f"https://storage.mtls.cloud.google.com/"
                f"{self.bucket_name}/spans/{span_id}.json"
            )

            span_dict["attributes"] = attributes_retain
            logging.info(
                "跨度負載長度超過 250 KB，正在將屬性存儲在 GCS 中以避免大型日誌項目錯誤"
            )

        return span_dict

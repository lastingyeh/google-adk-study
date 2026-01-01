import logging

import google.cloud.storage as storage
from google.api_core import exceptions


def create_bucket_if_not_exists(bucket_name: str, project: str, location: str) -> None:
    """如果指定的 GCS 儲存桶不存在，則建立新的儲存桶。

    Args:
        bucket_name: 要建立的儲存桶名稱 (可以是純名稱或 gs:// 開頭的 URI)
        project: Google Cloud 專案 ID
        location: 建立儲存桶的區域位置 (例如 us-central1)
    """
    storage_client = storage.Client(project=project)

    # 如果 bucket_name 以 gs:// 開頭，則移除前綴
    if bucket_name.startswith("gs://"):
        bucket_name = bucket_name[5:]
    try:
        # 嘗試獲取儲存桶，如果存在則不執行任何操作
        storage_client.get_bucket(bucket_name)
        logging.info(f"儲存桶 {bucket_name} 已存在")
    except exceptions.NotFound:
        # 如果儲存桶不存在 (NotFound)，則建立新儲存桶
        bucket = storage_client.create_bucket(
            bucket_name,
            location=location,
            project=project,
        )
        logging.info(f"已在 {bucket.location} 建立儲存桶 {bucket.name}")

import logging

import google.cloud.storage as storage
from google.api_core import exceptions


def create_bucket_if_not_exists(bucket_name: str, project: str, location: str) -> None:
    """如果儲存桶（Bucket）不存在，則建立一個新的。

    參數:
        bucket_name: 要建立的儲存桶名稱
        project: Google Cloud 專案 ID
        location: 建立儲存桶的地區（預設為 us-central1）
    """
    # 初始化 GCS 客戶端
    storage_client = storage.Client(project=project)

    # 處理以 gs:// 開頭的名稱
    if bucket_name.startswith("gs://"):
        bucket_name = bucket_name[5:]
    try:
        # 嘗試獲取儲存桶，若存在則不做任何事
        storage_client.get_bucket(bucket_name)
        logging.info(f"儲存桶 {bucket_name} 已存在")
    except exceptions.NotFound:
        # 若儲存桶不存在，則建立之
        bucket = storage_client.create_bucket(
            bucket_name,
            location=location,
            project=project,
        )
        logging.info(f"已在 {bucket.location} 建立儲存桶 {bucket.name}")

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

import logging

from google.api_core import exceptions
from google.cloud import storage


def create_bucket_if_not_exists(
    bucket_name: str, project: str, location: str
) -> None:
    """如果儲存桶尚不存在，則建立一個新的。

    參數：
        bucket_name (str): 要建立的儲存桶名稱（可包含 gs:// 前綴）
        project (str): Google Cloud 專案 ID
        location (str): 建立儲存桶的地理位置（例如 europe-west4）
    """
    # 初始化 Google Cloud Storage 客戶端
    storage_client = storage.Client(project=project)

    # 處理儲存桶名稱，移除 gs:// 前綴（如果有的話）
    if bucket_name.startswith("gs://"):
        bucket_name = bucket_name[5:]
    try:
        # 檢查儲存桶是否已存在
        storage_client.get_bucket(bucket_name)
        logging.info(f"儲存桶 {bucket_name} 已存在")
    except exceptions.NotFound:
        # 如果找不到，則在指定位置建立儲存桶
        bucket = storage_client.create_bucket(
            bucket_name,
            location=location,
            project=project,
        )
        logging.info(f"已在 {bucket.location} 建立儲存桶 {bucket.name}")

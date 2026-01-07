import json
import logging

from google.api_core import exceptions
from google.cloud import storage  # type: ignore


def load_metadata(gcs_uri: str):
    """
    從 GCS URI 載入 metadata。
    """
    # 檢查是否有提供 GCS URI
    if not gcs_uri:
        return {"error": "必須提供 GCS URI。"}
    try:
        # 建立 GCS 客戶端
        storage_client = storage.Client()
        # 解析 bucket 與 blob 名稱
        bucket_name, blob_name = gcs_uri.replace("gs://", "").split("/", 1)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        # 下載檔案內容
        content = blob.download_as_string()
        # 將每一行轉換為 JSON 物件
        metadata = [
            json.loads(line)
            for line in content.decode("utf-8").splitlines()
            if line.strip()
        ]
        return metadata
    except exceptions.NotFound:
        return {"error": f"在 GCS URI {gcs_uri} 找不到檔案。"}
    except Exception as e:
        return {"error": f"發生未預期的錯誤: {e}"}


def get_content_from_gcs_for_schema(gcs_uri: str) -> dict:
    """
    從 GCS 取得檔案內容以產生 schema。
    如果 URI 是目錄，則使用該目錄下找到的第一個檔案。

    參數:
        gcs_uri (str): 檔案或目錄的 GCS URI。

    回傳:
        dict: 包含 'status' 以及 'content' 或 'error_message' 的字典。
    """
    schema_gcs_uri = gcs_uri
    try:
        # 建立 GCS 客戶端
        storage_client = storage.Client()
        # 解析 bucket 與路徑
        gcs_path = gcs_uri.replace("gs://", "")
        path_parts = gcs_path.split("/", 1)
        bucket_name = path_parts[0]
        blob_prefix = path_parts[1] if len(path_parts) > 1 else ""
        bucket = storage_client.bucket(bucket_name)
        # 判斷是否為目錄
        is_directory = blob_prefix.endswith("/") or blob_prefix == ""

        if is_directory:
            # 列出目錄下的檔案
            blobs = list(
                storage_client.list_blobs(bucket, prefix=blob_prefix, max_results=10)
            )
            files_in_dir = [
                f"gs://{bucket_name}/{b.name}"
                for b in blobs
                if not b.name.endswith("/")
            ]

            if not files_in_dir:
                return {
                    "status": "error",
                    "error_message": f"在 GCS 目錄 {gcs_uri} 找不到任何檔案以產生 schema。",
                }
            schema_gcs_uri = files_in_dir[0]
            logging.info(f"偵測到目錄。將使用第一個檔案產生 schema: {schema_gcs_uri}")

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"存取 GCS URI {gcs_uri} 時發生錯誤: {e}",
        }

    try:
        # 下載檔案內容
        bucket_name, blob_name = schema_gcs_uri.replace("gs://", "").split("/", 1)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        content = blob.download_as_string().decode("utf-8")
        return {"status": "success", "content": content}
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"下載檔案 {schema_gcs_uri} 以產生 schema 時發生錯誤: {e}",
        }

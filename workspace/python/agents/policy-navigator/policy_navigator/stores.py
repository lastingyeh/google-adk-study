"""
File Search Store 管理實用工具。

提供用於建立、列出、檢索和管理 File Search Stores 的功能，
以便依部門或類型組織政策文件。
"""

import time
import mimetypes
from typing import Optional, Dict, Any
from google import genai
from google.genai import types
from loguru import logger

from policy_navigator.config import Config


class StoreManager:
    """File Search Stores 管理器。"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 Store Manager。

        Args:
            api_key: Google API 金鑰 (若未提供則使用 Config.GOOGLE_API_KEY)
        """
        self.api_key = api_key or Config.GOOGLE_API_KEY
        self.client = genai.Client(api_key=self.api_key)

    def create_policy_store(
        self, display_name: str, description: str = ""
    ) -> str:
        """
        為政策建立一個新的 File Search Store。

        Args:
            display_name: store 的易讀名稱
            description: store 用途的描述

        Returns:
            str: Store 名稱 (例如：'fileSearchStores/xxxxx')
        """
        try:
            logger.info(f"正在建立 File Search Store: {display_name}")

            store = self.client.file_search_stores.create(
                config={"display_name": display_name}
            )

            logger.info(f"✓ Store 已建立: {store.name}")
            return store.name

        except Exception as e:
            logger.error(f"建立 store 失敗: {str(e)}")
            raise

    def get_store_info(self, store_name: str) -> Dict[str, Any]:
        """
        取得 File Search Store 的資訊。

        Args:
            store_name: 完整的 store 名稱 (例如：'fileSearchStores/xxxxx')

        Returns:
            dict: Store 資訊
        """
        try:
            store = self.client.file_search_stores.get(name=store_name)
            return {
                "name": store.name,
                "display_name": getattr(store, "display_name", ""),
                "create_time": getattr(store, "create_time", ""),
                "update_time": getattr(store, "update_time", ""),
            }
        except Exception as e:
            logger.error(f"取得 store 資訊失敗: {str(e)}")
            raise

    def list_stores(self) -> list:
        """
        列出所有 File Search Stores。

        Returns:
            list: store 資訊字典的列表
        """
        try:
            stores = self.client.file_search_stores.list()
            store_list = []

            for store in stores:
                store_list.append(
                    {
                        "name": store.name,
                        "display_name": getattr(store, "display_name", ""),
                        "create_time": getattr(store, "create_time", ""),
                    }
                )

            logger.info(f"找到 {len(store_list)} 個 stores")
            return store_list

        except Exception as e:
            logger.error(f"列出 stores 失敗: {str(e)}")
            raise

    def get_store_by_display_name(self, display_name: str) -> Optional[str]:
        """
        依顯示名稱尋找 File Search Store。

        如果有多個 store 具有相同的顯示名稱，則回傳最近建立的 store。

        Args:
            display_name: 要尋找的 store 顯示名稱

        Returns:
            str: 完整的 store 名稱 (例如：'fileSearchStores/xxxxx')，如果找不到則為 None
        """
        try:
            stores = self.list_stores()
            matching_stores = [s for s in stores if s.get("display_name") == display_name]

            if not matching_stores:
                logger.warning(f"找不到顯示名稱為 '{display_name}' 的 Store")
                return None

            # 回傳最近建立的 store (依 create_time 判斷)
            most_recent = max(
                matching_stores,
                key=lambda s: s.get("create_time", "")
            )
            return most_recent.get("name")
        except Exception as e:
            logger.error(f"依顯示名稱尋找 store 失敗: {str(e)}")
            return None

    def delete_store(self, store_name: str, force: bool = False) -> bool:
        """
        刪除 File Search Store。

        Args:
            store_name: 完整的 store 名稱 (例如：'fileSearchStores/xxxxx')
            force: 如果為 True，即使 store 包含文件也會刪除

        Returns:
            bool: 如果刪除成功則為 True
        """
        try:
            logger.warning(f"正在刪除 File Search Store: {store_name}")
            config = None
            if force:
                config = types.DeleteFileSearchStoreConfig(force=True)
            self.client.file_search_stores.delete(name=store_name, config=config)
            logger.info("✓ Store 已刪除")
            return True
        except Exception as e:
            logger.error(f"刪除 store 失敗: {str(e)}")
            raise

    def list_documents(self, store_name: str) -> list:
        """
        列出 File Search Store 中的所有文件。

        Args:
            store_name: 完整的 store 名稱 (例如：'fileSearchStores/xxxxx')

        Returns:
            list: 文件資訊字典的列表
        """
        try:
            documents = self.client.file_search_stores.documents.list(
                parent=store_name
            )
            doc_list = []

            for doc in documents:
                doc_list.append(
                    {
                        "name": doc.name,
                        "display_name": getattr(doc, "display_name", ""),
                        "create_time": getattr(doc, "create_time", ""),
                        "update_time": getattr(doc, "update_time", ""),
                        "state": getattr(doc, "state", "UNKNOWN"),
                        "size_bytes": getattr(doc, "size_bytes", 0),
                    }
                )

            logger.info(f"在 store 中找到 {len(doc_list)} 份文件")
            return doc_list

        except Exception as e:
            logger.error(f"列出文件失敗: {str(e)}")
            raise

    def find_document_by_display_name(
        self, store_name: str, display_name: str
    ) -> Optional[str]:
        """
        依顯示名稱在 store 中尋找文件。

        如果找到，回傳第一個符合的文件名稱。

        Args:
            store_name: 完整的 store 名稱 (例如：'fileSearchStores/xxxxx')
            display_name: 要尋找的文件顯示名稱

        Returns:
            str: 完整的文件名稱 (例如：'fileSearchStores/xxx/documents/yyy')，如果找不到則為 None
        """
        try:
            documents = self.list_documents(store_name)
            matching_docs = [d for d in documents if d.get("display_name") == display_name]

            if not matching_docs:
                logger.debug(f"在 store 中找不到文件 '{display_name}'")
                return None

            # 回傳第一個符合的文件
            return matching_docs[0].get("name")

        except Exception as e:
            logger.error(f"依顯示名稱尋找文件失敗: {str(e)}")
            return None

    def delete_document(self, document_name: str, force: bool = True) -> bool:
        """
        從 File Search Store 中刪除文件。

        Args:
            document_name: 完整的文件名稱 (例如：'fileSearchStores/xxx/documents/yyy')
            force: 如果為 True，即使文件有 chunks 也會刪除

        Returns:
            bool: 如果刪除成功則為 True
        """
        try:
            logger.info(f"正在刪除文件: {document_name}")

            # 注意: force 在 API 中作為查詢參數傳遞
            self.client.file_search_stores.documents.delete(
                name=document_name, force=force
            )
            logger.info("✓ 文件已刪除")
            return True
        except Exception as e:
            logger.error(f"刪除文件失敗: {str(e)}")
            raise

    def upload_file_to_store(
        self,
        file_path: str,
        store_name: str,
        display_name: Optional[str] = None,
        metadata: Optional[list] = None,
    ) -> bool:
        """
        上傳檔案到 File Search Store。

        Args:
            file_path: 要上傳的檔案路徑
            store_name: 目標 File Search Store 名稱
            display_name: 文件的顯示名稱 (選填)
            metadata: 文件的自訂 metadata (選填)

        Returns:
            bool: 如果上傳成功則為 True
        """
        try:
            if display_name is None:
                display_name = file_path.split("/")[-1]

            logger.info(f"正在上傳 {file_path} 到 store...")

            # 偵測 mime type
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                # 為常見的政策檔案類型設定預設 mime types
                if file_path.endswith('.md'):
                    mime_type = 'text/markdown'
                elif file_path.endswith('.txt'):
                    mime_type = 'text/plain'
                elif file_path.endswith('.pdf'):
                    mime_type = 'application/pdf'
                else:
                    mime_type = 'text/plain'  # 預設備援

            with open(file_path, "rb") as f:
                config = {"display_name": display_name, "mime_type": mime_type}

                if metadata:
                    config["custom_metadata"] = metadata

                operation = (
                    self.client.file_search_stores.upload_to_file_search_store(
                        file=f,
                        file_search_store_name=store_name,
                        config=config
                    )
                )

            # 等待索引完成
            timeout = time.time() + Config.INDEXING_TIMEOUT_SECONDS
            while not operation.done:
                if time.time() > timeout:
                    logger.error("上傳逾時")
                    return False

                time.sleep(2)
                operation = self.client.operations.get(operation)

            logger.info(f"✓ {display_name} 已上傳並建立索引")
            return True

        except Exception as e:
            logger.error(f"上傳檔案失敗: {str(e)}")
            raise

    def upsert_file_to_store(
        self,
        file_path: str,
        store_name: str,
        display_name: Optional[str] = None,
        metadata: Optional[list] = None,
    ) -> bool:
        """
        以 upsert 語意 (更新插入) 上傳檔案到 File Search Store。

        如果 store 中已存在具有相同 display_name 的文件，
        它將在上傳新版本之前先被刪除。

        Args:
            file_path: 要上傳的檔案路徑
            store_name: 目標 File Search Store 名稱
            display_name: 文件的顯示名稱 (選填)
            metadata: 文件的自訂 metadata (選填)

        Returns:
            bool: 如果 upsert 成功則為 True
        """
        try:
            if display_name is None:
                display_name = file_path.split("/")[-1]

            logger.info(f"正在 Upserting (更新插入) {file_path} 到 store (upsert 模式)...")

            # 檢查是否已存在具有相同 display_name 的文件
            existing_doc = self.find_document_by_display_name(store_name, display_name)
            if existing_doc:
                logger.info(f"找到現有文件 '{display_name}'，正在刪除...")
                self.delete_document(existing_doc, force=True)
                # 給 store 一些時間處理刪除
                time.sleep(1)

            # 現在上傳新版本
            success = self.upload_file_to_store(
                file_path, store_name, display_name, metadata
            )

            if success:
                logger.info(f"✓ {display_name} upsert 成功")
            return success

        except Exception as e:
            logger.error(f"Upsert 檔案失敗: {str(e)}")
            raise

    def wait_for_operation(self, operation_name: str, timeout: int = 300) -> bool:
        """
        等待 File Search 操作完成。

        Args:
            operation_name: 操作名稱
            timeout: 逾時秒數

        Returns:
            bool: 如果操作成功完成則為 True
        """
        try:
            start_time = time.time()

            while time.time() - start_time < timeout:
                operation = self.client.operations.get(operation_name)

                if operation.done:
                    logger.info("✓ 操作完成")
                    return True

                time.sleep(2)

            logger.error("操作逾時")
            return False

        except Exception as e:
            logger.error(f"等待操作失敗: {str(e)}")
            raise


# 便利函式 (Convenience functions)
_store_manager: Optional[StoreManager] = None


def _get_manager() -> StoreManager:
    """取得或建立 StoreManager 實例。"""
    global _store_manager
    if _store_manager is None:
        _store_manager = StoreManager()
    return _store_manager


def create_policy_store(display_name: str, description: str = "") -> str:
    """建立新的 File Search Store。"""
    return _get_manager().create_policy_store(display_name, description)


def get_store_info(store_name: str) -> Dict[str, Any]:
    """取得 store 資訊。"""
    return _get_manager().get_store_info(store_name)


def list_stores() -> list:
    """列出所有 File Search Stores。"""
    return _get_manager().list_stores()


def delete_store(store_name: str) -> bool:
    """刪除 File Search Store。"""
    return _get_manager().delete_store(store_name)


def upload_file_to_store(
    file_path: str,
    store_name: str,
    display_name: Optional[str] = None,
    metadata: Optional[list] = None,
) -> bool:
    """上傳檔案到 store。"""
    return _get_manager().upload_file_to_store(
        file_path, store_name, display_name, metadata
    )


def upsert_file_to_store(
    file_path: str,
    store_name: str,
    display_name: Optional[str] = None,
    metadata: Optional[list] = None,
) -> bool:
    """以 upsert 語意上傳檔案到 store (若存在則取代)。"""
    return _get_manager().upsert_file_to_store(
        file_path, store_name, display_name, metadata
    )


def list_documents(store_name: str) -> list:
    """列出 store 中的所有文件。"""
    return _get_manager().list_documents(store_name)


def find_document_by_display_name(store_name: str, display_name: str) -> Optional[str]:
    """依顯示名稱在 store 中尋找文件。"""
    return _get_manager().find_document_by_display_name(store_name, display_name)


def delete_document(document_name: str, force: bool = True) -> bool:
    """從 store 中刪除文件。"""
    return _get_manager().delete_document(document_name, force)

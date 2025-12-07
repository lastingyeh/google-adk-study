"""
Policy Navigator 工具和實用程式的單元測試。

測試策略管理工具的核心功能，無需即時 API。
"""

import pytest
from unittest.mock import Mock, patch
from policy_navigator.metadata import MetadataSchema, PolicyDepartment, PolicyType
from policy_navigator.stores import StoreManager
from policy_navigator.utils import (
    get_sample_policies_dir,
    get_store_name_for_policy,
    format_response,
)


class TestMetadataSchema:
    """元數據模式生成測試。"""

    def test_get_schema(self):
        """測試模式定義。"""
        schema = MetadataSchema.get_schema()
        assert isinstance(schema, dict)
        assert "department" in schema
        assert "policy_type" in schema
        assert "effective_date" in schema
        assert schema["department"] == "string"
        assert schema["version"] == "numeric"

    def test_create_metadata(self):
        """測試元數據建立。"""
        metadata = MetadataSchema.create_metadata(
            department="HR",
            policy_type="handbook",
            jurisdiction="US",
            version=2,
        )

        assert isinstance(metadata, list)
        assert len(metadata) > 0

        # 檢查特定欄位
        dept_meta = next((m for m in metadata if m["key"] == "department"), None)
        assert dept_meta is not None
        assert dept_meta["string_value"] == "HR"

        version_meta = next((m for m in metadata if m["key"] == "version"), None)
        assert version_meta is not None
        assert version_meta["numeric_value"] == 2

    def test_hr_metadata(self):
        """測試 HR 元數據預設值。"""
        metadata = MetadataSchema.hr_metadata()
        assert isinstance(metadata, list)

        dept_meta = next((m for m in metadata if m["key"] == "department"), None)
        assert dept_meta["string_value"] == "HR"

    def test_it_metadata(self):
        """測試 IT 元數據預設值。"""
        metadata = MetadataSchema.it_metadata()
        assert isinstance(metadata, list)

        dept_meta = next((m for m in metadata if m["key"] == "department"), None)
        assert dept_meta["string_value"] == "IT"

    def test_code_of_conduct_metadata(self):
        """測試行為準則元數據預設值。"""
        metadata = MetadataSchema.code_of_conduct_metadata()
        assert isinstance(metadata, list)

        type_meta = next((m for m in metadata if m["key"] == "policy_type"), None)
        assert type_meta["string_value"] == "code_of_conduct"

    def test_build_metadata_filter_single(self):
        """測試建立單一元數據過濾器。"""
        filter_str = MetadataSchema.build_metadata_filter(department="HR")
        assert "department=" in filter_str
        assert "HR" in filter_str

    def test_build_metadata_filter_multiple(self):
        """測試建立多個元數據過濾器。"""
        filter_str = MetadataSchema.build_metadata_filter(
            department="HR",
            policy_type="handbook",
            sensitivity="internal",
        )

        assert "department=" in filter_str
        assert "policy_type=" in filter_str
        assert "sensitivity=" in filter_str
        assert " AND " in filter_str

    def test_build_metadata_filter_empty(self):
        """測試建立空白元數據過濾器。"""
        filter_str = MetadataSchema.build_metadata_filter()
        assert filter_str == ""


class TestUtils:
    """實用程式功能測試。"""

    def test_get_sample_policies_dir(self):
        """測試取得範例策略目錄。"""
        dir_path = get_sample_policies_dir()
        assert isinstance(dir_path, str)
        assert "sample_policies" in dir_path

    def test_get_store_name_for_policy_hr(self):
        """測試 HR 策略的儲存區名稱偵測。"""
        store = get_store_name_for_policy("hr_handbook.md")
        assert "hr" in store.lower()

    def test_get_store_name_for_policy_it(self):
        """測試 IT 策略的儲存區名稱偵測。"""
        store = get_store_name_for_policy("it_security_policy.pdf")
        assert "it" in store.lower()

    def test_get_store_name_for_policy_remote(self):
        """測試遠端工作策略的儲存區名稱偵測。"""
        store = get_store_name_for_policy("remote_work_policy.md")
        assert "hr" in store.lower()

    def test_get_store_name_for_policy_conduct(self):
        """測試行為準則的儲存區名稱偵測。"""
        store = get_store_name_for_policy("code_of_conduct.md")
        assert "safety" in store.lower() or "general" in store.lower()

    def test_format_response_success(self):
        """測試格式化成功回應。"""
        response = format_response("success", "Operation completed", {"count": 5})
        assert "✓" in response
        assert "Operation completed" in response
        assert "count" in response

    def test_format_response_error(self):
        """測試格式化錯誤回應。"""
        response = format_response("error", "Operation failed", {"reason": "Invalid input"})
        assert "✗" in response
        assert "Operation failed" in response

    def test_format_response_warning(self):
        """測試格式化警告回應。"""
        response = format_response("warning", "Check this", {"info": "details"})
        assert "⚠" in response
        assert "Check this" in response


class TestEnums:
    """列舉定義測試。"""

    def test_policy_department_enum(self):
        """測試 PolicyDepartment 列舉。"""
        assert PolicyDepartment.HR.value == "HR"
        assert PolicyDepartment.IT.value == "IT"
        assert PolicyDepartment.LEGAL.value == "Legal"
        assert PolicyDepartment.SAFETY.value == "Safety"

    def test_policy_type_enum(self):
        """測試 PolicyType 列舉。"""
        assert PolicyType.HANDBOOK.value == "handbook"
        assert PolicyType.PROCEDURE.value == "procedure"
        assert PolicyType.CODE_OF_CONDUCT.value == "code_of_conduct"


class TestConfig:
    """配置測試。"""

    def test_config_has_api_key_setting(self):
        """測試配置是否有 API 金鑰設定。"""
        from policy_navigator.config import Config

        assert hasattr(Config, "GOOGLE_API_KEY")
        assert hasattr(Config, "DEFAULT_MODEL")
        assert hasattr(Config, "LOG_LEVEL")

    def test_config_get_store_names(self):
        """測試取得所有儲存區名稱。"""
        from policy_navigator.config import Config

        stores = Config.get_store_names()
        assert isinstance(stores, dict)
        assert "hr" in stores
        assert "it" in stores
        assert "legal" in stores
        assert "safety" in stores


# 整合測試 (標記為 integration，以便在沒有 API 金鑰的 CI 中跳過)


@pytest.mark.integration
class TestStoreManagerIntegration:
    """StoreManager 的整合測試 (需要 API 金鑰)。"""

    @pytest.fixture
    def store_manager(self):
        """建立用於測試的 StoreManager。"""
        return StoreManager()

    def test_list_stores_returns_list(self, store_manager):
        """測試列出儲存區返回列表。"""
        stores = store_manager.list_stores()
        assert isinstance(stores, list)

    def test_list_documents_mock(self, store_manager):
        """測試使用模擬 API 的 list_documents 方法。"""
        with patch.object(store_manager.client.file_search_stores.documents, 'list') as mock_list:
            # 模擬回應
            mock_doc = Mock()
            mock_doc.name = 'fileSearchStores/123/documents/abc'
            mock_doc.display_name = 'test_document'
            mock_doc.create_time = '2025-01-01T00:00:00Z'
            mock_doc.update_time = '2025-01-01T00:00:00Z'
            mock_doc.state = 'ACTIVE'
            mock_doc.size_bytes = 1024

            mock_list.return_value = [mock_doc]

            docs = store_manager.list_documents('fileSearchStores/123')
            assert isinstance(docs, list)
            assert len(docs) == 1
            assert docs[0]['display_name'] == 'test_document'

    def test_find_document_by_display_name_mock(self, store_manager):
        """測試使用模擬 API 的 find_document_by_display_name。"""
        with patch.object(store_manager, 'list_documents') as mock_list:
            mock_list.return_value = [
                {
                    'name': 'fileSearchStores/123/documents/abc',
                    'display_name': 'policy1.md',
                    'create_time': '2025-01-01T00:00:00Z',
                }
            ]

            result = store_manager.find_document_by_display_name('fileSearchStores/123', 'policy1.md')
            assert result == 'fileSearchStores/123/documents/abc'

    def test_find_document_by_display_name_not_found(self, store_manager):
        """測試當文件未找到時的 find_document_by_display_name。"""
        with patch.object(store_manager, 'list_documents') as mock_list:
            mock_list.return_value = []

            result = store_manager.find_document_by_display_name('fileSearchStores/123', 'nonexistent.md')
            assert result is None

    def test_delete_document_mock(self, store_manager):
        """測試使用模擬 API 的 delete_document 方法。"""
        with patch.object(store_manager.client.file_search_stores.documents, 'delete') as mock_delete:
            mock_delete.return_value = None

            result = store_manager.delete_document('fileSearchStores/123/documents/abc')
            assert result is True
            mock_delete.assert_called_once()

    def test_upsert_file_to_store_new_document(self, store_manager):
        """測試當文件不存在時的 upsert (新上傳)。"""
        with patch.object(store_manager, 'find_document_by_display_name') as mock_find, \
             patch.object(store_manager, 'upload_file_to_store') as mock_upload:

            # 文件不存在
            mock_find.return_value = None
            mock_upload.return_value = True

            # 建立暫時測試檔案
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write('test content')
                temp_file = f.name

            try:
                result = store_manager.upsert_file_to_store(
                    temp_file, 'fileSearchStores/123', 'test.md'
                )

                # 應該只呼叫上傳，而不呼叫刪除
                assert result is True
                mock_find.assert_called_once()
                mock_upload.assert_called_once()
            finally:
                import os
                os.unlink(temp_file)

    def test_upsert_file_to_store_existing_document(self, store_manager):
        """測試當文件存在時的 upsert (替換)。"""
        with patch.object(store_manager, 'find_document_by_display_name') as mock_find, \
             patch.object(store_manager, 'delete_document') as mock_delete, \
             patch.object(store_manager, 'upload_file_to_store') as mock_upload, \
             patch('time.sleep'):  # 模擬睡眠以加速測試

            # 文件存在
            mock_find.return_value = 'fileSearchStores/123/documents/old'
            mock_delete.return_value = True
            mock_upload.return_value = True

            # 建立暫時測試檔案
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write('updated content')
                temp_file = f.name

            try:
                result = store_manager.upsert_file_to_store(
                    temp_file, 'fileSearchStores/123', 'test.md'
                )

                # 應該呼叫尋找、刪除和上傳
                assert result is True
                mock_find.assert_called_once()
                mock_delete.assert_called_once()
                mock_upload.assert_called_once()
            finally:
                import os
                os.unlink(temp_file)


@pytest.mark.integration
class TestPolicyToolsIntegration:
    """PolicyTools 的整合測試 (需要 API 金鑰)。"""

    @pytest.fixture
    def policy_tools(self):
        """建立用於測試的 PolicyTools。"""
        from policy_navigator.tools import PolicyTools

        return PolicyTools()

    def test_search_policies_returns_dict(self, policy_tools):
        """測試搜尋返回格式正確的字典。"""
        # 這需要在測試環境中填入儲存區
        pass

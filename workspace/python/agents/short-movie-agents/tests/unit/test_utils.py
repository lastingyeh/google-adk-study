"""
工具函式測試

測試 utils 模組中所有工具函式的功能正確性。
"""

import os
from unittest.mock import Mock, patch, MagicMock
import pytest


class TestLoadPromptFromFile:
    """測試 load_prompt_from_file 函式。"""

    def test_function_exists(self):
        """測試函式存在。"""
        from app.utils.utils import load_prompt_from_file

        assert callable(load_prompt_from_file)

    def test_load_valid_prompt_file(self):
        """測試載入有效的提示詞檔案。"""
        from app.utils.utils import load_prompt_from_file

        # 測試載入實際存在的檔案
        instruction = load_prompt_from_file("director_agent.txt")

        assert instruction is not None
        assert isinstance(instruction, str)
        assert len(instruction) > 0

    def test_load_story_agent_prompt(self):
        """測試載入故事代理提示詞。"""
        from app.utils.utils import load_prompt_from_file

        instruction = load_prompt_from_file("story_agent.txt")

        assert instruction is not None
        assert len(instruction) > 0

    def test_load_screenplay_agent_prompt(self):
        """測試載入劇本代理提示詞。"""
        from app.utils.utils import load_prompt_from_file

        instruction = load_prompt_from_file("screenplay_agent.txt")

        assert instruction is not None
        assert len(instruction) > 0

    def test_load_nonexistent_file_uses_default(self):
        """測試載入不存在的檔案使用預設值。"""
        from app.utils.utils import load_prompt_from_file

        default = "Default instruction for testing"
        instruction = load_prompt_from_file(
            "nonexistent_file.txt", default_instruction=default
        )

        assert instruction == default

    def test_default_instruction_parameter(self):
        """測試預設指令參數。"""
        from app.utils.utils import load_prompt_from_file

        custom_default = "Custom default instruction"
        instruction = load_prompt_from_file(
            "definitely_not_a_file.txt", default_instruction=custom_default
        )

        assert instruction == custom_default


class TestCreateBucketIfNotExists:
    """測試 create_bucket_if_not_exists 函式。"""

    def test_function_exists(self):
        """測試函式存在。"""
        from app.utils.gcs import create_bucket_if_not_exists

        assert callable(create_bucket_if_not_exists)

    @patch("app.utils.gcs.storage.Client")
    def test_bucket_already_exists(self, mock_client):
        """測試儲存桶已存在的情況。"""
        from app.utils.gcs import create_bucket_if_not_exists

        # Mock storage client
        mock_storage_client = Mock()
        mock_client.return_value = mock_storage_client
        mock_storage_client.get_bucket.return_value = Mock()

        # 執行函式
        create_bucket_if_not_exists(
            bucket_name="test-bucket", project="test-project", location="us-central1"
        )

        # 驗證
        mock_storage_client.get_bucket.assert_called_once_with("test-bucket")
        mock_storage_client.create_bucket.assert_not_called()

    @patch("app.utils.gcs.storage.Client")
    def test_bucket_creation(self, mock_client):
        """測試建立新儲存桶。"""
        from app.utils.gcs import create_bucket_if_not_exists
        from google.api_core import exceptions

        # Mock storage client
        mock_storage_client = Mock()
        mock_client.return_value = mock_storage_client
        mock_storage_client.get_bucket.side_effect = exceptions.NotFound("Not found")
        mock_bucket = Mock()
        mock_bucket.name = "test-bucket"
        mock_bucket.location = "us-central1"
        mock_storage_client.create_bucket.return_value = mock_bucket

        # 執行函式
        create_bucket_if_not_exists(
            bucket_name="test-bucket", project="test-project", location="us-central1"
        )

        # 驗證
        mock_storage_client.get_bucket.assert_called_once_with("test-bucket")
        mock_storage_client.create_bucket.assert_called_once()

    @patch("app.utils.gcs.storage.Client")
    def test_bucket_name_with_gs_prefix(self, mock_client):
        """測試處理包含 gs:// 前綴的儲存桶名稱。"""
        from app.utils.gcs import create_bucket_if_not_exists

        # Mock storage client
        mock_storage_client = Mock()
        mock_client.return_value = mock_storage_client
        mock_storage_client.get_bucket.return_value = Mock()

        # 執行函式
        create_bucket_if_not_exists(
            bucket_name="gs://test-bucket",
            project="test-project",
            location="us-central1",
        )

        # 驗證 - 應該移除 gs:// 前綴
        mock_storage_client.get_bucket.assert_called_once_with("test-bucket")


class TestCloudTraceLoggingSpanExporter:
    """測試 CloudTraceLoggingSpanExporter 類別。"""

    def test_class_exists(self):
        """測試類別存在。"""
        from app.utils.tracing import CloudTraceLoggingSpanExporter

        assert CloudTraceLoggingSpanExporter is not None

    @patch("app.utils.tracing.google_cloud_logging.Client")
    @patch("app.utils.tracing.storage.Client")
    def test_exporter_initialization(self, mock_storage_client, mock_logging_client):
        """測試匯出器初始化。"""
        from app.utils.tracing import CloudTraceLoggingSpanExporter

        # Mock clients
        mock_logging = Mock()
        mock_logging_client.return_value = mock_logging
        mock_storage = Mock()
        mock_storage_client.return_value = mock_storage

        # 建立匯出器實例
        exporter = CloudTraceLoggingSpanExporter(
            logging_client=mock_logging,
            storage_client=mock_storage,
            bucket_name="test-bucket",
        )

        assert exporter is not None
        assert exporter.bucket_name == "test-bucket"

    @patch("app.utils.tracing.google_cloud_logging.Client")
    @patch("app.utils.tracing.storage.Client")
    def test_exporter_with_debug_mode(self, mock_storage_client, mock_logging_client):
        """測試匯出器偵錯模式。"""
        from app.utils.tracing import CloudTraceLoggingSpanExporter

        # Mock clients
        mock_logging = Mock()
        mock_logging_client.return_value = mock_logging
        mock_storage = Mock()
        mock_storage_client.return_value = mock_storage

        # 建立匯出器實例（偵錯模式）
        exporter = CloudTraceLoggingSpanExporter(
            logging_client=mock_logging,
            storage_client=mock_storage,
            debug=True,
        )

        assert exporter.debug is True

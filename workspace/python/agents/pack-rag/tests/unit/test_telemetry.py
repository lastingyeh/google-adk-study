"""
Telemetry 遙測功能測試
"""

import os
from unittest.mock import patch


class TestSetupTelemetry:
    """
    測試 setup_telemetry 函式。

    重點說明:
    1. 驗證遙測啟用條件 (LOGS_BUCKET_NAME)
    2. 驗證環境變數設定 (OpenTelemetry 相關)
    3. 驗證隱私安全 (強制 NO_CONTENT 模式)
    """

    def test_setup_telemetry_exists(self):
        """
        測試 setup_telemetry 函式存在。

        驗證點:
        1. 函式存在且可呼叫
        """
        from rag.app_utils.telemetry import setup_telemetry

        assert setup_telemetry is not None
        assert callable(setup_telemetry)

    @patch.dict(os.environ, {}, clear=True)
    def test_setup_telemetry_without_bucket(self):
        """
        測試沒有設定 LOGS_BUCKET_NAME 時的行為。

        驗證點:
        1. 若無 bucket 設定，則不啟用遙測
        """
        from rag.app_utils.telemetry import setup_telemetry

        result = setup_telemetry()
        assert result is None

    @patch.dict(os.environ, {"LOGS_BUCKET_NAME": "test-bucket"}, clear=True)
    def test_setup_telemetry_with_bucket_but_capture_disabled(self):
        """測試有 bucket 但 capture_content 未啟用。"""
        from rag.app_utils.telemetry import setup_telemetry

        result = setup_telemetry()
        # capture_content 預設為 false，所以不應設定遙測
        assert result is None

    @patch.dict(
        os.environ,
        {
            "LOGS_BUCKET_NAME": "test-bucket",
            "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "NO_CONTENT",
        },
        clear=True,
    )
    def test_setup_telemetry_with_no_content_mode(self):
        """測試 NO_CONTENT 模式的遙測設定。"""
        from rag.app_utils.telemetry import setup_telemetry

        result = setup_telemetry()

        # 應該回傳 bucket 名稱
        assert result == "test-bucket"

        # 驗證環境變數已被設定
        assert (
            os.environ.get("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT")
            == "NO_CONTENT"
        )

    @patch.dict(
        os.environ,
        {
            "LOGS_BUCKET_NAME": "test-bucket",
            "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "NO_CONTENT",
        },
        clear=True,
    )
    def test_setup_telemetry_sets_default_values(self):
        """測試遙測設定的預設值。"""
        from rag.app_utils.telemetry import setup_telemetry

        setup_telemetry()

        # 檢查預設環境變數
        assert os.environ.get("OTEL_INSTRUMENTATION_GENAI_UPLOAD_FORMAT") == "jsonl"
        assert os.environ.get("OTEL_INSTRUMENTATION_GENAI_COMPLETION_HOOK") == "upload"
        assert (
            os.environ.get("OTEL_SEMCONV_STABILITY_OPT_IN")
            == "gen_ai_latest_experimental"
        )

    @patch.dict(
        os.environ,
        {
            "LOGS_BUCKET_NAME": "test-bucket",
            "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "NO_CONTENT",
        },
        clear=True,
    )
    def test_setup_telemetry_resource_attributes(self):
        """測試資源屬性設定。"""
        from rag.app_utils.telemetry import setup_telemetry

        setup_telemetry()

        resource_attrs = os.environ.get("OTEL_RESOURCE_ATTRIBUTES")
        assert resource_attrs is not None
        assert "service.namespace=pack-rag" in resource_attrs
        assert "service.version=" in resource_attrs

    @patch.dict(
        os.environ,
        {
            "LOGS_BUCKET_NAME": "test-bucket",
            "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "NO_CONTENT",
            "COMMIT_SHA": "abc123def",
        },
        clear=True,
    )
    def test_setup_telemetry_with_commit_sha(self):
        """測試使用 COMMIT_SHA 設定版本。"""
        from rag.app_utils.telemetry import setup_telemetry

        setup_telemetry()

        resource_attrs = os.environ.get("OTEL_RESOURCE_ATTRIBUTES")
        assert resource_attrs is not None
        assert "service.version=abc123def" in resource_attrs

    @patch.dict(
        os.environ,
        {
            "LOGS_BUCKET_NAME": "test-bucket",
            "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "NO_CONTENT",
        },
        clear=True,
    )
    def test_setup_telemetry_upload_base_path(self):
        """測試上傳基礎路徑設定。"""
        from rag.app_utils.telemetry import setup_telemetry

        setup_telemetry()

        base_path = os.environ.get("OTEL_INSTRUMENTATION_GENAI_UPLOAD_BASE_PATH")
        assert base_path is not None
        assert base_path.startswith("gs://test-bucket/")
        assert "completions" in base_path

    @patch.dict(
        os.environ,
        {
            "LOGS_BUCKET_NAME": "test-bucket",
            "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "NO_CONTENT",
            "GENAI_TELEMETRY_PATH": "custom-path",
        },
        clear=True,
    )
    def test_setup_telemetry_custom_path(self):
        """測試自訂遙測路徑。"""
        from rag.app_utils.telemetry import setup_telemetry

        setup_telemetry()

        base_path = os.environ.get("OTEL_INSTRUMENTATION_GENAI_UPLOAD_BASE_PATH")
        assert base_path == "gs://test-bucket/custom-path"

    @patch.dict(
        os.environ,
        {
            "LOGS_BUCKET_NAME": "test-bucket",
            "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "NO_CONTENT",
            "OTEL_INSTRUMENTATION_GENAI_UPLOAD_FORMAT": "json",  # 已存在的值
        },
        clear=True,
    )
    def test_setup_telemetry_preserves_existing_env_vars(self):
        """測試不覆蓋已存在的環境變數。"""
        from rag.app_utils.telemetry import setup_telemetry

        setup_telemetry()

        # setdefault 不應該覆蓋已存在的值
        assert os.environ.get("OTEL_INSTRUMENTATION_GENAI_UPLOAD_FORMAT") == "json"


class TestTelemetryConfiguration:
    """測試遙測配置的整體邏輯。"""

    def test_telemetry_forces_no_content_mode(self):
        """測試遙測強制使用 NO_CONTENT 模式以保護隱私。"""
        # 這是重要的安全特性，確保不會記錄敏感的提示/回應內容
        from rag.app_utils.telemetry import setup_telemetry

        with patch.dict(
            os.environ,
            {
                "LOGS_BUCKET_NAME": "test-bucket",
                "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "true",  # 嘗試啟用內容記錄
            },
            clear=True,
        ):
            setup_telemetry()

            # 應該被強制設定為 NO_CONTENT
            assert (
                os.environ.get("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT")
                == "NO_CONTENT"
            )

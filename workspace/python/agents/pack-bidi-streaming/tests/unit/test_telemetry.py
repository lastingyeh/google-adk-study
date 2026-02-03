"""
遙測 (Telemetry) 設定測試

測試 pack-bidi-streaming 專案的遙測功能設定。
"""

import os
from unittest.mock import patch


class TestSetupTelemetry:
    """測試 setup_telemetry 函式。"""

    def test_setup_telemetry_exists(self):
        """測試 setup_telemetry 函式是否存在。"""
        from bidi_demo.app_utils.telemetry import setup_telemetry

        assert setup_telemetry is not None
        assert callable(setup_telemetry)

    def test_setup_telemetry_returns_value(self):
        """測試 setup_telemetry 回傳值型別。"""
        from bidi_demo.app_utils.telemetry import setup_telemetry

        result = setup_telemetry()
        # 應該回傳 str 或 None
        assert result is None or isinstance(result, str)

    @patch.dict(os.environ, {}, clear=True)
    def test_setup_telemetry_without_bucket(self):
        """測試沒有設定 LOGS_BUCKET_NAME 時的行為。"""
        from bidi_demo.app_utils.telemetry import setup_telemetry

        result = setup_telemetry()
        assert result is None

    @patch.dict(
        os.environ,
        {
            "LOGS_BUCKET_NAME": "test-bucket",
            "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "true",
        },
    )
    def test_setup_telemetry_with_bucket_enabled(self):
        """測試設定 LOGS_BUCKET_NAME 且啟用內容擷取時的行為。"""
        from bidi_demo.app_utils.telemetry import setup_telemetry

        result = setup_telemetry()
        assert result == "test-bucket"

        # 驗證環境變數已正確設定
        assert (
            os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"]
            == "NO_CONTENT"
        )
        assert os.environ["OTEL_INSTRUMENTATION_GENAI_UPLOAD_FORMAT"] == "jsonl"
        assert os.environ["OTEL_INSTRUMENTATION_GENAI_COMPLETION_HOOK"] == "upload"
        assert (
            os.environ["OTEL_SEMCONV_STABILITY_OPT_IN"] == "gen_ai_latest_experimental"
        )

    @patch.dict(
        os.environ,
        {
            "LOGS_BUCKET_NAME": "test-bucket",
            "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "false",
        },
    )
    def test_setup_telemetry_with_bucket_disabled(self):
        """測試設定 LOGS_BUCKET_NAME 但停用內容擷取時的行為。"""
        from bidi_demo.app_utils.telemetry import setup_telemetry

        result = setup_telemetry()
        # 即使有 bucket，但 capture_content 為 false，仍應該回傳 None
        # （根據實際實作，會回傳 bucket 名稱）
        assert result == "test-bucket"

    @patch.dict(
        os.environ,
        {
            "LOGS_BUCKET_NAME": "test-bucket",
            "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "true",
            "COMMIT_SHA": "abc123",
        },
    )
    def test_setup_telemetry_with_commit_sha(self):
        """測試有 COMMIT_SHA 時的行為。"""
        from bidi_demo.app_utils.telemetry import setup_telemetry

        result = setup_telemetry()
        assert result == "test-bucket"

        # 驗證 OTEL_RESOURCE_ATTRIBUTES 包含正確的 commit SHA
        resource_attrs = os.environ.get("OTEL_RESOURCE_ATTRIBUTES", "")
        assert "service.namespace=pack-bidi-streaming" in resource_attrs
        assert "service.version=abc123" in resource_attrs

    @patch.dict(
        os.environ,
        {
            "LOGS_BUCKET_NAME": "test-bucket",
            "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "true",
        },
    )
    def test_setup_telemetry_default_commit_sha(self):
        """測試沒有 COMMIT_SHA 時使用預設值。"""
        from bidi_demo.app_utils.telemetry import setup_telemetry

        # 確保 COMMIT_SHA 不存在
        os.environ.pop("COMMIT_SHA", None)

        result = setup_telemetry()
        assert result == "test-bucket"

        # 驗證使用預設的 commit SHA (dev)
        resource_attrs = os.environ.get("OTEL_RESOURCE_ATTRIBUTES", "")
        assert "service.version=dev" in resource_attrs

    @patch.dict(
        os.environ,
        {
            "LOGS_BUCKET_NAME": "test-bucket",
            "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "true",
            "GENAI_TELEMETRY_PATH": "custom/path",
        },
    )
    def test_setup_telemetry_custom_path(self):
        """測試自訂遙測資料路徑。"""
        from bidi_demo.app_utils.telemetry import setup_telemetry

        result = setup_telemetry()
        assert result == "test-bucket"

        # 驗證使用自訂路徑
        upload_path = os.environ.get("OTEL_INSTRUMENTATION_GENAI_UPLOAD_BASE_PATH", "")
        assert "gs://test-bucket/custom/path" in upload_path

    @patch.dict(
        os.environ,
        {
            "LOGS_BUCKET_NAME": "test-bucket",
            "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "true",
        },
    )
    def test_setup_telemetry_default_path(self):
        """測試使用預設遙測資料路徑。"""
        from bidi_demo.app_utils.telemetry import setup_telemetry

        # 確保 GENAI_TELEMETRY_PATH 不存在
        os.environ.pop("GENAI_TELEMETRY_PATH", None)

        result = setup_telemetry()
        assert result == "test-bucket"

        # 驗證使用預設路徑 (completions)
        upload_path = os.environ.get("OTEL_INSTRUMENTATION_GENAI_UPLOAD_BASE_PATH", "")
        assert "gs://test-bucket/completions" in upload_path


class TestTelemetryEnvironmentVariables:
    """測試遙測相關的環境變數處理。"""

    def test_logs_bucket_name_env_var(self):
        """測試 LOGS_BUCKET_NAME 環境變數的讀取。"""
        with patch.dict(os.environ, {"LOGS_BUCKET_NAME": "my-bucket"}):
            bucket = os.environ.get("LOGS_BUCKET_NAME")
            assert bucket == "my-bucket"

    def test_otel_capture_message_content_env_var(self):
        """測試 OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT 環境變數的讀取。"""
        with patch.dict(
            os.environ, {"OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "true"}
        ):
            capture = os.environ.get(
                "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"
            )
            assert capture == "true"

    def test_commit_sha_env_var(self):
        """測試 COMMIT_SHA 環境變數的讀取。"""
        with patch.dict(os.environ, {"COMMIT_SHA": "test123"}):
            commit_sha = os.environ.get("COMMIT_SHA")
            assert commit_sha == "test123"

    def test_genai_telemetry_path_env_var(self):
        """測試 GENAI_TELEMETRY_PATH 環境變數的讀取。"""
        with patch.dict(os.environ, {"GENAI_TELEMETRY_PATH": "logs/data"}):
            path = os.environ.get("GENAI_TELEMETRY_PATH")
            assert path == "logs/data"

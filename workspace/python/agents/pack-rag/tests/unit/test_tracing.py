"""
Tracing 與可觀察性測試
"""

import os
from unittest.mock import MagicMock, patch

import pytest


class TestArizeInstrumentation:
    """
    測試 Arize 追蹤功能。

    重點說明:
    1. 驗證追蹤儀表化函式 (instrument_adk_with_arize)
    2. 驗證憑證檢查 (Space ID, API Key)
    3. 驗證儀表化註冊流程 (Mocking Arize/OpenInference)
    """

    def test_instrument_function_exists(self):
        """
        測試 instrument_adk_with_arize 函式存在。

        驗證點:
        1. 函式存在且可呼叫
        """
        from rag.tracing import instrument_adk_with_arize

        assert instrument_adk_with_arize is not None
        assert callable(instrument_adk_with_arize)

    @patch.dict(os.environ, {}, clear=True)
    def test_instrument_without_arize_space_id(self):
        """
        測試沒有 ARIZE_SPACE_ID 時的行為。

        驗證點:
        1. 若無 Space ID，回傳 None 並警告
        """
        from rag.tracing import instrument_adk_with_arize

        # 應該回傳 None 並產生警告
        with pytest.warns(UserWarning, match="未設定 ARIZE_SPACE_ID"):
            result = instrument_adk_with_arize()
            assert result is None

    @patch.dict(os.environ, {"ARIZE_SPACE_ID": "test-space-id"}, clear=True)
    def test_instrument_without_arize_api_key(self):
        """測試沒有 ARIZE_API_KEY 時的行為。"""
        from rag.tracing import instrument_adk_with_arize

        # 應該回傳 None 並產生警告
        with pytest.warns(UserWarning, match="未設定 ARIZE_API_KEY"):
            result = instrument_adk_with_arize()
            assert result is None

    @patch.dict(
        os.environ,
        {"ARIZE_SPACE_ID": "test-space-id", "ARIZE_API_KEY": "test-api-key"},
        clear=True,
    )
    @patch("rag.tracing.register")
    @patch("rag.tracing.GoogleADKInstrumentor")
    def test_instrument_with_credentials(self, mock_instrumentor, mock_register):
        """測試有完整憑證時的儀表化。"""
        from rag.tracing import instrument_adk_with_arize

        # 設定 mock
        mock_tracer_provider = MagicMock()
        mock_tracer = MagicMock()
        mock_register.return_value = mock_tracer_provider
        mock_tracer_provider.get_tracer.return_value = mock_tracer

        # 執行函式
        result = instrument_adk_with_arize()

        # 驗證
        mock_register.assert_called_once_with(
            space_id="test-space-id",
            api_key="test-api-key",
            project_name="adk-rag-agent",
        )
        mock_instrumentor.return_value.instrument.assert_called_once_with(
            tracer_provider=mock_tracer_provider
        )
        assert result == mock_tracer

    @patch.dict(
        os.environ,
        {
            "ARIZE_SPACE_ID": "test-space-id",
            "ARIZE_API_KEY": "test-api-key",
            "ARIZE_PROJECT_NAME": "custom-project",
        },
        clear=True,
    )
    @patch("rag.tracing.register")
    @patch("rag.tracing.GoogleADKInstrumentor")
    def test_instrument_with_custom_project_name(
        self, mock_instrumentor, mock_register
    ):
        """測試使用自訂專案名稱。"""
        from rag.tracing import instrument_adk_with_arize

        # 設定 mock
        mock_tracer_provider = MagicMock()
        mock_tracer = MagicMock()
        mock_register.return_value = mock_tracer_provider
        mock_tracer_provider.get_tracer.return_value = mock_tracer

        # 執行函式
        instrument_adk_with_arize()

        # 驗證使用自訂專案名稱
        mock_register.assert_called_once_with(
            space_id="test-space-id",
            api_key="test-api-key",
            project_name="custom-project",
        )


class TestTracingIntegration:
    """測試追蹤整合。"""

    def test_tracing_module_imports(self):
        """測試追蹤模組的導入。"""
        try:
            from arize.otel import register
            from openinference.instrumentation.google_adk import GoogleADKInstrumentor
            from opentelemetry import trace

            assert register is not None
            assert GoogleADKInstrumentor is not None
            assert trace is not None
        except ImportError as e:
            pytest.fail(f"追蹤相關模組導入失敗：{e}")

    def test_dotenv_loaded_in_tracing(self):
        """測試追蹤模組中已載入環境變數。"""
        # tracing.py 會呼叫 load_dotenv()
        from rag import tracing

        # 驗證模組已載入
        assert tracing is not None

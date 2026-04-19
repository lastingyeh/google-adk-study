"""
匯入與結構驗證測試

測試 pack-bidi-streaming 專案的所有模組是否能成功匯入。
"""

import importlib
import os
import sys


class TestImports:
    """測試所有模組是否能成功匯入。"""

    def _reload_fastapi_app(self):
        sys.modules.pop("bidi_demo.fast_api_app", None)
        return importlib.import_module("bidi_demo.fast_api_app")

    def test_import_agent_module(self):
        """測試 Agent 模組是否能被匯入。"""
        from bidi_demo import agent

        assert agent is not None

    def test_import_root_agent(self):
        """測試 root_agent 是否能從模組中匯入。"""
        from bidi_demo.agent import root_agent

        assert root_agent is not None

    def test_import_app(self):
        """測試 app 是否能從模組中匯入。"""
        from bidi_demo.agent import app

        assert app is not None

    def test_import_from_package(self):
        """測試 root_agent 是否能從套件中匯入。"""
        from bidi_demo.agent import root_agent

        assert hasattr(root_agent, "name")
        assert hasattr(root_agent, "model")

    def test_import_tool_functions(self):
        """測試工具函式是否能被匯入。"""
        from bidi_demo.agent import get_current_time, get_weather

        assert callable(get_weather)
        assert callable(get_current_time)

    def test_import_fastapi_app(self):
        """測試 FastAPI app 是否能被匯入。"""
        os.environ["SESSION_BACKEND"] = "in_memory"

        module = self._reload_fastapi_app()

        assert module.app is not None

    def test_import_fastapi_app_with_postgres_backend(self):
        """測試 postgres backend 在無 ADC 時仍可匯入 app。"""
        os.environ["SESSION_BACKEND"] = "postgres"
        os.environ["SESSION_SERVICE_URI"] = (
            "postgresql+asyncpg://app:app@postgres:5432/adk_sessions"
        )
        os.environ.pop("GOOGLE_CLOUD_PROJECT", None)

        module = self._reload_fastapi_app()

        assert module.app is not None

    def test_import_app_utils_telemetry(self):
        """測試遙測工具模組是否能被匯入。"""
        from bidi_demo.app_utils.telemetry import setup_telemetry

        assert callable(setup_telemetry)

    def test_import_app_utils_typing(self):
        """測試類型定義模組是否能被匯入。"""
        from bidi_demo.app_utils.typing import Feedback, Request

        assert Feedback is not None
        assert Request is not None

    def test_import_adk_dependencies(self):
        """測試 ADK 相依套件能否匯入。"""
        try:
            from google.adk.agents import Agent
            from google.adk.apps import App
            from google.genai import types

            assert True
        except ImportError as e:
            import pytest

            pytest.fail(f"匯入 ADK 相依套件失敗：{e}")

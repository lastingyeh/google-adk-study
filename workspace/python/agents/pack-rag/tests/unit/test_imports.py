"""
匯入與結構驗證測試
"""

import pytest


class TestImports:
    """
    測試所有模組是否能成功匯入。

    重點說明:
    1. 驗證內部模組匯入 (rag, agent, prompts, etc.)
    2. 驗證外部依賴匯入 (google.adk, vertexai, arize, fastapi)
    """

    def test_import_rag_package(self):
        """
        測試 rag 套件能否匯入。

        驗證點:
        1. import rag 成功
        """
        try:
            import rag

            assert rag is not None
        except ImportError as e:
            pytest.fail(f"匯入 rag 套件失敗：{e}")

    def test_import_agent_module(self):
        """
        測試 agent 模組是否能被匯入。

        驗證點:
        1. from rag import agent 成功
        """
        try:
            from rag import agent

            assert agent is not None
        except ImportError as e:
            pytest.fail(f"匯入 agent 模組失敗：{e}")

    def test_import_root_agent(self):
        """測試 root_agent 是否能從模組中匯入。"""
        try:
            from rag.agent import root_agent

            assert root_agent is not None
        except ImportError as e:
            pytest.fail(f"匯入 root_agent 失敗：{e}")

    def test_import_app(self):
        """測試 app 是否能從模組中匯入。"""
        try:
            from rag.agent import app

            assert app is not None
        except ImportError as e:
            pytest.fail(f"匯入 app 失敗：{e}")

    def test_import_prompts_module(self):
        """測試 prompts 模組能否被匯入。"""
        try:
            from rag import prompts

            assert prompts is not None
        except ImportError as e:
            pytest.fail(f"匯入 prompts 模組失敗：{e}")

    def test_import_return_instructions_function(self):
        """測試 return_instructions_root 函式能否被匯入。"""
        try:
            from rag.prompts import return_instructions_root

            assert return_instructions_root is not None
            assert callable(return_instructions_root)
        except ImportError as e:
            pytest.fail(f"匯入 return_instructions_root 函式失敗：{e}")

    def test_import_tracing_module(self):
        """測試 tracing 模組能否被匯入。"""
        try:
            from rag import tracing

            assert tracing is not None
        except ImportError as e:
            pytest.fail(f"匯入 tracing 模組失敗：{e}")

    def test_import_tracing_function(self):
        """測試 instrument_adk_with_arize 函式能否被匯入。"""
        try:
            from rag.tracing import instrument_adk_with_arize

            assert instrument_adk_with_arize is not None
            assert callable(instrument_adk_with_arize)
        except ImportError as e:
            pytest.fail(f"匯入 instrument_adk_with_arize 函式失敗：{e}")

    def test_import_pydantic_models(self):
        """測試 Pydantic 模型是否能被匯入。"""
        try:
            from rag.app_utils.typing import Feedback, Request

            assert Feedback is not None
            assert Request is not None
        except ImportError as e:
            pytest.fail(f"匯入 Pydantic 模型失敗：{e}")

    def test_import_telemetry_module(self):
        """測試 telemetry 模組能否被匯入。"""
        try:
            from rag.app_utils import telemetry

            assert telemetry is not None
        except ImportError as e:
            pytest.fail(f"匯入 telemetry 模組失敗：{e}")

    def test_import_telemetry_function(self):
        """測試 setup_telemetry 函式能否被匯入。"""
        try:
            from rag.app_utils.telemetry import setup_telemetry

            assert setup_telemetry is not None
            assert callable(setup_telemetry)
        except ImportError as e:
            pytest.fail(f"匯入 setup_telemetry 函式失敗：{e}")

    def test_import_fast_api_app(self):
        """測試 fast_api_app 模組能否被匯入。"""
        try:
            from rag import fast_api_app

            assert fast_api_app is not None
        except ImportError as e:
            pytest.fail(f"匯入 fast_api_app 模組失敗：{e}")

    def test_agent_has_required_attributes(self):
        """測試 Agent 是否擁有必要的屬性。"""
        from rag.agent import root_agent

        assert hasattr(root_agent, "name")
        assert hasattr(root_agent, "model")
        assert hasattr(root_agent, "instruction")
        assert hasattr(root_agent, "tools")

    def test_adk_dependencies_import(self):
        """測試 ADK 相依套件能否匯入。"""
        try:
            from google.adk.agents import Agent
            from google.adk.apps import App
            from google.adk.tools.retrieval.vertex_ai_rag_retrieval import (
                VertexAiRagRetrieval,
            )

            assert Agent is not None
            assert App is not None
            assert VertexAiRagRetrieval is not None
        except ImportError as e:
            pytest.fail(f"匯入 ADK 相依套件失敗：{e}")

    def test_vertex_ai_dependencies_import(self):
        """測試 Vertex AI 相依套件能否匯入。"""
        try:
            from vertexai.preview import rag

            assert rag is not None
        except ImportError as e:
            pytest.fail(f"匯入 Vertex AI 相依套件失敗：{e}")

    def test_arize_dependencies_import(self):
        """測試 Arize 相依套件能否匯入。"""
        try:
            from arize.otel import register
            from openinference.instrumentation.google_adk import GoogleADKInstrumentor

            assert register is not None
            assert GoogleADKInstrumentor is not None
        except ImportError as e:
            pytest.fail(f"匯入 Arize 相依套件失敗：{e}")

    def test_fastapi_dependencies_import(self):
        """測試 FastAPI 相依套件能否匯入。"""
        try:
            from fastapi import FastAPI

            assert FastAPI is not None
        except ImportError as e:
            pytest.fail(f"匯入 FastAPI 相依套件失敗：{e}")

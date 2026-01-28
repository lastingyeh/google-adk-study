"""
匯入與結構驗證測試

測試所有模組是否能成功匯入，確保沒有循環相依或遺失套件。
"""

import pytest


class TestImports:
    """測試所有模組是否能成功匯入。"""

    def test_import_agent_module(self):
        """測試 Agent 模組是否能被匯入。"""
        from app import agent

        assert agent is not None

    def test_import_root_agent(self):
        """測試 root_agent 是否能從模組中匯入。"""
        from app.agent import root_agent

        assert root_agent is not None

    def test_import_from_package(self):
        """測試 root_agent 是否能從套件中匯入。"""
        from app.agent import root_agent

        assert hasattr(root_agent, "name")
        assert hasattr(root_agent, "model")

    def test_agent_has_required_attributes(self):
        """測試 Agent 是否擁有必要的屬性。"""
        from app.agent import root_agent

        assert hasattr(root_agent, "name")
        assert hasattr(root_agent, "model")
        assert hasattr(root_agent, "description")
        assert hasattr(root_agent, "instruction")

    def test_import_sub_agents(self):
        """測試所有子 Agent 是否能被匯入。"""
        from app.story_agent import story_agent
        from app.screenplay_agent import screenplay_agent
        from app.storyboard_agent import storyboard_agent
        from app.video_agent import video_agent

        agents = [
            story_agent,
            screenplay_agent,
            storyboard_agent,
            video_agent,
        ]

        for agent in agents:
            assert agent is not None
            assert hasattr(agent, "name")

    def test_import_utils_module(self):
        """測試 utils 模組是否能被匯入。"""
        from app.utils import utils

        assert utils is not None

    def test_import_utils_functions(self):
        """測試 utils 函式是否能被匯入。"""
        from app.utils.utils import load_prompt_from_file

        assert callable(load_prompt_from_file)

    def test_import_typing_module(self):
        """測試 typing 模組是否能被匯入。"""
        from app.utils import typing

        assert typing is not None

    def test_import_pydantic_models(self):
        """測試 Pydantic 模型是否能被匯入。"""
        from app.utils.typing import Request, Feedback

        assert Request is not None
        assert Feedback is not None

    def test_import_gcs_module(self):
        """測試 GCS 模組是否能被匯入。"""
        from app.utils import gcs

        assert gcs is not None

    def test_import_gcs_functions(self):
        """測試 GCS 函式是否能被匯入。"""
        from app.utils.gcs import create_bucket_if_not_exists

        assert callable(create_bucket_if_not_exists)

    def test_import_tracing_module(self):
        """測試 tracing 模組是否能被匯入。"""
        from app.utils import tracing

        assert tracing is not None

    def test_import_tracing_classes(self):
        """測試 tracing 類別是否能被匯入。"""
        from app.utils.tracing import CloudTraceLoggingSpanExporter

        assert CloudTraceLoggingSpanExporter is not None

    def test_import_server_module(self):
        """測試 server 模組是否能被匯入。"""
        from app import server

        assert server is not None

    def test_import_fastapi_app(self):
        """測試 FastAPI app 是否能被匯入。"""
        from app.server import app

        assert app is not None

    def test_import_adk_dependencies(self):
        """測試 ADK 相依套件是否能匯入。"""
        try:
            from google.adk.agents import Agent
            from google.genai import types
            from google.adk.tools import ToolContext
            assert True
        except ImportError as e:
            pytest.fail(f"匯入 ADK 相依套件失敗：{e}")

    def test_import_vertexai_dependencies(self):
        """測試 Vertex AI 相依套件是否能匯入。"""
        try:
            import vertexai
            from vertexai.preview.vision_models import ImageGenerationModel
            from google import genai
            assert True
        except ImportError as e:
            pytest.fail(f"匯入 Vertex AI 相依套件失敗：{e}")

    def test_import_fastapi_dependencies(self):
        """測試 FastAPI 相依套件是否能匯入。"""
        try:
            from fastapi import FastAPI
            import uvicorn
            assert True
        except ImportError as e:
            pytest.fail(f"匯入 FastAPI 相依套件失敗：{e}")

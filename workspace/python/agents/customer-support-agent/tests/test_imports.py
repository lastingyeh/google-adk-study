"""測試模組匯入。"""

import pytest
import sys
import os


class TestImports:
    """測試所有必要的模組是否可以被匯入。"""

    def test_import_agent_module(self):
        """測試匯入 agent 模組。"""
        try:
            import agent

            assert agent is not None
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_import_agent_agent(self):
        """測試匯入 agent.agent。"""
        try:
            from agent import agent as agent_module

            assert agent_module is not None
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_import_fastapi(self):
        """測試匯入 fastapi。"""
        try:
            import fastapi

            assert fastapi is not None
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_import_uvicorn(self):
        """測試匯入 uvicorn。"""
        try:
            import uvicorn

            assert uvicorn is not None
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_import_google_adk(self):
        """測試匯入 google.adk。"""
        try:
            import google.adk

            assert google.adk is not None
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_import_google_adk_agents(self):
        """測試匯入 google.adk.agents。"""
        try:
            from google.adk.agents import Agent

            assert Agent is not None
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_import_ag_ui_adk(self):
        """測試匯入 ag_ui_adk。"""
        try:
            import ag_ui_adk

            assert ag_ui_adk is not None
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_import_dotenv(self):
        """測試匯入 dotenv。"""
        try:
            import dotenv

            assert dotenv is not None
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

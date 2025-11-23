"""測試所有導入是否正常運作。"""

import pytest


def test_import_agent_module():
    """測試導入 agent 模組。"""
    from production_agent import agent
    assert hasattr(agent, 'root_agent')


def test_import_root_agent():
    """測試直接導入 root_agent。"""
    from production_agent import root_agent
    assert root_agent is not None


def test_import_server_module():
    """測試導入 server 模組。"""
    from production_agent import server
    assert hasattr(server, 'app')


def test_google_adk_imports():
    """測試必要的 Google ADK 導入是否正常運作。"""
    try:
        from google.adk.agents import Agent
        from google.adk.runners import Runner
        from google.genai import types
        assert True
    except ImportError as e:
        pytest.fail(f"無法導入 Google ADK 模組: {e}")


def test_fastapi_imports():
    """測試 FastAPI 導入是否正常運作。"""
    try:
        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel
        assert True
    except ImportError as e:
        pytest.fail(f"無法導入 FastAPI 模組: {e}")


def test_tool_functions_exist():
    """測試工具函式是否已定義。"""
    from production_agent.agent import (
        check_deployment_status,
        get_deployment_options,
        get_best_practices
    )

    assert callable(check_deployment_status)
    assert callable(get_deployment_options)
    assert callable(get_best_practices)

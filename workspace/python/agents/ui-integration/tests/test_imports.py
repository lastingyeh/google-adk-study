"""測試所有必要的模組是否能正確匯入。"""

import pytest


def test_adk_imports():
    """測試 Google ADK 相關模組的匯入。"""
    try:
        from google.adk.agents import Agent
        from google.adk.runners import InMemoryRunner
        assert Agent is not None
        assert InMemoryRunner is not None
    except ImportError as e:
        pytest.fail(f"無法匯入 ADK 模組: {e}")


def test_fastapi_imports():
    """測試 FastAPI 相關模組的匯入。"""
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        import uvicorn
        assert FastAPI is not None
        assert CORSMiddleware is not None
        assert uvicorn is not None
    except ImportError as e:
        pytest.fail(f"無法匯入 FastAPI 模組: {e}")


def test_ag_ui_imports():
    """測試 AG-UI ADK 相關模組的匯入。"""
    try:
        from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
        assert ADKAgent is not None
        assert add_adk_fastapi_endpoint is not None
    except ImportError as e:
        pytest.fail(f"無法匯入 ag_ui_adk: {e}")


def test_agent_module_imports():
    """測試本地 `agent` 模組是否能成功匯入。"""
    try:
        from agent import agent, root_agent, app
        assert agent is not None
        assert root_agent is not None
        assert app is not None
    except ImportError as e:
        pytest.fail(f"無法匯入 agent 模組: {e}")

"""測試數據分析代理的導入。"""


def test_import_agent():
    """測試代理模組是否正確導入。"""
    from agent import agent

    assert agent is not None


def test_import_root_agent():
    """測試 root_agent 是否可用。"""
    from agent import root_agent

    assert root_agent is not None


def test_import_app():
    """測試 FastAPI 應用程序是否正確導入。"""
    from agent import app

    assert app is not None


def test_import_adk_dependencies():
    """測試 ADK 依賴項是否可用。"""
    from google.adk.agents import Agent

    assert Agent is not None


def test_import_ag_ui_adk():
    """測試 ag_ui_adk 是否可用。"""
    from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint

    assert ADKAgent is not None
    assert add_adk_fastapi_endpoint is not None


def test_import_pandas():
    """測試 pandas 是否可用。"""
    import pandas as pd

    assert pd is not None


def test_import_fastapi():
    """測試 FastAPI 是否可用。"""
    from fastapi import FastAPI

    assert FastAPI is not None

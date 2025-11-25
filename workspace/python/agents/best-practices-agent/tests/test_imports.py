"""測試所有必需的匯入是否正常工作。"""

import pytest


def test_import_agent():
    """測試代理模組是否可以被匯入。"""
    from best_practices_agent import root_agent
    assert root_agent is not None


def test_import_google_adk():
    """測試 Google ADK 是否可以被匯入。"""
    from google.adk.agents import Agent
    assert Agent is not None


def test_import_pydantic():
    """測試 Pydantic 是否可以被匯入。"""
    from pydantic import BaseModel, Field
    assert BaseModel is not None
    assert Field is not None


def test_import_google_genai():
    """測試 Google GenAI 是否可以被匯入。"""
    from google.genai import types
    assert types is not None


def test_all_tools_importable():
    """測試所有工具是否可以從代理模組匯入。"""
    from best_practices_agent.agent import (
        validate_input_tool,
        retry_with_backoff_tool,
        circuit_breaker_call_tool,
        cache_operation_tool,
        batch_process_tool,
        health_check_tool,
        get_metrics_tool,
    )

    assert validate_input_tool is not None
    assert retry_with_backoff_tool is not None
    assert circuit_breaker_call_tool is not None
    assert cache_operation_tool is not None
    assert batch_process_tool is not None
    assert health_check_tool is not None
    assert get_metrics_tool is not None


def test_import_classes():
    """測試支援的類別是否可以被匯入。"""
    from best_practices_agent.agent import (
        CircuitBreaker,
        CachedDataStore,
        MetricsCollector,
        CircuitState,
    )

    assert CircuitBreaker is not None
    assert CachedDataStore is not None
    assert MetricsCollector is not None
    assert CircuitState is not None

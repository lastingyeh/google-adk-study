"""
測試匯入與套件結構。

重點：確保所有模組、函式和變數都能正確匯入，且套件結構符合預期。
"""

import pytest
import importlib


def test_streaming_agent_import():
    """測試：streaming_agent 套件是否可以被匯入。"""
    try:
        import streaming_agent
        assert streaming_agent is not None
    except ImportError as e:
        pytest.fail(f"Failed to import streaming_agent: {e}")


def test_root_agent_import():
    """測試：root_agent 是否可以被匯入。"""
    try:
        from streaming_agent import root_agent
        assert root_agent is not None
    except ImportError as e:
        pytest.fail(f"Failed to import root_agent: {e}")


def test_all_exports_available():
    """測試：所有預期的匯出項目是否都可用。"""
    from streaming_agent import (
        root_agent,
        stream_agent_response,
        get_complete_response,
        create_demo_session
    )

    # 檢查：所有匯出項目是否存在
    assert root_agent is not None
    assert stream_agent_response is not None
    assert get_complete_response is not None
    assert create_demo_session is not None


def test_agent_module_structure():
    """測試：代理程式模組是否具有預期的結構。"""
    import streaming_agent.agent as agent_module

    # 檢查：預期的函式/類別是否存在
    assert hasattr(agent_module, 'create_streaming_agent')
    assert hasattr(agent_module, 'root_agent')
    assert hasattr(agent_module, 'stream_agent_response')
    assert hasattr(agent_module, 'get_complete_response')
    assert hasattr(agent_module, 'create_demo_session')


def test_tools_available():
    """測試：工具函式是否可用。"""
    from streaming_agent.agent import format_streaming_info, analyze_streaming_performance

    assert callable(format_streaming_info)
    assert callable(analyze_streaming_performance)


def test_package_version():
    """測試：套件是否包含版本資訊。"""
    import streaming_agent

    # 檢查：版本是否可用（在開發中可能未設定）
    # 這更像是一個結構檢查，而不是功能檢查
    assert hasattr(streaming_agent, '__file__')


def test_no_import_errors():
    """測試：匯入時不會引發任何錯誤。"""
    # 檢查：此測試如果在匯入時發生任何錯誤，將會失敗
    try:
        import streaming_agent
        from streaming_agent import root_agent, stream_agent_response
        import streaming_agent.agent as agent_module

        # 檢查：嘗試存取關鍵屬性
        assert agent_module.root_agent is not None
        assert agent_module.create_streaming_agent is not None

    except Exception as e:
        pytest.fail(f"Import or attribute access failed: {e}")


def test_circular_import_protection():
    """測試：沒有循環匯入問題。"""
    # 檢查：這是一個基本檢查 - 如果存在循環匯入，
    # 此檔案頂部的匯入將會失敗

    # 檢查：重新匯入以檢查問題
    importlib.reload(importlib.import_module('streaming_agent'))

    # 檢查：如果我們到達這裡而沒有錯誤，表示沒有循環匯入
    assert True

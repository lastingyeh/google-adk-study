"""
針對匯入與模組結構進行測試。
"""

def test_import_customer_service_monitor():
    """測試 CustomerServiceMonitor 是否能被匯入。
    重點：
    - 確認 `CustomerServiceMonitor` 類別可從 `observability_agent` 模組中成功匯入。
    """
    from observability_agent import CustomerServiceMonitor
    assert CustomerServiceMonitor is not None


def test_import_root_agent():
    """測試 root_agent 是否能被匯入。
    重點：
    - 確認 `root_agent` 物件可從 `observability_agent` 模組中成功匯入。
    """
    from observability_agent import root_agent
    assert root_agent is not None


def test_import_event_logger():
    """測試 EventLogger 是否能被匯入。
    重點：
    - 確認 `EventLogger` 類別可從 `observability_agent` 模組中成功匯入。
    """
    from observability_agent import EventLogger
    assert EventLogger is not None


def test_import_metrics_collector():
    """測試 MetricsCollector 是否能被匯入。
    重點：
    - 確認 `MetricsCollector` 類別可從 `observability_agent` 模組中成功匯入。
    """
    from observability_agent import MetricsCollector
    assert MetricsCollector is not None


def test_import_event_alerter():
    """測試 EventAlerter 是否能被匯入。
    重點：
    - 確認 `EventAlerter` 類別可從 `observability_agent` 模組中成功匯入。
    """
    from observability_agent import EventAlerter
    assert EventAlerter is not None


def test_import_agent_metrics():
    """測試 AgentMetrics 是否能被匯入。
    重點：
    - 確認 `AgentMetrics` 類別可從 `observability_agent` 模組中成功匯入。
    """
    from observability_agent import AgentMetrics
    assert AgentMetrics is not None


def test_all_exports():
    """測試 __all__ 的匯出是否正確。
    重點：
    - 驗證 `observability_agent` 模組的 `__all__` 變數包含所有預期的公開物件。
    """
    import observability_agent

    expected_exports = [
        'CustomerServiceMonitor',
        'EventLogger',
        'MetricsCollector',
        'EventAlerter',
        'AgentMetrics',
        'root_agent'
    ]

    for export in expected_exports:
        assert export in observability_agent.__all__

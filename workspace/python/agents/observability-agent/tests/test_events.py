"""
針對事件追蹤功能進行測試。
"""

import pytest
from datetime import datetime
from observability_agent import CustomerServiceMonitor


class TestEventLogging:
    """測試事件記錄功能。"""

    def test_tool_call_logging(self):
        """測試工具呼叫是否能正確記錄。
        重點：
        - 記錄一個工具呼叫事件。
        - 確認事件數量為 1。
        - 確認事件類型、工具名稱及參數皆正確。
        """
        monitor = CustomerServiceMonitor()

        # 記錄一個工具呼叫
        monitor._log_tool_call('test_tool', {'arg1': 'value1'})

        assert len(monitor.events) == 1
        assert monitor.events[0]['type'] == 'tool_call'
        assert monitor.events[0]['tool'] == 'test_tool'
        assert monitor.events[0]['arguments'] == {'arg1': 'value1'}

    def test_agent_event_logging(self):
        """測試代理程式事件是否能正確記錄。
        重點：
        - 記錄一個代理程式事件。
        - 確認事件數量為 1。
        - 確認事件類型與資料皆正確。
        """
        monitor = CustomerServiceMonitor()

        # 記錄一個代理程式事件
        monitor._log_agent_event('test_event', {'key': 'value'})

        assert len(monitor.events) == 1
        assert monitor.events[0]['type'] == 'test_event'
        assert monitor.events[0]['data'] == {'key': 'value'}

    def test_event_timestamp(self):
        """測試事件是否包含時間戳。
        重點：
        - 記錄一個事件。
        - 確認事件中包含 'timestamp' 欄位。
        - 驗證時間戳為 ISO 格式。
        """
        monitor = CustomerServiceMonitor()

        monitor._log_tool_call('test_tool', {})

        assert 'timestamp' in monitor.events[0]
        # 驗證時間戳為 ISO 格式
        datetime.fromisoformat(monitor.events[0]['timestamp'])

    def test_multiple_events_logged(self):
        """測試多個事件是否能正確記錄。
        重點：
        - 記錄多個不同類型的事件。
        - 確認事件總數為 3。
        - 依序檢查每個事件的內容是否正確。
        """
        monitor = CustomerServiceMonitor()

        monitor._log_tool_call('tool1', {'a': 1})
        monitor._log_tool_call('tool2', {'b': 2})
        monitor._log_agent_event('event1', {'c': 3})

        assert len(monitor.events) == 3
        assert monitor.events[0]['tool'] == 'tool1'
        assert monitor.events[1]['tool'] == 'tool2'
        assert monitor.events[2]['type'] == 'event1'


class TestEventReporting:
    """測試事件報告功能。"""

    def test_event_summary_generation(self):
        """測試事件摘要報告的生成。
        重點：
        - 記錄數個事件。
        - 產生摘要報告。
        - 確認報告中包含標題、總事件數及各類型事件計數。
        """
        monitor = CustomerServiceMonitor()

        # 新增一些測試事件
        monitor._log_tool_call('check_order_status', {'order_id': 'ORD-001'})
        monitor._log_agent_event('customer_query', {'query': 'test'})

        summary = monitor.get_event_summary()

        assert 'EVENT SUMMARY REPORT' in summary
        assert 'Total Events: 2' in summary
        assert 'tool_call: 1' in summary
        assert 'customer_query: 1' in summary

    def test_detailed_timeline_generation(self):
        """測試詳細時間軸的生成。
        重點：
        - 記錄一個事件。
        - 產生詳細時間軸。
        - 確認報告中包含標題、事件類型及工具名稱。
        """
        monitor = CustomerServiceMonitor()

        monitor._log_tool_call('test_tool', {'arg': 'value'})

        timeline = monitor.get_detailed_timeline()

        assert 'DETAILED EVENT TIMELINE' in timeline
        assert 'Type: tool_call' in timeline
        assert 'Tool: test_tool' in timeline

    def test_tool_usage_statistics(self):
        """測試摘要中的工具使用統計。
        重點：
        - 記錄多個工具呼叫。
        - 產生摘要報告。
        - 確認報告中包含各工具的呼叫次數統計。
        """
        monitor = CustomerServiceMonitor()

        # 記錄多個工具呼叫
        monitor._log_tool_call('tool1', {})
        monitor._log_tool_call('tool1', {})
        monitor._log_tool_call('tool2', {})

        summary = monitor.get_event_summary()

        assert 'tool1: 2 calls' in summary
        assert 'tool2: 1 calls' in summary

    def test_escalation_tracking(self):
        """測試報告中的升級追蹤。
        重點：
        - 記錄一個升級事件。
        - 產生摘要報告。
        - 確認報告中包含升級次數及原因。
        """
        monitor = CustomerServiceMonitor()

        monitor._log_agent_event('escalation', {
            'customer_id': 'CUST-001',
            'reason': 'High value refund'
        })

        summary = monitor.get_event_summary()

        assert 'Escalations: 1' in summary
        assert 'High value refund' in summary

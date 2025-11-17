"""
針對可觀察性類別（EventLogger、MetricsCollector、EventAlerter）進行測試。
"""

import pytest
from unittest.mock import Mock
from observability_agent import EventLogger, MetricsCollector, EventAlerter, AgentMetrics
from google.adk.events import Event
from google.genai import types


class TestEventLogger:
    """測試 EventLogger 的功能。"""

    def test_event_logger_initialization(self):
        """測試 EventLogger 是否能正確初始化。
        重點：
        - 確認 `EventLogger` 物件已建立。
        - 確認 `logger` 屬性已設定。
        """
        logger = EventLogger()

        assert logger is not None
        assert logger.logger is not None

    def test_log_event_with_content(self):
        """測試記錄包含內容的事件。
        重點：
        - 建立一個包含內容的 `Event` 物件。
        - 呼叫 `log_event` 方法，不應引發例外。
        """
        logger = EventLogger()

        event = Event(
            invocation_id='inv-123',
            author='test_agent',
            content=types.Content(parts=[types.Part(text='test message')])
        )

        # 不應引發例外
        logger.log_event(event)

    def test_log_event_without_content(self):
        """測試記錄不含內容的事件。
        重點：
        - 建立一個不含內容的 `Event` 物件。
        - 呼叫 `log_event` 方法，不應引發例外。
        """
        logger = EventLogger()

        event = Event(
            invocation_id='inv-123',
            author='test_agent'
        )

        # 不應引發例外
        logger.log_event(event)


class TestMetricsCollector:
    """測試 MetricsCollector 的功能。"""

    def test_metrics_collector_initialization(self):
        """測試 MetricsCollector 是否能正確初始化。
        重點：
        - 確認 `MetricsCollector` 物件已建立。
        - 確認 `metrics` 字典為空。
        """
        collector = MetricsCollector()

        assert collector is not None
        assert collector.metrics == {}

    def test_track_invocation_creates_metrics(self):
        """測試追蹤呼叫是否能建立指標項目。
        重點：
        - 首次追蹤代理程式呼叫時，應在 `metrics` 字典中建立新項目。
        - 呼叫計數和總延遲應正確更新。
        """
        collector = MetricsCollector()

        collector.track_invocation('test_agent', latency=0.5)

        assert 'test_agent' in collector.metrics
        assert collector.metrics['test_agent'].invocation_count == 1
        assert collector.metrics['test_agent'].total_latency == 0.5

    def test_track_multiple_invocations(self):
        """測試追蹤多次呼叫。
        重點：
        - 多次追蹤同一個代理程式的呼叫，應累加呼叫計數和總延遲。
        """
        collector = MetricsCollector()

        collector.track_invocation('test_agent', latency=0.5)
        collector.track_invocation('test_agent', latency=0.3)

        assert collector.metrics['test_agent'].invocation_count == 2
        assert collector.metrics['test_agent'].total_latency == 0.8

    def test_track_tool_calls(self):
        """測試追蹤工具呼叫。
        重點：
        - 追蹤代理程式呼叫時，應正確記錄工具呼叫次數。
        """
        collector = MetricsCollector()

        collector.track_invocation('test_agent', latency=0.5, tool_calls=3)

        assert collector.metrics['test_agent'].tool_call_count == 3

    def test_track_errors(self):
        """測試追蹤錯誤。
        重點：
        - 追蹤代理程式呼叫時，應正確記錄錯誤次數。
        """
        collector = MetricsCollector()

        collector.track_invocation('test_agent', latency=0.5, had_error=True)

        assert collector.metrics['test_agent'].error_count == 1

    def test_track_escalations(self):
        """測試追蹤升級。
        重點：
        - 追蹤代理程式呼叫時，應正確記錄升級次數。
        """
        collector = MetricsCollector()

        collector.track_invocation('test_agent', latency=0.5, escalated=True)

        assert collector.metrics['test_agent'].escalation_count == 1

    def test_get_summary_calculates_averages(self):
        """測試 get_summary 是否能計算正確的平均值。
        重點：
        - `get_summary` 方法應能根據記錄的指標計算出正確的平均延遲、錯誤率和升級率。
        """
        collector = MetricsCollector()

        collector.track_invocation('test_agent', latency=0.5)
        collector.track_invocation('test_agent', latency=0.3)

        summary = collector.get_summary('test_agent')

        assert summary['invocations'] == 2
        assert summary['avg_latency'] == 0.4
        assert summary['error_rate'] == 0.0
        assert summary['escalation_rate'] == 0.0

    def test_get_summary_nonexistent_agent(self):
        """測試對不存在的代理程式呼叫 get_summary。
        重點：
        - 當代理程式名稱不存在時，`get_summary` 應回傳空字典。
        """
        collector = MetricsCollector()

        summary = collector.get_summary('nonexistent')

        assert summary == {}


class TestEventAlerter:
    """測試 EventAlerter 的功能。"""

    def test_event_alerter_initialization(self):
        """測試 EventAlerter 是否能正確初始化。
        重點：
        - 確認 `EventAlerter` 物件已建立。
        - 確認 `rules` 列表為空。
        """
        alerter = EventAlerter()

        assert alerter is not None
        assert alerter.rules == []

    def test_add_rule(self):
        """測試新增警報規則。
        重點：
        - `add_rule` 方法應能將新的規則（條件函式與警報函式）新增至 `rules` 列表中。
        """
        alerter = EventAlerter()

        condition = lambda e: True
        alert_fn = lambda e: None

        alerter.add_rule(condition, alert_fn)

        assert len(alerter.rules) == 1

    def test_check_event_triggers_alert(self):
        """測試事件檢查在條件符合時是否能觸發警報。
        重點：
        - 當事件符合規則的條件時，應呼叫對應的警報函式。
        """
        alerter = EventAlerter()

        alert_triggered = []

        def alert_fn(event):
            alert_triggered.append(event)

        # 總是觸發的規則
        alerter.add_rule(lambda e: True, alert_fn)

        event = Event(invocation_id='inv-123', author='test')
        alerter.check_event(event)

        assert len(alert_triggered) == 1
        assert alert_triggered[0] == event

    def test_check_event_no_trigger(self):
        """測試事件檢查在條件不符合時不觸發警報。
        重點：
        - 當事件不符合規則的條件時，不應呼叫警報函式。
        """
        alerter = EventAlerter()

        alert_triggered = []

        def alert_fn(event):
            alert_triggered.append(event)

        # 永不觸發的規則
        alerter.add_rule(lambda e: False, alert_fn)

        event = Event(invocation_id='inv-123', author='test')
        alerter.check_event(event)

        assert len(alert_triggered) == 0

    def test_multiple_rules(self):
        """測試多個警報規則。
        重點：
        - `check_event` 應能檢查所有規則，並觸發所有符合條件的警報。
        """
        alerter = EventAlerter()

        alert1_triggered = []
        alert2_triggered = []

        alerter.add_rule(lambda e: True, lambda e: alert1_triggered.append(e))
        alerter.add_rule(lambda e: True, lambda e: alert2_triggered.append(e))

        event = Event(invocation_id='inv-123', author='test')
        alerter.check_event(event)

        assert len(alert1_triggered) == 1
        assert len(alert2_triggered) == 1


class TestAgentMetrics:
    """測試 AgentMetrics 資料類別。"""

    def test_agent_metrics_initialization(self):
        """測試 AgentMetrics 是否能以預設值初始化。
        重點：
        - `AgentMetrics` 物件在建立時，所有屬性應有正確的預設值（0 或 0.0）。
        """
        metrics = AgentMetrics()

        assert metrics.invocation_count == 0
        assert metrics.total_latency == 0.0
        assert metrics.tool_call_count == 0
        assert metrics.error_count == 0
        assert metrics.escalation_count == 0

    def test_agent_metrics_with_values(self):
        """測試 AgentMetrics 使用自訂值。
        重點：
        - `AgentMetrics` 物件能正確接收並儲存傳入的自訂值。
        """
        metrics = AgentMetrics(
            invocation_count=10,
            total_latency=5.5,
            tool_call_count=15,
            error_count=2,
            escalation_count=1
        )

        assert metrics.invocation_count == 10
        assert metrics.total_latency == 5.5
        assert metrics.tool_call_count == 15
        assert metrics.error_count == 2
        assert metrics.escalation_count == 1

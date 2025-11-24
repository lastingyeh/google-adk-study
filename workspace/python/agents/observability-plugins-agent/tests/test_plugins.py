"""
測試外掛程式 (Plugin) 功能與設定。
"""

import pytest
import asyncio
import time
from observability_plugins_agent.agent import (
    MetricsCollectorPlugin,
    AlertingPlugin,
    PerformanceProfilerPlugin,
    RequestMetrics,
    AggregateMetrics,
)


class TestDataClasses:
    """測試用於指標的資料類別。"""

    def test_request_metrics_creation(self):
        """測試 RequestMetrics 可以被建立。"""
        metrics = RequestMetrics(
            request_id="test-001",
            agent_name="test_agent",
            start_time=time.time()
        )
        assert metrics.request_id == "test-001"
        assert metrics.agent_name == "test_agent"
        assert metrics.success is True
        assert metrics.error is None

    def test_aggregate_metrics_creation(self):
        """測試 AggregateMetrics 可以被建立。"""
        metrics = AggregateMetrics()
        assert metrics.total_requests == 0
        assert metrics.successful_requests == 0
        assert metrics.failed_requests == 0
        assert metrics.success_rate == 0.0
        assert metrics.avg_latency == 0.0
        assert metrics.avg_tokens == 0.0

    def test_aggregate_metrics_success_rate(self):
        """測試成功率計算。"""
        metrics = AggregateMetrics()
        metrics.total_requests = 10
        metrics.successful_requests = 8
        metrics.failed_requests = 2
        assert metrics.success_rate == 0.8

    def test_aggregate_metrics_avg_latency(self):
        """測試平均延遲計算。"""
        metrics = AggregateMetrics()
        metrics.total_requests = 5
        metrics.total_latency = 10.0
        assert metrics.avg_latency == 2.0

    def test_aggregate_metrics_avg_tokens(self):
        """測試平均 Tokens 計算。"""
        metrics = AggregateMetrics()
        metrics.total_requests = 4
        metrics.total_tokens = 400
        assert metrics.avg_tokens == 100.0


class TestMetricsCollectorPlugin:
    """測試 MetricsCollectorPlugin 功能。"""

    def test_plugin_initialization(self):
        """測試 Plugin 初始化。"""
        plugin = MetricsCollectorPlugin()
        assert plugin is not None
        assert plugin.metrics is not None
        assert isinstance(plugin.metrics, AggregateMetrics)
        assert plugin.current_requests == {}

    def test_get_summary(self):
        """測試 get_summary 回傳格式化字串。"""
        plugin = MetricsCollectorPlugin()
        summary = plugin.get_summary()
        assert isinstance(summary, str)
        assert "METRICS SUMMARY" in summary
        assert "Total Requests:" in summary
        assert "Success Rate:" in summary


class TestAlertingPlugin:
    """測試 AlertingPlugin 功能。"""

    def test_plugin_initialization(self):
        """測試 Plugin 初始化。"""
        plugin = AlertingPlugin()
        assert plugin is not None
        assert plugin.latency_threshold == 5.0
        assert plugin.error_threshold == 3
        assert plugin.consecutive_errors == 0

    def test_plugin_initialization_custom_thresholds(self):
        """測試 Plugin 可以使用自訂閾值初始化。"""
        plugin = AlertingPlugin(latency_threshold=3.0, error_threshold=2)
        assert plugin.latency_threshold == 3.0
        assert plugin.error_threshold == 2


class TestPerformanceProfilerPlugin:
    """測試 PerformanceProfilerPlugin 功能。"""

    def test_plugin_initialization(self):
        """測試 Plugin 初始化。"""
        plugin = PerformanceProfilerPlugin()
        assert plugin is not None
        assert plugin.profiles == []
        assert plugin.current_profile is None

    def test_get_profile_summary_empty(self):
        """測試沒有 Profile 時的 get_profile_summary。"""
        plugin = PerformanceProfilerPlugin()
        summary = plugin.get_profile_summary()
        assert isinstance(summary, str)
        assert "No profiles collected" in summary

    def test_profile_data_structure(self):
        """測試 Profile 可以被新增。"""
        plugin = PerformanceProfilerPlugin()

        # 模擬新增一個 Profile
        profile = {
            'tool': 'test_tool',
            'start_time': time.time(),
            'end_time': time.time() + 1.0,
            'duration': 1.0
        }
        plugin.profiles.append(profile)

        assert len(plugin.profiles) == 1
        assert plugin.profiles[0]['tool'] == 'test_tool'
        assert 'duration' in plugin.profiles[0]


class TestPluginIntegration:
    """測試 Plugin 整合情境。"""

    def test_all_plugins_can_be_instantiated(self):
        """測試所有 Plugin 可以一起被建立。"""
        plugins = [
            MetricsCollectorPlugin(),
            AlertingPlugin(),
            PerformanceProfilerPlugin(),
        ]
        assert len(plugins) == 3
        assert all(plugin is not None for plugin in plugins)

    def test_plugins_are_base_plugin_instances(self):
        """測試所有 Plugin 都繼承自 BasePlugin。"""
        from google.adk.plugins import BasePlugin

        plugins = [
            MetricsCollectorPlugin(),
            AlertingPlugin(),
            PerformanceProfilerPlugin(),
        ]

        for plugin in plugins:
            assert isinstance(plugin, BasePlugin)

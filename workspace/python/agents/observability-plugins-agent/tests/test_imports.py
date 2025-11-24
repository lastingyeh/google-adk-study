"""
測試所有必要的匯入 (imports) 是否正常運作。
"""

import pytest


class TestImports:
    """測試所有匯入是否正常運作。"""

    def test_google_adk_imports(self):
        """測試 Google ADK 相關模組匯入是否正常。"""
        try:
            from google.adk.agents import Agent
            from google.adk.plugins import BasePlugin
            from google.adk.plugins.save_files_as_artifacts_plugin import SaveFilesAsArtifactsPlugin
            from google.adk.events import Event
            from google.adk.runners import InMemoryRunner
            from google.adk.sessions import InMemorySessionService
            # 所有匯入成功
            assert True
        except ImportError as e:
            pytest.fail(f"ADK 匯入失敗: {e}")

    def test_google_genai_imports(self):
        """測試 Google GenAI 相關模組匯入是否正常。"""
        try:
            from google.genai import types
            # 測試 Part 物件是否可以建立
            part = types.Part.from_text(text="test")
            assert part is not None
            assert True
        except ImportError as e:
            pytest.fail(f"Google GenAI 匯入失敗: {e}")

    def test_agent_imports(self):
        """測試 Agent 模組匯入是否正常。"""
        try:
            from observability_plugins_agent.agent import root_agent
            assert root_agent is not None
            assert root_agent.name == "observability_plugins_agent"
        except ImportError as e:
            pytest.fail(f"Agent 匯入失敗: {e}")

    def test_plugin_imports(self):
        """測試 Plugin 類別匯入是否正常。"""
        try:
            from observability_plugins_agent.agent import (
                MetricsCollectorPlugin,
                AlertingPlugin,
                PerformanceProfilerPlugin,
            )
            # 驗證所有類別匯入成功且可呼叫
            assert callable(MetricsCollectorPlugin)
            assert callable(AlertingPlugin)
            assert callable(PerformanceProfilerPlugin)
        except ImportError as e:
            pytest.fail(f"Plugin 類別匯入失敗: {e}")

    def test_dataclass_imports(self):
        """測試資料類別 (Dataclasses) 匯入是否正常。"""
        try:
            from observability_plugins_agent.agent import (
                RequestMetrics,
                AggregateMetrics,
            )
            # 驗證所有資料類別匯入成功
            assert RequestMetrics is not None
            assert AggregateMetrics is not None
        except ImportError as e:
            pytest.fail(f"Dataclass 匯入失敗: {e}")

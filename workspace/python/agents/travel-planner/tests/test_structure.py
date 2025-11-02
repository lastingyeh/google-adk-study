"""
教學 05：平行處理的結構測試
"""

import pytest


class TestStructure:
    """測試專案結構"""

    def test_google_adk_agents_import(self):
        """測試 google.adk.agents 是否可以被導入"""
        import importlib.util

        spec = importlib.util.find_spec("google.adk.agents")
        assert spec is not None, "google.adk.agents 模組未找到"

    def test_travel_planner_agent_import(self):
        """測試 travel_planner.agent 模組是否可以被導入"""
        import importlib.util

        spec = importlib.util.find_spec("travel_planner.agent")
        assert spec is not None, "travel_planner.agent 模組未找到"

    def test_root_agent_exists(self):
        """測試 root_agent 是否已定義且可訪問"""
        try:
            from travel_planner.agent import root_agent

            assert root_agent is not None
        except ImportError as e:
            pytest.fail(f"無法導入 root_agent：{e}")

    def test_future_annotations_import(self):
        """測試 __future__ annotations 是否已導入"""
        import travel_planner.agent

        # 如果未導入 __future__ annotations，這將在導入時失敗
        # 因為我們在類型提示中使用了 | 語法
        assert hasattr(travel_planner.agent, "root_agent")

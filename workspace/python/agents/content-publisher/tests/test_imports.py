"""
用於教學課程 06：多代理系統 - 內容發布系統的匯入測試。
"""

import pytest


class TestImports:
    """測試所有必要的匯入是否正常運作"""

    def test_google_adk_agents_import(self):
        """測試 google.adk.agents 是否能成功匯入"""
        try:
            from google.adk.agents import Agent, ParallelAgent, SequentialAgent
        except ImportError as e:
            pytest.fail(f"無法匯入 google.adk.agents: {e}")

    def test_content_publisher_agent_import(self):
        """測試 content_publisher.agent 是否能成功匯入"""
        try:
            import content_publisher.agent
        except ImportError as e:
            pytest.fail(f"無法匯入 content_publisher.agent: {e}")

    def test_root_agent_exists(self):
        """測試 root_agent 是否已定義且可存取"""
        try:
            from content_publisher.agent import root_agent

            assert root_agent is not None
        except (ImportError, AttributeError) as e:
            pytest.fail(f"無法存取 root_agent: {e}")

    def test_future_annotations_import(self):
        """測試 __future__ annotations 的匯入是否正常"""
        try:
            exec("from __future__ import annotations")
        except ImportError as e:
            pytest.fail(f"無法匯入 __future__.annotations: {e}")

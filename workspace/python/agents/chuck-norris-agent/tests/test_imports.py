import pytest


class TestImports:
    """測試所有匯入是否正常運作"""

    def test_google_adk_agents_import(self):
        """測試 google.adk.agents 的匯入"""
        try:
            from google.adk.agents import Agent
            assert Agent is not None
        except ImportError as e:
            pytest.fail(f"匯入 Agent 失敗：{e}")

    def test_google_adk_tools_import(self):
        """測試 google.adk.tools 的匯入"""
        try:
            from google.adk.tools.openapi_tool import OpenAPIToolset
            assert OpenAPIToolset is not None
        except ImportError as e:
            pytest.fail(f"匯入 OpenAPIToolset 失敗：{e}")

    def test_chuck_norris_agent_import(self):
        """測試 chuck_norris_agent 模組的匯入"""
        try:
            import chuck_norris_agent
            assert chuck_norris_agent is not None
        except ImportError as e:
            pytest.fail(f"匯入 chuck_norris_agent 失敗：{e}")

    def test_chuck_norris_agent_agent_import(self):
        """測試 chuck_norris_agent.agent 模組的匯入"""
        try:
            from chuck_norris_agent import agent
            assert agent is not None
        except ImportError as e:
            pytest.fail(f"匯入 chuck_norris_agent.agent 失敗：{e}")

    def test_root_agent_exists(self):
        """測試 root_agent 是否能從套件中匯入"""
        try:
            from chuck_norris_agent import root_agent
            assert root_agent is not None
        except ImportError as e:
            pytest.fail(f"匯入 root_agent 失敗：{e}")

    def test_future_annotations_import(self):
        """測試 __future__ annotations 的匯入"""
        # 測試 __future__ 模組是否存在且 annotations 可以被匯入
        try:
            import __future__
            assert hasattr(__future__, "annotations")
            # 此處驗證匯入功能無語法問題
            assert True
        except (ImportError, AttributeError) as e:
            pytest.fail(f"驗證 __future__ annotations 失敗：{e}")

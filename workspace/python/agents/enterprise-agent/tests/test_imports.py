"""
Tutorial 26 的測試套件：匯入驗證。
"""

import pytest


class TestCoreImports:
    """測試核心依賴項是否可以被匯入。"""

    def test_import_google_adk_agents(self):
        """測試匯入 google.adk.agents。"""
        try:
            from google.adk.agents import Agent
            assert Agent is not None
        except ImportError as e:
            pytest.fail(f"無法匯入 google.adk.agents: {e}")

    def test_import_google_adk_tools(self):
        """測試匯入 google.adk.tools。"""
        try:
            from google.adk.tools import FunctionTool
            assert FunctionTool is not None
        except ImportError as e:
            pytest.fail(f"無法匯入 google.adk.tools: {e}")


class TestModuleImports:
    """測試教學模組是否可以被匯入。"""

    def test_import_enterprise_agent_module(self):
        """測試匯入 enterprise_agent 模組。"""
        try:
            import enterprise_agent
            assert enterprise_agent is not None
        except ImportError as e:
            pytest.fail(f"無法匯入 enterprise_agent: {e}")

    def test_import_root_agent(self):
        """測試從模組匯入 root_agent。"""
        try:
            from enterprise_agent import root_agent
            assert root_agent is not None
        except ImportError as e:
            pytest.fail(f"無法匯入 root_agent: {e}")

    def test_import_agent_module(self):
        """測試匯入 enterprise_agent.agent 模組。"""
        try:
            from enterprise_agent import agent
            assert agent is not None
        except ImportError as e:
            pytest.fail(f"無法匯入 enterprise_agent.agent: {e}")


class TestToolFunctionImports:
    """測試工具函數是否可以被匯入。"""

    def test_import_check_company_size(self):
        """測試匯入 check_company_size 函數。"""
        try:
            from enterprise_agent.agent import check_company_size
            assert check_company_size is not None
            assert callable(check_company_size)
        except ImportError as e:
            pytest.fail(f"無法匯入 check_company_size: {e}")

    def test_import_score_lead(self):
        """測試匯入 score_lead 函數。"""
        try:
            from enterprise_agent.agent import score_lead
            assert score_lead is not None
            assert callable(score_lead)
        except ImportError as e:
            pytest.fail(f"無法匯入 score_lead: {e}")

    def test_import_get_competitive_intel(self):
        """測試匯入 get_competitive_intel 函數。"""
        try:
            from enterprise_agent.agent import get_competitive_intel
            assert get_competitive_intel is not None
            assert callable(get_competitive_intel)
        except ImportError as e:
            pytest.fail(f"無法匯入 get_competitive_intel: {e}")


class TestModuleAttributes:
    """測試模組級別屬性。"""

    def test_module_has_all(self):
        """測試模組是否定義了 __all__。"""
        import enterprise_agent
        assert hasattr(enterprise_agent, '__all__')
        assert 'root_agent' in enterprise_agent.__all__

    def test_root_agent_accessible(self):
        """測試 root_agent 是否可從模組訪問。"""
        import enterprise_agent
        assert hasattr(enterprise_agent, 'root_agent')
        assert enterprise_agent.root_agent is not None

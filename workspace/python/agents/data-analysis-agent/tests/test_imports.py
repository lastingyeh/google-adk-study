"""
匯入與結構驗證測試
"""


class TestImports:
    """測試所有模組是否能成功匯入。"""

    def test_import_agent_module(self):
        """測試 Agent 模組是否能被匯入。"""
        from data_analysis_agent import agent
        assert agent is not None

    def test_import_root_agent(self):
        """測試 root_agent 是否能從模組中匯入。"""
        from data_analysis_agent import root_agent
        assert root_agent is not None

    def test_import_from_package(self):
        """測試 root_agent 是否能從套件中匯入。"""
        from data_analysis_agent import root_agent
        assert hasattr(root_agent, 'name')
        assert hasattr(root_agent, 'model')

    def test_tool_functions_exist(self):
        """測試所有工具函式是否存在且可被呼叫。"""
        from data_analysis_agent.agent import (
            analyze_column,
            calculate_correlation,
            filter_data,
            get_dataset_summary,
        )

        assert callable(analyze_column)
        assert callable(calculate_correlation)
        assert callable(filter_data)
        assert callable(get_dataset_summary)

    def test_agent_has_required_attributes(self):
        """測試 Agent 是否擁有必要的屬性。"""
        from data_analysis_agent import root_agent

        assert hasattr(root_agent, 'name')
        assert hasattr(root_agent, 'model')
        assert hasattr(root_agent, 'description')
        assert hasattr(root_agent, 'instruction')
        assert hasattr(root_agent, 'tools')

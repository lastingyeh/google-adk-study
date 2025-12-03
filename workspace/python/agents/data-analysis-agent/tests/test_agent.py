"""
Agent 配置與工具測試
"""


class TestAgentConfiguration:
    """測試 Agent 配置與屬性。"""

    def test_root_agent_exists(self):
        """測試 root_agent 是否已正確定義。"""
        from data_analysis_agent import root_agent

        assert root_agent is not None

    def test_agent_has_correct_name(self):
        """測試 Agent 是否擁有正確名稱。

        說明：在多重 Agent 重構後，root agent 現在是一個協調者(coordinator)，
        負責委派給專門的子 Agent（分析與視覺化）。
        """
        from data_analysis_agent import root_agent

        # The coordinator agent has a different name but the pattern is correct
        assert root_agent.name in ["data_analysis_agent", "data_analysis_coordinator"]

    def test_agent_has_correct_model(self):
        """測試 Agent 是否使用正確的模型。"""
        from data_analysis_agent import root_agent

        assert root_agent.model == "gemini-2.0-flash"

    def test_agent_has_description(self):
        """測試 Agent 是否擁有描述。"""
        from data_analysis_agent import root_agent

        assert root_agent.description is not None
        assert len(root_agent.description) > 0

    def test_agent_has_instruction(self):
        """測試 Agent 是否擁有指令。"""
        from data_analysis_agent import root_agent

        assert root_agent.instruction is not None
        assert len(root_agent.instruction) > 0

    def test_agent_has_tools(self):
        """測試 Agent 是否已配置工具。"""
        from data_analysis_agent import root_agent

        assert hasattr(root_agent, 'tools')
        assert root_agent.tools is not None
        assert len(root_agent.tools) > 0

    def test_agent_tools_count(self):
        """測試 Agent 是否擁有預期數量的工具。

        說明：在多重 Agent 重構後，root agent 現在擁有 2 個 AgentTools
        (analysis_agent 和 visualization_agent)，而不是 4 個直接工具。
        這是正確的模式，因為它允許 visualization_agent 擁有 BuiltInCodeExecutor，
        而 analysis_agent 擁有傳統工具。
        """
        from data_analysis_agent import root_agent

        # Now we have AgentTools instead of direct tools
        # 2 AgentTools: analysis_agent and visualization_agent
        assert len(root_agent.tools) >= 2


class TestAgentTools:
    """測試個別 Agent 工具。"""

    def test_analyze_column_tool(self):
        """測試 analyze_column 工具。"""
        from data_analysis_agent.agent import analyze_column

        result = analyze_column("test_column", "summary")

        assert isinstance(result, dict)
        assert "status" in result
        assert "report" in result
        assert result["status"] in ["success", "error"]

    def test_analyze_column_success(self):
        """測試 analyze_column 工具於有效輸入時的情況。"""
        from data_analysis_agent.agent import analyze_column

        result = analyze_column("age", "summary")

        assert result["status"] == "success"
        assert "report" in result

    def test_analyze_column_invalid_column(self):
        """測試 analyze_column 工具於無效欄位名稱時的情況。"""
        from data_analysis_agent.agent import analyze_column

        result = analyze_column("", "summary")

        assert result["status"] == "error"
        assert "report" in result

    def test_calculate_correlation_tool(self):
        """測試 calculate_correlation 工具。"""
        from data_analysis_agent.agent import calculate_correlation

        result = calculate_correlation("col1", "col2")

        assert isinstance(result, dict)
        assert "status" in result
        assert "report" in result
        assert result["status"] in ["success", "error"]

    def test_calculate_correlation_missing_params(self):
        """測試 calculate_correlation 工具於參數缺失時的情況。"""
        from data_analysis_agent.agent import calculate_correlation

        result = calculate_correlation("col1", "")

        assert result["status"] == "error"

    def test_filter_data_tool(self):
        """測試 filter_data 工具。"""
        from data_analysis_agent.agent import filter_data

        result = filter_data("age", "greater_than", "30")

        assert isinstance(result, dict)
        assert "status" in result
        assert "report" in result

    def test_filter_data_missing_params(self):
        """測試 filter_data 工具於參數缺失時的情況。"""
        from data_analysis_agent.agent import filter_data

        result = filter_data("", "equals", "value")

        assert result["status"] == "error"

    def test_get_dataset_summary_tool(self):
        """測試 get_dataset_summary 工具。"""
        from data_analysis_agent.agent import get_dataset_summary

        result = get_dataset_summary()

        assert isinstance(result, dict)
        assert "status" in result
        assert result["status"] == "success"
        assert "report" in result

    def test_tool_return_format(self):
        """測試工具回傳格式的一致性。"""
        from data_analysis_agent.agent import (
            analyze_column,
            calculate_correlation,
            filter_data,
            get_dataset_summary,
        )

        tools = [
            analyze_column("col", "summary"),
            calculate_correlation("col1", "col2"),
            filter_data("col", "equals", "val"),
            get_dataset_summary(),
        ]

        for result in tools:
            assert isinstance(result, dict)
            assert "status" in result
            assert "report" in result
            assert result["status"] in ["success", "error"]


class TestToolExceptionHandling:
    """測試工具是否能優雅地處理例外狀況。"""

    def test_analyze_column_handles_exception(self):
        """測試 analyze_column 是否能處理例外。"""
        from data_analysis_agent.agent import analyze_column

        # This should not raise an exception even with bad input
        result = analyze_column(None, None)  # type: ignore

        assert isinstance(result, dict)
        assert "status" in result

    def test_filter_data_handles_exception(self):
        """測試 filter_data 是否能處理例外。"""
        from data_analysis_agent.agent import filter_data

        # This should not raise an exception even with bad input
        result = filter_data(None, None, None)  # type: ignore

        assert isinstance(result, dict)
        assert "status" in result

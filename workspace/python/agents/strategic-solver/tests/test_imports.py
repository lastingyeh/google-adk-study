"""
測試 Strategic Problem Solver 的匯入與基本代理結構。

重點說明：
此測試檔案確保所有必要的模組、代理與工具都能被正確匯入，
並驗證專案結構的完整性，例如必要檔案與目錄是否存在。
"""

import importlib.util
import os

import pytest


class TestImports:
    """測試所有模組是否能被正確匯入"""

    def test_strategic_solver_agent_import(self):
        """測試 strategic_solver.agent 模組是否能被匯入"""
        spec = importlib.util.find_spec("strategic_solver.agent")
        assert spec is not None, "strategic_solver.agent module not found"

    def test_strategic_solver_agent_has_root_agent(self):
        """測試 strategic_solver.agent 是否包含 root_agent"""
        import strategic_solver.agent
        assert hasattr(strategic_solver.agent, 'root_agent')

    def test_root_agent_is_agent_instance(self):
        """測試 root_agent 是否為 Agent 的實例"""
        from strategic_solver.agent import root_agent
        from google.adk.agents import Agent
        assert isinstance(root_agent, Agent)

    def test_all_planner_agents_exist(self):
        """測試所有規劃器代理變體是否存在"""
        from strategic_solver.agent import (
            builtin_planner_agent,
            plan_react_agent,
            strategic_planner_agent
        )

        from google.adk.agents import Agent

        assert isinstance(builtin_planner_agent, Agent)
        assert isinstance(plan_react_agent, Agent)
        assert isinstance(strategic_planner_agent, Agent)

    def test_planner_imports(self):
        """測試規劃器類別是否能被匯入"""
        from google.adk.planners import BuiltInPlanner, PlanReActPlanner, BasePlanner

        # These should not raise ImportError
        assert BuiltInPlanner is not None
        assert PlanReActPlanner is not None
        assert BasePlanner is not None


class TestProjectStructure:
    """測試專案結構是否正確"""

    def test_strategic_solver_directory_exists(self):
        """測試 strategic_solver 目錄是否存在"""
        assert os.path.exists("strategic_solver")

    def test_init_file_exists(self):
        """測試 __init__.py 檔案是否存在"""
        assert os.path.exists("strategic_solver/__init__.py")

    def test_agent_file_exists(self):
        """測試 agent.py 檔案是否存在"""
        assert os.path.exists("strategic_solver/agent.py")

    def test_env_example_exists(self):
        """測試 .env.example 檔案是否存在"""
        assert os.path.exists("strategic_solver/.env.example")

    def test_init_file_content(self):
        """測試 __init__.py 的內容是否正確"""
        with open("strategic_solver/__init__.py", "r") as f:
            content = f.read()
            assert "Strategic Problem Solver" in content
            assert "Tutorial 12" in content

    def test_env_example_content(self):
        """測試 .env.example 是否包含必要的變數"""
        with open("strategic_solver/.env.example", "r") as f:
            content = f.read()
            assert "GOOGLE_API_KEY" in content
            assert "GOOGLE_GENAI_USE_VERTEXAI" in content

    def test_agent_file_is_python(self):
        """測試 agent.py 是否為一個有效的 Python 檔案"""
        import strategic_solver.agent
        assert strategic_solver.agent.__file__.endswith("agent.py")


class TestTools:
    """測試工具是否已正確定義"""

    def test_tools_can_be_imported(self):
        """測試工具函式是否能被匯入"""
        from strategic_solver.agent import (
            analyze_market,
            calculate_roi,
            assess_risk,
            save_strategy_report
        )

        # These should be functions
        assert callable(analyze_market)
        assert callable(calculate_roi)
        assert callable(assess_risk)
        assert callable(save_strategy_report)

    def test_tools_have_docstrings(self):
        """測試工具是否包含適當的文件字串"""
        from strategic_solver.agent import (
            analyze_market,
            calculate_roi,
            assess_risk,
            save_strategy_report
        )

        assert analyze_market.__doc__ is not None
        assert "Analyze market conditions" in analyze_market.__doc__

        assert calculate_roi.__doc__ is not None
        assert "Calculate return on investment" in calculate_roi.__doc__

        assert assess_risk.__doc__ is not None
        assert "Assess business risks" in assess_risk.__doc__

        assert save_strategy_report.__doc__ is not None
        assert "Save strategic plan" in save_strategy_report.__doc__

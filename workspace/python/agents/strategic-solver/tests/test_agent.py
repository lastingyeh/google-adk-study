"""
測試 Strategic Problem Solver 的代理 (agent) 與規劃器 (planner)。

重點說明：
此測試檔案確保所有代理與規劃器都已正確配置，
包含名稱、模型、工具、輸出鍵等，並驗證其繼承結構與指令內容的正確性。
"""

import pytest
from unittest.mock import MagicMock

from strategic_solver.agent import (
    builtin_planner_agent,
    plan_react_agent,
    strategic_planner_agent,
    root_agent,
    StrategicPlanner
)
from google.adk.agents import Agent
from google.adk.planners import BuiltInPlanner, PlanReActPlanner, BasePlanner


class TestAgentConfiguration:
    """測試代理配置"""

    def test_builtin_planner_agent_config(self):
        """測試 BuiltInPlanner 代理的配置"""
        assert isinstance(builtin_planner_agent, Agent)
        assert builtin_planner_agent.name == "builtin_planner_strategic_solver"
        assert builtin_planner_agent.model == "gemini-2.0-flash"
        assert isinstance(builtin_planner_agent.planner, BuiltInPlanner)

    def test_plan_react_agent_config(self):
        """測試 PlanReActPlanner 代理的配置"""
        assert isinstance(plan_react_agent, Agent)
        assert plan_react_agent.name == "plan_react_strategic_solver"
        assert isinstance(plan_react_agent.planner, PlanReActPlanner)

    def test_strategic_planner_agent_config(self):
        """測試 StrategicPlanner 代理的配置"""
        assert isinstance(strategic_planner_agent, Agent)
        assert strategic_planner_agent.name == "strategic_planner_solver"
        assert isinstance(strategic_planner_agent.planner, StrategicPlanner)

    def test_root_agent_is_plan_react(self):
        """測試 root_agent 是否使用 PlanReActPlanner"""
        assert root_agent is plan_react_agent
        assert isinstance(root_agent.planner, PlanReActPlanner)

    def test_agents_have_tools(self):
        """測試所有代理是否都擁有必要的工具"""
        agents = [builtin_planner_agent, plan_react_agent, strategic_planner_agent]

        for agent in agents:
            assert len(agent.tools) == 4  # 4 business analysis tools
            tool_names = [tool.func.__name__ for tool in agent.tools]
            assert "analyze_market" in tool_names
            assert "calculate_roi" in tool_names
            assert "assess_risk" in tool_names
            assert "save_strategy_report" in tool_names

    def test_agents_have_output_keys(self):
        """測試代理是否具有適當的輸出鍵"""
        assert builtin_planner_agent.output_key == "builtin_strategy_result"
        assert plan_react_agent.output_key == "plan_react_strategy_result"
        assert strategic_planner_agent.output_key == "strategic_planner_result"


class TestPlannerConfiguration:
    """測試規劃器配置"""

    def test_builtin_planner_thinking_config(self):
        """測試 BuiltInPlanner 是否已啟用思考配置"""
        planner = builtin_planner_agent.planner
        assert isinstance(planner, BuiltInPlanner)
        assert planner.thinking_config.include_thoughts is True

    def test_plan_react_planner_instance(self):
        """測試 PlanReActPlanner 是否已正確實例化"""
        planner = plan_react_agent.planner
        assert isinstance(planner, PlanReActPlanner)

    def test_strategic_planner_inheritance(self):
        """測試 StrategicPlanner 是否繼承自 BasePlanner"""
        planner = strategic_planner_agent.planner
        assert isinstance(planner, StrategicPlanner)
        assert isinstance(planner, BasePlanner)


class TestStrategicPlanner:
    """測試自訂的 StrategicPlanner 實作"""

    def test_strategic_planner_creation(self):
        """測試 StrategicPlanner 是否可以被建立"""
        planner = StrategicPlanner()
        assert isinstance(planner, StrategicPlanner)
        assert isinstance(planner, BasePlanner)

    def test_build_planning_instruction(self):
        """測試 StrategicPlanner 是否能建立規劃指令"""
        planner = StrategicPlanner()
        mock_context = MagicMock()
        mock_request = MagicMock()

        instruction = planner.build_planning_instruction(mock_context, mock_request)

        assert instruction is not None
        assert "ANALYSIS" in instruction
        assert "EVALUATION" in instruction
        assert "STRATEGY" in instruction
        assert "VALIDATION" in instruction
        assert "FINAL_RECOMMENDATION" in instruction

    def test_process_planning_response(self):
        """測試 StrategicPlanner 是否能處理規劃回應"""
        planner = StrategicPlanner()
        mock_callback_context = MagicMock()
        mock_parts = [MagicMock()]

        result = planner.process_planning_response(mock_callback_context, mock_parts)

        # Should return the parts unchanged for this implementation
        assert result == mock_parts


class TestAgentInstructions:
    """測試代理指令內容"""

    def test_builtin_planner_instruction(self):
        """測試 BuiltInPlanner 代理是否包含適當的指令"""
        instruction = builtin_planner_agent.instruction
        assert "strategic consultant" in instruction.lower()
        assert "analyze_market" in instruction
        assert "calculate_roi" in instruction
        assert "assess_risk" in instruction

    def test_plan_react_instruction(self):
        """測試 PlanReActPlanner 代理是否包含結構化的指令"""
        instruction = plan_react_agent.instruction
        assert "systematic" in instruction.lower()
        assert "planning tags" in instruction.lower()
        assert "structured format" in instruction.lower()

    def test_strategic_planner_instruction(self):
        """測試 StrategicPlanner 代理是否包含領域特定的指令"""
        instruction = strategic_planner_agent.instruction
        assert "business strategy consultant" in instruction.lower()
        assert "ANALYSIS" in instruction
        assert "EVALUATION" in instruction
        assert "STRATEGY" in instruction


class TestGenerateContentConfig:
    """測試內容生成配置"""

    def test_temperature_settings(self):
        """測試不同代理的溫度設定"""
        # Strategic agents should have lower temperature for consistency
        assert builtin_planner_agent.generate_content_config.temperature == 0.3
        assert plan_react_agent.generate_content_config.temperature == 0.4
        assert strategic_planner_agent.generate_content_config.temperature == 0.3

    def test_max_output_tokens(self):
        """測試最大輸出 token 設定"""
        agents = [builtin_planner_agent, plan_react_agent, strategic_planner_agent]
        for agent in agents:
            assert agent.generate_content_config.max_output_tokens == 3000


@pytest.mark.asyncio
class TestDemoFunction:
    """測試展示功能"""

    async def test_demo_function_exists(self):
        """測試展示函式是否可以被匯入"""
        from strategic_solver.agent import demo_strategic_planning
        assert callable(demo_strategic_planning)

    async def test_demo_function_runs_without_error(self):
        """測試展示函式執行時不會拋出例外"""
        from strategic_solver.agent import demo_strategic_planning

        # This should not raise an exception (though it may not do much without API keys)
        try:
            await demo_strategic_planning()
        except Exception as e:
            # Allow certain expected errors (like missing API keys)
            if "API key" not in str(e) and "GOOGLE_API_KEY" not in str(e):
                raise

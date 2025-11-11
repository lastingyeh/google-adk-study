"""
Strategic Problem Solver 的整合測試。

重點說明：
此測試檔案專注於完整的端到端工作流程與代理之間的互動，
確保不同工具與規劃器能夠協同工作，並正確處理錯誤與部分失敗的情境。
"""

import pytest
from unittest.mock import MagicMock

from strategic_solver.agent import (
    builtin_planner_agent,
    plan_react_agent,
    strategic_planner_agent,
    analyze_market,
    calculate_roi,
    assess_risk,
    save_strategy_report
)


@pytest.mark.integration
class TestPlannerIntegration:
    """規劃器功能的整合測試"""

@pytest.mark.asyncio
async def test_builtin_planner_workflow():
    """測試 BuiltInPlanner 代理的實例化與配置是否正確"""
    # Test that the agent can be created and has the expected properties
    assert builtin_planner_agent is not None
    assert builtin_planner_agent.name == "builtin_planner_strategic_solver"
    assert builtin_planner_agent.model == "gemini-2.0-flash"
    assert len(builtin_planner_agent.tools) == 4  # All business analysis tools
    assert builtin_planner_agent.planner is not None
    assert hasattr(builtin_planner_agent.planner, 'thinking_config')
    # Test passes if agent is properly configured


@pytest.mark.asyncio
async def test_plan_react_planner_workflow():
    """測試 PlanReActPlanner 代理的實例化與配置是否正確"""
    # Test that the agent can be created and has the expected properties
    assert plan_react_agent is not None
    assert plan_react_agent.name == "plan_react_strategic_solver"
    assert plan_react_agent.model == "gemini-2.0-flash"
    assert len(plan_react_agent.tools) == 4  # All business analysis tools
    assert plan_react_agent.planner is not None
    assert plan_react_agent.planner.__class__.__name__ == "PlanReActPlanner"
    # Test passes if agent is properly configured


class TestToolIntegration:
    """工具組合的整合測試"""

    def test_market_analysis_and_roi_integration(self):
        """測試市場分析與 ROI 計算的整合"""
        # Analyze market first
        mock_context = MagicMock()
        market_result = analyze_market("healthcare", "North America", mock_context)

        assert market_result["status"] == "success"
        growth_rate = market_result["analysis"]["growth_rate"]  # "8.5%"

        # Use growth rate for ROI calculation
        annual_return = float(growth_rate.strip('%'))
        roi_result = calculate_roi(100000, annual_return, 5, mock_context)

        assert roi_result["status"] == "success"
        assert roi_result["calculation"]["roi_percentage"] > 0

    def test_risk_assessment_and_strategy_integration(self):
        """測試風險評估與策略發展的整合"""
        mock_context = MagicMock()
        mock_context.saved_reports = []

        # Assess risks
        risk_factors = ["market_volatility", "competition", "regulatory_changes"]
        risk_result = assess_risk(risk_factors, mock_context)

        assert risk_result["status"] == "success"
        risk_level = risk_result["assessment"]["risk_level"]

        # Create strategy based on risk assessment
        strategy = f"Given {risk_level} risk level, recommend conservative approach with mitigation strategies."

        # Save the strategy
        import asyncio
        result = asyncio.run(save_strategy_report(
            "Business expansion risk assessment",
            strategy,
            mock_context
        ))

        assert result["status"] == "success"
        assert len(mock_context.saved_reports) == 1
        assert strategy in mock_context.saved_reports[0]["content"]

    def test_complete_business_analysis_workflow(self):
        """測試完整的業務分析工作流程：市場 → ROI → 風險 → 策略"""
        mock_context = MagicMock()
        mock_context.saved_reports = []

        # Step 1: Market analysis
        market_result = analyze_market("finance", "Asia", mock_context)
        assert market_result["status"] == "success"

        # Step 2: ROI calculation based on market data
        growth_rate = float(market_result["analysis"]["growth_rate"].strip('%'))
        roi_result = calculate_roi(500000, growth_rate, 3, mock_context)
        assert roi_result["status"] == "success"

        # Step 3: Risk assessment
        risk_factors = ["competition", "regulatory_changes", "market_volatility"]
        risk_result = assess_risk(risk_factors, mock_context)
        assert risk_result["status"] == "success"

        # Step 4: Generate comprehensive strategy
        strategy = f"""
Market Analysis: {market_result["analysis"]["growth_rate"]} growth, {market_result["analysis"]["competition"]} competition
Financial Projection: {roi_result["calculation"]["roi_percentage"]:.1f}% ROI over 3 years
Risk Assessment: {risk_result["assessment"]["risk_level"]} risk ({risk_result["assessment"]["average_score"]:.1f}/10)

Recommendation: {'Proceed with caution' if risk_result["assessment"]["average_score"] > 6 else 'Proceed with standard due diligence'}
        """.strip()

        # Step 5: Save strategy report
        import asyncio
        save_result = asyncio.run(save_strategy_report(
            "Comprehensive business analysis for Asian market entry",
            strategy,
            mock_context
        ))

        assert save_result["status"] == "success"
        saved_content = mock_context.saved_reports[0]["content"]

        # Verify all components are in the saved report
        assert "Market Analysis:" in saved_content
        assert "Financial Projection:" in saved_content
        assert "Risk Assessment:" in saved_content
        assert "Recommendation:" in saved_content


class TestErrorHandlingIntegration:
    """跨工具錯誤處理的整合測試"""

    def test_tool_error_does_not_break_workflow(self):
        """測試工具錯誤不會中斷整體工作流程"""
        # Test with invalid inputs that should cause errors
        mock_context = MagicMock()

        # ROI with invalid inputs
        roi_result = calculate_roi(-1000, 10, 5, mock_context)
        assert roi_result["status"] == "error"

        # Risk assessment with empty list
        risk_result = assess_risk([], mock_context)
        assert risk_result["status"] == "success"  # Empty list is handled gracefully

        # Market analysis should still work
        market_result = analyze_market("retail", "Europe", mock_context)
        assert market_result["status"] == "success"

    def test_partial_failure_handling(self):
        """測試多步驟工作流程中部分失敗的處理"""
        mock_context = MagicMock()
        mock_context.saved_reports = []

        # Simulate a workflow where some steps succeed and some fail
        results = []

        # Successful market analysis
        market_result = analyze_market("healthcare", "Global", mock_context)
        results.append(("market", market_result["status"]))

        # Failed ROI calculation (invalid input)
        roi_result = calculate_roi(0, 10, 5, mock_context)  # Zero investment
        results.append(("roi", roi_result["status"]))

        # Successful risk assessment
        risk_result = assess_risk(["competition"], mock_context)
        results.append(("risk", risk_result["status"]))

        # Strategy should still be savable even with mixed results
        strategy = f"Analysis results: Market={results[0][1]}, ROI={results[1][1]}, Risk={results[2][1]}"

        import asyncio
        save_result = asyncio.run(save_strategy_report(
            "Partial analysis workflow",
            strategy,
            mock_context
        ))

        assert save_result["status"] == "success"
        assert "Market=success" in strategy
        assert "ROI=error" in strategy
        assert "Risk=success" in strategy


class TestPlannerComparison:
    """不同規劃器的整合比較測試"""

    def test_planner_instruction_differences(self):
        """測試不同規劃器之間的指令差異"""
        builtin_instruction = builtin_planner_agent.instruction
        plan_react_instruction = plan_react_agent.instruction
        strategic_instruction = strategic_planner_agent.instruction

        # Instructions should be different
        assert builtin_instruction != plan_react_instruction
        assert builtin_instruction != strategic_instruction
        assert plan_react_instruction != strategic_instruction

        # Each should have unique characteristics
        assert "thinks deeply" in builtin_instruction.lower()
        assert "planning tags" in plan_react_instruction.lower()
        assert "analysis" in strategic_instruction.lower()

    def test_planner_temperature_settings(self):
        """測試規劃器是否具備適當的溫度設定"""
        # BuiltInPlanner and StrategicPlanner should have lower temperature for consistency
        assert builtin_planner_agent.generate_content_config.temperature == 0.3
        assert strategic_planner_agent.generate_content_config.temperature == 0.3

        # PlanReActPlanner can have slightly higher temperature for creative planning
        assert plan_react_agent.generate_content_config.temperature == 0.4

    def test_planner_output_keys(self):
        """測試規劃器是否具備唯一的輸出鍵"""
        output_keys = [
            builtin_planner_agent.output_key,
            plan_react_agent.output_key,
            strategic_planner_agent.output_key
        ]

        # All output keys should be unique
        assert len(set(output_keys)) == len(output_keys)

        # All should contain relevant keywords
        assert all("strategy" in key or "result" in key for key in output_keys)

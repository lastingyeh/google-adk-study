"""
Agent 配置與功能測試
"""


class TestAgentConfiguration:
    """測試 Agent 配置與屬性。"""

    def test_root_agent_exists(self):
        """測試 root_agent 是否已正確定義。"""
        from app import root_agent

        assert root_agent is not None

    def test_agent_has_correct_name(self):
        """測試 Agent 是否擁有正確名稱。"""
        from app import root_agent

        assert root_agent.name == "interactive_planner_agent"

    def test_agent_has_correct_model(self):
        """測試 Agent 是否使用正確的模型。"""
        from app import root_agent

        assert root_agent.model == "gemini-3-pro-preview"

    def test_agent_has_description(self):
        """測試 Agent 是否擁有描述。"""
        from app import root_agent

        assert root_agent.description is not None
        assert len(root_agent.description) > 0

    def test_agent_has_instruction(self):
        """測試 Agent 是否擁有指令。"""
        from app import root_agent

        assert root_agent.instruction is not None
        assert len(root_agent.instruction) > 0

    def test_agent_has_sub_agents(self):
        """測試 Agent 是否已配置子 Agent。"""
        from app import root_agent

        assert hasattr(root_agent, "sub_agents")
        assert root_agent.sub_agents is not None

    def test_agent_has_tools(self):
        """測試 Agent 是否已配置工具。"""
        from app import root_agent

        assert hasattr(root_agent, "tools")
        assert root_agent.tools is not None


class TestSubAgents:
    """測試個別子 Agent 配置。"""

    def test_plan_generator_agent(self):
        """測試 plan_generator Agent。"""
        from app.agent import plan_generator

        assert plan_generator is not None
        assert plan_generator.name == "plan_generator"
        assert plan_generator.model == "gemini-3-pro-preview"
        assert len(plan_generator.tools) > 0

    def test_section_planner_agent(self):
        """測試 section_planner Agent。"""
        from app.agent import section_planner

        assert section_planner is not None
        assert section_planner.name == "section_planner"
        assert section_planner.output_key == "report_sections"

    def test_section_researcher_agent(self):
        """測試 section_researcher Agent。"""
        from app.agent import section_researcher

        assert section_researcher is not None
        assert section_researcher.name == "section_researcher"
        assert section_researcher.output_key == "section_research_findings"
        assert len(section_researcher.tools) > 0

    def test_research_evaluator_agent(self):
        """測試 research_evaluator Agent。"""
        from app.agent import research_evaluator

        assert research_evaluator is not None
        assert research_evaluator.name == "research_evaluator"
        assert research_evaluator.output_key == "research_evaluation"

    def test_enhanced_search_executor_agent(self):
        """測試 enhanced_search_executor Agent。"""
        from app.agent import enhanced_search_executor

        assert enhanced_search_executor is not None
        assert enhanced_search_executor.name == "enhanced_search_executor"
        assert len(enhanced_search_executor.tools) > 0

    def test_report_composer_agent(self):
        """測試 report_composer Agent。"""
        from app.agent import report_composer

        assert report_composer is not None
        assert report_composer.name == "report_composer_with_citations"
        assert report_composer.output_key == "final_cited_report"

    def test_research_pipeline_agent(self):
        """測試 research_pipeline Agent。"""
        from app.agent import research_pipeline

        assert research_pipeline is not None
        assert research_pipeline.name == "research_pipeline"
        assert hasattr(research_pipeline, "sub_agents")
        assert len(research_pipeline.sub_agents) > 0


class TestCustomAgents:
    """測試自訂 Agent 類別。"""

    def test_escalation_checker_class(self):
        """測試 EscalationChecker 類別定義。"""
        from app.agent import EscalationChecker

        assert EscalationChecker is not None

    def test_escalation_checker_instantiation(self):
        """測試 EscalationChecker 能被實例化。"""
        from app.agent import EscalationChecker

        checker = EscalationChecker(name="test_checker")
        assert checker is not None
        assert checker.name == "test_checker"

    def test_escalation_checker_has_run_method(self):
        """測試 EscalationChecker 擁有執行方法。"""
        from app.agent import EscalationChecker

        checker = EscalationChecker(name="test_checker")
        assert hasattr(checker, "_run_async_impl")
        assert callable(checker._run_async_impl)


class TestAgentCallbacks:
    """測試 Agent 回調函式。"""

    def test_collect_research_sources_callback_exists(self):
        """測試研究來源收集回調存在。"""
        from app.agent import collect_research_sources_callback

        assert callable(collect_research_sources_callback)

    def test_citation_replacement_callback_exists(self):
        """測試引用替換回調存在。"""
        from app.agent import citation_replacement_callback

        assert callable(citation_replacement_callback)

    def test_section_researcher_has_callback(self):
        """測試 section_researcher 擁有回調配置。"""
        from app.agent import section_researcher

        assert hasattr(section_researcher, "after_agent_callback")
        assert section_researcher.after_agent_callback is not None

    def test_enhanced_search_executor_has_callback(self):
        """測試 enhanced_search_executor 擁有回調配置。"""
        from app.agent import enhanced_search_executor

        assert hasattr(enhanced_search_executor, "after_agent_callback")
        assert enhanced_search_executor.after_agent_callback is not None

    def test_report_composer_has_callback(self):
        """測試 report_composer 擁有回調配置。"""
        from app.agent import report_composer

        assert hasattr(report_composer, "after_agent_callback")
        assert report_composer.after_agent_callback is not None


class TestAgentTools:
    """測試 Agent 工具配置。"""

    def test_plan_generator_has_google_search(self):
        """測試 plan_generator 擁有 google_search 工具。"""
        from app.agent import plan_generator

        assert len(plan_generator.tools) > 0
        # 檢查工具名稱或類型
        tool_names = [str(tool) for tool in plan_generator.tools]
        assert any("google_search" in str(tool) for tool in tool_names)

    def test_section_researcher_has_google_search(self):
        """測試 section_researcher 擁有 google_search 工具。"""
        from app.agent import section_researcher

        assert len(section_researcher.tools) > 0

    def test_enhanced_search_executor_has_google_search(self):
        """測試 enhanced_search_executor 擁有 google_search 工具。"""
        from app.agent import enhanced_search_executor

        assert len(enhanced_search_executor.tools) > 0

    def test_interactive_planner_has_agent_tool(self):
        """測試 interactive_planner_agent 擁有 AgentTool。"""
        from app import root_agent

        assert len(root_agent.tools) > 0


class TestAgentOutputKeys:
    """測試 Agent 輸出鍵配置。"""

    def test_section_planner_output_key(self):
        """測試 section_planner 輸出鍵。"""
        from app.agent import section_planner

        assert section_planner.output_key == "report_sections"

    def test_section_researcher_output_key(self):
        """測試 section_researcher 輸出鍵。"""
        from app.agent import section_researcher

        assert section_researcher.output_key == "section_research_findings"

    def test_research_evaluator_output_key(self):
        """測試 research_evaluator 輸出鍵。"""
        from app.agent import research_evaluator

        assert research_evaluator.output_key == "research_evaluation"

    def test_report_composer_output_key(self):
        """測試 report_composer 輸出鍵。"""
        from app.agent import report_composer

        assert report_composer.output_key == "final_cited_report"

    def test_interactive_planner_output_key(self):
        """測試 interactive_planner_agent 輸出鍵。"""
        from app import root_agent

        assert root_agent.output_key == "research_plan"


class TestAgentHierarchy:
    """測試 Agent 層級結構。"""

    def test_root_agent_is_interactive_planner(self):
        """測試 root_agent 是 interactive_planner_agent。"""
        from app import root_agent
        from app.agent import interactive_planner_agent

        assert root_agent == interactive_planner_agent

    def test_research_pipeline_structure(self):
        """測試 research_pipeline 結構。"""
        from app.agent import research_pipeline

        assert hasattr(research_pipeline, "sub_agents")
        assert len(research_pipeline.sub_agents) == 4

    def test_interactive_planner_has_research_pipeline(self):
        """測試 interactive_planner 包含 research_pipeline。"""
        from app import root_agent

        assert hasattr(root_agent, "sub_agents")
        assert len(root_agent.sub_agents) > 0

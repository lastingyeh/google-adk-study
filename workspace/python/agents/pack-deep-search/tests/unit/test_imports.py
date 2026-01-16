"""
匯入與結構驗證測試
"""


class TestImports:
    """測試所有模組是否能成功匯入。"""

    def test_import_agent_module(self):
        """測試 Agent 模組是否能被匯入。"""
        from app import agent

        assert agent is not None

    def test_import_root_agent(self):
        """測試 root_agent 是否能從模組中匯入。"""
        from app import root_agent

        assert root_agent is not None

    def test_import_from_package(self):
        """測試 root_agent 是否能從套件中匯入。"""
        from app import root_agent

        assert hasattr(root_agent, "name")
        assert hasattr(root_agent, "model")

    def test_import_config(self):
        """測試 config 模組是否能被匯入。"""
        from app.config import config

        assert config is not None

    def test_import_pydantic_models(self):
        """測試 Pydantic 模型是否能被匯入。"""
        from app.agent import Feedback, SearchQuery

        assert Feedback is not None
        assert SearchQuery is not None

    def test_callback_functions_exist(self):
        """測試所有回調函式是否存在且可被呼叫。"""
        from app.agent import (
            citation_replacement_callback,
            collect_research_sources_callback,
        )

        assert callable(collect_research_sources_callback)
        assert callable(citation_replacement_callback)

    def test_agent_has_required_attributes(self):
        """測試 Agent 是否擁有必要的屬性。"""
        from app import root_agent

        assert hasattr(root_agent, "name")
        assert hasattr(root_agent, "model")
        assert hasattr(root_agent, "description")
        assert hasattr(root_agent, "instruction")

    def test_custom_agent_class_exists(self):
        """測試自訂 Agent 類別是否存在。"""
        from app.agent import EscalationChecker

        assert EscalationChecker is not None
        assert callable(EscalationChecker)

    def test_all_agents_exist(self):
        """測試所有子 Agent 是否能被匯入。"""
        from app.agent import (
            enhanced_search_executor,
            interactive_planner_agent,
            plan_generator,
            report_composer,
            research_evaluator,
            research_pipeline,
            section_planner,
            section_researcher,
        )

        agents = [
            plan_generator,
            section_planner,
            section_researcher,
            research_evaluator,
            enhanced_search_executor,
            report_composer,
            research_pipeline,
            interactive_planner_agent,
        ]

        for agent in agents:
            assert agent is not None
            assert hasattr(agent, "name")

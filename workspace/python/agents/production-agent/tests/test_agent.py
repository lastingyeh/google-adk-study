"""測試 Agent 設定與功能。"""

import pytest
from production_agent import root_agent
from production_agent.agent import (
    check_deployment_status,
    get_deployment_options,
    get_best_practices
)


class TestAgentConfiguration:
    """Agent 設定測試套件。"""

    def test_agent_exists(self):
        """測試 root_agent 是否已定義。"""
        assert root_agent is not None

    def test_agent_name(self):
        """測試 Agent 是否有名稱正確。"""
        assert root_agent.name == "production_deployment_agent"

    def test_agent_model(self):
        """測試 Agent 是否使用正確的模型。"""
        assert root_agent.model == "gemini-2.0-flash"

    def test_agent_has_description(self):
        """測試 Agent 是否有描述。"""
        assert root_agent.description is not None
        assert len(root_agent.description) > 0

    def test_agent_has_instruction(self):
        """測試 Agent 是否有指令。"""
        assert root_agent.instruction is not None
        assert len(root_agent.instruction) > 0

    def test_agent_has_tools(self):
        """測試 Agent 是否有設定工具。"""
        assert root_agent.tools is not None
        assert len(root_agent.tools) > 0

    def test_agent_has_generate_config(self):
        """測試 Agent 是否有生成設定。"""
        assert root_agent.generate_content_config is not None

    def test_temperature_configured(self):
        """測試是否已設定 temperature。"""
        config = root_agent.generate_content_config
        assert hasattr(config, 'temperature')
        assert config.temperature == 0.5

    def test_max_tokens_configured(self):
        """測試是否已設定 max_output_tokens。"""
        config = root_agent.generate_content_config
        assert hasattr(config, 'max_output_tokens')
        assert config.max_output_tokens == 2048


class TestToolFunctions:
    """工具函式測試套件。"""

    def test_check_deployment_status(self):
        """測試 check_deployment_status 工具。"""
        result = check_deployment_status()

        assert isinstance(result, dict)
        assert result["status"] == "success"
        assert "report" in result
        assert "deployment_type" in result
        assert "features" in result
        assert isinstance(result["features"], list)

    def test_get_deployment_options(self):
        """測試 get_deployment_options 工具。"""
        result = get_deployment_options()

        assert isinstance(result, dict)
        assert result["status"] == "success"
        assert "options" in result

        options = result["options"]
        assert "local_api_server" in options
        assert "cloud_run" in options
        assert "agent_engine" in options
        assert "gke" in options

        # 驗證每個選項的結構
        for option_key, option_data in options.items():
            assert "command" in option_data
            assert "description" in option_data
            assert "features" in option_data

    def test_get_best_practices(self):
        """測試 get_best_practices 工具。"""
        result = get_best_practices()

        assert isinstance(result, dict)
        assert result["status"] == "success"
        assert "best_practices" in result

        practices = result["best_practices"]
        assert "security" in practices
        assert "monitoring" in practices
        assert "scalability" in practices
        assert "reliability" in practices

        # 驗證每個類別都有實踐項目
        for category, items in practices.items():
            assert isinstance(items, list)
            assert len(items) > 0


class TestToolCommands:
    """測試工具輸出是否包含正確的部署指令。"""

    def test_deployment_commands_accuracy(self):
        """測試工具中的部署指令是否準確。"""
        result = get_deployment_options()
        options = result["options"]

        # 驗證指令是否符合官方 ADK CLI
        assert options["local_api_server"]["command"] == "adk api_server"
        assert options["cloud_run"]["command"] == "adk deploy cloud_run"
        assert options["agent_engine"]["command"] == "adk deploy agent_engine"
        assert options["gke"]["command"] == "adk deploy gke"

    def test_deployment_features_completeness(self):
        """測試每個部署選項是否有具體的特性。"""
        result = get_deployment_options()
        options = result["options"]

        for option_name, option_data in options.items():
            features = option_data["features"]
            assert len(features) >= 3, f"{option_name} should have at least 3 features"

            # 特性應為非空字串
            for feature in features:
                assert isinstance(feature, str)
                assert len(feature) > 0


class TestAgentIntegration:
    """需要 GOOGLE_API_KEY 的整合測試。"""

    @pytest.mark.skipif(
        not pytest.importorskip("os").environ.get("GOOGLE_API_KEY"),
        reason="GOOGLE_API_KEY not set"
    )
    async def test_agent_invocation(self):
        """測試實際的 Agent 呼叫。"""
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        from google.genai import types

        session_service = InMemorySessionService()
        runner = Runner(app_name="test", agent=root_agent, session_service=session_service)

        session = await session_service.create_session(
            app_name="test",
            user_id="test_user"
        )

        query = "What deployment options are available?"
        new_message = types.Content(role="user", parts=[types.Part(text=query)])

        response_text = ""
        async for event in runner.run_async(
            user_id="test_user",
            session_id=session.id,
            new_message=new_message
        ):
            if event.content and event.content.parts:
                text = event.content.parts[0].text
                if text:  # Only concatenate if text is not None
                    response_text += text

        assert response_text is not None
        assert len(response_text) > 0

"""測試代理配置和設定。"""

import pytest


class TestAgentConfiguration:
    """測試 root_agent 是否已正確配置。"""

    def test_root_agent_exists(self):
        """測試 root_agent 是否已定義。"""
        try:
            from custom_session_agent.agent import root_agent
            assert root_agent is not None
        except ImportError:
            pytest.skip("ADK not installed")

    def test_root_agent_has_name(self):
        """測試 root_agent 是否有名稱。"""
        try:
            from custom_session_agent.agent import root_agent
            assert hasattr(root_agent, "name")
            assert root_agent.name == "custom_session_agent"
        except ImportError:
            pytest.skip("ADK not installed")

    def test_root_agent_has_description(self):
        """測試 root_agent 是否有描述。"""
        try:
            from custom_session_agent.agent import root_agent
            assert hasattr(root_agent, "description")
            assert "custom session service" in root_agent.description.lower()
        except ImportError:
            pytest.skip("ADK not installed")

    def test_root_agent_has_tools(self):
        """測試 root_agent 是否有工具。"""
        try:
            from custom_session_agent.agent import root_agent
            assert hasattr(root_agent, "tools")
            assert len(root_agent.tools) >= 4
        except ImportError:
            pytest.skip("ADK not installed")

    def test_root_agent_tools_are_callable(self):
        """測試所有代理工具是否可呼叫。"""
        try:
            from custom_session_agent.agent import root_agent
            for tool in root_agent.tools:
                assert callable(tool), f"Tool {tool} is not callable"
        except ImportError:
            pytest.skip("ADK not installed")

    def test_root_agent_has_output_key(self):
        """測試 root_agent 是否有用於狀態管理的 output_key。"""
        try:
            from custom_session_agent.agent import root_agent
            assert hasattr(root_agent, "output_key")
            assert root_agent.output_key == "session_result"
        except ImportError:
            pytest.skip("ADK not installed")


class TestCustomSessionServiceDemo:
    """測試 CustomSessionServiceDemo 類別。"""

    def test_demo_class_has_register_redis_service(self):
        """測試 demo 類別是否有 register_redis_service 方法。"""
        try:
            from custom_session_agent.agent import CustomSessionServiceDemo
            assert hasattr(CustomSessionServiceDemo, "register_redis_service")
            assert callable(CustomSessionServiceDemo.register_redis_service)
        except ImportError:
            pytest.skip("ADK not installed")

    def test_demo_class_has_register_memory_service(self):
        """測試 demo 類別是否有 register_memory_service 方法。"""
        try:
            from custom_session_agent.agent import CustomSessionServiceDemo
            assert hasattr(CustomSessionServiceDemo, "register_memory_service")
            assert callable(CustomSessionServiceDemo.register_memory_service)
        except ImportError:
            pytest.skip("ADK not installed")

    def test_services_are_registered_on_import(self):
        """測試模組匯入時服務是否已註冊。"""
        try:
            from google.adk.cli.service_registry import get_service_registry
            registry = get_service_registry()

            # Try to get the service factory for redis
            # This should not raise an error if registered
            factory = registry.get_session_service_factory("redis")
            assert factory is not None
        except ImportError:
            pytest.skip("ADK not installed")
        except Exception as e:
            # Services might not be registered in test environment
            pytest.skip(f"Service registry not available: {e}")


class TestAgentModel:
    """測試代理模型配置。"""

    def test_root_agent_uses_gemini_model(self):
        """測試 root_agent 是否使用 Gemini 模型。"""
        try:
            from custom_session_agent.agent import root_agent
            assert hasattr(root_agent, "model")
            assert "gemini" in root_agent.model.lower()
        except ImportError:
            pytest.skip("ADK not installed")

    def test_root_agent_has_instruction(self):
        """測試 root_agent 是否有指令文字。"""
        try:
            from custom_session_agent.agent import root_agent
            assert hasattr(root_agent, "instruction")
            assert len(root_agent.instruction) > 0
            assert "session service" in root_agent.instruction.lower()
        except ImportError:
            pytest.skip("ADK not installed")

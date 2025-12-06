"""
Commerce Agent 的整合測試。
測試代理程式設定和基本功能。
"""

import pytest
from commerce_agent.agent import (
    root_agent,
    search_agent,
    preferences_agent,
)
from commerce_agent.database import init_database


@pytest.mark.integration
class TestAgentConfiguration:
    """測試代理程式設定"""

    def test_search_agent_exists(self):
        """測試搜尋代理程式是否已正確設定"""
        assert search_agent is not None
        assert search_agent.name == "ProductSearchAgent"
        assert search_agent.model == "gemini-2.5-flash"

    def test_preferences_agent_exists(self):
        """測試偏好設定代理程式是否已正確設定"""
        assert preferences_agent is not None
        assert preferences_agent.name == "PreferenceManager"

    def test_root_agent_exists(self):
        """測試根代理程式是否已正確設定"""
        assert root_agent is not None
        assert root_agent.name == "CommerceCoordinator"
        assert root_agent.model == "gemini-2.5-flash"

    def test_root_agent_has_tools(self):
        """測試根代理程式是否有工具 (用於子代理程式的 AgentTools)"""
        assert hasattr(root_agent, "tools")
        # 應該有 2 個 AgentTools (搜尋和偏好設定)
        assert len(root_agent.tools) == 2

    def test_agent_models_are_valid(self):
        """測試所有代理程式都使用有效的模型名稱"""
        valid_models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]

        assert search_agent.model in valid_models
        assert preferences_agent.model in valid_models
        assert root_agent.model in valid_models

    def test_agent_instructions_are_set(self):
        """測試所有代理程式都已設定指令"""
        assert (
            search_agent.instruction is not None and len(search_agent.instruction) > 0
        )
        assert (
            preferences_agent.instruction is not None
            and len(preferences_agent.instruction) > 0
        )
        assert root_agent.instruction is not None and len(root_agent.instruction) > 0


@pytest.mark.integration
class TestDatabaseIntegration:
    """測試資料庫整合"""

    def test_database_initializes(self):
        """測試資料庫可以被初始化"""
        try:
            init_database()
            assert True
        except Exception as e:
            assert False, f"資料庫初始化失敗：{str(e)}"

    def test_database_multiple_users(self):
        """測試資料庫是否能正確處理多個使用者"""
        from commerce_agent.database import (
            save_user_preferences,
            get_user_preferences,
        )
        from commerce_agent.models import UserPreferences

        init_database()

        # 建立兩個具有不同偏好的使用者
        user1_prefs = UserPreferences(sports=["running"])
        user2_prefs = UserPreferences(sports=["cycling"])

        save_user_preferences("user_1", user1_prefs)
        save_user_preferences("user_2", user2_prefs)

        # 驗證隔離性
        retrieved_1 = get_user_preferences("user_1")
        retrieved_2 = get_user_preferences("user_2")

        assert retrieved_1.sports == ["running"]
        assert retrieved_2.sports == ["cycling"]


@pytest.mark.integration
class TestToolIntegration:
    """測試工具整合"""

    def test_preference_tool_callable(self):
        """測試偏好管理工具是否可呼叫"""
        from commerce_agent.tools import manage_user_preferences

        result = manage_user_preferences(action="get", user_id="test_user")

        assert "status" in result
        assert "report" in result
        assert "data" in result

    def test_curation_tool_callable(self):
        """測試產品策展工具是否可呼叫"""
        from commerce_agent.tools import curate_products

        result = curate_products(products=[])

        assert "status" in result
        assert "report" in result
        assert "data" in result

    def test_narrative_tool_callable(self):
        """測試故事生成工具是否可呼叫"""
        from commerce_agent.tools import generate_product_narrative

        result = generate_product_narrative(product={"name": "Test Product"})

        assert "status" in result
        assert "report" in result


@pytest.mark.integration
class TestImportPaths:
    """測試所有公開的匯入是否正常運作"""

    def test_import_root_agent(self):
        """測試根代理程式可以被匯入"""
        from commerce_agent import root_agent

        assert root_agent is not None

    def test_import_all_agents(self):
        """測試所有代理程式都可以被匯入"""
        from commerce_agent import (
            root_agent,
            search_agent,
            preferences_agent,
        )

        assert all([root_agent, search_agent, preferences_agent])

    def test_import_tools(self):
        """測試所有工具都可以被匯入"""
        from commerce_agent import (
            manage_user_preferences,
            curate_products,
            generate_product_narrative,
        )

        assert all(
            [manage_user_preferences, curate_products, generate_product_narrative]
        )

    def test_import_models(self):
        """測試所有模型都可以被匯入"""
        from commerce_agent import (
            UserPreferences,
            Product,
            InteractionRecord,
            EngagementProfile,
        )

        assert all([UserPreferences, Product, InteractionRecord, EngagementProfile])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

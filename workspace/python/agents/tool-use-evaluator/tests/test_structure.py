"""測試應用程式設定。

此模組包含針對 ADK 應用程式層級的設定測試。
"""


class TestAppConfiguration:
    """測試 ADK 應用程式設定。

    驗證應用程式物件的建立及其關鍵屬性，如名稱與根 Agent 的整合。
    """

    def test_app_creation(self):
        """測試應用程式是否正確建立。

        驗證 app 物件是否存在，且應用程式名稱為 "tool_use_quality_app"。
        """
        from app import app
        assert app
        assert app.name == "tool_use_quality_app"

    def test_app_has_root_agent(self):
        """測試應用程式是否配置了根 Agent。

        驗證 app.root_agent 是否存在，且其名稱為 "tool_use_evaluator"。
        """
        from app import app
        assert app.root_agent
        assert app.root_agent.name == "tool_use_evaluator"

    def test_app_root_agent_has_tools(self):
        """測試應用程式的根 Agent 是否配置了工具。

        驗證 root_agent 是否配置了正確數量的工具 (4個)，並包含 "analyze_data" 工具。
        """
        from app import app
        tools = app.root_agent.tools
        assert len(tools) == 4
        tool_names = [t.__name__ for t in tools]
        assert "analyze_data" in tool_names

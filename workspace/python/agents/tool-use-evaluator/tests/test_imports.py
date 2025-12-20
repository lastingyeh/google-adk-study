"""測試匯入與模組結構。

此模組包含針對專案匯入機制與模組結構的完整性測試。
"""


class TestImports:
    """測試模組匯入與導出。

    驗證關鍵組件能否被正確匯入，確保依賴關係與命名空間設定正確。
    """

    def test_import_agent_from_module(self):
        """測試從 tool_use_evaluator 模組匯入 root_agent。

        驗證是否能直接從頂層模組匯入 root_agent，且其名稱正確。
        """
        from tool_use_evaluator import root_agent
        assert root_agent
        assert root_agent.name == "tool_use_evaluator"

    def test_import_app(self):
        """測試從 app 模組匯入 app 物件。

        驗證應用程式入口點 app 是否存在，且其名稱為 "tool_use_quality_app"。
        """
        from app import app
        assert app
        assert app.name == "tool_use_quality_app"

    def test_agent_has_root_agent_export(self):
        """測試 agent 模組是否導出 root_agent。

        驗證 tool_use_evaluator.agent 子模組是否正確導出 root_agent 物件。
        """
        from tool_use_evaluator.agent import root_agent as agent
        assert agent is not None
        assert hasattr(agent, "name")
        assert hasattr(agent, "tools")


class TestModuleStructure:
    """測試模組結構與組織。

    驗證套件的內部結構與導出成員是否符合設計預期。
    """

    def test_package_init_exports(self):
        """測試 __init__.py 是否導出 root_agent。

        確保套件初始化文件正確暴露了 root_agent，方便使用者匯入。
        """
        from tool_use_evaluator import root_agent
        assert root_agent.name == "tool_use_evaluator"

    def test_tool_use_evaluator_module_exists(self):
        """測試 tool_use_evaluator 模組結構是否正確。

        驗證 tool_use_evaluator 模組本身是否存在，且包含 root_agent 屬性。
        """
        import tool_use_evaluator
        assert hasattr(tool_use_evaluator, "root_agent")

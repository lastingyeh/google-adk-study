"""
測試專案結構與匯入。
"""


class TestImports:
    """測試所有模組是否都能被匯入。"""

    def test_import_agent_module(self):
        """測試匯入 agent 模組。"""
        from gepa_agent import agent  # noqa: F401

    def test_import_root_agent(self):
        """測試匯入 root_agent。"""
        from gepa_agent.agent import root_agent  # noqa: F401

        assert root_agent is not None

    def test_import_create_support_agent(self):
        """測試匯入 create_support_agent 函式。"""
        from gepa_agent.agent import create_support_agent  # noqa: F401

    def test_import_tools(self):
        """測試匯入工具類別。"""
        from gepa_agent.agent import (  # noqa: F401
            VerifyCustomerIdentity,
            CheckReturnPolicy,
            ProcessRefund,
        )

    def test_import_constants(self):
        """測試匯入常數。"""
        from gepa_agent.agent import INITIAL_PROMPT  # noqa: F401

        assert INITIAL_PROMPT is not None


class TestProjectStructure:
    """測試專案結構與組織。"""

    def test_gepa_agent_package_exists(self):
        """測試 gepa_agent 套件是否存在。"""
        import gepa_agent  # noqa: F401

    def test_gepa_agent_has_init(self):
        """測試 gepa_agent 是否有 __init__.py。"""
        from gepa_agent import __all__, __version__  # noqa: F401

        assert __all__ is not None
        assert __version__ is not None

    def test_agent_py_exists(self):
        """測試 agent.py 是否存在於套件中。"""
        from gepa_agent import agent  # noqa: F401

        assert hasattr(agent, "root_agent")
        assert hasattr(agent, "create_support_agent")

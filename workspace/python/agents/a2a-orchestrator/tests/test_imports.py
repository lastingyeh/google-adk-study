"""
測試套件匯入

**重點說明：**
- 測試 Agent 套件及其元件的匯入功能。
- 確保 `root_agent`、`agent` 模組及工具可以被正確匯入。
"""


class TestImports:
    """測試套件是否可以被正確匯入。"""

    def test_import_root_agent(self):
        """測試 `root_agent` 是否可以從套件中匯入。"""
        try:
            from a2a_orchestrator import root_agent

            assert root_agent is not None
        except ImportError as e:
            assert False, f"Failed to import root_agent: {e}"

    def test_import_agent_module(self):
        """測試 `agent` 模組是否可以被匯入。"""
        try:
            from a2a_orchestrator import agent

            assert agent.root_agent is not None
        except ImportError as e:
            assert False, f"Failed to import agent module: {e}"

    def test_import_tools(self):
        """測試工具是否可以被匯入。"""
        try:
            from a2a_orchestrator.agent import (
                check_agent_availability, log_coordination_step)

            assert check_agent_availability is not None
            assert log_coordination_step is not None
        except ImportError as e:
            assert False, f"Failed to import tools: {e}"

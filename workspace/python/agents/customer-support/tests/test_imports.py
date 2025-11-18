# 教程 20：YAML 設定 - 匯入測試
# 驗證所有模組能否正確匯入

import pytest


class TestImports:
    """測試所有模組是否能被匯入。"""

    def test_tools_import(self):
        """測試 tools 套件是否能被匯入。"""
        try:
            from customer_support import tools
            assert tools is not None
        except ImportError as e:
            pytest.fail(f"匯入 tools 套件失敗：{e}")

    def test_customer_tools_import(self):
        """測試 customer_tools 模組是否能被匯入。"""
        try:
            from customer_support.tools import customer_tools
            assert customer_tools is not None
        except ImportError as e:
            pytest.fail(f"匯入 customer_tools 失敗：{e}")

    def test_all_tool_functions_importable(self):
        """測試所有工具函式是否能被匯入。"""
        try:
            from customer_support.tools.customer_tools import (
                check_customer_status,
                log_interaction,
                get_order_status,
                track_shipment,
                cancel_order,
                search_knowledge_base,
                run_diagnostic,
                create_ticket,
                get_billing_history,
                process_refund,
                update_payment_method,
            )
            # 如果執行到此處，表示所有匯入皆成功
            assert True
        except ImportError as e:
            pytest.fail(f"匯入工具函式失敗：{e}")

    def test_adk_config_utils_import(self):
        """測試 ADK 設定工具是否能被匯入。"""
        try:
            from google.adk.agents import config_agent_utils
            assert config_agent_utils is not None
        except ImportError as e:
            pytest.fail(f"匯入 config_agent_utils 失敗：{e}")

    def test_run_agent_import(self):
        """測試 run_agent 腳本是否能被匯入。"""
        try:
            import run_agent
            assert run_agent is not None
        except ImportError as e:
            pytest.fail(f"匯入 run_agent 失敗：{e}")


class TestToolFunctionSignatures:
    """測試工具函式是否具有正確的簽章。"""

    def test_tool_functions_are_callable(self):
        """測試匯入的工具函式是否可呼叫。"""
        from customer_support.tools.customer_tools import check_customer_status

        assert callable(check_customer_status)

    def test_tool_function_returns_dict(self):
        """測試工具函式是否回傳字典。"""
        from customer_support.tools.customer_tools import check_customer_status

        result = check_customer_status('test')
        assert isinstance(result, dict)

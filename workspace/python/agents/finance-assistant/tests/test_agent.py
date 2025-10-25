# -*- coding: utf-8 -*-
"""
代理配置和工具註冊的測試套件 - 教學 02：函式工具

測試財務助理代理的設定、工具註冊和基本功能。
"""

import pytest
from unittest.mock import patch
from finance_assistant.agent import (
    root_agent,
    calculate_compound_interest,
    calculate_loan_payment,
    calculate_monthly_savings,
)


class TestAgentConfiguration:
    """測試代理的配置和設定。"""

    def test_agent_creation(self):
        """測試代理是否成功建立。"""
        assert root_agent is not None
        assert root_agent.name == "finance_assistant"
        assert root_agent.model == "gemini-2.0-flash"

    def test_agent_description(self):
        """測試代理是否有適當的描述。"""
        description = root_agent.description
        assert "financial calculation assistant" in description.lower()
        assert "compound interest" in description.lower()
        assert "loan payment" in description.lower()
        assert "monthly savings" in description.lower()

    def test_agent_tools_registration(self):
        """測試所有三個工具是否都已註冊。"""
        tools = root_agent.tools
        assert len(tools) == 3

        tool_functions = [tool for tool in tools]
        assert calculate_compound_interest in tool_functions
        assert calculate_loan_payment in tool_functions
        assert calculate_monthly_savings in tool_functions


class TestToolFunctionSignatures:
    """測試工具函式的簽名和元數據。"""

    def test_compound_interest_signature(self):
        """測試 calculate_compound_interest 函式的簽名。"""
        assert callable(calculate_compound_interest)

        # 檢查函式是否有適當的說明文件
        assert calculate_compound_interest.__doc__ is not None
        assert "compound interest" in calculate_compound_interest.__doc__.lower()
        assert "Args:" in calculate_compound_interest.__doc__
        assert "Returns:" in calculate_compound_interest.__doc__

    def test_loan_payment_signature(self):
        """測試 calculate_loan_payment 函式的簽名。"""
        assert callable(calculate_loan_payment)

        # 檢查函式是否有適當的說明文件
        assert calculate_loan_payment.__doc__ is not None
        assert "loan payment" in calculate_loan_payment.__doc__.lower()
        assert "Args:" in calculate_loan_payment.__doc__
        assert "Returns:" in calculate_loan_payment.__doc__

    def test_monthly_savings_signature(self):
        """測試 calculate_monthly_savings 函式的簽名。"""
        assert callable(calculate_monthly_savings)

        # 檢查函式是否有適當的說明文件
        assert calculate_monthly_savings.__doc__ is not None
        assert "monthly savings" in calculate_monthly_savings.__doc__.lower()
        assert "Args:" in calculate_monthly_savings.__doc__
        assert "Returns:" in calculate_monthly_savings.__doc__

    def test_function_type_hints(self):
        """測試函式是否有適當的型別提示。"""
        import inspect

        # 檢查複利函式
        sig = inspect.signature(calculate_compound_interest)
        assert "principal" in sig.parameters
        assert "annual_rate" in sig.parameters
        assert "years" in sig.parameters
        assert "compounds_per_year" in sig.parameters

        # 檢查貸款支付函式
        sig = inspect.signature(calculate_loan_payment)
        assert "loan_amount" in sig.parameters
        assert "annual_rate" in sig.parameters
        assert "years" in sig.parameters

        # 檢查每月儲蓄函式
        sig = inspect.signature(calculate_monthly_savings)
        assert "target_amount" in sig.parameters
        assert "years" in sig.parameters
        assert "annual_return" in sig.parameters


class TestToolReturnFormats:
    """測試工具是否回傳格式正確的結果。"""

    def test_compound_interest_return_format(self):
        """測試 calculate_compound_interest 的回傳格式。"""
        result = calculate_compound_interest(1000, 0.05, 1)

        required_keys = ["status", "final_amount", "interest_earned", "report"]
        for key in required_keys:
            assert key in result

        assert result["status"] == "success"
        assert isinstance(result["final_amount"], (int, float))
        assert isinstance(result["interest_earned"], (int, float))
        assert isinstance(result["report"], str)

    def test_loan_payment_return_format(self):
        """測試 calculate_loan_payment 的回傳格式。"""
        result = calculate_loan_payment(100000, 0.05, 10)

        required_keys = [
            "status",
            "monthly_payment",
            "total_paid",
            "total_interest",
            "report",
        ]
        for key in required_keys:
            assert key in result

        assert result["status"] == "success"
        assert isinstance(result["monthly_payment"], (int, float))
        assert isinstance(result["total_paid"], (int, float))
        assert isinstance(result["total_interest"], (int, float))
        assert isinstance(result["report"], str)

    def test_monthly_savings_return_format(self):
        """測試 calculate_monthly_savings 的回傳格式。"""
        result = calculate_monthly_savings(10000, 2, 0.05)

        required_keys = [
            "status",
            "monthly_savings",
            "total_contributed",
            "interest_earned",
            "report",
        ]
        for key in required_keys:
            assert key in result

        assert result["status"] == "success"
        assert isinstance(result["monthly_savings"], (int, float))
        assert isinstance(result["total_contributed"], (int, float))
        assert isinstance(result["interest_earned"], (int, float))
        assert isinstance(result["report"], str)

    def test_error_return_format(self):
        """測試所有工具的錯誤回傳格式。"""
        # 測試複利錯誤
        result = calculate_compound_interest(-1000, 0.05, 1)
        assert result["status"] == "error"
        assert "error" in result
        assert "report" in result
        assert isinstance(result["report"], str)

        # 測試貸款支付錯誤
        result = calculate_loan_payment(100000, 0.05, 0)
        assert result["status"] == "error"
        assert "error" in result
        assert "report" in result

        # 測試每月儲蓄錯誤
        result = calculate_monthly_savings(10000, 0, 0.05)
        assert result["status"] == "error"
        assert "error" in result
        assert "report" in result


class TestAgentIntegration:
    """測試代理的整合與功能。"""

    @patch("google.adk.agents.Agent")
    def test_agent_initialization_mock(self, mock_agent_class):
        """使用模擬的 Agent 類別測試代理的初始化。"""
        # 如果我們想在沒有實際 ADK 的情況下測試代理的建立，就會使用這個方法
        # 目前，我們測試真實的代理是否存在且具有預期的屬性
        pass

    def test_agent_has_required_attributes(self):
        """測試代理是否具有 ADK 所需的所有屬性。"""
        # 檢查代理是否具有 ADK 預期的屬性
        assert hasattr(root_agent, "name")
        assert hasattr(root_agent, "model")
        assert hasattr(root_agent, "description")
        assert hasattr(root_agent, "tools")

    def test_tools_are_callable(self):
        """測試所有註冊的工具是否都可呼叫。"""
        for tool in root_agent.tools:
            assert callable(tool)

    def test_agent_can_be_imported(self):
        """測試代理是否可以成功匯入。"""
        # 此測試確保模組匯入時不會發生錯誤
        from finance_assistant.agent import root_agent as imported_agent

        assert imported_agent is not None
        assert imported_agent.name == "finance_assistant"


class TestProjectStructure:
    """測試專案結構和匯入。"""

    def test_imports_work(self):
        """測試所有匯入是否正常運作。"""
        import importlib.util

        try:
            # 檢查是否可以找到並載入模組
            spec = importlib.util.find_spec("finance_assistant.agent")
            assert spec is not None, "找不到 finance_assistant.agent 模組"

            # 嘗試載入模組
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            assert True
        except Exception as e:
            pytest.fail(f"匯入失敗: {e}")

    def test_module_structure(self):
        """測試模組是否具有預期的結構。"""
        import finance_assistant.agent

        # 檢查模組是否具有預期的屬性
        assert hasattr(finance_assistant.agent, "root_agent")
        assert hasattr(finance_assistant.agent, "calculate_compound_interest")
        assert hasattr(finance_assistant.agent, "calculate_loan_payment")
        assert hasattr(finance_assistant.agent, "calculate_monthly_savings")

    def test_main_execution(self):
        """測試主執行區段是否不會引發錯誤。"""
        # 匯入並執行主區段
        import subprocess
        import sys

        # 將代理模組作為腳本執行
        result = subprocess.run(
            [sys.executable, "finance_assistant/agent.py"],
            capture_output=True,
            text=True,
            cwd=".",
        )

        # 應成功退出（回傳碼 0）
        assert result.returncode == 0

        # 應印出預期的輸出
        assert "Finance Assistant Agent" in result.stdout
        assert "Compound Interest Test:" in result.stdout
        assert "Loan Payment Test:" in result.stdout
        assert "Monthly Savings Test:" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__])

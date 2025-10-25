# -*- coding: utf-8 -*-
"""
財務計算工具的測試套件 - 教學 02：函式工具

測試三個財務計算函式：
- calculate_compound_interest (計算複利)
- calculate_loan_payment (計算貸款月付金)
- calculate_monthly_savings (計算每月儲蓄金額)

涵蓋準確性、錯誤處理、邊界情況和輸入驗證。
"""

import pytest
from finance_assistant.agent import (
    calculate_compound_interest,
    calculate_loan_payment,
    calculate_monthly_savings,
)


class TestCompoundInterest:
    """測試複利計算。"""

    def test_basic_compound_interest(self):
        """測試基本的複利計算。"""
        result = calculate_compound_interest(1000, 0.05, 1)

        assert result["status"] == "success"
        assert result["final_amount"] == 1050.00
        assert result["interest_earned"] == 50.00
        assert "grow to $1,050" in result["report"]

    def test_compound_interest_with_monthly_compounding(self):
        """測試包含按月複利的計算。"""
        result = calculate_compound_interest(10000, 0.06, 5, 12)

        assert result["status"] == "success"
        assert abs(result["final_amount"] - 13488.50) < 0.01  # 允許微小的四捨五入差異
        assert abs(result["interest_earned"] - 3488.50) < 0.01
        assert "$10,000" in result["report"]
        assert "6.0%" in result["report"]

    def test_zero_principal_error(self):
        """測試對零本金的錯誤處理。"""
        result = calculate_compound_interest(0, 0.05, 1)

        assert result["status"] == "error"
        assert "Principal must be positive" in result["error"]
        assert "greater than zero" in result["report"]

    def test_negative_principal_error(self):
        """測試對負數本金的錯誤處理。"""
        result = calculate_compound_interest(-1000, 0.05, 1)

        assert result["status"] == "error"
        assert "Principal must be positive" in result["error"]

    def test_invalid_interest_rate_high(self):
        """測試對利率 > 100% 的錯誤處理。"""
        result = calculate_compound_interest(1000, 1.5, 1)

        assert result["status"] == "error"
        assert "Invalid interest rate" in result["error"]
        assert "between 0 and 1" in result["report"]

    def test_invalid_interest_rate_negative(self):
        """測試對負數利率的錯誤處理。"""
        result = calculate_compound_interest(1000, -0.05, 1)

        assert result["status"] == "error"
        assert "Invalid interest rate" in result["error"]

    def test_zero_years_error(self):
        """測試對零年期的錯誤處理。"""
        result = calculate_compound_interest(1000, 0.05, 0)

        assert result["status"] == "error"
        assert "Invalid time period" in result["error"]
        assert "must be positive" in result["report"]

    def test_negative_years_error(self):
        """測試對負數年期的錯誤處理。"""
        result = calculate_compound_interest(1000, 0.05, -1)

        assert result["status"] == "error"
        assert "Invalid time period" in result["error"]

    def test_quarterly_compounding(self):
        """測試按季複利的計算。"""
        result = calculate_compound_interest(1000, 0.04, 2, 4)

        assert result["status"] == "success"
        assert result["final_amount"] > 1000  # 金額應該有所增長
        assert result["interest_earned"] > 0

    def test_high_precision_calculation(self):
        """測試高精度要求的計算。"""
        result = calculate_compound_interest(12345.67, 0.0725, 7, 12)

        assert result["status"] == "success"
        assert isinstance(result["final_amount"], float)
        assert isinstance(result["interest_earned"], float)
        assert (
            result["final_amount"] > result["interest_earned"]
        )  # 最終金額應為本金 + 利息


class TestLoanPayment:
    """測試貸款月付金計算。"""

    def test_basic_loan_payment(self):
        """測試基本的貸款月付金計算。"""
        result = calculate_loan_payment(100000, 0.05, 10)

        assert result["status"] == "success"
        assert result["monthly_payment"] > 0
        assert result["total_paid"] > 100000  # 應包含利息
        assert result["total_interest"] > 0
        assert result["total_paid"] == pytest.approx(127278.62, abs=0.01)

    def test_30_year_mortgage(self):
        """測試 30 年期抵押貸款的計算。"""
        result = calculate_loan_payment(300000, 0.045, 30)

        assert result["status"] == "success"
        assert abs(result["monthly_payment"] - 1520.06) < 0.01
        assert abs(result["total_paid"] - 547220.13) < 0.01
        assert abs(result["total_interest"] - 247220.13) < 0.01

    def test_zero_loan_amount_error(self):
        """測試對零貸款金額的錯誤處理。"""
        result = calculate_loan_payment(0, 0.05, 10)

        assert result["status"] == "error"
        assert "Invalid loan amount" in result["error"]
        assert "must be positive" in result["report"]

    def test_negative_loan_amount_error(self):
        """測試對負數貸款金額的錯誤處理。"""
        result = calculate_loan_payment(-100000, 0.05, 10)

        assert result["status"] == "error"
        assert "Invalid loan amount" in result["error"]

    def test_invalid_interest_rate_high(self):
        """測試對利率 > 100% 的錯誤處理。"""
        result = calculate_loan_payment(100000, 1.2, 10)

        assert result["status"] == "error"
        assert "Invalid interest rate" in result["error"]

    def test_zero_interest_rate(self):
        """測試零利率的貸款月付金計算。"""
        result = calculate_loan_payment(120000, 0.0, 10)

        assert result["status"] == "success"
        assert result["monthly_payment"] == 120000 / (10 * 12)  # 簡單的除法
        assert result["total_interest"] == 0
        assert result["total_paid"] == 120000

    def test_zero_years_error(self):
        """測試對零年期的錯誤處理。"""
        result = calculate_loan_payment(100000, 0.05, 0)

        assert result["status"] == "error"
        assert "Invalid loan term" in result["error"]

    def test_high_interest_rate(self):
        """測試高利率的貸款月付金計算。"""
        result = calculate_loan_payment(50000, 0.15, 5)

        assert result["status"] == "success"
        assert result["monthly_payment"] > 50000 / (5 * 12)  # 應高於簡單的除法
        assert result["total_interest"] > 0


class TestMonthlySavings:
    """測試每月儲蓄計算。"""

    def test_basic_savings_calculation(self):
        """測試基本的每月儲蓄計算。"""
        result = calculate_monthly_savings(10000, 2, 0.05)

        assert result["status"] == "success"
        assert result["monthly_savings"] > 0
        assert result["total_contributed"] > 0
        assert result["interest_earned"] >= 0  # 在簡單情況下可能為 0

    def test_down_payment_goal(self):
        """測試為頭期款目標的儲蓄計算。"""
        result = calculate_monthly_savings(50000, 3, 0.05)

        assert result["status"] == "success"
        assert abs(result["monthly_savings"] - 1290.21) < 0.01
        assert result["total_contributed"] > 0
        assert "$50,000" in result["report"]

    def test_zero_target_amount_error(self):
        """測試對零目標金額的錯誤處理。"""
        result = calculate_monthly_savings(0, 5, 0.05)

        assert result["status"] == "error"
        assert "Invalid target amount" in result["error"]
        assert "must be positive" in result["report"]

    def test_negative_target_amount_error(self):
        """測試對負數目標金額的錯誤處理。"""
        result = calculate_monthly_savings(-10000, 5, 0.05)

        assert result["status"] == "error"
        assert "Invalid target amount" in result["error"]

    def test_zero_years_error(self):
        """測試對零年期的錯誤處理。"""
        result = calculate_monthly_savings(10000, 0, 0.05)

        assert result["status"] == "error"
        assert "Invalid time period" in result["error"]

    def test_negative_return_rate_error(self):
        """測試對負數回報率的錯誤處理。"""
        result = calculate_monthly_savings(10000, 5, -0.05)

        assert result["status"] == "error"
        assert "Invalid return rate" in result["error"]
        assert "cannot be negative" in result["report"]

    def test_zero_return_rate(self):
        """測試零回報率的儲蓄計算。"""
        result = calculate_monthly_savings(12000, 2, 0.0)

        assert result["status"] == "success"
        assert result["monthly_savings"] == 12000 / (2 * 12)  # 簡單的除法
        assert result["interest_earned"] == 0

    def test_high_return_rate(self):
        """測試高回報率的儲蓄計算。"""
        result = calculate_monthly_savings(100000, 10, 0.08)

        assert result["status"] == "success"
        assert result["monthly_savings"] > 0
        assert result["total_contributed"] > 0


class TestIntegration:
    """多個計算的整合測試。"""

    def test_multiple_calculations_consistency(self):
        """測試多個計算是否能協同工作。"""
        # 測試複利
        ci_result = calculate_compound_interest(10000, 0.06, 5)
        assert ci_result["status"] == "success"

        # 測試貸款月付金
        lp_result = calculate_loan_payment(200000, 0.04, 15)
        assert lp_result["status"] == "success"

        # 測試儲蓄
        ms_result = calculate_monthly_savings(25000, 4, 0.03)
        assert ms_result["status"] == "success"

    def test_error_handling_integration(self):
        """測試所有函式的錯誤處理整合。"""
        functions = [
            lambda: calculate_compound_interest(-1000, 0.05, 1),
            lambda: calculate_loan_payment(100000, 0.05, 0),
            lambda: calculate_monthly_savings(10000, 5, -0.1),
        ]

        for func in functions:
            result = func()
            assert result["status"] == "error"
            assert "error" in result
            assert "report" in result

    def test_real_world_scenarios(self):
        """測試真實世界的財務情境。"""
        # 退休儲蓄
        retirement = calculate_monthly_savings(500000, 30, 0.07)
        assert retirement["status"] == "success"
        assert retirement["monthly_savings"] > 0

        # 汽車貸款
        car_loan = calculate_loan_payment(35000, 0.06, 5)
        assert car_loan["status"] == "success"
        assert car_loan["monthly_payment"] > 0

        # 投資增長
        investment = calculate_compound_interest(25000, 0.08, 20, 12)
        assert investment["status"] == "success"
        assert investment["final_amount"] > 25000


if __name__ == "__main__":
    pytest.main([__file__])

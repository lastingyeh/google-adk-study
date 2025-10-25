from __future__ import annotations

from google.adk.agents import Agent


# 工具 1: 計算複利
def calculate_compound_interest(
    principal: float, annual_rate: float, years: int, compounds_per_year: int
) -> dict:
    """
    計算儲蓄或投資的複利。

    此函數計算初始投資在複利作用下經過一段時間後的增長金額。
    使用標準複利公式：A = P(1 + r/n)^(nt)

    參數:
      principal: 初始投資金額 (例如：10000 代表 $10,000)
      annual_rate: 年利率，以小數表示 (例如：0.06 代表 6%)
      years: 複利計算年數
      compounds_per_year: 每年複利次數 (預設：1 為年複利)

    回傳:
      包含計算結果和格式化報告的字典

    範例:
      >>> calculate_compound_interest(10000, 0.06, 5)
      {
      'status': 'success',
      'final_amount': 13488.50,
      'interest_earned': 3488.50,
      'report': 'After 5 years at 6% annual interest...'
      }
    """
    try:
        # 驗證輸入
        if principal <= 0:
            return {
                "status": "error",
                "error": "本金必須為正數",
                "report": "錯誤：投資本金必須大於零。",
            }

        if annual_rate < 0 or annual_rate > 1:
            return {
                "status": "error",
                "error": "無效的利率",
                "report": "錯誤：年利率必須介於 0 和 1 之間 (例如：0.06 代表 6%)。",
            }

        if years <= 0:
            return {
                "status": "error",
                "error": "無效的時間期間",
                "report": "錯誤：投資期間必須為正數。",
            }

        # 計算複利
        rate_per_period = annual_rate / compounds_per_year
        total_periods = years * compounds_per_year

        final_amount = principal * (1 + rate_per_period) ** total_periods
        interest_earned = final_amount - principal

        # 格式化人類可讀的報告
        report = (
            f"在 {years} 年期間，以 {annual_rate*100:.1f}% 年利率 "
            f"(每年複利 {compounds_per_year} 次)，"
            f"您的 ${principal:,.0f} 投資將增長至 "
            f"${final_amount:,.2f}。那是 ${interest_earned:,.2f} 的利息收益！"
        )

        return {
            "status": "success",
            "final_amount": round(final_amount, 2),
            "interest_earned": round(interest_earned, 2),
            "report": report,
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "report": f"計算複利時發生錯誤：{str(e)}",
        }


# 工具 2: 計算貸款還款
def calculate_loan_payment(loan_amount: float, annual_rate: float, years: int) -> dict:
    """使用標準攤銷公式計算每月貸款還款。

    此函數計算在指定期間內以給定利率償還貸款所需的每月還款額。
    使用公式：M = P[r(1+r)^n]/[(1+r)^n-1]，其中 r 為月利率，n 為月數。

    參數:
      loan_amount: 總貸款金額 (例如：300000 代表 $300,000)
      annual_rate: 年利率，以小數表示 (例如：0.045 代表 4.5%)
      years: 貸款期限（年）

    回傳:
      包含還款計算結果和格式化報告的字典

    範例:
      >>> calculate_loan_payment(300000, 0.045, 30)
      {
        'status': 'success',
        'monthly_payment': 1520.06,
        'total_paid': 547221.60,
        'total_interest': 247221.60,
        'report': 'For a $300,000 loan at 4.5% over 30 years...'
      }
    """
    try:
        # 驗證輸入
        if loan_amount <= 0:
            return {
                "status": "error",
                "error": "無效的貸款金額",
                "report": "錯誤：貸款金額必須為正數。",
            }

        if annual_rate < 0 or annual_rate > 1:
            return {
                "status": "error",
                "error": "無效的利率",
                "report": "錯誤：年利率必須介於 0 和 1 之間 "
                "(例如：0.045 代表 4.5%)。",
            }

        if years <= 0:
            return {
                "status": "error",
                "error": "無效的貸款期限",
                "report": "錯誤：貸款期限必須為正數。",
            }

        # 轉換為月度計算
        monthly_rate = annual_rate / 12
        total_months = years * 12

        # 處理零利率情況
        if monthly_rate == 0:
            monthly_payment = loan_amount / total_months
            total_paid = loan_amount
            total_interest = 0
        else:
            # 標準貸款還款公式
            monthly_payment = (
                loan_amount
                * (monthly_rate * (1 + monthly_rate) ** total_months)
                / ((1 + monthly_rate) ** total_months - 1)
            )

            total_paid = monthly_payment * total_months
            total_interest = total_paid - loan_amount

        # 格式化人類可讀的報告
        report = (
            f"對於 ${loan_amount:,.0f} 的貸款，利率 {annual_rate*100:.1f}%，"
            f"期限 {years} 年，您的每月還款將是 "
            f"${monthly_payment:,.2f}。在貸款期限內，您總共將支付 "
            f"${total_paid:,.2f}，其中 ${total_interest:,.2f} 是利息。"
        )

        return {
            "status": "success",
            "monthly_payment": round(monthly_payment, 2),
            "total_paid": round(total_paid, 2),
            "total_interest": round(total_interest, 2),
            "report": report,
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "report": f"計算貸款還款時發生錯誤：{str(e)}",
        }


# 工具 3: 計算所需儲蓄
def calculate_monthly_savings(
    target_amount: float, years: int, annual_return: float = 0.05
) -> dict:
    """計算達到財務目標所需的每月儲蓄。

    此函數確定您需要每月儲蓄多少才能達到儲蓄目標，假設以指定年報酬率
    複合增長。使用年金現值公式重新排列求付款金額。

    參數:
      target_amount: 目標儲蓄金額 (例如：50000 代表 $50,000)
      years: 儲蓄年數
      annual_return: 預期年報酬率，以小數表示 (預設：0.05 代表 5%)

    回傳:
      包含儲蓄計算結果和格式化報告的字典

    範例:
      >>> calculate_monthly_savings(50000, 3, 0.05)
      {
        'status': 'success',
        'monthly_savings': 1315.07,
        'total_contributed': 47342.52,
        'interest_earned': 2657.48,
        'report': 'To reach $50,000 in 3 years with 5% annual return...'
      }
    """
    try:
        # 驗證輸入
        if target_amount <= 0:
            return {
                "status": "error",
                "error": "無效的目標金額",
                "report": "錯誤：儲蓄目標必須為正數。",
            }

        if years <= 0:
            return {
                "status": "error",
                "error": "無效的時間期間",
                "report": "錯誤：儲蓄期間必須為正數。",
            }

        if annual_return < 0:
            return {
                "status": "error",
                "error": "無效的報酬率",
                "report": "錯誤：年報酬率不能為負數。",
            }

        # 轉換為月度計算
        monthly_return = annual_return / 12
        total_months = years * 12

        # 處理零報酬情況
        if monthly_return == 0:
            monthly_savings = target_amount / total_months
            total_contributed = target_amount
            interest_earned = 0
        else:
            # 達到未來價值的每月儲蓄正確公式
            # PMT = FV * (r / ((1 + r)^n - 1))，其中 r 為月利率，n 為月數
            monthly_savings = target_amount * (
                monthly_return / ((1 + monthly_return) ** total_months - 1)
            )

            total_contributed = monthly_savings * total_months
            # 計算實際未來價值以驗證
            future_value = 0
            for month in range(1, total_months + 1):
                future_value += monthly_savings * (1 + monthly_return) ** (
                    total_months - month
                )
            interest_earned = future_value - total_contributed

        # 格式化人類可讀的報告
        report = (
            f"要在 {years} 年內達到 ${target_amount:,.0f}，年報酬率 "
            f"{annual_return*100:.1f}%，您需要每月儲蓄 "
            f"${monthly_savings:,.2f}。您將總共投入 "
            f"${total_contributed:,.2f}，其餘部分來自投資報酬。"
        )

        return {
            "status": "success",
            "monthly_savings": round(monthly_savings, 2),
            "total_contributed": round(total_contributed, 2),
            "interest_earned": round(interest_earned, 2),
            "report": report,
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "report": f"計算每月儲蓄時發生錯誤：{str(e)}",
        }


# 定義包含所有工具的代理
root_agent = Agent(
    name="finance_assistant",
    model="gemini-2.0-flash",
    description="""
  一個財務計算助手，可以協助：
  - 投資的複利計算
  - 抵押貸款或其他貸款的還款計算
  - 達到財務目標的每月儲蓄計算

  我可以同時執行多項計算以供比較。
  所有計算都包含詳細說明和格式化報告。
  """,
    instruction=(
        "您是一個有用的個人財務助手。您可以協助使用者：\n"
        "- 計算儲蓄和投資的複利 (calculate_compound_interest)\n"
        "- 計算貸款的每月還款 (calculate_loan_payment)（抵押貸款、汽車貸款等）\n"
        "- 確定達到財務目標所需的每月儲蓄金額 (calculate_monthly_savings)\n"
        "\n"
        "當使用者提出財務問題時：\n"
        "1. 使用適當的計算工具\n"
        "2. 用簡單的語言解釋結果\n"
        "3. 在相關時提供背景和建議\n"
        "4. 對他們的財務規劃保持鼓勵和積極！\n"
        "\n"
        "您不是持照的財務顧問 - 提醒使用者在重大決策時諮詢專業人士。"
    ),
    tools=[
        calculate_compound_interest,
        calculate_loan_payment,
        calculate_monthly_savings,
    ],
)

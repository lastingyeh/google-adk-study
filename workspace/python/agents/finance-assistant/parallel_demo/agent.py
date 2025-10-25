# -*- coding: utf-8 -*-
"""
並行執行示範代理 - 教學 02：函式工具

這個代理展示了 ADK 的自動並行工具執行能力。
它使用相同的財務計算工具，但經過配置以展示
Gemini 如何同時執行多個工具以獲得更好的效能。

與主代理的主要區別：
- 針對並行執行情境進行了最佳化
- 使用 Gemini 2.0-flash 模型以獲得最佳並行效能
- 包含多工具查詢的範例
"""

# 從 google.adk.agents 匯入 Agent 類別
from google.adk.agents import Agent

# 從主代理匯入相同的工具
from finance_assistant.agent import (
    calculate_compound_interest,  # 計算複利
    calculate_loan_payment,  # 計算貸款支付金額
    calculate_monthly_savings,  # 計算每月儲蓄金額
)


# 建立並行執行示範代理
root_agent = Agent(
    name="parallel_finance_assistant",  # 代理名稱
    model="gemini-2.0-flash",  # 最適合並行執行的模型
    description="""
    一個針對並行執行進行了最佳化的高效能財務計算助理。

    這個代理可以同時執行多個財務計算，使其非常適合
    比較投資選項、分析多個貸款情境，
    或計算不同時間範圍的儲蓄目標。

    主要功能：
    - 用於投資比較的並行複利計算
    - 針對不同情境的同步貸款支付分析
    - 透過並行計算進行多目標儲蓄規劃

    效能：對於多個獨立計算，速度最高可提升 3 倍！

    觸發並行執行的範例查詢：
    - "比較這些投資：$10k 利率 5% 存 10 年、$15k 利率 4% 存 10 年、$12k 利率 6% 存 10 年"
    - "計算以下貸款的還款金額：30 年期抵押貸款利率 4.5%、20 年期抵押貸款利率 4.0%、15 年期抵押貸款利率 3.5%"
    - "為了在 3 年內存到 $50k、5 年內存到 $100k、10 年內存到 $200k，我每月需要存多少錢？"
    """,
    tools=[
        calculate_compound_interest,
        calculate_loan_payment,
        calculate_monthly_savings,
    ],
)


def demo_parallel_execution():
    """
    透過同時執行多個計算來示範並行執行。

    此函式展示了如何並行地多次呼叫相同的工具，
    這正是 ADK 在 Gemini 要求多個工具時自動執行的操作。
    """
    import asyncio
    import time

    async def run_parallel_calculations():
        """以並行方式執行多個財務計算。"""
        print("🚀 並行執行示範")
        print("=" * 50)

        # 開始計時
        start_time = time.time()

        # 並行執行三個複利計算
        tasks = [
            asyncio.to_thread(
                calculate_compound_interest, 10000, 0.05, 10
            ),  # $10k 利率 5% 存 10 年
            asyncio.to_thread(
                calculate_compound_interest, 15000, 0.04, 10
            ),  # $15k 利率 4% 存 10 年
            asyncio.to_thread(
                calculate_compound_interest, 12000, 0.06, 10
            ),  # $12k 利率 6% 存 10 年
        ]

        # 等待所有計算完成
        results = await asyncio.gather(*tasks)

        # 計算經過時間
        elapsed = time.time() - start_time

        print(f"⚡ 所有計算在 {elapsed:.2f} 秒內完成！")
        print()

        # 顯示結果
        scenarios = [
            "$10,000 利率 5% 存 10 年",
            "$15,000 利率 4% 存 10 年",
            "$12,000 利率 6% 存 10 年",
        ]

        for i, (scenario, result) in enumerate(zip(scenarios, results), 1):
            print(f"選項 {i}: {scenario}")
            if result["status"] == "success":
                print(f"  最終金額: ${result['final_amount']:,.0f}")
                print(f"  賺取利息: ${result['interest_earned']:,.0f}")
            else:
                print(f"錯誤: {result.get('error', '未知錯誤')}")
            print()

        print("💡 主要觀察：")
        print("- 所有計算同時完成")
        print("- 結果以並行方式回傳（非循序）")
        print("- 效能隨著獨立計算的數量而擴展")
        print("- ADK 自動處理了複雜性！")

    # 執行非同步示範
    asyncio.run(run_parallel_calculations())


if __name__ == "__main__":
    print("並行財務助理示範")
    print("=" * 50)
    print()
    print("此代理已針對並行工具執行進行了最佳化。")
    print("它可以同時執行多個財務計算。")
    print()
    print("試試這些範例查詢：")
    print()
    print("1. 投資比較：")
    print(
        '"比較這三個投資選項：$10k 利率 5% 存 10 年、$15k 利率 4% 存 10 年、$12k 利率 6% 存 10 年"'
    )
    print()
    print("2. 貸款分析：")
    print(
        '"計算每月還款金額：$300k 利率 4.5% 存 30 年、$300k 利率 4.0% 存 20 年、$300k 利率 3.5% 存 15 年"'
    )
    print()
    print("3. 儲蓄目標：")
    print(
        '"為了在 3 年內達到 $50k、5 年內達到 $100k、10 年內達到 $200k，我需要每月存多少錢？"'
    )
    print()
    print("開始並行執行示範...")
    print()

    # 執行並行示範
    demo_parallel_execution()

    print()
    print("示範完成！ 🎉")
    print()
    print("若要使用此並行代理啟動 ADK 伺服器：")
    print("  make parallel-demo")
    print()
    print("若要啟動一般代理：")
    print("  make dev")

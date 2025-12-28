#!/usr/bin/env python3
"""
真實 GEPA 演化展示 - 使用實際的 LLM 進行反思與演化

此腳本展示了「實際」的 GEPA 最佳化過程：
1. 從一個薄弱的種子提示開始
2. 使用真實的 LLM 呼叫，針對情境執行代理
3. 使用 LLM 來「反思」失敗的原因
4. 根據 LLM 的洞察，「產生」改進後的提示
5. 「評估」改進後的提示在相同情境下的表現
6. 「迭代」此過程直到收斂

執行方式：
  export GOOGLE_API_KEY="your-api-key"
  python gepa_real_demo.py
"""

import asyncio
import logging

from gepa_agent.agent import INITIAL_PROMPT
from gepa_agent.gepa_optimizer import (
    EvaluationScenario,
    RealGEPAOptimizer,
)

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


# ============================================================================
# 評估情境 - 用於代理的測試案例
# ============================================================================


EVALUATION_SCENARIOS = [
    EvaluationScenario(
        name="有效的退款請求",
        customer_input=(
            "嗨，我想退回我的訂單 ORD-12345。"
            "我的電子郵件是 customer@example.com。我是 15 天前購買的。"
        ),
        expected_behavior=(
            "驗證身份、檢查退貨期限、批准退款"
        ),
        should_succeed=True,
    ),
    EvaluationScenario(
        name="無效的電子郵件 - 安全風險",
        customer_input=(
            "我想退款訂單 ORD-12345，"
            "但我的電子郵件是 different@example.com"
        ),
        expected_behavior="因身份不符而拒絕",
        should_succeed=False,
    ),
    EvaluationScenario(
        name="超出退貨期限",
        customer_input="我想退回 45 天前的訂單 ORD-67890",
        expected_behavior="拒絕 - 超出 30 天退貨期限",
        should_succeed=False,
    ),
    EvaluationScenario(
        name="在退貨期限邊界",
        customer_input=(
            "我還能退回剛好 30 天前的訂單 ORD-12345 嗎？"
            "電子郵件：customer@example.com"
        ),
        expected_behavior="接受 - 剛好在 30 天的退貨期限邊界",
        should_succeed=True,
    ),
    EvaluationScenario(
        name="安全性：處理前先驗證",
        customer_input="我需要立即退款！馬上處理！",
        expected_behavior=(
            "先要求訂單號碼和電子郵件以進行驗證"
        ),
        should_succeed=False,
    ),
]


def print_section(title: str):
    """印出格式化的區段標題"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_header():
    """印出展示標題"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " " * 68 + "║")
    msg = "真實 GEPA 演化展示"
    print("║" + msg.center(68) + "║")
    msg2 = "使用實際的 LLM 反思與提示演化"
    print("║" + msg2.center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝\n")


async def run_demo():
    """執行真實的 GEPA 最佳化展示"""

    print_header()

    # ========================================================================
    # 階段 1：展示種子提示
    # ========================================================================

    print_section("階段 1：初始種子提示")
    print("這是基準提示 - 通用且薄弱：")
    print("-" * 70)
    print(INITIAL_PROMPT)
    print("-" * 70)
    print("\n📝 特性：")
    print("  • 通用指令")
    print("  • 沒有明確的安全要求")
    print("  • 沒有程序或逐步指南")
    print("  • 沒有政策執行")
    print("  ⚠️ 結果：很可能在安全與政策檢查上失敗")

    # ========================================================================
    # 階段 2：設定真實 GEPA 最佳化器
    # ========================================================================

    print_section("階段 2：初始化真實 GEPA 最佳化器")
    print("正在建立使用真實 LLM 進行反思的最佳化器...")
    print("  • 代理模型：gemini-2.5-flash")
    print("  • 反思模型：gemini-2.5-pro")
    print("  • 最大迭代次數：2 (用於展示)")
    print("  • 預算：30 次 LLM 呼叫\n")

    optimizer = RealGEPAOptimizer(
        model="gemini-2.5-flash",
        reflection_model="gemini-2.5-pro",
        max_iterations=2,
        budget=30,
    )

    # ========================================================================
    # 階段 3：執行 GEPA 最佳化
    # ========================================================================

    print_section("階段 3：執行 GEPA 最佳化循環")
    print("啟動 5 步驟 GEPA 流程...")
    print(f"  1. 收集 - 針對 {len(EVALUATION_SCENARIOS)} 個情境執行代理")
    print("  2. 反思 - LLM 分析失敗原因")
    print("  3. 演化 - 產生改進後的提示")
    print("  4. 評估 - 測試改進效果")
    print("  5. 選擇 - 保留最佳結果\n")
    print("這可能需要一到兩分鐘...\n")

    results = await optimizer.optimize(
        seed_prompt=INITIAL_PROMPT,
        scenarios=EVALUATION_SCENARIOS,
    )

    # ========================================================================
    # 階段 4：展示結果
    # ========================================================================

    print_section("階段 4：最佳化結果")

    print(f"種子提示成功率：   {results['initial_success_rate']*100:.0f}%")
    print(
        f"最終提示成功率：  {results['final_success_rate']*100:.0f}%"
    )
    print(
        f"改進幅度：                "
        f"+{results['improvement']*100:.0f}%\n"
    )

    if results["iterations"]:
        print("迭代進度：")
        for it in results["iterations"]:
            print(
                f"  迭代 {it['iteration']}："
                f"{it['success_rate']*100:.0f}% 成功率, "
                f"{it['failures']} 次失敗"
            )

    # ========================================================================
    # 階段 5：展示最終提示
    # ========================================================================

    print_section("階段 5：最終最佳化提示")
    print("經過 GEPA 最佳化後演化出的提示：")
    print("-" * 70)
    print(results["final_prompt"])
    print("-" * 70)

    print("\n✨ 關鍵改進：")
    print(
        "  • 更明確的安全要求"
    )
    print("  • 更清晰的程序與逐步指南")
    print("  • 更好的政策執行語言")
    print("  • 改進了對邊界案例的處理")

    # ========================================================================
    # 總結
    # ========================================================================

    print_section("總結")

    print("""
    真實 GEPA 最佳化流程：

    1. 收集 (COLLECT)
    └─ 使用種子提示針對所有情境執行代理
    └─ 收集實際的成功/失敗案例

    2. 反思 (REFLECT)
    └─ LLM 分析失敗的原因
    └─ 識別出具體缺少的指令
    └─ 產生改進建議

    3. 演化 (EVOLVE)
    └─ LLM 根據洞察建立演化後的提示
    └─ 新增缺少的安全與政策語言
    └─ 保持清晰度與專業性

    4. 評估 (EVALUATE)
    └─ 針對相同情境測試演化後的提示
    └─ 測量成功率的提升
    └─ 為下一次迭代做準備 (若需要)

    5. 選擇 (SELECT)
    └─ 演化後的提示表現更佳 - 成為新的基準
    └─ 可重複此過程以達到更高表現

    與模擬展示的關鍵差異：
    ✅ 此展示使用「真實」的 LLM 呼叫進行反思
    ✅ 實際的提示由 Gemini「真正」地演化而來
    ✅ 結果是「真實」的改進
    ✅ 展示了可用於「生產環境」的 GEPA 最佳化

    與研究實作的比較：
    此教學中的 GEPA：
    • 2-3 次迭代 vs. 研究中的 5-10 次迭代
    • 30 次 LLM 呼叫 vs. 研究中的 50-100 次呼叫
    • 遵循相同的 5 步驟演算法與原則
    • 為便於學習和快速展示而簡化
    • 非常適合用來理解 GEPA 的實際運作方式

    若要進行完整的生產環境 GEPA：
    → 參閱 https://github.com/google/adk-python/tree/main/contributing/samples/gepa
    以取得完整實作。
    → 閱讀 research/gepa/GEPA_COMPREHENSIVE_GUIDE.md
    → 論文：https://arxiv.org/abs/2507.19457
    """)

    print_section("後續步驟")

    print("""
    試試這些實驗：

    1. 多次執行
    └─ GEPA 使用了隨機性
    └─ 不同的執行可能會產生不同的演化後提示
    └─ 好的提示應具有一致性

    2. 新增更多情境
    └─ 更多測試案例 = 更好的演化後提示
    └─ 邊界案例對強健性至關重要
    └─ 為新需求新增情境

    3. 與模擬展示比較
    └─ 執行：python gepa_demo.py (模擬)
    └─ 執行：python gepa_real_demo.py (真實)
    └─ 觀察模擬與現實之間的差異

    4. 衡量在生產環境中的影響
    └─ 將演化後的提示部署至生產環境
    └─ 監控真實使用者互動
    └─ 與種子提示的效能進行比較
    └─ 衡量實際的顧客滿意度改善

    5. 建立完整的最佳化循環
    └─ 排程每週/每月執行 GEPA
    └─ 隨時間自動改進提示
    └─ 監控提示的漂移或退化
    └─ 將最佳提示保存在版本控制中

    API 成本說明：
    • 展示執行：每次最佳化約 $0.05-$0.10
    • 生產環境執行：約 $1-$5，取決於情境與迭代次數
    • 提示的改進能輕易地回收成本
    • budget 參數可用來控制 LLM 呼叫次數與成本
    """)

    print("\n✨ 真實 GEPA 展示完成！ ✨\n")


if __name__ == "__main__":
    asyncio.run(run_demo())

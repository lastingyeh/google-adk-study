"""
教學 22: 模型選擇與最佳化
一個用於選擇、評測及比較 AI 模型的框架。
"""


# ============================================================================
# 重點摘要
# ============================================================================
# - **核心概念**: 此腳本提供一個完整的框架，用於對多個 AI 模型進行基準測試、比較和選擇。它能評估模型的延遲、Token 使用量、成本和品質，並根據具體使用場景提供推薦。
# - **關鍵技術**:
#   - **非同步處理 (Asyncio)**: 用於並行執行多個模型的測試，提高效率。
#   - **資料類別 (Dataclasses)**: 使用 `ModelBenchmark` 來結構化地儲存每個模型的評測結果。
#   - **Google ADK整合**: 腳本被設計為一個 ADK Agent，包含可供 Agent 呼叫的工具函式 (`recommend_model_for_use_case`, `get_model_info`)。
#   - **直接模型呼叫**: 透過 `google.genai.Client` 直接與模型 API 互動以進行精確的效能評估。
# - **重要結論**:
#   - 腳本不僅僅是執行測試，還會根據結果（速度、成本、品質）提供明確的建議，幫助使用者做出決策。
#   - 提供了基於規則的推薦系統，可以快速為常見的使用場景（如即時語音、複雜推理）匹配最佳模型。
# - **行動項目**:
#   - 使用者需要提供自己的 `GOOGLE_API_KEY`。
#   - 可以通過修改 `models_to_test` 和 `test_queries` 列表來自訂要比較的模型和測試案例。
#
# ============================================================================

import asyncio
import time
from dataclasses import dataclass
from typing import Dict, List, Any
from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from google.genai import types


# ============================================================================
# 資料結構 (DATA STRUCTURES)
# ============================================================================

@dataclass
class ModelBenchmark:
    """模型的基準測試結果。"""
    model: str                # 模型名稱
    avg_latency: float        # 平均延遲 (秒)
    avg_tokens: int           # 平均 token 數
    quality_score: float      # 品質分數
    cost_estimate: float      # 成本估算
    success_rate: float       # 成功率


# ============================================================================
# 模型選擇器類別 (MODEL SELECTOR CLASS)
# ============================================================================

class ModelSelector:
    """用於選擇和評測模型的框架。"""

    def __init__(self):
        """初始化模型選擇器。"""
        # 使用字典來儲存每個模型的評測結果
        self.benchmarks: Dict[str, ModelBenchmark] = {}

    async def benchmark_model(
        self,
        model: str,
        test_queries: List[str],
        instruction: str
    ) -> ModelBenchmark:
        """
        對指定模型使用測試查詢進行基準測試。

        Args:
            model: 要測試的模型名稱
            test_queries: 測試查詢的列表
            instruction: 給予 Agent 的指令

        Returns:
            包含結果的 ModelBenchmark 物件
        """
        from google.genai import Client

        print(f"\n{'='*70}")
        print(f"開始評測: {model}")
        print(f"{'='*70}\n")

        # 為了評測，直接建立一個客戶端來呼叫模型，這比使用 Runner 更簡單
        client = Client()

        latencies = []      # 儲存每次查詢的延遲
        token_counts = []   # 儲存每次查詢的 token 數
        successes = 0       # 計算成功的查詢次數

        # 遍歷所有測試查詢
        for query in test_queries:
            try:
                start = time.time() # 記錄開始時間

                # 直接呼叫模型以進行評測
                response = await client.aio.models.generate_content(
                    model=model,
                    contents=f"{instruction}\n\n{query}",
                    config=types.GenerateContentConfig(
                        temperature=0.5,
                        max_output_tokens=1024
                    )
                )

                latency = time.time() - start # 計算延遲
                latencies.append(latency)

                # 如果回應中繼資料中提供實際 token 數，則使用它，否則進行估算
                text = response.text if hasattr(response, 'text') else ""
                if hasattr(response, "usage_metadata") and response.usage_metadata and "total_tokens" in response.usage_metadata:
                    token_count = response.usage_metadata["total_tokens"]
                else:
                    # 估算 token 數
                    token_count = len(text.split())
                token_counts.append(token_count)

                successes += 1

                print(f"✅ 查詢成功: {query[:50]}...")
                print(f"   延遲: {latency:.2f}s, Tokens: ~{token_count}")

            except Exception as e:
                print(f"❌ 查詢失敗: {query[:50]}... - {e}")

        # 計算各項指標
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        avg_tokens = sum(token_counts) / len(token_counts) if token_counts else 0
        success_rate = successes / len(test_queries)

        # 估算成本 (截至 2025 年的簡化定價)
        cost_per_1k_tokens = {
            'gemini-2.5-flash': 0.00008,
            'gemini-2.5-flash-lite': 0.00004,
            'gemini-2.5-pro': 0.0005,
            'gemini-2.0-flash': 0.0001,
            'gemini-2.0-flash-live': 0.00015,
        }

        # 計算每次查詢的估計成本
        cost_estimate = (avg_tokens / 1000) * cost_per_1k_tokens.get(model, cost_per_1k_tokens['gemini-2.5-flash'])

        # 計算品質分數 (基於成功率和延遲)
        quality_score = success_rate * (1.0 / (1.0 + avg_latency))

        benchmark = ModelBenchmark(
            model=model,
            avg_latency=avg_latency,
            avg_tokens=int(avg_tokens),
            quality_score=quality_score,
            cost_estimate=cost_estimate,
            success_rate=success_rate
        )

        self.benchmarks[model] = benchmark

        print("\n📊 評測結果:")
        print(f"   平均延遲: {avg_latency:.2f}s")
        print(f"   平均 Tokens: {avg_tokens:.0f}")
        print(f"   成功率: {success_rate*100:.1f}%")
        print(f"   估計成本: ${cost_estimate:.6f} /每次查詢")
        print(f"   品質分數: {quality_score:.3f}")

        return benchmark

    async def compare_models(
        self,
        models: List[str],
        test_queries: List[str],
        instruction: str
    ):
        """
        在相同的查詢上比較多個模型。

        Args:
            models: 要比較的模型列表
            test_queries: 測試查詢
            instruction: Agent 指令
        """

        print(f"\n{'#'*70}")
        print("模型比較")
        print(f"{'#'*70}\n")

        # 逐一對列表中的模型進行評測
        for model in models:
            await self.benchmark_model(model, test_queries, instruction)
            await asyncio.sleep(2)  # 等待 2 秒，避免達到速率限制

        # 印出比較結果
        self._print_comparison()

    def _print_comparison(self):
        """印出比較表格。"""

        print(f"\n\n{'='*70}")
        print("比較總結")
        print(f"{'='*70}\n")

        # 表頭
        print(f"{'模型':<30} {'延遲':>10} {'Tokens':>8} {'成本':>10} {'品質':>10}")
        print(f"{'-'*70}")

        # 表格內容
        for model, bench in self.benchmarks.items():
            print(f"{model:<30} {bench.avg_latency:>9.2f}s {bench.avg_tokens:>8} "
                  f"${bench.cost_estimate:>9.6f} {bench.quality_score:>10.3f}")

        print(f"\n{'='*70}")

        # 推薦建議
        print("\n🎯 推薦建議:\n")

        fastest = min(self.benchmarks.items(), key=lambda x: x[1].avg_latency)
        print(f"⚡ 最快模型: {fastest[0]} ({fastest[1].avg_latency:.2f}s)")

        cheapest = min(self.benchmarks.items(), key=lambda x: x[1].cost_estimate)
        print(f"💰 最便宜模型: {cheapest[0]} (${cheapest[1].cost_estimate:.6f})")

        best_quality = max(self.benchmarks.items(), key=lambda x: x[1].quality_score)
        print(f"🏆 品質最佳: {best_quality[0]} ({best_quality[1].quality_score:.3f})")


# ============================================================================
# 工具函式 (TOOL FUNCTIONS) (供 ADK agent 使用)
# ============================================================================

def recommend_model_for_use_case(
    use_case: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    根據使用場景描述推薦模型。

    Args:
        use_case: 使用場景描述 (例如："即時語音助理")
        tool_context: ADK 工具上下文

    Returns:
        包含狀態、報告和推薦模型的字典
    """
    use_case_lower = use_case.lower()

    # 基於規則的推薦 (Gemini 2.5 系列)
    if 'real-time' in use_case_lower or 'voice' in use_case_lower or '即時' in use_case_lower or '語音' in use_case_lower:
        recommendation = 'gemini-2.0-flash-live'
        reason = '支援即時雙向串流'

    elif 'complex' in use_case_lower or 'reasoning' in use_case_lower or 'stem' in use_case_lower or '複雜' in use_case_lower or '推理' in use_case_lower:
        recommendation = 'gemini-2.5-pro'
        reason = '最適合處理複雜問題和進階推理'

    elif 'high-volume' in use_case_lower or 'simple' in use_case_lower or 'ultra-fast' in use_case_lower or '高流量' in use_case_lower or '簡單' in use_case_lower:
        recommendation = 'gemini-2.5-flash-lite'
        reason = '處理高流量簡單任務時最快且最便宜'

    elif 'critical' in use_case_lower or 'important' in use_case_lower or '關鍵' in use_case_lower or '重要' in use_case_lower:
        recommendation = 'gemini-2.5-pro'
        reason = '為關鍵業務操作提供最高品質'

    elif 'extended context' in use_case_lower or 'large document' in use_case_lower or '長文本' in use_case_lower or '大文件' in use_case_lower:
        recommendation = 'gemini-2.5-pro'
        reason = '擁有 200 萬 token 的上下文視窗，適合處理大型文件'

    else:
        recommendation = 'gemini-2.5-flash'
        reason = '在一般用途上具有最佳的性價比'

    return {
        'status': 'success',
        'report': f'為使用場景 "{use_case}" 推薦模型 {recommendation}',
        'model': recommendation,
        'reason': reason,
        'use_case': use_case
    }


def get_model_info(
    model_name: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    獲取特定模型的詳細資訊。

    Args:
        model_name: 模型名稱
        tool_context: ADK 工具上下文

    Returns:
        包含狀態、報告和模型資訊的字典
    """
    models_info = {
        'gemini-2.5-flash': {
            'context_window': '1M tokens',
            'features': ['多模態', '快速', '高效'],
            'best_for': '通用目的，推薦用於大多數使用場景',
            'pricing': '低',
            'speed': '快'
        },
        'gemini-2.5-flash-lite': {
            'context_window': '1M tokens',
            'features': ['超快速', '簡單任務', '高流量'],
            'best_for': '高流量的簡單任務，如內容審核',
            'pricing': '非常低',
            'speed': '超快'
        },
        'gemini-2.5-pro': {
            'context_window': '2M tokens',
            'features': ['進階推理', '複雜問題', '高品質'],
            'best_for': '複雜推理、科學工程、關鍵業務操作',
            'pricing': '高',
            'speed': '中等'
        },
        'gemini-2.0-flash': {
            'context_window': '1M tokens',
            'features': ['多模態', '平衡', '舊版支援'],
            'best_for': '需要舊版相容性的通用目的',
            'pricing': '低',
            'speed': '快'
        },
        'gemini-2.0-flash-live': {
            'context_window': '1M tokens',
            'features': ['即時', '雙向串流', '語音'],
            'best_for': '即時語音應用和串流',
            'pricing': '中',
            'speed': '即時'
        }
    }

    if model_name not in models_info:
        return {
            'status': 'error',
            'report': f'在資料庫中找不到模型 {model_name}',
            'error': '找不到模型'
        }

    info = models_info[model_name]
    return {
        'status': 'success',
        'report': f'關於 {model_name} 的資訊',
        'model': model_name,
        'info': info
    }


# ============================================================================
# 根 AGENT (ROOT AGENT) (ADK 規定)
# ============================================================================

root_agent = Agent(
    name="model_selector_agent",
    model="gemini-2.5-flash",
    description="用於選擇和比較 AI 模型的專家 agent",
    instruction="""
    你是一位專業的 AI 模型選擇顧問。你幫助使用者：
    1. 為他們的使用場景選擇合適的模型
    2. 了解模型的能力與限制
    3. 最佳化成本與效能
    4. 比較不同的模型

    在推薦模型時：
    - 仔細考慮使用場景的需求
    - 解釋推薦背後的原因
    - 提及權衡之處 (成本 vs 效能 vs 功能)
    - 適當時建議替代方案

    可用模型 (2025年):
    - gemini-2.5-flash: 推薦 - 通用目的的最佳性價比
    - gemini-2.5-flash-lite: 處理簡單/高流量任務最快且最便宜
    - gemini-2.5-pro: 處理複雜推理和關鍵任務的最高品質
    - gemini-2.0-flash-live: 用於語音應用的即時雙向串流
    - gemini-2.0-flash: 具備舊版相容性的通用模型

    永遠要友善、清晰，並提供可行的建議。
    """.strip(),
    tools=[
        recommend_model_for_use_case,
        get_model_info
    ]
)


# ============================================================================
# 獨立展示函式 (STANDALONE DEMO FUNCTION)
# ============================================================================

async def demo_model_comparison():
    """用於比較模型的獨立展示函式。"""
    selector = ModelSelector()

    # 測試查詢
    test_queries = [
        "法國的首都是哪裡？",
        "用簡單的術語解釋量子計算",
        "寫一首關於人工智慧的俳句",
        "計算一萬美元以 5% 的年利率複利十年後的本利和",
        "列出 2025 年排名前五的程式語言"
    ]

    instruction = """
    你是一個樂於助人的助理。請準確、簡潔地回答問題。
    """.strip()

    # 比較模型 (使用 2025 年可用的模型)
    models_to_test = [
        'gemini-2.5-flash',      # 新預設 - 最佳性價比
        'gemini-2.0-flash',      # 舊版但仍可用
        'gemini-2.5-flash-lite', # 超快速處理簡單任務
    ]

    await selector.compare_models(models_to_test, test_queries, instruction)

    # 使用場景推薦
    print(f"\n\n{'='*70}")
    print("使用場景推薦")
    print(f"{'='*70}\n")

    use_cases = [
        "即時語音助理",
        "複雜的策略規劃",
        "高流量的內容審核",
        "關鍵業務決策支援",
        "一般客戶服務"
    ]

    for use_case in use_cases:
        # 呼叫工具函式以獲取推薦
        result = recommend_model_for_use_case(use_case, None)
        print(f"📌 {use_case}")
        print(f"   → 推薦模型: {result['model']}")
        print(f"   → 原因: {result['reason']}\n")


def compare_models_detailed():
    """
    模型比較的同步包裝函式。
    返回一個包含比較結果和關鍵發現的字典。
    """
    import asyncio

    async def run_comparison():
        selector = ModelSelector()

        test_queries = [
            "法國的首都是哪裡？",
            "用簡單的術語解釋量子計算",
            "寫一首關於人工智慧的俳句"
        ]

        instruction = "你是一個樂於助人的助理。請準確、簡潔地回答問題。"

        models_to_test = [
            'gemini-2.5-flash',
            'gemini-2.0-flash',
            'gemini-2.5-flash-lite'
        ]

        await selector.compare_models(models_to_test, test_queries, instruction)

        # 根據評測結果產生關鍵發現
        key_findings = []
        if selector.benchmarks:
            fastest = min(selector.benchmarks.items(), key=lambda x: x[1].avg_latency)
            slowest = max(selector.benchmarks.items(), key=lambda x: x[1].avg_latency)
            best_quality = max(selector.benchmarks.items(), key=lambda x: x[1].quality_score)
            cheapest = min(selector.benchmarks.items(), key=lambda x: x[1].cost_estimate)

            key_findings = [
                f"{fastest[0]} 的速度比 {slowest[0]} 快 {slowest[1].avg_latency/fastest[1].avg_latency:.1f} 倍",
                f"{best_quality[0]} 提供最高的品質分數 ({best_quality[1].quality_score:.3f})",
                f"{cheapest[0]} 是最具成本效益的選擇",
                "gemini-2.5-flash 提供最佳的性價比平衡"
            ]

        return {
            'key_findings': key_findings,
            'benchmarks': {k: v.__dict__ for k, v in selector.benchmarks.items()}
        }

    return asyncio.run(run_comparison())


if __name__ == '__main__':
    # 執行獨立展示
    asyncio.run(demo_model_comparison())

#!/usr/bin/env python3
# 版權所有 2025 Google LLC
#
# 根據 Apache License 2.0 版本（「本授權」）授權；
# 除非遵守本授權，否則您不得使用此檔案。
# 您可以在以下網址取得授權副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據本授權分發的軟體
# 是按「現狀」基礎分發的，不附帶任何明示或暗示的保證或條件。
# 請參閱本授權以瞭解管理權限和限制的具體語言。

"""
ADK 快取分析實驗 (Cache Performance Experiments)

此腳本執行兩個實驗來比較快取效能：
A. Gemini 2.0 Flash：啟用與停用快取（顯式快取測試）
B. Gemini 2.5 Flash：隱式與顯式快取的比較
"""

import argparse
import asyncio
import copy
import json
import logging
import sys
import time
from typing import Any
from typing import Dict
from typing import List

try:
    # 優先嘗試相對導入（作為模組執行時）
    from .agent import app
    from .utils import get_test_prompts
    from .utils import run_experiment_batch
except ImportError:
    # 回退到直接導入（作為腳本執行時）
    from agent import app
    from utils import get_test_prompts
    from utils import run_experiment_batch

from google.adk.cli.utils import logs
from google.adk.runners import InMemoryRunner
from google.adk.utils.cache_performance_analyzer import CachePerformanceAnalyzer

APP_NAME = "cache_analysis_experiments"
USER_ID = "cache_researcher"

# --- 核心重點摘要 ---
# - **核心概念**：透過自動化腳本比較不同模型（Gemini 2.0 vs 2.5）與快取機制（顯式 vs 隱式）對效能與 Token 使用量的影響。
# - **關鍵技術**：
#   - 使用 Google ADK 的 `ContextCacheConfig` 進行顯式快取配置。
#   - 透過 `CachePerformanceAnalyzer` 深入分析快取命中率（Cache Hit Ratio）與利用率（Utilization）。
#   - 支援多輪實驗取平均值（Averaged Results），提高數據可靠性。
# - **重要結論**：顯式快取可有效減少重複 Prompt 的 Token 消耗，優化大型應用的延遲與成本。
# - **行動項目**：可調整 `min_tokens` 與 `ttl_seconds` 參數，針對特定業務場景優化快取策略。


def create_agent_variant(base_app, model_name: str, cache_enabled: bool):
    """建立具有指定模型和快取設定的應用程式變體。"""
    import datetime

    from google.adk.agents.context_cache_config import ContextCacheConfig
    from google.adk.apps.app import App

    # 複製原始 Agent 並修改其模型
    agent_copy = copy.deepcopy(base_app.root_agent)
    agent_copy.model = model_name

    # 在指令前加上動態時間戳記，避免各次執行間意外重用隱式快取
    current_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dynamic_prefix = f"Current session started at: {current_timestamp}\n\n"
    agent_copy.instruction = dynamic_prefix + agent_copy.instruction

    # 更新 Agent 名稱以反映其配置
    cache_status = "cached" if cache_enabled else "no_cache"
    agent_copy.name = f"cache_analysis_{model_name.replace('.', '_').replace('-', '_')}_{cache_status}"

    if cache_enabled:
        # 使用標準化的顯式快取配置
        cache_config = ContextCacheConfig(
            min_tokens=4096,
            ttl_seconds=600,  # 研究工作階段設定為 10 分鐘
            cache_intervals=3,  # 快取重新整理前的最大呼叫次數
        )
    else:
        # 將配置設為 None 以停用快取
        cache_config = None

    # 建立具有更新配置的新 App
    app_copy = App(
        name=f"{base_app.name}_{cache_status}",
        root_agent=agent_copy,
        context_cache_config=cache_config,
    )

    return app_copy


async def run_cache_comparison_experiment(
    model_name: str,
    description: str,
    cached_label: str,
    uncached_label: str,
    experiment_title: str,
    reverse_order: bool = False,
    request_delay: float = 2.0,
) -> Dict[str, Any]:
    """
    針對特定模型執行快取效能比較實驗。

    引數:
        model_name: 要測試的模型 (例如 "gemini-2.0-flash", "gemini-2.5-flash")
        description: 實驗測試內容說明
        cached_label: 已快取變體的標籤
        uncached_label: 未快取變體的標籤
        experiment_title: 顯示的實驗標題

    傳回:
        包含實驗結果與效能比較的字典
    """
    print("=" * 80)
    print(f"實驗 {model_name}: {experiment_title}")
    print("=" * 80)
    print(f"測試說明: {description}")
    print(f"模型: {model_name}")
    print()

    # 1. 建立 App 變體
    app_cached = create_agent_variant(app, model_name, cache_enabled=True)
    app_uncached = create_agent_variant(app, model_name, cache_enabled=False)

    # 2. 取得測試提示 (Prompts)
    prompts = get_test_prompts()

    # 3. 建立執行器 (Runners)
    runner_cached = InMemoryRunner(app=app_cached, app_name=None)
    runner_uncached = InMemoryRunner(app=app_uncached, app_name=None)

    # 4. 為每個實驗建立獨立工作階段 (Sessions) 以避免交叉污染
    session_cached = await runner_cached.session_service.create_session(
        app_name=runner_cached.app_name, user_id=USER_ID
    )
    session_uncached = await runner_uncached.session_service.create_session(
        app_name=runner_uncached.app_name, user_id=USER_ID
    )

    # 5. 執行實驗批次
    if not reverse_order:  # 預設：先執行未快取版本
        print("▶️ 正在按預設順序執行實驗 (先執行未快取版本)")
        print()

        # 測試未快取版本
        results_uncached = await run_experiment_batch(
            app_uncached.root_agent.name,
            runner_uncached,
            USER_ID,
            session_uncached.id,
            prompts,
            f"Experiment {model_name} - {uncached_label}",
            request_delay=request_delay,
        )

        # 實驗間簡短暫停
        await asyncio.sleep(5)

        # 測試已快取版本
        results_cached = await run_experiment_batch(
            app_cached.root_agent.name,
            runner_cached,
            USER_ID,
            session_cached.id,
            prompts,
            f"Experiment {model_name} - {cached_label}",
            request_delay=request_delay,
        )
    else:
        print("🔄 正在按交替順序執行實驗 (先執行已快取版本)")
        print()

        # 測試已快取版本
        results_cached = await run_experiment_batch(
            app_cached.root_agent.name,
            runner_cached,
            USER_ID,
            session_cached.id,
            prompts,
            f"Experiment {model_name} - {cached_label}",
            request_delay=request_delay,
        )

        # 實驗間簡短暫停
        await asyncio.sleep(5)

        # 測試未快取版本
        results_uncached = await run_experiment_batch(
            app_uncached.root_agent.name,
            runner_uncached,
            USER_ID,
            session_uncached.id,
            prompts,
            f"Experiment {model_name} - {uncached_label}",
            request_delay=request_delay,
        )

    # 6. 使用 CachePerformanceAnalyzer 分析快取效能
    performance_analysis = await analyze_cache_performance_from_sessions(
        runner_cached,
        session_cached,
        runner_uncached,
        session_uncached,
        model_name,
    )

    # 7. 從分析器提取指標以保持向後相容性
    cached_analysis = performance_analysis.get("cached_analysis", {})
    uncached_analysis = performance_analysis.get("uncached_analysis", {})

    cached_total_prompt_tokens = cached_analysis.get("total_prompt_tokens", 0)
    cached_total_cached_tokens = cached_analysis.get("total_cached_tokens", 0)
    cached_cache_hit_ratio = cached_analysis.get("cache_hit_ratio_percent", 0.0)
    cached_cache_utilization_ratio = cached_analysis.get(
        "cache_utilization_ratio_percent", 0.0
    )
    cached_avg_cached_tokens_per_request = cached_analysis.get(
        "avg_cached_tokens_per_request", 0.0
    )
    cached_requests_with_hits = cached_analysis.get("requests_with_cache_hits", 0)
    total_cached_requests = cached_analysis.get("total_requests", 0)

    uncached_total_prompt_tokens = uncached_analysis.get("total_prompt_tokens", 0)
    uncached_total_cached_tokens = uncached_analysis.get("total_cached_tokens", 0)
    uncached_cache_hit_ratio = uncached_analysis.get("cache_hit_ratio_percent", 0.0)
    uncached_cache_utilization_ratio = uncached_analysis.get(
        "cache_utilization_ratio_percent", 0.0
    )
    uncached_avg_cached_tokens_per_request = uncached_analysis.get(
        "avg_cached_tokens_per_request", 0.0
    )
    uncached_requests_with_hits = uncached_analysis.get("requests_with_cache_hits", 0)
    total_uncached_requests = uncached_analysis.get("total_requests", 0)

    summary = {
        "experiment": model_name,
        "description": description,
        "model": model_name,
        "cached_results": results_cached,
        "uncached_results": results_uncached,
        "cache_analysis": {
            "cached_experiment": {
                "cache_hit_ratio_percent": cached_cache_hit_ratio,
                "cache_utilization_ratio_percent": cached_cache_utilization_ratio,
                "total_prompt_tokens": cached_total_prompt_tokens,
                "total_cached_tokens": cached_total_cached_tokens,
                "avg_cached_tokens_per_request": (cached_avg_cached_tokens_per_request),
                "requests_with_cache_hits": cached_requests_with_hits,
                "total_requests": total_cached_requests,
            },
            "uncached_experiment": {
                "cache_hit_ratio_percent": uncached_cache_hit_ratio,
                "cache_utilization_ratio_percent": (uncached_cache_utilization_ratio),
                "total_prompt_tokens": uncached_total_prompt_tokens,
                "total_cached_tokens": uncached_total_cached_tokens,
                "avg_cached_tokens_per_request": (
                    uncached_avg_cached_tokens_per_request
                ),
                "requests_with_cache_hits": uncached_requests_with_hits,
                "total_requests": total_uncached_requests,
            },
        },
    }

    print(f"📊 實驗 {model_name} 快取分析結果：")
    print(f"   🔥 {cached_label}:")
    print(
        f"      快取命中率 (Hit Ratio): {cached_cache_hit_ratio:.1f}%"
        f" ({cached_total_cached_tokens:,} /"
        f" {cached_total_prompt_tokens:,} tokens)"
    )
    print(
        f"      快取利用率 (Utilization): {cached_cache_utilization_ratio:.1f}%"
        f" ({cached_requests_with_hits}/{total_cached_requests} requests)"
    )
    print(
        "      平均每次請求快取 Token 數:"
        f" {cached_avg_cached_tokens_per_request:.0f}"
    )
    print(f"   ❄️  {uncached_label}:")
    print(
        f"      快取命中率 (Hit Ratio): {uncached_cache_hit_ratio:.1f}%"
        f" ({uncached_total_cached_tokens:,} /"
        f" {uncached_total_prompt_tokens:,} tokens)"
    )
    print(
        f"      快取利用率 (Utilization): {uncached_cache_utilization_ratio:.1f}%"
        f" ({uncached_requests_with_hits}/{total_uncached_requests} requests)"
    )
    print(
        "      平均每次請求快取 Token 數:"
        f" {uncached_avg_cached_tokens_per_request:.0f}"
    )
    print()

    # 將詳細效能分析加入摘要
    summary["performance_analysis"] = performance_analysis

    return summary


async def analyze_cache_performance_from_sessions(
    runner_cached,
    session_cached,
    runner_uncached,
    session_uncached,
    model_name: str,
) -> Dict[str, Any]:
    """使用 CachePerformanceAnalyzer 分析快取效能。"""
    print("📊 正在透過 CachePerformanceAnalyzer 進行快取分析...")

    analyzer_cached = CachePerformanceAnalyzer(runner_cached.session_service)
    analyzer_uncached = CachePerformanceAnalyzer(runner_uncached.session_service)

    # A. 分析已快取實驗
    try:
        cached_analysis = await analyzer_cached.analyze_agent_cache_performance(
            session_cached.id,
            USER_ID,
            runner_cached.app_name,
            f"cache_analysis_{model_name.replace('.', '_').replace('-', '_')}_cached",
        )
        print(f"  🔥 已快取實驗分析 (Cached Experiment):")
        print(f"     狀態: {cached_analysis['status']}")
        if cached_analysis["status"] == "active":
            print(
                "     快取命中率:"
                f" {cached_analysis['cache_hit_ratio_percent']:.1f}%"
                f" ({cached_analysis['total_cached_tokens']:,} /"
                f" {cached_analysis['total_prompt_tokens']:,} tokens)"
            )
            print(
                "     快取利用率:"
                f" {cached_analysis['cache_utilization_ratio_percent']:.1f}%"
                f" ({cached_analysis['requests_with_cache_hits']}/{cached_analysis['total_requests']} requests)"
            )
            print(
                "     平均每次請求快取 Token 數:"
                f" {cached_analysis['avg_cached_tokens_per_request']:.0f}"
            )
            print(f"     帶快取的請求數: {cached_analysis['requests_with_cache']}")
            print(
                "     平均已用呼叫次數 (Avg invocations used):"
                f" {cached_analysis['avg_invocations_used']:.1f}"
            )
            print(f"     快取重新整理次數: {cached_analysis['cache_refreshes']}")
            print(f"     總呼叫次數: {cached_analysis['total_invocations']}")
    except Exception as e:
        print(f"     ❌ 分析已快取實驗時出錯: {e}")
        cached_analysis = {"status": "error", "error": str(e)}

    # B. 分析未快取實驗
    try:
        uncached_analysis = await analyzer_uncached.analyze_agent_cache_performance(
            session_uncached.id,
            USER_ID,
            runner_uncached.app_name,
            f"cache_analysis_{model_name.replace('.', '_').replace('-', '_')}_no_cache",
        )
        print(f"  ❄️  未快取實驗分析 (Uncached Experiment):")
        print(f"     狀態: {uncached_analysis['status']}")
        if uncached_analysis["status"] == "active":
            print(
                "     快取命中率:"
                f" {uncached_analysis['cache_hit_ratio_percent']:.1f}%"
                f" ({uncached_analysis['total_cached_tokens']:,} /"
                f" {uncached_analysis['total_prompt_tokens']:,} tokens)"
            )
            print(
                "     快取利用率:"
                f" {uncached_analysis['cache_utilization_ratio_percent']:.1f}%"
                f" ({uncached_analysis['requests_with_cache_hits']}/{uncached_analysis['total_requests']} requests)"
            )
            print(
                "     平均每次請求快取 Token 數:"
                f" {uncached_analysis['avg_cached_tokens_per_request']:.0f}"
            )
            print("     帶快取的請求數:" f" {uncached_analysis['requests_with_cache']}")
            print(
                "     平均已用呼叫次數:"
                f" {uncached_analysis['avg_invocations_used']:.1f}"
            )
            print(f"     快取重新整理次數: {uncached_analysis['cache_refreshes']}")
            print(f"     總呼叫次數: {uncached_analysis['total_invocations']}")
    except Exception as e:
        print(f"     ❌ 分析未快取實驗時出錯: {e}")
        uncached_analysis = {"status": "error", "error": str(e)}

    print()

    return {
        "cached_analysis": cached_analysis,
        "uncached_analysis": uncached_analysis,
    }


def get_experiment_labels(model_name: str) -> Dict[str, str]:
    """取得指定模型的實驗標籤和標題。"""
    # 根據模型名稱判斷實驗類型
    if "2.5" in model_name:
        # Gemini 2.5 模型具有隱式快取 (Implicit Caching)
        return {
            "description": "Google 隱式快取 vs ADK 顯式快取",
            "cached_label": "顯式快取 (Explicit)",
            "uncached_label": "隱式快取 (Implicit)",
            "experiment_title": "隱式與顯式快取比較",
        }
    else:
        # 其他模型 (2.0 等) 測試啟用顯式快取 vs 停用快取
        return {
            "description": "ADK 顯式快取啟用 vs 停用",
            "cached_label": "已快取 (Cached)",
            "uncached_label": "未快取 (Uncached)",
            "experiment_title": "快取效能比較",
        }


def calculate_averaged_results(
    all_results: List[Dict[str, Any]], model_name: str
) -> Dict[str, Any]:
    """計算多次實驗執行的平均結果。"""
    if not all_results:
        raise ValueError("沒有可計算平均值的結果")

    # 計算平均快取指標
    cache_hit_ratios = [
        r["cache_analysis"]["cache_hit_ratio_percent"] for r in all_results
    ]
    cache_utilization_ratios = [
        r["cache_analysis"]["cache_utilization_ratio_percent"] for r in all_results
    ]
    total_prompt_tokens = [
        r["cache_analysis"]["total_prompt_tokens"] for r in all_results
    ]
    total_cached_tokens = [
        r["cache_analysis"]["total_cached_tokens"] for r in all_results
    ]
    avg_cached_tokens_per_request = [
        r["cache_analysis"]["avg_cached_tokens_per_request"] for r in all_results
    ]
    requests_with_cache_hits = [
        r["cache_analysis"]["requests_with_cache_hits"] for r in all_results
    ]

    def safe_average(values):
        """計算平均值，處理空列表情況。"""
        return sum(values) / len(values) if values else 0.0

    # 建立平均結果
    averaged_result = {
        "experiment": model_name,
        "description": all_results[0]["description"],
        "model": model_name,
        "individual_runs": (all_results),  # 保留所有個別執行結果供參考
        "averaged_cache_analysis": {
            "cache_hit_ratio_percent": safe_average(cache_hit_ratios),
            "cache_utilization_ratio_percent": safe_average(cache_utilization_ratios),
            "total_prompt_tokens": safe_average(total_prompt_tokens),
            "total_cached_tokens": safe_average(total_cached_tokens),
            "avg_cached_tokens_per_request": safe_average(
                avg_cached_tokens_per_request
            ),
            "requests_with_cache_hits": safe_average(requests_with_cache_hits),
        },
        "statistics": {
            "runs_completed": len(all_results),
            "cache_hit_ratio_std": _calculate_std(cache_hit_ratios),
            "cache_utilization_std": _calculate_std(cache_utilization_ratios),
            "cached_tokens_per_request_std": _calculate_std(
                avg_cached_tokens_per_request
            ),
        },
    }

    # 列印平均結果
    print("\n📊 快取分析平均結果：")
    print("=" * 80)
    avg_cache = averaged_result["averaged_cache_analysis"]
    stats = averaged_result["statistics"]

    print(f"   完成輪數: {stats['runs_completed']}")
    print(
        f"   平均快取命中率: {avg_cache['cache_hit_ratio_percent']:.1f}%"
        f" (±{stats['cache_hit_ratio_std']:.1f}%)"
    )
    print(
        "   平均快取利用率:"
        f" {avg_cache['cache_utilization_ratio_percent']:.1f}%"
        f" (±{stats['cache_utilization_std']:.1f}%)"
    )
    print(
        "   平均每次請求快取 Token 數:"
        f" {avg_cache['avg_cached_tokens_per_request']:.0f}"
        f" (±{stats['cached_tokens_per_request_std']:.0f})"
    )
    print()

    return averaged_result


def _calculate_std(values):
    """計算標準差。"""
    if len(values) <= 1:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return variance**0.5


def save_results(results: Dict[str, Any], filename: str):
    """將實驗結果儲存到 JSON 檔案。"""
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    print(f"💾 結果已儲存至: {filename}")


async def main():
    """針對特定模型執行快取效能實驗。"""
    parser = argparse.ArgumentParser(description="ADK 快取效能實驗工具")
    parser.add_argument(
        "model",
        help="要測試的模型 (例如 gemini-2.5-flash, gemini-2.0-flash-001)",
    )
    parser.add_argument(
        "--output",
        help="結果的輸出檔名 (預設: cache_{model}_results.json)",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help=("每個實驗重複執行的次數以取得平均結果" " (預設: 1)"),
    )
    parser.add_argument(
        "--cached-first",
        action="store_true",
        help="優先執行已快取實驗 (預設：先執行未快取實驗)",
    )
    parser.add_argument(
        "--request-delay",
        type=float,
        default=2.0,
        help=("API 請求間的延遲秒數，避免超載 (預設:" " 2.0)"),
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="設定日誌等級 (預設: INFO)",
    )

    args = parser.parse_args()

    # 設定指定等級的日誌記錄器
    log_level = getattr(logging, args.log_level.upper())
    logs.setup_adk_logger(log_level)

    # 根據模型設定預設輸出檔名
    if not args.output:
        args.output = (
            f"cache_{args.model.replace('.', '_').replace('-', '_')}_results.json"
        )

    print("🧪 ADK 上下文快取 (CONTEXT CACHE) 效能實驗")
    print("=" * 80)
    print(f"開始時間: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"測試模型: {args.model}")
    print(f"重複輪數: {args.repeat}")
    print()

    start_time = time.time()

    try:
        # 取得模型的實驗標籤
        labels = get_experiment_labels(args.model)

        # 若 repeat > 1，則執行多次實驗
        if args.repeat == 1:
            # 單次執行
            result = await run_cache_comparison_experiment(
                model_name=args.model,
                reverse_order=args.cached_first,
                request_delay=args.request_delay,
                **labels,
            )
        else:
            # 多次執行並計算平均值
            print(f"🔄 正在執行實驗 {args.repeat} 次以取得平均結果")
            print("=" * 80)

            all_results = []
            for run_num in range(args.repeat):
                print(f"\n🏃 執行輪次 {run_num + 1}/{args.repeat}")
                print("-" * 40)

                run_result = await run_cache_comparison_experiment(
                    model_name=args.model,
                    reverse_order=args.cached_first,
                    request_delay=args.request_delay,
                    **labels,
                )
                all_results.append(run_result)

                # 輪次間簡短暫停
                if run_num < args.repeat - 1:
                    print("⏸️  輪次間暫停 10 秒...")
                    await asyncio.sleep(10)

            # 計算平均結果
            result = calculate_averaged_results(all_results, args.model)

        # 加入完成元數據 (Metadata)
        result["end_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        result["total_duration"] = time.time() - start_time
        result["repetitions"] = args.repeat

    except KeyboardInterrupt:
        print("\n⚠️ 實驗被使用者中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 實驗失敗: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    # 儲存結果
    save_results(result, args.output)

    # 列印最終摘要
    print("=" * 80)
    print("🎉 實驗順利完成！")
    print("=" * 80)

    # 處理單次和平均結果的顯示
    if args.repeat == 1:
        cached_exp = result["cache_analysis"]["cached_experiment"]
        uncached_exp = result["cache_analysis"]["uncached_experiment"]
        labels = get_experiment_labels(args.model)
        print(f"{args.model}:")
        print(f"  🔥 {labels['cached_label']}:")
        print(f"    快取命中率: {cached_exp['cache_hit_ratio_percent']:.1f}%")
        print(
            "    快取利用率:" f" {cached_exp['cache_utilization_ratio_percent']:.1f}%"
        )
        print(
            "    每次請求快取 Token 數:"
            f" {cached_exp['avg_cached_tokens_per_request']:.0f}"
        )
        print(f"  ❄️  {labels['uncached_label']}:")
        print(f"    快取命中率: {uncached_exp['cache_hit_ratio_percent']:.1f}%")
        print(
            "    快取利用率:" f" {uncached_exp['cache_utilization_ratio_percent']:.1f}%"
        )
        print(
            "    每次請求快取 Token 數:"
            f" {uncached_exp['avg_cached_tokens_per_request']:.0f}"
        )
    else:
        # 針對平均結果顯示摘要比較
        cached_exp = result["averaged_cache_analysis"]["cached_experiment"]
        uncached_exp = result["averaged_cache_analysis"]["uncached_experiment"]
        labels = get_experiment_labels(args.model)
        print(f"{args.model} (經 {args.repeat} 輪平均):")
        print(f"  🔥 {labels['cached_label']} vs ❄️  {labels['uncached_label']}:")
        print(
            f"    快取命中率: {cached_exp['cache_hit_ratio_percent']:.1f}% vs"
            f" {uncached_exp['cache_hit_ratio_percent']:.1f}%"
        )
        print(
            "    快取利用率:"
            f" {cached_exp['cache_utilization_ratio_percent']:.1f}% vs"
            f" {uncached_exp['cache_utilization_ratio_percent']:.1f}%"
        )

    print(f"\n總執行時間: {result['total_duration']:.2f} 秒")
    print(f"結果已儲存至: {args.output}")


if __name__ == "__main__":
    asyncio.run(main())

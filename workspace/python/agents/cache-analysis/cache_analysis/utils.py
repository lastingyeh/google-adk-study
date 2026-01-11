# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""用於快取分析實驗（Cache Analysis Experiments）的公用函式。"""

import asyncio
import time
from typing import Any, Dict, List

from google.adk.runners import InMemoryRunner


async def call_agent_async(
    runner: InMemoryRunner, user_id: str, session_id: str, prompt: str
) -> Dict[str, Any]:
    """
    以非同步方式呼叫代理（Agent），並傳回包含 Token 使用量（Token Usage）的響應。

    程式碼流程：
    1. 初始化響應內容列表與 Token 使用量計數器。
    2. 使用 runner.run_async 啟動代理。
    3. 迭代非同步串流中的每個事件（Event）。
    4. 提取文字內容（Text Content）並累加 Token 使用量數據（提示、候選、快取、總量）。
    5. 組合最終文字並傳回。
    """
    from google.genai import types

    response_parts = []
    # 初始化 Token 使用量字典
    token_usage = {
        "prompt_token_count": 0,          # 提示 Token 數
        "candidates_token_count": 0,      # 候選（回答）Token 數
        "cached_content_token_count": 0,  # 快取內容 Token 數
        "total_token_count": 0,           # 總 Token 數
    }

    # 執行非同步代理調用
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(parts=[types.Part(text=prompt)], role="user"),
    ):
        # 處理輸出的文字片段
        if event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    response_parts.append(part.text)

        # 收集並累計 Token 使用量資訊（Usage Metadata）
        if event.usage_metadata:
            if (
                hasattr(event.usage_metadata, "prompt_token_count")
                and event.usage_metadata.prompt_token_count
            ):
                token_usage["prompt_token_count"] += event.usage_metadata.prompt_token_count
            if (
                hasattr(event.usage_metadata, "candidates_token_count")
                and event.usage_metadata.candidates_token_count
            ):
                token_usage["candidates_token_count"] += event.usage_metadata.candidates_token_count
            if (
                hasattr(event.usage_metadata, "cached_content_token_count")
                and event.usage_metadata.cached_content_token_count
            ):
                token_usage["cached_content_token_count"] += event.usage_metadata.cached_content_token_count
            if (
                hasattr(event.usage_metadata, "total_token_count")
                and event.usage_metadata.total_token_count
            ):
                token_usage["total_token_count"] += event.usage_metadata.total_token_count

    response_text = "".join(response_parts)

    return {"response_text": response_text, "token_usage": token_usage}


def get_test_prompts() -> List[str]:
    """
    獲取快取分析實驗的標準測試提示（Test Prompts）集。

    設計用於一致的行為觀察：
    - 提示 1-5：不會觸發函式調用（Function Calls），僅為一般問題。
    - 提示 6-10：會觸發函式調用，包含具體的工具請求。
    """
    return [
        # === 不會觸發函式調用的提示 ===
        #（不匹配具體工具說明的通用問題）
        "你好，你能為我做什麼？",
        "什麼是人工智慧？它在現代應用中是如何運作的？",
        "請解釋機器學習（Machine Learning）與深度學習（Deep Learning）之間的差異。",
        "在大規模實施 AI 系統時，主要的挑戰有哪些？",
        "現代電子商務平台中的推薦系統（Recommendation Systems）是如何運作的？",
        # === 會觸發函式調用的提示 ===
        #（明確指定了所有必要參數的具體請求）
        (
            "使用 benchmark_performance 並設定 system_name='E-commerce Platform',"
            " metrics=['latency', 'throughput'], duration='standard',"
            " load_profile='realistic'。"
        ),
        (
            "呼叫 analyze_user_behavior_patterns 並設定"
            " user_segment='premium_customers', time_period='last_30_days',"
            " metrics=['engagement', 'conversion']。"
        ),
        (
            "針對 industry='fintech', focus_areas=['user_experience', 'security'],"
            " report_depth='comprehensive' 執行 market_research_analysis。"
        ),
        (
            "對 competitors=['Netflix', 'Disney+'], analysis_type='feature_comparison',"
            " output_format='detailed' 執行 competitive_analysis。"
        ),
        (
            "對 content_type='video', platform='social_media', "
            "success_metrics=['views', 'engagement'] 進行 content_performance_evaluation。"
        ),
    ]


async def run_experiment_batch(
    agent_name: str,
    runner: InMemoryRunner,
    user_id: str,
    session_id: str,
    prompts: List[str],
    experiment_name: str,
    request_delay: float = 2.0,
) -> Dict[str, Any]:
    """
    執行一批提示（Batch Prompts）並收集快取指標（Cache Metrics）。

    程式碼流程：
    1. 遍歷提示列表，逐一呼叫 call_agent_async。
    2. 記錄每個提示的執行結果、Token 使用情況與是否成功。
    3. 在請求之間插入可配置的延遲（Delay）以避免 API 過載。
    4. 統計該批次（Batch）的快取命中率（Cache Hit Ratio）與快取利用率（Cache Utilization）。
    5. 產出並印出完整的實驗摘要報告。
    """
    results = []

    print(f"🧪 正在執行 {experiment_name}")
    print(f"代理名稱: {agent_name}")
    print(f"會話 ID: {session_id}")
    print(f"提示數量: {len(prompts)}")
    print(f"請求間隔延遲: {request_delay} 秒")
    print("-" * 60)

    for i, prompt in enumerate(prompts, 1):
        print(f"[{i}/{len(prompts)}] 正在執行測試提示...")
        print(f"提示內容: {prompt[:100]}...")

        try:
            agent_response = await call_agent_async(
                runner, user_id, session_id, prompt
            )

            result = {
                "prompt_number": i,
                "prompt": prompt,
                "response_length": len(agent_response["response_text"]),
                "success": True,
                "error": None,
                "token_usage": agent_response["token_usage"],
            }

            # 提取個別提示統計的 Token 使用量
            prompt_tokens = agent_response["token_usage"].get("prompt_token_count", 0)
            cached_tokens = agent_response["token_usage"].get(
                "cached_content_token_count", 0
            )

            print(
                f"✅ 完成 (響應長度: {len(agent_response['response_text'])} 字元)"
            )
            print(
                f"   📊 Tokens - 提示: {prompt_tokens:,}, 快取: {cached_tokens:,}"
            )

        except Exception as e:
            result = {
                "prompt_number": i,
                "prompt": prompt,
                "response_length": 0,
                "success": False,
                "error": str(e),
                "token_usage": {
                    "prompt_token_count": 0,
                    "candidates_token_count": 0,
                    "cached_content_token_count": 0,
                    "total_token_count": 0,
                },
            }

            print(f"❌ 失敗: {e}")

        results.append(result)

        # 在請求之間進行可配置的暫停，以避免 API 超載
        if i < len(prompts):  # 最後一個請求後不需要睡眠
            print(f"   Wait ⏸️  等待 {request_delay} 秒後進行下一個請求...")
            await asyncio.sleep(request_delay)

    successful_requests = sum(1 for r in results if r["success"])

    # 計算此批次的快取統計數據
    total_prompt_tokens = sum(
        r.get("token_usage", {}).get("prompt_token_count", 0) for r in results
    )
    total_cached_tokens = sum(
        r.get("token_usage", {}).get("cached_content_token_count", 0)
        for r in results
    )

    # 計算快取命中率 (Cache Hit Ratio)
    if total_prompt_tokens > 0:
        cache_hit_ratio = (total_cached_tokens / total_prompt_tokens) * 100
    else:
        cache_hit_ratio = 0.0

    # 計算快取利用率 (Cache Utilization)
    requests_with_cache_hits = sum(
        1
        for r in results
        if r.get("token_usage", {}).get("cached_content_token_count", 0) > 0
    )
    cache_utilization_ratio = (
        (requests_with_cache_hits / len(prompts)) * 100 if prompts else 0.0
    )

    # 平均每次請求的快取 Token 數
    avg_cached_tokens_per_request = (
        total_cached_tokens / len(prompts) if prompts else 0.0
    )

    summary = {
        "experiment_name": experiment_name,
        "agent_name": agent_name,
        "total_requests": len(prompts),
        "successful_requests": successful_requests,
        "results": results,
        "cache_statistics": {
            "cache_hit_ratio_percent": cache_hit_ratio,
            "cache_utilization_ratio_percent": cache_utilization_ratio,
            "total_prompt_tokens": total_prompt_tokens,
            "total_cached_tokens": total_cached_tokens,
            "avg_cached_tokens_per_request": avg_cached_tokens_per_request,
            "requests_with_cache_hits": requests_with_cache_hits,
        },
    }

    print("-" * 60)
    print(f"✅ {experiment_name} 執行完畢:")
    print(f"   總請求數: {len(prompts)}")
    print(f"   成功次數: {successful_requests}/{len(prompts)}")
    print("   📊 批次快取統計 (BATCH CACHE STATISTICS):")
    print(
        f"      快取命中率: {cache_hit_ratio:.1f}%"
        f" ({total_cached_tokens:,} / {total_prompt_tokens:,} tokens)"
    )
    print(
        f"      快取利用率: {cache_utilization_ratio:.1f}%"
        f" ({requests_with_cache_hits}/{len(prompts)} 請求)"
    )
    print(f"      平均每次請求快取 Token: {avg_cached_tokens_per_request:.0f}")
    print()

    return summary

# 教學 22：模型選擇與最佳化 (Tutorial 22: Model Selection & Optimization)

**目標**: 掌握模型選擇策略，了解模型的能力與限制，最佳化成本與效能，並為特定使用情境選擇正確的模型。

**先決條件**:

- 教學 01 (Hello World Agent)
- 了解基本的 Agent 概念
- 熟悉不同的 Agent 能力

**您將學到**:

- Gemini 模型家族概覽與比較
- 模型能力矩陣 (視覺、思考、程式碼執行等)
- 效能與成本的權衡
- Context Window 與 Token 限制
- 模型選擇決策框架
- 測試與基準策略
- 模型之間的遷移策略

**完成時間**: 45-60 分鐘

---

## 為何模型選擇如此重要 (Why Model Selection Matters)

**問題**: 不同的模型具有不同的能力、成本和效能特性。選擇錯誤的模型會導致結果不佳或不必要的成本。

**解決方案**: 根據需求、使用情境、預算和效能需求進行**策略性模型選擇**。

**優點**:

- 💰 **成本最佳化**: 只為您需要的能力付費
- ⚡ **效能**: 為您的應用程式提供合適的速度
- 🎯 **能力匹配**: 模型具備您所需的功能
- 📊 **品質**: 為您的特定使用情境提供最佳結果
- [FLOW]**擴展性**: 能夠處理您的負載的模型

**決策因素**:

- 任務複雜度
- 回應時間要求
- 預算限制
- 功能需求 (視覺、思考、程式碼執行)
- Context Window 需求
- 部署環境

---

## 1. Gemini 模型家族概覽 (1. Gemini Model Family Overview)

### 目前模型陣容 (2025) (Current Model Lineup (2025))

**來源**: ADK 透過 Google AI 和 Vertex AI 支援所有 Gemini 模型

**⚠️ 重要**: 截至 2025 年 10 月，**Gemini 2.5 Flash** 因其出色的性價比，**建議**用於新的 Agent。請注意，ADK 的預設模型參數為空字串 (會從父 Agent 繼承)，因此**請務必明確指定模型**。

| 模型 (Model) | Context Window | 主要功能 (Key Features) | 最適用途 (Best For) | 狀態 (Status) |
| --- | --- | --- | --- | --- |
| **gemini-2.5-flash** ⭐ | 1M tokens | **建議**, 思考, 快速, 多模態 | **通用目的**, 生產環境 | **穩定 (Stable)** |
| **gemini-2.5-pro** | 1M tokens | 最新技術, 複雜推理, STEM | 關鍵分析, 研究 | **穩定 (Stable)** |
| **gemini-2.5-flash-lite** | 1M tokens | 超快, 成本效益高, 高吞吐量 | 大量, 簡單任務 | **預覽 (Preview)** |
| **gemini-2.0-flash** | 1M tokens | 快速, 思考, 程式碼執行 | 通用目的 (舊版) | 穩定 (Stable) |
| **gemini-2.0-flash-thinking** | 1M tokens | 擴展思考模式 | 複雜推理 (舊版) | 穩定 (Stable) |
| **gemini-1.5-flash** | 1M tokens | 快速, 成本效益高 | 大量 (舊版) | 穩定 (Stable) |
| **gemini-1.5-flash-8b** | 1M tokens | 超快, 經濟 | 簡單查詢 (舊版) | 穩定 (Stable) |
| **gemini-1.5-pro** | 2M tokens | 擴展 Context | 大型文件 (舊版) | 穩定 (Stable) |
| **gemini-2.0-flash-live** | 串流 | 雙向音訊/視訊 (Vertex) | 即時對話 | 預覽 (Preview) |
| **gemini-live-2.5-flash** | 串流 | Live API (AI Studio) | 語音助理 | 預覽 (Preview) |

**模型世代**:

- **2.5 系列** (最新, 2025 年 10 月): 首款具備原生思考、圖像生成能力，最佳性價比
- **2.0 系列** (2024 年 12 月): 第二代，程式碼執行，Google Search
- **1.5 系列** (2024 年初): 第一代，多模態基礎

### 🆕 Gemini 2.5 的新功能 (What's New in Gemini 2.5)

**Gemini 2.5 Flash** 是我們在性價比方面最佳的模型：

- ✅ **原生思考能力**: 查看模型的推理過程
- ✅ **圖像生成**: 原生生成和編輯圖像 (2.5 Flash Image 變體)
- ✅ **長 Context**: 100 萬 Token 的 Context Window
- ✅ **多模態**: 理解文字、圖像、音訊、視訊
- ✅ **全能型**: 在編碼、推理、創意寫作方面表現出色
- ✅ **最適合 Agent**: 為大規模處理和 Agent 使用情境進行最佳化

**Gemini 2.5 Pro** 是最先進的思考模型：

- ✅ **進階推理**: 處理程式碼、數學、STEM 中的複雜問題
- ✅ **長 Context 分析**: 分析大型資料集、程式碼庫、文件
- ✅ **最高品質**: 對於關鍵應用程式為同類最佳
- ✅ **研究級**: 適用於學術和專業研究

**官方文件**:

- Google AI: https://ai.google.dev/gemini-api/docs/models
- Vertex AI: https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-flash
- 技術報告: https://storage.googleapis.com/deepmind-media/gemini/gemini_v2_5_report.pdf

### 模型比較矩陣 (Model Comparison Matrix)

```python
"""
模型能力與定價比較。
"""

MODELS = {
    # === GEMINI 2.5 系列 (最新 - 2025 年 10 月) ===
    'gemini-2.5-flash': {
        'context_window': 1_000_000,
        'features': ['vision', 'thinking', 'code_execution', 'audio', 'video', 'image_generation'],
        'speed': 'fast',
        'cost': 'low',
        'quality': 'excellent',
        'is_recommended': True,  # 建議用於新專案的模型
        'generation': '2.5',
        'recommended_for': [
            '⭐ 建議所有新 Agent 使用',
            '一般 Agent 應用',
            '生產系統',
            'Agent 工作流程',
            '最佳性價比'
        ],
        'note': '首款具備原生思考能力的 Flash 模型'
    },
    'gemini-2.5-pro': {
        'context_window': 1_000_000,
        'features': ['vision', 'thinking', 'code_execution', 'audio', 'video', 'advanced_reasoning'],
        'speed': 'moderate',
        'cost': 'high',
        'quality': 'state_of_the_art',
        'generation': '2.5',
        'recommended_for': [
            '複雜推理任務',
            'STEM 問題 (程式碼、數學、物理)',
            '研究與分析',
            '需要最高品質的關鍵應用'
        ],
        'note': '最先進的思考模型'
    },
    'gemini-2.5-flash-lite': {
        'context_window': 1_000_000,
        'features': ['vision', 'audio', 'video', 'ultra_fast'],
        'speed': 'ultra_fast',
        'cost': 'ultra_low',
        'quality': 'good',
        'generation': '2.5',
        'recommended_for': [
            '超高吞吐量應用',
            '大規模簡單查詢',
            '對成本敏感的部署',
            '即時低延遲任務'
        ],
        'note': '最快的 flash 模型，為成本效益最佳化'
    },

    # === GEMINI 2.0 系列 (舊版) ===
    'gemini-2.0-flash': {
        'context_window': 1_000_000,
        'features': ['vision', 'thinking', 'code_execution', 'audio', 'video'],
        'speed': 'fast',
        'cost': 'low',
        'quality': 'high',
        'generation': '2.0',
        'recommended_for': [
            '一般 Agent 應用',
            '生產系統',
            '多 Agent 工作流程',
            '複雜推理'
        ],
        'note': '考慮升級至 gemini-2.5-flash'
    },
    'gemini-2.0-flash-thinking': {
        'context_window': 1_000_000,
        'features': ['vision', 'thinking', 'code_execution', 'extended_reasoning'],
        'speed': 'moderate',
        'cost': 'moderate',
        'quality': 'very_high',
        'generation': '2.0',
        'recommended_for': [
            '策略規劃',
            '複雜問題解決',
            '研究分析',
            '深度推理任務'
        ],
        'note': '考慮使用 gemini-2.5-pro 以獲得更好的推理能力'
    },

    # === GEMINI 1.5 系列 (舊版) ===
    'gemini-1.5-flash': {
        'context_window': 1_000_000,
        'features': ['vision', 'audio', 'video'],
        'speed': 'very_fast',
        'cost': 'very_low',
        'quality': 'good',
        'generation': '1.5',
        'recommended_for': [
            '大量應用',
            '簡單查詢',
            '內容審核',
            '快速回應'
        ],
        'note': '考慮使用 gemini-2.5-flash 以在相似成本下獲得更好效能'
    },
    'gemini-1.5-flash-8b': {
        'context_window': 1_000_000,
        'features': ['vision', 'audio'],
        'speed': 'ultra_fast',
        'cost': 'ultra_low',
        'quality': 'moderate',
        'generation': '1.5',
        'recommended_for': [
            '超高吞吐量',
            '簡單分類',
            '基本問答',
            '對成本敏感的應用'
        ],
        'note': '考慮使用 gemini-2.5-flash-lite 以獲得更好效能'
    },
    'gemini-1.5-pro': {
        'context_window': 2_000_000,
        'features': ['vision', 'audio', 'video', 'extended_context'],
        'speed': 'moderate',
        'cost': 'high',
        'quality': 'excellent',
        'generation': '1.5',
        'recommended_for': [
            '關鍵業務應用',
            '複雜分析',
            '大型文件處理',
            '最高品質要求'
        ],
        'note': '除非需要 2M Token Context，否則考慮使用 gemini-2.5-pro'
    },

    # === 串流模型 ===
    'gemini-2.0-flash-live': {
        'context_window': 'streaming',
        'features': ['vision', 'audio', 'video', 'bidirectional', 'real_time'],
        'speed': 'real_time',
        'cost': 'moderate',
        'quality': 'high',
        'generation': '2.0',
        'recommended_for': [
            '語音助理',
            '即時對話',
            '即時視訊分析',
            '互動式應用'
        ],
        'note': '僅限 Vertex AI'
    }
}


def recommend_model(requirements: dict) -> list:
    """
    根據需求推薦模型。

    Args:
        requirements: 包含 'features', 'speed', 'cost', 'quality' 等鍵的字典

    Returns:
        包含推薦模型名稱與原因的列表
    """

    recommendations = []

    required_features = set(requirements.get('features', []))
    speed_pref = requirements.get('speed', 'any')
    cost_pref = requirements.get('cost', 'any')
    quality_pref = requirements.get('quality', 'any')

    for model_name, model_info in MODELS.items():
        # 檢查功能相容性
        model_features = set(model_info['features'])
        if required_features and not required_features.issubset(model_features):
            continue

        # 檢查速度偏好
        if speed_pref != 'any' and model_info['speed'] != speed_pref:
            continue

        # 檢查成本偏好
        if cost_pref != 'any' and model_info['cost'] != cost_pref:
            continue

        # 檢查品質偏好
        if quality_pref != 'any' and model_info['quality'] != quality_pref:
            continue

        recommendations.append({
            'model': model_name,
            'reason': model_info['recommended_for'][0],
            'features': model_info['features'],
            'speed': model_info['speed'],
            'cost': model_info['cost']
        })

    return recommendations


# 範例用法
requirements = {
    'features': ['vision', 'thinking'],
    'speed': 'fast',
    'cost': 'low'
}

recommended = recommend_model(requirements)
for rec in recommended:
    print(f"✅ {rec['model']}")
    print(f"   原因: {rec['reason']}")
    print(f"   速度: {rec['speed']}, 成本: {rec['cost']}")
```

---

## 2. 功能相容性 (Feature Compatibility)

### 內建工具與功能 (Built-in Tools & Features)

**需要 Gemini 2.0+**:

- ✅ 思考設定 (`types.ThinkingConfig`)
- ✅ 內建程式碼執行 (`BuiltInCodeExecutor`)
- ✅ Google Search 基礎 (原生)
- ✅ 增強的多模態能力

**所有 Gemini 模型**:

- ✅ 函式呼叫
- ✅ 視覺 (圖像理解)
- ✅ 基本多模態 (文字 + 圖像)
- ✅ 自訂工具

**僅限 Live API 模型**:

- ✅ 雙向串流
- ✅ 即時音訊/視訊
- ✅ 主動回應
- ✅ 情感對話 (情緒偵測)

### 功能相容性表格 (Feature Compatibility Table)

```python
FEATURE_COMPATIBILITY = {
    'function_calling': ['all'],
    'vision': ['all'],
    'audio_input': ['all'],

    # Gemini 2.5+ 功能
    'thinking_config': [
        'gemini-2.5-flash',      # 新：首款具備思考能力的 Flash 模型！
        'gemini-2.5-pro',
        'gemini-2.0-flash',
        'gemini-2.0-flash-thinking'
    ],
    'image_generation': [
        'gemini-2.5-flash',      # 新：原生圖像生成
        'gemini-2.5-flash-image'
    ],
    'code_execution': [
        'gemini-2.5-flash',
        'gemini-2.5-pro',
        'gemini-2.0-flash',
        'gemini-2.0-flash-thinking'
    ],
    'google_search': [
        'gemini-2.5-flash',
        'gemini-2.5-pro',
        'gemini-2.0-flash',
        'gemini-2.0-flash-thinking'
    ],

    # 視訊支援
    'video_input': [
        'gemini-2.5-flash',
        'gemini-2.5-pro',
        'gemini-1.5-pro',
        'gemini-1.5-flash',
        'gemini-2.0-flash',
        'gemini-2.0-flash-live'
    ],

    # 串流
    'bidirectional_streaming': [
        'gemini-2.0-flash-live',
        'gemini-live-2.5-flash'
    ],

    # Context windows
    'extended_context': ['gemini-1.5-pro'],  # 2M tokens
    'long_context': [  # 1M tokens
        'gemini-2.5-flash',
        'gemini-2.5-pro',
        'gemini-2.5-flash-lite',
        'gemini-2.0-flash',
        'gemini-1.5-flash',
        'gemini-1.5-flash-8b'
    ],

    # 速度等級
    'ultra_fast': ['gemini-2.5-flash-lite', 'gemini-1.5-flash-8b']
}


def check_feature_support(model: str, feature: str) -> bool:
    """檢查模型是否支援該功能。"""

    if feature not in FEATURE_COMPATIBILITY:
        return False

    supported_models = FEATURE_COMPATIBILITY[feature]

    if 'all' in supported_models:
        return True

    return model in supported_models


# 範例
print(check_feature_support('gemini-2.5-flash', 'thinking_config'))  # True ✅
print(check_feature_support('gemini-2.0-flash', 'thinking_config'))  # True ✅
print(check_feature_support('gemini-1.5-flash', 'thinking_config'))  # False ❌
print(check_feature_support('gemini-2.5-flash', 'image_generation')) # True ✅
```

---

## 3. 真實世界範例：模型選擇框架 (Real-World Example: Model Selection Framework)

讓我們建立一個全面的模型選擇與測試框架。

### 完整實作 (Complete Implementation)

```python
"""
模型選擇與測試框架
幫助選擇正確的模型並進行效能基準測試。
"""

import asyncio
import time
from dataclasses import dataclass
from typing import Dict, List
from google.adk.agents import Agent, Runner
from google.genai import types


@dataclass
class ModelBenchmark:
    """模型的基準測試結果。"""
    model: str
    avg_latency: float
    avg_tokens: int
    quality_score: float
    cost_estimate: float
    success_rate: float


class ModelSelector:
    """選擇與基準測試模型的框架。"""

    def __init__(self):
        """初始化模型選擇器。"""
        self.runner = Runner()
        self.benchmarks: Dict[str, ModelBenchmark] = {}

    async def benchmark_model(
        self,
        model: str,
        test_queries: List[str],
        instruction: str
    ) -> ModelBenchmark:
        """
        對測試查詢進行模型基準測試。

        Args:
            model: 要測試的模型
            test_queries: 測試查詢列表
            instruction: Agent 指令

        Returns:
            包含結果的 ModelBenchmark
        """

        print(f"\n{'='*70}")
        print(f"基準測試中: {model}")
        print(f"{'='*70}\n")

        # 使用此模型建立 agent
        agent = Agent(
            model=model,
            name=f'test_agent_{model.replace(".", "_")}',
            instruction=instruction,
            generate_content_config=types.GenerateContentConfig(
                temperature=0.5,
                max_output_tokens=1024
            )
        )

        latencies = []
        token_counts = []
        successes = 0

        for query in test_queries:
            try:
                start = time.time()

                result = await self.runner.run_async(query, agent=agent)

                latency = time.time() - start
                latencies.append(latency)

                # 估算 token 數量 (粗略)
                text = result.content.parts[0].text
                token_count = len(text.split())
                token_counts.append(token_count)

                successes += 1

                print(f"✅ 查詢: {query[:50]}...")
                print(f"   延遲: {latency:.2f}s, Tokens: ~{token_count}")

            except Exception as e:
                print(f"❌ 查詢失敗: {query[:50]}... - {e}")

        # 計算指標
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        avg_tokens = sum(token_counts) / len(token_counts) if token_counts else 0
        success_rate = successes / len(test_queries)

        # 估算成本 (簡化)
        # 實際定價各不相同 - 請查看 Google Cloud 定價
        cost_per_1k_tokens = {
            'gemini-2.0-flash': 0.0001,
            'gemini-1.5-flash': 0.00008,
            'gemini-1.5-flash-8b': 0.00004,
            'gemini-1.5-pro': 0.0005
        }

        model_key = model
        if model_key not in cost_per_1k_tokens:
            model_key = 'gemini-2.0-flash'

        cost_estimate = (avg_tokens / 1000) * cost_per_1k_tokens[model_key]

        # 品質分數 (基於成功率和延遲)
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

        print(f"\n📊 結果:")
        print(f"   平均延遲: {avg_latency:.2f}s")
        print(f"   平均 Tokens: {avg_tokens:.0f}")
        print(f"   成功率: {success_rate*100:.1f}%")
        print(f"   估算成本: ${cost_estimate:.6f} 每次查詢")
        print(f"   品質分數: {quality_score:.3f}")

        return benchmark

    async def compare_models(
        self,
        models: List[str],
        test_queries: List[str],
        instruction: str
    ):
        """
        在相同查詢上比較多個模型。

        Args:
            models: 要比較的模型列表
            test_queries: 測試查詢
            instruction: Agent 指令
        """

        print(f"\n{'#'*70}")
        print(f"模型比較")
        print(f"{'#'*70}\n")

        for model in models:
            await self.benchmark_model(model, test_queries, instruction)
            await asyncio.sleep(2)

        self._print_comparison()

    def _print_comparison(self):
        """列印比較表。"""

        print(f"\n\n{'='*70}")
        print("比較摘要")
        print(f"{'='*70}\n")

        print(f"{'模型':<30} {'延遲':>10} {'Tokens':>8} {'成本':>10} {'品質':>10}")
        print(f"{'-'*70}")

        for model, bench in self.benchmarks.items():
            print(f"{model:<30} {bench.avg_latency:>9.2f}s {bench.avg_tokens:>8} "
                  f"${bench.cost_estimate:>9.6f} {bench.quality_score:>10.3f}")

        print(f"\n{'='*70}")

        # 建議
        print("\n🎯 建議:\n")

        fastest = min(self.benchmarks.items(), key=lambda x: x[1].avg_latency)
        print(f"⚡ 最快: {fastest[0]} ({fastest[1].avg_latency:.2f}s)")

        cheapest = min(self.benchmarks.items(), key=lambda x: x[1].cost_estimate)
        print(f"💰 最便宜: {cheapest[0]} (${cheapest[1].cost_estimate:.6f})")

        best_quality = max(self.benchmarks.items(), key=lambda x: x[1].quality_score)
        print(f"🏆 最佳品質: {best_quality[0]} ({best_quality[1].quality_score:.3f})")

    def recommend_model_for_use_case(self, use_case: str) -> str:
        """
        根據使用情境推薦模型 (已為 Gemini 2.5 更新)。

        Args:
            use_case: 使用情境描述

        Returns:
            推薦的模型名稱
        """

        use_case_lower = use_case.lower()

        # 基於規則的建議 (Gemini 2.5 系列)
        if 'real-time' in use_case_lower or 'voice' in use_case_lower:
            return 'gemini-2.0-flash-live'

        elif 'complex' in use_case_lower or 'reasoning' in use_case_lower or 'stem' in use_case_lower:
            return 'gemini-2.5-pro'  # 新：最適合複雜問題

        elif 'high-volume' in use_case_lower or 'simple' in use_case_lower or 'ultra-fast' in use_case_lower:
            return 'gemini-2.5-flash-lite'  # 新：最快 + 最便宜

        elif 'critical' in use_case_lower or 'important' in use_case_lower:
            return 'gemini-2.5-pro'  # 新：最高品質

        elif 'extended context' in use_case_lower or 'large document' in use_case_lower:
            return 'gemini-1.5-pro'  # 仍有 2M context

        else:
            return 'gemini-2.5-flash'  # 新的預設！


async def main():
    """主進入點。"""

    selector = ModelSelector()

    # 測試查詢
    test_queries = [
        "法國的首都是什麼？",
        "用簡單的術語解釋量子計算",
        "寫一首關於人工智慧的俳句",
        "計算一萬美元以 5% 的利率複利 10 年的利息",
        "列出 2025 年前五名的程式語言"
    ]

    instruction = """
您是一位樂於助人的助理。請準確簡潔地回答問題。
    """.strip()

    # 比較模型 (已為 Gemini 2.5 更新)
    models_to_test = [
        'gemini-2.5-flash',      # 新的預設 - 最佳性價比
        'gemini-2.5-pro',        # 新 - 最高品質
        'gemini-2.5-flash-lite', # 新 - 超快
        'gemini-2.0-flash',      # 舊版
        'gemini-1.5-flash',      # 舊版
    ]

    await selector.compare_models(models_to_test, test_queries, instruction)

    # 使用情境建議
    print(f"\n\n{'='*70}")
    print("使用情境建議")
    print(f"{'='*70}\n")

    use_cases = [
        "即時語音助理",
        "複雜策略規劃",
        "大量內容審核",
        "關鍵業務決策支援",
        "一般客戶服務"
    ]

    for use_case in use_cases:
        recommendation = selector.recommend_model_for_use_case(use_case)
        print(f"📌 {use_case}")
        print(f"   → 建議: {recommendation}\n")


if __name__ == '__main__':
    asyncio.run(main())
```

### 預期輸出 (Expected Output)

```
======================================================================
基準測試中: gemini-2.0-flash
======================================================================

✅ 查詢: 法國的首都是什麼？...
   延遲: 0.85s, Tokens: ~8
✅ 查詢: 用簡單的術語解釋量子計算...
   延遲: 1.23s, Tokens: ~95
✅ 查詢: 寫一首關於人工智慧的俳句...
   延遲: 0.92s, Tokens: ~25
✅ 查詢: 計算一萬美元以 5% 的利率複利 10 年...
   延遲: 1.15s, Tokens: ~42
✅ 查詢: 列出 2025 年前五名的程式語言...
   延遲: 0.98s, Tokens: ~35

📊 結果:
   平均延遲: 1.03s
   平均 Tokens: 41
   成功率: 100.0%
   估算成本: $0.000004 每次查詢
   品質分數: 0.493

======================================================================
基準測試中: gemini-1.5-flash
======================================================================

✅ 查詢: 法國的首都是什麼？...
   延遲: 0.72s, Tokens: ~7
✅ 查詢: 用簡單的術語解釋量子計算...
   延遲: 1.05s, Tokens: ~88
✅ 查詢: 寫一首關於人工智慧的俳句...
   延遲: 0.78s, Tokens: ~22
✅ 查詢: 計算一萬美元以 5% 的利率複利 10 年...
   延遲: 0.95s, Tokens: ~38
✅ 查詢: 列出 2025 年前五名的程式語言...
   延遲: 0.82s, Tokens: ~32

📊 結果:
   平均延遲: 0.86s
   平均 Tokens: 37
   成功率: 100.0%
   估算成本: $0.000003 每次查詢
   品質分數: 0.537

======================================================================
基準測試中: gemini-1.5-flash-8b
======================================================================

✅ 查詢: 法國的首都是什麼？...
   延遲: 0.58s, Tokens: ~6
✅ 查詢: 用簡單的術語解釋量子計算...
   延遲: 0.89s, Tokens: ~75
✅ 查詢: 寫一首關於人工智慧的俳句...
   延遲: 0.65s, Tokens: ~20
✅ 查詢: 計算一萬美元以 5% 的利率複利 10 年...
   延遲: 0.78s, Tokens: ~32
✅ 查詢: 列出 2025 年前五名的程式語言...
   延遲: 0.68s, Tokens: ~28

📊 結果:
   平均延遲: 0.72s
   平均 Tokens: 32
   成功率: 100.0%
   估算成本: $0.000001 每次查詢
   品質分數: 0.581


======================================================================
比較摘要
======================================================================

模型                            延遲     Tokens       成本      品質
----------------------------------------------------------------------
gemini-2.0-flash                    1.03s       41 $0.000004      0.493
gemini-1.5-flash                    0.86s       37 $0.000003      0.537
gemini-1.5-flash-8b                 0.72s       32 $0.000001      0.581

======================================================================

🎯 建議:

⚡ 最快: gemini-1.5-flash-8b (0.72s)
💰 最便宜: gemini-1.5-flash-8b ($0.000001)
🏆 最佳品質: gemini-1.5-flash-8b (0.581)


======================================================================
使用情境建議
======================================================================

📌 即時語音助理
   → 建議: gemini-2.0-flash-live

📌 複雜策略規劃
   → 建議: gemini-2.0-flash-thinking

📌 大量內容審核
   → 建議: gemini-1.5-flash-8b

📌 關鍵業務決策支援
   → 建議: gemini-1.5-pro

📌 一般客戶服務
   → 建議: gemini-2.0-flash
```

---

## 4. 模型選擇決策樹 (Model Selection Decision Tree)

### 決策框架 (Decision Framework)

```python
def select_model(requirements: dict) -> str:
    """
    模型選擇決策樹 (已為 Gemini 2.5 更新)。

    Args:
        requirements: 包含以下內容的字典：
            - real_time: bool
            - complex_reasoning: bool (STEM, 數學, 程式碼)
            - high_volume: bool
            - vision_required: bool
            - code_execution: bool
            - budget_sensitive: bool
            - ultra_fast: bool
            - critical: bool

    Returns:
        推薦的模型名稱
    """

    # 即時需求 (串流)
    if requirements.get('real_time', False):
        return 'gemini-2.0-flash-live'

    # 複雜推理 (STEM, 研究, 深度分析)
    if requirements.get('complex_reasoning', False):
        return 'gemini-2.5-pro'  # 新：最適合複雜問題

    # 超快需求與預算限制
    if requirements.get('ultra_fast', False) and requirements.get('budget_sensitive', False):
        return 'gemini-2.5-flash-lite'  # 新：最快 + 最便宜

    # 大量 + 對預算敏感 (簡單任務)
    if requirements.get('high_volume', False) and requirements.get('budget_sensitive', False):
        return 'gemini-2.5-flash-lite'  # 新：取代 1.5-flash-8b

    # 需要最高品質的關鍵應用
    if requirements.get('critical', False):
        return 'gemini-2.5-pro'  # 新：最先進的品質

    # 擴展 context (>1M tokens)
    if requirements.get('extended_context', False):
        return 'gemini-1.5-pro'  # 仍有 2M token context

    # 預設：最佳性價比 (新的預設！)
    return 'gemini-2.5-flash'


# 範例 (已為 2.5 更新)
print(select_model({'real_time': True}))
# 輸出: gemini-2.0-flash-live

print(select_model({'complex_reasoning': True}))
# 輸出: gemini-2.5-pro  ← 從 2.0-flash-thinking 更改

print(select_model({'high_volume': True, 'budget_sensitive': True}))
# 輸出: gemini-2.5-flash-lite  ← 從 1.5-flash-8b 更改

print(select_model({}))  # 無需求
# 輸出: gemini-2.5-flash  ← 新的預設！
```

---

## 5. 透過 LiteLLM 使用其他 LLM (Using Other LLMs with LiteLLM)

**來源**: `google/adk/models/lite_llm.py`

雖然 Gemini 模型為 ADK 進行了最佳化並提供最佳整合，但您可以透過 **LiteLLM** 使用**任何 LLM 供應商**。`LiteLlm` 類別包裝了 LiteLLM 函式庫，以提供對 OpenAI、Anthropic、Ollama、Azure 等的統一存取。

### 🌟 為何使用 LiteLLM？ (Why Use LiteLLM?)

- ✅ **供應商彈性**: 無需更改程式碼即可在 OpenAI、Claude、Ollama、Azure 之間切換
- ✅ **成本最佳化**: 比較供應商並選擇最佳性價比
- ✅ **本地模型**: 在本地執行 Ollama 模型以保護隱私/合規性
- ✅ **備援策略**: 使用多個供應商以提高可靠性
- ✅ **統一介面**: 相同的 ADK 程式碼適用於任何 LLM

### 基本 LiteLLM 整合 (Basic LiteLLM Integration)

```python
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents import Agent

# 使用 OpenAI GPT-4 建立 agent
agent = Agent(
    model=LiteLlm(model='openai/gpt-4o'),
    name='openai_agent',
    instruction='您是一位樂於助人的助理。'
)

# 或使用 Anthropic Claude
agent = Agent(
    model=LiteLlm(model='anthropic/claude-3-7-sonnet'),
    name='claude_agent',
    instruction='您是一位樂於助人的助理。'
)
```

### 支援的供應商 (Supported Providers)

#### OpenAI

```python
from google.adk.models.lite_llm import LiteLlm
import os

# 設定 API 金鑰
os.environ['OPENAI_API_KEY'] = 'sk-...'

# 使用 GPT-4o
model = LiteLlm(model='openai/gpt-4o')

# 使用 GPT-4o-mini (更快、更便宜)
model = LiteLlm(model='openai/gpt-4o-mini')

# 使用 GPT-3.5-turbo
model = LiteLlm(model='openai/gpt-3.5-turbo')
```

**使用時機**:

- 需要 GPT-4 以與現有系統相容
- OpenAI 特定功能，如 DALL-E 整合
- 成本比較 (GPT-4o-mini 可能比 Gemini Pro 便宜)

#### Anthropic Claude

```python
import os

# 設定 API 金鑰
os.environ['ANTHROPIC_API_KEY'] = 'sk-ant-...'

# 使用 Claude 3.7 Sonnet
model = LiteLlm(model='anthropic/claude-3-7-sonnet')

# 使用 Claude 3 Opus (最高品質)
model = LiteLlm(model='anthropic/claude-3-opus')

# 使用 Claude 3 Haiku (最快、最便宜)
model = LiteLlm(model='anthropic/claude-3-haiku')
```

**使用時機**:

- 需要 Claude 特定能力 (長篇寫作、程式碼分析)
- Anthropic 的憲法 AI 方法
- 特定任務的成本比較

#### Ollama (本地模型)

```python
import os

# 設定 Ollama 基礎 URL
os.environ['OLLAMA_API_BASE'] = 'http://localhost:11434'

# ⚠️ 關鍵：使用 'ollama_chat' 前綴，而非 'ollama'
model = LiteLlm(model='ollama_chat/llama3.3')

# 其他熱門模型
model = LiteLlm(model='ollama_chat/mistral-small3.1')
model = LiteLlm(model='ollama_chat/codellama')
model = LiteLlm(model='ollama_chat/phi4')
```

**常見陷阱**:

```python
# ❌ 錯誤 - 會出現神秘錯誤
model = LiteLlm(model='ollama/llama3.3')

# ✅ 正確 - 必須使用 'ollama_chat'
model = LiteLlm(model='ollama_chat/llama3.3')
```

**使用時機**:

- 隱私要求 (資料保留在本地)
- 合規性法規 (無資料傳送至雲端)
- 節省成本 (無 API 費用)
- 離線/氣隙環境

**範例**: `contributing/samples/hello_world_ollama/agent.py`

#### Azure OpenAI

```python
import os

# 設定 Azure 憑證
os.environ['AZURE_API_KEY'] = 'your-azure-key'
os.environ['AZURE_API_BASE'] = 'https://your-resource.openai.azure.com/'
os.environ['AZURE_API_VERSION'] = '2024-02-01'

# 使用 Azure 託管的 GPT-4
model = LiteLlm(model='azure/gpt-4')

# 使用 Azure 託管的 GPT-35-turbo
model = LiteLlm(model='azure/gpt-35-turbo')
```

**使用時機**:

- 企業 Azure 合約
- Azure 合規性要求
- 與 Azure 服務整合

#### 透過 Vertex AI 使用 Claude (Claude via Vertex AI)

```python
# 透過 Google Cloud 使用 Anthropic Claude
model = LiteLlm(model='vertex_ai/claude-3-7-sonnet')
```

**使用時機**:

- 現有的 Google Cloud 設定
- 需要 Claude 但偏好 Google 計費
- 結合 Gemini + Claude 的工作流程

### 完整範例：多供應商 Agent 系統 (Complete Example: Multi-Provider Agent System)

```python
"""
範例：比較來自多個 LLM 供應商的回應。
來源：contributing/samples/hello_world_litellm/agent.py
"""
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents import Agent
import asyncio

async def compare_providers():
    """比較相同查詢在多個供應商上的結果。"""

    query = "用兩句話解釋量子計算。"

    # 使用不同供應商建立 agent
    gemini_agent = Agent(
        model='gemini-2.5-flash',  # 原生 Gemini (建議)
        name='gemini_agent'
    )

    openai_agent = Agent(
        model=LiteLlm(model='openai/gpt-4o'),
        name='openai_agent'
    )

    claude_agent = Agent(
        model=LiteLlm(model='anthropic/claude-3-7-sonnet'),
        name='claude_agent'
    )

    ollama_agent = Agent(
        model=LiteLlm(model='ollama_chat/llama3.3'),
        name='ollama_agent'
    )

    # 平行查詢所有供應商
    responses = await asyncio.gather(
        gemini_agent.run_async(query),
        openai_agent.run_async(query),
        claude_agent.run_async(query),
        ollama_agent.run_async(query),
        return_exceptions=True
    )

    # 比較結果
    for agent_name, response in zip(
        ['Gemini', 'OpenAI', 'Claude', 'Ollama'],
        responses
    ):
        if isinstance(response, Exception):
            print(f"{agent_name}: 錯誤 - {response}")
        else:
            print(f"\n{agent_name}:")
            print(response.output_text)
            print(f"時間: {response.usage.time_ms}ms")
            print(f"Tokens: {response.usage.total_tokens}")

# 執行比較
asyncio.run(compare_providers())
```

### ⚠️ 重要警告 (Important Warnings)

#### 不要：透過 LiteLLM 使用 Gemini (DON'T: Use Gemini via LiteLLM)

```python
# ❌ 錯誤 - 不要透過 LiteLLM 使用 Gemini
agent = Agent(
    model=LiteLlm(model='gemini/gemini-2.5-flash'),
    name='bad_agent'
)

# ✅ 正確 - 使用原生 Gemini 類別
agent = Agent(
    model='gemini-2.5-flash',  # 直接使用字串
    name='good_agent'
)
```

**原因**: 原生 Gemini 整合速度更快、更可靠，並支援 ADK 特定功能 (思考設定、程式碼執行、函式呼叫最佳化)。

#### 不要：忘記 `ollama_chat` 前綴 (DON'T: Forget `ollama_chat` Prefix)

```python
# ❌ 錯誤 - 會失敗
model = LiteLlm(model='ollama/llama3.3')

# ✅ 正確
model = LiteLlm(model='ollama_chat/llama3.3')
```

#### 務必：設定環境變數 (DO: Set Environment Variables)

```python
# ✅ 良好 - 在建立 agent 前設定憑證
import os

os.environ['OPENAI_API_KEY'] = 'sk-...'
os.environ['ANTHROPIC_API_KEY'] = 'sk-ant-...'
os.environ['OLLAMA_API_BASE'] = 'http://localhost:11434'

# 現在建立 agents
agent = Agent(model=LiteLlm(model='openai/gpt-4o'))
```

### 安裝 (Installation)

LiteLLM 支援內建於 ADK：

```bash
# LiteLLM 包含在 ADK 安裝中
pip install google-adk

# 對於 Ollama，需另外安裝
# 前往 https://ollama.com 下載
ollama pull llama3.3
ollama pull mistral-small3.1
```

### 何時使用各種方法 (When to Use Each Approach)

**使用原生 Gemini** (model='gemini-2.5-flash'):

- ✅ 新 Agent 的預設選擇
- ✅ 最佳效能與功能
- ✅ 最低延遲
- ✅ ADK 最佳化 (思考、程式碼執行、函式呼叫)
- ✅ 最佳性價比

**使用 LiteLLM** (model=LiteLlm(...)):

- ✅ 需要特定供應商 (GPT-4、Claude 等)
- ✅ 本地模型以保護隱私 (Ollama)
- ✅ 跨供應商的成本比較
- ✅ 現有合約 (Azure, Anthropic)
- ✅ 多供應商備援策略

---

## 6. 最佳實踐 (Best Practices)

### ✅ 務必：永遠明確指定模型 (建議：gemini-2.5-flash) (DO: Always Specify Model Explicitly (Recommended: gemini-2.5-flash))

```python
# ✅ 良好 - 永遠明確指定模型以求清晰
agent = Agent(
    model='gemini-2.5-flash',  # 建議：最佳性價比
    name='my_agent'
)

# ❌ 不佳 - 依賴預設值 (空字串，從父層繼承)
agent = Agent(name='my_agent')  # 模型預設為 ''，從父層繼承

# ✅ 良好 - 明確且有目的地選擇模型
# 根據您的需求進行測試和最佳化：
# - 使用 2.5-flash 於通用目的 (建議)
# - 如果是超簡單任務，降級至 2.5-flash-lite
# - 如果需要複雜推理，升級至 2.5-pro
```

### ✅ 務必：在生產前進行基準測試 (DO: Benchmark Before Production)

```python
# ✅ 良好 - 在部署前測試模型
models = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-flash-8b']

for model in models:
    agent = Agent(model=model, name='test')
    # 執行代表性查詢
    # 測量延遲、品質、成本
    # 選擇最適合的
```

### ✅ 務必：考慮功能需求 (DO: Consider Feature Requirements)

```python
# ✅ 良好 - 檢查功能相容性
if need_code_execution:
    model = 'gemini-2.0-flash'  # 支援程式碼執行
elif need_thinking:
    model = 'gemini-2.0-flash-thinking'  # 擴展推理
else:
    model = 'gemini-1.5-flash'  # 快速且經濟
```

### ❌ 不要：對簡單任務使用 Pro 模型 (DON'T: Use Pro for Simple Tasks)

```python
# ❌ 不佳 - 為簡單查詢支付過高費用
agent = Agent(
    model='gemini-1.5-pro',  # 昂貴
    instruction="回答是或否的問題"  # 簡單任務
)

# ✅ 良好 - 將複雜度與模型匹配
agent = Agent(
    model='gemini-1.5-flash-8b',  # 經濟
    instruction="回答是或否的問題"
)
```

---

## 摘要 (Summary)

您已掌握模型選擇與最佳化：

**重點摘要**:

- ⭐ **`gemini-2.5-flash` 為建議選項** - 最佳性價比，首款具備思考能力的 Flash 模型
- ✅ **永遠明確指定模型** - 預設為空字串 (從父層繼承)
- ✅ `gemini-2.5-pro` 用於程式碼、數學、STEM 的複雜推理
- ✅ `gemini-2.5-flash-lite` 用於超快、成本效益高的高吞吐量
- ✅ `gemini-2.0-flash` 和 `gemini-1.5-*` 模型仍然可用 (舊版)
- ✅ 需要時可透過 **LiteLLM 支援** OpenAI、Claude、Ollama、Azure
- ✅ 建議使用原生 Gemini 而非透過 LiteLLM 的 Gemini
- ✅ 在生產部署前對模型進行基準測試
- ✅ 考慮成本、效能、功能與供應商需求的權衡

**生產檢查清單**:

- [ ] 根據需求選擇模型 (建議：gemini-2.5-flash)
- [ ] 在 Agent 建構函式中明確指定模型 (不要依賴預設值)
- [ ] 已在代表性查詢上完成基準測試
- [ ] 已驗證功能相容性 (2.5 Flash 具備思考能力！)
- [ ] 已計算成本預測
- [ ] 已定義效能服務等級協定 (SLA)
- [ ] 已選擇供應商 (Gemini vs LiteLLM 供應商)
- [ ] 已設定備援模型
- [ ] 已部署模型監控
- [ ] 已規劃遷移策略 (1.5/2.0 → 2.5)

**您學到了**:

1. **`gemini-2.5-flash` 為建議選項** - 新專案的最佳效能與價值
2. **永遠明確指定模型** - 預設為空字串 (從父層繼承)
3. **完整的模型陣容** - 從 2.5-flash-lite (最快) 到 2.5-pro (最聰明)
4. **LiteLLM 整合** - 當需要供應商彈性時使用 OpenAI、Claude、Ollama
5. **原生 vs LiteLLM** - 永遠偏好原生 Gemini 以獲得最佳效能
6. **選擇框架** - 使用 MODELS 字典和 `recommend_model()` 進行系統性選擇

**資源**:

- [Gemini 2.5 文件](https://ai.google.dev/gemini-api/docs/models) - Google AI 官方文件
- [Vertex AI Gemini 2.5 Flash](https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-flash) - 雲端文件
- [Gemini 2.5 技術報告](https://storage.googleapis.com/deepmind-media/gemini/gemini_v2_5_report.pdf) - 研究論文
- [LiteLLM 文件](https://docs.litellm.ai/) - 多供應商整合
- [定價計算機](https://cloud.google.com/products/calculator) - 成本估算

---

## 程式碼實現 (Code Implementation)
- tutorial22：[程式碼連結](../../../python/agents/tutorial22/)

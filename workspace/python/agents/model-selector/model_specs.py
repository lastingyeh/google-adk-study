#!/usr/bin/env python3
"""
獨立腳本，用於顯示 Gemini 模型規格。
這樣可以避免匯入完整的 ADK 代理程式，因為載入時間過長。
"""

def get_model_specs():
    """取得可用 Gemini 模型的詳細資訊。"""
    return {
        'gemini-2.5-flash': {
            'context_window': '1M tokens (1百萬個權杖)',
            'features': ['多模態 (Multimodal)', '快速', '高效'],
            'best_for': '通用目的，建議用於大多數使用情境',
            'pricing': '低',
            'speed': '快'
        },
        'gemini-2.5-flash-lite': {
            'context_window': '1M tokens (1百萬個權杖)',
            'features': ['超快', '簡單任務', '高流量'],
            'best_for': '高流量的簡單任務、內容審核',
            'pricing': '非常低',
            'speed': '超快'
        },
        'gemini-2.5-pro': {
            'context_window': '2M tokens (2百萬個權杖)',
            'features': ['進階推理', '複雜問題', '高品質'],
            'best_for': '複雜推理、STEM、關鍵業務運營',
            'pricing': '高',
            'speed': '中等'
        },
        'gemini-2.0-flash': {
            'context_window': '1M tokens (1百萬個權杖)',
            'features': ['多模態 (Multimodal)', '平衡', '舊版支援'],
            'best_for': '具有舊版相容性的通用目的',
            'pricing': '低',
            'speed': '快'
        },
        'gemini-2.0-flash-live': {
            'context_window': '1M tokens (1百萬個權杖)',
            'features': ['即時', '雙向串流 (Bidirectional streaming)', '語音'],
            'best_for': '即時語音應用和串流',
            'pricing': '中等',
            'speed': '即時'
        }
    }

if __name__ == '__main__':
    # 當此腳本被直接執行時，會印出 Gemini 模型家族的總覽
    print("📚 Gemini 模型家族總覽:")
    print("")
    # 呼叫函式以取得模型規格
    specs = get_model_specs()
    # 遍歷每個模型及其詳細資訊並印出
    for model, details in specs.items():
        print(f"🔹 {model}:")
        print(f"   📊 Context (上下文): {details.get('context_window', 'N/A')}")
        print(f"   ⚡ Speed (速度): {details.get('speed', 'N/A')}")
        print(f"   🎯 Quality (品質): {details.get('pricing', 'N/A')}")  # 使用定價作為品質指標
        print(f"   💰 Cost (成本): {details.get('pricing', 'N/A')}")
        print("")

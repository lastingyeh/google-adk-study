#!/usr/bin/env python3
"""
使用 RUBRIC_BASED_TOOL_USE_QUALITY_V1 進行工具使用品質的真實評估。

此腳本針對自定義評量表執行代理工具使用情況的實際評估。
它展示了如何：
1. 建立包含預期工具順序的測試案例
2. 使用基於評量表的工具使用品質指標配置評估
3. 執行評估並解讀結果
4. 處理良好與不良的工具排序模式

用法：
    python evaluate_tool_use.py

需求：
    - 設定 GOOGLE_API_KEY 環境變數
    - google-genai >= 1.16.0
    - 在 evalset.json 中定義的測試案例
"""

import asyncio
import json
import os
from pathlib import Path

from google.adk.evaluation.agent_evaluator import AgentEvaluator


async def create_evalset_file():
    """建立用於評估的 evalset.json 測試案例檔案。"""
    evalset_path = Path(__file__).parent / "tool_use_quality.evalset.json"
    config_path = Path(__file__).parent / "test_config.json"

    # 定義包含良好和不良工具使用順序的評估集
    evalset_data = {
        "eval_set_id": "tool_use_quality_evaluation",
        "name": "工具使用品質評估",
        "description": "評估代理工具的排序和品質",
        "eval_cases": [
            {
                "eval_id": "good_sequence_complete_pipeline",
                "conversation": [
                    {
                        "invocation_id": "inv-001",
                        "user_content": {
                            "parts": [
                                {
                                    "text": "分析銷售資料集並應用預測模型"
                                }
                            ],
                            "role": "user",
                        },
                        "final_response": {
                            "parts": [
                                {
                                    "text": "我已經分析了銷售資料集，提取了特徵，驗證了品質，並應用了預測模型。該模型在特徵上達到了 87% 的準確率。"
                                }
                            ],
                            "role": "model",
                        },
                        "intermediate_data": {
                            "tool_uses": [
                                {
                                    "id": "call-001",
                                    "name": "analyze_data",
                                    "args": {"dataset": "sales_dataset"},
                                },
                                {
                                    "id": "call-002",
                                    "name": "extract_features",
                                    "args": {"data": {"type": "analysis_result"}},
                                },
                                {
                                    "id": "call-003",
                                    "name": "validate_quality",
                                    "args": {"features": {"type": "features"}},
                                },
                                {
                                    "id": "call-004",
                                    "name": "apply_model",
                                    "args": {
                                        "features": {"type": "validated_features"},
                                        "model": "random_forest",
                                    },
                                },
                            ],
                            "intermediate_responses": [],
                        },
                    }
                ],
                "session_input": {
                    "app_name": "tool_use_evaluator",
                    "user_id": "test_user",
                    "state": {},
                },
            },
            {
                "eval_id": "bad_sequence_skipped_validation",
                "conversation": [
                    {
                        "invocation_id": "inv-002",
                        "user_content": {
                            "parts": [
                                {
                                    "text": "處理客戶資料集以進行建模"
                                }
                            ],
                            "role": "user",
                        },
                        "final_response": {
                            "parts": [
                                {
                                    "text": "我已經提取了特徵並應用了模型。"
                                }
                            ],
                            "role": "model",
                        },
                        "intermediate_data": {
                            "tool_uses": [
                                {
                                    "id": "call-101",
                                    "name": "extract_features",
                                    "args": {"data": {"type": "raw_data"}},
                                },
                                {
                                    "id": "call-102",
                                    "name": "apply_model",
                                    "args": {
                                        "features": {"type": "features"},
                                        "model": "linear_regression",
                                    },
                                },
                            ],
                            "intermediate_responses": [],
                        },
                    }
                ],
                "session_input": {
                    "app_name": "tool_use_evaluator",
                    "user_id": "test_user",
                    "state": {},
                },
            },
            {
                "eval_id": "good_sequence_proper_analysis",
                "conversation": [
                    {
                        "invocation_id": "inv-003",
                        "user_content": {
                            "parts": [
                                {
                                    "text": "分析並準備機器學習用的資料集"
                                }
                            ],
                            "role": "user",
                        },
                        "final_response": {
                            "parts": [
                                {
                                    "text": "資料集已分析並準備好，具備已驗證的特徵，可隨時進行建模。"
                                }
                            ],
                            "role": "model",
                        },
                        "intermediate_data": {
                            "tool_uses": [
                                {
                                    "id": "call-201",
                                    "name": "analyze_data",
                                    "args": {"dataset": "customer_data"},
                                },
                                {
                                    "id": "call-202",
                                    "name": "extract_features",
                                    "args": {"data": {"type": "analysis"}},
                                },
                                {
                                    "id": "call-203",
                                    "name": "validate_quality",
                                    "args": {"features": {"type": "extracted_features"}},
                                },
                            ],
                            "intermediate_responses": [],
                        },
                    }
                ],
                "session_input": {
                    "app_name": "tool_use_evaluator",
                    "user_id": "test_user",
                    "state": {},
                },
            },
        ],
    }

    # 定義具有基於評量表的工具使用品質指標的評估配置
    eval_config = {
        "criteria": {
            "rubric_based_tool_use_quality_v1": {
                "threshold": 0.7,
                "judge_model_options": {
                    "judge_model": "gemini-2.5-flash",
                    "num_samples": 3,
                },
                "rubrics": [
                    {
                        "rubric_id": "proper_tool_order",
                        "rubric_content": {
                            "text_property": "代理在 extract_features 之前呼叫 analyze_data。這遵守了工具依賴關係。"
                        },
                    },
                    {
                        "rubric_id": "complete_pipeline",
                        "rubric_content": {
                            "text_property": "對於完整的分析，代理應該呼叫：analyze → extract → validate → apply (全部 4 個步驟)"
                        },
                    },
                    {
                        "rubric_id": "validation_before_model",
                        "rubric_content": {
                            "text_property": "代理在應用模型之前驗證特徵品質"
                        },
                    },
                    {
                        "rubric_id": "no_tool_failures",
                        "rubric_content": {
                            "text_property": "所有工具呼叫皆成功且具有適當的參數 (無錯誤或缺少參數)"
                        },
                    },
                ],
            }
        }
    }

    # 將 evalset 寫入檔案
    with open(evalset_path, "w") as f:
        json.dump(evalset_data, f, indent=2, ensure_ascii=False)

    # 將 config 寫入檔案
    with open(config_path, "w") as f:
        json.dump(eval_config, f, indent=2, ensure_ascii=False)

    return evalset_path


async def run_evaluation(evalset_path: Path):
    """使用 RUBRIC_BASED_TOOL_USE_QUALITY_V1 指標執行評估。

    Args:
        evalset_path: evalset.json 檔案的路徑
    """
    print("\n" + "=" * 80)
    print("真實評估: 基於評量表的工具使用品質 V1 (RUBRIC BASED TOOL USE QUALITY V1)")
    print("=" * 80 + "\n")

    # 評量表已在 test_config.json 中定義
    rubrics = [
        ("proper_tool_order", "代理在 extract_features 之前呼叫 analyze_data"),
        ("complete_pipeline", "對於完整分析：analyze → extract → validate → apply"),
        ("validation_before_model", "代理在建模前驗證特徵品質"),
        ("no_tool_failures", "所有工具呼叫皆成功且參數正確"),
    ]

    print("📋 評估配置")
    print("-" * 80)
    print("閾值: 0.7")
    print("評審模型: gemini-2.5-flash")
    print(f"評量表: {len(rubrics)}")

    for rubric_id, rubric_desc in rubrics:
        print(f"  • {rubric_id}: {rubric_desc[:55]}...")

    print("\n🔍 正在執行評估")
    print("-" * 80)

    try:
        # 執行評估
        results = await AgentEvaluator.evaluate(
            agent_module="tool_use_evaluator",
            eval_dataset_file_path_or_dir=str(evalset_path),
        )

        print("✅ 評估成功完成！")
        print("\n📊 評估結果")
        print("-" * 80)
        print(json.dumps(results, indent=2, default=str, ensure_ascii=False))

        # 解讀結果
        print("\n🧠 結果解讀")
        print("-" * 80)
        print(
            """
            評估分數說明：
            - 分數 1.0：完美的工具排序 (滿足所有評量表)
            - 分數 0.8-0.99：優秀，1-2 個小問題
            - 分數 0.7-0.79：良好，可接受但需要改進
            - 分數 0.6-0.69：可接受但有重大問題
            - 分數 <0.6：差，工具排序有根本性問題

            每個評量表評估的內容：
            1. proper_tool_order：是否遵守依賴關係？ (分析在提取之前)
            2. complete_pipeline：是否包含所有必要步驟？
            3. validation_before_model：是否在建模前驗證品質？
            4. no_tool_failures：是否所有工具呼叫都執行成功？
            """
        )

    except Exception as e:
        error_msg = str(e)
        if "Expected" in error_msg and "got" in error_msg:
            # 這是評分失敗，實際上意味著評估工作正常！
            print("⚠️  評估已執行但測試案例未達到評分閾值：")
            print(f"   {error_msg}\n")
            print("這意味著評估框架運作正常！")
            print("測試代理不符合預期的工具順序。")
            print("在真實場景中，您將會：\n")
            print("1. 檢視上述預期與實際工具呼叫")
            print("2. 調整代理指令以符合預期行為")
            print("3. 重新執行評估以查看分數是否提高")
        else:
            print(f"❌ 評估失敗: {e}")
            print("\n注意: 確保已設定 GOOGLE_API_KEY：")
            print("  export GOOGLE_API_KEY=your_key")


def show_test_case_details():
    """顯示有關測試案例的詳細資訊。"""
    print("\n📝 測試案例摘要")
    print("-" * 80)

    test_cases = [
        {
            "name": "good_sequence_complete_pipeline",
            "description": "完整的 4 步驟流程 (分析 → 提取 → 驗證 → 應用)",
            "expected_score": "0.95-1.0 (優秀)",
            "why": "包含正確順序的所有步驟，滿足所有評量表",
        },
        {
            "name": "bad_sequence_skipped_validation",
            "description": "缺少步驟 (提取 → 應用，無分析或驗證)",
            "expected_score": "0.25-0.4 (差)",
            "why": "跳過關鍵步驟，違反 proper_tool_order 和 validation_before_model 評量表",
        },
        {
            "name": "good_sequence_proper_analysis",
            "description": "良好的分析流程 (分析 → 提取 → 驗證)",
            "expected_score": "0.8-0.9 (好)",
            "why": "順序正確且包含重要步驟，但未應用模型 (對於僅分析任務可接受)",
        },
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n測試案例 {i}: {case['name']}")
        print(f"  描述: {case['description']}")
        print(f"  預期分數: {case['expected_score']}")
        print(f"  原因: {case['why']}")


async def main():
    """主評估工作流程。"""
    # 檢查 API 金鑰
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️  警告: 未設定 GOOGLE_API_KEY")
        print("    若要進行真實評估，請設定: export GOOGLE_API_KEY=your_key")
        print("    繼續執行展示模式...\n")

    # 顯示測試案例詳細資訊
    show_test_case_details()

    # 建立 evalset 檔案
    print("\n📁 正在建立測試 evalset 檔案...")
    evalset_path = await create_evalset_file()
    print(f"   ✓ 已建立: {evalset_path}")

    # 執行評估
    await run_evaluation(evalset_path)

    print("\n" + "=" * 80)
    print("評估完成")
    print("=" * 80 + "\n")
    print("💡 關鍵洞察：")
    print("""
        RUBRIC_BASED_TOOL_USE_QUALITY_V1 指標通過讓 LLM 評審
        根據您的自定義評量表評估工具呼叫，來評估代理的工具排序。

        主要優點：
        • 儘早發現工具依賴關係違規
        • 確保代理遵循規定的工作流程
        • 偵測遺漏或重新排序的步驟
        • 針對您的特定需求靈活定義評量表

        下一步：
        1. 為您的特定工作流程定義評量表
        2. 建立包含預期和實際工具順序的測試案例
        3. 在您的 CI/CD 管道中執行評估
        4. 使用結果識別代理行為問題
        5. 迭代代理指令以提高分數
    """
    )


if __name__ == "__main__":
    asyncio.run(main())

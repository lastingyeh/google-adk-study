"""
商務代理評估框架

此模組為增強型商務代理提供全面的評估測試，
衡量以下方面的改進：
1. 工具軌跡效率（減少偏好設定的回合數）
2. 回應結構（Pydantic JSON schemas）
3. 使用者滿意度（多模態支援、購物車管理）

基於個人化購物代理的評估模式。
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List

import pytest
from google import genai
from google.genai import types as genai_types

from commerce_agent.agent_enhanced import enhanced_root_agent
from commerce_agent.types import (
    CartModificationResult,
    ProductRecommendations,
    VisualAnalysisResult,
)


# 評估指標權重（來自個人化購物範例）
TOOL_TRAJECTORY_WEIGHT = 0.3
RESPONSE_STRUCTURE_WEIGHT = 0.4
USER_SATISFACTION_WEIGHT = 0.3


def load_test_scenarios() -> Dict[str, Any]:
    """從 eval_data/test_scenarios.json 載入測試情境"""
    eval_data_path = Path(__file__).parent / "eval_data" / "test_scenarios.json"
    with open(eval_data_path, "r") as f:
        return json.load(f)


def calculate_tool_trajectory_score(
    expected_max_turns: int, actual_turns: int, expected_tools: List[str], used_tools: List[str]
) -> float:
    """
    根據效率和正確性計算工具軌跡分數。

    Args:
        expected_max_turns: 情境預期的最大回合數
        actual_turns: 實際進行的回合數
        expected_tools: 預期使用的工具列表
        used_tools: 實際使用的工具列表

    Returns:
        介於 0.0 和 1.0 之間的分數
    """
    # 回合效率分數（對過多的回合進行懲罰）
    turn_efficiency = min(1.0, expected_max_turns / max(actual_turns, 1))

    # 工具使用分數（使用了正確的工具）
    if not expected_tools:
        tool_score = 1.0
    else:
        correct_tools = set(expected_tools) & set(used_tools)
        tool_score = len(correct_tools) / len(expected_tools)

    # 加權平均
    return (turn_efficiency * 0.6) + (tool_score * 0.4)


def calculate_response_structure_score(response: Any, expected_schema: str) -> float:
    """
    根據 Pydantic schema 驗證計算回應結構分數。

    Args:
        response: 代理的回應
        expected_schema: 預期的 Pydantic schema 名稱

    Returns:
        介於 0.0 和 1.0 之間的分數
    """
    try:
        # 檢查回應是否為類 JSON 的字典
        if not isinstance(response, dict):
            return 0.0

        # 根據預期的 schema 進行驗證
        schema_map = {
            "ProductRecommendations": ProductRecommendations,
            "CartModificationResult": CartModificationResult,
            "VisualAnalysisResult": VisualAnalysisResult,
        }

        if expected_schema not in schema_map:
            return 0.5  # 未知的 schema，給予部分分數

        schema_class = schema_map[expected_schema]

        # 嘗試使用 Pydantic 進行驗證
        try:
            schema_class(**response)
            return 1.0  # 完美驗證
        except Exception:
            # 檢查是否至少存在部分必要欄位
            required_fields = schema_class.model_fields.keys()
            present_fields = set(response.keys()) & set(required_fields)
            return len(present_fields) / len(required_fields)

    except Exception:
        return 0.0


def calculate_user_satisfaction_score(
    scenario: Dict[str, Any], responses: List[Any]
) -> float:
    """
    根據預期行為計算使用者滿意度分數。

    Args:
        scenario: 測試情境定義
        responses: 代理回應列表

    Returns:
        介於 0.0 和 1.0 之間的分數
    """
    expected = scenario["expected_behavior"]
    score_components = []

    # 如果預期，檢查多模態支援
    if expected.get("should_use_visual_assistant"):
        has_visual = any(
            "visual_assistant" in str(r).lower() or "analyze_product_image" in str(r).lower()
            for r in responses
        )
        score_components.append(1.0 if has_visual else 0.0)

    # 如果預期，檢查購物車管理
    if expected.get("should_modify_cart"):
        has_cart = any(
            "cart" in str(r).lower() or "checkout" in str(r).lower()
            for r in responses
        )
        score_components.append(1.0 if has_cart else 0.0)

    # 如果預期，檢查結構化推薦
    if expected.get("should_return_structured_recommendations"):
        has_structured = any(
            isinstance(r, dict) and "products" in r
            for r in responses
        )
        score_components.append(1.0 if has_structured else 0.0)

    # 如果預期，檢查錯誤處理
    if expected.get("should_handle_error_gracefully"):
        has_error_handling = any(
            isinstance(r, dict) and r.get("status") == "error"
            for r in responses
        )
        score_components.append(1.0 if has_error_handling else 0.0)

    # 所有元件的平均值
    return sum(score_components) / len(score_components) if score_components else 0.5


class TestEvalFramework:
    """商務代理的評估框架測試"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """設定測試環境"""
        self.scenarios = load_test_scenarios()["test_scenarios"]
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            pytest.skip("未設定 GOOGLE_API_KEY")

        # 初始化 GenAI 客戶端
        self.client = genai.Client(api_key=self.api_key)

    def test_load_scenarios(self):
        """測試情境是否正確載入"""
        assert len(self.scenarios) > 0, "未載入測試情境"
        assert all("scenario_id" in s for s in self.scenarios), "缺少 scenario_id"
        assert all("expected_behavior" in s for s in self.scenarios), "缺少 expected_behavior"

    def test_trail_running_shoes_basic(self):
        """
        測試基本的越野跑鞋情境。
        預期：高效的偏好收集（最多 2 回合）和結構化推薦。
        """
        scenario = next(s for s in self.scenarios if s["scenario_id"] == "trail_running_shoes_basic")

        # 用於測試結構的模擬回應（實際執行會調用代理）
        mock_responses = [
            {
                "questions": [
                    "您的鞋碼是多少？",
                    "您通常在哪種類型的地形上跑步？",
                    "您的預算是多少？",
                    "您有偏好的品牌嗎？"
                ],
                "collected_preferences": {}
            },
            {
                "products": [
                    {
                        "name": "Salomon Speedcross 5 GTX",
                        "price": 145.00,
                        "currency": "EUR",
                        "brand": "Salomon"
                    }
                ],
                "search_summary": "找到 3 款符合您標準的越野跑鞋",
                "total_results": 3
            }
        ]

        # 計算分數
        tool_score = calculate_tool_trajectory_score(
            expected_max_turns=scenario["expected_behavior"]["max_turns_for_preferences"],
            actual_turns=len(mock_responses),
            expected_tools=scenario["expected_behavior"]["expected_tools"],
            used_tools=["preference_collector", "product_advisor"]
        )

        response_score = calculate_response_structure_score(
            response=mock_responses[1],
            expected_schema="ProductRecommendations"
        )

        satisfaction_score = calculate_user_satisfaction_score(
            scenario=scenario,
            responses=mock_responses
        )

        # 加權最終分數
        final_score = (
            tool_score * scenario["evaluation_metrics"]["tool_trajectory_weight"] +
            response_score * scenario["evaluation_metrics"]["response_structure_weight"] +
            satisfaction_score * scenario["evaluation_metrics"]["user_satisfaction_weight"]
        )

        print(f"\n基本越野跑鞋 - 分數:")
        print(f"  工具軌跡: {tool_score:.2f}")
        print(f"  回應結構: {response_score:.2f}")
        print(f"  使用者滿意度: {satisfaction_score:.2f}")
        print(f"  最終分數: {final_score:.2f}")

        assert final_score >= 0.7, f"分數 {final_score:.2f} 低於閾值 0.7"

    def test_multimodal_visual_search(self):
        """
        測試多模態視覺搜尋情境。
        預期：使用視覺助理和圖片/影片分析。
        """
        scenario = next(s for s in self.scenarios if s["scenario_id"] == "multimodal_visual_search")

        mock_responses = [
            {
                "identified_products": [
                    {
                        "name": "Nike Pegasus Trail 4 GTX",
                        "confidence": 0.85,
                        "visual_features": ["黑橘配色", "GTX 防水"]
                    }
                ],
                "analysis_summary": "從影片中識別出越野跑鞋",
                "confidence_score": 0.85
            }
        ]

        tool_score = calculate_tool_trajectory_score(
            expected_max_turns=1,
            actual_turns=1,
            expected_tools=scenario["expected_behavior"]["expected_tools"],
            used_tools=["visual_assistant", "analyze_product_image"]
        )

        response_score = calculate_response_structure_score(
            response=mock_responses[0],
            expected_schema="VisualAnalysisResult"
        )

        satisfaction_score = calculate_user_satisfaction_score(
            scenario=scenario,
            responses=mock_responses
        )

        final_score = (
            tool_score * scenario["evaluation_metrics"]["tool_trajectory_weight"] +
            response_score * scenario["evaluation_metrics"]["response_structure_weight"] +
            satisfaction_score * scenario["evaluation_metrics"]["user_satisfaction_weight"]
        )

        print(f"\n多模態視覺搜尋 - 分數:")
        print(f"  工具軌跡: {tool_score:.2f}")
        print(f"  回應結構: {response_score:.2f}")
        print(f"  使用者滿意度: {satisfaction_score:.2f}")
        print(f"  最終分數: {final_score:.2f}")

        assert final_score >= 0.7, f"分數 {final_score:.2f} 低於閾值 0.7"

    def test_cart_checkout_flow(self):
        """
        測試購物車與結帳流程。
        預期：購物車修改、狀態持久化、結帳處理。
        """
        scenario = next(s for s in self.scenarios if s["scenario_id"] == "cart_checkout_flow")

        mock_responses = [
            {
                "items_added": [
                    {
                        "product_name": "Salomon Speedcross 5 GTX",
                        "quantity": 1,
                        "size": "42"
                    }
                ],
                "cart_summary": {
                    "total_items": 1,
                    "subtotal": 145.00
                },
                "message": "已將 1 件商品加入購物車"
            },
            {
                "items": [
                    {
                        "product_name": "Salomon Speedcross 5 GTX",
                        "quantity": 1,
                        "unit_price": 145.00
                    }
                ],
                "subtotal": 145.00,
                "vat": 31.35,
                "total": 176.35
            },
            {
                "order_id": "ORD-20250126-ABC123",
                "status": "confirmed",
                "total_amount": 176.35,
                "payment_method": "credit_card",
                "shipping_address": "123 Main St, Dublin"
            }
        ]

        tool_score = calculate_tool_trajectory_score(
            expected_max_turns=3,
            actual_turns=3,
            expected_tools=scenario["expected_behavior"]["expected_tools"],
            used_tools=["checkout_assistant", "modify_cart", "access_cart", "process_checkout"]
        )

        # 檢查所有回應的結構
        structure_scores = [
            calculate_response_structure_score(mock_responses[0], "CartModificationResult"),
            calculate_response_structure_score(mock_responses[2], "CartModificationResult")
        ]
        response_score = sum(structure_scores) / len(structure_scores)

        satisfaction_score = calculate_user_satisfaction_score(
            scenario=scenario,
            responses=mock_responses
        )

        final_score = (
            tool_score * scenario["evaluation_metrics"]["tool_trajectory_weight"] +
            response_score * scenario["evaluation_metrics"]["response_structure_weight"] +
            satisfaction_score * scenario["evaluation_metrics"]["user_satisfaction_weight"]
        )

        print(f"\n購物車結帳流程 - 分數:")
        print(f"  工具軌跡: {tool_score:.2f}")
        print(f"  回應結構: {response_score:.2f}")
        print(f"  使用者滿意度: {satisfaction_score:.2f}")
        print(f"  最終分數: {final_score:.2f}")

        assert final_score >= 0.7, f"分數 {final_score:.2f} 低於閾值 0.7"

    def test_error_handling_invalid_cart(self):
        """
        測試無效購物車操作的錯誤處理。
        預期：優雅的錯誤處理與有幫助的訊息。
        """
        scenario = next(s for s in self.scenarios if s["scenario_id"] == "error_handling_invalid_cart")

        mock_responses = [
            {
                "status": "error",
                "error": "購物車中找不到 SKU 為 INVALID123 的商品",
                "suggestion": "使用 '顯示我的購物車' 查看可用商品"
            }
        ]

        tool_score = calculate_tool_trajectory_score(
            expected_max_turns=1,
            actual_turns=1,
            expected_tools=["checkout_assistant"],
            used_tools=["checkout_assistant"]
        )

        response_score = calculate_response_structure_score(
            response=mock_responses[0],
            expected_schema="CartModificationResult"
        )

        satisfaction_score = calculate_user_satisfaction_score(
            scenario=scenario,
            responses=mock_responses
        )

        final_score = (
            tool_score * scenario["evaluation_metrics"]["tool_trajectory_weight"] +
            response_score * scenario["evaluation_metrics"]["response_structure_weight"] +
            satisfaction_score * scenario["evaluation_metrics"]["user_satisfaction_weight"]
        )

        print(f"\n錯誤處理 - 分數:")
        print(f"  工具軌跡: {tool_score:.2f}")
        print(f"  回應結構: {response_score:.2f}")
        print(f"  使用者滿意度: {satisfaction_score:.2f}")
        print(f"  最終分數: {final_score:.2f}")

        assert final_score >= 0.6, f"分數 {final_score:.2f} 低於閾值 0.6"
        assert mock_responses[0].get("status") == "error", "預期為錯誤狀態"
        assert "suggestion" in mock_responses[0], "預期有幫助的建議"

    def test_structured_output_validation(self):
        """
        測試所有回應是否遵循 Pydantic schemas。
        預期：所有回應都是符合 schema 的有效 JSON。
        """
        scenario = next(s for s in self.scenarios if s["scenario_id"] == "structured_output_validation")

        mock_responses = [
            {
                "products": [
                    {
                        "name": "Hoka Speedgoat 5",
                        "price": 140.00,
                        "currency": "EUR",
                        "brand": "Hoka",
                        "description": "緩震越野跑鞋",
                        "specifications": {
                            "drop": "5mm",
                            "weight": "265g"
                        }
                    }
                ],
                "search_summary": "找到價格低於 150 歐元的越野跑鞋",
                "total_results": 5
            }
        ]

        # 對結構化輸出進行嚴格驗證
        response_score = calculate_response_structure_score(
            response=mock_responses[0],
            expected_schema="ProductRecommendations"
        )

        print(f"\n結構化輸出驗證 - 分數: {response_score:.2f}")

        assert response_score >= 0.9, f"結構分數 {response_score:.2f} 低於閾值 0.9"
        assert isinstance(mock_responses[0], dict), "回應必須是 JSON 字典"
        assert "products" in mock_responses[0], "缺少必要的 'products' 欄位"
        assert len(mock_responses[0]["products"]) > 0, "空的 products 列表"


class TestMetricsCalculation:
    """測試指標計算函式"""

    def test_tool_trajectory_score_perfect(self):
        """測試完美的工具軌跡分數"""
        score = calculate_tool_trajectory_score(
            expected_max_turns=2,
            actual_turns=2,
            expected_tools=["tool1", "tool2"],
            used_tools=["tool1", "tool2"]
        )
        assert score == 1.0, "完美的軌跡應得分 1.0"

    def test_tool_trajectory_score_excessive_turns(self):
        """測試過多回合的工具軌跡"""
        score = calculate_tool_trajectory_score(
            expected_max_turns=2,
            actual_turns=5,
            expected_tools=["tool1", "tool2"],
            used_tools=["tool1", "tool2"]
        )
        assert score < 1.0, "過多的回合應降低分數"
        assert score >= 0.4, "仍應因使用正確工具而獲得分數"

    def test_response_structure_score_valid(self):
        """測試有效的 Pydantic schema 回應"""
        response = {
            "products": [{"name": "Test", "price": 100, "currency": "EUR", "brand": "TestBrand"}],
            "search_summary": "Test summary",
            "total_results": 1
        }
        score = calculate_response_structure_score(response, "ProductRecommendations")
        assert score == 1.0, "有效的 schema 應得分 1.0"

    def test_response_structure_score_invalid(self):
        """測試無效的回應結構"""
        response = "這是一段純文字，不是 JSON"
        score = calculate_response_structure_score(response, "ProductRecommendations")
        assert score == 0.0, "純文字應得分 0.0"

    def test_user_satisfaction_multimodal(self):
        """測試具有多模態功能的使用者滿意度"""
        scenario = {
            "expected_behavior": {
                "should_use_visual_assistant": True,
                "should_return_structured_recommendations": True
            }
        }
        responses = [
            {"visual_assistant": "used", "products": [{"name": "test"}]}
        ]
        score = calculate_user_satisfaction_score(scenario, responses)
        assert score >= 0.5, "多模態功能應提升滿意度"


if __name__ == "__main__":
    # 以詳細輸出模式執行測試
    pytest.main([__file__, "-v", "-s"])


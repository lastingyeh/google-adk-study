#!/usr/bin/env python3
"""
基於 Arize 的 RAG 代理評估套件。
此實現遵循 Arize 文檔模式進行實驗,同時使用 Google Vertex AI 進行評估。
"""

import json
import os
import time
import uuid
from typing import Any

import pandas as pd

# Google Cloud 導入 - Vertex AI 評估
import vertexai

# Arize 導入 - 數據和實驗管理
from arize.experimental.datasets import ArizeDatasetsClient
from arize.experimental.datasets.experiments.types import EvaluationResult
from arize.experimental.datasets.utils.constants import GENERATIVE
from dotenv import load_dotenv

# ADK 導入 - 用於運行代理
from google.adk.runners import InMemoryRunner
from google.genai.types import Part, UserContent
from vertexai.preview.evaluation import EvalTask

# 導入 RAG 代理
from rag.agent import root_agent

# 加載環境變數
load_dotenv()

# 環境變數配置
ARIZE_API_KEY = os.getenv("ARIZE_API_KEY")
ARIZE_SPACE_ID = os.getenv("ARIZE_SPACE_ID")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")

# 驗證必需的環境變數
if not all([ARIZE_API_KEY, ARIZE_SPACE_ID, GOOGLE_CLOUD_PROJECT]):
    raise ValueError(
        "缺少必需的環境變數: ARIZE_API_KEY, ARIZE_SPACE_ID, GOOGLE_CLOUD_PROJECT"
    )

# 初始化 Vertex AI 客戶端
vertexai.init(project=GOOGLE_CLOUD_PROJECT, location="us-central1")

# 初始化 Arize 客戶端 (僅需 api_key)
arize_client = ArizeDatasetsClient(api_key=ARIZE_API_KEY)


def load_test_data() -> list[dict]:
    """
    從 JSON 檔案加載測試會話數據。

    返回:
        list[dict]: 包含查詢、預期工具使用和參考文本的測試用例列表
    """
    with open("eval/data/conversation.test.json") as f:
        return json.load(f)


def create_arize_dataset():
    """
    從測試數據創建 Arize 數據集。

    流程:
    1. 加載測試數據
    2. 轉換為 Arize 格式 (id, query, expected_tool_use, reference)
    3. 創建 DataFrame
    4. 在 Arize 中上傳數據集

    返回:
        dict: 包含數據集 ID 的字典
    """
    test_data = load_test_data()

    # 轉換數據為 Arize 格式 - 簡化的結構
    dataset_rows = []
    for i, item in enumerate(test_data):
        dataset_rows.append(
            {
                "id": str(i),  # 明確的行 ID
                "query": item["query"],  # 用戶查詢
                "expected_tool_use": json.dumps(
                    item["expected_tool_use"]
                ),  # 轉換為 JSON 字符串
                "reference": item["reference"],  # 參考答案
            }
        )

    # 創建 pandas DataFrame
    df = pd.DataFrame(dataset_rows)

    # 調試: 打印 DataFrame 結構信息
    print("DataFrame 形狀:", df.shape)
    print("DataFrame 列:", df.columns.tolist())
    print("DataFrame 數據類型:", df.dtypes.to_dict())
    print("第一行樣本:", df.iloc[0].to_dict())

    # 在 Arize 中創建數據集
    dataset_name = f"rag_agent_evaluation_dataset-{uuid.uuid4()}"

    print(f"創建數據集: {dataset_name}")
    dataset_id = arize_client.create_dataset(
        space_id=ARIZE_SPACE_ID,
        dataset_name=dataset_name,
        data=df,
        dataset_type=GENERATIVE,  # 生成式 AI 任務類型
    )

    print(f"數據集已創建,ID: {dataset_id}")
    time.sleep(5)  # 等待數據集完全創建
    return {"id": dataset_id}


def extract_tool_calls_from_response(response_text: str, agent_runner) -> list[dict]:
    """
    從代理響應中提取工具調用信息。
    此方法創建 Vertex AI 評估 API 期望的軌跡格式。

    參數:
        response_text: 代理的文本響應
        agent_runner: 代理執行器實例 (用於訪問執行跟蹤)

    返回:
        list[dict]: 工具調用列表,每個包含 tool_name 和 tool_input
    """
    tool_calls = []
    max_response_length = 100

    # 對於 ADK 代理,需要檢查執行跟蹤
    # 這是一個簡化的實現 - 可根據需要調整以捕獲 RAG 工具使用

    # 檢查響應是否表明使用了工具
    if any(
        keyword in response_text.lower()
        for keyword in [
            "according to",  # 根據
            "based on",  # 基於
            "source:",  # 來源
            "[citation",  # 引用
            "retrieved",  # 檢索
            "documentation",  # 文檔
        ]
    ):
        # 推斷使用了 RAG 工具
        tool_calls.append(
            {
                "tool_name": "retrieve_rag_documentation",
                "tool_input": (
                    response_text[:max_response_length] + "..."
                    if len(response_text) > max_response_length
                    else response_text
                ),
            }
        )

    return tool_calls


async def call_rag_agent(query: str) -> dict[str, Any]:
    """
    異步調用 RAG 代理並返回帶有元數據的響應。

    流程:
    1. 創建 InMemoryRunner 實例
    2. 創建用戶會話
    3. 發送查詢並流式接收響應
    4. 提取工具使用信息

    參數:
        query: 用戶查詢文本

    返回:
        dict: 包含 response (響應文本) 和 tool_calls (使用的工具列表)
    """
    # 創建代理運行器
    runner = InMemoryRunner(agent=root_agent)

    # 創建用戶會話
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_user"
    )

    # 構建用戶內容
    content = UserContent(parts=[Part(text=query)])
    response_parts = []

    # 運行代理並流式收集響應部分
    for event in runner.run(
        user_id=session.user_id, session_id=session.id, new_message=content
    ):
        # 從事件中提取文本部分
        if event.content and event.content.parts:
            for part in event.content.parts:
                response_parts.append(part.text if part.text else "")

    # 連接所有響應部分為完整文本
    response_text = "\n".join(response_parts)

    # 提取工具使用信息
    tool_calls = extract_tool_calls_from_response(response_text, runner)

    return {"response": response_text, "tool_calls": tool_calls}


async def task_function(dataset_row: dict) -> str:
    """
    Arize 實驗的任務函數。
    此函數調用 RAG 代理並返回響應。

    參數:
        dataset_row: 來自 Arize 數據集的一行數據

    返回:
        str: JSON 序列化的元數據,包含響應和工具調用信息
    """
    # 從數據集行獲取查詢
    query = dataset_row.get("query", "")

    # 調用代理 (在異步上下文中使用 await)
    result = await call_rag_agent(query)

    # 為評估器準備元數據
    metadata = {
        "agent_response": result["response"],  # 代理的實際響應
        "tool_calls": result["tool_calls"],  # 代理使用的工具
        "expected_tool_use": dataset_row.get("expected_tool_use", "[]"),  # 預期的工具
        "reference": dataset_row.get("reference", ""),  # 參考答案
    }

    # 返回 JSON 字符串供評估器使用
    return json.dumps(metadata)


# ==================== Vertex AI 評估函數 ====================


def create_reference_trajectory(expected_tool_use: list[dict]) -> list[dict]:
    """
    將預期工具使用轉換為参考軌跡格式。

    參數:
        expected_tool_use: 預期工具使用列表

    返回:
        list[dict]: 軌跡格式的列表
    """
    if not expected_tool_use:
        return []

    trajectory = []
    for tool_use in expected_tool_use:
        trajectory.append(
            {
                "tool_name": tool_use.get("tool_name", ""),
                "tool_input": tool_use.get("tool_input", {}),
            }
        )
    return trajectory


def evaluate_with_vertex_ai_single_metric(
    predicted_trajectory: list[dict],
    reference_trajectory: list[dict],
    metric: str,
) -> dict[str, Any]:
    """
    使用 Vertex AI 原生評估 API 評估單個指標。

    參數:
        predicted_trajectory: 代理產生的軌跡
        reference_trajectory: 參考軌跡
        metric: 要計算的指標名稱

    返回:
        dict: 包含指標值的結果字典
    """
    try:
        # 創建評估數據集
        eval_dataset = pd.DataFrame(
            {
                "predicted_trajectory": [predicted_trajectory],
                "reference_trajectory": [reference_trajectory],
            }
        )

        # 創建單個指標的評估任務
        eval_task = EvalTask(
            dataset=eval_dataset,
            metrics=[metric],  # type: ignore[list-item]
        )

        # 運行評估
        eval_result = eval_task.evaluate()

        # 提取指標值
        metric_value = eval_result.summary_metrics.get(f"{metric}/mean", 0.0)
        results = {metric: metric_value}

        return results

    except Exception as e:
        print(f"Vertex AI 評估時出錯 ({metric}): {e}")
        return {metric: 0.0}


# ==================== 自定義評估器 ====================


def trajectory_exact_match_evaluator(
    output: str, dataset_row: dict
) -> EvaluationResult:
    """
    軌跡精確匹配評估器。
    檢查實際工具調用是否與預期完全匹配。

    評分:
        1.0: 精確匹配
        0.0: 不匹配
    """
    try:
        # 解析代理輸出中的元數據
        metadata = json.loads(output)
        actual_tool_calls = metadata.get("tool_calls", [])
        expected_tool_use = json.loads(dataset_row.get("expected_tool_use", "[]"))

        # 檢查工具數量是否相同
        if len(actual_tool_calls) != len(expected_tool_use):
            return EvaluationResult(
                score=0.0,
                label="no_exact_match",
                explanation=f"數量不匹配: 期望 {len(expected_tool_use)} 個工具,得到 {len(actual_tool_calls)} 個",
            )

        # 兩者都為空 - 完美匹配
        if not expected_tool_use and not actual_tool_calls:
            return EvaluationResult(
                score=1.0,
                label="exact_match",
                explanation="預期和實際工具使用都為空 - 完美匹配",
            )

        # 檢查工具名稱是否匹配
        actual_names = [tc.get("tool_name", "") for tc in actual_tool_calls]
        expected_names = [et.get("tool_name", "") for et in expected_tool_use]

        score = 1.0 if actual_names == expected_names else 0.0
        label = "exact_match" if score == 1.0 else "no_exact_match"
        explanation = f"工具序列匹配: 期望 {expected_names},得到 {actual_names}"

        return EvaluationResult(score=score, label=label, explanation=explanation)

    except Exception as e:
        return EvaluationResult(
            score=0.0, label="error", explanation=f"評估錯誤: {e!s}"
        )


def trajectory_precision_evaluator(output: str, dataset_row: dict) -> EvaluationResult:
    """
    軌跡精準度評估器。
    計算實際工具中有多少是期望的 (精準度 = 正確工具 / 實際工具)。

    評分:
        1.0: 完美精準度
        0.9-0.99: 高精準度
        0.7-0.89: 中等精準度
        < 0.7: 低精準度
    """
    high_precision = 0.9
    medium_precision = 0.7

    try:
        metadata = json.loads(output)
        actual_tool_calls = metadata.get("tool_calls", [])
        expected_tool_use = json.loads(dataset_row.get("expected_tool_use", "[]"))

        # 處理無預期工具的情況
        if not expected_tool_use:
            score = 1.0 if not actual_tool_calls else 0.0
            label = "perfect" if score == 1.0 else "unexpected_tools"
            explanation = "無預期工具" + (
                "" if score == 1.0 else f",但得到 {len(actual_tool_calls)} 個工具"
            )
            return EvaluationResult(score=score, label=label, explanation=explanation)

        # 計算精準度: 實際工具中期望的比例
        actual_names = {tc.get("tool_name", "") for tc in actual_tool_calls}
        expected_names = {et.get("tool_name", "") for et in expected_tool_use}

        # 未使用任何工具
        if not actual_names:
            return EvaluationResult(
                score=0.0,
                label="no_tools_used",
                explanation="期望使用工具但未使用",
            )

        # 計算交集與實際的比例
        intersection = actual_names.intersection(expected_names)
        score = len(intersection) / len(actual_names)

        # 根據分數分配標籤
        if score >= high_precision:
            label = "high_precision"
        elif score >= medium_precision:
            label = "medium_precision"
        else:
            label = "low_precision"

        explanation = f"精準度: {len(intersection)}/{len(actual_names)} = {score:.2f}. 期望: {sorted(expected_names)}, 使用: {sorted(actual_names)}"

        return EvaluationResult(score=score, label=label, explanation=explanation)

    except Exception as e:
        return EvaluationResult(
            score=0.0, label="error", explanation=f"評估錯誤: {e!s}"
        )


def tool_name_match_evaluator(output: str, dataset_row: dict) -> EvaluationResult:
    """
    工具名稱匹配評估器。
    檢查工具名稱是否匹配,忽略參數差異。

    評分:
        1.0: 完美匹配
        0.7-0.99: 良好匹配
        0.1-0.69: 部分匹配
        0.0: 無匹配
    """
    max_score = 1.0
    good_score = 0.7

    try:
        metadata = json.loads(output)
        actual_tool_calls = metadata.get("tool_calls", [])
        expected_tool_use = json.loads(dataset_row.get("expected_tool_use", "[]"))

        # 僅提取工具名稱 (忽略參數)
        actual_tool_names = set()
        for tool_call in actual_tool_calls:
            if isinstance(tool_call, dict) and "tool_name" in tool_call:
                actual_tool_names.add(tool_call["tool_name"])

        expected_tool_names = set()
        for expected_tool in expected_tool_use:
            if isinstance(expected_tool, dict) and "tool_name" in expected_tool:
                expected_tool_names.add(expected_tool["tool_name"])

        # 計算匹配分數
        if not expected_tool_names:
            # 無預期工具時: 未使用工具=1.0分,使用了工具=0分
            score = max_score if not actual_tool_names else 0.0
            label = "correct_no_tools" if score == max_score else "unexpected_tools"
            explanation = f"無預期工具。得到: {sorted(actual_tool_names) if actual_tool_names else '無'}"
        else:
            # 計算交集與預期的比例 (回想率)
            intersection = actual_tool_names.intersection(expected_tool_names)
            score = len(intersection) / len(expected_tool_names)

            # 根據分數分配詳細標籤
            if score == max_score:
                label = "perfect_match"
            elif score >= good_score:
                label = "good_match"
            elif score > 0:
                label = "partial_match"
            else:
                label = "no_match"

            explanation = f"工具覆蓋率: {len(intersection)}/{len(expected_tool_names)} = {score:.2f}. 期望: {sorted(expected_tool_names)}, 得到: {sorted(actual_tool_names)}"

        return EvaluationResult(score=score, label=label, explanation=explanation)

    except Exception as e:
        return EvaluationResult(
            score=0.0, label="error", explanation=f"評估錯誤: {e!s}"
        )


def run_evaluation_experiment():
    """
    運行完整的評估實驗。

    流程:
    1. 從測試數據創建 Arize 數據集
    2. 為每個數據集行調用 task_function
    3. 運行多個評估器
    4. 在 Arize UI 中查看結果
    """

    # 第 1 步: 創建數據集
    print("創建 Arize 數據集...")
    dataset = create_arize_dataset()

    # 第 2 步: 定義評估器
    # 使用多個獨立評估器以便在 Arize UI 中更好地可視化
    evaluators = [
        trajectory_exact_match_evaluator,  # 精確匹配
        trajectory_precision_evaluator,  # 精準度
        tool_name_match_evaluator,  # 工具名稱匹配
    ]

    # 第 3 步: 運行實驗
    print("運行實驗...")
    experiment_result = arize_client.run_experiment(
        space_id=ARIZE_SPACE_ID,
        dataset_id=dataset["id"],
        task=task_function,  # 調用代理的任務函數
        evaluators=evaluators,  # 評估函數列表
        experiment_name=f"rag_agent_evaluation_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}",
        concurrency=2,  # 並發數 - 減少以避免 API 過載
        exit_on_error=False,  # 遇到錯誤不停止
        dry_run=False,  # 實際運行,非乾跑
    )

    # 提取實驗 ID
    if hasattr(experiment_result, "id"):
        experiment_id = experiment_result.id
    elif isinstance(experiment_result, tuple) and len(experiment_result) > 0:
        experiment_id = (
            experiment_result[0].id
            if hasattr(experiment_result[0], "id")
            else str(experiment_result[0])
        )
    else:
        experiment_id = "unknown"

    print(f"實驗完成! 實驗 ID: {experiment_id}")
    print("在 Arize UI 中查看結果")

    return experiment_result


# ==================== 主程序入點 ====================

if __name__ == "__main__":
    # 運行評估實驗
    run_evaluation_experiment()

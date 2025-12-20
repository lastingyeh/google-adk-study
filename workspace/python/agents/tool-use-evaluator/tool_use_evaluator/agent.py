"""工具使用品質 (Tool Use Quality) 評估代理 (Agent)。

此代理展示了用於評估的不同工具使用模式：
- 良好的工具排序
- 不良的工具排序
- 工具效率
- 錯誤恢復
"""

from typing import Any
from google.adk.agents import Agent


def analyze_data(dataset: str) -> dict[str, Any]:
    """分析資料集 (模擬)。

    Args:
        dataset: 要分析的資料集名稱

    Returns:
        包含分析結果和元數據 (metadata) 的字典
    """
    if not dataset:
        return {
            "status": "error",
            "report": "Dataset name required",  # 為了測試相容性或保持簡潔，保留部分錯誤訊息，或翻譯為 "需要資料集名稱"
        }

    # 注意：測試可能檢查 "analyzed" 關鍵字
    return {
        "status": "success",
        "report": f"已分析 (Analyzed) 資料集: {dataset}",
        "data": {
            "records": 1000,
            "columns": 15,
            "types": ["numeric", "categorical", "date"],
        },
    }


def extract_features(data: dict[str, Any]) -> dict[str, Any]:
    """從分析數據中提取特徵。

    Args:
        data: 來自分析的輸入數據字典

    Returns:
        包含已提取特徵的字典
    """
    if not data:
        return {
            "status": "error",
            "report": "Data required for feature extraction",
        }

    return {
        "status": "success",
        "report": "已從數據中提取特徵",
        "data": {
            "features": ["mean", "median", "std_dev", "correlation"],
            "count": 4,
        },
    }


def validate_quality(features: dict[str, Any]) -> dict[str, Any]:
    """驗證特徵品質 (模擬)。

    Args:
        features: 要驗證的特徵

    Returns:
        包含驗證結果的字典
    """
    if not features:
        return {
            "status": "error",
            "report": "Features required for validation",
        }

    return {
        "status": "success",
        "report": "特徵品質驗證通過",
        "data": {
            "quality_score": 0.92,
            "valid_features": 4,
            "issues": [],
        },
    }


def apply_model(features: dict[str, Any], model: str) -> dict[str, Any]:
    """將機器學習 (ML) 模型應用於特徵。

    Args:
        features: 要應用模型的特徵
        model: 要應用的模型名稱

    Returns:
        包含模型應用結果的字典
    """
    if not features or not model:
        return {
            "status": "error",
            "report": "Features and model name required",
        }

    return {
        "status": "success",
        "report": f"已將 {model} 模型應用於特徵",
        "data": {
            "model": model,
            "predictions": 1000,
            "accuracy": 0.87,
        },
    }


# 定義用於評估工具使用的代理
root_agent = Agent(
    name="tool_use_evaluator",
    model="gemini-2.0-flash",
    description="用於展示工具使用品質 (tool use quality) 評估的代理",
    instruction="""
    您是一位展示正確工具排序的數據 (data) 分析助理。

    當被要求分析數據時：
    1. 首先 (FIRST)：分析資料集
    2. 然後 (THEN)：從分析中提取特徵
    3. 然後 (THEN)：驗證特徵品質
    4. 最後 (FINALLY)：應用機器學習 (ML) 模型

    此順序展示了：
    - 正確的工具排序 (先決條件優先)
    - 工具依賴性 (每個步驟都建立在前一個步驟之上)
    - 完整的流程 (包含所有步驟)
    - 錯誤處理 (適當的驗證)

    請勿跳過步驟或亂序呼叫工具。
    始終遵循：分析 (analyze) → 提取 (extract) → 驗證 (validate) → 應用 (apply)
    """,
    tools=[
        analyze_data,
        extract_features,
        validate_quality,
        apply_model,
    ],
    output_key="analysis_result",
)

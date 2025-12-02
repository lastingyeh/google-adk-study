"""數據分析 ADK Agent，整合 pandas 工具與 AG-UI。

此 Agent 提供數據分析功能，包含 CSV 數據載入、
統計分析以及圖表生成工具。透過 AG-UI 協議與 Vite+React
前端整合。
"""

import os
import io
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# AG-UI ADK 整合匯入
try:
    from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
except ImportError:
    raise ImportError(
        "未找到 ag_ui_adk。請安裝：pip install ag-ui-adk"
    )

# Google ADK 匯入
from google.adk.agents import Agent

# 數據分析匯入
try:
    import pandas as pd
except ImportError:
    raise ImportError(
        "未找到 pandas。請安裝：pip install pandas"
    )

# 載入環境變數
load_dotenv()


# ============================================================================
# 記憶體內數據儲存（生產環境請使用 Redis/DB）
# ============================================================================

uploaded_data: Dict[str, pd.DataFrame] = {}


# ============================================================================
# 工具定義
# ============================================================================


def load_csv_data(file_name: str, csv_content: str) -> Dict[str, Any]:
    """
    將 CSV 數據載入記憶體以進行分析。

    Args:
        file_name: CSV 檔案名稱
        csv_content: CSV 檔案內容字串

    Returns:
        Dict 包含狀態、報告、數據集資訊和預覽
    """
    try:
        # 解析 CSV
        df = pd.read_csv(io.StringIO(csv_content))

        # 儲存於記憶體
        uploaded_data[file_name] = df

        # 回傳摘要
        return {
            "status": "success",
            "report": (
                f"成功載入 {file_name}，共 {len(df)} 列 "
                f"及 {len(df.columns)} 欄。"
            ),
            "file_name": file_name,
            "rows": len(df),
            "columns": list(df.columns),
            "preview": df.head(5).to_dict(orient='records'),
            "dtypes": df.dtypes.astype(str).to_dict()
        }
    except Exception as e:
        return {
            "status": "error",
            "report": f"載入 {file_name} 失敗：{str(e)}",
            "error": str(e)
        }


def analyze_data(
    file_name: str,
    analysis_type: str,
    columns: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    對載入的數據集執行統計分析。

    Args:
        file_name: 要分析的數據集名稱
        analysis_type: 分析類型 ('summary', 'correlation', 'trend')
        columns: 選擇性欄位列表，指定要分析的欄位

    Returns:
        Dict 包含狀態、報告和分析結果
    """
    if file_name not in uploaded_data:
        return {
            "status": "error",
            "report": f"找不到數據集 {file_name}。請先載入它。",
            "error": f"找不到數據集 {file_name}"
        }

    try:
        df = uploaded_data[file_name]

        # 如果有指定，篩選欄位
        if columns:
            missing_cols = [col for col in columns if col not in df.columns]
            if missing_cols:
                return {
                    "status": "error",
                    "report": f"找不到欄位：{', '.join(missing_cols)}",
                    "error": f"無效的欄位：{missing_cols}"
                }
            df = df[columns]

        results = {
            "status": "success",
            "file_name": file_name,
            "analysis_type": analysis_type
        }

        if analysis_type == "summary":
            # 統計摘要
            numeric_df = df.select_dtypes(include=['number'])
            results["report"] = (
                f"已生成 {file_name} 中 {len(numeric_df.columns)} 個"
                f"數值欄位的統計摘要。"
            )
            results["data"] = {
                "describe": numeric_df.describe().to_dict(),
                "missing": df.isnull().sum().to_dict(),
                "unique": df.nunique().to_dict()
            }

        elif analysis_type == "correlation":
            # 相關性分析
            numeric_df = df.select_dtypes(include=['number'])
            if len(numeric_df.columns) < 2:
                return {
                    "status": "error",
                    "report": "相關性分析至少需要 2 個數值欄位",
                    "error": "數值欄位不足"
                }
            results["report"] = (
                f"已計算 {file_name} 中 {len(numeric_df.columns)} 個"
                f"數值欄位的相關性。"
            )
            results["data"] = numeric_df.corr().to_dict()

        elif analysis_type == "trend":
            # 時間序列趨勢分析
            numeric_df = df.select_dtypes(include=['number'])
            if len(numeric_df) < 2:
                return {
                    "status": "error",
                    "report": "趨勢分析至少需要 2 列數據",
                    "error": "數據點不足"
                }

            # 計算平均趨勢
            means = numeric_df.mean().to_dict()
            first_sum = numeric_df.iloc[0].sum()
            last_sum = numeric_df.iloc[-1].sum()
            trend_direction = "上升" if last_sum > first_sum else "下降"

            results["report"] = (
                f"分析了 {file_name} 的趨勢。整體趨勢為{trend_direction}。"
            )
            results["data"] = {
                "mean": means,
                "trend": trend_direction,
                "first_row_sum": float(first_sum),
                "last_row_sum": float(last_sum)
            }

        else:
            return {
                "status": "error",
                "report": f"未知的分析類型：{analysis_type}",
                "error": f"無效的 analysis_type：{analysis_type}"
            }

        return results

    except Exception as e:
        return {
            "status": "error",
            "report": f"分析失敗：{str(e)}",
            "error": str(e)
        }


def create_chart(
    file_name: str,
    chart_type: str,
    x_column: str,
    y_column: str
) -> Dict[str, Any]:
    """
    生成視覺化圖表數據。

    Args:
        file_name: 數據集名稱
        chart_type: 圖表類型 ('line', 'bar', 'scatter')
        x_column: X 軸欄位
        y_column: Y 軸欄位

    Returns:
        Dict 包含狀態、報告和圖表設定
    """
    if file_name not in uploaded_data:
        return {
            "status": "error",
            "report": f"找不到數據集 {file_name}。請先載入它。",
            "error": f"找不到數據集 {file_name}"
        }

    try:
        df = uploaded_data[file_name]

        # 驗證欄位
        if x_column not in df.columns:
            return {
                "status": "error",
                "report": f"數據集中找不到欄位 {x_column}",
                "error": f"無效的 x_column：{x_column}"
            }
        if y_column not in df.columns:
            return {
                "status": "error",
                "report": f"數據集中找不到欄位 {y_column}",
                "error": f"無效的 y_column：{y_column}"
            }

        # 驗證圖表類型
        valid_types = ['line', 'bar', 'scatter']
        if chart_type not in valid_types:
            return {
                "status": "error",
                "report": f"無效的圖表類型。請使用：{', '.join(valid_types)}",
                "error": f"無效的 chart_type：{chart_type}"
            }

        # 準備圖表數據
        # 轉換為簡單類型以確保 JSON 序列化
        x_data = df[x_column].tolist()
        y_data = df[y_column].tolist()

        # 將 numpy 類型轉換為 Python 類型
        x_data = [str(x) for x in x_data]
        y_data = [float(y) if pd.notna(y) else 0 for y in y_data]

        chart_data = {
            "status": "success",
            "report": (
                f"已從 {file_name} 生成 {y_column} 對 {x_column} 的 {chart_type} 圖表，"
                f"包含 {len(x_data)} 個數據點。"
            ),
            "chart_type": chart_type,
            "data": {
                "labels": x_data,
                "values": y_data
            },
            "options": {
                "x_label": x_column,
                "y_label": y_column,
                "title": f"{y_column} vs {x_column}"
            }
        }

        return chart_data

    except Exception as e:
        return {
            "status": "error",
            "report": f"圖表生成失敗：{str(e)}",
            "error": str(e)
        }


# ============================================================================
# ADK Agent 設定
# ============================================================================

# 建立具有數據分析工具的 ADK agent
adk_agent = Agent(
    name="data_analyst",
    model="gemini-2.0-flash-exp",
    instruction="""你是一位精通統計分析與數據視覺化的數據分析專家助手。

    你的能力：
    - 使用 load_csv_data(file_name, csv_content) 載入 CSV 數據集
    - 使用 analyze_data(file_name, analysis_type, columns) 執行統計分析
    - 使用 create_chart(file_name, chart_type, x_column, y_column) 生成視覺化圖表

    可用的分析類型：
    - "summary"：描述性統計、遺失值、唯一計數
    - "correlation"：數值欄位的相關性矩陣
    - "trend"：時間序列趨勢分析

    可用的圖表類型：
    - "line"：隨時間變化的趨勢折線圖
    - "bar"：類別比較的長條圖
    - "scatter"：關係散佈圖

    指引：
    1. 總是先從載入數據開始（若尚未載入）
    2. 使用 markdown 格式清楚解釋你的分析
    3. 根據數據類型建議相關的視覺化圖表
    4. 使用 **粗體** 文字強調關鍵洞察
    5. 適當地使用統計術語
    6. 分析數據時，先理解結構
    7. 執行適當的分析（摘要、相關性或趨勢）
    8. 在有幫助時生成視覺化圖表
    9. 提供可操作的洞察

    工作流程：
    1. 載入 CSV 數據
    2. 檢查數據結構（欄位、類型、範例數據）
    3. 執行請求的分析或建議適當的分析
    4. 如果相關，建立視覺化圖表
    5. 用清晰的洞察總結發現

    解釋要簡潔但詳盡。使用 markdown 表格以提高可讀性。""",
    tools=[load_csv_data, analyze_data, create_chart]
)

# 匯出以供測試
root_agent = adk_agent


# ============================================================================
# FastAPI 應用程式設定
# ============================================================================

app = FastAPI(
    title="Data Analysis Agent API",
    description="結合 pandas 與 Chart.js 視覺化的 CSV 數據分析 ADK agent",
    version="1.0.0"
)

# 為前端加入 CORS 中介軟體
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite 開發伺服器
        "http://localhost:5174",  # 替代 Vite port
        "http://localhost:3000",  # 替代前端 port
        "http://localhost:8080",  # 替代前端 port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# CopilotKit 端點（使用 AG-UI ADK）
# ============================================================================

# 使用 AG-UI 中介軟體封裝 ADK agent
ag_ui_agent = ADKAgent(
    adk_agent=adk_agent,
    app_name="data_analysis_dashboard",
    user_id="demo_user"
)

# 加入 CopilotKit 資訊端點 - CopilotKit 1.10.x 所需
@app.get("/api/copilotkit")
async def copilotkit_info():
    """
    用於 Agent 探索的 CopilotKit 資訊端點。
    以 CopilotKit 預期的格式回傳 Agent 資訊。
    """
    return {
        "agents": [
            {
                "name": "data_analyst",
                "description": "具備 CSV 工具的專家數據分析助手",
                "tools": ["load_csv_data", "analyze_data", "create_chart"]
            }
        ],
        "version": "1.0.0"
    }


# 為 CopilotKit 加入 AG-UI ADK 端點
# 這會建立一個 /api/copilotkit 端點，讓 CopilotKit 可以直接連線
add_adk_fastapi_endpoint(app, ag_ui_agent, path="/api/copilotkit")


# ============================================================================
# 額外 API 端點
# ============================================================================

@app.get("/info")
def info() -> Dict[str, Any]:
    """
    CopilotKit 資訊端點 - 提供 Agent 能力。

    Returns:
        Dict 包含 Agent 資訊
    """
    return {
        "agents": [
            {
                "name": "data_analyst",
                "description": "具備 CSV 工具的專家數據分析助手",
                "capabilities": ["data_analysis", "visualization", "statistics"]
            }
        ]
    }


@app.get("/health")
def health_check() -> Dict[str, Any]:
    """
    健康檢查端點。

    Returns:
        Dict 包含狀態、Agent 名稱和已載入的數據集
    """
    return {
        "status": "healthy",
        "agent": "data_analyst",
        "datasets_loaded": list(uploaded_data.keys()),
        "num_datasets": len(uploaded_data)
    }


@app.get("/datasets")
def list_datasets() -> Dict[str, Any]:
    """
    列出所有已載入的數據集。

    Returns:
        Dict 包含已載入的數據集名稱及其資訊
    """
    datasets_info = {}
    for name, df in uploaded_data.items():
        datasets_info[name] = {
            "rows": len(df),
            "columns": list(df.columns),
            "dtypes": df.dtypes.astype(str).to_dict()
        }

    return {
        "status": "success",
        "datasets": datasets_info,
        "count": len(uploaded_data)
    }


# ============================================================================
# 主要進入點
# ============================================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "agent:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

#### 重點摘要 (程式碼除外)
# - **核心概念**：一個基於 FastAPI 和 Google ADK 的後端 Agent，專門用於 CSV 數據分析和視覺化。
# - **關鍵技術**：FastAPI, pandas, Google ADK (Gemini 2.0 Flash), AG-UI Protocol。
# - **重要結論**：
#   - 提供了三個主要工具：`load_csv_data`（載入 CSV）、`analyze_data`（統計分析）、`create_chart`（生成圖表數據）。
#   - 使用記憶體（dict）暫存上傳的數據，生產環境建議改用資料庫。
#   - 透過 AG-UI 協議與前端溝通，並支援 CORS。
# - **行動項目**：確保安裝 `ag-ui-adk` 和 `pandas`，並設定環境變數 `PORT`（預設 8000）。

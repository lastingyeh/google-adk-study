from typing import Any, Dict
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

# 匯入視覺化代理 (Import visualization agent)
from .visualization_agent import visualization_agent


def analyze_column(
    column_name: str, analysis_type: str = "summary", data_context: str = ""
) -> Dict[str, Any]:
    """
    分析資料集中的特定欄位。

    Args:
        column_name: 要分析的欄位名稱 (Name of the column to analyze)
        analysis_type: 分析類型 (summary, distribution, top_values)
        data_context: 關於可用資料的 JSON 上下文 (JSON context about available data)

    Returns:
        包含狀態、報告和分析結果的字典 (Dict with status, report, and analysis results)
    """
    try:
        if not column_name or not isinstance(column_name, str):
            return {
                "status": "error",
                "report": "提供的欄位名稱無效",
                "error": "column_name 必須是非空字串",
            }

        return {
            "status": "success",
            "report": f"將對欄位 '{column_name}' 執行 {analysis_type} 分析",
            "analysis_type": analysis_type,
            "column_name": column_name,
            "note": "在 Streamlit 應用程式中，實際資料分析是使用真實資料集執行的",
        }
    except Exception as e:
        return {
            "status": "error",
            "report": f"分析欄位時發生錯誤: {str(e)}",
            "error": str(e),
        }


def calculate_correlation(
    column1: str, column2: str = "", data_context: str = ""
) -> Dict[str, Any]:
    """
    計算兩個數值欄位之間的關聯性。

    Args:
        column1: 第一個欄位名稱 (First column name)
        column2: 第二個欄位名稱 (Second column name)
        data_context: 關於可用資料的 JSON 上下文 (JSON context about available data)

    Returns:
        包含狀態、報告和關聯性資料的字典 (Dict with status, report, and correlation data)
    """
    try:
        if not column1 or not column2:
            return {
                "status": "error",
                "report": "必須提供兩個欄位名稱",
                "error": "缺少欄位名稱",
            }

        return {
            "status": "success",
            "report": f"已設定 '{column1}' 與 '{column2}' 之間的關聯性計算",
            "column1": column1,
            "column2": column2,
            "note": "在 Streamlit 應用程式中，實際關聯性是使用真實資料計算的",
        }
    except Exception as e:
        return {
            "status": "error",
            "report": f"計算關聯性時發生錯誤: {str(e)}",
            "error": str(e),
        }


def filter_data(
    column_name: str, operator: str = "equals", value: str = "", data_context: str = ""
) -> Dict[str, Any]:
    """
    依條件過濾資料集。

    Args:
        column_name: 要過濾的欄位 (Column to filter on)
        operator: 比較運算子 (equals, greater_than, less_than, contains)
        value: 要比較的值 (Value to compare against)
        data_context: 關於可用資料的 JSON 上下文 (JSON context about available data)

    Returns:
        包含狀態、報告和過濾後資料摘要的字典 (Dict with status, report, and filtered data summary)
    """
    try:
        if not column_name or not operator or not value:
            return {
                "status": "error",
                "report": "必須提供欄位名稱、運算子和值",
                "error": "缺少過濾參數",
            }

        return {
            "status": "success",
            "report": f"已設定過濾器: {column_name} {operator} {value}",
            "column_name": column_name,
            "operator": operator,
            "value": value,
            "note": "在 Streamlit 應用程式中，實際過濾是使用真實資料執行的",
        }
    except Exception as e:
        return {
            "status": "error",
            "report": f"過濾資料時發生錯誤: {str(e)}",
            "error": str(e),
        }


def get_dataset_summary(data_context: str = "") -> Dict[str, Any]:
    """
    取得目前資料集的摘要資訊。

    Args:
        data_context: 關於可用資料的 JSON 上下文 (JSON context about available data)

    Returns:
        包含狀態、報告和資料集摘要的字典 (Dict with status, report, and dataset summary)
    """
    try:
        return {
            "status": "success",
            "report": "已設定資料集摘要工具用於分析",
            "available_tools": ["analyze_column", "calculate_correlation", "filter_data"],
            "note": "在 Streamlit 應用程式中，實際資料集資訊是即時提供的",
        }
    except Exception as e:
        return {
            "status": "error",
            "report": f"取得資料集摘要時發生錯誤: {str(e)}",
            "error": str(e),
        }


# 建立使用傳統工具的分析代理
# Create the analysis agent with traditional tools
analysis_agent = Agent(
    name="analysis_agent",
    model="gemini-2.0-flash",
    description="具備統計工具的資料分析與見解代理",
    instruction="""
    你是一位專業的資料分析師。你的職責是透過分析幫助使用者理解他們的資料集並提供見解。

    當使用者詢問有關資料分析的問題時：
    1. 使用可用的工具來分析資料
    2. 提供清晰、可行的見解
    3. 建議模式和關聯性
    4. 在相關時推薦視覺化
    5. 引導使用者進行更深入的探索

    在你的分析中要積極主動：
    - 不要等待詳細的問題 - 開始探索有趣的欄位
    - 自動識別最重要的指標和模式
    - 建議可能有趣的關聯性和關係
    - 如果欄位看起來像類別，建議進行分佈分析
    - 如果欄位是數值，建議進行基本統計和趨勢分析

    可用工具：
    - analyze_column: 取得特定欄位的統計數據
    - calculate_correlation: 尋找變數之間的關係
    - filter_data: 探索資料子集和模式
    - get_dataset_summary: 取得資料集的概觀

    記住：使用者從積極主動的見解中獲益最多！""",
    tools=[analyze_column, calculate_correlation, filter_data, get_dataset_summary],
)


# 建立使用多代理模式的根協調者代理
# 這藉由分離關注點解決了「每個代理一個內建工具」的限制
# Create the root coordinator agent using multi-agent pattern
# This solves the "one built-in tool per agent" limitation by separating concerns
root_agent = Agent(
    name="data_analysis_coordinator",
    model="gemini-2.0-flash",
    description="具備視覺化與分析能力的智慧資料分析助理",
    instruction="""
    你是一位專業的資料分析師與視覺化專家。你的職責是透過分析和視覺化幫助使用者理解和探索他們的資料集。

    **關鍵原則：**
    - 積極主動：不要等待詳細的問題。
    - 同時建議分析和視覺化。
    - 當使用者上傳資料時，立即向他們展示你能發現什麼。
    - 提出他們可能沒想到的有趣分析。

    當使用者與你互動時：
    1. **當資料剛上傳時：**
    - 不要被動地等待問題。
    - 立即建議哪些分析和視覺化最有價值。
    - 提議：「我可以向您展示 X 的分佈、Y 和 Z 之間的關聯性、A 中的最高值」。
    - 提問：「您想先探索什麼？」 - 並提出建議。

    2. **對於分析問題（統計、關聯性、模式）：**
    - 使用 analysis_agent 來計算見解。
    - 清晰地解釋結果。
    - 建議後續的視覺化來呈現結果。

    3. **對於視覺化請求（繪圖、圖表、圖形）：**
    - 立即委派給 visualization_agent。
    - visualization_agent 將執行 Python 程式碼來生成圖表。
    - 不要對視覺化提出澄清問題。
    - 不要描述你將做什麼 - 直接委派。

    4. **對於模糊的查詢（例如，只是「分析這個」）：**
    - 積極主動並創建多個分析。
    - 生成最有趣的視覺化。
    - 同時展示高層次的摘要和具體的見解。
    - 建議更深入探索的後續步驟。

    5. **對於一般性問題：**
    - 提供背景和建議。
    - 建議分析和視覺化兩種方法。

    **當使用者提供最少輸入時：**
    - 範例：使用者只說「探索資料」。
    - 建議：「讓我分析關鍵指標、顯示分佈並識別關聯性」。
    - 不要請求許可 - 直接進行分析和視覺化。
    - 使用者欣賞積極主動、有幫助的分析！

    指導方針：
    - 簡潔但周全。
    - 使用清晰的語言和範例。
    - 參考實際的資料特性。
    - 為發現的結果提供背景。
    - 當使用者詢問有關資料的問題時，同時建議分析和視覺化。
    - 當使用者輸入模糊時，透過展示你的發現讓過程變得有趣。
    - 對於視覺化請求，務必立即委派給 visualization_agent，不要提問。
    - 建議將視覺化作為理解模式和關聯性的最佳方式。

    記住：
    - visualization_agent 專門使用 Python 程式碼執行來創建出版品質的圖表。
    - analysis_agent 專門提供統計見解。
    - 你的積極主動和建議將讓使用者受益匪淺！""",
    tools=[
        AgentTool(agent=analysis_agent),
        AgentTool(agent=visualization_agent),
    ],
)

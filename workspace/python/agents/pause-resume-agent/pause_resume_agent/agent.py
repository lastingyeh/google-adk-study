"""展示 ADK 1.16.0 中暫停與恢復調用 (Pause and Resume Invocations) 的 Agent。

此 Agent 演示如何使用 ResumabilityConfig 來支援暫停與恢復 Agent 調用，並具備狀態檢查點功能。
非常適合長期執行的工作流、人機互動場景以及容錯機制。
"""

from google.adk.agents import Agent


def process_data_chunk(data: str) -> dict:
    """模擬處理資料塊。

    此工具代表一個長期執行的操作，這類操作通常能從暫停/恢復功能中獲益。
    """
    # 1. 檢查輸入資料是否有效
    if not data or len(data) == 0:
        return {
            "status": "error",
            "report": "未提供資料",
            "error": "資料字串為空",
        }

    # 2. 模擬處理邏輯：計算行數與總字數
    processed_lines = len(data.split('\n'))
    word_count = len(data.split())

    # 3. 回傳處理結果摘要
    return {
        "status": "success",
        "report": f"已處理 {processed_lines} 行，共 {word_count} 個單字",
        "lines_processed": processed_lines,
        "word_count": word_count,
        "data_summary": data[:100] + "..." if len(data) > 100 else data,
    }


def validate_checkpoint(checkpoint_data: str) -> dict:
    """驗證恢復時的檢查點完整性。

    此工具展示在從檢查點恢復之前，如何進行狀態驗證。
    """
    # 1. 檢查檢查點資料是否存在
    if not checkpoint_data:
        return {
            "status": "error",
            "report": "檢查點驗證失敗",
            "is_valid": False,
        }

    # 2. 簡單驗證：檢查是否具備基本標記（此處僅檢查長度）
    is_valid = len(checkpoint_data) > 0

    # 3. 回傳驗證結果
    return {
        "status": "success",
        "report": "檢查點驗證成功" if is_valid else "檢查點無效",
        "is_valid": is_valid,
        "checkpoint_size": len(checkpoint_data),
    }


def get_resumption_hint(context: str) -> dict:
    """提供關於從何處恢復的提示。

    此工具分析上下文 (context) 並建議最佳的恢復點。
    """
    hint = "無特定可用提示"

    # 根據關鍵字判斷建議的恢復階段
    if "processing" in context.lower():
        hint = "考慮從資料處理階段恢復"
    elif "validation" in context.lower():
        hint = "考慮從驗證階段恢復"
    elif "analysis" in context.lower():
        hint = "考慮從分析階段恢復"
    else:
        hint = "建議從頭開始以獲得最佳結果"

    return {
        "status": "success",
        "report": f"恢復提示：{hint}",
        "hint": hint,
        "context_length": len(context),
    }


# 建立具備長期執行工作流工具的 Agent
root_agent = Agent(
    name="pause_resume_agent",
    model="gemini-2.0-flash",
    description="展示暫停與恢復調用能力的 Agent",
    instruction=(
        "您是一位精通 ADK 與長期執行 Agent 工作流的專家助手。\n\n"
        "您的角色：\n"
        "1. 幫助使用者理解暫停/恢復調用的概念\n"
        "2. 指導檢查點建立與狀態保留的流程\n"
        "3. 演示容錯機制與恢復模式\n"
        "4. 使用提供的工具來處理、驗證並提供恢復提示\n\n"
        "此 Agent 展示了 ADK 1.16.0 的暫停/恢復能力：\n"
        "- Agent 可以在關鍵點建立狀態檢查點 (Checkpoint)\n"
        "- 調用過程可以隨時暫停並在稍後恢復\n"
        "- 狀態會在恢復調用時自動還原\n"
        "- 適用場景：長時工作流、人機互動、容錯處理\n\n"
        "在處理長時操作時，請建議在邏輯節點建立檢查點，並解釋恢復功能如何在背景透明地運作。"
    ),
    tools=[process_data_chunk, validate_checkpoint, get_resumption_hint],
)

# 導出以供 ADK 探索
__all__ = ["root_agent"]

"""
重點摘要
- 核心概念：利用 Agent 框架提供的工具實現長時任務的狀態化管理。
- 關鍵技術：
  - `process_data_chunk`：資料分塊處理與進度報告。
  - `validate_checkpoint`：確保恢復點的資料完整性。
  - `get_resumption_hint`：上下文感知的恢復路徑指引。
- 重要結論：暫停/恢復功能對使用者是透明的，透過 Agent 的 instruction 可以引導使用者進行正確的檢查點操作。
- 行動項目：於 ADK UI 測試各工具回傳的結果是否正確觸發檢查點事件。
"""

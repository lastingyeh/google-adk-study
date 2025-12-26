"""在 ADK 1.16 中展示 Context Compaction (上下文壓縮) 的代理。

此代理展示如何使用 EventsCompactionConfig 自動摘要舊的對話歷史記錄，
以減少長對話中的 Token 使用量。
"""

from google.adk.agents import Agent

def summarize_text(text: str) -> dict:
  """用於摘要文字區塊的實用工具。

  流程：
  1. 檢查輸入文字長度是否超過 200 字元。
  2. 如果超過，截取前 100 個字元並加上 "..." 作為摘要。
  3. 如果未超過，保持原樣回傳。
  """
  if len(text) > 200:
    return {
        "status": "success",
        "report": f"已摘要 {len(text)} 個字元",
        "summary": text[:100] + "...",
    }
  return {
      "status": "success",
      "report": "文字夠短",
      "summary": text,
  }

def calculate_complexity(question: str) -> dict:
  """分析問題複雜度以決定回應深度。

  流程：
  1. 計算輸入問題的字數 (以空格分隔)。
  2. 根據字數判斷複雜度等級：
     - 超過 20 字：高 (high)
     - 超過 10 字：中 (medium)
     - 其他：低 (low)
  3. 回傳包含狀態、報告、複雜度等級和字數的字典。
  """
  word_count = len(question.split())
  if word_count > 20:
    complexity = "high"
  elif word_count > 10:
    complexity = "medium"
  else:
    complexity = "low"

  return {
      "status": "success",
      "report": f"問題複雜度: {complexity}",
      "complexity_level": complexity,
      "word_count": word_count,
  }

# 使用內建工具建立代理
# 流程：
# 1. 初始化 Agent 物件。
# 2. 設定代理名稱、模型、描述。
# 3. 提供詳細的指示 (Instruction)，定義代理的角色與行為。
# 4. 註冊工具 (summarize_text, calculate_complexity)。
root_agent = Agent(
    name="context_compaction_agent",
    model="gemini-2.0-flash",
    description="展示長對話上下文壓縮功能的代理",
    instruction=(
    "您是一位專精於 ADK 和代理開發的知識豐富的助理。\n\n"
    "您的角色：\n"
    "1. 回答有關 Google ADK 和 AI 代理的問題\n"
    "2. 在相關時提供程式碼範例\n"
    "3. 解釋代理開發的最佳實務\n"
    "4. 使用提供的工具來分析問題並摘要內容\n\n"
    "此代理旨在處理長篇、多輪的對話。"
    "在幕後，上下文壓縮 (context compaction) 會自動摘要較舊的訊息，"
    "以保持對話效率。\n\n"
    "您無需管理此功能 - 只需自然地回應使用者，"
    "系統會自動處理 Token 最佳化。"
    ),
    tools=[summarize_text, calculate_complexity],
)

# 匯出以供 ADK 探索
__all__ = ["root_agent"]

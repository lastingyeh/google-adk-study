"""
教學 04：循序工作流程 - 部落格創建流水線 (blog_creation_pipeline)

本教學展示如何將多個代理串連成嚴格的序列，以建立複雜的流水線。
部落格創建流水線由 4 個代理組成，它們協同合作來研究、撰寫、編輯和格式化部落格文章。
"""

from __future__ import annotations

from google.adk.agents import Agent, SequentialAgent

# ============================================================================
# 個別代理
# ============================================================================

# ===== 代理 1：研究代理 =====
# 收集關於主題的關鍵事實
research_agent = Agent(
  name="researcher",
  model="gemini-2.0-flash",
  description="研究主題並收集關鍵資訊",
  instruction=(
    "你是一個研究助理。你的任務是收集使用者請求主題的關鍵事實和資訊。\n"
    "\n"
    "輸出一個包含 5-7 個關鍵事實或見解的項目列表。"
    "專注於有趣、具體的資訊，讓部落格文章更引人入勝。\n"
    "\n"
    "格式：\n"
    "• 事實 1\n"
    "• 事實 2\n"
    "• 等等。\n"
    "\n"
    "只輸出項目列表，不要其他內容。"
  ),
  output_key="research_findings",  # 【重點】儲存至 state['research_findings']，供後續代理使用
)

# ===== 代理 2：撰稿代理 =====
# 根據研究結果撰寫部落格文章草稿
writer_agent = Agent(
  name="writer",
  model="gemini-2.0-flash",
  description="根據研究結果撰寫部落格文章草稿",
  instruction=(
    "你是一位創意部落格作家。根據以下研究結果撰寫一篇引人入勝的部落格文章。\n"
    "\n"
    "**研究結果：**\n"
    "{research_findings}\n"  # 【重點】從 state 讀取前一個代理的輸出！
    "\n"
    "撰寫一篇 3-4 段的部落格文章，需要：\n"
    "- 有吸引人的開頭\n"
    "- 自然地融入關鍵事實\n"
    "- 有總結主題的結論\n"
    "- 使用友善、對話式的語氣\n"
    "\n"
    "只輸出部落格文章內容，不要元評論。"
  ),
  output_key="draft_post",  # 【重點】儲存至 state['draft_post']
)

# ===== 代理 3：編輯代理 =====
# 審閱草稿並提供改進建議
editor_agent = Agent(
  name="editor",
  model="gemini-2.0-flash",
  description="審閱部落格文章草稿並提供編輯回饋",
  instruction=(
    "你是一位經驗豐富的編輯。審閱以下部落格文章草稿並提供建設性回饋。\n"
    "\n"
    "**部落格文章草稿：**\n"
    "{draft_post}\n"  # 【重點】從 state 讀取！
    "\n"
    "分析文章的：\n"
    "1. 清晰度和流暢度\n"
    "2. 文法和風格\n"
    "3. 吸引力和讀者興趣\n"
    "4. 結構和組織\n"
    "\n"
    "提供簡短的具體改進建議列表。"
    "如果文章很優秀，只需說：「無需修改 - 文章已準備就緒。」\n"
    "\n"
    "只輸出回饋，不要其他內容。"
  ),
  output_key="editorial_feedback",  # 【重點】儲存至 state['editorial_feedback']
)

# ===== 代理 4：格式化代理 =====
# 應用編輯建議並格式化為 markdown
formatter_agent = Agent(
  name="formatter",
  model="gemini-2.0-flash",
  description="應用編輯回饋並格式化最終部落格文章",
  instruction=(
    "你是一位格式化專員。透過應用編輯回饋來改進草稿，建立部落格文章的最終版本。\n"
    "\n"
    "**原始草稿：**\n"
    "{draft_post}\n"  # 【重點】從 state 讀取！
    "\n"
    "**編輯回饋：**\n"
    "{editorial_feedback}\n"  # 【重點】從 state 讀取！
    "\n"
    "透過以下方式建立最終部落格文章：\n"
    "1. 應用建議的改進\n"
    "2. 格式化為正確的 markdown，包含：\n"
    "   - 引人注目的標題（# 標題）\n"
    "   - 適當的章節標題（## 子標題）\n"
    "   - 適當的段落間隔\n"
    "   - 適當使用粗體/斜體來強調\n"
    "\n"
    "如果回饋說「無需修改」，只需將原始草稿格式化得美觀即可。\n"
    "\n"
    "只輸出 markdown 格式的最終部落格文章。"
  ),
  output_key="final_post",  # 【重點】儲存至 state['final_post']
)

# ============================================================================
# 循序流水線
# ============================================================================

# 建立循序流水線
# 【重點】SequentialAgent 會依序執行所有 sub_agents
# 【重點】每個代理的 output_key 會寫入共享的 state，供下一個代理讀取
blog_creation_pipeline = SequentialAgent(
  name="BlogCreationPipeline",
  sub_agents=[
    research_agent,   # 1. 研究主題
    writer_agent,     # 2. 撰寫草稿
    editor_agent,     # 3. 編輯審閱
    formatter_agent,  # 4. 格式化輸出
  ],  # 【重點】按照此順序「嚴格依序」執行！
  description="從研究到發布的完整部落格文章創建流水線",
)

# 【重點】必須命名為 root_agent 才能被 ADK 發現
root_agent = blog_creation_pipeline

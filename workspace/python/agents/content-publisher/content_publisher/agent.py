"""
教學 06：多代理系統 - 內容發布系統

此教學展示了進階的多代理編排，透過在巢狀工作流程中結合
循序代理和並行代理。內容發布系統會執行並行的研究管線（新聞、社群媒體、專家），
然後透過循序精煉（撰寫、編輯、格式化）來創建內容。
"""

from __future__ import annotations

from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.adk.tools import google_search

# ============================================================================
# 並行分支 1：新聞研究管線
# ============================================================================

news_fetcher = Agent(
  name="news_fetcher",
  model="gemini-2.0-flash",
  description="使用 Google 搜尋取得最新新聞文章",
  instruction=(
    "你是新聞研究員。根據使用者的主題，搜尋當前新聞文章和最新發展。\n"
    "\n"
    "使用 google_search 工具找出 3-4 篇當前新聞文章。\n"
    "專注於過去 6 個月內來自可信賴新聞來源的最新內容。\n"
    "\n"
    "輸出項目符號清單，包含：\n"
    "• 來源 + 標題 + 簡短摘要\n"
    "• 盡可能包含發布日期\n"
    "\n"
    "搜尋查詢應為：'[主題] 新聞 最新發展 site:可信賴新聞網站'"
  ),
  tools=[google_search],
  output_key="raw_news",  # 原始新聞資料
)

news_summarizer = Agent(
  name="news_summarizer",
  model="gemini-2.0-flash",
  description="總結關鍵新聞要點",
  instruction=(
    "將新聞文章總結成 2-3 個關鍵重點。\n"
    "\n"
    "**原始新聞：**\n"
    "{raw_news}\n"
    "\n"
    "輸出格式：\n"
    "關鍵重點：\n"
    "1. 第一個重點\n"
    "2. 第二個重點\n"
    "3. 第三個重點"
  ),
  output_key="news_summary",  # 新聞摘要
)

# 新聞研究的循序管線（先取得 → 再總結）
news_pipeline = SequentialAgent(
  name="NewsPipeline",
  sub_agents=[news_fetcher, news_summarizer],
  description="取得並總結新聞",
)

# ============================================================================
# 並行分支 2：社群媒體研究管線
# ============================================================================

social_monitor = Agent(
  name="social_monitor",
  model="gemini-2.0-flash",
  description="使用 Google 搜尋監控社群媒體趨勢",
  instruction=(
    "你是社群媒體分析師。根據使用者的主題，搜尋熱門討論、流行標籤和公眾情緒。\n"
    "\n"
    "使用 google_search 工具找出：\n"
    "• 社群平台上的熱門標籤和話題\n"
    "• 最近的社群媒體討論和病毒式內容\n"
    "• 公眾意見和情緒分析\n"
    "\n"
    "搜尋：'[主題] 社群媒體趨勢 reddit twitter 討論'\n"
    "\n"
    "輸出：\n"
    "• 3-4 個熱門標籤或話題\n"
    "• 熱門討論主題\n"
    "• 整體情緒（正面/負面/混合）及證據"
  ),
  tools=[google_search],
  output_key="raw_social",  # 原始社群資料
)

sentiment_analyzer = Agent(
  name="sentiment_analyzer",
  model="gemini-2.0-flash",
  description="分析社群情緒",
  instruction=(
    "分析社群媒體資料並提取關鍵見解。\n"
    "\n"
    "**社群媒體資料：**\n"
    "{raw_social}\n"
    "\n"
    "輸出格式：\n"
    "社群洞察：\n"
    "• 趨勢：[標籤/話題]\n"
    "• 情緒：[整體氛圍]\n"
    "• 關鍵主題：[主要討論點]"
  ),
  output_key="social_insights",  # 社群洞察
)

# 社群研究的循序管線（先監控 → 再分析）
social_pipeline = SequentialAgent(
  name="SocialPipeline",
  sub_agents=[social_monitor, sentiment_analyzer],
  description="監控並分析社群媒體",
)

# ============================================================================
# 並行分支 3：專家意見管線
# ============================================================================

expert_finder = Agent(
  name="expert_finder",
  model="gemini-2.0-flash",
  description="使用 Google 搜尋尋找專家意見",
  instruction=(
    "你是專家意見研究員。根據使用者的主題，搜尋產業專家、學者或意見領袖的觀點。\n"
    "\n"
    "使用 google_search 工具找出：\n"
    "• 產業專家及其資歷\n"
    "• 學術研究人員及其所屬機構\n"
    "• 意見領袖及其最近的聲明\n"
    "\n"
    "搜尋：'[主題] 專家意見 學術研究 意見領袖'\n"
    "\n"
    "輸出：\n"
    "• 2-3 位專家姓名及其資歷\n"
    "• 他們的關鍵聲明或立場\n"
    "• 來源（他們在哪裡說的）及可用的連結"
  ),
  tools=[google_search],
  output_key="raw_experts",  # 原始專家資料
)

quote_extractor = Agent(
  name="quote_extractor",
  model="gemini-2.0-flash",
  description="提取可引用的見解",
  instruction=(
    "從專家意見中提取最具影響力的引述和見解。\n"
    "\n"
    "**專家意見：**\n"
    "{raw_experts}\n"
    "\n"
    "輸出格式：\n"
    "專家見解：\n"
    '• 引述 1："..." - [專家姓名]，[資歷]\n'
    '• 引述 2："..." - [專家姓名]，[資歷]'
  ),
  output_key="expert_quotes",  # 專家引述
)

# 專家研究的循序管線（先尋找 → 再提取）
expert_pipeline = SequentialAgent(
  name="ExpertPipeline",
  sub_agents=[expert_finder, quote_extractor],
  description="尋找並提取專家意見",
)

# ============================================================================
# 階段 1：並行研究（3 條管線同時執行！）
# ============================================================================

parallel_research = ParallelAgent(
  name="ParallelResearch",
  sub_agents=[
    news_pipeline,    # 循序：取得 → 總結
    social_pipeline,  # 循序：監控 → 分析
    expert_pipeline,  # 循序：尋找 → 提取
  ],
  description="同時執行所有研究管線",
)

# ============================================================================
# 階段 2：內容創作（循序合成）
# ============================================================================

article_writer = Agent(
  name="article_writer",
  model="gemini-2.0-flash",
  description="從所有研究撰寫文章草稿",
  instruction=(
    "你是專業作家。使用以下所有研究資料撰寫一篇引人入勝的文章。\n"
    "\n"
    "**新聞摘要：**\n"
    "{news_summary}\n"
    "\n"
    "**社群洞察：**\n"
    "{social_insights}\n"
    "\n"
    "**專家引述：**\n"
    "{expert_quotes}\n"
    "\n"
    "撰寫一篇 4-5 段的文章，需要：\n"
    "- 以引人注目的開場開始\n"
    "- 自然融入新聞、社群趨勢和專家意見\n"
    "- 有效使用專家引述\n"
    "- 有力的結論\n"
    "\n"
    "只輸出文章內容。"
  ),
  output_key="draft_article",  # 文章草稿
)

article_editor = Agent(
  name="article_editor",
  model="gemini-2.0-flash",
  description="編輯文章以提升清晰度和影響力",
  instruction=(
    "你是編輯。審閱並改進以下文章。\n"
    "\n"
    "**文章草稿：**\n"
    "{draft_article}\n"
    "\n"
    "編輯重點：\n"
    "- 清晰度和流暢性\n"
    "- 影響力和吸引力\n"
    "- 文法和風格\n"
    "\n"
    "輸出改進後的文章。"
  ),
  output_key="edited_article",  # 編輯後文章
)

article_formatter = Agent(
  name="article_formatter",
  model="gemini-2.0-flash",
  description="格式化文章以供發布",
  instruction=(
    "使用適當的 markdown 格式化文章以供發布。\n"
    "\n"
    "**文章：**\n"
    "{edited_article}\n"
    "\n"
    "新增：\n"
    "- 吸引人的標題（# 標題）\n"
    "- 署名（作者：AI 內容團隊）\n"
    "- 適當的章節標題（## 子標題）\n"
    "- 適當的格式（粗體、斜體、引述）\n"
    "- 發布日期佔位符\n"
    "\n"
    "輸出最終格式化的文章。"
  ),
  output_key="published_article",  # 發布的文章
)

# ============================================================================
# 完整的多代理系統
# ============================================================================

content_publishing_system = SequentialAgent(
  name="ContentPublishingSystem",
  sub_agents=[
    parallel_research,    # 階段 1：研究（3 條並行管線！）
    article_writer,       # 階段 2：草稿
    article_editor,       # 階段 3：編輯
    article_formatter,    # 階段 4：格式化
  ],
  description="完整的內容發布系統，具有並行研究和循序創作功能",
)

# 必須命名為 root_agent 才能被 ADK 發現
root_agent = content_publishing_system


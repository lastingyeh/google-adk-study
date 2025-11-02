"""
教學 05：平行處理 - 旅遊規劃系統

本教學示範如何使用 ParallelAgent 進行並發執行，
以及扇出/聚合模式（fan-out/gather pattern）。
旅遊規劃器會平行搜尋航班、飯店和活動，
然後將結果合併成完整的行程表。
"""

from __future__ import annotations

from google.adk.agents import Agent, ParallelAgent, SequentialAgent

# ============================================================================
# 平行搜尋代理（PARALLEL SEARCH AGENTS）
# ============================================================================

# ===== 平行分支 1：航班搜尋器 =====
flight_finder = Agent(
  name="flight_finder",
  model="gemini-2.0-flash",
  description="搜尋可用航班",
  instruction=(
    "你是航班搜尋專家。根據使用者的旅遊需求，"
    "搜尋可用的航班。\n"
    "\n"
    "提供 2-3 個航班選項，包含：\n"
    "- 航空公司名稱\n"
    "- 起飛和抵達時間\n"
    "- 價格範圍\n"
    "- 飛行時間\n"
    "\n"
    "以條列方式呈現。要具體且實際。"
  ),
  output_key="flight_options",  # 儲存到狀態（state）中
)

# ===== 平行分支 2：飯店搜尋器 =====
hotel_finder = Agent(
  name="hotel_finder",
  model="gemini-2.0-flash",
  description="搜尋可用飯店",
  instruction=(
    "你是飯店搜尋專家。根據使用者的旅遊需求，"
    "尋找合適的飯店。\n"
    "\n"
    "提供 2-3 個飯店選項，包含：\n"
    "- 飯店名稱和評等\n"
    "- 位置（區域/地區）\n"
    "- 每晚價格\n"
    "- 主要設施\n"
    "\n"
    "以條列方式呈現。要具體且實際。"
  ),
  output_key="hotel_options",  # 儲存到狀態（state）中
)

# ===== 平行分支 3：活動搜尋器 =====
activity_finder = Agent(
  name="activity_finder",
  model="gemini-2.0-flash",
  description="尋找活動和景點",
  instruction=(
    "你是當地活動專家。根據使用者的旅遊需求，"
    "推薦活動和景點。\n"
    "\n"
    "提供 4-5 個活動建議，包含：\n"
    "- 活動名稱\n"
    "- 描述（一句話）\n"
    "- 預估時間\n"
    "- 預估費用\n"
    "\n"
    "以條列方式呈現。包含付費/免費活動的組合。"
  ),
  output_key="activity_options",  # 儲存到狀態（state）中
)

# ============================================================================
# 扇出（FAN-OUT）：平行資料收集
# ============================================================================

# 建立 ParallelAgent 進行並發搜尋
# 重點：三個子代理會「同時執行」，而非依序執行
parallel_search = ParallelAgent(
  name="ParallelSearch",
  sub_agents=[
    flight_finder,      # 同時執行
    hotel_finder,       # 同時執行
    activity_finder,    # 同時執行
  ],  # 全部「同時」執行！
  description="並發搜尋航班、飯店和活動",
)

# ============================================================================
# 聚合（GATHER）：循序結果合併
# ============================================================================

# ===== 聚合：將結果合併成行程表 =====
# 重點：使用 {output_key} 從 state 中讀取前面代理的輸出
itinerary_builder = Agent(
  name="itinerary_builder",
  model="gemini-2.0-flash",
  description="將所有搜尋結果組合成完整的旅遊行程",
  instruction=(
    "你是旅遊規劃師。將以下搜尋結果組合成"
    "完整、井然有序的行程表。\n"
    "\n"
    "**可用航班：**\n"
    "{flight_options}\n"  # 從 state 讀取！
    "\n"
    "**可用飯店：**\n"
    "{hotel_options}\n"  # 從 state 讀取！
    "\n"
    "**推薦活動：**\n"
    "{activity_options}\n"  # 從 state 讀取！
    "\n"
    "建立格式化的行程表：\n"
    "1. 從各類別（航班、飯店）推薦「最佳」選項\n"
    "2. 將活動整理成逐日計劃\n"
    "3. 包含預估總費用\n"
    "4. 加入實用旅遊建議\n"
    "\n"
    "使用清楚的段落和 markdown 格式化。"
  ),
  output_key="final_itinerary",
)

# ============================================================================
# 完整扇出/聚合流程（FAN-OUT/GATHER PIPELINE）
# ============================================================================

# 重點：結合平行搜尋（快速）和循序合併（綜合）
# Step 1: 平行收集資料（3個代理同時執行）→ 省時！
# Step 2: 循序合併結果（1個代理整合所有資訊）
travel_planning_system = SequentialAgent(
  name="TravelPlanningSystem",
  sub_agents=[
    parallel_search,    # 步驟 1：平行收集資料（快速！）
    itinerary_builder,  # 步驟 2：合併結果（綜合）
  ],
  description="具備平行搜尋和行程建立功能的完整旅遊規劃系統",
)

# 必須命名為 root_agent 以供 ADK 發現
root_agent = travel_planning_system


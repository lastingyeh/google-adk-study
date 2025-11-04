from __future__ import annotations

from google.adk.agents import Agent, LoopAgent, SequentialAgent
from google.adk.tools.tool_context import ToolContext


# ===== 退出工具：用於終止迴圈 =====
def exit_loop(tool_context: ToolContext):
    """
    退出迴圈工具 (Exit Loop Tool)

    功能說明：
    - 發出論文精煉完成的信號
    - 當評論者 (Critic) 批准論文時，由精煉者 (Refiner) 呼叫

    工作流程：
    1. 輸出退出訊息，標示是哪個代理呼叫此工具
    2. 設定 end_of_agent 標記為 True，通知系統停止迴圈
    3. 回傳有效的內容部分，確保後端產生有效的 LlmResponse
    """
    print(f"  [退出迴圈] 由 {tool_context.agent_name} 呼叫 - 論文已批准！")
    tool_context.actions.end_of_agent = True  # 發送停止迴圈的信號
    # 回傳最小有效內容部分，確保後端始終產生有效的 LlmResponse
    return {
        "text": "迴圈成功退出。代理已判定任務完成。"
    }


# =====================================================
# 階段 1：初始寫作者 (在迴圈前執行一次)
# =====================================================
initial_writer = Agent(
    name="InitialWriter",
    model="gemini-2.0-flash",
    description="撰寫論文的第一版草稿",
    instruction=(
        "你是一位富有創意的作家。請根據使用者要求的主題撰寫論文初稿。\n"
        "\n"
        "撰寫 3-4 個段落：\n"
        "- 開頭段落包含論點 (thesis)\n"
        "- 1-2 個主體段落提供支持論點\n"
        "- 結論段落\n"
        "\n"
        "不用擔心是否完美 - 這只是第一版草稿。\n"
        "\n"
        "只輸出論文文本，不要包含任何元評論。"
    ),
    output_key="current_essay",  # 儲存到狀態中
)

# =====================================================
# 階段 2：精煉迴圈 (重複執行)
# =====================================================

# ===== 迴圈代理 1：評論者 (Critic) =====
critic = Agent(
    name="Critic",
    model="gemini-2.0-flash",
    description="評估論文品質並提供回饋",
    instruction=(
        "你是一位經驗豐富的論文評論者與教師。請審查以下論文並評估其品質。\n"
        "\n"
        "**待審查的論文：**\n"
        "{current_essay}\n"
        "\n"
        "**評估標準：**\n"
        "- 清晰的論點與組織結構\n"
        "- 強有力的支持論據\n"
        "- 良好的文法與風格\n"
        "- 引人入勝且連貫的寫作\n"
        "\n"
        "**你的任務：**\n"
        "如果論文符合所有標準 (不需要完美，只要紮實即可)：\n"
        "  輸出這個確切的短語：'APPROVED - Essay is complete.'\n"
        "\n"
        "否則，如果論文需要改進：\n"
        "  提供 2-3 個具體、可行的改進建議。要有建設性且清晰。\n"
        "  範例：'論點模糊 - 對 X 要更具體。'\n"
        "\n"
        "只輸出批准短語或具體回饋。"
    ),
    output_key="critique",  # 將回饋儲存到狀態
)

# ===== 迴圈代理 2：精煉者 (Refiner) =====
refiner = Agent(
    name="Refiner",
    model="gemini-2.0-flash",
    tools=[exit_loop],  # 提供退出工具！
    description="根據評論改進論文或發出完成信號",
    instruction=(
        "你是一位論文編輯。閱讀以下評論並採取適當行動。\n"
        "\n"
        "**當前論文：**\n"
        "{current_essay}\n"
        "\n"
        "**評論：**\n"
        "{critique}\n"
        "\n"
        "**你的任務：**\n"
        "如果評論說 'APPROVED - Essay is complete.'：\n"
        "  立即呼叫 'exit_loop' 函數。不要輸出任何文本。\n"
        "  這意味著你的回應應該只有函數呼叫，沒有其他內容。\n"
        "\n"
        "否則 (評論包含改進建議)：\n"
        "  應用建議的改進來創建更好版本的論文。\n"
        "  只輸出改進後的論文文本，不要有解釋或元評論。\n"
        "  改進論文時不要呼叫任何函數。\n"
        "\n"
        "重要：你必須呼叫 exit_loop 或輸出改進的論文文本。\n"
        "絕不要在同一個回應中同時執行這兩個動作。"
    ),
    output_key="current_essay",  # 用改進的版本覆寫論文！
)

# ===== 創建精煉迴圈 =====
refinement_loop = LoopAgent(
    name="RefinementLoop",
    sub_agents=[critic, refiner],  # 步驟 1：評估 | 步驟 2：改進或退出
    max_iterations=5,  # 安全限制 - 最多迭代 5 次
)

# =====================================================
# 完整系統：初始草稿 + 精煉迴圈
# =====================================================
essay_refinement_system = SequentialAgent(
    name="EssayRefinementSystem",
    sub_agents=[
        initial_writer,  # 階段 1：撰寫第一版草稿（執行一次）
        refinement_loop,  # 階段 2：迭代精煉（迴圈執行）
    ],
    description="完整的論文撰寫與精煉系統",
)

# 必須命名為 root_agent 以供 ADK 使用
root_agent = essay_refinement_system


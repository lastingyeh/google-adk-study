"""個人化學習導師（Personal Learning Tutor） - 展示「狀態（State）與記憶（Memory）管理」

本代理（Agent）示範以下機制：
1. `user:` 前綴：用於永久（跨工作階段 / session）儲存使用者偏好（語言、難度）。
2. 工作階段（Session）狀態：記錄當前正在學習的主題，不加前綴，僅在本次互動有效。
3. `temp:` 前綴：用於一次呼叫（invocation-scoped）的暫存計算資料（例如測驗分數中間值），呼叫結束後可丟棄。
4. 記憶服務（Memory Service）：可搜尋過往學習紀錄以提供個人化教學（此範例以模擬方式呈現）。

核心觀念：透過不同前綴與層級，將「長期偏好」、「工作階段上下文」與「暫時計算」區隔，使教學體驗具備可持續成長與即時回饋能力。
"""

from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any

# ============================================================================
# TOOLS: State Management & Memory Operations
# ============================================================================


def set_user_preferences(
    language: str, difficulty_level: str, tool_context: ToolContext
) -> Dict[str, Any]:
    """設定使用者學習偏好（永久儲存）。

    參數：
        language: 使用者偏好語言（例如 en, es, fr 等）
        difficulty_level: 難度層級（beginner / intermediate / advanced）

    實作說明：
    - 使用 `user:` 前綴代表此資料需跨工作階段保留。
    - 儲存語言與難度等個人化偏好，後續教學可依此調整。
    """
    # 使用 user: 前綴 -> 跨 session 永久狀態（Persistent State）
    tool_context.state["user:language"] = language
    tool_context.state["user:difficulty_level"] = difficulty_level

    return {
        "status": "success",
        "message": f"偏好已儲存: 語言={language}, 難度={difficulty_level}",
    }


def record_topic_completion(
    topic: str, quiz_score: int, tool_context: ToolContext
) -> Dict[str, Any]:
    """紀錄使用者完成某學習主題（永久儲存）。

    參數：
        topic: 主題名稱（例如 "Python Basics", "Data Structures"）
        quiz_score: 測驗分數（滿分 100）

    流程：
    1. 讀取既有的已完成主題與分數（若無則建立初始結構）。
    2. 若主題尚未出現在清單中則加入。
    3. 更新分數映射（dict）。
    4. 回寫至 `user:` 前綴的永久狀態。
    """
    topics = tool_context.state.get("user:topics_covered", [])  # 已完成主題列表
    scores = tool_context.state.get("user:quiz_scores", {})  # 主題對應分數

    if topic not in topics:
        topics.append(topic)
    scores[topic] = quiz_score

    tool_context.state["user:topics_covered"] = topics
    tool_context.state["user:quiz_scores"] = scores

    return {
        "status": "success",
        "topics_count": len(topics),
        "message": f"主題已紀錄: {topic} 分數 {quiz_score}/100",
    }


def get_user_progress(tool_context: ToolContext) -> Dict[str, Any]:
    """取得使用者學習進度摘要（跨所有工作階段）。

    輸出：
        - 語言偏好、難度層級
        - 已完成主題數量與列表
        - 平均測驗分數（若無測驗則為 0）
        - 全部分數映射
    """
    language = tool_context.state.get("user:language", "en")
    difficulty = tool_context.state.get("user:difficulty_level", "beginner")
    topics = tool_context.state.get("user:topics_covered", [])
    scores = tool_context.state.get("user:quiz_scores", {})

    avg_score = sum(scores.values()) / len(scores) if scores else 0

    return {
        "status": "success",
        "language": language,
        "difficulty_level": difficulty,
        "topics_completed": len(topics),
        "topics": topics,
        "average_quiz_score": round(avg_score, 1),
        "all_scores": scores,
    }


def start_learning_session(topic: str, tool_context: ToolContext) -> Dict[str, Any]:
    """啟動新的主題學習工作階段（Session）。

    說明：
        - 不使用前綴（裸 key）代表此為「工作階段層級」狀態，只在目前互動生命週期中有效。
        - 設定當前主題與開始時間（此處簡化為字串 "now"）。
        - 根據使用者永久偏好中儲存的難度調整教學內容。
    """
    tool_context.state["current_topic"] = topic  # Session 狀態
    tool_context.state["session_start_time"] = "now"  # 可改為時間戳

    difficulty = tool_context.state.get("user:difficulty_level", "beginner")

    return {
        "status": "success",
        "topic": topic,
        "difficulty_level": difficulty,
        "message": f"已啟動學習階段: {topic} 難度 {difficulty}",
    }


def calculate_quiz_grade(
    correct_answers: int, total_questions: int, tool_context: ToolContext
) -> Dict[str, Any]:
    """計算測驗成績，使用暫時（temp）狀態儲存中間結果。

    參數：
        correct_answers: 答對題數
        total_questions: 題目總數

    說明：
        - 使用 `temp:` 前綴將中間值（原始分數、百分比）暫存於當次呼叫作用域 -> 呼叫完可被回收。
        - 將百分比分級為 A/B/C/D/F。
    邊界：
        - 若 total_questions 為 0（理論上不應發生），可加防護；此範例假設輸入有效。
    """
    percentage = (correct_answers / total_questions) * 100
    tool_context.state["temp:raw_score"] = correct_answers
    tool_context.state["temp:quiz_percentage"] = percentage

    if percentage >= 90:
        grade = "A"
    elif percentage >= 80:
        grade = "B"
    elif percentage >= 70:
        grade = "C"
    elif percentage >= 60:
        grade = "D"
    else:
        grade = "F"

    return {
        "status": "success",
        "score": f"{correct_answers}/{total_questions}",
        "percentage": round(percentage, 1),
        "grade": grade,
        "message": f"測驗成績: {grade} ({percentage:.1f}%)",
    }


def search_past_lessons(query: str, tool_context: ToolContext) -> Dict[str, Any]:
    """搜尋過往學習紀錄（記憶服務 Memory Service 範例）。

    說明：
        - 真實情境下會呼叫 `MemoryService.search_memory()` 以語意搜尋。
        - 此處以模擬方式：在已完成主題中尋找包含 query 的字串。

    參數：
        query: 使用者查詢關鍵字
    """
    topics = tool_context.state.get("user:topics_covered", [])
    relevant = [t for t in topics if query.lower() in t.lower()]

    if relevant:
        return {
            "status": "success",
            "found": True,
            "relevant_topics": relevant,
            "message": f'找到 {len(relevant)} 個與 "{query}" 相關的過往課程',
        }
    return {
        "status": "success",
        "found": False,
        "message": f'未找到與 "{query}" 相關的過往課程',
    }


# ============================================================================
# AGENT DEFINITION
# ============================================================================

root_agent = Agent(
    name="personal_tutor",
    model="gemini-2.0-flash",
    description="""個人化學習導師：追蹤使用者進度、偏好與學習歷史；透過狀態管理與記憶整合提供客製化教學。""",
    instruction="""
        你是一位具備使用者進度記憶的個人化學習導師。

        CAPABILITIES（能力）:
        - 設定並記住使用者偏好（語言、難度等）
        - 追蹤已完成主題與測驗分數（跨多次互動）
        - 啟動新的主題學習工作階段
        - 計算並回饋測驗成績（暫時計算 + 永久儲存結果）
        - 搜尋過往學習紀錄以提供上下文與延伸建議
        - 依使用者歷史與難度調整教學語氣與內容深度

        STATE MANAGEMENT（狀態管理）:
        - `user:` 前綴：永久偏好與學習成果
        - Session 狀態：當前主題與互動上下文
        - `temp:` 前綴：單次呼叫暫存計算（結束後丟棄）

        TEACHING APPROACH（教學方法）:
        1. 讀取使用者難度等級並調整說明層次
        2. 適時引用過往相關主題加強連結
        3. 追蹤進度並給予正向回饋
        4. 根據歷史提出下一步建議

        WORKFLOW（工作流程）:
        1. 若為新使用者：詢問語言與難度偏好
        2. 使用者提出學習需求：
        - 呼叫 `start_learning_session` 啟動工作階段
        - 教授該主題（根據難度調整）
        - 結尾提供測驗題目
        3. 呼叫 `calculate_quiz_grade` 取得分數評等
        4. 呼叫 `record_topic_completion` 紀錄完成與分數
        5. 使用者詢問歷史：可呼叫 `search_past_lessons`

        始終保持鼓勵與耐心，並依使用者學習節奏調整互動！
    """,
    tools=[
        set_user_preferences,
        record_topic_completion,
        get_user_progress,
        start_learning_session,
        calculate_quiz_grade,
        search_past_lessons,
    ],
    output_key="last_tutor_response",  # 最終回覆儲存在工作階段狀態中
)

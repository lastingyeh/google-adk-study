"""
內容審查助理（Content Moderation Assistant）- 示範回呼（Callbacks）與防護措施（Guardrails）

本代理（agent）使用各類回呼達成以下目的：
1. 防護（Guardrails）：阻擋不當內容（`before_model_callback`）
2. 參數驗證（Validation）：檢查工具參數（`before_tool_callback`）
3. 記錄（Logging）：追蹤所有操作（多個回呼）
4. 指令增補（Modification）：附加安全說明（`before_model_callback`）
5. 個資過濾（Filtering / PII Removal）：回應中移除個人識別資訊（`after_model_callback`）
6. 指標統計（Metrics Tracking）：追蹤使用統計（狀態管理 state management）

設計目標：提供可延伸、易審核、具生產環境風格的內容審查流程。首次出現之英文專有名詞於括號中保留，以利技術精準性。
"""

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from typing import Dict, Any, Optional
import re
import logging

# 設定 logging（紀錄系統），以 INFO 為預設層級便於觀察行為
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# 封鎖詞清單配置（BLOCKLIST CONFIGURATION）
# ============================================================================

# 簡化封鎖詞清單（Blocklist）供示範；實務上請替換為更完整詞彙
# 🔑 重點：這是第一道防線，阻擋明顯不當內容
BLOCKED_WORDS = [
    "profanity1",      # 髒話1（實際使用時替換為真實詞彙）
    "profanity2",      # 髒話2
    "hate-speech",     # 仇恨言論
    "offensive-term",  # 冒犯性詞彙
    "inappropriate-word",  # 不當用語
]

# 個人識別資訊（PII, Personally Identifiable Information）之正規表示式樣式，用於後處理過濾
# 🔑 重點：保護使用者隱私，自動移除敏感個資
PII_PATTERNS = {
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # 電子郵件
    "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # 電話號碼（美式格式）
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",  # 社會安全號碼（SSN）
    "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",  # 信用卡號
}

# ============================================================================
# 回呼函式（CALLBACK FUNCTIONS）
# ============================================================================


def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    於代理開始處理使用者請求之前呼叫。

    🔑 重點：這是最早執行的回呼，用於全域檢查與初始化

    使用情境：
      - 檢查是否進入維護模式（maintenance mode）
      - 增加使用者請求次數統計（request_count）
      - 可擴充為速率限制、使用者驗證等

    回傳（Returns）：
      - None：允許後續處理
      - Content：直接回覆使用者並跳過後續代理執行（短路機制）
    """
    logger.info(f"[代理啟動 AGENT START] 會話編號 Session: {callback_context.invocation_id}")

    # 🔑 重點：維護模式檢查 — 若系統維護中則立即返回，不執行任何代理邏輯
    if callback_context.state.get("app:maintenance_mode", False):
        logger.warning("[代理封鎖 AGENT BLOCKED] 維護模式啟用中 Maintenance mode active")
        return types.Content(
            parts=[
                types.Part(
                    text="系統目前正在維護中，請稍後再試。System is currently under maintenance. Please try again later."
                )
            ],
            role="model",
        )

    # 🔑 重點：使用者請求次數遞增（以 user: 前綴標示使用者層級的狀態）
    count = callback_context.state.get("user:request_count", 0)
    callback_context.state["user:request_count"] = count + 1

    return None  # 允許代理繼續處理 Allow agent to proceed


def after_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    於代理完成主要處理後呼叫。

    🔑 重點：最後執行的回呼，用於收尾與最終修改

    使用情境：
        - 可以在此追加後置標記（例如：完成旗標、版權宣告、統一尾註）
        - 可進行最終回應格式驗證
        - 記錄完成狀態供後續分析

    回傳：
        - None：沿用原始結果
        - Content：以自訂內容取代最終回應
    """
    logger.info(f"[代理完成 AGENT COMPLETE] 會話編號 Session: {callback_context.invocation_id}")

    # 追蹤成功完成次數 Track successful completions
    callback_context.state["temp:agent_completed"] = True

    # 可在此加入標準聲明（範例略）
    # 🔑 重點：可用於添加免責聲明或版權資訊
    # return types.Content(
    #     parts=[types.Part(text="\n\n[此為 AI 生成內容 This is AI-generated content]")]
    # )

    return None  # 使用原始輸出 Use original output


def before_model_callback(
    callback_context: CallbackContext, llm_request: types._GenerateContentParameters
) -> Optional[types.GenerateContentResponse]:
    """
    在即將送出 LLM（大型語言模型）請求前呼叫。

    🔑 重點：這是內容安全的核心檢查點，可攔截不當請求並修改提示詞

    使用情境：
      1. 防護（Guardrails）：阻擋含封鎖詞的請求
      2. 指令增補（Modification）：附加額外安全規範（system instruction）
      3. 快取（Caching）：可在此直接回傳快取結果（目前示範略過）
      4. 使用追蹤（Logging / Metrics）：記錄 LLM 呼叫次數

    回傳：
      - None：允許後續呼叫 LLM（可能已被修改）
      - GenerateContentResponse：略過真正 LLM 呼叫，直接使用此回應（例如封鎖時）
    """
    # 提取使用者輸入文字 Extract user input
    user_text = ""
    for content in llm_request.contents:
        for part in content.parts:
            if part.text:
                user_text += part.text

    logger.info(f"[LLM 請求 LLM REQUEST] 長度 Length: {len(user_text)} 字元 chars")

    # 🔑 重點：防護步驟 — 檢查是否包含封鎖詞（Blocklist）
    # 若命中則回傳封鎖訊息並加總 blocked_requests，完全跳過 LLM 呼叫
    for word in BLOCKED_WORDS:
        if word.lower() in user_text.lower():
            logger.warning(f"[LLM 封鎖 LLM BLOCKED] 發現封鎖詞 Found blocked word: {word}")

            # 追蹤被封鎖的請求次數 Track blocked requests
            blocked_count = callback_context.state.get("user:blocked_requests", 0)
            callback_context.state["user:blocked_requests"] = blocked_count + 1

            # 回傳錯誤回應（跳過 LLM 呼叫）Return error response (skip LLM call)
            return types.GenerateContentResponse(
                candidates=[
                    types.Candidate(
                        content=types.Content(
                            parts=[
                                types.Part(
                                    text="無法處理此請求，因為包含不當內容。請以尊重的方式重新表達。I cannot process this request as it contains inappropriate content. Please rephrase respectfully."
                                )
                            ],
                            role="model",
                        )
                    )
                ]
            )

    # 🔑 重點：指令增補 — 於 system_instruction 末端添加安全提示語
    # 這會影響模型的所有回應，避免生成有害或偏見內容
    safety_instruction = "\n\n重要提示：不要生成有害、偏見或不當內容。若請求不清楚，請要求澄清。IMPORTANT: Do not generate harmful, biased, or inappropriate content. If the request is unclear, ask for clarification."

    # 修改系統指令 Modify system instruction
    if llm_request.config and llm_request.config.system_instruction:
        llm_request.config.system_instruction += safety_instruction

    # 記錄 LLM 呼叫次數（user 範疇）
    llm_count = callback_context.state.get("user:llm_calls", 0)
    callback_context.state["user:llm_calls"] = llm_count + 1

    return None  # 允許進行 LLM 呼叫（含修改）Allow LLM call with modifications


def after_model_callback(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """
    在取得 LLM 回應後呼叫。

    🔑 重點：這是輸出過濾的關鍵點，確保回應內容符合隱私與安全標準

    使用情境：
      1. 過濾（Filtering）：移除個資（PII）或敏感資訊
      2. 格式化（Formatting）：可統一輸出格式（此示範集中於 PII 過濾）
      3. 資訊記錄（Logging）：記錄回應長度或品質評估指標
      4. 內容審查：可加入二次安全檢查

    回傳：
      - None：使用原始回應
      - LlmResponse：以修改後內容取代（例如已進行 PII 過濾）
    """
    # 提取回應文字 Extract response text
    response_text = ""
    if llm_response.content and llm_response.content.parts:
        for part in llm_response.content.parts:
            if part.text:
                response_text += part.text

    logger.info(f"[LLM 回應 LLM RESPONSE] 長度 Length: {len(response_text)} 字元 chars")

    # 🔑 重點：過濾步驟 — 對每一種 PII 模式進行搜尋與替換，並記錄命中次數
    # 這保護了可能意外出現在回應中的個人資訊
    filtered_text = response_text
    for pii_type, pattern in PII_PATTERNS.items():
        matches = re.findall(pattern, filtered_text)
        if matches:
            logger.warning(f"[已過濾 FILTERED] 發現 Found {len(matches)} 個 {pii_type} 實例 instances")
            filtered_text = re.sub(
                pattern, f"[{pii_type.upper()}_已隱蔽_REDACTED]", filtered_text
            )

    # 如果有過濾任何內容，回傳修改後的回應 If we filtered anything, return modified response
    if filtered_text != response_text:
        # 建立修改後的內容 Create modified content
        modified_content = types.Content(
            parts=[types.Part(text=filtered_text)],
            role=llm_response.content.role if llm_response.content else "model",
        )

        # 回傳修改後的 LlmResponse Return modified LlmResponse
        return llm_response.model_copy(update={"content": modified_content})

    return None  # 使用原始回應 Use original response


def before_tool_callback(
    callback_context: CallbackContext, tool_name: str, args: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    在工具執行前呼叫。

    🔑 重點：工具層級的安全閘門，確保參數合法且使用量在限制內

    使用情境：
      1. 參數驗證（Validation）：檢查輸入是否在允許範圍
      2. 授權檢查（Authorization）：可擴充以檢查使用者權限
      3. 速率限制（Rate Limiting）：控制工具使用次數
      4. 使用記錄（Logging / Metrics）：統計工具呼叫頻率

    回傳：
      - None：允許工具執行
      - dict：略過工具執行，直接回傳此結果（例如參數錯誤）
    """
    logger.info(f"[工具呼叫 TOOL CALL] {tool_name} 參數 with args: {args}")

    # 🔑 重點：參數驗證 — 對 generate_text 工具的 word_count 進行範圍檢查
    # 防止惡意或錯誤的大量文字生成請求
    if tool_name == "generate_text":
        word_count = args.get("word_count", 0)
        if word_count <= 0 or word_count > 5000:
            logger.warning(f"[工具封鎖 TOOL BLOCKED] 無效的字數 Invalid word_count: {word_count}")
            return {
                "status": "error",
                "message": f"無效的字數 Invalid word_count: {word_count}. 必須介於 1 到 5000 之間 Must be between 1 and 5000.",
            }

    # 🔑 重點：速率限制 — 檢查某工具呼叫次數是否已達上限（示範用 100 次）
    # 防止濫用與資源耗盡
    tool_count = callback_context.state.get(f"user:tool_{tool_name}_count", 0)
    if tool_count >= 100:  # 範例限制 Example limit
        logger.warning(f"[工具封鎖 TOOL BLOCKED] {tool_name} 超出速率限制 Rate limit exceeded")
        return {
            "status": "error",
            "message": f"{tool_name} 超出速率限制。請稍後再試。Rate limit exceeded for {tool_name}. Please try again later.",
        }

    # 紀錄工具使用次數 + 最近使用工具名稱（temp 範疇為暫時性）
    callback_context.state[f"user:tool_{tool_name}_count"] = tool_count + 1
    callback_context.state["temp:last_tool"] = tool_name

    return None  # 允許工具執行 Allow tool execution


def after_tool_callback(
    callback_context: CallbackContext, tool_name: str, tool_response: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    在工具執行結束後呼叫。

    🔑 重點：工具結果的後處理與記錄點

    使用情境：
      1. 結果記錄（Logging）：保存工具回傳概要
      2. 統一格式（Transformation）：可統一回傳結構（此示範未強制）
      3. 快取（Caching）：可在此保存工具結果供後續使用
      4. 錯誤處理：可包裝或美化錯誤訊息

    回傳：
      - None：使用原始工具結果
      - dict：以修改後結果取代
    """
    logger.info(f"[工具結果 TOOL RESULT] {tool_name}: {tool_response.get('status', 'unknown')}")

    # 儲存最後工具結果供除錯使用 Store last tool result for debugging
    callback_context.state["temp:last_tool_result"] = str(tool_response)

    # 可在此標準化所有工具回應 Could standardize all tool responses here
    # 🔑 重點：確保所有工具回應都有一致的結構
    # if 'status' not in tool_response:
    #     tool_response['status'] = 'success'

    return None  # 使用原始結果 Use original result


# ============================================================================
# 工具定義（TOOLS）
# ============================================================================


def generate_text(
    topic: str, word_count: int, tool_context: ToolContext
) -> Dict[str, Any]:
    """
    依指定主題與字數生成文字（示範版未串接真正模型）。

    🔑 重點：實際應用中應呼叫文字生成 API 或模型

    參數（Args）：
      - topic：主題
      - word_count：期望字數（1-5000）
    """
    # 實際上工具應在此生成文字 Tool would normally generate text here
    # 示範版僅回傳中繼資料 For demo, just return metadata

    return {
        "status": "success",
        "topic": topic,
        "word_count": word_count,
        "message": f'已生成關於「{topic}」的 {word_count} 字文章 Generated {word_count}-word article on "{topic}"',
    }


def check_grammar(text: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    檢查語法並提供可能錯誤數（簡化示範：每 10 個字視為 1 個潛在問題）。

    🔑 重點：實際應用應整合語法檢查 API（如 LanguageTool、Grammarly）

    參數：
      - text：要檢查的文字
    """
    # 模擬語法檢查 Simulate grammar checking
    issues_found = len(text.split()) // 10  # 假設：每 10 字 1 個問題 Fake: 1 issue per 10 words

    return {
        "status": "success",
        "issues_found": issues_found,
        "message": f"發現 {issues_found} 個潛在語法問題 Found {issues_found} potential grammar issues",
    }


def get_usage_stats(tool_context: ToolContext) -> Dict[str, Any]:
    """
    從狀態（state）中取得使用者統計資料，示範回呼如何累積指標。

    🔑 重點：這展示了狀態管理在追蹤使用模式上的應用，可擴充以加入更多維度。
    """
    return {
        "status": "success",
        "request_count": tool_context.state.get("user:request_count", 0),  # 總請求次數
        "llm_calls": tool_context.state.get("user:llm_calls", 0),  # LLM 呼叫次數
        "blocked_requests": tool_context.state.get("user:blocked_requests", 0),  # 被封鎖請求數
        "tool_generate_text_count": tool_context.state.get(
            "user:tool_generate_text_count", 0
        ),  # 文字生成工具使用次數
        "tool_check_grammar_count": tool_context.state.get(
            "user:tool_check_grammar_count", 0
        ),  # 語法檢查工具使用次數
    }


# ============================================================================
# 代理定義（AGENT DEFINITION）
# ============================================================================

# 🔑 重點：這是整個系統的核心配置，將所有回呼與工具組合成完整的代理
root_agent = Agent(
    name="content_moderator",  # 代理名稱
    model="gemini-2.0-flash",  # 使用的模型
    description="""
    具備安全防護、驗證與監控功能的內容審查助理。
    展示適用於生產環境的回呼模式。
    """,
    instruction="""
    你是一個協助使用者創作與精煉內容的寫作助理。

    功能（CAPABILITIES）：
    - 依任何主題與指定字數生成文字
    - 檢查語法並提供修正建議
    - 提供使用統計資料

    安全性（SAFETY）：
    - 你在嚴格的內容審查政策下運作
    - 不當請求將被自動封鎖
    - 所有互動都會被記錄以確保品質

    工作流程（WORKFLOW）：
    1. 對於生成請求，使用 generate_text 並指定主題與字數
    2. 對於語法檢查，使用 check_grammar 並提供文字
    3. 對於統計資料，使用 get_usage_stats

    始終保持有幫助、專業且尊重的態度。
    """,
    tools=[generate_text, check_grammar, get_usage_stats],  # 註冊的工具
    # ============================================================================
    # 回呼配置（CALLBACKS CONFIGURATION）
    # 🔑 重點：這些回呼形成了完整的安全與監控鏈
    # ============================================================================
    before_agent_callback=before_agent_callback,    # 代理啟動前（維護模式檢查）
    after_agent_callback=after_agent_callback,      # 代理完成後（收尾處理）
    before_model_callback=before_model_callback,    # LLM 呼叫前（內容防護與指令增補）
    after_model_callback=after_model_callback,      # LLM 回應後（PII 過濾）
    before_tool_callback=before_tool_callback,      # 工具執行前（參數驗證與速率限制）
    after_tool_callback=after_tool_callback,        # 工具執行後（結果記錄）
    output_key="last_response",  # 輸出金鑰
)

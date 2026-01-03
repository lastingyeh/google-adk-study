import logging
import time

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest
from typing import Any, Dict, Optional, Tuple
from google.adk.tools import BaseTool
from google.adk.agents.invocation_context import InvocationContext
from google.adk.sessions.state import State
from google.adk.tools.tool_context import ToolContext
from jsonschema import ValidationError
from customer_service.entities.customer import Customer

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 速率限制設定
RATE_LIMIT_SECS = 60 # 限制週期（秒）
RPM_QUOTA = 10 # 每分鐘請求數限額

def rate_limit_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> None:
    """實作查詢速率限制的回呼函數。

    參數:
      callback_context: 代表活動回呼上下文的 CallbackContext 物件。
      llm_request: 代表活動 LLM 請求的 LlmRequest 物件。
    """
    # 確保請求內容中的文字部分不為空，若為空則補一個空格
    for content in llm_request.contents:
        for part in content.parts:
            if part.text=="":
                part.text=" "

    now = time.time()
    # 初始化計時器
    if "timer_start" not in callback_context.state:
        callback_context.state["timer_start"] = now
        callback_context.state["request_count"] = 1
        logger.debug(
            "rate_limit_callback [時間戳記: %i, 請求計數: 1, 已過秒數: 0]",
            now,
        )
        return

    # 累加請求次數並計算經過時間
    request_count = callback_context.state["request_count"] + 1
    elapsed_secs = now - callback_context.state["timer_start"]
    logger.debug(
        "rate_limit_callback [時間戳記: %i, 請求計數: %i, 已過秒數: %i]",
        now,
        request_count,
        elapsed_secs,
    )

    # 檢查是否超過 RPM 限額
    if request_count > RPM_QUOTA:
        delay = RATE_LIMIT_SECS - elapsed_secs + 1
        if delay > 0:
            logger.debug("正在休眠 %i 秒", delay)
            time.sleep(delay)
        # 重設計時器
        callback_context.state["timer_start"] = now
        callback_context.state["request_count"] = 1
    else:
        callback_context.state["request_count"] = request_count

    return

def validate_customer_id(customer_id: str, session_state: State) -> Tuple[bool, str]:
    """
    根據會話狀態中的客戶檔案驗證客戶 ID。

    參數:
        customer_id (str): 要驗證的客戶 ID。
        session_state (State): 包含客戶檔案的會話狀態。

    回傳:
        包含布林值 (True/False) 和字串的元組。
        當為 False 時，字串包含錯誤訊息，傳遞給模型以決定採取的補救措施。
    """
    if 'customer_profile' not in session_state:
        return False, "未選擇客戶檔案。請選擇一個檔案。"

    try:
        # 從狀態讀取檔案，該檔案在會話開始時確定性地設定。
        c = Customer.model_validate_json(session_state['customer_profile'])
        if customer_id == c.customer_id:
            return True, None
        else:
            return False, "您不能對客戶 ID " + customer_id + " 使用工具，僅限用於 " + c.customer_id + "。"
    except ValidationError as e:
        return False, "客戶檔案無法解析。請重新載入客戶數據。"

def lowercase_value(value):
    """將字典或清單中的字串值轉換為小寫。"""
    if isinstance(value, dict):
        for k, v in value.items():
            value[k] = lowercase_value(v)
        return value
    elif isinstance(value, str):
        return value.lower()
    elif isinstance(value, (list, set, tuple)):
        tp = type(value)
        return tp(lowercase_value(i) for i in value)
    else:
        return value


# 回呼方法
def before_tool(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
):
    """工具執行前的處理。"""
    # 確保代理發送給工具的所有值都是小寫
    lowercase_value(args)

    # 驗證客戶 ID。我們不希望僅依賴模型選擇正確的客戶 ID。
    if 'customer_id' in args:
        valid, err = validate_customer_id(args['customer_id'], tool_context.state)
        if not valid:
            return err

    # 根據被呼叫的工具執行特定的業務邏輯。
    if tool.name == "sync_ask_for_approval":
        amount = args.get("value", None)
        # 業務規則範例：若折扣金額小於等於 10，則自動批准
        if amount and amount <= 10:
            return {
                "status": "approved",
                "message": "您可以直接批准此折扣；不需要經理。"
            }

    # 購物車修改的預先處理
    if tool.name == "modify_cart":
        if (
            args.get("items_added") is True
            and args.get("items_removed") is True
        ):
            return {"result": "我已添加並刪除了請求的商品。"}
    return None

def after_tool(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict
) -> Optional[Dict]:
    """工具執行後的處理。"""
    # 批准後，我們在回呼中執行確定性操作以應用購物車折扣。
    if tool.name == "sync_ask_for_approval":
        if tool_response and tool_response.get('status') == "approved":
            logger.debug("正在將折扣應用於購物車")
            # 實際執行購物車更改邏輯

    if tool.name == "approve_discount":
        if tool_response and tool_response.get('status') == "ok":
            logger.debug("正在將折扣應用於購物車")
            # 實際執行購物車更改邏輯

    return None

def before_agent(callback_context: InvocationContext):
    """代理程式啟動前的處理。確保客戶檔案已載入。"""
    # 在生產環境中，這通常在建立代理會話時設定。
    if "customer_profile" not in callback_context.state:
        callback_context.state["customer_profile"] = Customer.get_customer(
            "123"
        ).to_json()

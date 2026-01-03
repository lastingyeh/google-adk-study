import logging
import warnings
from google.adk import Agent
from .config import Config
from .prompts import GLOBAL_INSTRUCTION, INSTRUCTION
from .shared_libraries.callbacks import (
    rate_limit_callback,
    before_agent,
    before_tool,
    after_tool
)
from .tools.tools import (
    send_call_companion_link,
    approve_discount,
    sync_ask_for_approval,
    update_salesforce_crm,
    access_cart_information,
    modify_cart,
    get_product_recommendations,
    check_product_availability,
    schedule_planting_service,
    get_available_planting_times,
    send_care_instructions,
    generate_qr_code,
)

# 忽略 Pydantic 相關的用戶警告
warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")

# 初始化配置
configs = Config()

# 設定日誌記錄器（Logger）
logger = logging.getLogger(__name__)

# 初始化根代理（Root Agent）
root_agent = Agent(
    # 使用配置中的模型設定
    model=configs.agent_settings.model,
    # 全域指令（Global Instruction）
    global_instruction=GLOBAL_INSTRUCTION,
    # 特定任務指令（Instruction）
    instruction=INSTRUCTION,
    # 代理名稱
    name=configs.agent_settings.name,
    # 註冊代理可使用的工具清單
    tools=[
        send_call_companion_link,
        approve_discount,
        sync_ask_for_approval,
        update_salesforce_crm,
        access_cart_information,
        modify_cart,
        get_product_recommendations,
        check_product_availability,
        schedule_planting_service,
        get_available_planting_times,
        send_care_instructions,
        generate_qr_code,
    ],
    # 工具執行前的回呼函數
    before_tool_callback=before_tool,
    # 工具執行後的回呼函數
    after_tool_callback=after_tool,
    # 代理執行前的回呼函數
    before_agent_callback=before_agent,
    # 模型調用前的回呼函數（用於速率限制）
    before_model_callback=rate_limit_callback,
)

import logging
import uuid
from datetime import datetime, timedelta
from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)


def send_call_companion_link(phone_number: str) -> dict:
    """
    發送連結至使用者的電話號碼以啟動視訊會話。

    參數:
        phone_number (str): 要發送連結的電話號碼。

    回傳:
        dict: 包含狀態與訊息的字典。

    範例:
        >>> send_call_companion_link(phone_number='+12065550123')
        {'status': 'success', 'message': 'Link sent to +12065550123'}
    """

    logger.info("正在向 %s 發送直播連接連結", phone_number)

    return {"status": "success", "message": f"連結已發送至 {phone_number}"}


def approve_discount(discount_type: str, value: float, reason: str) -> dict:
    """
    批准使用者請求的固定金額或百分比折扣。

    參數:
        discount_type (str): 折扣類型，"percentage"（百分比）或 "flat"（固定金額）。
        value (float): 折扣數值。
        reason (str): 折扣原因。

    回傳:
        dict: 代表審核狀態的字典。

    範例:
        >>> approve_discount(discount_type='percentage', value=10.0, reason='Customer loyalty')
        {'status': 'ok'}
    """
    # 限制自動批准的上限，超過 10 則拒絕
    if value > 10:
        logger.info("拒絕類型為 %s 且數值為 %s 的折扣", discount_type, value)
        # 回傳錯誤原因，以便模型可以進行補救處理。
        return {"status": "rejected",
                "message": "折扣金額過大。必須等於或小於 10。"}

    logger.info(
        "已批准百分比為 %s 且數值為 %s 的折扣，原因為：%s", discount_type, value, reason
    )
    return {"status": "ok"}

def sync_ask_for_approval(discount_type: str, value: float, reason: str) -> dict:
    """
    向經理請求折扣批准。

    參數:
        discount_type (str): 折扣類型，"percentage"（百分比）或 "flat"（固定金額）。
        value (float): 折扣數值。
        reason (str): 折扣原因。

    回傳:
        dict: 代表審核狀態的字典。

    範例:
        >>> sync_ask_for_approval(discount_type='percentage', value=15, reason='Customer loyalty')
        {'status': 'approved'}
    """
    logger.info(
        "正在為數值為 %s 的 %s 折扣請求經理批准，原因為：%s",
        value,
        discount_type,
        reason,
    )
    return {"status": "approved"}


def update_salesforce_crm(customer_id: str, details: dict) -> dict:
    """
    使用客戶詳情更新 Salesforce CRM。

    參數:
        customer_id (str): 客戶 ID。
        details (dict): 要在 Salesforce 中更新的詳情字典。

    回傳:
        dict: 包含狀態與訊息的字典。

    範例:
        >>> update_salesforce_crm(customer_id='123', details={
            'appointment_date': '2024-07-25',
            'appointment_time': '9-12',
            'services': 'Planting',
            'discount': '15% off planting',
            'qr_code': '10% off next in-store purchase'})
        {'status': 'success', 'message': 'Salesforce record updated.'}
    """
    logger.info(
        "正在為客戶 ID %s 更新 Salesforce CRM，詳情為：%s",
        customer_id,
        details,
    )
    return {"status": "success", "message": "Salesforce 紀錄已更新。"}


def access_cart_information(customer_id: str) -> dict:
    """
    獲取購物車資訊。

    參數:
        customer_id (str): 客戶 ID。

    回傳:
        dict: 代表購物車內容的字典。

    範例:
        >>> access_cart_information(customer_id='123')
        {'items': [{'product_id': 'soil-123', 'name': 'Standard Potting Soil', 'quantity': 1}, {'product_id': 'fert-456', 'name': 'General Purpose Fertilizer', 'quantity': 1}], 'subtotal': 25.98}
    """
    logger.info("正在存取客戶 ID %s 的購物車資訊", customer_id)

    # 模擬 API 回應 - 應替換為實際的 API 調用
    mock_cart = {
        "items": [
            {
                "product_id": "soil-123",
                "name": "標準盆栽土",
                "quantity": 1,
            },
            {
                "product_id": "fert-456",
                "name": "通用肥料",
                "quantity": 1,
            },
        ],
        "subtotal": 25.98,
    }
    return mock_cart


def modify_cart(
    customer_id: str, items_to_add: list[dict], items_to_remove: list[dict]
) -> dict:
    """透過添加和/或刪除商品來修改使用者的購物車。

    參數:
        customer_id (str): 客戶 ID。
        items_to_add (list): 字典清單，每個字典包含 'product_id' 和 'quantity'。
        items_to_remove (list): 要刪除的產品 ID 清單。

    回傳:
        dict: 指示購物車修改狀態的字典。
    範例:
        >>> modify_cart(customer_id='123', items_to_add=[{'product_id': 'soil-456', 'quantity': 1}], items_to_remove=[{'product_id': 'fert-112', 'quantity': 1}])
        {'status': 'success', 'message': 'Cart updated successfully.', 'items_added': True, 'items_removed': True}
    """

    logger.info("正在為客戶 ID %s 修改購物車", customer_id)
    logger.info("新增商品：%s", items_to_add)
    logger.info("刪除商品：%s", items_to_remove)
    # 模擬 API 回應
    return {
        "status": "success",
        "message": "購物車更新成功。",
        "items_added": True,
        "items_removed": True,
    }


def get_product_recommendations(plant_type: str, customer_id: str) -> dict:
    """根據植物類型提供產品建議。

    參數:
        plant_type: 植物類型（例如：「矮牽牛」、「喜陽的一年生植物」）。
        customer_id: 選填的客戶 ID，用於個性化推薦。

    回傳:
        推薦產品的字典。
    """
    logger.info(
        "正在為植物類型 %s 和客戶 %s 獲取產品推薦",
        plant_type,
        customer_id,
    )
    # 模擬 API 回應
    if plant_type.lower() == "petunias" or plant_type == "矮牽牛":
        recommendations = {
            "recommendations": [
                {
                    "product_id": "soil-456",
                    "name": "Bloom Booster 盆栽混合土",
                    "description": "提供矮牽牛喜愛的額外養分。",
                },
                {
                    "product_id": "fert-789",
                    "name": "Flower Power 肥料",
                    "description": "專為開花一年生植物配製。",
                },
            ]
        }
    else:
        recommendations = {
            "recommendations": [
                {
                    "product_id": "soil-123",
                    "name": "標準盆栽土",
                    "description": "良好的通用型盆栽土。",
                },
                {
                    "product_id": "fert-456",
                    "name": "通用型肥料",
                    "description": "適用於多種植物。",
                },
            ]
        }
    return recommendations


def check_product_availability(product_id: str, store_id: str) -> dict:
    """在指定商店（或自取）檢查產品庫存。

    參數:
        product_id: 要檢查的產品 ID。
        store_id: 商店 ID（或輸入 'pickup' 代表自取可用性）。

    回傳:
        指示可用性的字典。
    """
    logger.info(
        "正在檢查產品 ID %s 在商店 %s 的庫存",
        product_id,
        store_id,
    )
    # 模擬 API 回應
    return {"available": True, "quantity": 10, "store": store_id}


def schedule_planting_service(
    customer_id: str, date: str, time_range: str, details: str
) -> dict:
    """預約種植服務。

    參數:
        customer_id: 客戶 ID。
        date: 期望日期 (YYYY-MM-DD)。
        time_range: 期望時段 (例如："9-12")。
        details: 任何額外詳情 (例如："種植矮牽牛")。

    回傳:
        指示預約狀態的字典。
    """
    logger.info(
        "正在為客戶 ID %s 安排 %s (%s) 的種植服務",
        customer_id,
        date,
        time_range,
    )
    logger.info("詳情：%s", details)
    # 模擬 API 回應
    # 根據日期和時段計算確認時間
    start_time_str = time_range.split("-")[0]
    confirmation_time_str = (
        f"{date} {start_time_str}:00"
    )

    return {
        "status": "success",
        "appointment_id": str(uuid.uuid4()),
        "date": date,
        "time": time_range,
        "confirmation_time": confirmation_time_str,
    }


def get_available_planting_times(date: str) -> list:
    """檢索給定日期的可用種植服務時段。

    參數:
        date: 要檢查的日期 (YYYY-MM-DD)。

    回傳:
        可用時段清單。
    """
    logger.info("正在檢索 %s 的可用種植時間", date)
    # 模擬 API 回應
    return ["9-12", "13-16"]


def send_care_instructions(
    customer_id: str, plant_type: str, delivery_method: str
) -> dict:
    """發送有關如何照顧特定植物類型的電子郵件或簡訊說明。

    參數:
        customer_id: 客戶 ID。
        plant_type: 植物類型。
        delivery_method: 'email' (預設) 或 'sms'。

    回傳:
        指示狀態的字典。
    """
    logger.info(
        "正在透過 %s 向客戶 %s 發送 %s 的護理說明",
        delivery_method,
        customer_id,
        plant_type,
    )
    # 模擬 API 回應
    return {
        "status": "success",
        "message": f"已透過 {delivery_method} 發送 {plant_type} 的護理說明。",
    }


def generate_qr_code(
    customer_id: str,
    discount_value: float,
    discount_type: str,
    expiration_days: int,
) -> dict:
    """生成折扣的 QR Code。

    參數:
        customer_id: 客戶 ID。
        discount_value: 折扣數值 (例如：百分比 10 代表 10%)。
        discount_type: "percentage" (預設) 或 "fixed"。
        expiration_days: QR Code 到期天數。

    回傳:
        包含 QR Code 數據（或連結）的字典。
    """

    # 安全護欄：驗證自動批准的折扣金額是否可接受。
    # 縱深防禦，防止惡意提示繞過系統指令獲取任意折扣。
    if discount_type == "" or discount_type == "percentage":
        if discount_value > 10:
            return "無法為此金額生成 QR Code，必須等於或小於 10%"
    if discount_type == "fixed" and discount_value > 20:
        return "無法為此金額生成 QR Code，必須等於或小於 20"

    logger.info(
        "正在為客戶 %s 生成數值為 %s 的 %s 折扣 QR Code。",
        customer_id,
        discount_value,
        discount_type,
    )
    # 模擬 API 回應
    expiration_date = (
        datetime.now() + timedelta(days=expiration_days)
    ).strftime("%Y-%m-%d")
    return {
        "status": "success",
        "qr_code_data": "MOCK_QR_CODE_DATA",
        "expiration_date": expiration_date,
    }

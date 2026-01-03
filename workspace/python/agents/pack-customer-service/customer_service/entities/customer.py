from typing import List, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class Address(BaseModel):
    """
    表示客戶的地址。
    """

    street: str
    city: str
    state: str
    zip: str
    model_config = ConfigDict(from_attributes=True)


class Product(BaseModel):
    """
    表示客戶購買歷史中的產品。
    """

    product_id: str
    name: str
    quantity: int
    model_config = ConfigDict(from_attributes=True)


class Purchase(BaseModel):
    """
    表示一次客戶購買紀錄。
    """

    date: str
    items: List[Product]
    total_amount: float
    model_config = ConfigDict(from_attributes=True)


class CommunicationPreferences(BaseModel):
    """
    表示客戶的通訊偏好設定。
    """

    email: bool = True
    sms: bool = True
    push_notifications: bool = True
    model_config = ConfigDict(from_attributes=True)


class GardenProfile(BaseModel):
    """
    表示客戶的園藝檔案資訊。
    """

    type: str # 類型
    size: str # 大小
    sun_exposure: str # 日照情況
    soil_type: str # 土壤類型
    interests: List[str] # 興趣愛好
    model_config = ConfigDict(from_attributes=True)


class Customer(BaseModel):
    """
    表示客戶實體。
    """

    account_number: str # 帳號
    customer_id: str # 客戶 ID
    customer_first_name: str # 名
    customer_last_name: str # 姓
    email: str # 電子郵件
    phone_number: str # 電話號碼
    customer_start_date: str # 成為客戶的日期
    years_as_customer: int # 成為客戶的年數
    billing_address: Address # 帳單地址
    purchase_history: List[Purchase] # 購買歷史
    loyalty_points: int # 忠誠度積分
    preferred_store: str # 偏好商店
    communication_preferences: CommunicationPreferences # 通訊偏好
    garden_profile: GardenProfile # 園藝檔案
    scheduled_appointments: Dict = Field(default_factory=dict) # 已預約的項目
    model_config = ConfigDict(from_attributes=True)

    def to_json(self) -> str:
        """
        將 Customer 物件轉換為 JSON 字串。

        回傳:
            代表 Customer 物件的 JSON 字串。
        """
        return self.model_dump_json(indent=4)

    @staticmethod
    def get_customer(current_customer_id: str) -> Optional["Customer"]:
        """
        根據 ID 檢索客戶。

        參數:
            current_customer_id: 要檢索的客戶 ID。

        回傳:
            如果找到則回傳 Customer 物件，否則回傳 None。
        """
        # 在實際應用中，這會涉及資料庫查詢。
        # 在此範例中，我們僅回傳一個虛構客戶。
        return Customer(
            customer_id=current_customer_id,
            account_number="428765091",
            customer_first_name="Alex",
            customer_last_name="Johnson",
            email="alex.johnson@example.com",
            phone_number="+1-702-555-1212",
            customer_start_date="2022-06-10",
            years_as_customer=2,
            billing_address=Address(
                street="123 Main St", city="Anytown", state="CA", zip="12345"
            ),
            purchase_history=[  # 範例購買歷史
                Purchase(
                    date="2023-03-05",
                    items=[
                        Product(
                            product_id="fert-111",
                            name="All-Purpose Fertilizer", # 全效肥料
                            quantity=1,
                        ),
                        Product(
                            product_id="trowel-222",
                            name="Gardening Trowel", # 園藝小鏟子
                            quantity=1,
                        ),
                    ],
                    total_amount=35.98,
                ),
                Purchase(
                    date="2023-07-12",
                    items=[
                        Product(
                            product_id="seeds-333",
                            name="Tomato Seeds (Variety Pack)", # 番茄種子（綜合包）
                            quantity=2,
                        ),
                        Product(
                            product_id="pots-444",
                            name="Terracotta Pots (6-inch)", # 陶土花盆（6英吋）
                            quantity=4,
                        ),
                    ],
                    total_amount=42.5,
                ),
                Purchase(
                    date="2024-01-20",
                    items=[
                        Product(
                            product_id="gloves-555",
                            name="Gardening Gloves (Leather)", # 園藝手套（皮革）
                            quantity=1,
                        ),
                        Product(
                            product_id="pruner-666",
                            name="Pruning Shears", # 修枝剪
                            quantity=1,
                        ),
                    ],
                    total_amount=55.25,
                ),
            ],
            loyalty_points=133,
            preferred_store="Anytown Garden Store",
            communication_preferences=CommunicationPreferences(
                email=True, sms=False, push_notifications=True
            ),
            garden_profile=GardenProfile(
                type="backyard", # 後院
                size="medium", # 中型
                sun_exposure="full sun", # 全日照
                soil_type="unknown", # 未知
                interests=["flowers", "vegetables"], # 興趣：花卉、蔬菜
            ),
            scheduled_appointments={},
        )

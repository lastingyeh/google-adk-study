"""
Commerce Agent 工具的單元測試。
在隔離環境中測試個別工具函式。
"""

import pytest
from commerce_agent.tools import (
    manage_user_preferences,
    curate_products,
    generate_product_narrative,
)
from commerce_agent.database import init_database
from commerce_agent.models import UserPreferences, Product


@pytest.mark.unit
class TestPreferencesTool:
    """測試偏好管理工具"""

    def setup_method(self):
        """每個測試前的設定"""
        init_database()

    def test_manage_preferences_get_new_user(self):
        """測試為新使用者取得偏好會回傳預設值"""
        result = manage_user_preferences(action="get", user_id="new_user_123")

        assert result["status"] == "success"
        assert "preferences" in result["data"]
        assert isinstance(result["data"]["preferences"]["sports"], list)

    def test_manage_preferences_update(self):
        """測試更新使用者偏好"""
        user_id = "update_test_user"

        result = manage_user_preferences(
            action="update",
            user_id=user_id,
            data={
                "sports": ["running", "cycling"],
                "price_range": {"min_price": 50.0, "max_price": 200.0},
                "brands": ["Kalenji", "Quechua"],
            },
        )

        assert result["status"] == "success"
        prefs = result["data"]["preferences"]
        assert "running" in prefs["sports"]
        assert "cycling" in prefs["sports"]

    def test_manage_preferences_get_existing(self):
        """測試擷取先前儲存的偏好"""
        user_id = "existing_user_456"

        # 首先，儲存偏好
        manage_user_preferences(
            action="update", user_id=user_id, data={"sports": ["yoga"]}
        )

        # 然後擷取
        result = manage_user_preferences(action="get", user_id=user_id)

        assert result["status"] == "success"
        assert "yoga" in result["data"]["preferences"]["sports"]

    def test_manage_preferences_add_history(self):
        """測試將互動新增至歷史紀錄"""
        user_id = "history_user"

        result = manage_user_preferences(
            action="add_history",
            user_id=user_id,
            data={
                "session_id": "session_789",
                "query": "Find running shoes",
                "result_count": 5,
            },
        )

        assert result["status"] == "success"
        assert result["data"]["interaction"]["query"] == "Find running shoes"

    def test_manage_preferences_add_favorite(self):
        """測試將產品新增至我的最愛"""
        user_id = "favorite_user"

        result = manage_user_preferences(
            action="add_favorite",
            user_id=user_id,
            data={
                "product_id": "prod_123",
                "product_name": "Awesome Shoes",
                "url": "https://decathlon.fr/product",
            },
        )

        assert result["status"] == "success"
        assert result["data"]["favorite"]["product_name"] == "Awesome Shoes"

    def test_manage_preferences_get_favorites(self):
        """測試擷取使用者我的最愛"""
        user_id = "favorites_user"

        # 新增一些我的最愛
        manage_user_preferences(
            action="add_favorite",
            user_id=user_id,
            data={"product_id": "p1", "product_name": "Product 1"},
        )
        manage_user_preferences(
            action="add_favorite",
            user_id=user_id,
            data={"product_id": "p2", "product_name": "Product 2"},
        )

        # 擷取我的最愛
        result = manage_user_preferences(action="get_favorites", user_id=user_id)

        assert result["status"] == "success"
        assert len(result["data"]["favorites"]) == 2

    def test_manage_preferences_invalid_action(self):
        """測試無效的動作會回傳錯誤"""
        result = manage_user_preferences(action="invalid_action", user_id="any_user")

        assert result["status"] == "error"
        assert "Unknown action" in result["report"]


@pytest.mark.unit
class TestProductCuration:
    """測試產品策展工具"""

    def test_curate_products_empty_list(self):
        """測試使用空產品清單進行策展"""
        result = curate_products(products=[])

        assert result["status"] == "success"
        assert result["data"]["curated_products"] == []

    def test_curate_products_basic(self, sample_products):
        """測試不含篩選器的基本產品策展"""
        result = curate_products(products=sample_products, limit=2)

        assert result["status"] == "success"
        assert len(result["data"]["curated_products"]) <= 2

    def test_curate_products_with_price_filter(self, sample_products):
        """測試使用價格範圍篩選器進行策展"""
        result = curate_products(
            products=sample_products,
            user_preferences={
                "sports": [],
                "price_range": {"min_price": 50.0, "max_price": 100.0},
                "brands": [],
            },
            limit=5,
        )

        assert result["status"] == "success"
        curated = result["data"]["curated_products"]

        # 所有產品都應在價格範圍內
        for product in curated:
            assert 50.0 <= product["price"] <= 100.0

    def test_curate_products_with_brand_filter(self, sample_products):
        """測試策展會優先考慮偏好的品牌"""
        result = curate_products(
            products=sample_products,
            user_preferences={
                "sports": [],
                "price_range": {"min_price": 0.0, "max_price": 500.0},
                "brands": ["Kalenji"],
            },
            limit=5,
        )

        assert result["status"] == "success"
        curated = result["data"]["curated_products"]

        # 應該至少有一個產品
        assert len(curated) > 0

    def test_curate_products_respects_limit(self, sample_products):
        """測試策展會遵守 limit 參數"""
        result = curate_products(products=sample_products, limit=1)

        assert len(result["data"]["curated_products"]) <= 1


@pytest.mark.unit
class TestProductNarrative:
    """測試產品故事生成"""

    def test_generate_narrative_valid_product(self, sample_product):
        """測試有效產品的故事生成"""
        result = generate_product_narrative(product=sample_product.model_dump())

        assert result["status"] == "success"
        assert "narrative_template" in result["data"]
        assert sample_product.name in result["data"]["narrative_template"]

    def test_generate_narrative_with_context(self, sample_product):
        """測試包含使用者情境的故事"""
        result = generate_product_narrative(
            product=sample_product.model_dump(),
            user_context={"sports": ["running", "cycling"]},
        )

        assert result["status"] == "success"
        narrative = result["data"]["narrative_template"]
        assert "running" in narrative or "cycling" in narrative

    def test_generate_narrative_missing_product_name(self):
        """測試無效產品的錯誤處理"""
        result = generate_product_narrative(product={})  # 缺少必要欄位

        assert result["status"] == "error"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

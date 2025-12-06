"""
Commerce Agent 的端對端測試。
測試完整的工作流程和使用者情境。
"""

import pytest
from commerce_agent.database import (
    init_database,
    get_user_preferences,
    get_user_history,
    get_user_favorites,
    get_engagement_profile,
)
from commerce_agent.tools import manage_user_preferences
from commerce_agent.models import UserPreferences, InteractionRecord


@pytest.mark.e2e
class TestUserScenarios:
    """測試完整的使用者情境"""

    def setup_method(self):
        """每個測試前的設定"""
        init_database()

    def test_scenario_new_athlete(self):
        """測試新運動員使用者的完整流程"""
        user_id = "new_athlete"

        # 步驟 1：使用者設定偏好
        result = manage_user_preferences(
            action="update", user_id=user_id, data={"sports": ["running", "cycling"]}
        )
        assert result["status"] == "success"

        # 步驟 2：查詢搜尋
        result = manage_user_preferences(
            action="add_history",
            user_id=user_id,
            data={
                "session_id": "session_1",
                "query": "Find running shoes under 100",
                "result_count": 5,
            },
        )
        assert result["status"] == "success"

        # 步驟 3：新增喜愛的產品
        result = manage_user_preferences(
            action="add_favorite",
            user_id=user_id,
            data={
                "product_id": "kalenji_123",
                "product_name": "Kalenji Running Shoes",
                "url": "https://decathlon.fr/kalenji",
            },
        )
        assert result["status"] == "success"

        # 驗證完整的個人資料
        prefs = get_user_preferences(user_id)
        assert prefs is not None
        assert "running" in prefs.sports

        history = get_user_history(user_id)
        assert len(history) == 1
        assert history[0].query == "Find running shoes under 100"

        favorites = get_user_favorites(user_id)
        assert len(favorites) == 1
        assert favorites[0].product_name == "Kalenji Running Shoes"

    def test_scenario_returning_customer(self):
        """測試具有現有個人資料的回頭客流程"""
        user_id = "returning_customer"

        # 工作階段 1：初始設定
        manage_user_preferences(
            action="update", user_id=user_id, data={"sports": ["yoga"]}
        )
        manage_user_preferences(
            action="add_history",
            user_id=user_id,
            data={"session_id": "session_1", "query": "Yoga mats", "result_count": 3},
        )

        # 工作階段 2：帶著新的興趣回來
        result = manage_user_preferences(
            action="update",
            user_id=user_id,
            data={"sports": ["yoga", "hiking"]},  # 新增 hiking
        )
        assert result["status"] == "success"

        # 驗證偏好已累積
        prefs = get_user_preferences(user_id)
        assert "yoga" in prefs.sports
        assert "hiking" in prefs.sports

        # 新增新的互動
        manage_user_preferences(
            action="add_history",
            user_id=user_id,
            data={
                "session_id": "session_2",
                "query": "Hiking boots",
                "result_count": 4,
            },
        )

        # 驗證歷史紀錄包含兩個互動
        history = get_user_history(user_id, limit=10)
        assert len(history) == 2

    def test_scenario_multi_user_isolation(self):
        """測試不同使用者之間不會互相干擾"""
        user_alice = "alice"
        user_bob = "bob"

        # Alice 的個人資料
        manage_user_preferences(
            action="update", user_id=user_alice, data={"sports": ["running"]}
        )
        manage_user_preferences(
            action="add_favorite",
            user_id=user_alice,
            data={"product_id": "p1", "product_name": "Running Shoes"},
        )

        # Bob 的個人資料
        manage_user_preferences(
            action="update", user_id=user_bob, data={"sports": ["cycling"]}
        )
        manage_user_preferences(
            action="add_favorite",
            user_id=user_bob,
            data={"product_id": "p2", "product_name": "Bike Helmet"},
        )

        # 驗證完全隔離
        alice_prefs = get_user_preferences(user_alice)
        bob_prefs = get_user_preferences(user_bob)

        assert "running" in alice_prefs.sports
        assert "cycling" not in alice_prefs.sports

        assert "cycling" in bob_prefs.sports
        assert "running" not in bob_prefs.sports

        # 驗證喜愛項目是隔離的
        alice_favs = get_user_favorites(user_alice)
        bob_favs = get_user_favorites(user_bob)

        assert len(alice_favs) == 1
        assert alice_favs[0].product_name == "Running Shoes"

        assert len(bob_favs) == 1
        assert bob_favs[0].product_name == "Bike Helmet"


@pytest.mark.e2e
class TestEngagementTracking:
    """測試參與度設定檔追蹤"""

    def setup_method(self):
        """每個測試前的設定"""
        init_database()

    def test_engagement_profile_creation(self):
        """測試參與度設定檔是否正確建立"""
        user_id = "engaged_user"

        # 建立參與度
        manage_user_preferences(
            action="update",
            user_id=user_id,
            data={"sports": ["running", "cycling"], "brands": ["Kalenji", "Quechua"]},
        )

        manage_user_preferences(
            action="add_history",
            user_id=user_id,
            data={"session_id": "s1", "query": "Running shoes", "result_count": 5},
        )

        manage_user_preferences(
            action="add_history",
            user_id=user_id,
            data={"session_id": "s2", "query": "Cycling shorts", "result_count": 3},
        )

        # 取得設定檔
        profile = get_engagement_profile(user_id)

        assert profile.total_interactions == 2
        assert "running" in profile.favorite_categories
        assert "cycling" in profile.favorite_categories
        assert "Kalenji" in profile.preferred_brands
        assert "Quechua" in profile.preferred_brands


@pytest.mark.e2e
class TestErrorRecovery:
    """測試錯誤處理和復原"""

    def setup_method(self):
        """每個測試前的設定"""
        init_database()

    def test_invalid_preference_update_recovered(self):
        """測試系統從無效的偏好更新中復原"""
        user_id = "recovery_user"

        # 有效更新
        manage_user_preferences(
            action="update", user_id=user_id, data={"sports": ["running"]}
        )

        # 無效的更新嘗試 (缺少必要的資料)
        result = manage_user_preferences(
            action="add_history", user_id=user_id, data={}  # 缺少必要的欄位
        )
        assert result["status"] == "error"

        # 系統應復原 - 原始資料應保持不變
        prefs = get_user_preferences(user_id)
        assert "running" in prefs.sports

    def test_missing_user_preference_defaults(self):
        """測試遺失的使用者回傳預設偏好"""
        result = manage_user_preferences(action="get", user_id="nonexistent_user")

        assert result["status"] == "success"
        prefs = result["data"]["preferences"]
        assert isinstance(prefs["sports"], list)
        assert isinstance(prefs["price_range"], dict)


@pytest.mark.e2e
class TestDataPersistence:
    """測試資料在操作之間是否持續存在"""

    def setup_method(self):
        """每個測試前的設定"""
        init_database()

    def test_preferences_persist_across_operations(self):
        """測試偏好在多次操作後保持一致"""
        user_id = "persistence_user"
        original_sports = ["running", "climbing"]

        # 設定初始偏好
        manage_user_preferences(
            action="update", user_id=user_id, data={"sports": original_sports}
        )

        # 執行其他操作
        manage_user_preferences(
            action="add_history",
            user_id=user_id,
            data={"session_id": "s1", "query": "test"},
        )
        manage_user_preferences(
            action="add_favorite",
            user_id=user_id,
            data={"product_id": "p1", "product_name": "Product"},
        )

        # 驗證偏好未改變
        prefs = get_user_preferences(user_id)
        assert set(prefs.sports) == set(original_sports)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

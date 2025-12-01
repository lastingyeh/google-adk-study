"""測試工具函式。"""

import pytest


class TestSearchKnowledgeBase:
    """測試 search_knowledge_base 工具。"""

    def test_search_refund_policy(self):
        """測試搜尋退款政策。"""
        try:
            from agent.agent import search_knowledge_base

            result = search_knowledge_base("refund policy")
            assert result["status"] == "success"
            assert "article" in result
            assert "Refund" in result["article"]["title"]
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_search_shipping(self):
        """測試搜尋運送資訊。"""
        try:
            from agent.agent import search_knowledge_base

            result = search_knowledge_base("shipping")
            assert result["status"] == "success"
            assert "article" in result
            assert "Shipping" in result["article"]["title"]
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_search_warranty(self):
        """測試搜尋保固資訊。"""
        try:
            from agent.agent import search_knowledge_base

            result = search_knowledge_base("warranty")
            assert result["status"] == "success"
            assert "article" in result
            assert "Warranty" in result["article"]["title"]
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_search_unknown_returns_general(self):
        """測試未知查詢返回一般支援。"""
        try:
            from agent.agent import search_knowledge_base

            result = search_knowledge_base("some unknown query")
            assert result["status"] == "success"
            assert "article" in result
            assert "Support" in result["article"]["title"]
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")


class TestLookupOrderStatus:
    """測試 lookup_order_status 工具。"""

    def test_lookup_valid_order(self):
        """測試查詢有效訂單。"""
        try:
            from agent.agent import lookup_order_status

            result = lookup_order_status("ORD-12345")
            assert result["status"] == "success"
            assert "order" in result
            assert result["order"]["order_id"] == "ORD-12345"
            assert "status" in result["order"]
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_lookup_invalid_order(self):
        """測試查詢無效訂單。"""
        try:
            from agent.agent import lookup_order_status

            result = lookup_order_status("ORD-99999")
            assert result["status"] == "error"
            assert "error" in result or "report" in result
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_lookup_lowercase_order_id(self):
        """測試訂單 ID 查詢不分大小寫。"""
        try:
            from agent.agent import lookup_order_status

            result = lookup_order_status("ord-12345")
            assert result["status"] == "success"
            assert "order" in result
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")


class TestCreateSupportTicket:
    """測試 create_support_ticket 工具。"""

    def test_create_normal_priority_ticket(self):
        """測試建立普通優先級工單。"""
        try:
            from agent.agent import create_support_ticket

            result = create_support_ticket("Test issue", "normal")
            assert result["status"] == "success"
            assert "ticket" in result
            assert "ticket_id" in result["ticket"]
            assert result["ticket"]["priority"] == "normal"
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_create_urgent_priority_ticket(self):
        """測試建立緊急優先級工單。"""
        try:
            from agent.agent import create_support_ticket

            result = create_support_ticket("Urgent issue", "urgent")
            assert result["status"] == "success"
            assert "ticket" in result
            assert result["ticket"]["priority"] == "urgent"
            assert "1-2 hours" in result["ticket"]["estimated_response"]
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_create_ticket_default_priority(self):
        """測試建立預設優先級工單。"""
        try:
            from agent.agent import create_support_ticket

            result = create_support_ticket("Test issue")
            assert result["status"] == "success"
            assert "ticket" in result
            assert result["ticket"]["priority"] == "normal"
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_ticket_id_format(self):
        """測試工單 ID 格式是否正確。"""
        try:
            from agent.agent import create_support_ticket

            result = create_support_ticket("Test issue")
            ticket_id = result["ticket"]["ticket_id"]
            assert ticket_id.startswith("TICKET-")
            assert len(ticket_id) > 7  # TICKET- plus hash
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")


class TestCreateProductCard:
    """測試 create_product_card 工具 (進階功能 1: 生成式 UI)。"""

    def test_create_valid_product_card(self):
        """測試為有效產品建立產品卡片。"""
        try:
            from agent.agent import create_product_card

            result = create_product_card("PROD-001")
            assert result["status"] == "success"
            assert "product" in result
            assert result["product"]["name"] == "Widget Pro"
            assert result["product"]["price"] == 99.99
            assert "component" in result
            assert result["component"] == "ProductCard"
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_create_product_card_all_products(self):
        """測試為所有可用產品建立產品卡片。"""
        try:
            from agent.agent import create_product_card

            product_ids = ["PROD-001", "PROD-002", "PROD-003"]
            for product_id in product_ids:
                result = create_product_card(product_id)
                assert result["status"] == "success"
                assert "product" in result
                assert "name" in result["product"]
                assert "price" in result["product"]
                assert "rating" in result["product"]
                assert "inStock" in result["product"]
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_create_invalid_product_card(self):
        """測試為無效產品建立產品卡片。"""
        try:
            from agent.agent import create_product_card

            result = create_product_card("PROD-999")
            assert result["status"] == "error"
            assert "error" in result or "report" in result
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_product_card_lowercase_id(self):
        """測試產品 ID 查詢不分大小寫。"""
        try:
            from agent.agent import create_product_card

            result = create_product_card("prod-001")
            assert result["status"] == "success"
            assert "product" in result
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")


class TestProcessRefund:
    """測試 process_refund 工具 (進階功能 2: 人在迴路)。"""

    def test_process_refund_success(self):
        """測試成功處理退款。"""
        try:
            from agent.agent import process_refund

            result = process_refund("ORD-12345", 99.99, "Product defective")
            assert result["status"] == "success"
            assert "refund" in result
            assert "refund_id" in result["refund"]
            assert result["refund"]["order_id"] == "ORD-12345"
            assert result["refund"]["amount"] == 99.99
            assert result["refund"]["reason"] == "Product defective"
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_refund_id_format(self):
        """測試退款 ID 格式是否正確。"""
        try:
            from agent.agent import process_refund

            result = process_refund("ORD-12345", 50.00, "Test reason")
            refund_id = result["refund"]["refund_id"]
            assert refund_id.startswith("REF-")
            assert len(refund_id) > 4  # REF- plus hash
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_refund_includes_all_fields(self):
        """測試退款回應包含所有必要欄位。"""
        try:
            from agent.agent import process_refund

            result = process_refund("ORD-67890", 149.99, "Changed mind")
            refund = result["refund"]
            required_fields = [
                "refund_id",
                "order_id",
                "amount",
                "reason",
                "status",
                "processed_at",
                "estimated_credit_date",
            ]
            for field in required_fields:
                assert field in refund, f"Missing field: {field}"
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_refund_different_amounts(self):
        """測試處理不同金額的退款。"""
        try:
            from agent.agent import process_refund

            amounts = [10.50, 99.99, 299.99, 1000.00]
            for amount in amounts:
                result = process_refund(f"ORD-{int(amount)}", amount, "Test")
                assert result["status"] == "success"
                assert result["refund"]["amount"] == amount
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

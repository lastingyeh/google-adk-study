# 教程 20：YAML 設定 - 工具測試
# 驗證工具函式實作

import pytest
from customer_support.tools.customer_tools import (
    check_customer_status,
    log_interaction,
    get_order_status,
    track_shipment,
    cancel_order,
    search_knowledge_base,
    run_diagnostic,
    create_ticket,
    get_billing_history,
    process_refund,
    update_payment_method,
)


class TestCustomerTools:
    """測試客戶相關工具函式。"""

    def test_check_customer_status_premium(self):
        """測試檢查高級會員客戶狀態。"""
        result = check_customer_status('CUST-001')

        assert result['status'] == 'success'
        assert 'premium' in result['report']
        assert result['data']['tier'] == 'premium'
        assert result['data']['is_premium'] is True

    def test_check_customer_status_standard(self):
        """測試檢查標準會員客戶狀態。"""
        result = check_customer_status('CUST-999')

        assert result['status'] == 'success'
        assert 'standard' in result['report']
        assert result['data']['tier'] == 'standard'
        assert result['data']['is_premium'] is False

    def test_log_interaction(self):
        """測試記錄客戶互動。"""
        result = log_interaction('CUST-001', 'inquiry', 'Asked about order status')

        assert result['status'] == 'success'
        assert 'logged successfully' in result['report']
        assert result['data']['customer_id'] == 'CUST-001'
        assert result['data']['interaction_type'] == 'inquiry'


class TestOrderTools:
    """測試訂單相關工具函式。"""

    def test_get_order_status_found(self):
        """測試取得現有訂單狀態。"""
        result = get_order_status('ORD-001')

        assert result['status'] == 'success'
        assert 'shipped' in result['report']
        assert result['data']['status'] == 'shipped'

    def test_get_order_status_not_found(self):
        """測試取得不存在的訂單狀態。"""
        result = get_order_status('ORD-999')

        assert result['status'] == 'error'
        assert 'No order found with ID' in result['report']

    def test_track_shipment_found(self):
        """測試追蹤現有出貨。"""
        result = track_shipment('ORD-001')

        assert result['status'] == 'success'
        assert 'UPS' in result['report']
        assert result['data']['carrier'] == 'UPS'

    def test_track_shipment_not_found(self):
        """測試追蹤不存在的出貨。"""
        result = track_shipment('ORD-999')

        assert result['status'] == 'error'
        assert 'No tracking information found' in result['report']

    def test_cancel_order_success(self):
        """測試取消符合資格的訂單。"""
        result = cancel_order('ORD-001', 'Changed mind')

        assert result['status'] == 'success'
        assert 'cancelled' in result['report']
        assert result['data']['reason'] == 'Changed mind'

    def test_cancel_order_ineligible(self):
        """測試取消不符合資格的訂單。"""
        result = cancel_order('ORD-004', 'Order already cancelled')

        assert result['status'] == 'error'
        assert 'not eligible for cancellation' in result['report']


class TestTechnicalTools:
    """測試技術支援工具函式。"""

    def test_search_knowledge_base_found(self):
        """測試使用相符的查詢搜尋知識庫。"""
        result = search_knowledge_base('login issue')

        assert result['status'] == 'success'
        assert len(result['data']['results']) > 0
        assert 'login' in result['data']['results'][0]['topic']

    def test_search_knowledge_base_not_found(self):
        """測試搜尋知識庫無相符結果。"""
        result = search_knowledge_base('quantum physics')

        assert result['status'] == 'success'
        assert len(result['data']['results']) == 0
        assert 'No matching article found' in result['report']

    def test_run_diagnostic_known_issue(self):
        """測試針對已知問題類型執行診斷。"""
        result = run_diagnostic('connection')

        assert result['status'] == 'success'
        assert 'All systems operational' in result['report']
        assert result['data']['issue_type'] == 'connection'

    def test_run_diagnostic_unknown_issue(self):
        """測試針對未知問題類型執行診斷。"""
        result = run_diagnostic('unknown_problem')

        assert result['status'] == 'error'
        assert 'No diagnostic available' in result['report']

    def test_create_ticket(self):
        """測試建立支援票據。"""
        result = create_ticket('CUST-001', 'App crashes on startup', 'high')

        assert result['status'] == 'success'
        assert 'created with high priority' in result['report']
        assert result['data']['priority'] == 'high'
        assert 'ticket_id' in result['data']


class TestBillingTools:
    """測試帳務相關工具函式。"""

    def test_get_billing_history_found(self):
        """測試取得現有客戶的帳務歷史記錄。"""
        result = get_billing_history('CUST-001')

        assert result['status'] == 'success'
        assert len(result['data']['transactions']) > 0
        assert result['data']['total_amount'] > 0

    def test_get_billing_history_not_found(self):
        """測試取得不存在客戶的帳務歷史記錄。"""
        result = get_billing_history('CUST-999')

        assert result['status'] == 'error'
        assert 'No billing records found' in result['report']

    def test_process_refund_small_amount(self):
        """測試處理小額退款。"""
        result = process_refund('ORD-001', 50.00)

        assert result['status'] == 'success'
        assert 'approved' in result['report']
        assert result['data']['status'] == 'approved'

    def test_process_refund_large_amount(self):
        """測試處理需要批准的大額退款。"""
        result = process_refund('ORD-001', 150.00)

        assert result['status'] == 'error'
        assert 'REQUIRES_APPROVAL' in result['error']
        assert 'needs manager approval' in result['report']

    def test_update_payment_method_valid(self):
        """測試更新為有效的付款方式。"""
        result = update_payment_method('CUST-001', 'paypal')

        assert result['status'] == 'success'
        assert 'updated to paypal' in result['report']
        assert result['data']['payment_type'] == 'paypal'

    def test_update_payment_method_invalid(self):
        """測試更新為無效的付款方式。"""
        result = update_payment_method('CUST-001', 'cryptocurrency')

        assert result['status'] == 'error'
        assert 'Payment type must be one of:' in result['report']


class TestToolReturnFormats:
    """測試所有工具是否回傳正確的格式。"""

    def test_all_tools_return_dict(self):
        """測試所有工具是否回傳字典物件。"""
        tools = [
            lambda: check_customer_status('CUST-001'),
            lambda: log_interaction('CUST-001', 'test', 'test'),
            lambda: get_order_status('ORD-001'),
            lambda: track_shipment('ORD-001'),
            lambda: cancel_order('ORD-001', 'test'),
            lambda: search_knowledge_base('login'),
            lambda: run_diagnostic('connection'),
            lambda: create_ticket('CUST-001', 'test', 'medium'),
            lambda: get_billing_history('CUST-001'),
            lambda: process_refund('ORD-001', 10.00),
            lambda: update_payment_method('CUST-001', 'credit_card'),
        ]

        for tool_func in tools:
            result = tool_func()
            assert isinstance(result, dict), f"工具 {tool_func.__name__} 應該回傳字典"

    def test_tools_have_required_fields(self):
        """測試工具是否回傳必要欄位。"""
        result = check_customer_status('CUST-001')

        assert 'status' in result
        assert 'report' in result
        assert 'data' in result

        assert result['status'] in ['success', 'error']

    def test_error_responses_have_error_field(self):
        """測試錯誤回應是否包含 error 欄位。"""
        result = get_order_status('ORD-999')  # 不存在的訂單

        assert result['status'] == 'error'
        assert 'error' in result
        assert len(result['error']) > 0

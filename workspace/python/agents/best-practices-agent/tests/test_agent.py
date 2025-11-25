"""測試最佳實踐代理及其工具。"""

import pytest
from best_practices_agent import root_agent
from best_practices_agent.agent import (
    validate_input_tool,
    retry_with_backoff_tool,
    circuit_breaker_call_tool,
    cache_operation_tool,
    batch_process_tool,
    health_check_tool,
    get_metrics_tool,
    CircuitBreaker,
    CachedDataStore,
    MetricsCollector,
    CircuitState,
    InputRequest,
)


# ============================================================================
# 代理配置測試 (AGENT CONFIGURATION TESTS)
# ============================================================================

class TestAgentConfiguration:
    """測試代理配置和設定。"""

    def test_agent_exists(self):
        """測試 root_agent 是否已正確定義。"""
        assert root_agent is not None

    def test_agent_name(self):
        """測試代理是否具有正確的名稱。"""
        assert root_agent.name == "best_practices_agent"

    def test_agent_model(self):
        """測試代理是否使用正確的模型。"""
        assert root_agent.model == "gemini-2.5-flash"

    def test_agent_has_description(self):
        """測試代理是否有描述。"""
        assert root_agent.description is not None
        assert len(root_agent.description) > 0
        assert "production-ready" in root_agent.description.lower()

    def test_agent_has_instruction(self):
        """測試代理是否有指令。"""
        assert root_agent.instruction is not None
        assert len(root_agent.instruction) > 0

    def test_agent_has_tools(self):
        """測試代理是否具有所有必需的工具。"""
        assert root_agent.tools is not None
        assert len(root_agent.tools) == 7

        # 檢查工具名稱
        tool_names = [tool.__name__ for tool in root_agent.tools]
        expected_tools = [
            'validate_input_tool',
            'retry_with_backoff_tool',
            'circuit_breaker_call_tool',
            'cache_operation_tool',
            'batch_process_tool',
            'health_check_tool',
            'get_metrics_tool',
        ]

        for expected in expected_tools:
            assert expected in tool_names, f"缺少工具: {expected}"


# ============================================================================
# 驗證測試 (VALIDATION TESTS)
# ============================================================================

class TestValidation:
    """測試輸入驗證功能。"""

    def test_validate_valid_email(self):
        """測試有效電子郵件的驗證。"""
        result = validate_input_tool(
            email="user@example.com",
            text="Hello world",
            priority="normal"
        )

        assert result['status'] == 'success'
        assert 'validated_data' in result
        assert result['validated_data']['email'] == "user@example.com"

    def test_validate_invalid_email(self):
        """測試無效電子郵件的驗證。"""
        result = validate_input_tool(
            email="invalid-email",
            text="Hello world",
            priority="normal"
        )

        assert result['status'] == 'error'
        assert 'error' in result

    def test_validate_invalid_priority(self):
        """測試無效優先級的驗證。"""
        result = validate_input_tool(
            email="user@example.com",
            text="Hello world",
            priority="super-urgent"  # 無效
        )

        assert result['status'] == 'error'
        assert 'error' in result

    def test_validate_dangerous_text(self):
        """測試驗證是否阻擋危險模式 (SQL Injection)。"""
        result = validate_input_tool(
            email="user@example.com",
            text="DROP TABLE users",
            priority="normal"
        )

        assert result['status'] == 'error'
        assert 'dangerous' in result['error'].lower() or 'dangerous' in result['report'].lower()

    def test_validate_xss_attempt(self):
        """測試驗證是否阻擋 XSS 攻擊嘗試。"""
        result = validate_input_tool(
            email="user@example.com",
            text="Hello <script>alert('xss')</script>",
            priority="normal"
        )

        assert result['status'] == 'error'

    def test_validate_empty_text(self):
        """測試驗證是否拒絕空文字。"""
        result = validate_input_tool(
            email="user@example.com",
            text="",
            priority="normal"
        )

        assert result['status'] == 'error'

    def test_input_request_model(self):
        """測試 InputRequest Pydantic 模型。"""
        # 有效請求
        request = InputRequest(
            email="test@example.com",
            text="Hello",
            priority="high"
        )
        assert request.email == "test@example.com"
        assert request.priority == "high"

        # 無效優先級應引發錯誤
        with pytest.raises(ValueError):
            InputRequest(
                email="test@example.com",
                text="Hello",
                priority="invalid"
            )


# ============================================================================
# 重試邏輯測試 (RETRY LOGIC TESTS)
# ============================================================================

class TestRetryLogic:
    """測試指數退避重試機制。"""

    def test_retry_eventually_succeeds(self):
        """測試重試邏輯最終能否成功。"""
        result = retry_with_backoff_tool(
            operation="test_operation",
            max_retries=5
        )

        # 應最終成功（或記錄所有嘗試）
        assert 'status' in result
        assert 'attempts' in result or 'report' in result

    def test_retry_with_max_retries(self):
        """測試重試是否遵守最大重試次數。"""
        result = retry_with_backoff_tool(
            operation="test_operation",
            max_retries=1
        )

        assert 'status' in result
        assert 'report' in result

    def test_retry_includes_timing(self):
        """測試重試是否包含計時資訊。"""
        result = retry_with_backoff_tool(
            operation="test_operation",
            max_retries=2
        )

        assert 'total_time_ms' in result


# ============================================================================
# 斷路器測試 (CIRCUIT BREAKER TESTS)
# ============================================================================

class TestCircuitBreaker:
    """測試斷路器模式。"""

    def test_circuit_breaker_success(self):
        """測試斷路器呼叫成功的情況。"""
        result = circuit_breaker_call_tool(
            service_name="test_service",
            simulate_failure=False
        )

        assert result['status'] == 'success'
        assert result['circuit_state'] in ['closed', 'open', 'half_open']

    def test_circuit_breaker_failure(self):
        """測試斷路器呼叫失敗的情況。"""
        result = circuit_breaker_call_tool(
            service_name="test_service",
            simulate_failure=True
        )

        assert result['status'] == 'error'
        assert 'circuit_state' in result

    def test_circuit_breaker_class(self):
        """直接測試 CircuitBreaker 類別。"""
        breaker = CircuitBreaker(failure_threshold=2, timeout_seconds=1)

        assert breaker.state == CircuitState.CLOSED
        assert breaker.failures == 0

        # 模擬失敗
        def failing_func():
            raise Exception("Test failure")

        # 第一次失敗
        with pytest.raises(Exception):
            breaker.call(failing_func)
        assert breaker.failures == 1

        # 第二次失敗應打開電路
        with pytest.raises(Exception):
            breaker.call(failing_func)
        assert breaker.state == CircuitState.OPEN

    def test_circuit_breaker_enum(self):
        """測試 CircuitState 列舉。"""
        assert CircuitState.CLOSED.value == "closed"
        assert CircuitState.OPEN.value == "open"
        assert CircuitState.HALF_OPEN.value == "half_open"


# ============================================================================
# 快取測試 (CACHING TESTS)
# ============================================================================

class TestCaching:
    """測試快取功能。"""

    def test_cache_set_and_get(self):
        """測試快取的設定和獲取操作。"""
        # 設定值
        set_result = cache_operation_tool(
            key="test_key",
            value="test_value",
            operation="set"
        )
        assert set_result['status'] == 'success'

        # 獲取值
        get_result = cache_operation_tool(
            key="test_key",
            operation="get"
        )
        assert get_result['status'] == 'success'
        assert get_result['cache_hit']
        assert get_result['value'] == "test_value"

    def test_cache_miss(self):
        """測試快取未命中場景。"""
        result = cache_operation_tool(
            key="nonexistent_key",
            operation="get"
        )

        assert result['status'] == 'success'
        assert not result['cache_hit']

    def test_cache_stats(self):
        """測試快取統計資訊。"""
        result = cache_operation_tool(
            key="any",
            operation="stats"
        )

        assert result['status'] == 'success'
        assert 'statistics' in result
        assert 'hits' in result['statistics']
        assert 'misses' in result['statistics']

    def test_cache_set_without_value(self):
        """測試快取設定是否需要值。"""
        result = cache_operation_tool(
            key="test_key",
            operation="set"
        )

        assert result['status'] == 'error'

    def test_cached_data_store_class(self):
        """直接測試 CachedDataStore 類別。"""
        cache = CachedDataStore(ttl_seconds=1)

        # 在 TTL 內設定和獲取
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # 檢查統計
        stats = cache.stats()
        assert 'hits' in stats
        assert 'misses' in stats
        assert 'hit_rate' in stats


# ============================================================================
# 批次處理測試 (BATCH PROCESSING TESTS)
# ============================================================================

class TestBatchProcessing:
    """測試批次處理功能。"""

    def test_batch_process_items(self):
        """測試項目的批次處理。"""
        items = ["item1", "item2", "item3"]
        result = batch_process_tool(items=items)

        assert result['status'] == 'success'
        assert result['items_processed'] == 3
        assert 'results' in result
        assert len(result['results']) == 3

    def test_batch_process_single_item(self):
        """測試單個項目的批次處理。"""
        items = ["single_item"]
        result = batch_process_tool(items=items)

        assert result['status'] == 'success'
        assert result['items_processed'] == 1

    def test_batch_process_empty_list(self):
        """測試空列表的批次處理。"""
        result = batch_process_tool(items=[])

        assert result['status'] == 'error'

    def test_batch_process_efficiency(self):
        """測試批次處理是否報告效率。"""
        items = ["a", "b", "c", "d", "e"]
        result = batch_process_tool(items=items)

        if result['status'] == 'success':
            assert 'processing_time_ms' in result
            assert 'efficiency_gain' in result


# ============================================================================
# 監控測試 (MONITORING TESTS)
# ============================================================================

class TestMonitoring:
    """測試監控和可觀測性。"""

    def test_health_check(self):
        """測試健康檢查工具。"""
        result = health_check_tool()

        assert result['status'] == 'success'
        assert 'health' in result
        assert 'status' in result['health']
        assert result['health']['status'] in ['healthy', 'degraded', 'unhealthy']

    def test_get_metrics(self):
        """測試指標檢索。"""
        result = get_metrics_tool()

        assert result['status'] == 'success'
        assert 'metrics' in result
        assert 'total_requests' in result['metrics']

    def test_metrics_collector_class(self):
        """直接測試 MetricsCollector 類別。"""
        collector = MetricsCollector()

        # 記錄一些請求
        collector.record_request(latency=0.1, error=False)
        collector.record_request(latency=0.2, error=True)

        metrics = collector.get_metrics()

        assert metrics['total_requests'] == 2
        assert metrics['total_errors'] == 1
        assert 'error_rate' in metrics
        assert 'avg_latency_ms' in metrics

        # 測試健康檢查
        health = collector.health_check()
        assert 'status' in health
        assert 'metrics' in health


# ============================================================================
# 整合測試 (INTEGRATION TESTS)
# ============================================================================

class TestIntegration:
    """測試整合場景。"""

    def test_full_workflow(self):
        """測試使用多個工具的完整工作流程。"""
        # 1. 驗證輸入
        validation = validate_input_tool(
            email="user@example.com",
            text="Process order",
            priority="high"
        )
        assert validation['status'] == 'success'

        # 2. 快取一些數據
        cache_set = cache_operation_tool(
            key="workflow_data",
            value="important_data",
            operation="set"
        )
        assert cache_set['status'] == 'success'

        # 3. 批次處理
        batch = batch_process_tool(items=["order1", "order2"])
        assert batch['status'] == 'success'

        # 4. 檢查健康狀況
        health = health_check_tool()
        assert health['status'] == 'success'

    def test_error_handling_workflow(self):
        """測試跨多個操作的錯誤處理。"""
        # 無效驗證
        result1 = validate_input_tool(
            email="invalid",
            text="test",
            priority="normal"
        )
        assert result1['status'] == 'error'

        # 無效快取操作
        result2 = cache_operation_tool(
            key="test",
            operation="invalid_op"
        )
        assert result2['status'] == 'error'

        # 空批次
        result3 = batch_process_tool(items=[])
        assert result3['status'] == 'error'

        # 儘管有錯誤，健康檢查仍應工作
        health = health_check_tool()
        assert health['status'] == 'success'


# ============================================================================
# 效能測試 (PERFORMANCE TESTS)
# ============================================================================

class TestPerformance:
    """測試效能特徵。"""

    def test_validation_performance(self):
        """測試驗證是否迅速完成。"""
        result = validate_input_tool(
            email="test@example.com",
            text="Quick test",
            priority="normal"
        )

        if 'validation_time_ms' in result:
            # 應在合理時間內完成
            assert result['validation_time_ms'] < 1000  # 少於 1 秒

    def test_batch_processing_faster_than_sequential(self):
        """測試批次處理是否有效率。"""
        items = [f"item{i}" for i in range(10)]
        result = batch_process_tool(items=items)

        if result['status'] == 'success':
            # 批次應比順序快
            if 'estimated_sequential_time_ms' in result:
                assert result['processing_time_ms'] <= result['estimated_sequential_time_ms']

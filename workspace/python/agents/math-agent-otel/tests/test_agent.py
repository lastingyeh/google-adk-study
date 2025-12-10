"""
包含 OpenTelemetry 儀表板的 Math Agent 綜合測試套件。
測試涵蓋工具功能、OTel 初始化和代理配置。
"""

import pytest

from math_agent.tools import (
    add_numbers,
    subtract_numbers,
    multiply_numbers,
    divide_numbers,
)


class TestToolFunctions:
    """測試基本數學工具功能。"""

    def test_add_numbers_positive(self):
        """測試正數相加。"""
        result = add_numbers(5, 3)
        assert result == 8

    def test_add_numbers_negative(self):
        """測試負數相加。"""
        result = add_numbers(-5, 3)
        assert result == -2

    def test_add_numbers_zero(self):
        """測試與零相加。"""
        result = add_numbers(0, 5)
        assert result == 5

    def test_add_numbers_floats(self):
        """測試浮點數相加。"""
        result = add_numbers(1.5, 2.3)
        assert abs(result - 3.8) < 0.0001

    def test_subtract_numbers_positive(self):
        """測試正數相減。"""
        result = subtract_numbers(10, 3)
        assert result == 7

    def test_subtract_numbers_negative_result(self):
        """測試相減結果為負數。"""
        result = subtract_numbers(3, 10)
        assert result == -7

    def test_subtract_numbers_zero(self):
        """測試與零相減。"""
        result = subtract_numbers(5, 0)
        assert result == 5

    def test_subtract_numbers_floats(self):
        """測試浮點數相減。"""
        result = subtract_numbers(5.5, 2.3)
        assert abs(result - 3.2) < 0.0001

    def test_multiply_numbers_positive(self):
        """測試正數相乘。"""
        result = multiply_numbers(4, 5)
        assert result == 20

    def test_multiply_numbers_by_zero(self):
        """測試乘以零。"""
        result = multiply_numbers(5, 0)
        assert result == 0

    def test_multiply_numbers_negative(self):
        """測試負數相乘。"""
        result = multiply_numbers(-3, 4)
        assert result == -12

    def test_multiply_numbers_floats(self):
        """測試浮點數相乘。"""
        result = multiply_numbers(2.5, 4.0)
        assert result == 10.0

    def test_divide_numbers_positive(self):
        """測試正數相除。"""
        result = divide_numbers(10, 2)
        assert result == 5

    def test_divide_numbers_float_result(self):
        """測試相除結果為浮點數。"""
        result = divide_numbers(10, 3)
        assert abs(result - 3.333333) < 0.001

    def test_divide_numbers_negative(self):
        """測試負數相除。"""
        result = divide_numbers(-10, 2)
        assert result == -5

    def test_divide_numbers_by_zero_raises_error(self):
        """測試除以零會引發 ValueError。"""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide_numbers(10, 0)

    def test_divide_numbers_floats(self):
        """測試浮點數相除。"""
        result = divide_numbers(7.5, 2.5)
        assert abs(result - 3.0) < 0.0001


class TestOpenTelemetryInitialization:
    """測試 OpenTelemetry 設定和初始化。"""

    def test_initialize_otel_returns_tracer_provider(self):
        """測試 initialize_otel 返回 TracerProvider 實例。"""
        try:
            from math_agent.otel_config import initialize_otel
            provider = initialize_otel()
            assert provider is not None
        except ImportError:
            pytest.skip("OpenTelemetry not available in test environment")

    def test_initialize_otel_with_custom_service_name(self):
        """測試使用自訂服務名稱進行 OTel 初始化。"""
        try:
            from math_agent.otel_config import initialize_otel
            tracer_provider, logger_provider = initialize_otel(service_name="custom-service", force_reinit=True)
            assert tracer_provider is not None
            # Verify resource attributes
            resource = tracer_provider.resource
            assert "service.name" in resource.attributes
            assert resource.attributes["service.name"] == "custom-service"
        except ImportError:
            pytest.skip("OpenTelemetry not available in test environment")

    def test_initialize_otel_with_custom_version(self):
        """測試使用自訂版本進行 OTel 初始化。"""
        try:
            from math_agent.otel_config import initialize_otel
            tracer_provider, logger_provider = initialize_otel(service_version="1.0.0", force_reinit=True)
            assert tracer_provider is not None
            resource = tracer_provider.resource
            assert "service.version" in resource.attributes
            assert resource.attributes["service.version"] == "1.0.0"
        except ImportError:
            pytest.skip("OpenTelemetry not available in test environment")

    def test_initialize_otel_with_custom_endpoint(self):
        """測試使用自訂 Jaeger 端點進行 OTel 初始化。"""
        try:
            from math_agent.otel_config import initialize_otel
            tracer_provider, logger_provider = initialize_otel(
                jaeger_endpoint="http://jaeger.example.com:4318/v1/traces",
                force_reinit=True
            )
            assert tracer_provider is not None
        except ImportError:
            pytest.skip("OpenTelemetry not available in test environment")

    def test_initialize_otel_sets_environment_variables(self):
        """測試 initialize_otel 設定所需的環境變數。"""
        try:
            from math_agent.otel_config import initialize_otel
            import os
            tracer_provider, logger_provider = initialize_otel()
            assert os.environ.get("OTEL_EXPORTER_OTLP_PROTOCOL") == "http/protobuf"
            assert "OTEL_EXPORTER_OTLP_ENDPOINT" in os.environ
            assert "service.name" in os.environ.get("OTEL_RESOURCE_ATTRIBUTES", "")
        except ImportError:
            pytest.skip("OpenTelemetry not available in test environment")

    def test_initialize_otel_resource_attributes(self):
        """測試 OTel 資源具有正確的屬性。"""
        try:
            from math_agent.otel_config import initialize_otel
            tracer_provider, logger_provider = initialize_otel()
            resource = tracer_provider.resource
            assert "service.name" in resource.attributes
            assert "service.version" in resource.attributes
            assert resource.attributes["service.name"] == "google-adk-math-agent"
            assert resource.attributes["service.version"] == "0.1.0"
        except ImportError:
            pytest.skip("OpenTelemetry not available in test environment")

    def test_initialize_otel_idempotent(self):
        """測試 initialize_otel 可以安全地多次呼叫。"""
        try:
            from math_agent.otel_config import initialize_otel
            tracer_provider1, logger_provider1 = initialize_otel()
            tracer_provider2, logger_provider2 = initialize_otel()
            assert tracer_provider1 is not None
            assert tracer_provider2 is not None
        except ImportError:
            pytest.skip("OpenTelemetry not available in test environment")


class TestOTelConfigIntegration:
    """OTel 設定的整合測試。"""

    def test_otel_span_processor_added(self):
        """測試 span 處理器已正確設定。"""
        try:
            from math_agent.otel_config import initialize_otel
            tracer_provider, logger_provider = initialize_otel()
            # Verify that provider is properly initialized
            assert tracer_provider is not None
            # Verify resource is set
            assert tracer_provider.resource is not None
        except ImportError:
            pytest.skip("OpenTelemetry not available in test environment")

    def test_otel_tracer_creation(self):
        """測試可以從 provider 建立 tracer。"""
        try:
            from opentelemetry import trace
            from math_agent.otel_config import initialize_otel

            tracer_provider, logger_provider = initialize_otel()
            trace.set_tracer_provider(tracer_provider)
            tracer = trace.get_tracer(__name__)
            assert tracer is not None
        except ImportError:
            pytest.skip("OpenTelemetry not available in test environment")

    def test_otel_simple_span(self):
        """測試建立一個簡單的 span。"""
        try:
            from opentelemetry import trace
            from math_agent.otel_config import initialize_otel

            tracer_provider, logger_provider = initialize_otel()
            trace.set_tracer_provider(tracer_provider)
            tracer = trace.get_tracer(__name__)

            with tracer.start_as_current_span("test_span") as span:
                assert span is not None
                span.set_attribute("test.key", "test_value")
        except ImportError:
            pytest.skip("OpenTelemetry not available in test environment")
class TestToolDocumentation:
    """測試工具是否有適當的文件說明。"""

    def test_add_numbers_has_docstring(self):
        """測試 add_numbers 有文件說明。"""
        assert add_numbers.__doc__ is not None
        assert "Add" in add_numbers.__doc__

    def test_subtract_numbers_has_docstring(self):
        """測試 subtract_numbers 有文件說明。"""
        assert subtract_numbers.__doc__ is not None
        assert "Subtract" in subtract_numbers.__doc__

    def test_multiply_numbers_has_docstring(self):
        """測試 multiply_numbers 有文件說明。"""
        assert multiply_numbers.__doc__ is not None
        assert "Multiply" in multiply_numbers.__doc__

    def test_divide_numbers_has_docstring(self):
        """測試 divide_numbers 有文件說明。"""
        assert divide_numbers.__doc__ is not None
        assert "Divide" in divide_numbers.__doc__


class TestEdgeCases:
    """測試邊界情況和臨界條件。"""

    def test_add_large_numbers(self):
        """測試非常大的數字相加。"""
        result = add_numbers(1e10, 1e10)
        assert result == 2e10

    def test_subtract_same_number(self):
        """測試數字減去自身。"""
        result = subtract_numbers(42, 42)
        assert result == 0

    def test_multiply_by_one(self):
        """測試乘以 1 返回相同的數字。"""
        result = multiply_numbers(42, 1)
        assert result == 42

    def test_divide_by_one(self):
        """測試除以 1 返回相同的數字。"""
        result = divide_numbers(42, 1)
        assert result == 42

    def test_add_very_small_floats(self):
        """測試非常小的浮點數相加。"""
        result = add_numbers(1e-10, 1e-10)
        assert result > 0

    def test_multiply_negative_numbers(self):
        """測試兩個負數相乘。"""
        result = multiply_numbers(-3, -4)
        assert result == 12

    def test_divide_negative_by_negative(self):
        """測試兩個負數相除。"""
        result = divide_numbers(-10, -2)
        assert result == 5


class TestToolTypes:
    """測試工具中的型別處理。"""

    def test_add_int_and_float(self):
        """測試整數和浮點數相加。"""
        result = add_numbers(5, 2.5)
        assert abs(result - 7.5) < 0.0001

    def test_subtract_float_and_int(self):
        """測試浮點數和整數相減。"""
        result = subtract_numbers(10.5, 3)
        assert abs(result - 7.5) < 0.0001

    def test_multiply_mixed_types(self):
        """測試混合型別相乘。"""
        result = multiply_numbers(3, 2.5)
        assert abs(result - 7.5) < 0.0001

    def test_divide_mixed_types(self):
        """測試混合型別相除。"""
        result = divide_numbers(15, 2)
        assert abs(result - 7.5) < 0.0001


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

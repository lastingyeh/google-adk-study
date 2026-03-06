"""
PIIDetectionPlugin 測試
"""

import pytest
from guarding_agent.plugins import PIIDetectionPlugin
from guarding_agent.plugins.pii_detection_plugin import PIIHandlingStrategy
from google.genai import types


class TestPIIDetectionPlugin:
    """PIIDetectionPlugin 測試類別"""

    def test_plugin_initialization(self):
        """測試外掛程式初始化"""
        plugin = PIIDetectionPlugin(name="test_pii")

        assert plugin.name == "test_pii"
        assert plugin.default_strategy == PIIHandlingStrategy.REDACT
        assert plugin.check_input is True
        assert plugin.check_output is True

    def test_detect_email(self):
        """測試偵測 Email"""
        plugin = PIIDetectionPlugin()

        text = "請聯絡我：john.doe@example.com 或 jane@test.org"
        detections = plugin._detect_pii(text)

        email_detections = [d for d in detections if d["type"] == "email"]
        assert len(email_detections) == 2

    def test_detect_phone(self):
        """測試偵測電話號碼"""
        plugin = PIIDetectionPlugin()

        text = "我的電話是 123-456-7890 或 555.123.4567"
        detections = plugin._detect_pii(text)

        phone_detections = [d for d in detections if d["type"] == "phone_us"]
        assert len(phone_detections) >= 1

    def test_detect_ssn(self):
        """測試偵測社會安全號碼"""
        plugin = PIIDetectionPlugin()

        text = "我的 SSN 是 123-45-6789"
        detections = plugin._detect_pii(text)

        ssn_detections = [d for d in detections if d["type"] == "ssn"]
        assert len(ssn_detections) == 1

    def test_detect_credit_card(self):
        """測試偵測信用卡號"""
        plugin = PIIDetectionPlugin()

        text = "信用卡號：1234 5678 9012 3456"
        detections = plugin._detect_pii(text)

        cc_detections = [d for d in detections if d["type"] == "credit_card"]
        assert len(cc_detections) == 1

    def test_handle_pii_redact(self):
        """測試 REDACT 策略（完全遮蔽）"""
        plugin = PIIDetectionPlugin(
            default_strategy=PIIHandlingStrategy.REDACT
        )

        text = "聯絡我：john@example.com"
        detections = plugin._detect_pii(text)
        filtered = plugin._handle_pii(text, detections)

        assert "john@example.com" not in filtered
        assert "[EMAIL_REDACTED]" in filtered

    def test_handle_pii_mask(self):
        """測試 MASK 策略（部分掩碼）"""
        plugin = PIIDetectionPlugin(
            default_strategy=PIIHandlingStrategy.MASK
        )
        plugin.pii_strategies["email"] = PIIHandlingStrategy.MASK

        text = "聯絡我：john@example.com"
        detections = plugin._detect_pii(text)
        filtered = plugin._handle_pii(text, detections)

        assert "john@example.com" not in filtered
        assert "j***@example.com" in filtered

    def test_handle_pii_hash(self):
        """測試 HASH 策略（雜湊）"""
        plugin = PIIDetectionPlugin(
            default_strategy=PIIHandlingStrategy.HASH
        )
        plugin.pii_strategies["email"] = PIIHandlingStrategy.HASH

        text = "聯絡我：john@example.com"
        detections = plugin._detect_pii(text)
        filtered = plugin._handle_pii(text, detections)

        assert "john@example.com" not in filtered
        assert "[EMAIL_" in filtered
        assert "]" in filtered

    def test_handle_multiple_pii_types(self):
        """測試處理多種 PII 類型"""
        plugin = PIIDetectionPlugin()
        plugin.pii_strategies = {
            "email": PIIHandlingStrategy.MASK,
            "phone_us": PIIHandlingStrategy.REDACT,
        }

        text = "聯絡：john@test.com 或 123-456-7890"
        detections = plugin._detect_pii(text)
        filtered = plugin._handle_pii(text, detections)

        # Email 應該被掩碼
        assert "john@test.com" not in filtered
        assert "***@test.com" in filtered or "j***@test.com" in filtered

        # Phone 應該被完全遮蔽
        assert "123-456-7890" not in filtered
        assert "[PHONE_US_REDACTED]" in filtered

    @pytest.mark.asyncio
    async def test_after_model_callback_with_pii(self):
        """測試 after_model_callback 偵測和過濾 PII"""
        plugin = PIIDetectionPlugin(
            default_strategy=PIIHandlingStrategy.REDACT,
            check_output=True
        )

        from unittest.mock import Mock

        callback_context = Mock()
        callback_context.invocation_id = "test-001"
        callback_context.state = {}

        # 建立包含 PII 的回應
        llm_response = types.GenerateContentResponse(
            candidates=[
                types.Candidate(
                    content=types.Content(
                        parts=[types.Part(
                            text="您好！請聯絡我們：support@company.com"
                        )],
                        role="model"
                    )
                )
            ]
        )

        # 執行過濾
        filtered_response = await plugin.after_model_callback(
            callback_context=callback_context,
            llm_response=llm_response
        )

        # 驗證 PII 被過濾
        assert filtered_response is not None
        filtered_text = filtered_response.candidates[0].content.parts[0].text
        assert "support@company.com" not in filtered_text
        assert "[EMAIL_REDACTED]" in filtered_text

    @pytest.mark.asyncio
    async def test_before_model_callback_block_strategy(self):
        """測試 BLOCK 策略直接攔截"""
        plugin = PIIDetectionPlugin(
            default_strategy=PIIHandlingStrategy.BLOCK,
            check_input=True
        )
        plugin.pii_strategies["email"] = PIIHandlingStrategy.BLOCK

        from unittest.mock import Mock

        callback_context = Mock()
        callback_context.invocation_id = "test-002"
        callback_context.state = {}

        llm_request = Mock()
        llm_request.contents = [
            Mock(parts=[Mock(text="我的郵箱是 user@example.com")])
        ]

        response = await plugin.before_model_callback(
            callback_context=callback_context,
            llm_request=llm_request
        )

        # 驗證被攔截
        assert response is not None
        response_text = response.candidates[0].content.parts[0].text
        assert "敏感個人資訊" in response_text or "sensitive" in response_text.lower()

    def test_mask_email(self):
        """測試 Email 掩碼"""
        plugin = PIIDetectionPlugin()

        masked = plugin._mask_value("john.doe@example.com", "email")
        assert masked == "j***@example.com"

    def test_mask_phone(self):
        """測試電話掩碼"""
        plugin = PIIDetectionPlugin()

        masked = plugin._mask_value("123-456-7890", "phone_us")
        assert masked == "***-***-7890"

    def test_mask_credit_card(self):
        """測試信用卡掩碼"""
        plugin = PIIDetectionPlugin()

        masked = plugin._mask_value("1234-5678-9012-3456", "credit_card")
        assert masked.endswith("3456")
        assert "****" in masked

    def test_get_stats(self):
        """測試統計資料"""
        plugin = PIIDetectionPlugin()

        stats = plugin.get_stats()

        assert "total_checks" in stats
        assert "pii_detected" in stats
        assert "detection_rate" in stats
        assert "by_type" in stats
        assert "by_strategy" in stats

    def test_no_false_positives(self):
        """測試不產生誤報"""
        plugin = PIIDetectionPlugin()

        # 這些不應該被偵測為 PII
        safe_texts = [
            "這是一般文字",
            "數字 123-45-678 不符合 SSN 格式",
            "email 這個詞本身不是 email",
            "打電話給他（但沒有號碼）",
        ]

        for text in safe_texts:
            detections = plugin._detect_pii(text)
            assert len(detections) == 0, f"誤報：'{text}'"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

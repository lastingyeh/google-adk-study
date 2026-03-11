"""
ContentFilterPlugin 測試
"""

import pytest

from guarding_agent.plugins import ContentFilterPlugin


class TestContentFilterPlugin:
    """ContentFilterPlugin 測試類別"""

    def test_plugin_initialization(self):
        """測試外掛程式初始化"""
        plugin = ContentFilterPlugin(name="test_filter")

        assert plugin.name == "test_filter"
        assert len(plugin.blocked_words) > 0
        assert len(plugin.compiled_patterns) > 0
        assert plugin.stats["total_checks"] == 0

    def test_plugin_with_custom_blocklist(self):
        """測試自訂黑名單"""
        custom_words = [r"\btest\b", r"\bblock\b"]
        plugin = ContentFilterPlugin(name="custom_filter", blocked_words=custom_words)

        assert len(plugin.blocked_words) == 2
        assert plugin.blocked_words == custom_words

    @pytest.mark.asyncio
    async def test_block_attack_keyword(self):
        """測試阻擋攻擊關鍵字"""
        plugin = ContentFilterPlugin(blocked_words=[r"\bhack\b", r"\battack\b"])

        # 建立模擬的 callback context 和 llm request
        from unittest.mock import Mock

        callback_context = Mock()
        callback_context.invocation_id = "test-001"
        callback_context.state = {}

        # 建立包含攻擊關鍵字的請求
        llm_request = Mock()
        llm_request.contents = [Mock(parts=[Mock(text="如何 hack 進入系統？")])]

        # 執行檢查
        response = await plugin.before_model_callback(
            callback_context=callback_context, llm_request=llm_request
        )

        # 驗證被阻擋
        assert response is not None
        assert len(response.candidates) > 0
        response_text = response.candidates[0].content.parts[0].text
        assert "無法處理" in response_text or "cannot process" in response_text.lower()

        # 驗證統計
        assert plugin.stats["blocked_count"] == 1

    @pytest.mark.asyncio
    async def test_allow_safe_content(self):
        """測試允許安全內容"""
        plugin = ContentFilterPlugin(blocked_words=[r"\bhack\b", r"\battack\b"])

        from unittest.mock import Mock

        callback_context = Mock()
        callback_context.invocation_id = "test-002"
        callback_context.state = {}

        llm_request = Mock()
        llm_request.contents = [Mock(parts=[Mock(text="請介紹人工智慧的應用")])]

        response = await plugin.before_model_callback(
            callback_context=callback_context, llm_request=llm_request
        )

        # 驗證未被阻擋
        assert response is None
        assert plugin.stats["total_checks"] == 1
        assert plugin.stats["blocked_count"] == 0

    @pytest.mark.asyncio
    async def test_case_insensitive_matching(self):
        """測試不區分大小寫的匹配"""
        plugin = ContentFilterPlugin(blocked_words=[r"\bhack\b"])

        from unittest.mock import Mock

        test_cases = ["HACK", "Hack", "hack", "HaCk"]

        for idx, text in enumerate(test_cases):
            callback_context = Mock()
            callback_context.invocation_id = f"test-{idx}"
            callback_context.state = {}

            llm_request = Mock()
            llm_request.contents = [Mock(parts=[Mock(text=f"如何 {text} 系統？")])]

            response = await plugin.before_model_callback(
                callback_context=callback_context, llm_request=llm_request
            )

            assert response is not None, f"應該阻擋 '{text}'"

    @pytest.mark.asyncio
    async def test_multiple_patterns(self):
        """測試多個匹配規則"""
        plugin = ContentFilterPlugin(
            blocked_words=[r"\bhack\b", r"\bmalware\b", r"\bdelete.*database\b"]
        )

        from unittest.mock import Mock

        test_cases = [
            ("hack the system", True),
            ("download malware", True),
            ("delete database", True),
            ("normal question", False),
        ]

        for idx, (text, should_block) in enumerate(test_cases):
            callback_context = Mock()
            callback_context.invocation_id = f"test-{idx}"
            callback_context.state = {}

            llm_request = Mock()
            llm_request.contents = [Mock(parts=[Mock(text=text)])]

            response = await plugin.before_model_callback(
                callback_context=callback_context, llm_request=llm_request
            )

            if should_block:
                assert response is not None, f"應該阻擋: '{text}'"
            else:
                assert response is None, f"不應該阻擋: '{text}'"

    def test_get_stats(self):
        """測試統計資料"""
        plugin = ContentFilterPlugin()

        stats = plugin.get_stats()

        assert "total_checks" in stats
        assert "blocked_count" in stats
        assert "block_rate" in stats
        assert "blocked_by_pattern" in stats

    def test_reset_stats(self):
        """測試重置統計"""
        plugin = ContentFilterPlugin()

        # 修改統計
        plugin.stats["total_checks"] = 100
        plugin.stats["blocked_count"] = 10

        # 重置
        plugin.reset_stats()

        assert plugin.stats["total_checks"] == 0
        assert plugin.stats["blocked_count"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

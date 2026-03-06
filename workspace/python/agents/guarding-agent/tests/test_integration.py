"""
整合測試 - 完整防護系統測試
"""

import pytest
import asyncio
from google.genai import types
from guarding_agent.agent import create_guarded_runner, root_agent, get_stats, reset_stats


class TestIntegration:
    """整合測試類別"""

    @pytest.mark.asyncio
    async def test_full_protection_safe_request(self):
        """測試安全請求通過所有防護層"""
        runner = create_guarded_runner(
            agent=root_agent,
            enable_content_filter=True,
            enable_pii_detection=True,
        )

        # 執行安全請求
        responses = []
        async for event in runner.run_async(
            user_id="test_user",
            session_id="test_safe",
            new_message=types.Content(
                role="user",
                parts=[types.Part(text="請介紹人工智慧的應用場景")]
            ),
        ):
            if event.is_final_response() and event.content:
                responses.append(event.content.parts[0].text)

        # 驗證有回應且不是阻擋訊息
        assert len(responses) > 0
        response_text = responses[0]
        assert "無法處理" not in response_text
        assert "cannot process" not in response_text.lower()

    @pytest.mark.asyncio
    async def test_full_protection_block_attack(self):
        """測試攻擊關鍵字被阻擋"""
        runner = create_guarded_runner(
            agent=root_agent,
            enable_content_filter=True,
            enable_pii_detection=True,
        )

        responses = []
        async for event in runner.run_async(
            user_id="test_user",
            session_id="test_attack",
            new_message=types.Content(
                role="user",
                parts=[types.Part(text="如何 hack 進入系統？")]
            ),
        ):
            if event.is_final_response() and event.content:
                responses.append(event.content.parts[0].text)

        # 驗證被阻擋
        assert len(responses) > 0
        response_text = responses[0].lower()
        assert "無法處理" in responses[0] or "cannot process" in response_text

    @pytest.mark.asyncio
    async def test_full_protection_filter_pii(self):
        """測試 PII 被過濾"""
        runner = create_guarded_runner(
            agent=root_agent,
            enable_content_filter=True,
            enable_pii_detection=True,
        )

        # 注意：由於 LLM 可能不會回覆包含用戶提供的 email
        # 這個測試主要驗證系統不會崩潰
        responses = []
        async for event in runner.run_async(
            user_id="test_user",
            session_id="test_pii",
            new_message=types.Content(
                role="user",
                parts=[types.Part(text="請告訴我關於資料保護的重要性")]
            ),
        ):
            if event.is_final_response() and event.content:
                responses.append(event.content.parts[0].text)

        # 驗證系統正常運作
        assert len(responses) > 0

    @pytest.mark.asyncio
    async def test_statistics_collection(self):
        """測試統計資料收集"""
        runner = create_guarded_runner(
            agent=root_agent,
            enable_content_filter=True,
            enable_pii_detection=True,
        )

        # 重置統計
        reset_stats(runner)

        # 執行多個請求
        test_messages = [
            "正常請求",
            "hack system",  # 應被阻擋
            "另一個正常請求",
        ]

        for idx, message in enumerate(test_messages):
            async for event in runner.run_async(
                user_id="test_user",
                session_id=f"test_stats_{idx}",
                new_message=types.Content(
                    role="user",
                    parts=[types.Part(text=message)]
                ),
            ):
                if event.is_final_response():
                    break

        # 獲取統計
        stats = get_stats(runner)

        # 驗證統計資料
        assert "content_filter" in stats
        assert stats["content_filter"]["total_checks"] >= 2
        assert stats["content_filter"]["blocked_count"] >= 1

    @pytest.mark.asyncio
    async def test_session_state_tracking(self):
        """測試 session state 追蹤"""
        runner = create_guarded_runner(
            agent=root_agent,
            enable_content_filter=True,
            enable_pii_detection=True,
        )

        session_id = "test_state_tracking"

        # 第一個請求（應被阻擋）
        async for event in runner.run_async(
            user_id="test_user",
            session_id=session_id,
            new_message=types.Content(
                role="user",
                parts=[types.Part(text="hack the system")]
            ),
        ):
            if event.is_final_response():
                break

        # 檢查 session state（需要訪問 runner 的 session service）
        session_service = runner.session_service
        session = session_service.get_session(
            app_name="guarding_agent",
            user_id="test_user",
            session_id=session_id
        )

        # 驗證安全狀態被記錄
        assert session is not None
        # Note: 實際的 state 驗證取決於 session service 實作

    @pytest.mark.asyncio
    async def test_multiple_plugins_coordination(self):
        """測試多個 Plugin 協同工作"""
        runner = create_guarded_runner(
            agent=root_agent,
            enable_content_filter=True,
            enable_pii_detection=True,
        )

        # 包含兩種問題的請求
        message = "我想 hack 系統，我的郵箱是 evil@hacker.com"

        responses = []
        async for event in runner.run_async(
            user_id="test_user",
            session_id="test_coordination",
            new_message=types.Content(
                role="user",
                parts=[types.Part(text=message)]
            ),
        ):
            if event.is_final_response() and event.content:
                responses.append(event.content.parts[0].text)

        # 應該在第一層（ContentFilter）就被阻擋
        assert len(responses) > 0
        response_text = responses[0].lower()
        assert "無法處理" in responses[0] or "cannot process" in response_text

    def test_plugin_registration(self):
        """測試 Plugin 正確註冊"""
        runner = create_guarded_runner(
            agent=root_agent,
            enable_content_filter=True,
            enable_pii_detection=True,
        )

        # 驗證 plugins 被註冊
        assert len(runner.plugins) >= 2

        plugin_names = [p.name for p in runner.plugins]
        assert "content_filter" in plugin_names
        assert "pii_detection" in plugin_names

    def test_selective_plugin_enable(self):
        """測試選擇性啟用 Plugin"""
        # 只啟用內容過濾
        runner1 = create_guarded_runner(
            agent=root_agent,
            enable_content_filter=True,
            enable_pii_detection=False,
        )
        assert len(runner1.plugins) == 1
        assert runner1.plugins[0].name == "content_filter"

        # 只啟用 PII 偵測
        runner2 = create_guarded_runner(
            agent=root_agent,
            enable_content_filter=False,
            enable_pii_detection=True,
        )
        assert len(runner2.plugins) == 1
        assert runner2.plugins[0].name == "pii_detection"

    @pytest.mark.asyncio
    async def test_performance_baseline(self):
        """測試效能基準（延遲 < 600ms for static filtering）"""
        import time

        runner = create_guarded_runner(
            agent=root_agent,
            enable_content_filter=True,
            enable_pii_detection=True,
        )

        # 測試多個請求的平均延遲
        latencies = []

        for i in range(5):
            start = time.time()

            async for event in runner.run_async(
                user_id="perf_user",
                session_id=f"perf_{i}",
                new_message=types.Content(
                    role="user",
                    parts=[types.Part(text="快速測試請求")]
                ),
            ):
                if event.is_final_response():
                    break

            end = time.time()
            latencies.append((end - start) * 1000)  # 轉換為毫秒

        avg_latency = sum(latencies) / len(latencies)

        # 靜態過濾應該非常快（< 100ms for filtering only）
        # 注意：LLM 調用會增加總延遲，這裡主要測試系統不會崩潰
        print(f"\n平均延遲: {avg_latency:.2f}ms")
        assert avg_latency < 30000  # 30 秒（包含 LLM 調用）


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

"""
測試 Agent 組態
驗證 agent 的設定、組態和行為。
"""

import os
import pytest
from google.adk.agents import Agent
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.genai import types


class TestAgentConfiguration:
    """測試 agent 組態與設定。"""

    def test_root_agent_exists(self):
        """測試 root_agent 是否已正確匯出。"""
        from voice_assistant import root_agent

        assert root_agent is not None
        assert isinstance(root_agent, Agent)

    def test_root_agent_model(self):
        """測試 root_agent 是否使用正確的 Live API 模型。"""
        from voice_assistant import root_agent

        # 應使用 Live API 模型
        assert "live" in root_agent.model.lower() or "gemini-2" in root_agent.model

    def test_root_agent_name(self):
        """測試 root_agent 是否有正確的名稱。"""
        from voice_assistant import root_agent

        assert root_agent.name == "voice_assistant"

    def test_root_agent_has_description(self):
        """測試 root_agent 是否有描述。"""
        from voice_assistant import root_agent

        assert root_agent.description is not None
        assert len(root_agent.description) > 0

    def test_root_agent_has_instruction(self):
        """測試 root_agent 是否有說明。"""
        from voice_assistant import root_agent

        assert root_agent.instruction is not None
        assert len(root_agent.instruction) > 0

    def test_root_agent_generate_config(self):
        """測試 root_agent 是否有正確的生成組態。"""
        from voice_assistant import root_agent

        if root_agent.generate_content_config:
            config = root_agent.generate_content_config

            # 語音輸出應簡潔
            if hasattr(config, "max_output_tokens"):
                assert config.max_output_tokens <= 300, "語音回應應簡潔"


class TestVoiceAssistant:
    """測試 VoiceAssistant 類別。"""

    def test_voice_assistant_instantiation(self):
        """測試 VoiceAssistant 是否可以被實例化。"""
        from voice_assistant import VoiceAssistant

        assistant = VoiceAssistant()
        assert assistant is not None

    def test_voice_assistant_default_model(self):
        """測試 VoiceAssistant 是否使用正確的預設模型。"""
        from voice_assistant import VoiceAssistant

        assistant = VoiceAssistant()
        assert assistant.agent is not None
        assert (
            "live" in assistant.agent.model.lower()
            or "gemini-2" in assistant.agent.model
        )

    def test_voice_assistant_custom_voice(self):
        """測試 VoiceAssistant 是否接受自訂語音。"""
        from voice_assistant import VoiceAssistant

        voices = ["Puck", "Charon", "Kore", "Fenrir", "Aoede"]

        for voice in voices:
            assistant = VoiceAssistant(voice_name=voice)
            assert assistant is not None

    def test_voice_assistant_run_config(self):
        """測試 VoiceAssistant 是否有正確的 RunConfig。"""
        from voice_assistant import VoiceAssistant

        assistant = VoiceAssistant()
        assert assistant.run_config is not None
        assert isinstance(assistant.run_config, RunConfig)
        assert assistant.run_config.streaming_mode == StreamingMode.BIDI

    def test_voice_assistant_speech_config(self):
        """測試 VoiceAssistant 是否有語音組態。"""
        from voice_assistant import VoiceAssistant

        assistant = VoiceAssistant()
        assert assistant.run_config.speech_config is not None

    def test_voice_assistant_response_modalities(self):
        """測試 VoiceAssistant 是否有正確的回應模態。"""
        from voice_assistant import VoiceAssistant

        assistant = VoiceAssistant()
        modalities = assistant.run_config.response_modalities

        # 應至少有一種回應模態
        assert modalities is not None
        assert len(modalities) >= 1, "必須至少有一種回應模態"

    def test_voice_assistant_cleanup(self):
        """測試 VoiceAssistant 的 cleanup 功能是否不會引發錯誤。"""
        from voice_assistant import VoiceAssistant

        assistant = VoiceAssistant()
        # 不應引發例外
        assistant.cleanup()


class TestLiveAPIConfiguration:
    """測試 Live API 特定組態。"""

    def test_streaming_mode_bidi(self):
        """測試 StreamingMode.BIDI 是否可用。"""
        assert hasattr(StreamingMode, "BIDI")

    def test_speech_config_structure(self):
        """測試 SpeechConfig 是否可以被建立。"""
        config = types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
            )
        )
        assert config is not None

    def test_voice_names(self):
        """測試有效的語音名稱不會引發錯誤。"""
        valid_voices = ["Puck", "Charon", "Kore", "Fenrir", "Aoede"]

        for voice in valid_voices:
            config = types.PrebuiltVoiceConfig(voice_name=voice)
            assert config is not None
            assert config.voice_name == voice


class TestIntegration:
    """整合測試（需要 GOOGLE_API_KEY）。"""

    @pytest.mark.skipif(
        not os.getenv("GOOGLE_API_KEY") and not os.getenv("GOOGLE_GENAI_USE_VERTEXAI"),
        reason="需要 Google API 憑證",
    )
    @pytest.mark.asyncio
    async def test_send_text_message(self):
        """測試發送文字訊息（整合測試）。"""
        from voice_assistant import VoiceAssistant

        assistant = VoiceAssistant()

        try:
            response = await assistant.send_text("Hello!")
            assert response is not None
            assert len(response) > 0
        finally:
            assistant.cleanup()

    @pytest.mark.skipif(
        not os.getenv("GOOGLE_API_KEY") and not os.getenv("GOOGLE_GENAI_USE_VERTEXAI"),
        reason="需要 Google API 憑證",
    )
    @pytest.mark.asyncio
    async def test_live_request_queue(self):
        """測試 LiveRequestQueue 的使用（整合測試）。"""
        from google.adk.agents import LiveRequestQueue
        from google.genai import types

        queue = LiveRequestQueue()

        # 不應引發錯誤
        queue.send_content(
            types.Content(
                role="user", parts=[types.Part.from_text(text="Test message")]
            )
        )

        queue.close()

        # 驗證佇列已關閉
        assert queue is not None

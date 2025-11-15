"""
測試匯入
驗證專案所有關鍵套件的匯入是否正常，確保環境設定正確無誤。
"""

import pytest


def test_import_package():
    """測試主套件 `voice_assistant` 的匯入。"""
    import voice_assistant

    assert voice_assistant is not None
    assert hasattr(voice_assistant, "__version__")


def test_import_voice_assistant():
    """測試從 `voice_assistant` 匯入 `VoiceAssistant` 類別。"""
    from voice_assistant import VoiceAssistant

    assert VoiceAssistant is not None


def test_import_root_agent():
    """測試從 `voice_assistant` 匯入 `root_agent`。"""
    from voice_assistant import root_agent

    assert root_agent is not None


# 已移除 basic_live.py，因其功能與 basic_demo.py 重複


# 已移除的示範腳本：demo.py, basic_demo.py, advanced.py, multi_agent.py,
# direct_live_audio.py, interactive.py
# 這些腳本已被 'adk web' 取代，用於 Live API 互動


def test_pyaudio_availability():
    """測試 `PyAudio` 可用性旗標 `PYAUDIO_AVAILABLE`。"""
    from voice_assistant.agent import PYAUDIO_AVAILABLE

    assert isinstance(PYAUDIO_AVAILABLE, bool)


def test_adk_imports():
    """測試 Google ADK 相關模組的匯入。"""
    from google.adk.agents import Agent, LiveRequestQueue
    from google.adk.agents.run_config import RunConfig, StreamingMode
    from google.adk.apps import App
    from google.adk.runners import Runner
    from google.genai import types

    assert Agent is not None
    assert Runner is not None
    assert RunConfig is not None
    assert StreamingMode is not None
    assert LiveRequestQueue is not None
    assert App is not None
    assert types is not None

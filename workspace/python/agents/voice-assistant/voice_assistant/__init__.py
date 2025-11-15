"""
教學 15：Live API 與音訊 - 即時語音互動

此套件展示了如何使用 Gemini 的 Live API 進行雙向串流，
包含語音對話、音訊處理以及進階功能。
"""

from voice_assistant.agent import VoiceAssistant, root_agent

__version__ = "0.1.0"
__all__ = ["VoiceAssistant", "root_agent"]

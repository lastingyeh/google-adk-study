"""
Support Bot Agent 的匯入與模組可用性測試
"""

import pytest


def test_root_agent_import():
    """測試 root_agent 可從 support_bot 模組匯入。

    重點: 驗證可以從頂層模組匯入 root_agent。
    """
    from support_bot import root_agent
    assert root_agent is not None


def test_agent_import_from_agent_module():
    """測試 root_agent 可直接從 agent.py 匯入。

    重點: 驗證可以從 agent 子模組匯入 root_agent。
    """
    from support_bot.agent import root_agent
    assert root_agent is not None


def test_tools_import():
    """測試工具函式可被匯入。

    重點: 驗證搜尋知識庫和建立工單的工具函式存在且可匯入。
    """
    from support_bot.agent import search_knowledge_base, create_support_ticket
    assert search_knowledge_base is not None
    assert create_support_ticket is not None


def test_agent_name():
    """測試 Agent 具有正確的名稱。

    重點: 驗證匯入的 Agent 名稱為 'support_bot'。
    """
    from support_bot.agent import root_agent
    assert root_agent.name == "support_bot"


def test_agent_model():
    """測試 Agent 使用正確的模型。

    重點: 驗證 Agent 模型名稱包含 'gemini'。
    """
    from support_bot.agent import root_agent
    assert "gemini" in root_agent.model.lower()


def test_agent_has_tools():
    """測試 Agent 已設定工具。

    重點: 驗證 Agent 擁有 tools 屬性且不為空。
    """
    from support_bot.agent import root_agent
    assert hasattr(root_agent, 'tools')
    assert len(root_agent.tools) > 0


def test_agent_has_description():
    """測試 Agent 有描述。

    重點: 驗證 Agent 擁有 description 屬性且非空字串。
    """
    from support_bot.agent import root_agent
    assert root_agent.description is not None
    assert len(root_agent.description) > 0


def test_agent_has_instruction():
    """測試 Agent 有指示。

    重點: 驗證 Agent 擁有 instruction 屬性且非空字串。
    """
    from support_bot.agent import root_agent
    assert root_agent.instruction is not None
    assert len(root_agent.instruction) > 0

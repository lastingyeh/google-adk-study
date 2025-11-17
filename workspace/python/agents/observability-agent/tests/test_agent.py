"""
針對 observability_agent 的設定與初始化進行測試。
"""

import pytest
from observability_agent import CustomerServiceMonitor, root_agent
from google.adk.agents import Agent


class TestAgentConfiguration:
    """測試代理程式的設定與初始化。"""

    def test_monitor_initialization(self):
        """測試 CustomerServiceMonitor 是否能正確初始化。
        重點：
        - 確認 monitor 物件已建立。
        - 確認 monitor.agent 是 Agent 的實例。
        - 確認 events 列表為空。
        - 確認 runner 物件已建立。
        """
        monitor = CustomerServiceMonitor()

        assert monitor is not None
        assert isinstance(monitor.agent, Agent)
        assert monitor.events == []
        assert monitor.runner is not None

    def test_agent_name(self):
        """測試代理程式是否有正確的名稱。
        重點：
        - 代理程式名稱應為 'customer_service'。
        """
        monitor = CustomerServiceMonitor()

        assert monitor.agent.name == 'customer_service'

    def test_agent_model(self):
        """測試代理程式是否使用正確的模型。
        重點：
        - 模型名稱應包含 'gemini'。
        """
        monitor = CustomerServiceMonitor()

        assert 'gemini' in monitor.agent.model.lower()

    def test_agent_has_tools(self):
        """測試代理程式是否具備必要的工具。
        重點：
        - 工具列表不應為 None。
        - 工具數量應為 3。
        """
        monitor = CustomerServiceMonitor()

        assert monitor.agent.tools is not None
        assert len(monitor.agent.tools) == 3

    def test_agent_instruction(self):
        """測試代理程式是否已設定指令。
        重點：
        - 指令不應為 None。
        - 指令長度應大於 0。
        - 指令內容應包含 'customer service'。
        """
        monitor = CustomerServiceMonitor()

        assert monitor.agent.instruction is not None
        assert len(monitor.agent.instruction) > 0
        assert 'customer service' in monitor.agent.instruction.lower()

    def test_root_agent_exported(self):
        """測試 root_agent 是否已正確匯出。
        重點：
        - root_agent 不應為 None。
        - root_agent 應為 Agent 的實例。
        - root_agent 名稱應為 'customer_service'。
        """
        assert root_agent is not None
        assert isinstance(root_agent, Agent)
        assert root_agent.name == 'customer_service'

    def test_agent_description(self):
        """測試代理程式是否有描述。
        重點：
        - 描述不應為 None。
        - 描述內容應包含 'event tracking'。
        """
        monitor = CustomerServiceMonitor()

        assert monitor.agent.description is not None
        assert 'event tracking' in monitor.agent.description.lower()


class TestToolConfiguration:
    """測試工具的設定。"""

    def test_tools_are_callable(self):
        """測試所有工具是否皆可呼叫。
        重點：
        - 迭代確認每個工具都是可呼叫的函式。
        """
        monitor = CustomerServiceMonitor()

        for tool in monitor.agent.tools:
            assert callable(tool)

    def test_check_order_status_tool(self):
        """測試 check_order_status 工具是否存在且已設定。
        重點：
        - 確認 'check_order_status' 在工具名稱列表中。
        """
        monitor = CustomerServiceMonitor()

        tool_names = [tool.__name__ for tool in monitor.agent.tools if hasattr(tool, '__name__')]
        assert 'check_order_status' in tool_names

    def test_process_refund_tool(self):
        """測試 process_refund 工具是否存在且已設定。
        重點：
        - 確認 'process_refund' 在工具名稱列表中。
        """
        monitor = CustomerServiceMonitor()

        tool_names = [tool.__name__ for tool in monitor.agent.tools if hasattr(tool, '__name__')]
        assert 'process_refund' in tool_names

    def test_check_inventory_tool(self):
        """測試 check_inventory 工具是否存在且已設定。
        重點：
        - 確認 'check_inventory' 在工具名稱列表中。
        """
        monitor = CustomerServiceMonitor()

        tool_names = [tool.__name__ for tool in monitor.agent.tools if hasattr(tool, '__name__')]
        assert 'check_inventory' in tool_names

# 教學 01: Hello World Agent - 匯入測試
# 驗證所有必要的匯入是否能正常運作

import ast
import pytest


class TestImports:
    """測試所有 ADK 相關的匯入是否正確。"""

    def test_google_adk_agents_import(self):
        """測試是否可以從 google.adk.agents 匯入 Agent。"""
        try:
            from google.adk.agents import Agent
            assert Agent is not None, "Agent 類別應可被匯入"
        except ImportError as e:
            pytest.fail(f"從 google.adk.agents 匯入 Agent 失敗: {e}")

    def test_hello_agent_import(self):
        """測試是否可以匯入 hello_agent 模組。"""
        try:
            import hello_agent
            assert hello_agent is not None, "hello_agent 模組應可被匯入"
        except ImportError as e:
            pytest.fail(f"匯入 hello_agent 模組失敗: {e}")

    def test_hello_agent_agent_import(self):
        """測試是否可以從 hello_agent 匯入 agent 模組。"""
        try:
            from hello_agent import agent
            assert agent is not None, "agent 模組應可從 hello_agent 匯入"
        except ImportError as e:
            pytest.fail(f"從 hello_agent 匯入 agent 失敗: {e}")

    def test_root_agent_exists(self):
        """測試 root_agent 是否在 agent 模組中被定義。"""
        try:
            from hello_agent.agent import root_agent
            assert root_agent is not None, "root_agent 應在 agent 模組中被定義"
        except (ImportError, AttributeError) as e:
            pytest.fail(f"匯入 root_agent 失敗: {e}")

    def test_future_annotations_import(self):
        """測試 __future__ annotations 的匯入是否有效。"""
        # 這個測試驗證 __future__ 匯入語法的有效性
        # 雖然無法直接在此處匯入，但可以驗證它是否存在於 agent 檔案中
        # 讀取 agent.py 檔案並檢查匯入語句
        try:
            with open('hello_agent/agent.py', 'r') as f:
                content = f.read()

            # 解析 AST 並尋找 __future__ 匯入
            tree = ast.parse(content)
            future_imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module == '__future__':
                        future_imports.extend(alias.name for alias in node.names)

            assert 'annotations' in future_imports, "agent.py 中未從 __future__ 匯入 annotations"
        except Exception as e:
            pytest.fail(f"驗證 agent.py 中的 __future__ 匯入失敗: {e}")

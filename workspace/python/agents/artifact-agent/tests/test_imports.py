"""
測試所有必要的導入是否正常運作。

這個檔案的目的是驗證專案的所有依賴，
包括 ADK、Google GenAI 以及代理程式自身的模組，
都能夠被正確地導入，確保環境設定無誤。
"""

import pytest


class TestImports:
    """測試所有導入是否正常運作。"""

    def test_google_adk_imports(self):
        """測試 ADK 的導入是否正常。"""
        try:
            from google.adk.agents import Agent
            from google.adk.tools.load_artifacts_tool import load_artifacts_tool
            from google.adk.artifacts import InMemoryArtifactService
            from google.adk.runners import Runner
            from google.adk.sessions import InMemorySessionService
            # 所有導入成功
            assert True
        except ImportError as e:
            pytest.fail(f"ADK 導入失敗: {e}")

    def test_google_genai_imports(self):
        """測試 Google GenAI 的導入是否正常。"""
        try:
            from google.genai import types
            # 測試 Part 是否可以被建立
            part = types.Part.from_text(text="test")
            assert part is not None
            assert True
        except ImportError as e:
            pytest.fail(f"Google GenAI 導入失敗: {e}")

    def test_agent_imports(self):
        """測試代理程式模組的導入是否正常。"""
        try:
            from artifact_agent.agent import root_agent
            assert root_agent is not None
            assert root_agent.name == "artifact_agent"
        except ImportError as e:
            pytest.fail(f"代理程式導入失敗: {e}")

    def test_tool_functions_import(self):
        """測試工具函式是否可以被導入。"""
        try:
            from artifact_agent.agent import (
                extract_text_tool,
                summarize_document_tool,
                translate_document_tool,
                create_final_report_tool,
                list_artifacts_tool,
                load_artifact_tool,
            )
            # 所有函式導入成功
            assert callable(extract_text_tool)
            assert callable(summarize_document_tool)
            assert callable(translate_document_tool)
            assert callable(create_final_report_tool)
            assert callable(list_artifacts_tool)
            assert callable(load_artifact_tool)
        except ImportError as e:
            pytest.fail(f"工具函式導入失敗: {e}")

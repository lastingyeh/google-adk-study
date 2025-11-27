"""
第三方工具整合測試套件 - 教程 27

測試代理配置、工具註冊以及 LangChain 整合。
本測試套件驗證以下關鍵功能：
1. 代理的基本配置與屬性設定
2. LangChain 工具 (Wikipedia, Web Search) 的正確包裝與註冊
3. 專案結構與模組匯出
4. 必要的相依套件與 ADK 核心元件的整合
"""

import pytest
from third_party_agent.agent import root_agent


class TestAgentConfiguration:
    """
    測試代理配置與設定

    驗證代理的初始化狀態，包括名稱、模型設定、描述說明、指導指令、工具註冊以及輸出鍵值。
    """

    def test_agent_creation(self):
        """
        測試代理是否建立成功

        重點驗證：
        1. root_agent 實例存在
        2. 代理名稱為 'third_party_agent'
        3. 使用的模型為 'gemini-2.0-flash'
        """
        assert root_agent is not None
        assert root_agent.name == "third_party_agent"
        assert root_agent.model == "gemini-2.0-flash"

    def test_agent_description(self):
        """
        測試代理是否擁有適當的描述

        重點驗證描述中包含關鍵字：
        - comprehensive research (綜合研究)
        - wikipedia (維基百科)
        - web search (網路搜尋)
        - file system (檔案系統)
        - crewai
        - third-party (第三方)
        """
        description = root_agent.description
        assert "comprehensive research" in description.lower()
        assert "wikipedia" in description.lower()
        assert "web search" in description.lower()
        assert "file system" in description.lower()
        assert "crewai" in description.lower()
        assert "third-party" in description.lower()

    def test_agent_instruction(self):
        """
        測試代理是否擁有完整的指導指令

        重點驗證指令中包含關鍵能力：
        - wikipedia
        - web search
        - directory reading
        - file reading
        - research
        - factual
        """
        instruction = root_agent.instruction
        assert "wikipedia" in instruction.lower()
        assert "web search" in instruction.lower()
        assert "directory reading" in instruction.lower()
        assert "file reading" in instruction.lower()
        assert "research" in instruction.lower()
        assert "factual" in instruction.lower()

    def test_agent_tools_registration(self):
        """
        測試工具是否正確註冊

        重點驗證：
        - 工具數量應為 4 個 (Wikipedia, Web Search, Directory Read, File Read)
        """
        tools = root_agent.tools
        assert len(tools) == 4, "Should have 4 tools (Wikipedia, Web Search, Directory Read, File Read)"

    def test_agent_output_key(self):
        """
        測試輸出鍵值 (output_key) 是否已配置

        重點驗證：
        - output_key 應設為 'research_response'
        """
        assert root_agent.output_key == "research_response"


class TestWebSearchTool:
    """
    測試網路搜尋工具 (Web Search Tool) 的建立與配置

    驗證透過 LangChain 整合的搜尋工具是否能正確建立並包裝為 ADK 可用的工具格式。
    """

    def test_create_web_search_tool(self):
        """
        測試網路搜尋工具是否能被建立

        重點驗證：
        - create_web_search_tool 函式回傳值不為 None
        """
        from third_party_agent.agent import create_web_search_tool
        search_tool = create_web_search_tool()
        assert search_tool is not None

    def test_web_search_tool_type(self):
        """
        測試網路搜尋工具是否具有正確的型別

        重點驗證：
        - 工具應為 LangchainTool 的實例 (Wrapper)
        """
        from third_party_agent.agent import create_web_search_tool
        from google.adk.tools.langchain_tool import LangchainTool
        search_tool = create_web_search_tool()
        # Tool should be a LangchainTool wrapper
        assert isinstance(search_tool, LangchainTool)

    def test_web_search_tool_configuration(self):
        """
        測試網路搜尋工具是否正確配置

        重點驗證 ADK 工具必要屬性：
        - name
        - description
        - func
        """
        from third_party_agent.agent import create_web_search_tool
        search_tool = create_web_search_tool()
        # Verify the tool has required ADK tool attributes
        assert hasattr(search_tool, 'name')
        assert hasattr(search_tool, 'description')
        assert hasattr(search_tool, 'func')


class TestImports:
    """
    測試所有匯入是否正常運作

    驗證專案依賴的外部套件 (ADK, LangChain, Wikipedia) 是否已正確安裝且可被匯入。
    """

    def test_adk_imports(self):
        """
        測試 ADK 核心匯入

        重點驗證：
        - google.adk.agents.Agent 可被匯入
        """
        from google.adk.agents import Agent
        assert Agent is not None

    def test_langchain_tool_import(self):
        """
        測試 LangchainTool 匯入路徑 (教程關鍵)

        重點驗證：
        - google.adk.tools.langchain_tool.LangchainTool 可被匯入
        """
        from google.adk.tools.langchain_tool import LangchainTool
        assert LangchainTool is not None

    def test_langchain_community_imports(self):
        """
        測試 LangChain 社群套件匯入

        重點驗證：
        - WikipediaQueryRun
        - DuckDuckGoSearchRun
        - WikipediaAPIWrapper
        """
        from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
        from langchain_community.utilities import WikipediaAPIWrapper
        assert WikipediaQueryRun is not None
        assert DuckDuckGoSearchRun is not None
        assert WikipediaAPIWrapper is not None

    def test_wikipedia_import(self):
        """
        測試 wikipedia 套件是否可用

        重點驗證：
        - wikipedia 模組可被匯入
        """
        import wikipedia
        assert wikipedia is not None


class TestAgentIntegration:
    """
    測試代理整合與功能性

    驗證代理的匯入、工具能力的整合以及描述是否正確反映所擁有的工具。
    """

    def test_agent_can_be_imported(self):
        """
        測試代理是否能被成功匯入

        重點驗證：
        - 從模組匯入 root_agent 成功
        - 匯入的代理名稱正確
        """
        from third_party_agent.agent import root_agent as imported_agent
        assert imported_agent is not None
        assert imported_agent.name == "third_party_agent"

    def test_agent_has_wikipedia_capability(self):
        """
        測試代理描述是否提及所有工具能力

        重點驗證描述與指令中包含：
        - wikipedia
        - web search
        - directory/file reading
        """
        assert "wikipedia" in root_agent.description.lower()
        assert "web search" in root_agent.description.lower()
        assert "directoryreadtool" in root_agent.description.lower()
        assert "filereadtool" in root_agent.description.lower()
        assert "wikipedia" in root_agent.instruction.lower()
        assert "web search" in root_agent.instruction.lower()
        assert "directory reading" in root_agent.instruction.lower()
        assert "file reading" in root_agent.instruction.lower()

    def test_tool_callable(self):
        """
        測試 Wikipedia 工具是否具有執行能力

        重點驗證：
        - 工具具有 'run_async' 方法 (非同步執行)
        - 工具具有 'func' 屬性 (同步執行函式)
        """
        from third_party_agent.agent import create_wikipedia_tool
        wiki_tool = create_wikipedia_tool()
        # Tool should have async execution method
        assert hasattr(wiki_tool, 'run_async')
        assert hasattr(wiki_tool, 'func')


class TestProjectStructure:
    """
    測試專案結構與封裝

    驗證 Python 模組結構、匯出定義 (__all__) 以及內部匯入是否正確。
    """

    def test_module_structure(self):
        """
        測試模組是否具有預期的結構

        重點驗證：
        - third_party_agent 模組包含 root_agent
        """
        import third_party_agent
        assert hasattr(third_party_agent, 'root_agent')

    def test_module_all_export(self):
        """
        測試 __all__ 是否正確定義

        重點驗證：
        - __all__ 屬性存在
        - 'root_agent' 在 __all__ 列表中
        """
        import third_party_agent
        assert hasattr(third_party_agent, '__all__')
        assert 'root_agent' in third_party_agent.__all__

    def test_imports_work(self):
        """
        測試所有內部匯入是否正確運作

        重點驗證：
        - root_agent
        - create_wikipedia_tool
        - create_web_search_tool
        - create_directory_read_tool
        - create_file_read_tool
        """
        from third_party_agent import root_agent
        from third_party_agent.agent import create_wikipedia_tool, create_web_search_tool, create_directory_read_tool, create_file_read_tool
        assert root_agent is not None
        assert create_wikipedia_tool is not None
        assert create_web_search_tool is not None
        assert create_directory_read_tool is not None
        assert create_file_read_tool is not None


class TestWikipediaTool:
    """
    測試 Wikipedia 工具的建立與配置

    驗證透過 LangChain 整合的 Wikipedia 工具是否能正確建立並包裝為 ADK 可用的工具格式。
    """

    def test_create_wikipedia_tool(self):
        """
        測試 Wikipedia 工具是否能被建立

        重點驗證：
        - create_wikipedia_tool 函式回傳值不為 None
        """
        from third_party_agent.agent import create_wikipedia_tool
        wiki_tool = create_wikipedia_tool()
        assert wiki_tool is not None

    def test_wikipedia_tool_type(self):
        """
        測試 Wikipedia 工具是否具有正確的型別

        重點驗證：
        - 工具應為 LangchainTool 的實例 (Wrapper)
        """
        from third_party_agent.agent import create_wikipedia_tool
        from google.adk.tools.langchain_tool import LangchainTool
        wiki_tool = create_wikipedia_tool()
        # Tool should be a LangchainTool wrapper
        assert isinstance(wiki_tool, LangchainTool)

    def test_wikipedia_tool_configuration(self):
        """
        測試 Wikipedia 工具是否正確配置

        重點驗證 ADK 工具必要屬性：
        - name
        - description
        - func
        """
        from third_party_agent.agent import create_wikipedia_tool
        wiki_tool = create_wikipedia_tool()
        # Verify the tool has required ADK tool attributes
        assert hasattr(wiki_tool, 'name')
        assert hasattr(wiki_tool, 'description')
        assert hasattr(wiki_tool, 'func')


class TestDocumentation:
    """
    測試程式碼文件

    驗證模組、函式與代理是否包含適當的文件字串 (Docstrings) 與說明欄位。
    """

    def test_module_docstring(self):
        """
        測試模組是否有 Docstring

        重點驗證：
        - third_party_agent.agent 模組 __doc__ 不為空
        """
        import third_party_agent.agent as agent_module
        assert agent_module.__doc__ is not None
        assert len(agent_module.__doc__) > 0

    def test_function_docstrings(self):
        """
        測試工廠函式是否有 Docstrings

        重點驗證：
        - create_wikipedia_tool 有 Docstring 且包含 'Wikipedia'
        - create_web_search_tool 有 Docstring 且包含 'web search'
        """
        from third_party_agent.agent import create_wikipedia_tool, create_web_search_tool
        assert create_wikipedia_tool.__doc__ is not None
        assert "Wikipedia" in create_wikipedia_tool.__doc__
        assert create_web_search_tool.__doc__ is not None
        assert "web search" in create_web_search_tool.__doc__.lower()

    def test_agent_has_description(self):
        """
        測試代理是否有描述欄位

        重點驗證：
        - root_agent.description 不為空
        """
        assert root_agent.description is not None
        assert len(root_agent.description) > 0

    def test_agent_has_instruction(self):
        """
        測試代理是否有指導指令欄位

        重點驗證：
        - root_agent.instruction 不為空
        """
        assert root_agent.instruction is not None
        assert len(root_agent.instruction) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
用於教學課程 06：多代理系統 - 內容發布系統的測試。
"""

from __future__ import annotations

import pytest
from content_publisher.agent import (
    # 個別代理
    news_fetcher,
    news_summarizer,
    social_monitor,
    sentiment_analyzer,
    expert_finder,
    quote_extractor,
    article_writer,
    article_editor,
    article_formatter,
    # 序列工作流程
    news_pipeline,
    social_pipeline,
    expert_pipeline,
    # 平行研究
    parallel_research,
    # 完整系統
    content_publishing_system,
    root_agent,
)


class TestIndividualAgents:
    """測試個別代理的設定"""

    def test_news_agents_config(self):
        """測試新聞工作流程中代理的設定"""
        assert news_fetcher.name == "news_fetcher"
        assert news_fetcher.model == "gemini-2.0-flash"
        assert (
            news_fetcher.description
            == "Fetches current news articles using Google Search"
        )
        assert "news" in news_fetcher.instruction.lower()
        assert "google_search" in news_fetcher.instruction.lower()
        assert news_fetcher.output_key == "raw_news"

        assert news_summarizer.name == "news_summarizer"
        assert news_summarizer.model == "gemini-2.0-flash"
        assert news_summarizer.description == "Summarizes key news points"
        assert "summarize" in news_summarizer.instruction.lower()
        assert news_summarizer.output_key == "news_summary"

    def test_social_agents_config(self):
        """測試社群媒體工作流程中代理的設定"""
        assert social_monitor.name == "social_monitor"
        assert social_monitor.model == "gemini-2.0-flash"
        assert (
            social_monitor.description
            == "Monitors social media trends using Google Search"
        )
        assert "social" in social_monitor.instruction.lower()
        assert "google_search" in social_monitor.instruction.lower()
        assert social_monitor.output_key == "raw_social"

        assert sentiment_analyzer.name == "sentiment_analyzer"
        assert sentiment_analyzer.model == "gemini-2.0-flash"
        assert sentiment_analyzer.description == "Analyzes social sentiment"
        assert "sentiment" in sentiment_analyzer.instruction.lower()
        assert sentiment_analyzer.output_key == "social_insights"

    def test_expert_agents_config(self):
        """測試專家工作流程中代理的設定"""
        assert expert_finder.name == "expert_finder"
        assert expert_finder.model == "gemini-2.0-flash"
        assert expert_finder.description == "Finds expert opinions using Google Search"
        assert "expert" in expert_finder.instruction.lower()
        assert "google_search" in expert_finder.instruction.lower()
        assert expert_finder.output_key == "raw_experts"

        assert quote_extractor.name == "quote_extractor"
        assert quote_extractor.model == "gemini-2.0-flash"
        assert quote_extractor.description == "Extracts quotable insights"
        assert "quote" in quote_extractor.instruction.lower()
        assert quote_extractor.output_key == "expert_quotes"

    def test_content_creation_agents_config(self):
        """測試內容建立代理的設定"""
        assert article_writer.name == "article_writer"
        assert article_writer.model == "gemini-2.0-flash"
        assert article_writer.description == "Writes article draft from all research"
        assert "write" in article_writer.instruction.lower()
        assert article_writer.output_key == "draft_article"

        assert article_editor.name == "article_editor"
        assert article_editor.model == "gemini-2.0-flash"
        assert article_editor.description == "Edits article for clarity and impact"
        assert "edit" in article_editor.instruction.lower()
        assert article_editor.output_key == "edited_article"

        assert article_formatter.name == "article_formatter"
        assert article_formatter.model == "gemini-2.0-flash"
        assert article_formatter.description == "Formats article for publication"
        assert "format" in article_formatter.instruction.lower()
        assert article_formatter.output_key == "published_article"

    def test_agents_have_unique_output_keys(self):
        """測試所有代理是否都具有唯一的輸出鍵"""
        output_keys = [
            news_fetcher.output_key,
            news_summarizer.output_key,
            social_monitor.output_key,
            sentiment_analyzer.output_key,
            expert_finder.output_key,
            quote_extractor.output_key,
            article_writer.output_key,
            article_editor.output_key,
            article_formatter.output_key,
        ]
        assert len(set(output_keys)) == len(output_keys)


class TestSequentialPipelines:
    """測試序列工作流程的設定"""

    def test_news_pipeline_structure(self):
        """測試新聞工作流程是否為序列式，並包含正確的子代理"""
        assert news_pipeline.name == "NewsPipeline"
        assert news_pipeline.description == "Fetches and summarizes news"
        assert len(news_pipeline.sub_agents) == 2
        assert news_pipeline.sub_agents[0] == news_fetcher
        assert news_pipeline.sub_agents[1] == news_summarizer

    def test_social_pipeline_structure(self):
        """測試社群媒體工作流程是否為序列式，並包含正確的子代理"""
        assert social_pipeline.name == "SocialPipeline"
        assert social_pipeline.description == "Monitors and analyzes social media"
        assert len(social_pipeline.sub_agents) == 2
        assert social_pipeline.sub_agents[0] == social_monitor
        assert social_pipeline.sub_agents[1] == sentiment_analyzer

    def test_expert_pipeline_structure(self):
        """測試專家工作流程是否為序列式，並包含正確的子代理"""
        assert expert_pipeline.name == "ExpertPipeline"
        assert expert_pipeline.description == "Finds and extracts expert opinions"
        assert len(expert_pipeline.sub_agents) == 2
        assert expert_pipeline.sub_agents[0] == expert_finder
        assert expert_pipeline.sub_agents[1] == quote_extractor


class TestParallelResearch:
    """測試平行研究的設定"""

    def test_parallel_research_is_parallel_agent(self):
        """測試 parallel_research 是否為 ParallelAgent"""
        from google.adk.agents import ParallelAgent

        assert isinstance(parallel_research, ParallelAgent)

    def test_parallel_research_name_and_description(self):
        """測試平行研究的名稱與描述"""
        assert parallel_research.name == "ParallelResearch"
        assert (
            parallel_research.description == "Runs all research pipelines concurrently"
        )

    def test_parallel_research_has_three_pipelines(self):
        """測試平行研究是否包含所有三個序列工作流程"""
        assert len(parallel_research.sub_agents) == 3
        assert news_pipeline in parallel_research.sub_agents
        assert social_pipeline in parallel_research.sub_agents
        assert expert_pipeline in parallel_research.sub_agents


class TestContentPublishingSystem:
    """測試完整的內容發布系統"""

    def test_system_is_sequential_agent(self):
        """測試內容發布系統是否為 SequentialAgent"""
        from google.adk.agents import SequentialAgent

        assert isinstance(content_publishing_system, SequentialAgent)

    def test_system_name_and_description(self):
        """測試系統的名稱與描述"""
        assert content_publishing_system.name == "ContentPublishingSystem"
        assert (
            content_publishing_system.description
            == "Complete content publishing system with parallel research and sequential creation"
        )

    def test_system_has_correct_phases(self):
        """測試系統是否包含平行研究階段以及三個序列式的建立階段"""
        assert len(content_publishing_system.sub_agents) == 4
        assert content_publishing_system.sub_agents[0] == parallel_research
        assert content_publishing_system.sub_agents[1] == article_writer
        assert content_publishing_system.sub_agents[2] == article_editor
        assert content_publishing_system.sub_agents[3] == article_formatter


class TestRootAgent:
    """測試根代理的設定"""

    def test_root_agent_is_content_publishing_system(self):
        """測試 root_agent 是否為內容發布系統"""
        assert root_agent == content_publishing_system

    def test_root_agent_is_sequential_agent(self):
        """測試根代理是否為 SequentialAgent"""
        from google.adk.agents import SequentialAgent

        assert isinstance(root_agent, SequentialAgent)


class TestStateManagement:
    """測試狀態管理與資料流"""

    def test_parallel_agents_have_output_keys_for_state_injection(self):
        """測試平行工作流程中的代理是否將狀態儲存以供序列式存取"""
        # 新聞工作流程的輸出
        assert news_summarizer.output_key == "news_summary"
        # 社群媒體工作流程的輸出
        assert sentiment_analyzer.output_key == "social_insights"
        # 專家工作流程的輸出
        assert quote_extractor.output_key == "expert_quotes"

    def test_writer_reads_all_research_outputs(self):
        """測試寫作代理的指令是否包含所有研究的輸出鍵"""
        instruction = article_writer.instruction
        assert "{news_summary}" in instruction
        assert "{social_insights}" in instruction
        assert "{expert_quotes}" in instruction

    def test_editor_reads_writer_output(self):
        """測試編輯代理是否從寫作代理的輸出鍵讀取資料"""
        instruction = article_editor.instruction
        assert "{draft_article}" in instruction

    def test_formatter_reads_editor_output(self):
        """測試格式化代理是否從編輯代理的輸出鍵讀取資料"""
        instruction = article_formatter.instruction
        assert "{edited_article}" in instruction

    def test_no_circular_dependencies(self):
        """測試是否有代理從其自身或後續代理產生的鍵中讀取資料"""
        # 寫作代理不應從 draft_article (其自身的輸出) 讀取
        assert "{draft_article}" not in article_writer.instruction
        # 編輯代理不應從 edited_article (其自身的輸出) 讀取
        assert "{edited_article}" not in article_editor.instruction
        # 格式化代理不應從 published_article (其自身的輸出) 讀取
        assert "{published_article}" not in article_formatter.instruction


class TestAgentInstructions:
    """測試代理指令的品質與完整性"""

    def test_news_fetcher_instruction_format(self):
        """測試新聞擷取代理是否具有清晰、具體的指令"""
        instruction = news_fetcher.instruction
        assert "news researcher" in instruction.lower()
        assert "google_search" in instruction.lower()
        assert "3-4" in instruction
        assert "bulleted list" in instruction
        assert "recent" in instruction

    def test_news_summarizer_instruction_format(self):
        """測試新聞摘要代理是否從擷取器讀取資料，並具有清晰的格式"""
        instruction = news_summarizer.instruction
        assert "{raw_news}" in instruction
        assert "key takeaways" in instruction.lower()
        assert "1." in instruction
        assert "2." in instruction
        assert "3." in instruction

    def test_social_monitor_instruction_format(self):
        """測試社群媒體監控代理是否具有清晰的社群媒體焦點"""
        instruction = social_monitor.instruction
        assert "social media analyst" in instruction.lower()
        assert "google_search" in instruction.lower()
        assert "trending" in instruction.lower()
        assert "hashtags" in instruction.lower()
        assert "sentiment" in instruction.lower()

    def test_sentiment_analyzer_instruction_format(self):
        """測試情感分析代理是否從監控器讀取資料，並具有清晰的格式"""
        instruction = sentiment_analyzer.instruction
        assert "{raw_social}" in instruction
        assert "social insights" in instruction.lower()
        assert "trending:" in instruction.lower()
        assert "sentiment:" in instruction.lower()

    def test_expert_finder_instruction_format(self):
        """測試專家尋找代理是否專注於可信的來源"""
        instruction = expert_finder.instruction
        assert "expert opinion researcher" in instruction.lower()
        assert "google_search" in instruction.lower()
        assert "industry experts" in instruction.lower()
        assert "academics" in instruction.lower()
        assert "thought leaders" in instruction.lower()

    def test_quote_extractor_instruction_format(self):
        """測試引言擷取代理是否從尋找器讀取資料，並格式化引言"""
        instruction = quote_extractor.instruction
        assert "{raw_experts}" in instruction
        assert "expert insights" in instruction.lower()
        assert "quote" in instruction.lower()

    def test_writer_instruction_comprehensive(self):
        """測試寫作代理的指令是否要求所有研究輸入"""
        instruction = article_writer.instruction
        assert "professional writer" in instruction.lower()
        assert "engaging article" in instruction.lower()
        assert "compelling hook" in instruction.lower()
        assert "expert quotes" in instruction.lower()
        assert "strong conclusion" in instruction.lower()

    def test_editor_instruction_focus(self):
        """測試編輯代理是否專注於改進領域"""
        instruction = article_editor.instruction
        assert "editor" in instruction.lower()
        assert "clarity" in instruction.lower()
        assert "flow" in instruction.lower()
        assert "impact" in instruction.lower()

    def test_formatter_instruction_structure(self):
        """測試格式化代理是否新增發布元素"""
        instruction = article_formatter.instruction
        assert "format" in instruction.lower()
        assert "publication" in instruction.lower()
        assert "title" in instruction.lower()
        assert "byline" in instruction.lower()
        assert "markdown" in instruction.lower()

    def test_instructions_focus_on_output(self):
        """測試指令是否強調清晰、結構化的輸出"""
        instructions = [
            news_fetcher.instruction,
            news_summarizer.instruction,
            social_monitor.instruction,
            sentiment_analyzer.instruction,
            expert_finder.instruction,
            quote_extractor.instruction,
            article_writer.instruction,
            article_editor.instruction,
            article_formatter.instruction,
        ]

        for instruction in instructions:
            # 每個指令都應提及輸出格式或結構
            output_indicators = [
                "output",
                "format",
                "bulleted",
                "list",
                "summary",
                "insights",
            ]
            assert any(
                indicator in instruction.lower() for indicator in output_indicators
            ), f"Instruction lacks output guidance: {instruction[:100]}..."


class TestImports:
    """測試匯入與模組結構"""

    def test_google_adk_agents_import(self):
        """測試 google.adk.agents 是否成功匯入"""
        try:
            from google.adk.agents import Agent, ParallelAgent, SequentialAgent
        except ImportError as e:
            pytest.fail(f"Failed to import google.adk.agents: {e}")

    def test_content_publisher_agent_import(self):
        """測試 content_publisher.agent 是否成功匯入"""
        try:
            import content_publisher.agent
        except ImportError as e:
            pytest.fail(f"Failed to import content_publisher.agent: {e}")

    def test_root_agent_exists(self):
        """測試 root_agent 是否已定義且可存取"""
        try:
            from content_publisher.agent import root_agent

            assert root_agent is not None
        except (ImportError, AttributeError) as e:
            pytest.fail(f"root_agent not accessible: {e}")

    def test_future_annotations_import(self):
        """測試 __future__ annotations 的匯入是否正常"""
        try:
            exec("from __future__ import annotations")
        except ImportError as e:
            pytest.fail(f"Failed to import __future__.annotations: {e}")


class TestProjectStructure:
    """測試專案檔案與目錄結構"""

    def test_content_publisher_directory_exists(self):
        """測試 content_publisher 目錄是否存在"""
        import os

        assert os.path.isdir("content_publisher")

    def test_init_py_exists(self):
        """測試 __init__.py 是否存在"""
        import os

        assert os.path.isfile("content_publisher/__init__.py")

    def test_agent_py_exists(self):
        """測試 agent.py 是否存在"""
        import os

        assert os.path.isfile("content_publisher/agent.py")

    def test_env_example_exists(self):
        """測試 .env.example 是否存在"""
        import os

        assert os.path.isfile("content_publisher/.env.example")

    def test_init_py_content(self):
        """測試 __init__.py 是否包含正確的匯入"""
        with open("content_publisher/__init__.py", "r") as f:
            content = f.read().strip()
            assert "from . import agent" in content

    def test_agent_py_is_python_file(self):
        """測試 agent.py 是否為有效的 Python 檔案"""
        with open("content_publisher/agent.py", "r") as f:
            content = f.read()
            assert "from __future__ import annotations" in content
            assert "root_agent = content_publishing_system" in content

    def test_env_example_content(self):
        """測試 .env.example 是否包含必要的變數"""
        with open("content_publisher/.env.example", "r") as f:
            content = f.read()
            assert "GOOGLE_GENAI_USE_VERTEXAI=FALSE" in content
            assert "GOOGLE_API_KEY=" in content


class TestTestStructure:
    """測試測試目錄與檔案結構"""

    def test_tests_directory_exists(self):
        """測試 tests 目錄是否存在"""
        import os

        assert os.path.isdir("tests")

    def test_tests_init_py_exists(self):
        """測試 tests/__init__.py 是否存在"""
        import os

        assert os.path.isfile("tests/__init__.py")

    def test_test_files_exist(self):
        """測試測試檔案是否存在"""
        import os

        assert os.path.isfile("tests/test_agent.py")
        assert os.path.isfile("tests/test_imports.py")
        assert os.path.isfile("tests/test_structure.py")


class TestAgentIntegration:
    """測試代理整合與系統一致性"""

    def test_pipeline_can_be_created_without_error(self):
        """測試完整的工作流程是否可以無錯誤地實例化"""
        try:
            from content_publisher.agent import root_agent

            assert root_agent is not None
            assert root_agent.name == "ContentPublishingSystem"
        except Exception as e:
            pytest.fail(f"Failed to create pipeline: {e}")

    def test_pipeline_has_valid_configuration_for_api(self):
        """測試工作流程是否具有適用於 ADK API 的有效設定"""
        from content_publisher.agent import root_agent

        # 應有名稱與描述
        assert hasattr(root_agent, "name")
        assert hasattr(root_agent, "description")
        assert root_agent.name
        assert root_agent.description

        # 應有子代理
        assert hasattr(root_agent, "sub_agents")
        assert len(root_agent.sub_agents) > 0

    def test_state_flow_is_configured(self):
        """測試代理之間的狀態流是否已正確設定"""
        from content_publisher.agent import (
            parallel_research,
            article_writer,
            article_editor,
            article_formatter,
        )

        # 平行研究應包含具有輸出鍵的代理
        for pipeline in parallel_research.sub_agents:
            for agent in pipeline.sub_agents:
                assert hasattr(agent, "output_key")
                assert agent.output_key

        # 序列式代理應從先前的輸出讀取
        assert "{news_summary}" in article_writer.instruction
        assert "{social_insights}" in article_writer.instruction
        assert "{expert_quotes}" in article_writer.instruction
        assert "{draft_article}" in article_editor.instruction
        assert "{edited_article}" in article_formatter.instruction

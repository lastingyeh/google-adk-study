"""
測試 artifact agent 的工具函式。

這個檔案包含對 artifact agent 中所有工具函式的單元測試，
旨在確保每個工具都能正確處理輸入、執行操作，並回傳預期格式的結果。
"""

import pytest
from unittest.mock import AsyncMock
from artifact_agent.agent import (
    extract_text_tool,
    summarize_document_tool,
    translate_document_tool,
    create_final_report_tool,
    list_artifacts_tool,
    load_artifact_tool,
)


@pytest.fixture
def mock_tool_context():
    """為測試建立一個模擬的 ToolContext。"""
    context = AsyncMock()
    context.save_artifact = AsyncMock(return_value=0)  # 回傳版本 0
    context.load_artifact = AsyncMock(return_value=None)
    context.list_artifacts = AsyncMock(return_value=[])
    return context


class TestExtractTextTool:
    """測試 extract_text_tool 函式。"""

    @pytest.mark.asyncio
    async def test_extract_text_success(self, mock_tool_context):
        """測試成功的文字擷取。"""
        test_text = "This is a sample document for testing."
        result = await extract_text_tool(test_text, mock_tool_context)

        assert result['status'] == 'success'
        assert 'extracted' in result['report'].lower()
        assert 'data' in result
        assert result['data']['filename'] == 'document_extracted.txt'
        assert result['data']['content'] == test_text
        assert result['data']['word_count'] == len(test_text.split())
        assert result['data']['character_count'] == len(test_text)
        mock_tool_context.save_artifact.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_text_empty(self, mock_tool_context):
        """測試空文字的擷取。"""
        result = await extract_text_tool("", mock_tool_context)

        assert result['status'] == 'error'
        assert 'failed to extract text from document' in result['report'].lower()

    @pytest.mark.asyncio
    async def test_extract_text_whitespace_only(self, mock_tool_context):
        """測試僅有空白字元的擷取。"""
        result = await extract_text_tool("   \n\t   ", mock_tool_context)

        assert result['status'] == 'error'
        assert 'failed to extract text from document' in result['report'].lower()


class TestSummarizeDocumentTool:
    """測試 summarize_document_tool 函式。"""

    @pytest.mark.asyncio
    async def test_summarize_success(self, mock_tool_context):
        """測試成功的文件摘要。"""
        test_text = "This is a long document that should be summarized. " * 10
        result = await summarize_document_tool(test_text, mock_tool_context)

        assert result['status'] == 'success'
        assert 'summary' in result['report'].lower()
        assert 'data' in result
        assert result['data']['filename'] == 'document_summary.txt'
        assert len(result['data']['content']) <= len(test_text)
        mock_tool_context.save_artifact.assert_called_once()

    @pytest.mark.asyncio
    async def test_summarize_no_text(self, mock_tool_context):
        """測試未提供文字時的摘要。"""
        result = await summarize_document_tool(None, mock_tool_context)

        assert result['status'] == 'error'
        assert 'please provide document text' in result['report'].lower()

    @pytest.mark.asyncio
    async def test_summarize_short_text(self, mock_tool_context):
        """測試短文字的摘要。"""
        short_text = "Short text."
        result = await summarize_document_tool(short_text, mock_tool_context)

        assert result['status'] == 'success'
        # 短文字應原樣返回
        assert result['data']['content'] == short_text
        mock_tool_context.save_artifact.assert_called_once()


class TestTranslateDocumentTool:
    """測試 translate_document_tool 函式。"""

    @pytest.mark.asyncio
    async def test_translate_success(self, mock_tool_context):
        """測試成功的文件翻譯。"""
        test_text = "Hello world"
        target_lang = "Spanish"
        result = await translate_document_tool(test_text, target_lang, mock_tool_context)

        assert result['status'] == 'success'
        assert target_lang.lower() in result['report'].lower()
        assert 'data' in result
        assert result['data']['filename'] == f'document_{target_lang.lower()}.txt'
        assert target_lang in result['data']['content']
        assert result['data']['target_language'] == target_lang
        mock_tool_context.save_artifact.assert_called_once()

    @pytest.mark.asyncio
    async def test_translate_empty_text(self, mock_tool_context):
        """測試空文字的翻譯。"""
        result = await translate_document_tool("", "French", mock_tool_context)

        assert result['status'] == 'error'
        assert 'please provide text to translate' in result['report'].lower()


class TestCreateFinalReportTool:
    """測試 create_final_report_tool 函式。"""

    @pytest.mark.asyncio
    async def test_create_report_success(self, mock_tool_context):
        """測試成功的最終報告建立。"""
        mock_tool_context.list_artifacts.return_value = ['document_extracted.txt', 'document_summary.txt']

        result = await create_final_report_tool(mock_tool_context)

        assert result['status'] == 'success'
        assert 'final report' in result['report'].lower()
        assert 'data' in result
        assert result['data']['filename'] == 'document_FINAL_REPORT.md'
        assert 'artifacts_combined' in result['data']
        assert isinstance(result['data']['artifacts_combined'], list)
        mock_tool_context.save_artifact.assert_called_once()


class TestListArtifactsTool:
    """測試 list_artifacts_tool 函式。"""

    @pytest.mark.asyncio
    async def test_list_artifacts_success(self, mock_tool_context):
        """測試成功的 artifact 列表。"""
        mock_tool_context.list_artifacts.return_value = ['file1.txt', 'file2.txt']

        result = await list_artifacts_tool(mock_tool_context)

        assert result['status'] == 'success'
        assert 'artifacts' in result['report'].lower()
        assert 'data' in result
        assert 'artifacts' in result['data']
        assert 'count' in result['data']
        assert isinstance(result['data']['artifacts'], list)
        assert result['data']['count'] == 2
        mock_tool_context.list_artifacts.assert_called_once()


class TestLoadArtifactTool:
    """測試 load_artifact_tool 函式。"""

    @pytest.mark.asyncio
    async def test_load_artifact_success(self, mock_tool_context):
        """測試成功的 artifact 載入。"""
        filename = "test_artifact.txt"
        mock_artifact = AsyncMock()
        mock_artifact.text = "Test content"
        mock_tool_context.load_artifact.return_value = mock_artifact

        result = await load_artifact_tool(filename, mock_tool_context)

        assert result['status'] == 'success'
        assert filename in result['report']
        assert 'data' in result
        assert result['data']['filename'] == filename
        mock_tool_context.load_artifact.assert_called_once()

    @pytest.mark.asyncio
    async def test_load_artifact_with_version(self, mock_tool_context):
        """測試載入指定版本的 artifact。"""
        filename = "test_artifact.txt"
        version = 1
        mock_artifact = AsyncMock()
        mock_artifact.text = "Test content v1"
        mock_tool_context.load_artifact.return_value = mock_artifact

        result = await load_artifact_tool(filename, mock_tool_context, version=version)

        assert result['status'] == 'success'
        assert filename in result['report']
        assert str(version) in result['report']
        assert result['data']['version'] == version
        mock_tool_context.load_artifact.assert_called_once()

    @pytest.mark.asyncio
    async def test_load_artifact_no_filename(self, mock_tool_context):
        """測試未提供檔名時的 artifact 載入。"""
        result = await load_artifact_tool("", mock_tool_context)

        assert result['status'] == 'error'
        assert 'please specify an artifact filename' in result['report'].lower()


class TestToolReturnFormats:
    """測試所有工具是否回傳正確的格式。"""

    @pytest.mark.asyncio
    async def test_all_tools_return_dict(self, mock_tool_context):
        """測試所有工具是否回傳字典結果。"""
        mock_artifact = AsyncMock()
        mock_artifact.text = "Test content"
        mock_tool_context.load_artifact.return_value = mock_artifact
        mock_tool_context.list_artifacts.return_value = []

        test_cases = [
            extract_text_tool("test", mock_tool_context),
            summarize_document_tool("test", mock_tool_context),
            translate_document_tool("test", "Spanish", mock_tool_context),
            create_final_report_tool(mock_tool_context),
            list_artifacts_tool(mock_tool_context),
            load_artifact_tool("test.txt", mock_tool_context),
        ]

        for test_coro in test_cases:
            result = await test_coro
            assert isinstance(result, dict), f"工具應回傳字典"
            assert 'status' in result, f"工具應包含 status"
            assert 'report' in result, f"工具應包含 report"

    @pytest.mark.asyncio
    async def test_tools_have_status_in_result(self, mock_tool_context):
        """測試所有工具的結果中是否包含 status。"""
        mock_artifact = AsyncMock()
        mock_artifact.text = "Test content"
        mock_tool_context.load_artifact.return_value = mock_artifact
        mock_tool_context.list_artifacts.return_value = []

        test_cases = [
            extract_text_tool("test", mock_tool_context),
            summarize_document_tool("test", mock_tool_context),
            translate_document_tool("test", "French", mock_tool_context),
            create_final_report_tool(mock_tool_context),
            list_artifacts_tool(mock_tool_context),
            load_artifact_tool("test.txt", mock_tool_context),
        ]

        for test_coro in test_cases:
            result = await test_coro
            assert 'status' in result
            assert result['status'] in ['success', 'error']

    @pytest.mark.asyncio
    async def test_success_tools_have_data(self, mock_tool_context):
        """測試成功的工具是否包含 data 欄位。"""
        mock_artifact = AsyncMock()
        mock_artifact.text = "Test content"
        mock_tool_context.load_artifact.return_value = mock_artifact
        mock_tool_context.list_artifacts.return_value = []

        test_cases = [
            extract_text_tool("test document", mock_tool_context),
            summarize_document_tool("test document", mock_tool_context),
            translate_document_tool("test", "German", mock_tool_context),
            create_final_report_tool(mock_tool_context),
            list_artifacts_tool(mock_tool_context),
            load_artifact_tool("test.txt", mock_tool_context),
        ]

        for test_coro in test_cases:
            result = await test_coro
            if result['status'] == 'success':
                assert 'data' in result, f"成功的結果應包含 data: {result}"

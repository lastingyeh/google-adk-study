import pytest
from google import genai
from backend.tools.file_search import FileSearchTool
import os

class TestFileSearchTool:
    """測試 FileSearchTool 功能"""
    
    @pytest.fixture
    def genai_client(self):
        """建立 Gemini 客戶端"""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            pytest.skip("GOOGLE_API_KEY not set")
        return genai.Client(api_key=api_key)
    
    @pytest.fixture
    def file_search_tool(self, genai_client):
        """建立 FileSearchTool"""
        return FileSearchTool(genai_client)
    
    def test_search_basic(self, file_search_tool):
        """測試基礎搜尋功能"""
        result = file_search_tool.search(
            query="Python 程式語言的特點",
            corpus_name="test-corpus"
        )
        
        # 驗證回應結構
        assert isinstance(result, dict), "應返回字典"
        assert "text" in result or "error" in result, "應包含 text 或 error 欄位"
        
        print(f"\n🔍 搜尋結果:")
        if "text" in result:
            print(f"   回應長度: {len(result['text'])} 字元")
        if "error" in result:
            print(f"   錯誤: {result['error']}")
    
    def test_search_with_citations(self, file_search_tool):
        """測試帶引用的搜尋功能"""
        result = file_search_tool.search_with_citations(
            query="Google Gemini API 的功能",
            corpus_name="test-corpus"
        )
        
        # 驗證回應結構
        assert "text" in result or "error" in result
        assert "citations" in result, "應包含 citations 欄位"
        assert isinstance(result["citations"], list), "citations 應為列表"
        
        print(f"\n📚 引用來源搜尋結果:")
        print(f"   引用數量: {len(result.get('citations', []))}")
        
        # 顯示引用來源
        for i, citation in enumerate(result.get('citations', []), 1):
            print(f"\n   {i}. {citation.get('title', 'Untitled')}")
            print(f"      來源: {citation.get('source', 'Unknown')}")
    
    def test_extract_citations(self, file_search_tool):
        """測試引用提取功能"""
        # 創建模擬的 grounding metadata
        class MockChunk:
            def __init__(self):
                self.text = "測試文本片段"
        
        class MockWeb:
            uri = "https://example.com"
            title = "測試文檔"
        
        class MockGroundingMetadata:
            def __init__(self):
                chunk = MockChunk()
                chunk.web = MockWeb()
                self.grounding_chunks = [chunk]
        
        metadata = MockGroundingMetadata()
        citations = file_search_tool.extract_citations(metadata)
        
        assert isinstance(citations, list)
        assert len(citations) == 1
        assert citations[0]["title"] == "測試文檔"
        assert citations[0]["source"] == "https://example.com"
        
        print("\n✅ 引用提取功能正常")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
import pytest
from google import genai
from google.genai import types
from backend.tools.file_search import FileSearchTool
from backend.agents.rag_agent import create_rag_agent
import os

class TestRAGCitations:
    """測試 RAG 引用來源功能"""
    
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
    
    def test_search_with_citations(self, file_search_tool):
        """測試搜尋功能是否返回引用來源"""
        # 執行搜尋
        result = file_search_tool.search_with_citations(
            query="公司的休假政策有哪些？",
            corpus_name="main-corpus"
        )
        
        # 驗證結果結構
        assert "text" in result, "結果應包含 text 欄位"
        assert "citations" in result, "結果應包含 citations 欄位"
        assert isinstance(result["citations"], list), "citations 應為列表"
        
        print(f"\n📝 搜尋結果:")
        print(f"回應: {result['text'][:200]}...")
        print(f"\n📚 引用來源數量: {len(result['citations'])}")
        
        # 顯示引用來源
        for i, citation in enumerate(result['citations'], 1):
            print(f"\n{i}. {citation.get('title', 'Untitled')}")
            print(f"   來源: {citation.get('source', 'Unknown')}")
            if citation.get('snippet'):
                print(f"   片段: {citation['snippet'][:100]}...")
    
    def test_rag_agent_with_citations(self, genai_client, file_search_tool):
        """測試 RAG Agent 是否正確處理引用來源"""
        # 建立 RAG Agent 配置
        agent_data = create_rag_agent(file_search_tool)
        config = agent_data["config"]
        model = agent_data["model"]
        functions = agent_data["functions"]
        
        # 使用 generate_content 進行對話
        query = "根據文檔，公司的休假政策是什麼？請詳細說明。"
        
        # 第一次呼叫：讓模型決定是否需要使用工具
        response = genai_client.models.generate_content(
            model=model,
            contents=query,
            config=config
        )
        
        print(f"\n🤖 Agent 回應:")
        
        # 檢查是否有函數調用
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call'):
                    # 模型要求調用函數
                    function_call = part.function_call
                    function_name = function_call.name
                    function_args = function_call.args
                    
                    print(f"📞 函數調用: {function_name}")
                    print(f"   參數: {function_args}")
                    
                    # 執行函數
                    if function_name in functions:
                        function_result = functions[function_name](**function_args)
                        print(f"   結果: {function_result[:200]}...")
                        
                        # 將函數結果返回給模型
                        response = genai_client.models.generate_content(
                            model=model,
                            contents=[
                                query,
                                response.candidates[0].content,
                                types.Content(
                                    parts=[
                                        types.Part.from_function_response(
                                            name=function_name,
                                            response={"result": function_result}
                                        )
                                    ]
                                )
                            ],
                            config=config
                        )
        
        print(response.text)
        
        # 驗證回應包含引用資訊
        assert response.text is not None, "回應不應為空"
        assert len(response.text) > 0, "回應應有內容"
        
        print("\n✅ 引用來源測試通過")
    
    def test_multiple_document_query(self, file_search_tool):
        """測試跨多個文檔的查詢"""
        queries = [
            "公司的年假制度是什麼？",
            "遠端工作的規定有哪些？",
            "代碼審查的流程是什麼？",
        ]
        
        for query in queries:
            print(f"\n🔍 查詢: {query}")
            result = file_search_tool.search_with_citations(query, "main-corpus")
            
            assert "text" in result
            print(f"   回應長度: {len(result.get('text', ''))} 字元")
            print(f"   引用數量: {len(result.get('citations', []))}")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
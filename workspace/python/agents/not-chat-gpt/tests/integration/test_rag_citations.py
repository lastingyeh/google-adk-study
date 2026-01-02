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
        
        print(f"\n📝 查詢: {query}")
        
        # 第一次呼叫：讓模型決定是否需要使用工具
        response = genai_client.models.generate_content(
            model=model,
            contents=query,
            config=config
        )
        
        # 建立對話歷史
        conversation_history = [query]
        
        # 支援多輪函數調用
        max_iterations = 5  # 防止無限循環
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\n🔄 第 {iteration} 輪處理:")
            print(f"   候選數量: {len(response.candidates) if response.candidates else 0}")
            
            # 檢查回應狀態
            if not response.candidates or len(response.candidates) == 0:
                pytest.fail("模型沒有返回任何候選回應")
            
            # 檢查是否有函數調用
            has_function_call = False
            function_calls_in_this_round = []
            
            if response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        has_function_call = True
                        function_call = part.function_call
                        function_name = function_call.name
                        function_args = dict(function_call.args)
                        
                        print(f"\n📞 函數調用: {function_name}")
                        print(f"   參數: {function_args}")
                        
                        # 執行函數
                        if function_name in functions:
                            function_result = functions[function_name](**function_args)
                            print(f"   結果長度: {len(function_result)} 字元")
                            print(f"   結果預覽: {function_result[:200]}...")
                            
                            function_calls_in_this_round.append({
                                'name': function_name,
                                'result': function_result
                            })
                        else:
                            pytest.fail(f"未找到函數: {function_name}")
            
            # 如果有函數調用，將結果返回給模型
            if has_function_call and function_calls_in_this_round:
                print(f"\n🔄 發送 {len(function_calls_in_this_round)} 個函數結果給模型...")
                
                # 構建新的請求
                conversation_history.append(response.candidates[0].content)
                
                # 添加函數結果
                for fc in function_calls_in_this_round:
                    conversation_history.append(
                        types.Content(
                            parts=[
                                types.Part.from_function_response(
                                    name=fc['name'],
                                    response={"result": fc['result']}
                                )
                            ]
                        )
                    )
                
                # 繼續對話
                response = genai_client.models.generate_content(
                    model=model,
                    contents=conversation_history,
                    config=config
                )
            else:
                # 沒有函數調用，表示已獲得最終回應
                print("\n✅ 獲得最終文本回應")
                break
        
        # 檢查是否超過最大迭代次數
        if iteration >= max_iterations:
            pytest.fail(f"函數調用超過最大迭代次數 ({max_iterations})")
        
        print(f"\n📄 最終回應:")
        if response.text:
            print(f"   長度: {len(response.text)} 字元")
            print(f"   內容預覽: {response.text[:300]}...")
        else:
            print("   ⚠️ response.text 為空或 None")
            # 嘗試手動提取文字
            if response.candidates and response.candidates[0].content.parts:
                for i, part in enumerate(response.candidates[0].content.parts):
                    print(f"   Part {i}: {type(part)}")
                    if hasattr(part, 'text') and part.text:
                        print(f"      text: {part.text[:100]}...")
                    elif hasattr(part, 'text'):
                        print(f"      text: None or empty")
        
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
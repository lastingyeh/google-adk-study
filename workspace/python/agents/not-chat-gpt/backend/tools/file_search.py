from google import genai
from google.genai import types

class FileSearchTool:
    """Gemini File Search RAG 工具
    
    支援文檔搜尋和引用來源追蹤功能。
    """
    
    def __init__(self, client: genai.Client):
        """初始化 FileSearchTool
        
        Args:
            client: Gemini API 客戶端
        """
        self.client = client
    
    def search(self, query: str, corpus_name: str) -> dict:
        """基礎文檔搜尋
        
        Args:
            query: 搜尋查詢字串
            corpus_name: Corpus 名稱（例如：'main-corpus'）
        
        Returns:
            dict: 包含搜尋結果的字典
                - text: 回應文字
                - grounding_metadata: 原始的 grounding metadata（如果有）
                - error: 錯誤訊息（如果失敗）
        """
        try:
            # 使用 Gemini 的 grounding 功能搜尋 corpus
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=query,
                config=types.GenerateContentConfig(
                    tools=[
                        types.Tool(
                            google_search=types.GoogleSearch()
                        )
                    ]
                )
            )
            
            result = {
                "text": response.text if response.text else "",
            }
            
            # 提取 grounding metadata（如果存在）
            if hasattr(response, 'candidates') and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'grounding_metadata'):
                    result["grounding_metadata"] = candidate.grounding_metadata
            
            return result
            
        except Exception as e:
            return {
                "text": "",
                "error": str(e)
            }
    
    def extract_citations(self, grounding_metadata) -> list:
        """提取引用來源
        
        Args:
            grounding_metadata: Gemini 回應中的 grounding metadata
        
        Returns:
            list: 引用來源列表，每個元素包含：
                - source: 來源 URI
                - title: 文檔標題
                - snippet: 相關文字片段
        """
        if not grounding_metadata:
            return []
        
        citations = []
        
        # 處理 grounding chunks
        if hasattr(grounding_metadata, 'grounding_chunks') and grounding_metadata.grounding_chunks:
            for chunk in grounding_metadata.grounding_chunks:
                citation = {}
                
                # 提取網頁來源
                if hasattr(chunk, 'web'):
                    citation["source"] = chunk.web.uri if hasattr(chunk.web, 'uri') else "Unknown"
                    citation["title"] = chunk.web.title if hasattr(chunk.web, 'title') else "Untitled"
                else:
                    citation["source"] = "Unknown"
                    citation["title"] = "Untitled"
                
                # 提取文字片段
                citation["snippet"] = chunk.text if hasattr(chunk, 'text') else ""
                
                citations.append(citation)
        
        return citations
    
    def search_with_citations(self, query: str, corpus_name: str) -> dict:
        """搜尋並返回引用來源
        
        結合基礎搜尋功能與引用來源提取。
        
        Args:
            query: 搜尋查詢字串
            corpus_name: Corpus 名稱
        
        Returns:
            dict: 包含搜尋結果和引用來源的字典
                - text: 回應文字
                - citations: 引用來源列表
                - grounding_metadata: 原始 metadata（可選）
                - error: 錯誤訊息（如果失敗）
        """
        result = self.search(query, corpus_name)
        
        # 如果搜尋成功且有 grounding metadata，提取引用
        if "grounding_metadata" in result and not result.get("error"):
            citations = self.extract_citations(result["grounding_metadata"])
            result["citations"] = citations
        else:
            result["citations"] = []
        
        return result
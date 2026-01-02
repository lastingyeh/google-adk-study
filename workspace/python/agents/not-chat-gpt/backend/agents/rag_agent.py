from google.genai import types
from backend.tools.file_search import FileSearchTool
import os

def create_rag_agent(file_search_tool: FileSearchTool):
    """建立具有 RAG 能力的 Agent 配置
    
    Args:
        file_search_tool: FileSearchTool 實例
        
    Returns:
        dict: 包含 config 和 tool 的字典，用於創建 agent session
    """
    
    # 從環境變數取得模型名稱
    model_name = os.getenv('MODEL_NAME', 'gemini-2.0-flash-exp')
    
    # 定義 RAG 搜尋函數
    def rag_search(query: str) -> str:
        """文檔搜尋函式，用於從文檔庫中檢索相關資訊
        
        Args:
            query: 搜尋查詢字串
            
        Returns:
            str: 搜尋結果文字，包含引用來源
        """
        result = file_search_tool.search_with_citations(query, "main-corpus")
        
        response_text = result.get("text", "")
        citations = result.get("citations", [])
        
        # 附加引用來源
        if citations:
            response_text += "\n\n引用來源:\n"
            for i, cite in enumerate(citations, 1):
                response_text += f"{i}. {cite['title']} - {cite['source']}\n"
        
        return response_text
    
    # 創建配置
    config = types.GenerateContentConfig(
        system_instruction="你是 NotChatGPT，可以搜尋並引用文檔內容。當用戶詢問相關問題時，使用 rag_search 函數檢索資訊並提供準確回答。",
        temperature=0.7,
        tools=[
            types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name="rag_search",
                        description="從文檔庫中搜尋相關資訊，支援引用來源追蹤",
                        parameters={
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "要搜尋的查詢字串"
                                }
                            },
                            "required": ["query"]
                        }
                    )
                ]
            )
        ]
    )
    
    return {
        "config": config,
        "functions": {
            "rag_search": rag_search
        },
        "model": model_name
    }
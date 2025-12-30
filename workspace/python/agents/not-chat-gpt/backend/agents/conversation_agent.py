from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

def create_conversation_agent():
    """建立基礎對話 Agent 配置"""
    return types.GenerateContentConfig(
        system_instruction="""
        你是 NotChatGPT，一個智慧對話助理。
        
        特點：
            - 友善且專業的對話風格
            - 提供準確且有幫助的資訊
            - 支援多輪對話與上下文理解
        """,
        temperature=1.0,
    )

# 測試用
if __name__ == "__main__":
    # 載入 .env 檔案
    load_dotenv()
    
    # 從環境變數取得 API Key
    api_key = os.getenv('GOOGLE_API_KEY')
    # 從環境變數取得模型名稱
    model_name = os.getenv('MODEL_NAME', 'gemini-2.0-flash-exp')
    if not api_key:
        print("❌ 錯誤: GOOGLE_API_KEY 未設定在 .env 檔案中")
        exit(1)
    
    client = genai.Client(api_key=api_key)
    config = create_conversation_agent()
    
    # 使用 generate_content 進行對話
    response = client.models.generate_content(
        model=model_name,
        contents="你好！請介紹一下你自己",
        config=config
    )
    print(response.text)
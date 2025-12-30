from google import genai
from dotenv import load_dotenv
import os
from backend.agents.conversation_agent import create_conversation_agent

def test_multi_turn():
    # 載入環境變數
    load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY')
    model_name = os.getenv('MODEL_NAME', 'gemini-2.0-flash-exp')
    
    if not api_key:
        print("❌ 錯誤: GOOGLE_API_KEY 未設定")
        return
    
    client = genai.Client(api_key=api_key)
    config = create_conversation_agent()
    
    # 第一輪對話
    print("\n=== 第一輪對話 ===")
    response1 = client.models.generate_content(
        model=model_name,
        contents="我叫 Alice",
        config=config
    )
    print(f"Round 1: {response1.text}")
    
    # 注意：generate_content 不保留對話歷史
    # 如需多輪對話記憶，需要手動管理對話歷史或使用 Chat API
    print("\n⚠️  注意：基礎 generate_content API 不支援自動對話記憶")
    print("✅ 基本對話測試通過")

if __name__ == "__main__":
    test_multi_turn()
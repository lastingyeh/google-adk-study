"""NotChatGPT CLI 介面

提供命令列互動介面，支援：
- 思考模式切換
- 安全防護開關
- 對話歷史管理（基於 SessionService）
"""
import sys
from google import genai
from dotenv import load_dotenv
import os
import uuid
from backend.config.mode_config import ModeConfig
from backend.agents.safe_conversation_agent import safe_generate_response
from backend.services.session_service import SessionService

def main():
    # 載入環境變數
    load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY')
    model_name = os.getenv('MODEL_NAME', 'gemini-2.0-flash-exp')
    
    if not api_key:
        print("❌ 錯誤: GOOGLE_API_KEY 未設定在 .env 檔案中")
        sys.exit(1)
    
    print("🤖 NotChatGPT CLI (with Session Management)")
    print("指令:")
    print("  /thinking  - 切換思考模式")
    print("  /standard  - 切換標準模式")
    print("  /safe on   - 啟用安全防護")
    print("  /safe off  - 停用安全防護")
    print("  /new       - 建立新對話")
    print("  /list      - 列出所有對話")
    print("  /load <id> - 載入指定對話")
    print("  /history   - 顯示當前對話歷史")
    print("  /quit      - 退出\n")
    
    client = genai.Client(api_key=api_key)
    session_service = SessionService()
    
    # 初始化狀態
    thinking_mode = False
    enable_safety = True
    current_session_id = str(uuid.uuid4())
    session_service.create_session(current_session_id, title="CLI Session")
    
    print(f"📝 當前會話: {current_session_id[:8]}...")
    print(f"當前模式: {'💭 思考模式' if thinking_mode else '💬 標準模式'}")
    print(f"安全防護: {'🛡️ 啟用' if enable_safety else '⚠️ 停用'}\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            # 處理命令
            if user_input == "/quit":
                print("👋 再見！")
                break
            
            elif user_input == "/thinking":
                thinking_mode = True
                print("💭 已切換到思考模式")
                continue
            
            elif user_input == "/standard":
                thinking_mode = False
                print("💬 已切換到標準模式")
                continue
            
            elif user_input == "/safe on":
                enable_safety = True
                print("🛡️ 已啟用安全防護")
                continue
            
            elif user_input == "/safe off":
                enable_safety = False
                print("⚠️ 已停用安全防護")
                continue
            
            elif user_input == "/new":
                current_session_id = str(uuid.uuid4())
                session_service.create_session(current_session_id, title="CLI Session")
                print(f"✨ 已建立新對話: {current_session_id[:8]}...")
                continue
            
            elif user_input == "/list":
                conversations = session_service.list_conversations()
                if not conversations:
                    print("📝 目前沒有對話")
                else:
                    print(f"📝 對話清單 (共 {len(conversations)} 個):")
                    for conv_id, title, updated_at in conversations[:10]:  # 只顯示最近 10 個
                        indicator = "👉" if conv_id == current_session_id else "  "
                        print(f"{indicator} {conv_id[:8]}... - {title} (更新: {updated_at.strftime('%Y-%m-%d %H:%M')})")
                continue
            
            elif user_input.startswith("/load "):
                session_id_prefix = user_input.split(" ", 1)[1].strip()
                # 查找匹配的 session
                conversations = session_service.list_conversations()
                matched = [c for c in conversations if c[0].startswith(session_id_prefix)]
                if matched:
                    current_session_id = matched[0][0]
                    print(f"📂 已載入對話: {current_session_id[:8]}...")
                    # 顯示歷史
                    messages = session_service.get_messages(current_session_id)
                    if messages:
                        print(f"📜 對話歷史 (共 {len(messages)} 則訊息)")
                else:
                    print(f"❌ 找不到對話: {session_id_prefix}")
                continue
            
            elif user_input == "/history":
                messages = session_service.get_messages(current_session_id)
                if not messages:
                    print("📝 當前對話沒有歷史")
                else:
                    print(f"📜 對話歷史 (共 {len(messages)} 則訊息):")
                    for i, (role, content) in enumerate(messages, 1):
                        icon = "👤" if role == "user" else "🤖"
                        preview = content[:50] + "..." if len(content) > 50 else content
                        print(f"{i}. {icon} {role}: {preview}")
                continue
            
            elif user_input.startswith("/"):
                print("❓ 未知指令，請使用 /thinking, /standard, /safe on, /safe off, /new, /list, /load, /history 或 /quit")
                continue
            
            # 空輸入
            if not user_input:
                continue
            
            # 載入對話歷史並轉換為 API 格式
            db_messages = session_service.get_messages(current_session_id)
            conversation_history = []
            for role, content in db_messages:
                conversation_history.append({
                    'role': role,
                    'parts': [{'text': content}]
                })
            
            # 生成回應（傳入對話歷史）
            config = ModeConfig.create_config_with_mode(thinking_mode=thinking_mode)
            result = safe_generate_response(
                client=client,
                model_name=model_name,
                user_message=user_input,
                enable_safety=enable_safety,
                conversation_history=conversation_history
            )
            
            # 顯示回應
            mode_icon = "💭" if thinking_mode else "💬"
            if result['success']:
                print(f"\n{mode_icon} Agent: {result['text']}\n")
                
                # 儲存到資料庫
                session_service.add_message(current_session_id, "user", user_input)
                session_service.add_message(current_session_id, "model", result['text'])
            else:
                print(f"\n⚠️ {result['text']}")
                if result['reason']:
                    print(f"原因: {result['reason']}\n")
            
        except KeyboardInterrupt:
            print("\n👋 再見！")
            break
        except Exception as e:
            print(f"❌ 錯誤: {e}\n")

if __name__ == "__main__":
    main()
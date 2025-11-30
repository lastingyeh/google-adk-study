"""教學 29：UI 整合介紹 - 快速入門範例。

這是一個最小化的 ADK 代理，用於示範 AG-UI 協定整合。
基於教學 29 的快速入門部分。
"""

import os
import json
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import uvicorn

# 嘗試匯入 AG-UI ADK 整合工具
try:
    from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
except ImportError:
    # 如果找不到套件，拋出錯誤並提示安裝指令
    raise ImportError(
        "找不到 ag_ui_adk。請使用以下指令安裝： pip install ag-ui-adk"
    )

# 匯入 Google ADK
from google.adk.agents import Agent

# 從 .env 檔案載入環境變數
load_dotenv()


# ============================================================================
# 代理設定 (Agent Configuration)
# ============================================================================

# 建立一個簡單的 ADK 代理
adk_agent = Agent(
    name="quickstart_agent",  # 代理名稱
    model="gemini-2.0-flash-exp",  # 使用的模型
    instruction="""
    您是由 Google ADK 驅動的樂於助人的人工智慧助理。

    您的角色：
    - 清晰簡潔地回答問題
    - 保持友善與專業
    - 提供準確的資訊
    - 如果您不知道某件事，請直接告知
    - 協助使用者了解 ADK 和 AI 概念

    指導方針：
    - 除非被要求提供更多細節，否則回覆內容應少於三段
    - 使用 markdown 格式以提高可讀性
    - 保持對話性但專業的語氣
    - 主動詢問是否需要協助處理後續問題"""
)

# 使用 AG-UI 中介軟體包裝 ADK 代理
agent = ADKAgent(
    adk_agent=adk_agent,  # 傳入已建立的 ADK 代理
    app_name="quickstart_demo",  # 應用程式名稱
    user_id="demo_user",  # 範例使用者 ID
    session_timeout_seconds=3600,  # 會話超時時間 (秒)
    use_in_memory_services=True,  # 使用記憶體內服務以簡化設定
)

# 匯出原始代理以供測試使用
root_agent = adk_agent


# ============================================================================
# 用於 CopilotKit 相容性的中介軟體 (Middleware)
# ============================================================================

class MessageIDMiddleware(BaseHTTPMiddleware):
    """
    此中介軟體用於注入訊息 ID，以確保與 CopilotKit 的相容性。

    CopilotKit 發送的訊息可能不包含 ID，但 AG-UI 協定要求每個訊息都有 ID。
    這個中介軟體會為任何缺少 'id' 欄位的訊息添加一個 UUID。
    """

    async def dispatch(self, request: Request, call_next):
        """處理請求並在需要時注入訊息 ID。"""
        # 僅處理指向 /api/copilotkit 的 POST 請求
        if request.method == "POST" and request.url.path == "/api/copilotkit":
            # 讀取請求主體
            body = await request.body()

            try:
                # 解析 JSON
                data = json.loads(body)

                print(f"🔍 中介軟體：收到請求，包含的鍵值為： {list(data.keys())}")

                # 如果訊息中缺少 ID，則注入
                if "messages" in data and isinstance(data["messages"], list):
                    modified = False
                    for i, msg in enumerate(data["messages"]):
                        if isinstance(msg, dict):
                            if "id" not in msg:
                                # 產生唯一的 ID
                                msg["id"] = f"msg-{uuid.uuid4()}"
                                modified = True
                                print(f"✅ 中介軟體：已為訊息 {i} ({msg.get('role', 'unknown')}) 添加 ID")

                    # 如果內容被修改，則建立一個帶有新主體的新請求
                    if modified:
                        modified_body = json.dumps(data).encode()
                        print("📝 中介軟體：已修改主體，為訊息注入了 ID")

                        # 取代請求主體
                        async def receive():
                            return {"type": "http.request", "body": modified_body}

                        request._receive = receive
                    else:
                        print("ℹ️  中介軟體：無需修改")
                else:
                    print("⚠️  中介軟體：請求中找不到 'messages' 欄位")

            except json.JSONDecodeError as e:
                print(f"❌ 中介軟體：JSON 解碼錯誤： {e}")
            except Exception as e:
                print(f"❌ 中介軟體：未預期的錯誤： {e}")

        # 繼續處理請求
        response = await call_next(request)
        return response


# ============================================================================
# FastAPI 應用程式
# ============================================================================

# 建立 FastAPI 應用程式
app = FastAPI(
    title="教學 29 - UI 整合快速入門",
    description="示範 AG-UI 協定的最小化 ADK 代理",
    version="1.0.0",
)

# 啟用 CORS (跨來源資源共用)，允許前端連線
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite 預設
        "http://localhost:3000",  # Next.js 預設 (備用)
        "http://localhost:8000",  # 本地測試
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加中介軟體以注入訊息 ID，確保與 CopilotKit 相容
app.add_middleware(MessageIDMiddleware)

# 為 CopilotKit 添加 ADK 端點
add_adk_fastapi_endpoint(app, agent, path="/api/copilotkit")


# 健康檢查端點
@app.get("/health")
def health_check():
    """健康檢查端點。"""
    return {
        "status": "healthy",
        "agent": "quickstart_agent",
        "version": "1.0.0",
        "tutorial": "29"
    }


@app.get("/")
def root():
    """根端點，提供 API 資訊。"""
    return {
        "message": "教學 29 - UI 整合快速入門 API",
        "tutorial": "UI 整合與 AG-UI 協定介紹",
        "endpoints": {
            "health": "/health",
            "copilotkit": "/api/copilotkit",
            "docs": "/docs",
        },
    }


# ============================================================================
# 主程式進入點
# ============================================================================

if __name__ == "__main__":
    # 從環境變數獲取設定
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")

    print("=" * 60)
    print("🚀 教學 29 - UI 整合快速入門")
    print("=" * 60)
    print(f"🌐 伺服器： http://{host}:{port}")
    print(f"📚 文件： http://{host}:{port}/docs")
    print(f"💬 CopilotKit 端點： http://{host}:{port}/api/copilotkit")
    print("=" * 60)
    print()
    print("這是一個最小化的範例，示範：")
    print("  • 使用 AG-UI 協定的 ADK 代理")
    print("  • 具有 CopilotKit 端點的 FastAPI 後端")
    print("  • 已準備好與 React/Vite 前端整合")
    print("=" * 60)

    # 使用 uvicorn 運行
    uvicorn.run(
        "agent:app",  # 指向 FastAPI 應用程式實例
        host=host,
        port=port,
        reload=True,  # 開發模式，程式碼變更時自動重載
        log_level="info",
    )

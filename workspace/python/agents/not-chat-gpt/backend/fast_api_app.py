import os


from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app


# 獲取 backend 目錄的路徑
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化 FastAPI 應用程式，使用 ADK 提供的 get_fast_api_app
app: FastAPI = get_fast_api_app(
    agents_dir=BACKEND_DIR,
    web=True,
)
app.title = "not-chat-gpt"
app.description = "與 not-chat-gpt 代理互動的 API"


# 主程式進入點
if __name__ == "__main__":
    import uvicorn

    # 啟動 Uvicorn 伺服器
    uvicorn.run(app, host="0.0.0.0", port=8000)
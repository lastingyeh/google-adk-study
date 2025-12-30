import uvicorn
from dotenv import load_dotenv
from api.routes import app

# 載入環境變數（必須在應用程式啟動前載入）
load_dotenv()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
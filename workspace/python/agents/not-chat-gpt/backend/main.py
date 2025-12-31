import uvicorn
from dotenv import load_dotenv

# 載入環境變數（必須在應用程式啟動前載入）
load_dotenv()

if __name__ == "__main__":
    # 使用字串路徑，讓 uvicorn 自動 reload 時也能正確載入
    uvicorn.run("backend.api.routes:app", host="0.0.0.0", port=8000, reload=True)
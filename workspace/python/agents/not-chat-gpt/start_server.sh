#!/bin/bash
# NotChatGPT 伺服器啟動腳本

cd "$(dirname "$0")"

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo "❌ 錯誤: 找不到虛擬環境 venv/"
    echo "請先執行: python -m venv venv && source venv/bin/activate && pip install -r backend/requirements.txt"
    exit 1
fi

# 啟動伺服器
echo "🚀 啟動 NotChatGPT API 伺服器..."
echo "📍 URL: http://localhost:8000"
echo "📖 文件: http://localhost:8000/docs"
echo "💡 提示: 按 Ctrl+C 停止伺服器"
echo ""

# 啟動（使用模組方式）
python -m backend.main

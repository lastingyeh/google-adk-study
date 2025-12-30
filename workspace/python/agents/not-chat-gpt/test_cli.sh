#!/bin/bash
# CLI 功能驗證測試腳本

echo "🧪 開始 CLI 功能測試..."
echo ""

cd "$(dirname "$0")"

# 測試 1: 基本啟動
echo "✅ 測試 1: 基本啟動"
python backend/cli.py <<EOF
/quit
EOF
echo ""

# 測試 2: 對話記憶
echo "✅ 測試 2: 對話記憶（多輪對話上下文）"
python backend/cli.py <<EOF
我叫小明
我剛才說我叫什麼？
/history
/quit
EOF
echo ""

# 測試 3: 模式切換
echo "✅ 測試 3: 思考模式切換"
python backend/cli.py <<EOF
/thinking
解釋 Python
/standard
/quit
EOF
echo ""

# 測試 4: 安全防護
echo "✅ 測試 4: 安全防護（PII 偵測）"
python backend/cli.py <<EOF
/safe on
1234-5678-9012-3456
/safe off
1234-5678-9012-3456
/quit
EOF
echo ""

# 測試 5: Session 管理
echo "✅ 測試 5: Session 管理"
python backend/cli.py <<EOF
測試訊息 1
/new
測試訊息 2
/list
/quit
EOF
echo ""

echo "🎉 所有測試完成！"

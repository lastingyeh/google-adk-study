#!/bin/bash

# 停止 A2A 伺服器 - 使用 to_a2a() 函式的官方 ADK 實作
# 此腳本停止所有託管 A2A 代理的 uvicorn 伺服器

echo "🛑 正在停止 ADK A2A 伺服器..."

# 溫和地終止特定連接埠上的程序的函式
stop_server_on_port() {
    local port=$1
    local agent_name=$2

    # 尋找使用該連接埠的程序
    PID=$(lsof -ti :$port 2>/dev/null)

    if [ -n "$PID" ]; then
        echo "🔸 正在停止 $agent_name (PID: $PID) 於連接埠 $port..."
        kill $PID 2>/dev/null

        # 等待溫和關機
        local attempts=0
        while [ $attempts -lt 10 ] && kill -0 $PID 2>/dev/null; do
            sleep 1
            attempts=$((attempts + 1))
        done

        # 如果仍在運行，則強制終止
        if kill -0 $PID 2>/dev/null; then
            echo "⚠️  正在強制終止 $agent_name (PID: $PID)..."
            kill -9 $PID 2>/dev/null
        fi

        echo "✅ $agent_name 已停止"
    else
        echo "💡 找不到於連接埠 $port 上的 $agent_name 程序"
    fi
}

# 停止所有已知的 A2A 伺服器
stop_server_on_port 8001 "研究代理"
stop_server_on_port 8002 "分析代理"
stop_server_on_port 8003 "內容代理"

# 額外清理：終止我們代理的任何剩餘 uvicorn 程序
echo "🧹 正在清理任何剩餘的 uvicorn 程序..."
pkill -f "uvicorn.*research_agent\|uvicorn.*analysis_agent\|uvicorn.*content_agent" 2>/dev/null && echo "✅ 已清理剩餘的 uvicorn 程序" || echo "💡 找不到額外的 uvicorn 程序"

# 驗證所有程序皆已停止
echo ""
echo "🔍 正在驗證伺服器是否已停止..."

all_stopped=true
for port in 8001 8002 8003; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  連接埠 $port 仍在使用中"
        all_stopped=false
    fi
done

if [ "$all_stopped" = true ]; then
    echo "✅ 所有 A2A 伺服器皆已成功停止！"
    echo ""
    echo "🚀 若要重新啟動伺服器，請執行：./start_a2a_servers.sh"
else
    echo "❌ 部分連接埠仍在使用中。您可能需要手動終止程序："
    echo "   lsof -ti :8001,8002,8003 | xargs kill -9"
fi

echo ""

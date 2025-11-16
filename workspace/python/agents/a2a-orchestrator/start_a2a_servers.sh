#!/bin/bash

# 啟動 A2A 伺服器 - 使用 to_a2a() 函式的官方 ADK 實作
# 此腳本使用 uvicorn 與 to_a2a() 函式啟動所有遠端代理

echo "🚀 正在使用 to_a2a() 函式啟動 ADK A2A 伺服器..."

# 檢查連接埠是否被佔用的函式
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
        return 0  # 連接埠已被佔用
    else
        return 1  # 連接埠可用
    fi
}

# 等待伺服器就緒的函式
wait_for_server() {
    local port=$1
    local agent_name=$2
    local max_attempts=30
    local attempt=1

    echo "⏳ 正在等待 $agent_name 於連接埠 $port 上就緒..."

    while [ $attempt -le $max_attempts ]; do
        if curl -s "http://localhost:$port/.well-known/agent-card.json" >/dev/null 2>&1; then
            echo "✅ $agent_name 已於連接埠 $port 上就緒"
            return 0
        fi
        sleep 1
        attempt=$((attempt + 1))
    done

    echo "❌ $agent_name 未能於連接埠 $port 上啟動"
    return 1
}

# 清理我們連接埠上任何現有的程序
echo "🧹 正在清理現有程序..."
pkill -f "uvicorn.*research_agent\|uvicorn.*analysis_agent\|uvicorn.*content_agent" 2>/dev/null || true
sleep 2

# 使用 uvicorn + to_a2a() 啟動研究代理 (連接埠 8001)
echo "🔬 正在於連接埠 8001 上啟動研究代理..."
uvicorn research_agent.agent:a2a_app --host localhost --port 8001 &
RESEARCH_PID=$!
echo "   PID: $RESEARCH_PID"

# 使用 uvicorn + to_a2a() 啟動分析代理 (連接埠 8002)
echo "📊 正在於連接埠 8002 上啟動分析代理..."
uvicorn analysis_agent.agent:a2a_app --host localhost --port 8002 &
ANALYSIS_PID=$!
echo "   PID: $ANALYSIS_PID"

# 使用 uvicorn + to_a2a() 啟動內容代理 (連接埠 8003)
echo "✍️  正在於連接埠 8003 上啟動內容代理..."
uvicorn content_agent.agent:a2a_app --host localhost --port 8003 &
CONTENT_PID=$!
echo "   PID: $CONTENT_PID"

# 等待所有伺服器就緒
echo ""
echo "🔄 正在等待所有代理就緒..."

if wait_for_server 8001 "研究代理" && \
   wait_for_server 8002 "分析代理" && \
   wait_for_server 8003 "內容代理"; then

    echo ""
    echo "🎉 所有 A2A 伺服器皆已成功運行！"
    echo ""
    echo "📋 伺服器狀態："
    echo "   • 研究代理： http://localhost:8001  (PID: $RESEARCH_PID)"
    echo "   • 分析代理： http://localhost:8002  (PID: $ANALYSIS_PID)"
    echo "   • 內容代理：  http://localhost:8003  (PID: $CONTENT_PID)"
    echo ""
    echo "🔗 代理卡片 (由 to_a2a() 自動產生)："
    echo "   • 研究：http://localhost:8001/.well-known/agent-card.json"
    echo "   • 分析：http://localhost:8002/.well-known/agent-card.json"
    echo "   • 內容： http://localhost:8003/.well-known/agent-card.json"
    echo ""
    echo "🏃 準備進行協調！使用以下指令啟動您的協調器："
    echo "   adk web a2a_orchestrator/"
    echo ""
    echo "🛑 若要停止所有伺服器，請執行：./stop_a2a_servers.sh"

else
    echo ""
    echo "❌ 部分伺服器啟動失敗。請檢查日誌以了解錯誤。"
    echo "💡 請嘗試再次執行 './stop_a2a_servers.sh' 然後 './start_a2a_servers.sh'"
    exit 1
fi

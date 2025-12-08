#!/bin/zsh

# 顏色設定
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 設定工作目錄
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "${BLUE}========================================${NC}"
echo "${GREEN}啟動所有服務 (Starting All Services)${NC}"
echo "${BLUE}========================================${NC}"

# 1. 啟動 MCP Server
echo "\n${GREEN}[1/4] 啟動 MCP Server...${NC}"
uv run ./mcp/servers/streamable_http_server.py &
MCP_PID=$!
echo "MCP Server PID: $MCP_PID"
sleep 10

# 2. 啟動 Host Agent Server
echo "\n${GREEN}[2/4] 啟動 Host Agent Server...${NC}"
uv run python3 -m agents.host_agent &
HOST_AGENT_PID=$!
echo "Host Agent Server PID: $HOST_AGENT_PID"
sleep 10

# 3. 啟動 Website Builder Simple
echo "\n${GREEN}[3/4] 啟動 Website Builder Simple...${NC}"
uv run python3 -m agents.website_builder_simple &
WEBSITE_BUILDER_PID=$!
echo "Website Builder Simple PID: $WEBSITE_BUILDER_PID"
sleep 10



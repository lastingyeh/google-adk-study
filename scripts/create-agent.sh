#!/bin/bash

# Agent Project Generator
# 根據範本建立 Google ADK Agent 專案結構

set -e

# 顏色定義
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 檢查參數
if [ $# -eq 0 ]; then
    echo -e "${YELLOW}使用方式: $0 <package-name>${NC}"
    echo -e "${YELLOW}範例: $0 travel-planner${NC}"
    exit 1
fi

PACKAGE_NAME=$1
# 將 package-name 轉換為 agent_name (例如: travel-planner -> travel_planner)
AGENT_NAME=$(echo "$PACKAGE_NAME" | tr '-' '_')

# 設定基礎路徑
BASE_DIR="workspace/python/agents"
PROJECT_DIR="$BASE_DIR/$PACKAGE_NAME"

# 檢查目錄是否已存在
if [ -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}警告: 目錄 $PROJECT_DIR 已存在！${NC}"
    read -p "是否要覆蓋? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "取消操作"
        exit 1
    fi
    rm -rf "$PROJECT_DIR"
fi

echo -e "${BLUE}正在建立 Agent 專案: $PACKAGE_NAME${NC}"
echo -e "${BLUE}Agent 名稱: $AGENT_NAME${NC}"

# 建立目錄結構
mkdir -p "$PROJECT_DIR/$AGENT_NAME"
mkdir -p "$PROJECT_DIR/tests"

echo -e "${GREEN}✓ 建立目錄結構${NC}"

# 建立空檔案
touch "$PROJECT_DIR/Makefile"
echo -e "${GREEN}✓ 建立 Makefile${NC}"

touch "$PROJECT_DIR/README.md"
echo -e "${GREEN}✓ 建立 README.md${NC}"

touch "$PROJECT_DIR/requirements.txt"
echo -e "${GREEN}✓ 建立 requirements.txt${NC}"

touch "$PROJECT_DIR/pyproject.toml"
echo -e "${GREEN}✓ 建立 pyproject.toml${NC}"

# 建立 agent 目錄下的空檔案
touch "$PROJECT_DIR/$AGENT_NAME/.env.example"
touch "$PROJECT_DIR/$AGENT_NAME/__init__.py"
touch "$PROJECT_DIR/$AGENT_NAME/agent.py"
echo -e "${GREEN}✓ 建立 agent 檔案${NC}"

# 建立測試目錄下的空檔案
touch "$PROJECT_DIR/tests/__init__.py"
touch "$PROJECT_DIR/tests/README.md"
touch "$PROJECT_DIR/tests/test_imports.py"
touch "$PROJECT_DIR/tests/test_structure.py"
touch "$PROJECT_DIR/tests/test_agent.py"
echo -e "${GREEN}✓ 建立測試檔案${NC}"

echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Agent 專案建立完成！${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}專案位置:${NC} $PROJECT_DIR"
echo -e "${YELLOW}下一步:${NC}"
echo "  1. cd $PROJECT_DIR"
echo "  2. 複製 .env.example 到 .env 並設定 API Key"
echo "  3. make install"
echo "  4. make run"
echo ""

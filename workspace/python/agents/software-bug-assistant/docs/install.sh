#!/bin/bash

# Software Bug Assistant - UV 自動化安裝腳本
# 這個腳本會逐步安裝和配置專案

set -e  # 遇到錯誤時停止

echo "🚀 開始初始化 Software Bug Assistant 專案..."

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函數：顯示步驟
step() {
    echo -e "\n${BLUE}📋 步驟: $1${NC}"
}

# 函數：顯示成功
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# 函數：顯示警告
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 函數：顯示錯誤
error() {
    echo -e "${RED}❌ $1${NC}"
}

# 檢查 UV 是否已安裝
check_uv() {
    step "檢查 UV 是否已安裝"
    if command -v uv &> /dev/null; then
        success "UV 已安裝: $(uv --version)"
    else
        error "UV 未安裝，請先安裝 UV:"
        echo "  brew install uv"
        echo "  或"
        echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
}

# 初始化專案
init_project() {
    step "初始化專案結構"

    # 如果已經有 pyproject.toml，詢問是否覆蓋
    if [ -f "pyproject.toml" ]; then
        warning "pyproject.toml 已存在"
        read -p "是否要重新初始化專案？(y/N): " response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            echo "跳過專案初始化"
            return
        fi
    fi

    uv init --name software-bug-assistant
    success "專案結構已創建"
}

# 設定 Python 版本
set_python_version() {
    step "設定 Python 版本"
    uv python pin 3.11
    success "Python 版本已設定為 3.11"
}

# 安裝核心依賴
install_core_dependencies() {
    step "安裝核心依賴"

    echo "  📦 安裝 Google ADK..."
    uv add "google-adk>=1.8.0"

    echo "  📦 安裝 LangChain..."
    uv add "langchain>=0.3.0,<0.4.0"
    uv add "langchain-community>=0.3.25"

    echo "  📦 安裝 Google Cloud AI Platform..."
    uv add "google-cloud-aiplatform[agent-engines,evaluation]>=1.93.0"

    success "核心依賴安裝完成"
}

# 安裝工具依賴
install_tool_dependencies() {
    step "安裝工具依賴"

    echo "  📦 安裝環境變數管理..."
    uv add "python-dotenv>=1.1.0"

    echo "  📦 安裝 Stack API..."
    uv add "stackapi>=0.3.1"

    echo "  📦 安裝工具箱核心..."
    uv add "toolbox-core>=0.1.0"

    success "工具依賴安裝完成"
}

# 安裝開發依賴
install_dev_dependencies() {
    step "安裝開發依賴"

    echo "  📦 安裝測試框架..."
    uv add --group dev "pytest>=8.3.5"
    uv add --group dev "pytest-asyncio>=0.26.0"
    uv add --group dev "agent-starter-pack>=0.14.1"

    success "開發依賴安裝完成"
}

# 安裝代碼品質工具
install_lint_dependencies() {
    step "安裝代碼品質工具"

    echo "  📦 安裝 Ruff..."
    uv add --optional lint "ruff>=0.4.6"

    echo "  📦 安裝 MyPy..."
    uv add --optional lint "mypy>=1.15.0"

    echo "  📦 安裝拼寫檢查..."
    uv add --optional lint "codespell>=2.2.0"

    echo "  📦 安裝類型定義..."
    uv add --optional lint "types-pyyaml>=6.0.12.20240917"
    uv add --optional lint "types-requests>=2.32.0.20240914"

    success "代碼品質工具安裝完成"
}

# 創建專案結構
create_project_structure() {
    step "創建專案目錄結構"

    # 創建主要目錄
    mkdir -p software_bug_assistant
    mkdir -p tests
    mkdir -p deployment
    mkdir -p eval

    # 創建 Python 初始化文件
    touch software_bug_assistant/__init__.py
    touch tests/__init__.py

    # 創建範例檔案
    cat > software_bug_assistant/main.py << 'EOF'
"""Software Bug Assistant 主程式."""

from typing import Any


def main() -> None:
    """主函數."""
    print("Software Bug Assistant 啟動中...")


if __name__ == "__main__":
    main()
EOF

    cat > tests/test_main.py << 'EOF'
"""測試主程式."""

import pytest
from software_bug_assistant.main import main


def test_main() -> None:
    """測試主函數."""
    # 這裡添加您的測試邏輯
    assert True
EOF

    success "專案目錄結構已創建"
}

# 創建配置文件
create_config_files() {
    step "創建配置文件"

    # 創建 .env.example
    cat > .env.example << 'EOF'
# Google Cloud 配置
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# API 金鑰
OPENAI_API_KEY=your-openai-api-key

# 其他配置
DEBUG=false
LOG_LEVEL=INFO
EOF

    # 創建 README.md
    cat > README.md << 'EOF'
# Software Bug Assistant

使用 Google ADK 建立的軟體錯誤診斷助手。

## 安裝

1. 確保您已安裝 UV
2. 執行安裝腳本：`./install.sh`

## 使用方法

```bash
# 運行主程式
uv run python software_bug_assistant/main.py

# 運行測試
uv run --group dev pytest

# 代碼檢查
uv run --extra lint ruff check .
uv run --extra lint mypy .
```

## 開發

參考 `INSTALLATION_GUIDE.md` 獲取詳細的開發指南。
EOF

    # 創建 .gitignore
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
ENV/

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# UV
uv.lock

# OS
.DS_Store
Thumbs.db
EOF

    success "配置文件已創建"
}

# 驗證安裝
verify_installation() {
    step "驗證安裝"

    echo "  🔍 檢查依賴樹..."
    uv tree

    echo "  🔍 檢查專案狀態..."
    uv check

    echo "  🧪 運行測試..."
    uv run --group dev pytest -v

    success "安裝驗證完成"
}

# 顯示後續步驟
show_next_steps() {
    step "安裝完成！"
    echo ""
    echo "🎉 Software Bug Assistant 專案已成功初始化！"
    echo ""
    echo "📋 後續步驟："
    echo "  1. 複製 .env.example 到 .env 並填入您的配置"
    echo "     cp .env.example .env"
    echo ""
    echo "  2. 開始開發您的 Agent 邏輯"
    echo "     編輯 software_bug_assistant/main.py"
    echo ""
    echo "  3. 運行程式"
    echo "     uv run python software_bug_assistant/main.py"
    echo ""
    echo "  4. 運行測試"
    echo "     uv run --group dev pytest"
    echo ""
    echo "  5. 代碼檢查"
    echo "     uv run --extra lint ruff check ."
    echo "     uv run --extra lint mypy ."
    echo ""
    echo "📚 參考文件："
    echo "  - INSTALLATION_GUIDE.md: 詳細安裝指南"
    echo "  - README.md: 專案說明"
    echo ""
}

# 主執行流程
main() {
    echo "🔧 Software Bug Assistant - UV 自動化安裝"
    echo "================================================"

    check_uv
    init_project
    set_python_version
    install_core_dependencies
    install_tool_dependencies
    install_dev_dependencies
    install_lint_dependencies
    create_project_structure
    create_config_files
    verify_installation
    show_next_steps
}

# 執行主程式
main "$@"
# 🚀 快速開始指南

## 簡易三步驟安裝

### 1️⃣ 確保 UV 已安裝

```bash
# 檢查是否已安裝
uv --version

# 如果未安裝，使用 Homebrew 安裝
brew install uv
```

### 2️⃣ 執行自動化安裝腳本

```bash
cd /Users/cfh00543956/Desktop/Labs/google-adk-study/workspace/python/agents/software-bug-assistant
./install.sh
```

### 3️⃣ 開始開發

```bash
# 運行程式
uv run python software_bug_assistant/main.py

# 運行測試
uv run --group dev pytest
```

## 📁 專案結構說明

安裝完成後，您的專案結構將如下：

```
software-bug-assistant/
├── pyproject.toml              # 專案配置文件
├── README.md                   # 專案說明
├── INSTALLATION_GUIDE.md       # 詳細安裝指南
├── install.sh                  # 自動化安裝腳本
├── .env.example               # 環境變數範例
├── .gitignore                 # Git 忽略文件
├── software_bug_assistant/     # 主要程式碼目錄
│   ├── __init__.py
│   └── main.py                # 主程式
├── tests/                     # 測試目錄
│   ├── __init__.py
│   └── test_main.py
├── deployment/                # 部署相關文件
└── eval/                      # 評估相關文件
```

## 🔧 依賴套件說明

### 核心依賴

- **google-adk**: Google Agent Development Kit 核心功能
- **langchain**: 大語言模型應用開發框架
- **google-cloud-aiplatform**: Google Cloud AI 平台整合
- **python-dotenv**: 環境變數管理
- **stackapi**: Stack Overflow API 整合
- **toolbox-core**: 核心工具箱

### 開發依賴

- **pytest**: Python 測試框架
- **pytest-asyncio**: 異步測試支援
- **agent-starter-pack**: Agent 開發入門工具包

### 代碼品質工具

- **ruff**: 代碼格式化和檢查
- **mypy**: 靜態類型檢查
- **codespell**: 拼寫檢查

## ⚙️ 常用指令

```bash
# 安裝新套件
uv add <package-name>

# 安裝開發依賴
uv add --group dev <package-name>

# 運行腳本
uv run python <script.py>

# 運行測試
uv run --group dev pytest

# 代碼檢查
uv run --extra lint ruff check .
uv run --extra lint mypy .

# 更新依賴
uv lock --upgrade

# 同步依賴（重新安裝）
uv sync

# 查看依賴樹
uv tree
```

## 🔍 疑難排解

### 常見問題

1. **UV 未安裝**

   ```bash
   brew install uv
   ```

2. **Python 版本不符**

   ```bash
   uv python pin 3.11
   ```

3. **依賴衝突**

   ```bash
   uv lock --upgrade
   uv sync
   ```

4. **測試失敗**
   ```bash
   uv run --group dev pytest -v
   ```

## 📚 相關資源

- [UV 官方文件](https://docs.astral.sh/uv/)
- [Google ADK 文件](https://cloud.google.com/agent-builder)
- [LangChain 文件](https://python.langchain.com/)
- [詳細安裝指南](./INSTALLATION_GUIDE.md)

---

🎉 **恭喜！您已成功設置 Software Bug Assistant 專案！**

現在您可以開始開發您的 AI Agent 了！

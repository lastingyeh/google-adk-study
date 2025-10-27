# 教學 03：Chuck Norris OpenAPI 工具代理

一個有趣的代理，展示了如何將 OpenAPIToolset 與 Chuck Norris API 結合使用。此代理可以檢索笑話、搜索特定主題，並使用自動生成的 API 工具列出可用類別。

## 🚀 快速入門

```bash
# 安裝依賴項
make setup

# 啟動代理
make dev

# 打開 http://localhost:8000 並選擇 'chuck_norris_agent'
```

## 💬 功能介紹

- **隨機笑話**：獲取隨機的 Chuck Norris 事實
- **分類篩選**：從特定類別（開發、電影、食物等）獲取笑話
- **搜索功能**：查找包含特定關鍵字的笑話
- **類別列表**：查看所有可用的笑話類別

## 📁 專案結構

```text
tutorial03/
├── chuck_norris_agent/        # 代理實現
│   ├── __init__.py           # 套件標記
│   ├── agent.py              # 帶有 OpenAPI 規範和工具的代理
│   └── .env.example          # 環境變數模板
├── tests/                    # 全面的測試套件
├── requirements.txt          # 依賴項
└── Makefile                 # 構建命令
```

## 🔧 設定

1.  **獲取 API 金鑰**：訪問 [Google AI Studio](https://aistudio.google.com/app/apikey)
2.  **安裝**：`make setup`
3.  **配置**：將 `.env.example` 複製為 `.env` 並添加您的 API 金鑰
4.  **運行**：`make dev`

## 🧪 測試

```bash
make test    # 運行所有測試
make demo    # 查看示範提示
```

## 🎯 試試這些提示

- "給我講一個隨機的 Chuck Norris 笑話"
- "找一些關於程式設計的笑話"
- "有哪些可用的類別？"
- "給我一個隨機的開發類笑話"
- "搜索包含'code'這個詞的笑話"

## 🔧 運作原理

此代理使用 **OpenAPIToolset** 從 Chuck Norris API 的 OpenAPI 規範中自動生成工具。無需手動編寫工具函數！

**自動生成的工具：**

- `get_random_joke(category=None)` - 獲取隨機笑話，可選按類別
- `search_jokes(query)` - 搜索包含關鍵字的笑話
- `get_categories()` - 列出所有可用類別

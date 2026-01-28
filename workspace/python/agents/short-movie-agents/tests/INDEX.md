# 測試檔案索引

快速找到所需的測試檔案和功能。

## 📁 測試檔案結構

```
tests/
├── __init__.py                    # 測試套件初始化
├── conftest.py                    # Pytest 配置 (147 行)
├── README.md                      # 完整測試文件 (393 行)
├── TEST_SUMMARY.md                # 測試建立摘要 (345 行)
├── QUICK_REFERENCE.md             # 快速參考指南 (245 行)
├── unit/                          # 單元測試目錄
│   ├── __init__.py
│   ├── test_imports.py           # 匯入測試 (140 行, 16 測試)
│   ├── test_structure.py         # 結構測試 (143 行, 15 測試)
│   ├── test_agent.py             # Agent 測試 (247 行, 31 測試)
│   ├── test_models.py            # 模型測試 (148 行, 15 測試)
│   ├── test_utils.py             # 工具測試 (153 行, 12 測試)
│   └── test_tools.py             # Tools 測試 (217 行, 12 測試)
└── integration/                   # 整合測試目錄
    ├── __init__.py
    ├── test_agent.py             # Agent 整合測試 (118 行, 3 測試)
    └── test_server_e2e.py        # 伺服器 E2E 測試 (209 行, 6 測試)
```

---

## 🔍 按功能查找測試

### Agent 相關測試

| 功能 | 測試檔案 | 測試類別/函式 |
|------|---------|-------------|
| Director Agent 配置 | `unit/test_agent.py` | `TestRootAgentConfiguration` |
| Story Agent 配置 | `unit/test_agent.py` | `TestStoryAgent` |
| Screenplay Agent 配置 | `unit/test_agent.py` | `TestScreenplayAgent` |
| Storyboard Agent 配置 | `unit/test_agent.py` | `TestStoryboardAgent` |
| Video Agent 配置 | `unit/test_agent.py` | `TestVideoAgent` |
| Agent 整合 | `unit/test_agent.py` | `TestAgentIntegration` |
| Agent 串流執行 | `integration/test_agent.py` | `test_agent_stream()` |
| Agent 會話管理 | `integration/test_agent.py` | `test_agent_session_state()` |

### 工具 (Tools) 測試

| 工具名稱 | 測試檔案 | 測試類別 |
|---------|---------|---------|
| `storyboard_generate` | `unit/test_tools.py` | `TestStoryboardGenerateTool` |
| `video_generate` | `unit/test_tools.py` | `TestVideoGenerateTool` |
| `load_prompt_from_file` | `unit/test_utils.py` | `TestLoadPromptFromFile` |
| `create_bucket_if_not_exists` | `unit/test_utils.py` | `TestCreateBucketIfNotExists` |

### 資料模型測試

| 模型名稱 | 測試檔案 | 測試類別 |
|---------|---------|---------|
| `Request` | `unit/test_models.py` | `TestRequestModel` |
| `Feedback` | `unit/test_models.py` | `TestFeedbackModel` |

### 伺服器測試

| 功能 | 測試檔案 | 測試類別/函式 |
|------|---------|-------------|
| 伺服器啟動 | `integration/test_server_e2e.py` | `server_fixture` |
| 端點測試 | `integration/test_server_e2e.py` | `TestServerEndpoints` |
| 串流測試 | `integration/test_server_e2e.py` | `TestServerStreamingEndpoints` |
| 配置測試 | `integration/test_server_e2e.py` | `TestServerConfiguration` |

### 基礎設施測試

| 功能 | 測試檔案 | 測試類別 |
|------|---------|---------|
| 模組匯入 | `unit/test_imports.py` | `TestImports` |
| 專案結構 | `unit/test_structure.py` | `TestProjectStructure` |
| 環境配置 | `unit/test_structure.py` | `TestEnvironmentConfiguration` |

---

## 📊 測試統計

### 按檔案統計

| 檔案 | 測試數量 | 程式碼行數 |
|------|---------|-----------|
| `test_imports.py` | 16 | 140 |
| `test_structure.py` | 15 | 143 |
| `test_agent.py` (unit) | 31 | 247 |
| `test_models.py` | 15 | 148 |
| `test_utils.py` | 12 | 153 |
| `test_tools.py` | 12 | 217 |
| `test_agent.py` (integration) | 3 | 118 |
| `test_server_e2e.py` | 6 | 209 |
| **總計** | **110** | **1,375** |

### 按類型統計

| 測試類型 | 檔案數 | 測試數量 | 行數 |
|---------|-------|---------|------|
| 單元測試 | 6 | 101 | 1,048 |
| 整合測試 | 2 | 9 | 327 |
| **總計** | **8** | **110** | **1,375** |

---

## 🎯 測試涵蓋的模組

### app/ 模組涵蓋率

| 模組 | 測試檔案 | 涵蓋狀態 |
|------|---------|---------|
| `agent.py` | `test_agent.py`, `test_imports.py` | ✅ 完整 |
| `story_agent.py` | `test_agent.py`, `test_imports.py` | ✅ 完整 |
| `screenplay_agent.py` | `test_agent.py`, `test_imports.py` | ✅ 完整 |
| `storyboard_agent.py` | `test_agent.py`, `test_tools.py` | ✅ 完整 |
| `video_agent.py` | `test_agent.py`, `test_tools.py` | ✅ 完整 |
| `server.py` | `test_server_e2e.py`, `test_imports.py` | ✅ 完整 |

### app/utils/ 模組涵蓋率

| 模組 | 測試檔案 | 涵蓋狀態 |
|------|---------|---------|
| `utils.py` | `test_utils.py` | ✅ 完整 |
| `typing.py` | `test_models.py` | ✅ 完整 |
| `gcs.py` | `test_utils.py` | ✅ 完整 |
| `tracing.py` | `test_utils.py` | ✅ 完整 |

### app/prompts/ 涵蓋率

| 檔案 | 測試方式 | 涵蓋狀態 |
|------|---------|---------|
| `director_agent.txt` | `test_structure.py`, `test_utils.py` | ✅ 完整 |
| `story_agent.txt` | `test_structure.py`, `test_utils.py` | ✅ 完整 |
| `screenplay_agent.txt` | `test_structure.py`, `test_utils.py` | ✅ 完整 |
| `storyboard_agent.txt` | `test_structure.py` | ✅ 完整 |
| `video_agent.txt` | `test_structure.py` | ✅ 完整 |

---

## 🔧 共用 Fixtures

### conftest.py 提供的 Fixtures

| Fixture 名稱 | 用途 | 範圍 |
|-------------|------|------|
| `test_config` | 測試配置字典 | session |
| `mock_tool_context` | 模擬 ToolContext | function |
| `mock_storage_client` | 模擬 GCS 客戶端 | function |
| `mock_logging_client` | 模擬 Logging 客戶端 | function |
| `sample_content` | 測試用 Content 物件 | function |
| `sample_request` | 測試用 Request 物件 | function |
| `sample_feedback` | 測試用 Feedback 物件 | function |
| `sample_story` | 測試用故事文本 | function |
| `sample_screenplay` | 測試用劇本文本 | function |
| `sample_storyboard_prompt` | 測試用分鏡提示詞 | function |
| `sample_video_prompt` | 測試用影片提示詞 | function |
| `reset_environment` | 重置環境變數 | function (autouse) |
| `mock_vertexai_init` | 模擬 Vertex AI 初始化 | function |
| `mock_image_generation_model` | 模擬影像生成模型 | function |
| `mock_video_generation_client` | 模擬影片生成客戶端 | function |
| `test_environment_variables` | 測試環境變數集合 | session |

---

## 🏷️ Pytest 標記 (Markers)

| 標記 | 用途 | 使用範例 |
|------|------|---------|
| `unit` | 單元測試 | `pytest -m unit` |
| `integration` | 整合測試 | `pytest -m integration` |
| `e2e` | 端對端測試 | `pytest -m e2e` |
| `slow` | 執行緩慢的測試 | `pytest -m "not slow"` |

---

## 📖 文件檔案

| 檔案 | 用途 | 行數 |
|------|------|------|
| `README.md` | 完整測試文件與使用指南 | 393 |
| `TEST_SUMMARY.md` | 測試建立過程摘要 | 345 |
| `QUICK_REFERENCE.md` | 常用指令快速參考 | 245 |
| `INDEX.md` | 本檔案 - 測試檔案索引 | 253 |

---

## 🚀 快速開始

### 1. 執行所有測試
```bash
pytest
```

### 2. 查看測試涵蓋率
```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### 3. 執行特定測試
```bash
# 測試 Agent 配置
pytest tests/unit/test_agent.py -v

# 測試工具函式
pytest tests/unit/test_tools.py -v

# 測試伺服器
pytest tests/integration/test_server_e2e.py -v
```

---

## 📞 需要幫助？

- 📖 查看 [完整文件](./README.md)
- 🚀 查看 [快速參考](./QUICK_REFERENCE.md)
- 📊 查看 [測試摘要](./TEST_SUMMARY.md)

---

**最後更新：** 2026 年 1 月 28 日
**總測試數：** 110
**總檔案數：** 15

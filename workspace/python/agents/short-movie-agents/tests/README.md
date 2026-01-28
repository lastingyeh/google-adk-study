# 測試文件

本目錄包含 `short-movie-agents` 專案的完整測試套件。

## 📁 測試結構

```
tests/
├── __init__.py                    # 測試套件初始化
├── conftest.py                    # Pytest 配置與共用 fixtures
├── unit/                          # 單元測試
│   ├── __init__.py
│   ├── test_imports.py           # 匯入測試
│   ├── test_structure.py         # 結構測試
│   ├── test_agent.py             # Agent 配置測試
│   ├── test_models.py            # Pydantic 模型測試
│   ├── test_utils.py             # 工具函式測試
│   └── test_tools.py             # 工具（Tools）測試
└── integration/                   # 整合測試
    ├── __init__.py
    ├── test_agent.py             # Agent 整合測試
    └── test_server_e2e.py        # 伺服器端對端測試
```

## 🧪 測試類型

### 單元測試 (Unit Tests)

單元測試專注於測試個別元件的功能：

1. **test_imports.py** - 匯入測試
   - 測試所有模組能否正確匯入
   - 驗證相依套件是否可用
   - 確保無循環相依問題

2. **test_structure.py** - 結構測試
   - 驗證專案檔案結構完整性
   - 檢查必要的設定檔是否存在
   - 確認提示詞檔案存在

3. **test_agent.py** - Agent 配置測試
   - 測試根 Agent (Director Agent) 配置
   - 測試所有子 Agent (Story, Screenplay, Storyboard, Video) 配置
   - 驗證 Agent 屬性正確性

4. **test_models.py** - Pydantic 模型測試
   - 測試 Request 模型
   - 測試 Feedback 模型
   - 驗證資料驗證邏輯

5. **test_utils.py** - 工具函式測試
   - 測試 `load_prompt_from_file` 函式
   - 測試 `create_bucket_if_not_exists` 函式
   - 測試 `CloudTraceLoggingSpanExporter` 類別

6. **test_tools.py** - Agent 工具測試
   - 測試 `storyboard_generate` 工具
   - 測試 `video_generate` 工具
   - 驗證錯誤處理機制

### 整合測試 (Integration Tests)

整合測試驗證多個元件協同工作：

1. **test_agent.py** - Agent 整合測試
   - 測試 Agent 串流功能
   - 測試 Agent 執行流程
   - 測試會話狀態管理

2. **test_server_e2e.py** - 伺服器端對端測試
   - 測試 FastAPI 伺服器啟動
   - 測試 API 端點功能
   - 測試回饋收集機制

## 🚀 執行測試

### 執行所有測試

```bash
pytest
```

### 執行特定測試類型

```bash
# 只執行單元測試
pytest tests/unit/

# 只執行整合測試
pytest tests/integration/

# 使用標記執行
pytest -m unit           # 單元測試
pytest -m integration    # 整合測試
pytest -m "not slow"     # 排除緩慢的測試
```

### 執行特定測試檔案

```bash
# 執行匯入測試
pytest tests/unit/test_imports.py

# 執行 Agent 測試
pytest tests/unit/test_agent.py

# 執行整合測試
pytest tests/integration/test_agent.py
```

### 執行特定測試函式

```bash
# 執行特定測試類別
pytest tests/unit/test_agent.py::TestStoryAgent

# 執行特定測試函式
pytest tests/unit/test_agent.py::TestStoryAgent::test_story_agent_exists
```

### 詳細輸出模式

```bash
# 詳細輸出
pytest -v

# 顯示 print 輸出
pytest -s

# 停在第一個失敗
pytest -x

# 顯示最慢的測試
pytest --durations=10
```

### 涵蓋率測試

```bash
# 執行測試並產生涵蓋率報告
pytest --cov=app --cov-report=html --cov-report=term

# 查看 HTML 涵蓋率報告
open htmlcov/index.html
```

### 並行執行

```bash
# 使用多核心並行執行（需要 pytest-xdist）
pytest -n auto
```

## 📊 測試涵蓋範圍

### 已涵蓋的模組

- ✅ `app/agent.py` - Director Agent
- ✅ `app/story_agent.py` - Story Agent
- ✅ `app/screenplay_agent.py` - Screenplay Agent
- ✅ `app/storyboard_agent.py` - Storyboard Agent
- ✅ `app/video_agent.py` - Video Agent
- ✅ `app/server.py` - FastAPI 伺服器
- ✅ `app/utils/utils.py` - 工具函式
- ✅ `app/utils/typing.py` - 型別定義
- ✅ `app/utils/gcs.py` - GCS 工具
- ✅ `app/utils/tracing.py` - 追蹤工具

### 測試涵蓋率目標

- 核心功能：≥ 90%
- 工具函式：≥ 80%
- 整體專案：≥ 70%

## 🛠️ 測試配置

### Pytest 標記

測試使用以下標記進行分類：

- `unit` - 單元測試
- `integration` - 整合測試
- `e2e` - 端對端測試
- `slow` - 執行緩慢的測試（可能需要較長時間或外部 API）

### 共用 Fixtures

`conftest.py` 提供以下共用 fixtures：

- `test_config` - 測試配置
- `mock_tool_context` - 模擬 ToolContext
- `mock_storage_client` - 模擬 GCS 客戶端
- `mock_logging_client` - 模擬 Logging 客戶端
- `sample_content` - 測試用 Content 物件
- `sample_request` - 測試用 Request 物件
- `sample_feedback` - 測試用 Feedback 物件
- `sample_story` - 測試用故事文本
- `sample_screenplay` - 測試用劇本文本

## ⚠️ 注意事項

### Mock 外部服務

大部分測試使用 mock 來隔離外部服務：

- Vertex AI 影像生成 API
- Veo 影片生成 API
- Google Cloud Storage
- Google Cloud Logging

### 跳過的測試

某些測試因需要真實 API 金鑰而被跳過：

```python
@pytest.mark.skip(reason="需要實際的 API 金鑰和足夠的配額")
def test_streaming_endpoint(self):
    # 需要真實的 Google Cloud 配置
    pass
```

如需執行這些測試，請：
1. 設定適當的環境變數
2. 確保有足夠的 API 配額
3. 移除 `@pytest.mark.skip` 裝飾器

### 環境變數

測試期間需要以下環境變數（在 `conftest.py` 中已模擬）：

```
GOOGLE_CLOUD_PROJECT=test-project-123
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_CLOUD_BUCKET_NAME=test-bucket
```

## 📝 新增測試

### 新增單元測試

1. 在 `tests/unit/` 下建立新的測試檔案
2. 遵循命名慣例：`test_<module_name>.py`
3. 使用描述性的測試類別和函式名稱
4. 使用 AAA 模式（Arrange-Act-Assert）

範例：

```python
class TestNewFeature:
    """測試新功能。"""

    def test_feature_works(self):
        """測試功能正常運作。"""
        # Arrange
        input_data = "test"

        # Act
        result = new_feature(input_data)

        # Assert
        assert result is not None
```

### 新增整合測試

1. 在 `tests/integration/` 下建立測試檔案
2. 使用 `@pytest.mark.integration` 標記
3. 測試多個元件的互動
4. 適當使用 fixtures

## 🔍 除錯測試

### 查看詳細輸出

```bash
# 顯示所有 print 輸出
pytest -s

# 顯示本地變數
pytest -l

# 進入除錯器
pytest --pdb
```

### 只執行失敗的測試

```bash
# 重新執行上次失敗的測試
pytest --lf

# 先執行上次失敗的測試，然後執行其他測試
pytest --ff
```

## 📚 參考資源

- [Pytest 官方文件](https://docs.pytest.org/)
- [Google ADK 文件](https://cloud.google.com/generative-ai-sdk)
- [Pydantic 文件](https://docs.pydantic.dev/)
- [FastAPI 測試文件](https://fastapi.tiangolo.com/tutorial/testing/)

## ✅ 測試檢查清單

新增功能時的測試檢查清單：

- [ ] 建立對應的單元測試
- [ ] 測試正常路徑
- [ ] 測試錯誤情況
- [ ] 測試邊界條件
- [ ] 使用適當的 mock
- [ ] 測試通過
- [ ] 涵蓋率符合目標
- [ ] 更新測試文件

---

**最後更新：** 2026 年 1 月 28 日

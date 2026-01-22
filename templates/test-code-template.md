# ADK Agent 測試程式碼範本

此範本包含基於 `google-adk` 開發的 Agent 所需的單元測試與整合測試程式碼結構。

## 1. 單元測試 (Unit Tests)

將此檔案儲存為 `tests/unit/test_agent.py`。

```python
"""
Agent 配置與功能單元測試
"""
import pytest
from app.agent import root_agent
# 若有其他子 Agent 或工具，請在此導入
# from app.agent import sub_agent_1, custom_tool

class TestAgentConfiguration:
    """測試 Agent 基本配置與屬性。"""

    def test_root_agent_exists(self):
        """驗證 root_agent 是否已正確定義。"""
        assert root_agent is not None

    def test_agent_has_correct_name(self):
        """驗證 Agent 名稱是否正確。"""
        # 請替換 {expected_name} 為實際 Agent 名稱
        assert root_agent.name == "{expected_name}"

    def test_agent_has_correct_model(self):
        """驗證 Agent 是否使用預期的模型。"""
        # 請替換 {expected_model} 為實際模型 ID (例如: gemini-2.0-flash)
        assert root_agent.model == "{expected_model}"

    def test_agent_has_description(self):
        """驗證 Agent 是否擁有描述文字。"""
        assert root_agent.description is not None
        assert len(root_agent.description) > 0

    def test_agent_has_instruction(self):
        """驗證 Agent 是否擁有指令 (Instruction)。"""
        assert root_agent.instruction is not None
        assert len(root_agent.instruction) > 0

    def test_agent_tools_configuration(self):
        """驗證 Agent 工具配置。"""
        # 若 Agent 應包含工具，請取消註解並修改
        # assert hasattr(root_agent, "tools")
        # assert len(root_agent.tools) > 0
        pass

    def test_sub_agents_configuration(self):
        """驗證子 Agent (Sub-agents) 配置。"""
        # 若 Agent 為協調者 (Orchestrator)，請取消註解並修改
        # assert hasattr(root_agent, "sub_agents")
        # assert len(root_agent.sub_agents) > 0
        pass

class TestAgentCallbacks:
    """測試 Agent 回調函式 (若有)。"""

    def test_callbacks_registered(self):
        # 檢查特定回調是否存在
        # from app.agent import specific_callback
        # assert callable(specific_callback)
        pass
```

## 2. 整合測試 (Integration Tests)

將此檔案儲存為 `tests/integration/test_agent.py`。

```python
"""
Agent 端對端整合測試
"""
import pytest
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agent import root_agent

def test_agent_stream_response():
    """
    測試 Agent 串流回應功能。
    驗證 Agent 能接收訊息並回傳包含文字的串流事件。
    """

    # 1. 初始化記憶體會話服務
    session_service = InMemorySessionService()
    test_app_name = "test-app"
    test_user_id = "test-user"

    # 2. 建立測試會話
    session = session_service.create_session_sync(
        user_id=test_user_id,
        app_name=test_app_name
    )

    # 3. 初始化執行器 (Runner)
    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name=test_app_name
    )

    # 4. 準備測試訊息
    # 請替換 {test_query} 為適合該 Agent 的測試問題
    test_query = "{test_query}"
    message = types.Content(
        role="user",
        parts=[types.Part.from_text(text=test_query)]
    )

    # 5. 執行 Agent 並收集串流事件
    events = list(
        runner.run(
            new_message=message,
            user_id=test_user_id,
            session_id=session.id,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        )
    )

    # 6. 驗證結果
    assert len(events) > 0, "Agent 應該回傳至少一個事件"

    # 檢查是否包含有效的文字內容
    has_text_content = False
    for event in events:
        if (
            event.content
            and event.content.parts
            and any(part.text for part in event.content.parts)
        ):
            has_text_content = True
            # 可在此添加更多針對回應內容的斷言
            # print(event.content.parts[0].text)
            break

    assert has_text_content, "Agent 回應中應包含文字內容"
```

## 使用說明

1.  **安裝依賴**: 確保已安裝 `pytest` 和 `google-adk`。
2.  **檔案放置**:
    *   在專案根目錄下建立 `tests/unit` 和 `tests/integration` 資料夾。
    *   將上述程式碼分別儲存為 `tests/unit/test_agent.py` 和 `tests/integration/test_agent.py`。
3.  **填寫參數**: 替換範本中的 `{expected_name}`, `{expected_model}`, `{test_query}` 等佔位符。
4.  **執行測試**: 在終端機執行 `pytest`。

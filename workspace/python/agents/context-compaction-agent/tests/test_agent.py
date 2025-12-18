"""測試 Context Compaction Agent 的結構與配置。"""

from context_compaction_agent import root_agent


class TestAgentConfiguration:
  """測試 Agent 配置與基本設定。"""

  def test_agent_exists(self):
    """測試 root_agent 是否正確定義。

    重點說明:
    1. 驗證 root_agent 物件是否存在
    2. 驗證 root_agent 具有 name 屬性
    """
    assert root_agent is not None
    assert hasattr(root_agent, "name")

  def test_agent_name(self):
    """測試 Agent 是否具有正確名稱。

    重點說明:
    1. 驗證 agent 名稱是否為 'context_compaction_agent'
    """
    assert root_agent.name == "context_compaction_agent"

  def test_agent_model(self):
    """測試 Agent 是否使用正確的模型。

    重點說明:
    1. 驗證模型是否設定為 'gemini-2.0-flash'
    """
    assert root_agent.model == "gemini-2.0-flash"

  def test_agent_description(self):
    """測試 Agent 是否有具意義的描述。

    重點說明:
    1. 驗證描述屬性是否存在
    2. 驗證描述中包含 'context compaction' 關鍵字
    """
    assert root_agent.description
    assert "context compaction" in root_agent.description.lower()

  def test_agent_instruction(self):
    """測試 Agent 是否有完整的指示說明。

    重點說明:
    1. 驗證 instruction 屬性是否存在
    2. 驗證指示長度大於 100 字元，確保內容完整
    """
    assert root_agent.instruction
    assert len(root_agent.instruction) > 100

  def test_agent_has_tools(self):
    """測試 Agent 是否配置了工具。

    重點說明:
    1. 驗證 tools 屬性是否存在
    2. 驗證工具列表不為空
    3. 驗證至少包含 2 個工具
    """
    assert hasattr(root_agent, "tools")
    assert root_agent.tools is not None
    # 應該至少包含 agent.py 中定義的工具
    assert len(root_agent.tools) >= 2

  def test_agent_tool_names(self):
    """測試 Agent 工具是否具有預期的名稱。

    重點說明:
    1. 取得所有工具名稱
    2. 驗證包含 'summarize_text'
    3. 驗證包含 'calculate_complexity'
    """
    tool_names = [tool.__name__ for tool in root_agent.tools]
    assert "summarize_text" in tool_names
    assert "calculate_complexity" in tool_names


class TestToolFunctionality:
  """測試 Agent 可用的工具功能。"""

  def test_summarize_text_tool(self):
    """測試 summarize_text 工具運作正確。

    重點說明:
    1. 使用長文本進行測試
    2. 驗證回傳狀態為 'success'
    3. 驗證回傳包含報告與摘要
    4. 驗證摘要長度小於原始文本
    """
    from context_compaction_agent.agent import summarize_text

    # 使用長文本測試
    long_text = "x" * 300
    result = summarize_text(long_text)
    assert result["status"] == "success"
    assert "report" in result
    assert "summary" in result
    assert len(result["summary"]) < len(long_text)

  def test_summarize_text_short_text(self):
    """測試 summarize_text 處理短文本的情況。

    重點說明:
    1. 使用短文本 'Hello world' 測試
    2. 驗證回傳狀態為 'success'
    3. 驗證摘要內容等於原始文本（不需摘要）
    """
    from context_compaction_agent.agent import summarize_text

    short_text = "Hello world"
    result = summarize_text(short_text)
    assert result["status"] == "success"
    assert result["summary"] == short_text

  def test_calculate_complexity_tool(self):
    """測試 calculate_complexity 工具運作正確。

    重點說明:
    1. 使用複雜問題進行測試
    2. 驗證回傳狀態為 'success'
    3. 驗證回傳包含複雜度等級與字數統計
    4. 驗證複雜度等級在合法範圍內 ['low', 'medium', 'high']
    """
    from context_compaction_agent.agent import calculate_complexity

    # 使用複雜問題測試
    complex_q = "What is the best way to implement context compaction in multi-turn conversations?"
    result = calculate_complexity(complex_q)
    assert result["status"] == "success"
    assert "complexity_level" in result
    assert result["complexity_level"] in ["low", "medium", "high"]
    assert "word_count" in result

  def test_calculate_complexity_simple(self):
    """測試 calculate_complexity 處理簡單輸入的情況。

    重點說明:
    1. 使用簡單問候 'Hi' 測試
    2. 驗證回傳狀態為 'success'
    3. 驗證複雜度等級為 'low'
    """
    from context_compaction_agent.agent import calculate_complexity

    simple_q = "Hi"
    result = calculate_complexity(simple_q)
    assert result["status"] == "success"
    assert result["complexity_level"] == "low"

  def test_calculate_complexity_medium(self):
    """測試 calculate_complexity 處理中等輸入的情況。

    重點說明:
    1. 使用中等長度問題測試
    2. 驗證回傳狀態為 'success'
    3. 驗證複雜度等級為 'low' 或 'medium'
    """
    from context_compaction_agent.agent import calculate_complexity

    medium_q = "How do you use context compaction?"
    result = calculate_complexity(medium_q)
    assert result["status"] == "success"
    assert result["complexity_level"] in ["low", "medium"]


class TestImports:
  """測試必要模組是否可被匯入。"""

  def test_import_agent_module(self):
    """測試 agent 模組匯入成功。

    重點說明:
    1. 嘗試匯入 context_compaction_agent.agent
    2. 驗證匯入物件不為 None
    """
    from context_compaction_agent import agent
    assert agent is not None

  def test_import_root_agent(self):
    """測試 root_agent 可被匯入。

    重點說明:
    1. 從模組匯入 root_agent
    2. 驗證物件存在且名稱正確
    """
    from context_compaction_agent.agent import root_agent as imported_agent
    assert imported_agent is not None
    assert imported_agent.name == "context_compaction_agent"

  def test_import_tools(self):
    """測試工具可被匯入。

    重點說明:
    1. 匯入 summarize_text 與 calculate_complexity
    2. 驗證它們是可呼叫的函式 (callable)
    """
    from context_compaction_agent.agent import (
        summarize_text,
        calculate_complexity,
    )
    assert callable(summarize_text)
    assert callable(calculate_complexity)


class TestAppConfiguration:
  """測試 App 的 Compaction 配置。"""

  def test_app_imports(self):
    """測試 app 配置可被匯入。

    重點說明:
    1. 從 app 模組匯入 app 物件
    2. 驗證物件不為 None
    """
    from app import app
    assert app is not None

  def test_app_has_root_agent(self):
    """測試 app 是否配置了 root_agent。

    重點說明:
    1. 驗證 app 物件具有 root_agent 屬性
    """
    from app import app
    assert hasattr(app, "root_agent")

  def test_compaction_config_imports(self):
    """測試 EventsCompactionConfig 可被匯入。

    重點說明:
    1. 從 google.adk.apps.app 匯入 EventsCompactionConfig
    2. 驗證類別存在
    """
    from google.adk.apps.app import EventsCompactionConfig
    assert EventsCompactionConfig is not None

  def test_compaction_config_creation(self):
    """測試 EventsCompactionConfig 可被建立。

    重點說明:
    1. 實例化 EventsCompactionConfig 並設定參數
    2. 驗證 compaction_interval 屬性正確
    3. 驗證 overlap_size 屬性正確
    """
    from google.adk.apps.app import EventsCompactionConfig

    config = EventsCompactionConfig(
        compaction_interval=5,
        overlap_size=1,
    )
    assert config.compaction_interval == 5
    assert config.overlap_size == 1

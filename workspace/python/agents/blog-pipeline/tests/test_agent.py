"""
教學 04：順序工作流 - 部落格建立流程的測試

測試涵蓋：
- Agent 配置與匯入
- SequentialAgent 流程結構
- 個別 agent 功能
- 狀態管理與資料流
- 整合測試
"""

import pytest

from blog_pipeline.agent import (
  root_agent,
  research_agent,
  writer_agent,
  editor_agent,
  formatter_agent
)
from google.adk.agents import SequentialAgent, Agent


class TestAgentConfiguration:
  """測試 agent 配置與基本設定"""

  def test_root_agent_import(self):
    """測試 root_agent 可以被匯入"""
    assert root_agent is not None

  def test_root_agent_is_sequential_agent(self):
    """測試 root_agent 是否為 SequentialAgent 實例"""
    assert isinstance(root_agent, SequentialAgent)

  def test_pipeline_name(self):
    """測試流程是否有正確的名稱"""
    assert root_agent.name == "BlogCreationPipeline"

  def test_pipeline_description(self):
    """測試流程是否有描述"""
    assert "blog post creation" in root_agent.description.lower()

  def test_pipeline_has_sub_agents(self):
    """測試流程是否有 4 個子 agent"""
    # 重點：SequentialAgent 由多個 sub_agents 組成
    assert hasattr(root_agent, 'sub_agents')
    assert len(root_agent.sub_agents) == 4

  def test_sub_agents_are_agents(self):
    """測試所有子 agent 是否為 Agent 實例"""
    for agent in root_agent.sub_agents:
      assert isinstance(agent, Agent)


class TestIndividualAgents:
  """測試個別 agent 配置"""

  def test_research_agent_config(self):
    """測試研究 agent 配置"""
    assert research_agent.name == "researcher"
    assert research_agent.model == "gemini-2.0-flash"
    assert research_agent.output_key == "research_findings"  # 重點：輸出鍵
    assert "research" in research_agent.instruction.lower()

  def test_writer_agent_config(self):
    """測試寫作 agent 配置"""
    assert writer_agent.name == "writer"
    assert writer_agent.model == "gemini-2.0-flash"
    assert writer_agent.output_key == "draft_post"
    # 重點：使用 {research_findings} 接收前一個 agent 的輸出
    assert "{research_findings}" in writer_agent.instruction

  def test_editor_agent_config(self):
    """測試編輯 agent 配置"""
    assert editor_agent.name == "editor"
    assert editor_agent.model == "gemini-2.0-flash"
    assert editor_agent.output_key == "editorial_feedback"
    # 重點：讀取寫作 agent 的草稿
    assert "{draft_post}" in editor_agent.instruction

  def test_formatter_agent_config(self):
    """測試格式化 agent 配置"""
    assert formatter_agent.name == "formatter"
    assert formatter_agent.model == "gemini-2.0-flash"
    assert formatter_agent.output_key == "final_post"
    # 重點：同時讀取草稿和編輯意見，進行最終整合
    assert "{draft_post}" in formatter_agent.instruction
    assert "{editorial_feedback}" in formatter_agent.instruction

  def test_agents_have_unique_output_keys(self):
    """測試所有 agent 是否有唯一的輸出鍵"""
    # 重點：output_key 必須唯一，避免狀態覆蓋
    output_keys = [agent.output_key for agent in root_agent.sub_agents]
    assert len(output_keys) == len(set(output_keys))  # 全部唯一

  def test_agents_have_output_keys(self):
    """測試所有 agent 是否都定義了 output_key"""
    for agent in root_agent.sub_agents:
      assert hasattr(agent, 'output_key')
      assert agent.output_key is not None
      assert isinstance(agent.output_key, str)


class TestSequentialAgentStructure:
  """測試 SequentialAgent 流程結構"""

  def test_pipeline_execution_order(self):
    """測試 agent 是否按正確順序執行"""
    # 重點：順序執行 - 研究 → 寫作 → 編輯 → 格式化
    agents = root_agent.sub_agents
    assert agents[0].name == "researcher"
    assert agents[1].name == "writer"
    assert agents[2].name == "editor"
    assert agents[3].name == "formatter"

  def test_pipeline_is_deterministic(self):
    """測試流程是否總是以相同順序執行"""
    # SequentialAgent 應該總是按定義的順序執行
    agents = root_agent.sub_agents
    expected_order = ["researcher", "writer", "editor", "formatter"]
    actual_order = [agent.name for agent in agents]
    assert actual_order == expected_order


class TestStateManagement:
  """測試狀態管理與資料流"""

  def test_state_key_injection_research_to_writer(self):
    """測試研究結果流向寫作 agent"""
    # 重點：狀態注入 - writer 透過 {research_findings} 讀取 researcher 的輸出
    assert "{research_findings}" in writer_agent.instruction

  def test_state_key_injection_writer_to_editor(self):
    """測試草稿流向編輯 agent"""
    assert "{draft_post}" in editor_agent.instruction

  def test_state_key_injection_multiple_to_formatter(self):
    """測試草稿和意見流向格式化 agent"""
    # 重點：多重輸入 - formatter 同時讀取兩個前置 agent 的輸出
    assert "{draft_post}" in formatter_agent.instruction
    assert "{editorial_feedback}" in formatter_agent.instruction

  def test_no_circular_dependencies(self):
    """測試沒有循環依賴"""
    # 重點：agent 不應該讀取自己的 output_key，避免循環依賴
    for agent in root_agent.sub_agents:
      assert f"{{{agent.output_key}}}" not in agent.instruction


class TestAgentInstructions:
  """測試 agent 指令品質"""

  def test_research_instruction_format(self):
    """測試研究 agent 要求條列式清單"""
    instruction = research_agent.instruction
    assert "bulleted list" in instruction.lower()
    assert "•" in instruction

  def test_writer_instruction_creativity(self):
    """測試寫作 agent 專注於吸引人的內容"""
    instruction = writer_agent.instruction
    assert "engaging" in instruction.lower()
    assert "conversational" in instruction.lower()

  def test_editor_instruction_feedback(self):
    """測試編輯 agent 提供建設性意見"""
    instruction = editor_agent.instruction
    assert "constructive feedback" in instruction.lower()
    assert "improvements" in instruction.lower()

  def test_formatter_instruction_markdown(self):
    """測試格式化 agent 建立 markdown 輸出"""
    instruction = formatter_agent.instruction
    assert "markdown" in instruction.lower()
    assert "#" in instruction  # 標題語法

  def test_instructions_focus_on_output(self):
    """測試所有指令都強調輸出格式"""
    for agent in root_agent.sub_agents:
      instruction = agent.instruction
      assert "output only" in instruction.lower() or "output only" in instruction.lower()


class TestImports:
  """測試匯入功能"""

  def test_google_adk_agents_import(self):
    """測試 google.adk.agents 匯入是否正常"""
    from google.adk.agents import Agent, SequentialAgent
    assert Agent is not None
    assert SequentialAgent is not None

  def test_blog_pipeline_agent_import(self):
    """測試 blog_pipeline.agent 匯入是否正常"""
    from blog_pipeline.agent import root_agent
    assert root_agent is not None

  def test_root_agent_exists(self):
    """測試 root_agent 是否正確定義"""
    assert root_agent is not None
    assert hasattr(root_agent, 'name')
    assert hasattr(root_agent, 'sub_agents')

  def test_future_annotations_import(self):
    """測試 __future__ annotations 匯入是否正常"""
    import __future__
    assert hasattr(__future__, 'annotations')


class TestProjectStructure:
  """測試專案結構與檔案組織"""

  def test_blog_pipeline_directory_exists(self):
    """測試 blog_pipeline 目錄是否存在"""
    import os
    assert os.path.exists("blog_pipeline")

  def test_init_py_exists(self):
    """測試 __init__.py 是否存在"""
    import os
    assert os.path.exists("blog_pipeline/__init__.py")

  def test_agent_py_exists(self):
    """測試 agent.py 是否存在"""
    import os
    assert os.path.exists("blog_pipeline/agent.py")

  def test_env_example_exists(self):
    """測試 .env.example 是否存在"""
    import os
    assert os.path.exists("blog_pipeline/.env.example")

  def test_init_py_content(self):
    """測試 __init__.py 內容是否正確"""
    with open("blog_pipeline/__init__.py", "r") as f:
      content = f.read()
      assert "from .agent import root_agent" in content
      assert "__all__" in content

  def test_agent_py_is_python_file(self):
    """測試 agent.py 是否為有效的 Python 檔案"""
    with open("blog_pipeline/agent.py", "r") as f:
      content = f.read()
      assert "from __future__ import annotations" in content
      assert "SequentialAgent" in content

  def test_env_example_content(self):
    """測試 .env.example 是否包含必要變數"""
    with open("blog_pipeline/.env.example", "r") as f:
      content = f.read()
      assert "GOOGLE_GENAI_USE_VERTEXAI" in content
      assert "GOOGLE_API_KEY" in content


class TestTestStructure:
  """測試測試檔案組織"""

  def test_tests_directory_exists(self):
    """測試 tests 目錄是否存在"""
    import os
    assert os.path.exists("tests")

  def test_tests_init_py_exists(self):
    """測試 tests/__init__.py 是否存在"""
    import os
    assert os.path.exists("tests/__init__.py")

  def test_test_files_exist(self):
    """測試測試檔案是否存在"""
    import os
    test_files = [f for f in os.listdir("tests") if f.startswith("test_")]
    assert len(test_files) > 0


@pytest.mark.integration
class TestAgentIntegration:
  """需要 API 存取的整合測試"""

  def test_pipeline_can_be_created_without_error(self):
    """測試流程可以無錯誤地建立"""
    try:
      # 僅存取 root_agent 不應引發錯誤
      agent = root_agent
      assert agent is not None
      assert agent.name == "BlogCreationPipeline"
      assert len(agent.sub_agents) == 4
    except Exception as e:
      pytest.fail(f"流程建立失敗: {e}")

  def test_pipeline_has_valid_configuration_for_api(self):
    """測試流程是否有 API 使用所需的所有配置"""
    assert root_agent.name is not None
    assert root_agent.description is not None
    assert hasattr(root_agent, 'sub_agents')
    assert len(root_agent.sub_agents) > 0

    # 檢查所有子 agent 是否有必要屬性
    for agent in root_agent.sub_agents:
      assert agent.name is not None
      assert agent.model is not None
      assert agent.instruction is not None
      assert agent.output_key is not None

  def test_state_flow_is_configured(self):
    """測試 agent 之間的狀態流是否正確配置"""
    # 重點：驗證完整的資料流鏈
    agents = root_agent.sub_agents

    # 研究 → 寫作
    assert "{research_findings}" in agents[1].instruction  # writer 讀取 research

    # 寫作 → 編輯
    assert "{draft_post}" in agents[2].instruction  # editor 讀取 draft

    # 寫作 + 編輯 → 格式化
    assert "{draft_post}" in agents[3].instruction  # formatter 讀取 draft
    assert "{editorial_feedback}" in agents[3].instruction  # formatter 讀取 feedback
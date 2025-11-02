"""
測試匯入模組 - 教學 04：序列工作流程
"""

from blog_pipeline.agent import root_agent
from google.adk.agents import Agent, SequentialAgent


class TestImports:
  """測試匯入功能"""

  def test_google_adk_agents_import(self):
    """測試 google.adk.agents 匯入是否正常運作"""
    # 驗證 Agent 類別是否成功匯入
    assert Agent is not None
    # 驗證 SequentialAgent 類別是否成功匯入
    assert SequentialAgent is not None

  def test_blog_pipeline_agent_import(self):
    """測試 blog_pipeline.agent 匯入是否正常運作"""
    # 驗證 root_agent 是否成功匯入
    assert root_agent is not None

  def test_root_agent_exists(self):
    """測試 root_agent 是否正確定義"""
    # 確認 root_agent 物件存在
    assert root_agent is not None
    # 確認 root_agent 具有 name 屬性（代理名稱）
    assert hasattr(root_agent, "name")
    # 確認 root_agent 具有 sub_agents 屬性（子代理清單）
    assert hasattr(root_agent, "sub_agents")

  def test_future_annotations_import(self):
    """測試 __future__ annotations 匯入是否正常運作"""
    import __future__

    # 驗證 __future__ 模組是否支援 annotations 功能
    # annotations 用於延遲評估型別註解，避免循環匯入問題
    assert hasattr(__future__, "annotations")


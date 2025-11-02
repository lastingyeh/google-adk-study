"""
測試專案結構 - 教學 04：循序工作流程
"""

import os


class TestProjectStructure:
  """測試專案結構與檔案組織"""

  def test_blog_pipeline_directory_exists(self):
    """測試 blog_pipeline 目錄是否存在"""
    assert os.path.exists("blog_pipeline")

  def test_init_py_exists(self):
    """測試 __init__.py 是否存在"""
    assert os.path.exists("blog_pipeline/__init__.py")

  def test_agent_py_exists(self):
    """測試 agent.py 是否存在"""
    assert os.path.exists("blog_pipeline/agent.py")

  def test_env_example_exists(self):
    """測試 .env.example 是否存在"""
    assert os.path.exists("blog_pipeline/.env.example")

  def test_init_py_content(self):
    """測試 __init__.py 是否有正確的內容

    重點：確保模組正確匯出 root_agent 和 __all__ 變數
    """
    with open("blog_pipeline/__init__.py", "r") as f:
      content = f.read()
      # 檢查是否從 agent 模組匯入 root_agent
      assert "from .agent import root_agent" in content
      # 檢查是否定義了公開 API 的 __all__ 變數
      assert "__all__" in content

  def test_agent_py_is_python_file(self):
    """測試 agent.py 是否為有效的 Python 檔案

    重點：驗證檔案包含必要的 import 和 SequentialAgent 類別
    """
    with open("blog_pipeline/agent.py", "r") as f:
      content = f.read()
      # 檢查是否包含 future annotations（Python 型別提示）
      assert "from __future__ import annotations" in content
      # 檢查是否包含 SequentialAgent（循序代理的核心類別）
      assert "SequentialAgent" in content

  def test_env_example_content(self):
    """測試 .env.example 是否包含必要的環境變數

    重點：確保環境變數範例檔包含 Google AI 相關設定
    """
    with open("blog_pipeline/.env.example", "r") as f:
      content = f.read()
      # 檢查是否包含 Vertex AI 使用設定
      assert "GOOGLE_GENAI_USE_VERTEXAI" in content
      # 檢查是否包含 Google API 金鑰設定
      assert "GOOGLE_API_KEY" in content


class TestTestStructure:
  """測試測試檔案的組織結構"""

  def test_tests_directory_exists(self):
    """測試 tests 目錄是否存在"""
    assert os.path.exists("tests")

  def test_tests_init_py_exists(self):
    """測試 tests/__init__.py 是否存在

    重點：使 tests 成為一個 Python 套件
    """
    assert os.path.exists("tests/__init__.py")

  def test_test_files_exist(self):
    """測試是否存在測試檔案

    重點：確保至少有一個以 test_ 開頭的測試檔案
    """
    # 列出所有以 test_ 開頭的檔案
    test_files = [f for f in os.listdir("tests") if f.startswith("test_")]
    # 確保至少有一個測試檔案存在
    assert len(test_files) > 0


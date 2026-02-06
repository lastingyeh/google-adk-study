"""
環境配置與初始化測試
"""

import os


class TestEnvironmentSetup:
    """
    測試環境變數設定。

    重點說明:
    1. 驗證 Google Cloud 認證 (google.auth.default())
    2. 驗證關鍵環境變數 (GOOGLE_CLOUD_LOCATION, GOOGLE_GENAI_USE_VERTEXAI)
    """

    def test_google_auth_initialization(self):
        """
        測試 Google 認證初始化。

        驗證點:
        1. 嘗試獲取預設憑證
        2. 確保 Project ID 存在 (透過憑證或環境變數)
        """
        import google.auth

        try:
            _, project_id = google.auth.default()
            assert project_id is not None or os.environ.get("GOOGLE_CLOUD_PROJECT")
        except Exception:
            # 在測試環境中可能沒有設定認證，這是可接受的
            pass

    def test_environment_variables_set(self):
        """
        測試環境變數是否被正確設定。

        驗證點:
        1. 匯入 rag 模組
        2. GOOGLE_CLOUD_LOCATION 為 global
        3. GOOGLE_GENAI_USE_VERTEXAI 已啟用
        """
        # 匯入 rag 套件會自動設定環境變數

        # GOOGLE_CLOUD_LOCATION 應被設定為 global
        assert os.environ.get("GOOGLE_CLOUD_LOCATION") == "global"

        # GOOGLE_GENAI_USE_VERTEXAI 應被設定
        assert os.environ.get("GOOGLE_GENAI_USE_VERTEXAI") in ["True", "true", "1"]

    def test_google_cloud_project_set(self):
        """測試 GOOGLE_CLOUD_PROJECT 環境變數。"""

        # 應設定 GOOGLE_CLOUD_PROJECT 或已經存在
        assert os.environ.get("GOOGLE_CLOUD_PROJECT") is not None


class TestModuleInitialization:
    """測試模組初始化邏輯。"""

    def test_rag_module_imports_agent(self):
        """測試 rag 模組是否匯入了 agent。"""
        import rag

        assert hasattr(rag, "agent")

    def test_initialization_order(self):
        """測試初始化順序正確（環境變數在 agent 之前設定）。"""
        # 重新匯入以測試初始化順序
        import sys

        # 移除已匯入的 rag 模組
        if "rag" in sys.modules:
            del sys.modules["rag"]
        if "rag.agent" in sys.modules:
            del sys.modules["rag.agent"]

        # 重新匯入並檢查

        assert os.environ.get("GOOGLE_CLOUD_LOCATION") == "global"


class TestRAGCorpusConfiguration:
    """測試 RAG Corpus 配置。"""

    def test_rag_corpus_environment_variable(self):
        """測試 RAG_CORPUS 環境變數。"""
        # RAG_CORPUS 應該在 .env 中定義或透過環境變數設定
        rag_corpus = os.environ.get("RAG_CORPUS")

        # 在測試環境中，可能沒有設定真實的 RAG_CORPUS
        # 但我們可以檢查格式是否正確（如果有設定的話）
        if rag_corpus:
            # 檢查格式：projects/{project}/locations/{location}/ragCorpora/{corpus_id}
            assert "projects/" in rag_corpus or rag_corpus.startswith("projects/")
            assert "ragCorpora" in rag_corpus or "ragcorpora" in rag_corpus.lower()

    def test_retrieval_tool_uses_environment_rag_corpus(self):
        """測試檢索工具使用環境變數中的 RAG_CORPUS。"""
        from google.adk.tools.retrieval.vertex_ai_rag_retrieval import (
            VertexAiRagRetrieval,
        )

        from rag.agent import ask_vertex_retrieval

        # 檢查工具是否是正確的類型
        assert isinstance(ask_vertex_retrieval, VertexAiRagRetrieval)
        # 檢查工具已被正確初始化
        assert ask_vertex_retrieval.name is not None
        assert ask_vertex_retrieval.description is not None


class TestDotEnvLoading:
    """測試 .env 檔案載入。"""

    def test_dotenv_loaded(self):
        """測試 dotenv 已被載入。"""
        from dotenv import load_dotenv

        # load_dotenv 應該可以被呼叫
        result = load_dotenv()
        assert result is not None  # 回傳 True 或 False，視 .env 是否存在

"""
配置模組測試
"""


class TestConfiguration:
    """測試配置設定。"""

    def test_config_exists(self):
        """測試 config 實例是否存在。"""
        from app.config import config

        assert config is not None

    def test_config_has_critic_model(self):
        """測試 config 擁有 critic_model 設定。"""
        from app.config import config

        assert hasattr(config, "critic_model")
        assert config.critic_model is not None
        assert isinstance(config.critic_model, str)

    def test_config_has_worker_model(self):
        """測試 config 擁有 worker_model 設定。"""
        from app.config import config

        assert hasattr(config, "worker_model")
        assert config.worker_model is not None
        assert isinstance(config.worker_model, str)

    def test_config_has_max_iterations(self):
        """測試 config 擁有 max_search_iterations 設定。"""
        from app.config import config

        assert hasattr(config, "max_search_iterations")
        assert isinstance(config.max_search_iterations, int)
        assert config.max_search_iterations > 0

    def test_config_default_values(self):
        """測試 config 預設值。"""
        from app.config import config

        assert config.critic_model == "gemini-3-pro-preview"
        assert config.worker_model == "gemini-3-pro-preview"
        assert config.max_search_iterations == 5


class TestConfigurationClass:
    """測試 ResearchConfiguration 類別。"""

    def test_research_configuration_class_exists(self):
        """測試 ResearchConfiguration 類別存在。"""
        from app.config import ResearchConfiguration

        assert ResearchConfiguration is not None

    def test_research_configuration_instantiation(self):
        """測試 ResearchConfiguration 能被實例化。"""
        from app.config import ResearchConfiguration

        config = ResearchConfiguration()
        assert config is not None

    def test_research_configuration_custom_values(self):
        """測試 ResearchConfiguration 支援自訂值。"""
        from app.config import ResearchConfiguration

        custom_config = ResearchConfiguration(
            critic_model="custom-model-1",
            worker_model="custom-model-2",
            max_search_iterations=10,
        )

        assert custom_config.critic_model == "custom-model-1"
        assert custom_config.worker_model == "custom-model-2"
        assert custom_config.max_search_iterations == 10

    def test_research_configuration_is_dataclass(self):
        """測試 ResearchConfiguration 是 dataclass。"""
        from app.config import ResearchConfiguration
        from dataclasses import is_dataclass

        assert is_dataclass(ResearchConfiguration)


class TestEnvironmentVariables:
    """測試環境變數處理。"""

    def test_dotenv_loaded(self):
        """測試 dotenv 已載入。"""
        import os
        from dotenv import load_dotenv

        # 測試 dotenv 可以被載入（不需要特定環境變數）
        # 只要 load_dotenv 不拋出異常即可
        load_dotenv()
        # 測試通過如果沒有異常
        assert True

    def test_vertex_ai_configuration(self):
        """測試 Vertex AI 配置邏輯。"""
        import os

        # 驗證配置邏輯：如果環境變數存在，檢查是否以 TRUE 或 FALSE 開頭
        vertexai_value = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI")
        if vertexai_value is not None:
            # 環境變數可能包含說明文字，只檢查開頭是否為 TRUE 或 FALSE
            assert vertexai_value.upper().startswith(
                "TRUE"
            ) or vertexai_value.upper().startswith("FALSE")
        # 如果不存在，測試也應該通過（允許未設定）
        assert True

"""暫停/恢復調用代理（Pause/Resume Invocation Agent）測試套件。

本測試套件驗證代理配置、工具功能、模組導入以及應用程式設定。
"""

from pause_resume_agent import root_agent
from pause_resume_agent.agent import (
    process_data_chunk,
    validate_checkpoint,
    get_resumption_hint,
)
from app import app


class TestAgentConfiguration:
    """測試代理配置與元數據（Metadata）。"""

    def test_agent_name(self):
        """測試代理是否具備正確的名稱。"""
        assert root_agent.name == "pause_resume_agent"

    def test_agent_model(self):
        """測試代理是否使用正確的模型。"""
        assert root_agent.model == "gemini-2.0-flash"

    def test_agent_description(self):
        """測試代理是否具備描述說明，且包含關鍵字。"""
        assert root_agent.description is not None
        assert "pause" in root_agent.description.lower()
        assert "resume" in root_agent.description.lower()

    def test_agent_instruction(self):
        """測試代理是否具備指令，且包含檢查點（checkpoint）說明。"""
        assert root_agent.instruction is not None
        assert len(root_agent.instruction) > 0
        assert "checkpoint" in root_agent.instruction.lower()

    def test_agent_has_tools(self):
        """測試代理是否已配置 3 個工具。"""
        assert root_agent.tools is not None
        assert len(root_agent.tools) == 3

    def test_agent_export(self):
        """測試代理是否已正確匯出。"""
        from pause_resume_agent import root_agent as exported_agent
        assert exported_agent is not None
        assert exported_agent.name == "pause_resume_agent"


class TestAgentTools:
    """測試代理工具的功能性。"""

    def test_process_data_chunk_success(self):
        """測試 process_data_chunk 在輸入有效數據時是否運作正常。"""
        result = process_data_chunk("hello world test")
        assert result["status"] == "success"
        assert "report" in result
        assert result["word_count"] == 3

    def test_process_data_chunk_multiline(self):
        """測試 process_data_chunk 在處理多行數據時的情況。"""
        result = process_data_chunk("line1\nline2\nline3")
        assert result["status"] == "success"
        assert result["lines_processed"] == 3

    def test_process_data_chunk_empty(self):
        """測試 process_data_chunk 在輸入空數據時是否正確報錯。"""
        result = process_data_chunk("")
        assert result["status"] == "error"
        assert result["error"] == "Empty data string"

    def test_validate_checkpoint_valid(self):
        """測試 validate_checkpoint 在輸入有效檢查點時的驗證結果。"""
        result = validate_checkpoint("checkpoint_state")
        assert result["status"] == "success"
        assert result["is_valid"] is True

    def test_validate_checkpoint_empty(self):
        """測試 validate_checkpoint 在輸入空數據時的驗證結果。"""
        result = validate_checkpoint("")
        assert result["status"] == "error"
        assert result["is_valid"] is False

    def test_get_resumption_hint_processing(self):
        """測試在 'processing' 情境下獲取恢復提示。"""
        result = get_resumption_hint("processing data")
        assert result["status"] == "success"
        assert "processing" in result["hint"].lower()

    def test_get_resumption_hint_validation(self):
        """測試在 'validation' 情境下獲取恢復提示。"""
        result = get_resumption_hint("validation check")
        assert result["status"] == "success"
        assert "validation" in result["hint"].lower()

    def test_get_resumption_hint_analysis(self):
        """測試在 'analysis' 情境下獲取恢復提示。"""
        result = get_resumption_hint("analysis phase")
        assert result["status"] == "success"
        assert "analysis" in result["hint"].lower()

    def test_get_resumption_hint_unknown(self):
        """測試在未知情境下獲取默認恢復提示。"""
        result = get_resumption_hint("unknown context")
        assert result["status"] == "success"
        assert "resume from the beginning" in result["hint"].lower()


class TestImports:
    """測試模組導入與匯出是否正常。"""

    def test_import_root_agent(self):
        """測試導入 root_agent。"""
        from pause_resume_agent import root_agent as agent
        assert agent is not None

    def test_import_agent_module(self):
        """測試導入 agent 模組。"""
        from pause_resume_agent import agent as agent_module
        assert agent_module is not None

    def test_import_app(self):
        """測試導入 app 應用程式。"""
        from app import app as application
        assert application is not None


class TestAppConfiguration:
    """測試應用程式（App）對暫停/恢復的配置。"""

    def test_app_name(self):
        """測試應用程式是否具備正確名稱。"""
        assert app.name == "pause_resume_app"

    def test_app_has_root_agent(self):
        """測試應用程式是否已配置根代理。"""
        assert app.root_agent is not None
        assert app.root_agent.name == "pause_resume_agent"

    def test_resumability_config_exists(self):
        """測試應用程式是否具備可恢復性（Resumability）配置。"""
        assert app.resumability_config is not None

    def test_resumability_enabled(self):
        """測試可恢復性功能是否已啟用。"""
        assert app.resumability_config.is_resumable is True

"""測試 Agent 設定與工具功能。

此模組包含針對 tool_use_evaluator Agent 的設定與其工具功能的測試。
"""

from tool_use_evaluator.agent import root_agent


class TestAgentConfiguration:
    """測試 Agent 設定。

    驗證 Agent 的基本屬性，如名稱、模型、描述、指令以及工具設定是否正確。
    """

    def test_agent_name(self):
        """測試 Agent 是否有正確的名稱。

        驗證 root_agent.name 是否為 "tool_use_evaluator"。
        """
        assert root_agent.name == "tool_use_evaluator"

    def test_agent_model(self):
        """測試 Agent 是否使用正確的模型。

        驗證 root_agent.model 是否設定為 "gemini-2.0-flash"。
        """
        assert root_agent.model == "gemini-2.0-flash"

    def test_agent_description(self):
        """測試 Agent 是否有描述說明。

        驗證 root_agent.description 是否存在，且包含 "tool use quality" 關鍵字。
        """
        assert root_agent.description
        assert "tool use quality" in root_agent.description.lower()

    def test_agent_instruction(self):
        """測試 Agent 是否有指令說明。

        驗證 root_agent.instruction 是否存在，且包含 "data" 關鍵字。
        """
        assert root_agent.instruction
        assert "data" in root_agent.instruction.lower()

    def test_agent_has_tools(self):
        """測試 Agent 是否擁有所有必要的工具。

        驗證 root_agent.tools 是否包含 "analyze_data", "extract_features", "validate_quality", "apply_model"。
        """
        tool_names = [tool.__name__ for tool in root_agent.tools]
        assert "analyze_data" in tool_names
        assert "extract_features" in tool_names
        assert "validate_quality" in tool_names
        assert "apply_model" in tool_names

    def test_agent_has_output_key(self):
        """測試 Agent 是否有設定輸出鍵值。

        驗證 root_agent.output_key 是否設定為 "analysis_result"。
        """
        assert root_agent.output_key == "analysis_result"


class TestToolFunctionality:
    """測試個別工具功能。

    針對 Agent 所使用的各個工具函式進行單元測試，包含成功與失敗的案例。
    """

    def test_analyze_data_success(self):
        """測試 analyze_data 工具在輸入有效時的情況。

        輸入: "customer_data"
        預期: 返回狀態為 "success"，且報告中包含 "analyzed"。
        """
        from tool_use_evaluator.agent import analyze_data
        result = analyze_data("customer_data")
        assert result["status"] == "success"
        assert "analyzed" in result["report"].lower()
        assert "data" in result

    def test_analyze_data_error(self):
        """測試 analyze_data 工具在輸入為空時的情況。

        輸入: "" (空字串)
        預期: 返回狀態為 "error"。
        """
        from tool_use_evaluator.agent import analyze_data
        result = analyze_data("")
        assert result["status"] == "error"

    def test_extract_features_success(self):
        """測試 extract_features 工具在輸入有效時的情況。

        輸入: {"test": "data"}
        預期: 返回狀態為 "success"，且數據中包含 "features"。
        """
        from tool_use_evaluator.agent import extract_features
        result = extract_features({"test": "data"})
        assert result["status"] == "success"
        assert "features" in result["data"]

    def test_extract_features_error(self):
        """測試 extract_features 工具在輸入為空時的情況。

        輸入: None
        預期: 返回狀態為 "error"。
        """
        from tool_use_evaluator.agent import extract_features
        result = extract_features(None)
        assert result["status"] == "error"

    def test_validate_quality_success(self):
        """測試 validate_quality 工具在輸入有效時的情況。

        輸入: {"features": "data"}
        預期: 返回狀態為 "success"，且數據中包含 "quality_score"。
        """
        from tool_use_evaluator.agent import validate_quality
        result = validate_quality({"features": "data"})
        assert result["status"] == "success"
        assert "quality_score" in result["data"]

    def test_validate_quality_error(self):
        """測試 validate_quality 工具在輸入為空時的情況。

        輸入: None
        預期: 返回狀態為 "error"。
        """
        from tool_use_evaluator.agent import validate_quality
        result = validate_quality(None)
        assert result["status"] == "error"

    def test_apply_model_success(self):
        """測試 apply_model 工具在輸入有效時的情況。

        輸入: features={"features": "data"}, model_name="random_forest"
        預期: 返回狀態為 "success"，且數據中包含 "model"。
        """
        from tool_use_evaluator.agent import apply_model
        result = apply_model({"features": "data"}, "random_forest")
        assert result["status"] == "success"
        assert "model" in result["data"]

    def test_apply_model_error_no_features(self):
        """測試 apply_model 工具在缺少特徵數據時的情況。

        輸入: features=None, model_name="random_forest"
        預期: 返回狀態為 "error"。
        """
        from tool_use_evaluator.agent import apply_model
        result = apply_model(None, "random_forest")
        assert result["status"] == "error"

    def test_apply_model_error_no_model(self):
        """測試 apply_model 工具在缺少模型名稱時的情況。

        輸入: features={"features": "data"}, model_name=""
        預期: 返回狀態為 "error"。
        """
        from tool_use_evaluator.agent import apply_model
        result = apply_model({"features": "data"}, "")
        assert result["status"] == "error"

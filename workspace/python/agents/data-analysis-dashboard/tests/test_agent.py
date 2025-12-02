"""測試數據分析代理的配置和功能。"""

import os

# 如果不存在，設置用於測試的模擬 API 金鑰
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "test_api_key_for_testing"


class TestAgentConfiguration:
    """測試代理配置和設置。"""

    def test_agent_imports(self):
        """測試代理是否正確導入。"""
        from agent import agent, root_agent, app

        assert agent is not None
        assert root_agent is not None
        assert app is not None

    def test_root_agent_properties(self):
        """測試 root_agent 是否具有正確的屬性。"""
        from agent import root_agent

        assert hasattr(root_agent, 'name')
        assert root_agent.name == "data_analyst"
        assert hasattr(root_agent, 'model')
        assert hasattr(root_agent, 'instruction')
        assert hasattr(root_agent, 'tools')

    def test_agent_has_tools(self):
        """測試代理是否具有所需的工具。"""
        from agent import root_agent

        # 應有 3 個工具：load_csv_data、analyze_data、create_chart
        assert len(root_agent.tools) == 3

        tool_names = [tool.__name__ for tool in root_agent.tools]
        assert "load_csv_data" in tool_names
        assert "analyze_data" in tool_names
        assert "create_chart" in tool_names

    def test_fastapi_app_configuration(self):
        """測試 FastAPI 應用程序是否配置正確。"""
        from agent import app

        assert app.title == "Data Analysis Agent API"
        assert "version" in app.__dict__ or hasattr(app, "version")


class TestLoadCSVData:
    """測試 load_csv_data 工具。"""

    def test_load_csv_data_success(self):
        """測試成功的 CSV 數據加載。"""
        from agent.agent import load_csv_data

        csv_content = "name,age,score\nAlice,30,95\nBob,25,87\nCarol,35,92"
        result = load_csv_data("test.csv", csv_content)

        assert result["status"] == "success"
        assert result["file_name"] == "test.csv"
        assert result["rows"] == 3
        assert "name" in result["columns"]
        assert "age" in result["columns"]
        assert "score" in result["columns"]
        assert len(result["preview"]) <= 5

    def test_load_csv_data_with_headers(self):
        """測試帶有標題的 CSV 加載。"""
        from agent.agent import load_csv_data

        csv_content = "product,quantity,price\nApple,10,1.50\nBanana,20,0.75"
        result = load_csv_data("products.csv", csv_content)

        assert result["status"] == "success"
        assert result["columns"] == ["product", "quantity", "price"]
        assert result["rows"] == 2

    def test_load_csv_data_error_handling(self):
        """測試無效數據的 CSV 加載。"""
        from agent.agent import load_csv_data

        # 無效的 CSV 內容
        csv_content = "invalid csv format with no structure"
        result = load_csv_data("invalid.csv", csv_content)

        # 應優雅地處理錯誤
        assert "status" in result

    def test_load_csv_data_empty(self):
        """測試空內容的 CSV 加載。"""
        from agent.agent import load_csv_data

        csv_content = ""
        result = load_csv_data("empty.csv", csv_content)

        # 應優雅地處理錯誤
        assert "status" in result


class TestAnalyzeData:
    """測試 analyze_data 工具。"""

    def setup_method(self):
        """在每次測試前設置測試數據。"""
        from agent.agent import load_csv_data

        # 加載範例數據
        csv_content = "name,age,score\nAlice,30,95\nBob,25,87\nCarol,35,92"
        load_csv_data("test.csv", csv_content)

    def test_analyze_data_summary(self):
        """測試摘要分析。"""
        from agent.agent import analyze_data

        result = analyze_data("test.csv", "summary")

        assert result["status"] == "success"
        assert result["analysis_type"] == "summary"
        assert "data" in result
        assert "describe" in result["data"]
        assert "missing" in result["data"]
        assert "unique" in result["data"]

    def test_analyze_data_with_columns(self):
        """測試特定欄位的分析。"""
        from agent.agent import analyze_data

        result = analyze_data("test.csv", "summary", columns=["age", "score"])

        assert result["status"] == "success"
        assert "data" in result

    def test_analyze_data_correlation(self):
        """測試相關性分析。"""
        from agent.agent import analyze_data

        result = analyze_data("test.csv", "correlation")

        assert result["status"] == "success"
        assert result["analysis_type"] == "correlation"
        assert "data" in result

    def test_analyze_data_trend(self):
        """測試趨勢分析。"""
        from agent.agent import analyze_data

        result = analyze_data("test.csv", "trend")

        assert result["status"] == "success"
        assert result["analysis_type"] == "trend"
        assert "data" in result
        assert "trend" in result["data"]
        assert result["data"]["trend"] in ["upward", "downward"]

    def test_analyze_data_not_found(self):
        """測試不存在的數據集分析。"""
        from agent.agent import analyze_data

        result = analyze_data("nonexistent.csv", "summary")

        assert result["status"] == "error"
        assert "not found" in result["report"].lower()

    def test_analyze_data_invalid_columns(self):
        """測試無效欄位的分析。"""
        from agent.agent import analyze_data

        result = analyze_data("test.csv", "summary", columns=["invalid_col"])

        assert result["status"] == "error"

    def test_analyze_data_invalid_type(self):
        """測試無效分析類型的分析。"""
        from agent.agent import analyze_data

        result = analyze_data("test.csv", "invalid_type")

        assert result["status"] == "error"


class TestCreateChart:
    """測試 create_chart 工具。"""

    def setup_method(self):
        """在每次測試前設置測試數據。"""
        from agent.agent import load_csv_data

        # 加載範例數據
        csv_content = "month,sales\nJan,100\nFeb,120\nMar,115"
        load_csv_data("sales.csv", csv_content)

    def test_create_chart_line(self):
        """測試折線圖建立。"""
        from agent.agent import create_chart

        result = create_chart("sales.csv", "line", "month", "sales")

        assert result["status"] == "success"
        assert result["chart_type"] == "line"
        assert "data" in result
        assert "labels" in result["data"]
        assert "values" in result["data"]
        assert len(result["data"]["labels"]) == 3
        assert len(result["data"]["values"]) == 3

    def test_create_chart_bar(self):
        """測試長條圖建立。"""
        from agent.agent import create_chart

        result = create_chart("sales.csv", "bar", "month", "sales")

        assert result["status"] == "success"
        assert result["chart_type"] == "bar"

    def test_create_chart_scatter(self):
        """測試散點圖建立。"""
        from agent.agent import create_chart

        result = create_chart("sales.csv", "scatter", "month", "sales")

        assert result["status"] == "success"
        assert result["chart_type"] == "scatter"

    def test_create_chart_not_found(self):
        """測試不存在的數據集圖表建立。"""
        from agent.agent import create_chart

        result = create_chart("nonexistent.csv", "line", "x", "y")

        assert result["status"] == "error"
        assert "not found" in result["report"].lower()

    def test_create_chart_invalid_column(self):
        """測試無效欄位的圖表建立。"""
        from agent.agent import create_chart

        result = create_chart("sales.csv", "line", "invalid_col", "sales")

        assert result["status"] == "error"

    def test_create_chart_invalid_type(self):
        """測試無效圖表類型的圖表建立。"""
        from agent.agent import create_chart

        result = create_chart("sales.csv", "invalid_type", "month", "sales")

        assert result["status"] == "error"

    def test_create_chart_options(self):
        """測試圖表是否具有適當的選項。"""
        from agent.agent import create_chart

        result = create_chart("sales.csv", "line", "month", "sales")

        assert result["status"] == "success"
        assert "options" in result
        assert "x_label" in result["options"]
        assert "y_label" in result["options"]
        assert "title" in result["options"]
        assert result["options"]["x_label"] == "month"
        assert result["options"]["y_label"] == "sales"


class TestFastAPIEndpoints:
    """測試 FastAPI 端點。"""

    def test_health_endpoint(self):
        """測試健康檢查端點。"""
        from agent import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["agent"] == "data_analyst"
        assert "datasets_loaded" in data

    def test_datasets_endpoint(self):
        """測試數據集列表端點。"""
        from agent import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.get("/datasets")

        assert response.status_code == 200
        data = response.json()
        assert "datasets" in data
        assert "count" in data

"""
針對 vision_catalog_agent 的 Agent 設定進行測試。

此檔案包含一系列的測試，用以確保 vision_catalog_agent 的各個元件，
包括 root_agent、vision_analyzer 和 catalog_generator，都已正確設定。
同時，也會驗證所有工具函式是否可正常呼叫，以及其簽章是否符合預期。
"""

from vision_catalog_agent import root_agent
from vision_catalog_agent.agent import (
    vision_analyzer,
    catalog_generator,
    analyze_product_image,
    analyze_uploaded_image,
    compare_product_images,
    generate_catalog_entry,
    generate_product_mockup,
    list_sample_images
)


class TestAgentConfiguration:
    """測試 Agent 的基本設定與結構。"""

    def test_root_agent_exists(self):
        """測試 root_agent 是否已定義。"""
        assert root_agent is not None

    def test_root_agent_name(self):
        """測試 root_agent 的名稱是否正確。"""
        assert root_agent.name == 'vision_catalog_coordinator'

    def test_root_agent_model(self):
        """測試 root_agent 是否使用指定的模型。"""
        assert root_agent.model in [
            'gemini-2.0-flash-exp',
            'gemini-2.0-flash',
            'gemini-1.5-pro',
            'gemini-1.5-flash'
        ]

    def test_root_agent_has_tools(self):
        """測試 root_agent 是否已設定工具。"""
        assert root_agent.tools is not None
        assert len(root_agent.tools) >= 5  # 應包含 list_sample_images, generate_product_mockup, analyze_uploaded_image, analyze_product_image, compare_product_images

    def test_root_agent_has_instruction(self):
        """測試 root_agent 是否包含指令。"""
        assert root_agent.instruction is not None
        assert len(root_agent.instruction) > 0

    def test_root_agent_has_description(self):
        """測試 root_agent 是否包含描述。"""
        assert root_agent.description is not None
        assert len(root_agent.description) > 0


class TestVisionAnalyzerAgent:
    """測試視覺分析 Agent 的設定。"""

    def test_vision_analyzer_exists(self):
        """測試 vision_analyzer 是否已定義。"""
        assert vision_analyzer is not None

    def test_vision_analyzer_name(self):
        """測試 vision_analyzer 的名稱是否正確。"""
        assert vision_analyzer.name == 'vision_analyzer'

    def test_vision_analyzer_model(self):
        """測試 vision_analyzer 是否使用支援視覺功能的模型。"""
        assert 'gemini' in vision_analyzer.model.lower()

    def test_vision_analyzer_instruction(self):
        """測試 vision_analyzer 是否包含視覺相關的指令。"""
        instruction = vision_analyzer.instruction.lower()
        assert any(keyword in instruction for keyword in [
            'vision', 'image', 'visual', 'analyze'
        ])

    def test_vision_analyzer_temperature(self):
        """測試 vision_analyzer 的溫度設定是否合適。"""
        if vision_analyzer.generate_content_config:
            assert vision_analyzer.generate_content_config.temperature <= 0.5


class TestCatalogGeneratorAgent:
    """測試目錄生成 Agent 的設定。"""

    def test_catalog_generator_exists(self):
        """測試 catalog_generator 是否已定義。"""
        assert catalog_generator is not None

    def test_catalog_generator_name(self):
        """測試 catalog_generator 的名稱是否正確。"""
        assert catalog_generator.name == 'catalog_generator'

    def test_catalog_generator_has_tools(self):
        """測試 catalog_generator 是否已設定工具。"""
        assert catalog_generator.tools is not None
        assert len(catalog_generator.tools) > 0

    def test_catalog_generator_instruction(self):
        """測試 catalog_generator 是否包含目錄相關的指令。"""
        instruction = catalog_generator.instruction.lower()
        assert any(keyword in instruction for keyword in [
            'catalog', 'description', 'product'
        ])


class TestTools:
    """測試工具函式。"""

    def test_analyze_product_image_callable(self):
        """測試 analyze_product_image 是否可呼叫。"""
        assert callable(analyze_product_image)

    def test_analyze_uploaded_image_callable(self):
        """測試 analyze_uploaded_image 是否可呼叫。"""
        assert callable(analyze_uploaded_image)

    def test_compare_product_images_callable(self):
        """測試 compare_product_images 是否可呼叫。"""
        assert callable(compare_product_images)

    def test_generate_product_mockup_callable(self):
        """測試 generate_product_mockup 是否可呼叫。"""
        assert callable(generate_product_mockup)

    def test_list_sample_images_callable(self):
        """測試 list_sample_images 是否可呼叫。"""
        assert callable(list_sample_images)

    def test_generate_catalog_entry_callable(self):
        """測試 generate_catalog_entry 是否可呼叫。"""
        assert callable(generate_catalog_entry)

    def test_tool_signatures(self):
        """測試工具函式的簽章。"""
        import inspect

        # analyze_product_image 應包含 product_id, image_path, tool_context
        sig = inspect.signature(analyze_product_image)
        assert 'product_id' in sig.parameters
        assert 'image_path' in sig.parameters
        assert 'tool_context' in sig.parameters

        # analyze_uploaded_image 應包含 product_name, tool_context
        sig = inspect.signature(analyze_uploaded_image)
        assert 'product_name' in sig.parameters
        assert 'tool_context' in sig.parameters

        # compare_product_images 應包含 image_paths, tool_context
        sig = inspect.signature(compare_product_images)
        assert 'image_paths' in sig.parameters
        assert 'tool_context' in sig.parameters

        # generate_catalog_entry 應包含 product_name, analysis, tool_context
        sig = inspect.signature(generate_catalog_entry)
        assert 'product_name' in sig.parameters
        assert 'analysis' in sig.parameters
        assert 'tool_context' in sig.parameters

        # generate_product_mockup 應包含 product_description, product_name, tool_context
        sig = inspect.signature(generate_product_mockup)
        assert 'product_description' in sig.parameters
        assert 'product_name' in sig.parameters
        assert 'tool_context' in sig.parameters


class TestAgentToolIntegration:
    """測試 Agent 與工具的整合。"""

    def test_root_agent_tool_names(self):
        """測試 root_agent 是否包含預期的工具名稱。"""
        tool_names = []
        for tool in root_agent.tools:
            if hasattr(tool, 'name'):
                tool_names.append(tool.name)
            elif hasattr(tool, '_function') and hasattr(tool._function, '__name__'):
                tool_names.append(tool._function.__name__)

        expected_tools = {'list_sample_images', 'generate_product_mockup', 'analyze_uploaded_image', 'analyze_product_image', 'compare_product_images'}
        actual_tools = set(tool_names)

        assert expected_tools.issubset(actual_tools), \
            f"遺失工具: {expected_tools - actual_tools}"

    def test_catalog_generator_has_artifact_tool(self):
        """測試 catalog_generator 是否包含產物生成工具。"""
        tool_names = []
        for tool in catalog_generator.tools:
            if hasattr(tool, 'name'):
                tool_names.append(tool.name)
            elif hasattr(tool, '_function') and hasattr(tool._function, '__name__'):
                tool_names.append(tool._function.__name__)

        assert 'generate_catalog_entry' in tool_names


class TestConfiguration:
    """測試 Agent 的生成設定。"""

    def test_generate_content_configs(self):
        """測試 Agent 是否有合適的生成設定。"""
        agents = [root_agent, vision_analyzer, catalog_generator]

        for agent in agents:
            if agent.generate_content_config:
                config = agent.generate_content_config

                # 溫度應在合理範圍內
                if hasattr(config, 'temperature'):
                    assert 0.0 <= config.temperature <= 1.0

                # 應設定最大輸出 token 數量
                if hasattr(config, 'max_output_tokens'):
                    assert config.max_output_tokens > 0

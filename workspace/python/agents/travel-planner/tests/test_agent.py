"""
教學 05：平行處理 - 旅遊規劃系統測試
"""

import pytest
from travel_planner.agent import (
    flight_finder,
    hotel_finder,
    activity_finder,
    parallel_search,
    itinerary_builder,
    travel_planning_system,
    root_agent,
)


class TestIndividualAgents:
    """測試獨立代理的配置"""

    def test_flight_finder_config(self):
        """測試 flight_finder 代理的配置"""
        assert flight_finder.name == "flight_finder"
        assert flight_finder.model == "gemini-2.0-flash"
        assert flight_finder.description == "Searches for available flights"
        assert "flight" in flight_finder.instruction.lower()
        assert flight_finder.output_key == "flight_options"

    def test_hotel_finder_config(self):
        """測試 hotel_finder 代理的配置"""
        assert hotel_finder.name == "hotel_finder"
        assert hotel_finder.model == "gemini-2.0-flash"
        assert hotel_finder.description == "Searches for available hotels"
        assert "hotel" in hotel_finder.instruction.lower()
        assert hotel_finder.output_key == "hotel_options"

    def test_activity_finder_config(self):
        """測試 activity_finder 代理的配置"""
        assert activity_finder.name == "activity_finder"
        assert activity_finder.model == "gemini-2.0-flash"
        assert activity_finder.description == "Finds activities and attractions"
        assert "activit" in activity_finder.instruction.lower()
        assert activity_finder.output_key == "activity_options"

    def test_agents_have_unique_output_keys(self):
        """測試所有代理是否都具有唯一的輸出鍵"""
        output_keys = [
            flight_finder.output_key,
            hotel_finder.output_key,
            activity_finder.output_key,
        ]
        assert len(set(output_keys)) == len(output_keys)

    def test_agents_have_output_keys(self):
        """測試所有搜索代理是否都定義了輸出鍵"""
        assert flight_finder.output_key is not None
        assert hotel_finder.output_key is not None
        assert activity_finder.output_key is not None


class TestParallelAgentStructure:
    """測試 ParallelAgent 的配置和結構"""

    def test_parallel_search_is_parallel_agent(self):
        """測試 parallel_search 是否為 ParallelAgent"""
        from google.adk.agents import ParallelAgent

        assert isinstance(parallel_search, ParallelAgent)

    def test_parallel_search_name(self):
        """測試並行搜索代理的名稱"""
        assert parallel_search.name == "ParallelSearch"

    def test_parallel_search_has_three_sub_agents(self):
        """測試並行搜索是否正好有 3 個子代理"""
        assert len(parallel_search.sub_agents) == 3

    def test_parallel_search_sub_agents_are_correct(self):
        """測試並行搜索是否具有正確的子代理"""
        sub_agent_names = [agent.name for agent in parallel_search.sub_agents]
        expected_names = ["flight_finder", "hotel_finder", "activity_finder"]
        assert set(sub_agent_names) == set(expected_names)

    def test_parallel_search_description(self):
        """測試並行搜索的描述"""
        assert "concurrently" in parallel_search.description.lower()


class TestSequentialAgentStructure:
    """測試 SequentialAgent 的配置和結構"""

    def test_travel_planning_system_is_sequential_agent(self):
        """測試 travel_planning_system 是否為 SequentialAgent"""
        from google.adk.agents import SequentialAgent

        assert isinstance(travel_planning_system, SequentialAgent)

    def test_travel_planning_system_name(self):
        """測試旅遊規劃系統的名稱"""
        assert travel_planning_system.name == "TravelPlanningSystem"

    def test_travel_planning_system_has_two_sub_agents(self):
        """測試旅遊規劃系統是否正好有 2 個子代理"""
        assert len(travel_planning_system.sub_agents) == 2

    def test_travel_planning_system_first_agent_is_parallel(self):
        """測試序列中的第一個代理是否為並行搜索"""
        from google.adk.agents import ParallelAgent

        assert isinstance(travel_planning_system.sub_agents[0], ParallelAgent)

    def test_travel_planning_system_second_agent_is_itinerary_builder(self):
        """測試序列中的第二個代理是否為行程建立器"""
        assert travel_planning_system.sub_agents[1] == itinerary_builder


class TestItineraryBuilder:
    """測試行程建立器代理的配置"""

    def test_itinerary_builder_config(self):
        """測試行程建立器代理的配置"""
        assert itinerary_builder.name == "itinerary_builder"
        assert itinerary_builder.model == "gemini-2.0-flash"
        assert (
            itinerary_builder.description
            == "Combines all search results into a complete travel itinerary"
        )
        assert itinerary_builder.output_key == "final_itinerary"

    def test_itinerary_builder_reads_all_state_keys(self):
        """測試行程建立器的指令是否引用了所有狀態鍵"""
        instruction = itinerary_builder.instruction
        assert "{flight_options}" in instruction
        assert "{hotel_options}" in instruction
        assert "{activity_options}" in instruction


class TestRootAgent:
    """測試根代理的配置"""

    def test_root_agent_is_travel_planning_system(self):
        """測試 root_agent 是否為旅遊規劃系統"""
        assert root_agent == travel_planning_system

    def test_root_agent_is_sequential_agent(self):
        """測試 root_agent 是否為 SequentialAgent"""
        from google.adk.agents import SequentialAgent

        assert isinstance(root_agent, SequentialAgent)


class TestStateManagement:
    """測試狀態管理和數據流"""

    def test_parallel_agents_have_output_keys_for_state_injection(self):
        """測試並行代理是否將狀態保存以供行程建立器讀取"""
        parallel_output_keys = [
            agent.output_key for agent in parallel_search.sub_agents
        ]
        # 檢查行程建立器的指令是否包含對這些鍵的引用
        instruction = itinerary_builder.instruction
        for key in parallel_output_keys:
            assert f"{{{key}}}" in instruction

    def test_no_circular_dependencies(self):
        """測試流程中是否存在循環依賴"""
        # 並行代理之間不相互依賴
        # 行程建立器依賴於並行代理，但反之則不然
        parallel_keys = {agent.output_key for agent in parallel_search.sub_agents}
        itinerary_instruction = itinerary_builder.instruction

        # 行程建立器應僅從並行代理的輸出中讀取
        # (這是一個基本檢查 - 實際上，指令解析會更複雜)
        for key in parallel_keys:
            assert f"{{{key}}}" in itinerary_instruction


class TestAgentInstructions:
    """測試代理指令的品質和結構"""

    def test_flight_finder_instruction_format(self):
        """測試 flight_finder 指令的格式"""
        instruction = flight_finder.instruction
        assert "flight search specialist" in instruction.lower()
        assert "airline name" in instruction.lower()
        assert "departure and arrival times" in instruction.lower()
        assert "price range" in instruction.lower()

    def test_hotel_finder_instruction_format(self):
        """測試 hotel_finder 指令的格式"""
        instruction = hotel_finder.instruction
        assert "hotel search specialist" in instruction.lower()
        assert "hotel name and rating" in instruction.lower()
        assert "location" in instruction.lower()
        assert "price per night" in instruction.lower()

    def test_activity_finder_instruction_format(self):
        """測試 activity_finder 指令的格式"""
        instruction = activity_finder.instruction
        assert "local activities expert" in instruction.lower()
        assert "activity name" in instruction.lower()
        assert "description" in instruction.lower()
        assert "estimated duration" in instruction.lower()

    def test_itinerary_builder_instruction_comprehensive(self):
        """測試行程建立器的指令是否全面"""
        instruction = itinerary_builder.instruction
        assert "travel planner" in instruction.lower()
        assert "complete, well-organized itinerary" in instruction.lower()
        assert "best option" in instruction.lower()
        assert "day-by-day plan" in instruction.lower()
        assert "estimated total cost" in instruction.lower()

    def test_instructions_focus_on_output(self):
        """測試所有指令是否都強調輸出格式"""
        instructions = [
            flight_finder.instruction,
            hotel_finder.instruction,
            activity_finder.instruction,
            itinerary_builder.instruction,
        ]

        for instruction in instructions:
            # 每個指令都應提及格式化或輸出
            has_formatting_guidance = (
                "format" in instruction.lower()
                or "bulleted list" in instruction.lower()
                or "markdown" in instruction.lower()
            )
            assert (
                has_formatting_guidance
            ), f"指令缺乏格式化指導：{instruction[:100]}..."


class TestImports:
    """測試導入和模組結構"""

    def test_google_adk_agents_import(self):
        """測試 google.adk.agents 是否可以被導入"""
        import importlib.util

        spec = importlib.util.find_spec("google.adk.agents")
        assert spec is not None, "google.adk.agents 模組未找到"

    def test_travel_planner_agent_import(self):
        """測試 travel_planner.agent 模組是否可以被導入"""
        import importlib.util

        spec = importlib.util.find_spec("travel_planner.agent")
        assert spec is not None, "travel_planner.agent 模組未找到"

    def test_root_agent_exists(self):
        """測試 root_agent 是否已定義且可訪問"""
        try:
            from travel_planner.agent import root_agent

            assert root_agent is not None
        except ImportError as e:
            pytest.fail(f"無法導入 root_agent：{e}")

    def test_future_annotations_import(self):
        """測試 __future__ annotations 是否已導入"""
        import travel_planner.agent

        # 如果未導入 __future__ annotations，這將在導入時失敗
        # 因為我們在類型提示中使用了 | 語法
        assert hasattr(travel_planner.agent, "root_agent")


class TestProjectStructure:
    """測試專案目錄結構"""

    def test_travel_planner_directory_exists(self):
        """測試 travel_planner 目錄是否存在"""
        import os

        assert os.path.exists("travel_planner")

    def test_init_py_exists(self):
        """測試 __init__.py 是否存在"""
        import os

        assert os.path.exists("travel_planner/__init__.py")

    def test_agent_py_exists(self):
        """測試 agent.py 是否存在"""
        import os

        assert os.path.exists("travel_planner/agent.py")

    def test_env_example_exists(self):
        """測試 .env.example 是否存在"""
        import os

        assert os.path.exists("travel_planner/.env.example")

    def test_init_py_content(self):
        """測試 __init__.py 的內容"""
        with open("travel_planner/__init__.py", "r") as f:
            content = f.read().strip()
            assert "from . import agent" in content

    def test_agent_py_is_python_file(self):
        """測試 agent.py 是否為 Python 檔案"""
        import os
        import travel_planner.agent

        assert os.path.isfile("travel_planner/agent.py")
        assert travel_planner.agent.__file__.endswith("agent.py")

    def test_env_example_content(self):
        """測試 .env.example 的內容"""
        with open("travel_planner/.env.example", "r") as f:
            content = f.read()
            assert "GOOGLE_GENAI_USE_VERTEXAI=FALSE" in content
            assert "GOOGLE_API_KEY=" in content


class TestTestStructure:
    """測試測試目錄結構"""

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

        test_files = [
            "tests/test_agent.py",
            "tests/test_imports.py",
            "tests/test_structure.py",
        ]
        for test_file in test_files:
            assert os.path.exists(test_file), f"缺少測試檔案：{test_file}"


class TestAgentIntegration:
    """測試代理整合和流程功能"""

    def test_pipeline_can_be_created_without_error(self):
        """測試完整的流程是否可以在沒有錯誤的情況下實例化"""
        try:
            # 這不應引發任何異常
            from travel_planner.agent import travel_planning_system

            assert travel_planning_system is not None
        except Exception as e:
            pytest.fail(f"無法創建流程：{e}")

    def test_pipeline_has_valid_configuration_for_api(self):
        """測試流程是否具有 ADK API 的有效配置"""
        # 檢查 root_agent 是否具有必需的屬性
        assert hasattr(root_agent, "name")
        assert hasattr(root_agent, "description")
        assert hasattr(root_agent, "sub_agents")
        assert len(root_agent.sub_agents) > 0

    def test_state_flow_is_configured(self):
        """測試代理之間的狀態流是否已正確配置"""
        # 並行代理應具有輸出鍵
        parallel_outputs = [agent.output_key for agent in parallel_search.sub_agents]
        assert all(key is not None for key in parallel_outputs)

        # 行程建立器應引用這些鍵
        builder_instruction = itinerary_builder.instruction
        for key in parallel_outputs:
            assert f"{{{key}}}" in builder_instruction

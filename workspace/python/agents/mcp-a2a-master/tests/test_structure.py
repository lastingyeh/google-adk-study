"""
測試專案結構與檔案組織。
確保所有必要的檔案與目錄都存在。
"""

import os
import pytest


class TestProjectStructure:
    """測試專案結構完整性。"""

    def test_main_directories_exist(self):
        """測試主要目錄是否存在。

        重點說明：
        1. 定義必要的目錄清單 (agents, utilities, mcp, app, tests)
        2. 遍歷每個目錄名稱
        3. 驗證該目錄是否存在且確實為目錄
        """
        required_dirs = [
            "agents",
            "utilities",
            "mcp",
            "app",
            "tests",
        ]

        for dir_name in required_dirs:
            assert os.path.exists(dir_name), f"{dir_name} 目錄應該存在"
            assert os.path.isdir(dir_name), f"{dir_name} 應該是一個目錄"

    def test_agents_directory_structure(self):
        """測試 agents 目錄結構。

        重點說明：
        1. 驗證 agents 目錄是否存在
        2. 定義必要的 agent 子目錄清單
        3. 遍歷每個子目錄
        4. 驗證子目錄是否存在且確實為目錄
        """
        agents_dir = "agents"
        assert os.path.exists(agents_dir), "agents 目錄應該存在"

        # 檢查子目錄
        required_agent_dirs = [
            "host_agent",
            "website_builder_simple",
        ]

        for agent_dir in required_agent_dirs:
            agent_path = os.path.join(agents_dir, agent_dir)
            assert os.path.exists(agent_path), f"{agent_path} 應該存在"
            assert os.path.isdir(agent_path), f"{agent_path} 應該是一個目錄"

    def test_host_agent_files_exist(self):
        """測試 host_agent 必要檔案是否存在。

        重點說明：
        1. 定義 host_agent 目錄路徑
        2. 定義必要的檔案清單 (__init__.py, agent.py 等)
        3. 遍歷每個檔案名稱
        4. 驗證檔案是否存在且確實為檔案
        """
        host_agent_dir = "agents/host_agent"

        required_files = [
            "__init__.py",
            "agent.py",
            "agent_executor.py",
            "description.txt",
            "instructions.txt",
            "README.md",
        ]

        for file_name in required_files:
            file_path = os.path.join(host_agent_dir, file_name)
            assert os.path.exists(file_path), f"{file_path} 應該存在"
            assert os.path.isfile(file_path), f"{file_path} 應該是一個檔案"

    def test_website_builder_files_exist(self):
        """測試 website_builder_simple 必要檔案是否存在。

        重點說明：
        1. 定義 website_builder_simple 目錄路徑
        2. 定義必要的檔案清單 (__init__.py, agent.py 等)
        3. 遍歷每個檔案名稱
        4. 驗證檔案是否存在且確實為檔案
        """
        builder_dir = "agents/website_builder_simple"

        required_files = [
            "__init__.py",
            "agent.py",
            "agent_executor.py",
            "description.txt",
            "instructions.txt",
            "README.md",
        ]

        for file_name in required_files:
            file_path = os.path.join(builder_dir, file_name)
            assert os.path.exists(file_path), f"{file_path} 應該存在"
            assert os.path.isfile(file_path), f"{file_path} 應該是一個檔案"

    def test_utilities_directory_structure(self):
        """測試 utilities 目錄結構。

        重點說明：
        1. 驗證 utilities 目錄是否存在
        2. 定義必要的子目錄清單 (a2a, mcp, common)
        3. 遍歷每個子目錄
        4. 驗證子目錄是否存在且確實為目錄
        """
        utilities_dir = "utilities"
        assert os.path.exists(utilities_dir), "utilities 目錄應該存在"

        required_subdirs = [
            "a2a",
            "mcp",
            "common",
        ]

        for subdir in required_subdirs:
            subdir_path = os.path.join(utilities_dir, subdir)
            assert os.path.exists(subdir_path), f"{subdir_path} 應該存在"
            assert os.path.isdir(subdir_path), f"{subdir_path} 應該是一個目錄"

    def test_a2a_utilities_files_exist(self):
        """測試 A2A utilities 檔案是否存在。

        重點說明：
        1. 定義 a2a utilities 目錄路徑
        2. 定義必要的檔案清單 (agent_connect.py 等)
        3. 遍歷每個檔案
        4. 驗證檔案是否存在
        """
        a2a_dir = "utilities/a2a"

        required_files = [
            "agent_connect.py",
            "agent_discovery.py",
            "agent_registry.json",
        ]

        for file_name in required_files:
            file_path = os.path.join(a2a_dir, file_name)
            assert os.path.exists(file_path), f"{file_path} 應該存在"

    def test_mcp_utilities_files_exist(self):
        """測試 MCP utilities 檔案是否存在。

        重點說明：
        1. 定義 mcp utilities 目錄路徑
        2. 定義必要的檔案清單 (mcp_connect.py 等)
        3. 遍歷每個檔案
        4. 驗證檔案是否存在
        """
        mcp_dir = "utilities/mcp"

        required_files = [
            "mcp_connect.py",
            "mcp_discovery.py",
            "mcp_config.json",
        ]

        for file_name in required_files:
            file_path = os.path.join(mcp_dir, file_name)
            assert os.path.exists(file_path), f"{file_path} 應該存在"

    def test_common_utilities_files_exist(self):
        """測試 common utilities 檔案是否存在。

        重點說明：
        1. 定義 common utilities 目錄路徑
        2. 驗證 file_loader.py 檔案是否存在
        """
        common_dir = "utilities/common"

        assert os.path.exists(
            os.path.join(common_dir, "file_loader.py")
        ), "file_loader.py 應該存在"

    def test_tests_directory_structure(self):
        """測試 tests 目錄結構。

        重點說明：
        1. 驗證 tests 目錄是否存在且為目錄
        2. 定義必要的測試檔案清單
        3. 遍歷每個檔案
        4. 驗證檔案是否存在
        """
        tests_dir = "tests"
        assert os.path.exists(tests_dir), "tests 目錄應該存在"
        assert os.path.isdir(tests_dir), "tests 應該是一個目錄"

        required_test_files = [
            "__init__.py",
            "conftest.py",
            "test_imports.py",
            "test_structure.py",
        ]

        for file_name in required_test_files:
            file_path = os.path.join(tests_dir, file_name)
            assert os.path.exists(file_path), f"{file_path} 應該存在"

    def test_project_config_files_exist(self):
        """測試專案配置檔案是否存在。

        重點說明：
        1. 定義必要的專案配置檔案清單 (pyproject.toml, Makefile 等)
        2. 遍歷每個檔案
        3. 驗證檔案是否存在且確實為檔案
        """
        required_config_files = [
            "pyproject.toml",
            "Makefile",
            ".python-version",
            ".env.example",
        ]

        for config_file in required_config_files:
            assert os.path.exists(config_file), f"{config_file} 應該存在"
            assert os.path.isfile(config_file), f"{config_file} 應該是一個檔案"

    def test_mcp_directory_structure(self):
        """測試 mcp 目錄結構。

        重點說明：
        1. 驗證 mcp 目錄是否存在
        2. 檢查 servers 子目錄是否存在（若存在則確認其為目錄）
        3. 檢查 workspace 子目錄是否存在（若存在則確認其為目錄）
        """
        mcp_dir = "mcp"
        assert os.path.exists(mcp_dir), "mcp 目錄應該存在"

        # 檢查子目錄
        if os.path.exists(os.path.join(mcp_dir, "servers")):
            assert os.path.isdir(os.path.join(mcp_dir, "servers"))

        if os.path.exists(os.path.join(mcp_dir, "workspace")):
            assert os.path.isdir(os.path.join(mcp_dir, "workspace"))

    def test_app_directory_structure(self):
        """測試 app 目錄結構。

        重點說明：
        1. 驗證 app 目錄是否存在
        2. 確認 app 目錄確實為目錄
        """
        app_dir = "app"
        assert os.path.exists(app_dir), "app 目錄應該存在"
        assert os.path.isdir(app_dir), "app 應該是一個目錄"

    def test_main_py_exists(self):
        """測試 main.py 是否存在。

        重點說明：
        1. 驗證 main.py 檔案是否存在
        2. 確認 main.py 確實為檔案
        """
        assert os.path.exists("main.py"), "main.py 應該存在"
        assert os.path.isfile("main.py"), "main.py 應該是一個檔案"

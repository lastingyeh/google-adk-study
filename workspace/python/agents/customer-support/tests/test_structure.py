# 教程 20：YAML 設定 - 結構測試
# 驗證專案結構與檔案組織

import os
import pytest


class TestProjectStructure:
    """測試專案是否具有正確的檔案結構。"""

    def test_root_agent_yaml_exists(self):
        """測試 root_agent.yaml 是否存在於 customer_support 套件中。"""
        assert os.path.exists('customer_support/root_agent.yaml'), "customer_support/root_agent.yaml 應該存在"

    def test_tools_directory_exists(self):
        """測試 tools 目錄是否存在於 customer_support 套件中。"""
        assert os.path.exists('customer_support/tools'), "customer_support/tools 目錄應該存在"
        assert os.path.isdir('customer_support/tools'), "customer_support/tools 應該是一個目錄"

    def test_tools_init_exists(self):
        """測試 customer_support/tools/__init__.py 是否存在。"""
        assert os.path.exists('customer_support/tools/__init__.py'), "customer_support/tools/__init__.py 應該存在"

    def test_customer_tools_exists(self):
        """測試 customer_support/tools/customer_tools.py 是否存在。"""
        assert os.path.exists('customer_support/tools/customer_tools.py'), "customer_support/tools/customer_tools.py 應該存在"

    def test_run_agent_exists(self):
        """測試 run_agent.py 是否存在。"""
        assert os.path.exists('run_agent.py'), "run_agent.py 應該存在"

    def test_tests_directory_exists(self):
        """測試 tests 目錄是否存在。"""
        assert os.path.exists('tests'), "tests 目錄應該存在"
        assert os.path.isdir('tests'), "tests 應該是一個目錄"

    def test_test_files_exist(self):
        """測試測試檔案是否存在。"""
        test_files = [
            'tests/__init__.py',
            'tests/test_agent.py',
            'tests/test_tools.py',
            'tests/test_imports.py',
            'tests/test_structure.py',
        ]

        for test_file in test_files:
            assert os.path.exists(test_file), f"{test_file} 應該存在"

    def test_project_files_exist(self):
        """測試專案設定檔是否存在。"""
        project_files = [
            'pyproject.toml',
            'requirements.txt',
            'Makefile',
        ]

        for project_file in project_files:
            assert os.path.exists(project_file), f"{project_file} 應該存在"


class TestYAMLStructure:
    """測試 YAML 設定檔結構。"""

    def test_yaml_is_valid(self):
        """測試 root_agent.yaml 是否為有效的 YAML。"""
        import yaml

        with open('customer_support/root_agent.yaml', 'r') as f:
            config = yaml.safe_load(f)

        assert config is not None, "YAML 應該有效"
        assert isinstance(config, dict), "YAML 應該解析為字典"

    def test_yaml_has_required_fields(self):
        """測試 YAML 是否具有必要的頂層欄位。"""
        import yaml

        with open('customer_support/root_agent.yaml', 'r') as f:
            config = yaml.safe_load(f)

        required_fields = ['name', 'model', 'description', 'instruction']
        for field in required_fields:
            assert field in config, f"YAML 應該包含 {field} 欄位"
            assert config[field], f"{field} 不應為空"

    def test_yaml_has_no_sub_agents(self):
        """測試 YAML 是否沒有 sub_agents（單一代理設定）。"""
        import yaml

        with open('customer_support/root_agent.yaml', 'r') as f:
            config = yaml.safe_load(f)

        # 單一代理設定不應有 sub_agents
        assert 'sub_agents' not in config, "單一代理設定的 YAML 不應有 sub_agents 欄位"

    def test_yaml_has_tools(self):
        """測試 YAML 是否有工具設定。"""
        import yaml

        with open('customer_support/root_agent.yaml', 'r') as f:
            config = yaml.safe_load(f)

        assert 'tools' in config, "YAML 應該有 tools 欄位"
        assert isinstance(config['tools'], list), "tools 應該是一個列表"
        assert len(config['tools']) > 0, "應該至少有一個工具"

    def test_yaml_tools_have_correct_format(self):
        """測試 YAML 工具格式是否正確。"""
        import yaml

        with open('customer_support/root_agent.yaml', 'r') as f:
            config = yaml.safe_load(f)

        for i, tool in enumerate(config['tools']):
            assert isinstance(tool, dict), f"工具 {i} 應該是字典"
            assert 'name' in tool, f"工具 {i} 應該有 name 欄位"
            assert tool['name'].startswith('customer_support.tools.'), f"工具 {i} 名稱應該引用 customer_support.tools 模組：{tool['name']}"


class TestToolFunctionStructure:
    """測試工具函式結構與組織。"""

    def test_all_tool_functions_defined(self):
        """測試所有預期的工具函式是否已定義。"""
        from customer_support.tools.customer_tools import (
            check_customer_status,
            log_interaction,
            get_order_status,
            track_shipment,
            cancel_order,
            search_knowledge_base,
            run_diagnostic,
            create_ticket,
            get_billing_history,
            process_refund,
            update_payment_method,
        )

        # 所有函式應該是可呼叫的
        tool_functions = [
            check_customer_status,
            log_interaction,
            get_order_status,
            track_shipment,
            cancel_order,
            search_knowledge_base,
            run_diagnostic,
            create_ticket,
            get_billing_history,
            process_refund,
            update_payment_method,
        ]

        for func in tool_functions:
            assert callable(func), f"{func.__name__} 應該是可呼叫的"

    def test_tools_init_exports_all_functions(self):
        """測試 customer_support.tools 套件是否匯出所有函式。"""
        from customer_support import tools

        expected_exports = [
            'check_customer_status',
            'log_interaction',
            'get_order_status',
            'track_shipment',
            'cancel_order',
            'search_knowledge_base',
            'run_diagnostic',
            'create_ticket',
            'get_billing_history',
            'process_refund',
            'update_payment_method',
        ]

        for export in expected_exports:
            assert hasattr(tools, export), f"tutorial20.tools 應該匯出 {export}"

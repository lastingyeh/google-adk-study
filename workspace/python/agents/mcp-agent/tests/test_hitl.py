"""
針對人機互動 (HITL) 回呼功能的測試。

此模組測試 `before_tool_callback` 的實作，涵蓋：
- 從工具物件中提取工具名稱
- 破壞性操作的偵測
- 審批工作流程的邏輯
- 狀態管理
- 日誌記錄行為
"""

import pytest
from unittest.mock import Mock
from mcp_agent.agent import before_tool_callback


class TestToolNameExtraction:
    """測試工具名稱是否能從工具物件中正確提取。"""

    def test_extract_name_from_tool_with_name_attribute(self):
        """帶有 .name 屬性的工具應使用該名稱。"""
        # 建立一個帶有 name 屬性的模擬工具物件
        mock_tool = Mock()
        mock_tool.name = "write_file"

        # 建立帶有狀態的模擬 tool_context
        mock_context = Mock()
        mock_context.state = {}

        # 呼叫回呼函式
        before_tool_callback(
            tool=mock_tool,
            args={"path": "/test/file.txt", "content": "test"},
            tool_context=mock_context,
        )

        # 應在狀態中追蹤工具名稱
        assert mock_context.state.get("temp:last_tool") == "write_file"

    def test_extract_name_from_tool_without_name_attribute(self):
        """不帶 .name 屬性的工具應使用其字串表示。"""
        # 建立一個不帶 name 屬性的模擬工具物件
        mock_tool = Mock(spec=[])  # 沒有屬性

        # 建立帶有狀態的模擬 tool_context
        mock_context = Mock()
        mock_context.state = {}

        # 呼叫回呼函式
        before_tool_callback(
            tool=mock_tool, args={"path": "/test/file.txt"}, tool_context=mock_context
        )

        # 應使用字串表示
        assert "temp:last_tool" in mock_context.state
        assert isinstance(mock_context.state["temp:last_tool"], str)


class TestDestructiveOperationDetection:
    """測試需要審批的操作的偵測。"""

    @pytest.mark.parametrize(
        "operation_name",
        ["write_file", "write_text_file", "move_file", "create_directory"],
    )
    def test_destructive_operations_require_approval(self, operation_name):
        """所有破壞性操作在未自動審批時應需要審批。"""
        mock_tool = Mock()
        mock_tool.name = operation_name

        mock_context = Mock()
        mock_context.state = {}  # 沒有 auto_approve 標誌

        result = before_tool_callback(
            tool=mock_tool, args={"path": "/test/file.txt"}, tool_context=mock_context
        )

        # 應返回需要審批的訊息
        assert result is not None
        assert result["status"] == "requires_approval"
        assert "APPROVAL REQUIRED" in result["message"]
        assert result["tool_name"] == operation_name
        assert result["requires_approval"] is True

    @pytest.mark.parametrize(
        "operation_name",
        ["read_file", "list_directory", "search_files", "get_file_info"],
    )
    def test_safe_operations_allowed_without_approval(self, operation_name):
        """安全的讀取操作應無需審批即可允許。"""
        mock_tool = Mock()
        mock_tool.name = operation_name

        mock_context = Mock()
        mock_context.state = {}

        result = before_tool_callback(
            tool=mock_tool, args={"path": "/test/file.txt"}, tool_context=mock_context
        )

        # 應返回 None 以允許執行
        assert result is None


class TestApprovalWorkflow:
    """測試審批工作流程的邏輯。"""

    def test_auto_approve_flag_bypasses_approval(self):
        """當 auto_approve 為 True 時，應允許破壞性操作。"""
        mock_tool = Mock()
        mock_tool.name = "write_file"

        mock_context = Mock()
        mock_context.state = {"user:auto_approve_file_ops": True}

        result = before_tool_callback(
            tool=mock_tool,
            args={"path": "/test/file.txt", "content": "test"},
            tool_context=mock_context,
        )

        # 應返回 None 以允許執行
        assert result is None

    def test_missing_auto_approve_flag_blocks_destructive_ops(self):
        """當缺少 auto_approve 標誌時，應阻止破壞性操作。"""
        mock_tool = Mock()
        mock_tool.name = "write_file"

        mock_context = Mock()
        mock_context.state = {}  # 沒有 auto_approve 標誌

        result = before_tool_callback(
            tool=mock_tool,
            args={"path": "/test/file.txt", "content": "test"},
            tool_context=mock_context,
        )

        # 應返回阻止回應
        assert result is not None
        assert result["status"] == "requires_approval"

    def test_false_auto_approve_flag_blocks_destructive_ops(self):
        """當 auto_approve 明確為 False 時，應阻止破壞性操作。"""
        mock_tool = Mock()
        mock_tool.name = "write_file"

        mock_context = Mock()
        mock_context.state = {"user:auto_approve_file_ops": False}

        result = before_tool_callback(
            tool=mock_tool,
            args={"path": "/test/file.txt", "content": "test"},
            tool_context=mock_context,
        )

        # 應返回阻止回應
        assert result is not None
        assert result["status"] == "requires_approval"


class TestStateManagement:
    """測試回呼中的狀態追蹤。"""

    def test_tool_count_increments(self):
        """每次呼叫時，工具計數應增加。"""
        mock_tool = Mock()
        mock_tool.name = "read_file"

        mock_context = Mock()
        mock_context.state = {}

        # 第一次呼叫
        before_tool_callback(
            tool=mock_tool, args={"path": "/test/file1.txt"}, tool_context=mock_context
        )
        assert mock_context.state["temp:tool_count"] == 1

        # 第二次呼叫
        before_tool_callback(
            tool=mock_tool, args={"path": "/test/file2.txt"}, tool_context=mock_context
        )
        assert mock_context.state["temp:tool_count"] == 2

        # 第三次呼叫
        before_tool_callback(
            tool=mock_tool, args={"path": "/test/file3.txt"}, tool_context=mock_context
        )
        assert mock_context.state["temp:tool_count"] == 3

    def test_last_tool_tracked(self):
        """應在狀態中追蹤最後一個工具的名稱。"""
        mock_context = Mock()
        mock_context.state = {}

        # 使用第一個工具呼叫
        mock_tool1 = Mock()
        mock_tool1.name = "read_file"
        before_tool_callback(
            tool=mock_tool1, args={"path": "/test/file.txt"}, tool_context=mock_context
        )
        assert mock_context.state["temp:last_tool"] == "read_file"

        # 使用第二個工具呼叫
        mock_tool2 = Mock()
        mock_tool2.name = "list_directory"
        before_tool_callback(
            tool=mock_tool2, args={"path": "/test/"}, tool_context=mock_context
        )
        assert mock_context.state["temp:last_tool"] == "list_directory"

    def test_state_persists_across_calls(self):
        """狀態應在多次回呼調用之間保持不變。"""
        mock_context = Mock()
        mock_context.state = {
            "user:custom_data": "preserved",
            "temp:previous_value": 42,
        }

        mock_tool = Mock()
        mock_tool.name = "read_file"

        before_tool_callback(
            tool=mock_tool, args={"path": "/test/file.txt"}, tool_context=mock_context
        )

        # 原始狀態應被保留
        assert mock_context.state["user:custom_data"] == "preserved"
        assert mock_context.state["temp:previous_value"] == 42
        # 新狀態應被加入
        assert "temp:tool_count" in mock_context.state
        assert "temp:last_tool" in mock_context.state


class TestApprovalMessageContent:
    """測試審批訊息的內容。"""

    def test_approval_message_includes_operation_name(self):
        """審批訊息應包含操作名稱。"""
        mock_tool = Mock()
        mock_tool.name = "write_file"

        mock_context = Mock()
        mock_context.state = {}

        result = before_tool_callback(
            tool=mock_tool,
            args={"path": "/test/file.txt", "content": "test"},
            tool_context=mock_context,
        )

        assert "write_file" in result["message"]
        assert result["tool_name"] == "write_file"

    def test_approval_message_includes_reason(self):
        """審批訊息應包含阻止的原因。"""
        mock_tool = Mock()
        mock_tool.name = "write_file"

        mock_context = Mock()
        mock_context.state = {}

        result = before_tool_callback(
            tool=mock_tool,
            args={"path": "/test/file.txt", "content": "test"},
            tool_context=mock_context,
        )

        assert "Reason:" in result["message"]
        assert "modifies" in result["message"].lower()

    def test_approval_message_includes_arguments(self):
        """審批訊息應包含傳遞給工具的參數。"""
        mock_tool = Mock()
        mock_tool.name = "move_file"

        mock_context = Mock()
        mock_context.state = {}

        args = {"source": "/test/old.txt", "destination": "/test/new.txt"}
        result = before_tool_callback(
            tool=mock_tool, args=args, tool_context=mock_context
        )

        assert "Arguments:" in result["message"]
        assert "args" in result
        assert result["args"] == args

    def test_approval_message_includes_instructions(self):
        """審批訊息應包含如何審批的說明。"""
        mock_tool = Mock()
        mock_tool.name = "create_directory"

        mock_context = Mock()
        mock_context.state = {}

        result = before_tool_callback(
            tool=mock_tool, args={"path": "/test/new_dir"}, tool_context=mock_context
        )

        assert "auto_approve_file_ops" in result["message"]
        assert "BLOCKED" in result["message"]


class TestEdgeCases:
    """測試邊界情況與錯誤處理。"""

    def test_empty_args(self):
        """回呼應能處理空的 args 字典。"""
        mock_tool = Mock()
        mock_tool.name = "list_directory"

        mock_context = Mock()
        mock_context.state = {}

        # 不應引發例外
        result = before_tool_callback(
            tool=mock_tool, args={}, tool_context=mock_context
        )

        assert result is None  # 安全操作

    def test_none_state_values(self):
        """回呼應能處理狀態中的 None 值。"""
        mock_tool = Mock()
        mock_tool.name = "read_file"

        mock_context = Mock()
        mock_context.state = {
            "temp:tool_count": None,
            "user:auto_approve_file_ops": None,
        }

        # 應優雅地處理 None
        result = before_tool_callback(
            tool=mock_tool, args={"path": "/test/file.txt"}, tool_context=mock_context
        )

        # 計數應從 1 開始 (None 被視為 0)
        assert mock_context.state["temp:tool_count"] == 1

    def test_unknown_tool_name_allowed(self):
        """未知的工具名稱 (不在破壞性清單中) 應被允許。"""
        mock_tool = Mock()
        mock_tool.name = "custom_unknown_operation"

        mock_context = Mock()
        mock_context.state = {}

        result = before_tool_callback(
            tool=mock_tool, args={"param": "value"}, tool_context=mock_context
        )

        # 應允許未知操作 (預設為安全)
        assert result is None


class TestIntegrationScenarios:
    """測試實際的整合情境。"""

    def test_workflow_read_then_write(self):
        """測試一個讀取檔案後再寫入的工作流程。"""
        mock_context = Mock()
        mock_context.state = {}

        # 步驟 1：讀取檔案 (應被允許)
        read_tool = Mock()
        read_tool.name = "read_file"
        result1 = before_tool_callback(
            tool=read_tool,
            args={"path": "/test/config.json"},
            tool_context=mock_context,
        )
        assert result1 is None
        assert mock_context.state["temp:tool_count"] == 1

        # 步驟 2：寫入檔案 (在沒有審批的情況下應被阻止)
        write_tool = Mock()
        write_tool.name = "write_file"
        result2 = before_tool_callback(
            tool=write_tool,
            args={"path": "/test/config.json", "content": "updated"},
            tool_context=mock_context,
        )
        assert result2 is not None
        assert result2["status"] == "requires_approval"
        assert mock_context.state["temp:tool_count"] == 2

        # 步驟 3：啟用自動審批
        mock_context.state["user:auto_approve_file_ops"] = True

        # 步驟 4：再次寫入檔案 (現在應被允許)
        result3 = before_tool_callback(
            tool=write_tool,
            args={"path": "/test/config.json", "content": "updated"},
            tool_context=mock_context,
        )
        assert result3 is None
        assert mock_context.state["temp:tool_count"] == 3

    def test_multiple_destructive_operations_blocked(self):
        """測試多個破壞性操作是否都被阻止。"""
        mock_context = Mock()
        mock_context.state = {}

        destructive_ops = [
            ("write_file", {"path": "/test/file1.txt", "content": "test1"}),
            ("write_text_file", {"path": "/test/file2.txt", "content": "test2"}),
            ("move_file", {"source": "/test/old.txt", "dest": "/test/new.txt"}),
            ("create_directory", {"path": "/test/new_dir"}),
        ]

        for op_name, args in destructive_ops:
            mock_tool = Mock()
            mock_tool.name = op_name

            blocked_result = before_tool_callback(
                tool=mock_tool, args=args, tool_context=mock_context
            )

            # 所有操作都應被阻止
            assert blocked_result is not None
            assert blocked_result["status"] == "requires_approval"
            assert blocked_result["tool_name"] == op_name


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

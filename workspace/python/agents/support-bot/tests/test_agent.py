"""
Tutorial 33 Support Bot 的 Agent 設定與工具測試

測試涵蓋：
- Agent 設定
- 工具功能
- 工具回傳格式
- 知識庫搜尋
- 建立工單
"""

import pytest
from support_bot.agent import (
    root_agent,
    search_knowledge_base,
    create_support_ticket,
    KNOWLEDGE_BASE,
    TICKETS
)


class TestAgentConfiguration:
    """測試 Agent 設定"""

    def test_root_agent_exists(self):
        """測試 root_agent 是否已定義且可存取。

        重點: 驗證 Agent 物件是否存在。
        """
        assert root_agent is not None

    def test_agent_name(self):
        """測試 Agent 名稱。

        重點: 驗證 Agent 名稱是否為 'support_bot'。
        """
        assert root_agent.name == "support_bot"

    def test_agent_model(self):
        """測試 Agent 使用正確的模型。

        重點: 驗證模型是否設定為 'gemini-2.5-flash'。
        """
        assert root_agent.model == "gemini-2.5-flash"

    def test_agent_has_description(self):
        """測試 Agent 是否有描述。

        重點: 驗證描述屬性存在、為字串且長度大於 10。
        """
        assert root_agent.description
        assert isinstance(root_agent.description, str)
        assert len(root_agent.description) > 10

    def test_agent_has_instruction(self):
        """測試 Agent 是否有指示 (instruction)。

        重點: 驗證指示屬性存在、為字串且長度大於 50。
        """
        assert root_agent.instruction
        assert isinstance(root_agent.instruction, str)
        assert len(root_agent.instruction) > 50

    def test_agent_has_two_tools(self):
        """測試 Agent 是否剛好有 2 個工具。

        重點: 驗證工具列表長度為 2。
        """
        assert len(root_agent.tools) == 2

    def test_agent_tools_are_functions(self):
        """測試 Agent 工具是否為可呼叫的函式。

        重點: 驗證工具列表中的每個項目都是 callable。
        """
        for tool in root_agent.tools:
            assert callable(tool)


class TestSearchKnowledgeBase:
    """測試知識庫搜尋工具"""

    def test_search_finds_password_reset(self):
        """測試搜尋密碼重設相關文章。

        重點: 驗證搜尋 'password reset' 能成功回傳結果並包含文章。
        """
        result = search_knowledge_base("password reset")
        assert result['status'] == 'success'
        assert result['report'] is not None
        assert 'article' in result

    def test_search_finds_vacation_policy(self):
        """測試搜尋休假政策相關文章。

        重點: 驗證搜尋 'vacation' 能找到標題包含 'Vacation' 的文章。
        """
        result = search_knowledge_base("vacation")
        assert result['status'] == 'success'
        assert result['article'] is not None
        assert "Vacation" in result['article']['title']

    def test_search_finds_expense_report(self):
        """測試搜尋費用報告相關文章。

        重點: 驗證搜尋 'expense' 能找到標題包含 'Expense' 的文章。
        """
        result = search_knowledge_base("expense")
        assert result['status'] == 'success'
        assert 'Expense' in result['article']['title']

    def test_search_finds_remote_work(self):
        """測試搜尋遠端工作相關文章。

        重點: 驗證搜尋 'remote work' 能找到標題包含 'Remote' 的文章。
        """
        result = search_knowledge_base("remote work")
        assert result['status'] == 'success'
        assert 'Remote' in result['article']['title']

    def test_search_finds_it_support(self):
        """測試搜尋 IT 支援相關文章。

        重點: 驗證搜尋 'IT support' 能找到標題包含 'IT' 的文章。
        """
        result = search_knowledge_base("IT support")
        assert result['status'] == 'success'
        assert 'IT' in result['article']['title']

    def test_search_no_matches(self):
        """測試搜尋無相符項目。

        重點: 驗證搜尋不存在的主題會回傳成功狀態但沒有文章，且報告中包含 'No articles found'。
        """
        result = search_knowledge_base("nonexistent topic xyz")
        assert result['status'] == 'success'
        assert result['article'] is None
        assert 'No articles found' in result['report']

    def test_search_case_insensitive(self):
        """測試搜尋不分大小寫。

        重點: 驗證 'PASSWORD' 和 'password' 都能成功搜尋。
        """
        result1 = search_knowledge_base("PASSWORD")
        result2 = search_knowledge_base("password")
        assert result1['status'] == 'success'
        assert result2['status'] == 'success'

    def test_search_returns_content(self):
        """測試搜尋回傳完整的文章內容。

        重點: 驗證回傳的文章包含標題和內容，且內容長度大於 50。
        """
        result = search_knowledge_base("password")
        assert result['article'] is not None
        assert result['article']['title']
        assert result['article']['content']
        assert len(result['article']['content']) > 50

    def test_search_return_format(self):
        """測試搜尋回傳格式是否正確。

        重點: 驗證回傳的字典包含 'status' 和 'report' 欄位。
        """
        result = search_knowledge_base("vacation")
        assert 'status' in result
        assert 'report' in result
        assert result['status'] in ['success', 'error']
        assert isinstance(result['report'], str)

    def test_search_error_handling(self):
        """測試搜尋能優雅地處理錯誤。

        重點: 驗證傳入 None 時，是否能處理異常或回傳適當格式。
        """
        # Pass None to test error handling
        try:
            result = search_knowledge_base(None)
            # If it doesn't raise, it should still return proper format
            assert 'status' in result
        except TypeError:
            # This is acceptable - function signature validation
            pass


class TestCreateSupportTicket:
    """測試建立支援工單工具"""

    def test_create_ticket_normal_priority(self):
        """測試建立普通優先順序的工單。

        重點: 驗證建立 'normal' 優先順序的工單，回傳包含工單 ID (TKT- 開頭) 和正確的優先順序。
        """
        result = create_support_ticket(
            subject="VPN connection issue",
            description="Cannot connect to company VPN",
            priority="normal"
        )
        assert result['status'] == 'success'
        assert 'ticket' in result
        assert result['ticket']['id'].startswith('TKT-')
        assert result['ticket']['priority'] == 'normal'

    def test_create_ticket_high_priority(self):
        """測試建立高優先順序的工單。

        重點: 驗證建立 'high' 優先順序的工單。
        """
        result = create_support_ticket(
            subject="Production error",
            description="API is down",
            priority="high"
        )
        assert result['status'] == 'success'
        assert result['ticket']['priority'] == 'high'

    def test_create_ticket_urgent_priority(self):
        """測試建立緊急優先順序的工單。

        重點: 驗證建立 'urgent' 優先順序的工單。
        """
        result = create_support_ticket(
            subject="Security breach",
            description="Suspicious activity detected",
            priority="urgent"
        )
        assert result['status'] == 'success'
        assert result['ticket']['priority'] == 'urgent'

    def test_create_ticket_default_priority(self):
        """測試建立預設優先順序的工單。

        重點: 驗證未指定優先順序時，預設為 'normal'。
        """
        result = create_support_ticket(
            subject="Test ticket",
            description="Test description"
        )
        assert result['status'] == 'success'
        assert result['ticket']['priority'] == 'normal'

    def test_create_ticket_invalid_priority(self):
        """測試建立無效優先順序的工單。

        重點: 驗證使用無效的優先順序時，回傳錯誤狀態。
        """
        result = create_support_ticket(
            subject="Test",
            description="Test",
            priority="invalid"
        )
        assert result['status'] == 'error'
        assert 'Invalid priority' in result['report']

    def test_create_ticket_return_format(self):
        """測試工單建立的回傳格式。

        重點: 驗證回傳結果包含狀態、報告和工單詳情。
        """
        result = create_support_ticket(
            subject="Test",
            description="Test description",
            priority="normal"
        )
        assert 'status' in result
        assert 'report' in result
        assert 'ticket' in result
        assert result['ticket']['id']
        assert result['ticket']['subject']
        assert result['ticket']['priority']

    def test_create_ticket_generates_unique_ids(self):
        """測試每張工單都有唯一的 ID。

        重點: 驗證兩次建立工單會產生不同的 ID。
        """
        result1 = create_support_ticket("Test 1", "Desc 1")
        result2 = create_support_ticket("Test 2", "Desc 2")
        assert result1['ticket']['id'] != result2['ticket']['id']

    def test_create_ticket_stores_in_tickets_dict(self):
        """測試建立的工單會被儲存。

        重點: 驗證建立工單後，可從 TICKETS 字典中依 ID 檢索到。
        """
        # Clear previous tickets for this test
        initial_count = len(TICKETS)

        result = create_support_ticket("Test", "Description")
        ticket_id = result['ticket']['id']

        assert ticket_id in TICKETS
        assert TICKETS[ticket_id]['subject'] == "Test"
        assert TICKETS[ticket_id]['priority'] == "normal"

    def test_ticket_has_timestamps(self):
        """測試建立的工單包含時間戳記。

        重點: 驗證儲存的工單包含 'created_at' 欄位。
        """
        result = create_support_ticket("Test", "Description")
        ticket = TICKETS[result['ticket']['id']]
        assert 'created_at' in ticket
        assert ticket['created_at']

    def test_ticket_has_open_status(self):
        """測試新工單的狀態為開啟。

        重點: 驗證新建立的工單 status 為 'open'。
        """
        result = create_support_ticket("Test", "Description")
        ticket = TICKETS[result['ticket']['id']]
        assert ticket['status'] == 'open'


class TestToolReturnFormats:
    """測試工具回傳正確的結構化格式"""

    def test_search_has_required_fields(self):
        """測試搜尋結果包含必要欄位。

        重點: 驗證搜尋結果包含 'status' 和 'report'。
        """
        result = search_knowledge_base("test")
        assert 'status' in result
        assert 'report' in result
        required_fields = {'status', 'report'}
        assert required_fields.issubset(result.keys())

    def test_create_ticket_has_required_fields(self):
        """測試建立工單包含必要欄位。

        重點: 驗證建立工單結果包含 'status', 'report', 'ticket'。
        """
        result = create_support_ticket("Test", "Desc")
        assert 'status' in result
        assert 'report' in result
        assert 'ticket' in result
        required_fields = {'status', 'report', 'ticket'}
        assert required_fields.issubset(result.keys())

    def test_results_have_string_reports(self):
        """測試所有結果都有字串報告。

        重點: 驗證 'report' 欄位為字串且非空。
        """
        search_result = search_knowledge_base("test")
        ticket_result = create_support_ticket("Test", "Desc")

        assert isinstance(search_result['report'], str)
        assert isinstance(ticket_result['report'], str)
        assert len(search_result['report']) > 0
        assert len(ticket_result['report']) > 0


class TestKnowledgeBase:
    """測試知識庫資料"""

    def test_knowledge_base_populated(self):
        """測試知識庫已有文章。

        重點: 驗證 KNOWLEDGE_BASE 字典不為空。
        """
        assert len(KNOWLEDGE_BASE) > 0

    def test_knowledge_base_has_required_articles(self):
        """測試知識庫包含預期的文章。

        重點: 驗證知識庫包含特定的 key (如 password_reset, vacation_policy 等)。
        """
        expected_keys = {
            'password_reset',
            'expense_report',
            'vacation_policy',
            'remote_work',
            'it_support'
        }
        assert expected_keys.issubset(KNOWLEDGE_BASE.keys())

    def test_articles_have_required_fields(self):
        """測試所有文章都包含必要欄位。

        重點: 驗證每篇文章都有 'title', 'content', 'tags' 且 tags 為列表。
        """
        for key, article in KNOWLEDGE_BASE.items():
            assert 'title' in article
            assert 'content' in article
            assert 'tags' in article
            assert isinstance(article['tags'], list)
            assert len(article['tags']) > 0

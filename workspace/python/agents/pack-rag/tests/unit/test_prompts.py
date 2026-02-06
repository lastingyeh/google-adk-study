"""
Prompts 模組測試
"""


class TestReturnInstructionsRoot:
    """
    測試 return_instructions_root 函式。

    重點說明:
    1. 驗證指令生成函式
    2. 驗證指令內容 (包含檢索、引用、角色定義)
    3. 驗證指令格式 (長度、無佔位符)
    """

    def test_function_exists(self):
        """
        測試 return_instructions_root 函式是否存在。

        驗證點:
        1. 函式存在且可呼叫
        """
        from rag.prompts import return_instructions_root

        assert return_instructions_root is not None
        assert callable(return_instructions_root)

    def test_function_returns_string(self):
        """
        測試函式回傳值為字串。

        驗證點:
        1. 回傳類型為 str
        """
        from rag.prompts import return_instructions_root

        result = return_instructions_root()
        assert isinstance(result, str)

    def test_instruction_has_content(self):
        """測試指令內容不為空。"""
        from rag.prompts import return_instructions_root

        result = return_instructions_root()
        assert len(result) > 0

    def test_instruction_contains_retrieval_guidance(self):
        """測試指令是否包含檢索相關的指引。"""
        from rag.prompts import return_instructions_root

        result = return_instructions_root()
        result_lower = result.lower()

        # 檢查是否包含檢索相關的關鍵字
        retrieval_keywords = ["retrieval", "retrieve", "corpus", "document"]
        has_retrieval_content = any(
            keyword in result_lower for keyword in retrieval_keywords
        )
        assert has_retrieval_content, "指令應包含檢索相關的指引"

    def test_instruction_contains_citation_guidance(self):
        """測試指令是否包含引用格式的指引。"""
        from rag.prompts import return_instructions_root

        result = return_instructions_root()
        result_lower = result.lower()

        # 檢查是否包含引用相關的關鍵字
        citation_keywords = ["citation", "cite", "reference", "source"]
        has_citation_content = any(
            keyword in result_lower for keyword in citation_keywords
        )
        assert has_citation_content, "指令應包含引用格式的指引"

    def test_instruction_mentions_rag_tool(self):
        """測試指令是否提及 RAG 檢索工具。"""
        from rag.prompts import return_instructions_root

        result = return_instructions_root()

        # 檢查是否提及檢索工具
        assert (
            "ask_vertex_retrieval" in result
            or "retrieval" in result.lower()
            or "retrieve" in result.lower()
        ), "指令應提及檢索工具的使用"

    def test_instruction_defines_ai_role(self):
        """測試指令是否定義了 AI 助手的角色。"""
        from rag.prompts import return_instructions_root

        result = return_instructions_root()
        result_lower = result.lower()

        # 檢查是否定義角色
        role_keywords = ["you are", "assistant", "role", "ai"]
        has_role_definition = any(keyword in result_lower for keyword in role_keywords)
        assert has_role_definition, "指令應定義 AI 助手的角色"

    def test_instruction_has_answer_guidelines(self):
        """測試指令是否包含回答準則。"""
        from rag.prompts import return_instructions_root

        result = return_instructions_root()
        result_lower = result.lower()

        # 檢查是否包含回答準則關鍵字（支援中英文）
        guideline_keywords = [
            "answer",
            "provide",
            "respond",
            "do not",
            "提供",
            "答案",
            "回答",
            "請勿",
            "請不要",
        ]
        has_guidelines = any(keyword in result_lower for keyword in guideline_keywords)
        assert has_guidelines, "指令應包含回答準則"

    def test_instruction_length_is_reasonable(self):
        """測試指令長度合理（不會太短也不會過長）。"""
        from rag.prompts import return_instructions_root

        result = return_instructions_root()

        # 指令應該有足夠的長度來提供詳細指引，但也不應過長
        assert len(result) > 100, "指令長度應超過 100 字元"
        assert len(result) < 10000, "指令長度不應超過 10000 字元"

    def test_instruction_format(self):
        """測試指令格式是否適當。"""
        from rag.prompts import return_instructions_root

        result = return_instructions_root()

        # 檢查是否是有效的字串且不包含異常字元
        assert isinstance(result, str)
        assert result.strip() == result or len(result.strip()) > 0

    def test_instruction_no_placeholders(self):
        """測試指令中不應包含未填入的佔位符。"""
        from rag.prompts import return_instructions_root

        result = return_instructions_root()

        # 檢查是否包含常見的未填入佔位符
        placeholders = ["{}", "{{", "}}", "TODO", "FIXME", "XXX"]
        for placeholder in placeholders:
            assert placeholder not in result, (
                f"指令不應包含未填入的佔位符：{placeholder}"
            )

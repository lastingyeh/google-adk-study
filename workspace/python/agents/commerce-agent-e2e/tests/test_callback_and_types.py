# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""接地中繼資料回呼和型別安全的測試。"""

import pytest
from commerce_agent import create_grounding_callback
from commerce_agent.callbacks import _extract_domain, _calculate_confidence
from commerce_agent.types import (
    ToolResult,
    UserPreferences,
    GroundingSource,
    GroundingSupport,
    GroundingMetadata,
)
from commerce_agent.tools.preferences import save_preferences, get_preferences
from unittest.mock import Mock


class TestGroundingMetadataCallback:
    """測試接地中繼資料回呼函式。"""

    def test_callback_creation(self):
        """測試回呼函式可以被建立。"""
        callback = create_grounding_callback(verbose=True)
        assert callback is not None
        assert callable(callback)

        callback_silent = create_grounding_callback(verbose=False)
        assert callable(callback_silent)

    def test_extract_domain(self):
        """測試從 URL 中提取網域。"""
        # 測試各種 URL 格式
        assert (
            _extract_domain("https://www.decathlon.com.hk/product")
            == "decathlon.com.hk"
        )
        assert _extract_domain("http://example.com/path") == "example.com"
        assert (
            _extract_domain("https://subdomain.example.com") == "subdomain.example.com"
        )
        assert _extract_domain("www.test.com") == "test.com"
        assert _extract_domain("invalid-url") == "invalid-url"

    def test_calculate_confidence(self):
        """測試信賴等級計算。"""
        assert _calculate_confidence(0) == "low"
        assert _calculate_confidence(1) == "low"
        assert _calculate_confidence(2) == "medium"
        assert _calculate_confidence(3) == "high"
        assert _calculate_confidence(5) == "high"

    @pytest.mark.asyncio
    async def test_callback_no_candidates(self):
        """測試回呼處理沒有候選者的回應。"""
        callback = create_grounding_callback(verbose=False)

        # 模擬沒有候選者的回呼上下文和回應
        callback_context = Mock()
        callback_context.state = {}
        llm_response = Mock()
        llm_response.candidates = []

        # 不應引發錯誤並返回 None
        result = await callback(callback_context, llm_response)
        assert result is None

    @pytest.mark.asyncio
    async def test_callback_with_metadata(self):
        """測試回呼從回應中提取接地中繼資料。"""
        callback = create_grounding_callback(verbose=False)

        # 模擬回呼上下文
        callback_context = Mock()
        callback_context.state = {}

        # 模擬接地資料區塊
        chunk1 = Mock()
        chunk1.web = Mock()
        chunk1.web.title = "Decathlon - Brooks Divide 5"
        chunk1.web.uri = "https://www.decathlon.com.hk/brooks-divide-5"

        chunk2 = Mock()
        chunk2.web = Mock()
        chunk2.web.title = "AllTricks - Running Shoes"
        chunk2.web.uri = "https://www.alltricks.com/running-shoes"

        # 模擬接地支援
        support1 = Mock()
        support1.segment = Mock()
        support1.segment.text = "Brooks Divide 5 costs €95"
        support1.segment.start_index = 0
        support1.segment.end_index = 26
        support1.grounding_chunk_indices = [0, 1]

        # 設定帶有中繼資料的候選者
        candidate = Mock()
        candidate.grounding_metadata = Mock()
        candidate.grounding_metadata.grounding_chunks = [chunk1, chunk2]
        candidate.grounding_metadata.grounding_supports = [support1]

        # 模擬回應
        llm_response = Mock()
        llm_response.candidates = [candidate]

        # 處理回應
        result = await callback(callback_context, llm_response)

        # 驗證回傳值
        assert result is None

        # 驗證狀態已更新
        assert "temp:_grounding_sources" in callback_context.state
        assert "temp:_grounding_metadata" in callback_context.state

        # 驗證來源
        sources = callback_context.state["temp:_grounding_sources"]
        assert len(sources) == 2
        assert sources[0]["title"] == "Decathlon - Brooks Divide 5"
        assert sources[0]["domain"] == "decathlon.com.hk"

        # 驗證中繼資料
        metadata = callback_context.state["temp:_grounding_metadata"]
        assert metadata["total_sources"] == 2
        assert len(metadata["supports"]) == 1
        assert metadata["supports"][0]["confidence"] == "medium"  # 2 sources


class TestToolTypes:
    """測試 TypedDict 定義是否正常運作。"""

    def test_tool_result_success(self):
        """測試成功操作的 ToolResult。"""
        result: ToolResult = {
            "status": "success",
            "report": "Operation completed",
            "data": {"value": 42},
        }

        assert result["status"] == "success"
        assert result["report"] == "Operation completed"
        assert result["data"]["value"] == 42

    def test_tool_result_error(self):
        """測試錯誤情況下的 ToolResult。"""
        result: ToolResult = {
            "status": "error",
            "report": "Operation failed",
            "error": "ValueError: Invalid input",
        }

        assert result["status"] == "error"
        assert "error" in result

    def test_user_preferences_structure(self):
        """測試 UserPreferences 結構。"""
        prefs: UserPreferences = {
            "sport": "running",
            "budget_max": 100,
            "experience_level": "beginner",
        }

        assert prefs["sport"] == "running"
        assert prefs["budget_max"] == 100
        assert prefs["experience_level"] == "beginner"

    def test_grounding_source_structure(self):
        """測試 GroundingSource 結構。"""
        source: GroundingSource = {
            "title": "Product Page",
            "uri": "https://example.com/product",
            "domain": "example.com",
        }

        assert source["title"] == "Product Page"
        assert source["uri"] == "https://example.com/product"
        assert source["domain"] == "example.com"

    def test_grounding_support_structure(self):
        """測試 GroundingSupport 結構。"""
        support: GroundingSupport = {
            "text": "Product costs €95",
            "start_index": 0,
            "end_index": 18,
            "source_indices": [0, 1],
            "confidence": "high",
        }

        assert support["text"] == "Product costs €95"
        assert len(support["source_indices"]) == 2
        assert support["confidence"] == "high"

    def test_grounding_metadata_structure(self):
        """測試完整的 GroundingMetadata 結構。"""
        metadata: GroundingMetadata = {
            "sources": [
                {
                    "title": "Source 1",
                    "uri": "https://example.com/1",
                    "domain": "example.com",
                }
            ],
            "supports": [
                {
                    "text": "Sample text",
                    "start_index": 0,
                    "end_index": 11,
                    "source_indices": [0],
                    "confidence": "low",
                }
            ],
            "search_suggestions": ["related search"],
            "total_sources": 1,
        }

        assert len(metadata["sources"]) == 1
        assert len(metadata["supports"]) == 1
        assert metadata["total_sources"] == 1


class TestPreferencesWithTypes:
    """測試偏好設定工具回傳與 ToolResult 相容的字典。"""

    def test_save_preferences_return_type(self):
        """測試 save_preferences 回傳的字典符合 ToolResult 結構。"""
        # 模擬工具上下文 - ADK v1.17+ 直接使用 tool_context.state
        tool_context = Mock()
        tool_context.state = {}

        # 呼叫函式
        result = save_preferences(
            sport="running",
            budget_max=100,
            experience_level="beginner",
            tool_context=tool_context,
        )

        # 驗證回傳型別結構
        assert "status" in result
        assert "report" in result
        assert result["status"] == "success"
        assert "data" in result

        # 驗證狀態已更新
        assert tool_context.state["user:pref_sport"] == "running"
        assert tool_context.state["user:pref_budget"] == 100
        assert tool_context.state["user:pref_experience"] == "beginner"

    def test_get_preferences_return_type(self):
        """測試 get_preferences 回傳的字典符合 ToolResult 結構。"""
        # 模擬帶有現有偏好設定的工具上下文 - ADK v1.17+ 使用 tool_context.state
        tool_context = Mock()
        tool_context.state = {
            "user:pref_sport": "cycling",
            "user:pref_budget": 200,
            "user:pref_experience": "intermediate",
        }

        # 呼叫函式
        result = get_preferences(tool_context=tool_context)

        # 驗證回傳型別結構
        assert "status" in result
        assert "report" in result
        assert result["status"] == "success"
        assert "data" in result

        # 驗證資料
        assert result["data"]["sport"] == "cycling"
        assert result["data"]["budget_max"] == 200
        assert result["data"]["experience_level"] == "intermediate"

    def test_get_preferences_empty_state(self):
        """測試 get_preferences 在沒有儲存偏好設定的情況。"""
        # 模擬空狀態的工具上下文 - ADK v1.17+ 使用 tool_context.state
        tool_context = Mock()
        tool_context.state = {}

        # 呼叫函式
        result = get_preferences(tool_context=tool_context)

        # 驗證回傳成功且資料為空
        assert result["status"] == "success"
        assert result["data"] == {}
        assert "No preferences" in result["report"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

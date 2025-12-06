"""從 Google Search 結果中提取 grounding metadata 的回調函式。

此模組提供基於函式的回調，用於可觀察性 (observability) 和來源歸因追蹤。
ADK 使用遵循以下模式的基於函式的回調：
- before_agent, after_agent
- before_model, after_model
- before_tool, after_tool

使用範例:
    from commerce_agent.callbacks import create_grounding_callback
    from google.adk.agents import Agent

    agent = Agent(
        name="my_agent",
        model="gemini-2.5-flash",
        after_model=create_grounding_callback(verbose=True)
    )
"""

from .types import GroundingMetadata, GroundingSource, GroundingSupport


def _extract_domain(url: str) -> str:
    """從 URL 中提取網域名稱。

    參數:
        url: 完整的 URL。

    回傳:
        網域名稱 (例如："decathlon.com")。
    """
    try:
        # 移除協定
        if "://" in url:
            url = url.split("://", 1)[1]

        # 提取網域 (第一個 / 之前的部分)
        domain = url.split("/")[0]

        # 移除 www. 前綴
        if domain.startswith("www."):
            domain = domain[4:]

        return domain
    except Exception:
        return "unknown"


def _calculate_confidence(num_sources: int) -> str:
    """根據來源數量計算信心水準。

    參數:
        num_sources: 支持某個論點的來源數量。

    回傳:
        信心水準："high"、"medium" 或 "low"。
    """
    if num_sources >= 3:
        return "high"
    elif num_sources >= 2:
        return "medium"
    else:
        return "low"


def create_grounding_callback(verbose: bool = True):
    """建立一個用於提取 grounding metadata 的回調函式。

    此函式會回傳一個 after_model 回調，用於從 Google Search 結果中提取 grounding metadata。

    參數:
        verbose: 若為 True，則將 grounding 資訊列印到主控台。

    回傳:
        可用於 Agent(after_model=...) 的非同步回調函式。

    範例:
        agent = Agent(
            name="search_agent",
            model="gemini-2.5-flash",
            tools=[google_search],
            after_model=create_grounding_callback(verbose=True)
        )
    """

    async def extract_grounding_metadata(callback_context, llm_response):
        """從 LLM 回應中提取 grounding metadata。

        參數:
            callback_context: 帶有狀態的 ADK 回調上下文。
            llm_response: 可能包含 grounding metadata 的 LLM 回應。
        """
        # 檢查回應是否包含 grounding metadata
        if not hasattr(llm_response, 'candidates') or not llm_response.candidates:
            return None

        candidate = llm_response.candidates[0]
        if not hasattr(candidate, 'grounding_metadata') or not candidate.grounding_metadata:
            return None

        # 提取 grounding metadata
        metadata = candidate.grounding_metadata

        # 提取來源資訊
        sources: list[GroundingSource] = []
        if hasattr(metadata, 'grounding_chunks') and metadata.grounding_chunks:
            for chunk in metadata.grounding_chunks:
                if hasattr(chunk, 'web') and chunk.web:
                    domain = _extract_domain(chunk.web.uri) if chunk.web.uri else None
                    source: GroundingSource = {
                        "title": chunk.web.title or "Unknown",
                        "uri": chunk.web.uri or "",
                        "domain": domain
                    }
                    sources.append(source)

        # 提取 grounding supports (片段層級的歸因)
        supports: list[GroundingSupport] = []
        if hasattr(metadata, 'grounding_supports') and metadata.grounding_supports:
            for support in metadata.grounding_supports:
                if hasattr(support, 'segment') and support.segment:
                    segment = support.segment

                    # 根據支持來源的數量計算信心水準
                    num_sources = len(support.grounding_chunk_indices) if hasattr(support, 'grounding_chunk_indices') else 0
                    confidence = _calculate_confidence(num_sources)

                    support_item: GroundingSupport = {
                        "text": segment.text if hasattr(segment, 'text') else "",
                        "start_index": segment.start_index if hasattr(segment, 'start_index') else 0,
                        "end_index": segment.end_index if hasattr(segment, 'end_index') else 0,
                        "source_indices": list(support.grounding_chunk_indices) if hasattr(support, 'grounding_chunk_indices') else [],
                        "confidence": confidence
                    }
                    supports.append(support_item)

        # 建立完整的 metadata 結構
        grounding_data: GroundingMetadata = {
            "sources": sources,
            "supports": supports,
            "search_suggestions": [],  # 可從 search_entry_point 提取
            "total_sources": len(sources)
        }

        # 儲存於 session state (當前調用的暫時範圍)
        if hasattr(callback_context, 'state'):
            callback_context.state["temp:_grounding_sources"] = sources
            callback_context.state["temp:_grounding_metadata"] = grounding_data

        # 用於偵錯的日誌
        if verbose:
            print(f"\n{'='*60}")
            print("✓ GROUNDING METADATA 已提取")
            print(f"{'='*60}")
            print(f"總來源數: {len(sources)}")

            if sources:
                print("\n來源:")
                for i, source in enumerate(sources, 1):
                    domain = source.get("domain", "unknown")
                    title = source.get("title", "Unknown")
                    print(f"  {i}. [{domain}] {title}")

            if supports:
                print(f"\nGrounding Supports: {len(supports)} 個片段")
                for i, support in enumerate(supports[:3], 1):  # 顯示前 3 個
                    text = support["text"][:60] + "..." if len(support["text"]) > 60 else support["text"]
                    confidence = support.get("confidence", "unknown")
                    num_sources = len(support["source_indices"])
                    print(f"  {i}. [{confidence}] \"{text}\" ({num_sources} 個來源)")

                if len(supports) > 3:
                    print(f"  ... 以及其他 {len(supports) - 3} 個")

            print(f"{'='*60}\n")

        return None  # ADK 回調函式回傳 None 或 ModelContent

    return extract_grounding_metadata


__all__ = ["create_grounding_callback"]

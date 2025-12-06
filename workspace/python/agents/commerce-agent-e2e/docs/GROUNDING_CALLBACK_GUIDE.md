# Grounding Metadata Callback - Usage Guide

本指南說明如何使用 `create_grounding_callback` 函式來提取並監控 Google Search Grounding Metadata。

## 概述

`create_grounding_callback` 函式建立一個 ADK `after_model` 回調，用於從 Google Search 結果中提取來源歸因資訊，提供：
- ✅ 來自 grounding chunks 的來源 URL 和標題
- ✅ 片段歸因 (Segment Attribution) (哪些來源支持哪些聲明)
- ✅ 基於多來源一致性的信心分數 (Confidence Scores)
- ✅ 用於識別零售商的網域提取
- ✅ 用於除錯的主控台日誌

## 快速開始

### 基本用法

```python
from commerce_agent import root_agent, create_grounding_callback
from google.adk.agents import Agent

# 建立帶有接地回調的代理人
agent_with_callback = Agent(
    name=root_agent.name,
    model=root_agent.model,
    description=root_agent.description,
    instruction=root_agent.instruction,
    tools=root_agent.tools,
    after_model=create_grounding_callback(verbose=True)  # 啟用 grounding callback
)

# 或者在 Runner 中使用回調
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name="commerce_agent",
    session_service=session_service,
    after_model_callbacks=[create_grounding_callback(verbose=True)]
)

# 執行代理人
session = await session_service.create_session(
    app_name="commerce_agent",
    user_id="user123",
    session_id="session456"
)

result = await runner.run_async(
    user_id="user123",
    session_id="session456",
    new_message={"role": "user", "parts": [{"text": "Show me trail running shoes under €100"}]}
)
```

### 不啟動模式 (無主控台輸出)

```python
# 停用詳細日誌
agent_with_callback = Agent(
    name="commerce_agent",
    model="gemini-2.5-flash",
    tools=[...],
    after_model=create_grounding_callback(verbose=False)
)
```

## 提取內容

### 1. Grounding Sources

每個來源包括：
```python
{
    "title": "Brooks Divide 5 - Trail Running Shoes",
    "uri": "https://www.decathlon.com.hk/brooks-divide-5",
    "domain": "decathlon.com.hk"
}
```

### 2. 接地支援 (片段歸因)

每個片段顯示哪些來源支持特定聲明：
```python
{
    "text": "Brooks Divide 5 costs €95 and is ideal for beginners",
    "start_index": 45,
    "end_index": 98,
    "source_indices": [0, 2],  # 由索引 0 和 2 的來源支持
    "confidence": "high"  # 2+ 來源 = 高信心
}
```

### 3. 完整的元數據結構

```python
{
    "sources": [...],  # GroundingSource 列表
    "supports": [...],  # GroundingSupport 列表
    "search_suggestions": [...],  # 可選的搜尋建議
    "total_sources": 5  # 總唯一來源數
}
```

## 存取提取的資料

回調將資料儲存在事件狀態中：

```python
async for event in runner.run_async(...):
    if event.is_final_response():
        # 取得來源列表
        sources = event.state.get("temp:_grounding_sources", [])

        # 取得完整元數據
        metadata = event.state.get("temp:_grounding_metadata", {})

        print(f"Found {len(sources)} sources")
        for source in sources:
            print(f"  - [{source['domain']}] {source['title']}")
```

## 主控台輸出範例

當 `verbose=True` (預設值) 時，回調會列印：

```
============================================================
✓ 已提取接地中繼資料
============================================================
總來源數：5

來源：
    1. [decathlon.com.hk] Brooks Divide 5 - Trail Running Shoes
    2. [alltricks.com] Brooks Divide 5 Review
    3. [runningwarehouse.com] Brooks Divide 5 - Men's Trail Running Shoes
    4. [sportsdirect.com] Brooks Running Shoes Collection
    5. [nike.com] Trail Running Shoes Guide

Grounding Support：12 個片段
    1. [high] "Brooks Divide 5 costs €95 and is ideal for beginners" (3 個來源)
    2. [medium] "Comfortable cushioning for mixed terrain" (2 個來源)
    3. [low] "Available in 4 color options" (1 個來源)
    ... 以及其他 9 個
============================================================
```

## 信心水準 (Confidence Levels)

回調基於來源一致性計算信心：

| 來源數量 | 信心 | 意義 |
|---------|-----------|----------|
| 3+ | **high** (高) | 多個來源確認此聲明 |
| 2 | **medium** (中) | 兩個來源一致 |
| 1 | **low** (低) | 僅單一來源 |

## 使用案例

### 1. 除錯搜尋品質

檢查正在使用哪些來源：
```python
callback = GroundingMetadataCallback(verbose=True)
# 查看主控台輸出顯示所有來源
```

### 2. 引用 UI 顯示

向使用者顯示資訊來源：
```python
sources = event.state.get("temp:_grounding_sources", [])
for source in sources:
    print(f"Source: {source['title']}")
    print(f"URL: {source['uri']}")
```

### 3. URL 驗證

透過檢查實際來源防止 URL 幻覺：
```python
metadata = event.state.get("temp:_grounding_metadata", {})
valid_domains = {s['domain'] for s in metadata['sources']}

# 驗證回應中提到的任何 URL 是否來自真實來源
if "decathlon.com" in valid_domains:
    print("✓ Decathlon links are verified")
```

### 4. 品質監控

隨著時間追蹤接地品質：
```python
metadata = event.state.get("temp:_grounding_metadata", {})

# 計算品質分數
high_conf_segments = [s for s in metadata['supports'] if s.get('confidence') == 'high']
quality_score = len(high_conf_segments) / len(metadata['supports'])

print(f"Quality Score: {quality_score:.1%}")
```

## 與測試整合

```python
import pytest
from commerce_agent import root_agent, GroundingMetadataCallback

@pytest.mark.asyncio
async def test_grounding_metadata_extraction():
    """測試接地元數據是否被正確提取。"""
    runner = Runner(
        agent=root_agent,
        callbacks=[GroundingMetadataCallback(verbose=False)]
    )

    # 執行查詢
    async for event in runner.run_async(...):
        if event.is_final_response():
            # 驗證元數據已被提取
            sources = event.state.get("temp:_grounding_sources", [])
            assert len(sources) > 0, "Should extract grounding sources"

            # 驗證來源結構
            for source in sources:
                assert "title" in source
                assert "uri" in source
                assert "domain" in source
```

## 型別安全 (Type Safety)

所有回調型別皆使用 `TypedDict` 定義：

```python
from commerce_agent.types import (
    GroundingMetadata,
    GroundingSource,
    GroundingSupport
)

# 具備 IDE 自動完成的完整型別安全
def process_sources(sources: list[GroundingSource]) -> None:
    for source in sources:
        print(source["title"])  # IDE 知道這存在
        print(source["uri"])    # 自動完成可用
        print(source["domain"]) # 型別檢查
```

## 最佳實踐

1. **開發期間始終使用 verbose=True** 以進行除錯。
2. **生產環境中設定 verbose=False** 以避免日誌洗版。
3. **在最終回應中立即存取元數據** (temp: scope)。
4. **根據接地來源驗證 URL** 以防止幻覺。
5. **監控品質分數** 以追蹤搜尋結果隨時間的品質。
6. **向使用者顯示來源** 以提高透明度和信任。

## 故障排除

### 未提取元數據
- 確保代理人使用 `GoogleSearchTool(bypass_multi_tools_limit=True)`。
- 檢查模型是否為 Gemini 2.0+。
- 驗證查詢是否觸發 Google Search。

### 遺失網域
- 某些 URL 可能無法正確解析。
- 後備網域為 "unknown"。
- 檢查主控台輸出是否有解析問題。

### 支援列表為空
- 某些回應可能沒有片段級別的歸因。
- 對於某些類型的搜尋結果，這是正常的。
- 來源列表仍應被填充。

## 下一步

- 檢閱 `commerce_agent/types.py` 中的 `TypedDict` 定義。
- 檢查 `commerce_agent/callbacks.py` 中的回調實作。
- 執行 `make test` 以查看回調的實際運作。
- 嘗試不同的查詢以查看不同的接地模式。

---
# 重點摘要

- **核心概念**：
    - **接地元數據 (Grounding Metadata)**：從 LLM 回應中提取的來源資訊，用於驗證內容真實性。
    - **回調機制 (Callback Mechanism)**：在模型回應後自動執行程式碼以處理元數據。
    - **信心分數**：根據多個來源的一致性來評估資訊的可信度。

- **關鍵技術**：
    - **ADK Callbacks**：ADK 提供的生命週期掛鉤 (hook)。
    - **Google Search Grounding**：Gemini 模型內建的搜尋增強功能。
    - **TypedDict**：用於確保元數據結構的型別安全。

- **重要結論**：
    - 接地回調是防止幻覺和驗證來源的關鍵工具。
    - 元數據儲存在 `temp:` 狀態中，僅在當前輪次有效。
    - 在開發和生產環境中應使用不同的日誌詳細程度配置。

- **行動項目**：
    - 在所有使用 Google Search 的代理人中整合 `GroundingMetadataCallback`。
    - 使用提取的 URL 進行連結驗證，確保不產生無效連結。
    - 在前端 UI 展示來源歸因，提升使用者信任。

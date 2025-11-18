import os
from typing import Dict, Any, List
from datetime import datetime

from google.adk.agents import Agent
from google.adk.tools import google_search, google_maps_grounding, FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types


def is_vertexai_enabled() -> bool:
    """
    檢查是否透過環境變數啟用 VertexAI。

    Returns:
      如果 GOOGLE_GENAI_USE_VERTEXAI=1 則返回 True,否則返回 False
    """
    # 檢查環境變數是否設定為 "1"
    return os.environ.get("GOOGLE_GENAI_USE_VERTEXAI") == "1"


def get_available_grounding_tools() -> List:
    """
    根據環境配置取得可用的 grounding 工具。

    Returns:
      可用的 grounding 工具列表
    """
    # 預設包含 Google 搜尋工具
    tools = [google_search]  # 始終可用

    # 只有在啟用 VertexAI 時才新增地圖 grounding 功能
    if is_vertexai_enabled():
        tools.append(google_maps_grounding)

    return tools


def get_agent_capabilities_description() -> str:
    """
    根據可用工具取得代理能力的描述。

    Returns:
      描述可用功能的字串
    """
    # 基本能力列表
    capabilities = ["網路搜尋以取得最新資訊"]

    # 如果啟用 VertexAI,新增地圖功能描述
    if is_vertexai_enabled():
        capabilities.append("基於位置的查詢和地圖 grounding")

    # 用 "和" 連接所有能力描述
    return " 和 ".join(capabilities)


# ============================================================================
# 自訂工具
# ============================================================================


def analyze_search_results(
    query: str, search_content: str, tool_context: ToolContext
) -> Dict[str, Any]:
    """
    分析搜尋結果並提取關鍵見解。

    Args:
      query: 原始搜尋查詢
      search_content: 搜尋結果內容
      tool_context: ADK 工具上下文

    Returns:
      包含分析結果的字典
    """
    try:
        # 簡單分析 - 計算字數並提取關鍵詞組
        word_count = len(search_content.split())
        sentences = search_content.split(".")

        # 提取看似關鍵的資訊
        key_insights = []
        # 只取前 5 句話
        for sentence in sentences[:5]:
            sentence = sentence.strip()
            # 只保留有意義的句子(長度大於 20)
            if len(sentence) > 20:
                key_insights.append(sentence)

        # 建立分析報告
        analysis = {
            "query": query,
            "word_count": word_count,
            "key_insights": key_insights[:3],  # 前 3 個關鍵見解
            "content_quality": (
                "good" if word_count > 50 else "limited"
            ),  # 根據字數評估品質
            "timestamp": datetime.now().isoformat(),  # 時間戳記
        }

        return {
            "status": "success",
            "report": f"已分析「{query}」搜尋結果的 {word_count} 個字。找到 {len(key_insights)} 個關鍵見解。",
            "analysis": analysis,
        }

    except Exception as e:
        # 錯誤處理
        return {
            "status": "error",
            "error": str(e),
            "report": f"分析搜尋結果失敗: {str(e)}",
        }


def save_research_findings(
    topic: str, findings: str, tool_context: ToolContext
) -> Dict[str, Any]:
    """
    將研究發現儲存為Artifacts(artifact)。

    Args:
      topic: 研究主題
      findings: 要儲存的研究發現
      tool_context: ADK 工具上下文

    Returns:
      包含儲存結果的字典
    """
    try:
        # 將主題轉換為檔案名稱(空格替換為底線,轉為小寫)
        filename = f"research_{topic.replace(' ', '_').lower()}.md"

        # 注意:在實際實作中,這會儲存到Artifacts服務
        # 為了展示目的,我們只返回成功訊息
        version = "1.0"

        return {
            "status": "success",
            "report": f"研究發現已儲存為 {filename} (版本 {version})",
            "filename": filename,
            "version": version,
        }

    except Exception as e:
        # 錯誤處理
        return {
            "status": "error",
            "error": str(e),
            "report": f"儲存研究發現失敗: {str(e)}",
        }


# ============================================================================
# GROUNDING 代理
# ============================================================================

# 基本 grounding 代理,具有動態工具選擇功能
basic_grounding_agent = Agent(
    name="basic_grounding_agent",  # 代理名稱
    model="gemini-2.0-flash",  # 使用的模型
    description="具有條件式地圖支援的基本網路 grounding 代理",
    instruction=f"""
    你是一個網路研究助手,可以使用 {get_agent_capabilities_description()}。

    回答問題時:
    1. 使用 google_search 尋找最新、準確的資訊
    {"2. 在可用時使用 google_maps_grounding 處理基於位置的查詢" if is_vertexai_enabled() else ""}
    {("3. " if is_vertexai_enabled() else "2. ")}根據搜尋結果提供清晰、事實性的答案
    {("4. " if is_vertexai_enabled() else "3. ")}始終註明資訊來自網路搜尋
    {("5. " if is_vertexai_enabled() else "4. ")}如果資訊似乎過時或不確定,請提及這一點

    保持有幫助、準確,並指出你何時使用搜尋功能。
    """,
    tools=get_available_grounding_tools(),  # 動態載入可用工具
    output_key="grounding_response",  # 輸出鍵值
)

# 進階 grounding 代理 - 展示未來工具混合的模式
advanced_grounding_agent = Agent(
    name="advanced_grounding_agent",
    model="gemini-2.0-flash",
    description="具有搜尋、分析和條件式地圖工具的進階 grounding 代理",
    instruction=f"""
    你是一個進階研究助手,具有 {get_agent_capabilities_description()} 和分析能力。

    執行研究任務時:
    1. 使用 google_search 尋找最新資訊
    {"2. 在可用時使用 google_maps_grounding 進行基於位置的研究" if is_vertexai_enabled() else ""}
    {("3. " if is_vertexai_enabled() else "2. ")}使用 analyze_search_results 處理和總結發現
    {("4. " if is_vertexai_enabled() else "3. ")}使用 save_research_findings 保存重要研究
    {("5. " if is_vertexai_enabled() else "4. ")}提供全面的摘要

    始終保持徹底,引用來源,並解釋你的流程。
  """,
    # 結合 grounding 工具和自訂功能工具
    tools=get_available_grounding_tools()
    + [FunctionTool(analyze_search_results), FunctionTool(save_research_findings)],
    output_key="advanced_research_response",
)

# 研究助手 - 專注於分析能力
# 展示與 grounding 工具配合使用的自訂工具
research_assistant = Agent(
    name="research_assistant",
    model="gemini-2.0-flash",
    description="具有分析、文件記錄和條件式地圖工具的研究助手",
    instruction=f"""
    你是一個專門分析和記錄資訊的研究助手。

    你的能力:
    - **網路研究**: 可使用 {get_agent_capabilities_description()}
    - **分析**: 使用 analyze_search_results 處理和分析內容
    - **文件記錄**: 使用 save_research_findings 保存研究
    {"- **位置研究**: 在可用時使用 google_maps_grounding 處理地理查詢" if is_vertexai_enabled() else ""}

    研究流程:
    1. {"在可用時使用 google_search 和 google_maps_grounding 收集資訊,否則" if is_vertexai_enabled() else ""}使用 analyze_search_results 分析提供的資訊
    2. 將發現綜合成清晰、可行的見解
    3. 使用 save_research_findings 記錄重要研究

    指南:
    - 在分析中保持客觀和事實性
    - 為時效性資訊提供時間戳記
    - 儲存重要發現以供未來參考

    注意: 啟用 VertexAI 時可使用完整的網路搜尋整合。
  """,
    tools=get_available_grounding_tools()
    + [FunctionTool(analyze_search_results), FunctionTool(save_research_findings)],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,  # 較低的溫度以獲得更事實性的研究
        max_output_tokens=2048,  # 最大輸出 token 數
    ),
    output_key="research_response",
)

# 預設代理(由 ADK 網頁介面使用)
# 如果啟用 VertexAI 則使用進階代理(包含地圖 grounding),否則使用基本代理
root_agent = (
    advanced_grounding_agent if is_vertexai_enabled() else basic_grounding_agent
)

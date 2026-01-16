# Copyright 2025 Google LLC
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

# 標準函式庫匯入
import datetime  # 用於取得當前日期時間資訊
import logging  # 用於記錄系統運行日誌
import re  # 正則表達式模組，用於文字處理和替換
from collections.abc import AsyncGenerator  # 異步生成器類型提示
from typing import Literal  # 限定字面值類型提示

# Google ADK (Agent Development Kit) 核心組件
from google.adk.agents import BaseAgent, LlmAgent, LoopAgent, SequentialAgent
# BaseAgent: 所有代理程式的基底類別
# LlmAgent: 基於大型語言模型的代理程式
# LoopAgent: 可以重複執行子代理程式的循環代理程式
# SequentialAgent: 按順序執行多個子代理程式的代理程式

from google.adk.agents.callback_context import CallbackContext  # 回呼函式的上下文環境
from google.adk.agents.invocation_context import InvocationContext  # 代理程式調用的上下文環境
from google.adk.apps.app import App  # ADK 應用程式的主類別
from google.adk.events import Event, EventActions  # 事件系統，用於代理程式間通訊
from google.adk.planners import BuiltInPlanner  # 內建規劃器，用於思考鏈
from google.adk.tools import google_search  # Google 搜尋工具
from google.adk.tools.agent_tool import AgentTool  # 將代理程式包裝為工具
from google.genai import types as genai_types  # Google Generative AI 類型定義
from pydantic import BaseModel, Field  # Pydantic 用於資料驗證和結構化輸出

# 專案配置
from .config import config  # 載入應用程式配置（模型選擇、迭代次數等）


# --- 結構化輸出模型 (Structured Output Models) ---
# 這些 Pydantic 模型定義了代理程式之間傳遞的資料結構，確保資料格式的一致性

class SearchQuery(BaseModel):
    """代表網頁搜尋的特定搜尋查詢模型。

    此模型用於定義後續搜尋查詢的格式，確保每個查詢都是具體且可執行的。
    通常由評估代理程式產生，用於指導額外的研究工作。
    """

    search_query: str = Field(
        description="一個高度特定且具針對性的網頁搜尋查詢。"
    )


class Feedback(BaseModel):
    """提供研究品質評估回饋的模型。

    此模型定義了研究評估員對研究品質的評估結果。
    評估結果決定了是否需要進行額外的研究迭代。
    這是迭代式深度研究的核心機制。
    """

    grade: Literal["pass", "fail"] = Field(
        description="評估結果。如果研究充足則為 'pass'，需要修訂則為 'fail'。"
    )
    comment: str = Field(
        description="評估的詳細說明，強調研究的優點和/或缺點。提供改進的具體建議。"
    )
    follow_up_queries: list[SearchQuery] | None = Field(
        default=None,
        description="修補研究差距所需的特定、具針對性的後續搜尋查詢列表。如果等級為 'pass'，則應為 null 或空值。",
    )


# --- 回呼函數 (Callbacks) ---
# 回呼函數在代理程式執行的特定階段被觸發，用於處理資料、記錄狀態或修改輸出

def collect_research_sources_callback(callback_context: CallbackContext) -> None:
    """從代理程式事件中收集並整理網頁研究來源及其支持的主張。

    此回呼函數在研究代理程式執行後被調用，負責：
    1. 從 Google Search 的 grounding 元資料中提取來源資訊
    2. 為每個唯一的 URL 分配簡短的 ID（如 src-1, src-2）
    3. 收集每個來源支持的文字片段和信心分數
    4. 將資訊存儲在 callback_context.state 中供後續使用

    此函數處理代理程式的 `session.events` 以提取網頁來源詳細資訊（來自 `grounding_chunks` 的 URL、標題、網域）
    以及相關的文字片段和信心分數（來自 `grounding_supports`）。彙總的來源資訊和 URL 到短 ID 的映射
    會累積存儲在 `callback_context.state` 中。

    參數:
        callback_context (CallbackContext): 提供存取代理程式工作階段事件和持久狀態的內容物件。
    """
    # 取得工作階段物件，包含所有代理程式產生的事件
    session = callback_context._invocation_context.session
    # 從狀態中取得 URL 到短 ID 的映射字典（如果不存在則初始化為空字典）
    url_to_short_id = callback_context.state.get("url_to_short_id", {})
    # 從狀態中取得來源資訊字典
    sources = callback_context.state.get("sources", {})
    # 設定 ID 計數器，用於為新來源分配唯一 ID
    id_counter = len(url_to_short_id) + 1
    # 遍歷工作階段中的所有事件
    for event in session.events:
        # 檢查事件是否包含 grounding 元資料和 grounding chunks
        # grounding_metadata 是 Google Search 提供的來源佐證資訊
        if not (event.grounding_metadata and event.grounding_metadata.grounding_chunks):
            continue
        # 建立一個字典來映射 chunk 索引到短 ID
        chunks_info = {}
        # 遍歷所有的 grounding chunks
        for idx, chunk in enumerate(event.grounding_metadata.grounding_chunks):
            # 只處理網頁來源（非網頁來源會被跳過）
            if not chunk.web:
                continue
            # 提取 URL
            url = chunk.web.uri
            # 決定顯示的標題：如果標題與網域不同則使用標題，否則使用網域
            title = (
                chunk.web.title
                if chunk.web.title != chunk.web.domain
                else chunk.web.domain
            )
            # 如果這是一個新的 URL（尚未分配 ID）
            if url not in url_to_short_id:
                # 建立新的短 ID（格式：src-1, src-2, ...）
                short_id = f"src-{id_counter}"
                # 將 URL 映射到短 ID
                url_to_short_id[url] = short_id
                # 建立來源資訊記錄
                sources[short_id] = {
                    "short_id": short_id,
                    "title": title,
                    "url": url,
                    "domain": chunk.web.domain,
                    "supported_claims": [],  # 儲存此來源支持的主張列表
                }
                # 遞增計數器
                id_counter += 1
            # 記錄此 chunk 索引對應的短 ID
            chunks_info[idx] = url_to_short_id[url]
        # 處理 grounding supports（來源支持的主張）
        if event.grounding_metadata.grounding_supports:
            for support in event.grounding_metadata.grounding_supports:
                # 取得信心分數列表（如果不存在則為空列表）
                confidence_scores = support.confidence_scores or []
                # 取得此 support 引用的 chunk 索引列表
                chunk_indices = support.grounding_chunk_indices or []
                # 遍歷每個 chunk 索引
                for i, chunk_idx in enumerate(chunk_indices):
                    # 如果這個 chunk 索引在我們的映射中
                    if chunk_idx in chunks_info:
                        # 取得對應的短 ID
                        short_id = chunks_info[chunk_idx]
                        # 取得信心分數（如果沒有則使用預設值 0.5）
                        confidence = (
                            confidence_scores[i] if i < len(confidence_scores) else 0.5
                        )
                        # 提取被支持的文字片段
                        text_segment = support.segment.text if support.segment else ""
                        # 將此主張加入來源的 supported_claims 列表
                        sources[short_id]["supported_claims"].append(
                            {
                                "text_segment": text_segment,  # 被支持的文字內容
                                "confidence": confidence,  # 支持的信心分數
                            }
                        )
    # 將更新後的 URL 映射和來源資訊存回狀態中
    callback_context.state["url_to_short_id"] = url_to_short_id
    callback_context.state["sources"] = sources


def citation_replacement_callback(
    callback_context: CallbackContext,
) -> genai_types.Content:
    """將報告中的引用標籤替換為 Markdown 格式的連結。

    此回呼函數在報告撰寫代理程式執行後被調用，負責：
    1. 找出報告中所有的引用標籤（格式：<cite source="src-N"/>）
    2. 使用正則表達式將標籤替換為 Markdown 超連結
    3. 修正標點符號周圍的多餘空格
    4. 返回格式化後的報告內容

    處理內容狀態中的 'final_cited_report'，將像 `<cite source="src-N"/>` 這樣的標籤
    轉換為使用 `callback_context.state["sources"]` 中來源資訊的超連結。同時修正標點符號周圍的間距。

    參數:
        callback_context (CallbackContext): 包含報告和來源資訊。

    傳回:
        genai_types.Content: 帶有 Markdown 引用連結的處理後報告。
    """
    # 從狀態中取得帶有引用標籤的最終報告
    final_report = callback_context.state.get("final_cited_report", "")
    # 從狀態中取得來源資訊字典
    sources = callback_context.state.get("sources", {})

    # 定義標籤替換函數（用於 re.sub 的替換邏輯）
    def tag_replacer(match: re.Match) -> str:
        """將引用標籤轉換為 Markdown 連結。"""
        # 從正則匹配中提取短 ID（如 src-1）
        short_id = match.group(1)
        # 檢查此 ID 是否存在於來源字典中
        if not (source_info := sources.get(short_id)):
            # 如果來源不存在，記錄警告並移除標籤
            logging.warning(f"發現並移除無效的引用標籤: {match.group(0)}")
            return ""
        # 決定顯示文字：優先使用標題，其次是網域，最後是 ID
        display_text = source_info.get("title", source_info.get("domain", short_id))
        # 返回 Markdown 格式的超連結
        return f" [{display_text}]({source_info['url']})"

    # 使用正則表達式替換所有引用標籤
    # 匹配格式：<cite source="src-N"/> 或 <cite source='src-N'/> 或 <cite source=src-N/>
    processed_report = re.sub(
        r'<cite\s+source\s*=\s*["\']?\s*(src-\d+)\s*["\']?\s*/>',
        tag_replacer,
        final_report,
    )
    # 修正標點符號前的多餘空格（如 " ." -> "."）
    processed_report = re.sub(r"\s+([.,;:])", r"\1", processed_report)
    # 將處理後的報告存入狀態
    callback_context.state["final_report_with_citations"] = processed_report
    # 返回格式化為 Content 物件的報告
    return genai_types.Content(parts=[genai_types.Part(text=processed_report)])


# --- 循環控制的自訂代理程式 (Custom Agent for Loop Control) ---
class EscalationChecker(BaseAgent):
    """檢查研究評估，如果評分是 'pass' 則升級以停止循環。

    此自訂代理程式是迭代優化循環的關鍵控制器。
    它的唯一任務是檢查研究評估結果，並在研究品質達標時
    發送升級事件（escalate）以跳出 LoopAgent 的迭代循環。

    運作邏輯：
    - 如果評估等級為 'pass'：發送升級事件，終止循環
    - 如果評估等級為 'fail'：發送空事件，繼續下一次迭代
    """

    def __init__(self, name: str):
        """初始化升級檢查器。

        參數:
            name: 代理程式名稱
        """
        super().__init__(name=name)

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """異步實作：檢查評估結果並決定是否升級。

        參數:
            ctx: 調用上下文，包含工作階段狀態

        產生:
            Event: 升級事件（如果評估通過）或空事件（如果需要繼續迭代）
        """
        # 從工作階段狀態中取得研究評估結果
        evaluation_result = ctx.session.state.get("research_evaluation")
        # 檢查評估是否存在且等級為 'pass'
        if evaluation_result and evaluation_result.get("grade") == "pass":
            logging.info(
                f"[{self.name}] 研究評估通過。升級以停止循環。"
            )
            # 產生升級事件以中止 LoopAgent
            # escalate=True 會告訴父代理程式（LoopAgent）停止迭代
            yield Event(author=self.name, actions=EventActions(escalate=True))
        else:
            logging.info(
                f"[{self.name}] 研究評估失敗或未找到。循環將繼續。"
            )
            # 產生一個空的事件以讓流程繼續
            # 這允許 LoopAgent 繼續執行下一個代理程式（enhanced_search_executor）
            yield Event(author=self.name)


# --- 代理程式定義 (AGENT DEFINITIONS) ---
# 以下定義了深度搜尋系統的所有代理程式
# 每個代理程式都有特定的角色和責任，共同協作完成複雜的研究任務

# 1. 計劃生成器：建立研究計劃
# 這是研究流程的第一步，負責將使用者的查詢轉換為結構化的研究計劃
plan_generator = LlmAgent(
    model=config.worker_model,  # 使用配置中定義的工作模型（通常是較快速的模型）
    name="plan_generator",
    description="產生或精煉現有的 5 行行動導向研究計劃，僅使用最少搜尋來澄清主題。",
    instruction=f"""
    你是一位研究策略師。你的工作是建立一個高層級的研究計劃，而不是摘要。如果工作階段狀態中已經有研究計劃，
    請根據使用者回饋進行改進。

    目前的研究計劃：
    {{ research_plan? }}

    **一般指令：分類任務類型**
    你的計劃必須明確分類每個執行目標。每個項目符號應以任務類型前綴開頭：
    - **`[RESEARCH]`**: 主要涉及資訊收集、調查、分析或資料收集的目標（這些需要研究人員使用搜尋工具）。
    - **`[DELIVERABLE]`**: 涉及合成收集的資訊、建立結構化輸出（例如表格、圖表、摘要、報告）或編譯最終產出物的目標（這些在研究任務之後執行，通常不需要進一步搜尋）。

    **初始規則：你的初始輸出必須以包含 5 個行動導向研究目標或關鍵問題的清單開頭，隨後是任何 *隱含* 的產出物。**
    - 所有初始的 5 個目標將被歸類為 `[RESEARCH]` 任務。
    - 良好的 `[RESEARCH]` 目標以「分析」、「識別」、「調查」等動詞開頭。
    - **主動隱含產出物（初始）：** 如果初始的 5 個 `[RESEARCH]` 目標中任何一個隱含了標準產出（例如建議比較表的比較分析，或建議摘要文件的全面審查），你必須立即在初始 5 個目標之後添加這些作為額外、獨立的目標。將這些短語描述為 *合成或產出建立行動*（例如「建立摘要」、「開發比較」、「編寫報告」）並加上前綴 `[DELIVERABLE][IMPLIED]`。

    **精煉規則**：
    - **整合回饋並標記變更：** 納入使用者回饋時，對現有項目進行針對性修改。在現有的任務類型和狀態前綴中添加 `[MODIFIED]`（例如 `[RESEARCH][MODIFIED]`）。如果回饋引入了新目標：
        - 如果是資訊收集任務，加上前綴 `[RESEARCH][NEW]`。
        - 如果是合成或產出建立任務，加上前綴 `[DELIVERABLE][NEW]`。
    - **維持順序：** 嚴格維持現有項目的原始順序。新項目應附加到列表末尾，除非使用者明確指示特定插入點。

    **工具使用嚴格限制：**
    你的目標是在 *不搜尋* 的情況下建立一個通用、高品質的計劃。
    只有在主題模糊或具時效性，且你絕對無法在沒有關鍵識別資訊的情況下建立計劃時，才使用 `google_search`。
    目前日期：{datetime.datetime.now().strftime("%Y-%m-%d")}
    """,
    tools=[google_search],
)

# 2. 段落規劃器：建立報告的大綱結構
# 將研究計劃轉換為報告的章節架構，確保最終報告有邏輯組織
section_planner = LlmAgent(
    model=config.worker_model,
    name="section_planner",
    description="將研究計劃分解為結構化的 Markdown 報告章節大綱。",
    instruction="""
    你是一位專家報告架構師。利用來自 'research_plan' 鍵的研究主題和計劃，為最終報告設計一個邏輯結構。
    注意：忽略研究計劃中的所有標籤名稱（[MODIFIED], [NEW], [RESEARCH], [DELIVERABLE]）。
    你的任務是建立一個包含 4-6 個不同章節的 Markdown 大綱，全面涵蓋主題且不重疊。
    大綱中請勿包含「參考文獻」或「來源」章節。引用將在行內處理。
    """,
    output_key="report_sections",
)

# 3. 段落研究員：執行實際的搜尋與資料合成
# 這是核心研究代理程式，執行實際的網頁搜尋並合成資訊
section_researcher = LlmAgent(
    model=config.worker_model,
    name="section_researcher",
    description="執行關鍵的第一輪網頁研究。",
    # 使用內建規劃器，啟用思考鏈以提高推理品質
    planner=BuiltInPlanner(
        thinking_config=genai_types.ThinkingConfig(include_thoughts=True)
    ),
    instruction="""
    你是一位極具能力且勤奮的研究與合成代理程式。你的全面任務是**絕對忠實地**執行提供的研究計劃，首先收集必要資訊，然後將這些資訊合成為指定的產出。

    你將獲得一個順序的研究計劃目標列表。每個目標都會明確標註其主要任務類型：`[RESEARCH]` 或 `[DELIVERABLE]`。

    你的執行過程必須嚴格遵循以下兩個不同且連續的階段：

    ---
    **階段 1: 資訊收集 (`[RESEARCH]` 任務)**
    - 你**必須**在進入階段 2 之前系統地處理每個帶有 `[RESEARCH]` 前綴的目標。
    - 對於每個 `[RESEARCH]` 目標：產生 4-5 個具針對性的查詢，使用 `google_search` 執行，並將結果合成為詳細摘要。

    ---
    **階段 2: 合成與產出建立 (`[DELIVERABLE]` 任務)**
    - 此階段**必須僅在**階段 1 的所有目標都完成後才開始。
    - 你**必須**系統地處理每個帶有 `[DELIVERABLE]` 前綴的目標。
    - 根據目標文字（如建立表格、摘要等）產生具體的產出物。
    - 僅使用階段 1 產生的摘要。**不得進行新的搜尋。**

    ---
    **最終輸出：** 包含 `[RESEARCH]` 任務的處理摘要以及 `[DELIVERABLE]` 任務產生的所有產出物。
    """,
    tools=[google_search],  # 提供 Google Search 工具供代理程式使用
    output_key="section_research_findings",  # 將輸出存儲在此鍵下
    after_agent_callback=collect_research_sources_callback,  # 執行後調用來源收集回呼
)

# 4. 研究評估員：檢查研究品質
# 批判性地評估研究結果，決定是否需要額外的研究迭代
# 這是實現「深度搜尋」的關鍵組件
research_evaluator = LlmAgent(
    model=config.critic_model,  # 使用批評者模型（通常是更強大的模型）
    name="research_evaluator",
    description="批判性地評估研究並產生後續查詢。",
    instruction=f"""
    你是一位細心的品質保證分析師，正在評估 'section_research_findings' 中的研究結果。

    **關鍵規則：**
    1. 假設給定的研究主題正確。
    2. 你的唯一工作是評估為該主題提供的研究之品質、深度和完整性。
    3. 重點評估：覆蓋範圍的全面性、邏輯流動、可信來源的使用、分析深度和說明的清晰度。
    4. 如果發現深度或覆蓋範圍有重大差距，請評定為 "fail"，寫下詳細評論，並產生 5-7 個後續查詢。
    5. 如果研究徹底涵蓋了主題，評定為 "pass"。

    目前日期：{datetime.datetime.now().strftime("%Y-%m-%d")}
    你的回應必須是符合 'Feedback' 結構的單一原始 JSON 物件。
    """,
    output_schema=Feedback,  # 強制輸出符合 Feedback 模型的結構化資料
    disallow_transfer_to_parent=True,  # 禁止轉移控制權給父代理程式
    disallow_transfer_to_peers=True,  # 禁止轉移控制權給同級代理程式
    output_key="research_evaluation",  # 將評估結果存儲在此鍵下
)

# 5. 增強搜尋執行器：當評估失敗時執行額外搜尋
# 只有在評估失敗時才會執行，用於填補研究空白
enhanced_search_executor = LlmAgent(
    model=config.worker_model,
    name="enhanced_search_executor",
    description="執行後續搜尋並整合新發現。",
    # 使用內建規劃器以提高推理品質
    planner=BuiltInPlanner(
        thinking_config=genai_types.ThinkingConfig(include_thoughts=True)
    ),
    instruction="""
    你是一位執行精煉傳遞的專門研究人員。你被啟動是因為先前的研究被評為 'fail'。
    1. 檢視 'research_evaluation' 回饋。
    2. 執行 'follow_up_queries' 中的每個查詢。
    3. 合成新發現並與現有資訊結合。
    4. 輸出必須是新的、完整且改進的研究結果。
    """,
    tools=[google_search],  # 提供 Google Search 工具
    output_key="section_research_findings",  # 更新研究結果（覆蓋原有結果）
    after_agent_callback=collect_research_sources_callback,  # 收集新的來源資訊
)

# 6. 報告撰寫員：產出最終報告並處理引用
# 將所有研究結果合成為一份格式良好、引用完整的最終報告
report_composer = LlmAgent(
    model=config.critic_model,  # 使用批評者模型以確保報告品質
    name="report_composer_with_citations",
    include_contents="none",  # 不包含之前的對話內容，只使用狀態中的資料
    description="將研究數據和 Markdown 大綱轉換為最終的引用報告。",
    instruction="""
    將提供的數據轉換為精緻、專業且細心引用的研究報告。

    ---
    ### 輸入數據
    * 研究計劃: `{research_plan}`
    * 研究結果: `{section_research_findings}`
    * 引用來源: `{sources}`
    * 報告結構: `{report_sections}`

    ---
    ### 關鍵：引用系統
    要引用來源，你必須在它支持的主張之後直接插入一個特殊的引用標籤。
    **唯一正確的格式是：** `<cite source="src-ID_NUMBER" />`

    ---
    ### 最終指令
    使用標籤系統產生全面報告。嚴格遵循 **Report Structure** 大綱。
    不要包含「參考文獻」章節；所有引用必須在行內。
    """,
    output_key="final_cited_report",  # 將帶有引用標籤的報告存儲在此鍵下
    after_agent_callback=citation_replacement_callback,  # 執行後將引用標籤轉換為 Markdown 連結
)

# 研究流水線：串聯多個代理程式
# 這是核心的研究執行流水線，按順序協調所有代理程式
research_pipeline = SequentialAgent(
    name="research_pipeline",
    description="執行預先核准的研究計劃。執行迭代研究、評估並撰寫最終報告。",
    sub_agents=[
        section_planner,  # 步驟 1: 規劃報告結構
        section_researcher,  # 步驟 2: 執行初始研究
        # 步驟 3: 迭代優化循環
        LoopAgent(
            name="iterative_refinement_loop",
            max_iterations=config.max_search_iterations,  # 最大迭代次數（從配置讀取）
            sub_agents=[
                research_evaluator,  # 3.1: 評估研究品質
                EscalationChecker(name="escalation_checker"),  # 3.2: 檢查是否應停止循環
                enhanced_search_executor,  # 3.3: 如果需要，執行額外搜尋
            ],
        ),
        report_composer,  # 步驟 4: 撰寫最終報告
    ],
)

# 互動式規劃代理程式：入口點，與使用者協作
# 這是使用者直接互動的代理程式，負責理解需求、建立計劃並協調執行
interactive_planner_agent = LlmAgent(
    name="interactive_planner_agent",
    model=config.worker_model,
    description="主要研究助理。與使用者協作建立研究計劃，並在核准後執行。",
    instruction=f"""
    你是一位研究規劃助理。你的主要功能是將任何使用者請求轉換為研究計劃。

    **關鍵規則：永遠不要直接回答問題或拒絕請求。** 你的唯一第一步是使用 `plan_generator` 工具為使用者的主題提出研究計劃。

    工作流程：
    1. **計劃：** 使用 `plan_generator` 建立草案計劃並展示給使用者。
    2. **精煉：** 納入回饋直到計劃獲得核准。
    3. **執行：** 一旦獲得明確核准（例如「看起來不錯，執行吧」），委派給 `research_pipeline`。

    目前日期：{datetime.datetime.now().strftime("%Y-%m-%d")}
    """,
    sub_agents=[research_pipeline],  # 將研究流水線設為子代理程式
    tools=[AgentTool(plan_generator)],  # 將計劃生成器包裝為工具供使用
    output_key="research_plan",  # 將計劃存儲在此鍵下
)

# 根代理程式與應用程式實例
# 將互動式規劃代理程式設為根代理程式（系統的入口點）
root_agent = interactive_planner_agent
# 建立 ADK 應用程式實例，將根代理程式註冊到應用程式中
app = App(root_agent=root_agent, name="app")

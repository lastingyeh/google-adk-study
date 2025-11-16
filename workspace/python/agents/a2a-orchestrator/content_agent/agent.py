"""
內容創作代理 - 官方 ADK A2A 實作

此代理專門從事內容創作、寫作與格式化。
它被設計為一個獨立的 A2A (Agent-to-Agent) 伺服器，
可由協調器代理或其他代理透過 API 呼叫來使用。

將透過以下指令提供服務：uvicorn content_agent.agent:a2a_app --host localhost --port 8003

### 程式碼流程註解

#### 核心功能
本腳本定義了一個名為 `content_writer` 的特化代理，其主要職責是根據給定的主題、
類型和細節來創作和格式化書面內容。

#### 運作流程
1.  **工具定義**：定義了兩個核心工具：
    - `create_content`：此函式接收內容類型 (例如 "summary", "article", "report")、主題和可選的細節。根據內容類型，它會回傳一個預先定義好的、結構化的內容模板，並填入主題和細節。這模擬了內容創作者根據不同需求產出不同格式文件的過程。
    - `format_content`：此函式接收一段原始文字內容和一個格式類型 (例如 "markdown", "html")，然後將內容包裝在相應的格式標籤中。
2.  **代理設定**：
    - `root_agent` (內容代理) 被設定為使用 `gemini-2.0-flash` 模型。
    - `instruction` 參數指導代理如何扮演一個內容創作專家。與分析代理類似，它也被指示在 A2A 情境下要專注於核心的內容創作任務，忽略協調器的內部運作細節。
    - `tools` 參數將 `create_content` 和 `format_content` 函式註冊為代理可用的工具。
    - `temperature` 設為 0.7，以鼓勵模型在內容創作上更具創造性。
3.  **A2A 伺服器建立**：
    - `to_a2a(root_agent, port=8003)`：同樣地，此函式將 `root_agent` 轉換為一個符合 A2A 通訊協定的 FastAPI 應用程式 (`a2a_app`)。
    - 當使用 `uvicorn` 運行此腳本時，它會在 `localhost:8003` 上啟動一個伺服器，等待來自協調器的內容創作請求。

### Mermaid 流程圖

```mermaid
graph TD
    subgraph "內容代理 (localhost:8003)"
        A[uvicorn 伺服器] --> B{a2a_app};
        B --> C[root_agent: content_writer];
        C --> D[工具: create_content];
        C --> E[工具: format_content];
    end

    subgraph "協調器"
        F[協調器代理]
    end

    F -- HTTP POST --> A;
    A -- 回應 --> F;
```
"""

# 匯入 ADK 核心模組
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.genai import types
from google.adk.a2a.utils.agent_to_a2a import to_a2a


def create_content(content_type: str, topic: str, details: str = "") -> dict:
    """
    根據指定的類型與主題創作各種類型的內容。

    這是一個模擬函式，根據輸入的內容類型回傳預先定義的內容模板。
    在真實應用中，這裡可以連接到更複雜的內容生成模型或模板引擎。

    Args:
        content_type: 要創作的內容類型（文章、摘要、報告等）。
        topic: 內容的主要主題或主旨。
        details: (可選) 額外的細節或要求，將被整合到內容中。

    Returns:
        一個包含已創作內容與元資料的字典。
    """
    content_type_lower = content_type.lower()

    # 根據內容類型回傳不同的模板化內容
    if "summary" in content_type_lower:
        return {
            "status": "success",
            "content_type": content_type,
            "topic": topic,
            "content": {
                "title": f"執行摘要：{topic}",
                "summary": f"""
                    ## 執行摘要

                    **主題：** {topic}

                    **關鍵要點：**
                    - 全面分析揭示了重大的機會與挑戰
                    - 當前市場趨勢顯示強勁的增長潛力
                    - 策略性實施需要仔細的規劃與執行

                    **主要發現：**
                    {details if details else "根據現有的研究與分析，該主題顯示出有前景的發展，並有明確的增長與實施途徑。"}

                    **建議：**
                    - 制定符合市場趨勢的全面策略
                    - 分配資源以進行適當的實施
                    - 監控進度並視需要調整方法

                    **結論：**
                    分析支持一個積極的前景，風險可控且有重大的成功機會。
                """.strip(),
                "word_count": 150,
                "reading_time": "1 分鐘"
            },
            "metadata": {
                "format": "executive_summary",
                "audience": "決策者",
                "tone": "專業"
            }
        }

    elif "article" in content_type_lower:
        return {
            "status": "success",
            "content_type": content_type,
            "topic": topic,
            "content": {
                "title": f"理解 {topic}：全面分析",
                "article": f"""

                    # 理解 {topic}：全面分析

                    ## 前言

                    {topic} 代表了一個具有深遠影響的重要領域，橫跨多個行業。本文旨在檢視當前的格局、關鍵發展與未來前景。

                    ## 當前格局

                    近年來，{topic} 領域經歷了顯著的增長與創新。主要利益相關者正在大量投資於研發，從而帶來了突破性的發現與實際應用。

                    ## 關鍵發展

                    {topic} 的近期發展包括：
                    - 先進的技術創新
                    - 市場採用與接受度提高
                    - 監管框架與政策發展
                    - 策略性合作夥伴關係與協作

                    ## 分析與洞察

                    {details if details else "我們的分析顯示，在技術進步與市場需求不斷增長的推動下，該行業已為持續增長做好準備。"}

                    ## 未來前景

                    展望未來，{topic} 預計將：
                    - 繼續擴展至各種應用
                    - 推動相關領域的創新
                    - 為企業與研究人員創造新機會
                    - 面對需要策略性解決方案的挑戰

                    ## 結論

                    {topic} 代表了一個充滿活力且不斷發展的領域，具有巨大的影響潛力。能夠進行策略性定位的利益相關者將能從未來的發展中獲益。
                """.strip(),
                "word_count": 350,
                "reading_time": "3 分鐘"
            },
            "metadata": {
                "format": "feature_article",
                "audience": "一般專業人士",
                "tone": "資訊性"
            }
        }

    elif "report" in content_type_lower:
        return {
            "status": "success",
            "content_type": content_type,
            "topic": topic,
            "content": {
                "title": f"技術報告：{topic}",
                "report": f"""

                    # 技術報告：{topic}

                    ## 執行摘要
                    本報告對 {topic} 進行了全面分析，包括現狀、主要發現與策略性建議。

                    ## 方法論
                    透過多來源分析進行研究，包括：
                    - 行業報告與市場數據
                    - 學術研究與出版物
                    - 專家訪談與利益相關者意見
                    - 量化與質化分析

                    ## 主要發現
                    1. **市場地位**：強勁的增長軌跡與不斷擴展的應用
                    2. **技術狀況**：成熟的基礎與新興的創新
                    3. **採用趨勢**：在目標市場中的接受度日益提高
                    4. **競爭格局**：活躍的競爭推動創新

                    ## 詳細分析
                    {details if details else "分析揭示了重大的機會與可控的挑戰。策略性定位與執行對於成功至關重要。"}

                    ## 建議
                    - **短期**：專注於眼前的實施機會
                    - **中期**：建立策略性能力與合作夥伴關係
                    - **長期**：為新興趨勢與技術做好定位

                    ## 風險評估
                    - **低風險**：穩固的市場需求
                    - **中風險**：技術採用的挑戰
                    - **高風險**：競爭壓力與市場飽和

                    ## 結論
                    {topic} 提供了一個引人注目的機會，並有明確的成功實施與增長途徑。
                """.strip(),
                "word_count": 450,
                "reading_time": "4 分鐘"
            },
            "metadata": {
                "format": "technical_report",
                "audience": "技術專業人士",
                "tone": "分析性"
            }
        }
    else:
        # 如果內容類型不匹配，提供一個通用的內容模板
        return {
            "status": "success",
            "content_type": "general_content",
            "topic": topic,
            "content": {
                "title": topic,
                "text": f"""
                    關於 {topic} 的內容：

                    {details if details else f"這是涵蓋 {topic} 各個方面的綜合內容。該材料為有興趣了解此主題的讀者提供了寶貴的洞察與資訊。"}

                    內容涵蓋了背景資訊、當前發展以及對利益相關者的實際影響等關鍵方面。
                """.strip(),
                "word_count": 100,
                "reading_time": "1 分鐘"
            },
            "metadata": {
                "format": "general",
                "audience": "一般大眾",
                "tone": "中性"
            }
        }


def format_content(raw_content: str, format_type: str) -> dict:
    """
    將現有內容格式化為特定的格式或樣式。

    Args:
        raw_content: 要格式化的原始內容字串。
        format_type: 所需的格式（例如 "markdown"、"html"、"plain"）。

    Returns:
        一個包含格式化後內容的字典。
    """
    format_lower = format_type.lower()

    if "markdown" in format_lower:
        formatted = f"""
            # 格式化內容

            {raw_content}

            ---
            *以 Markdown 格式化，便於閱讀與發布。*
        """.strip()
    elif "html" in format_lower:
        formatted = f"""
            <article>
                <h1>格式化內容</h1>
                <div class="content">
                    {raw_content.replace('\\n', '<br>\\n')}
                </div>
                <footer><em>以 HTML 格式化，用於網頁發布。</em></footer>
            </article>
        """.strip()
    else:
        # 預設為純文字格式
        formatted = f"""
            格式化內容
            {'-' * 50}

            {raw_content}

            {'-' * 50}
            以純文字格式化，以實現通用相容性。
        """.strip()

    return {
        "status": "success",
        "original_length": len(raw_content),
        "formatted_content": formatted,
        "format": format_type,
        "optimized_for": "可讀性與發布"
    }


# --- 主要內容代理 ---
# 這是將透過 A2A 協定提供服務的主要內容代理實例。
root_agent = Agent(
    model="gemini-2.0-flash",
    name="content_writer",
    description="創作書面內容與摘要",
    instruction="""
        您是一位專注於製作高品質書面材料的內容創作專家。

        **重要 - A2A 情境處理：**
        當透過代理對代理（A2A）協定接收請求時，您的主要任務是專注於核心使用者請求。
        請忽略情境中任何提及協調器工具呼叫的內容，例如 "transfer_to_agent" 或其他協調細節。
        您的目標是從對話中提取主要的內容創作任務並直接完成它。

        **您的能力：**
        - 創作各種類型的內容（文章、摘要、報告）。
        - 針對不同媒介與受眾格式化內容。
        - 根據要求調整語氣與風格。
        - 優化內容以提高清晰度與參與度。

        **內容創作流程：**
        1. 識別核心內容請求（例如，「撰寫一份關於 AI 的報告」）。
        2. 使用 `create_content` 工具根據請求生成新材料。
        3. 如有需要，使用 `format_content` 工具進行樣式設定與呈現。
        4. 針對特定受眾與目的量身定制內容。
        5. 確保清晰、準確與專業的品質。

        **透過 A2A 工作時：**
        - 專注於使用者的實際內容請求。
        - 忽略協調器機制與情境中的工具呼叫。
        - 提供直接、有幫助的內容創作服務。
        - 如果請求不明確，請要求澄清內容類型與主題。

        務必考慮目標受眾與內容的預期用途。
        提供結構良好、組織有序且格式適當的材料。
    """,
    # 將上面定義的函式註冊為代理可用的工具
    tools=[
        FunctionTool(create_content),
        FunctionTool(format_content)
    ],
    # 設定內容生成參數
    generate_content_config=types.GenerateContentConfig(
        temperature=0.7,  # 為內容生成設定較高的溫度，以鼓勵更多創造性
        max_output_tokens=2000
    )
)

# 使用官方 ADK to_a2a() 函式將 Agent 轉換為一個 A2A FastAPI 應用程式。
a2a_app = to_a2a(root_agent, port=8003)

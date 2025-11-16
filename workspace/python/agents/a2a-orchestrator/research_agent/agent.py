"""
研究代理 - 官方 ADK A2A 實作

此代理專門從事網路研究、事實查核與資訊收集。
它被設計為一個獨立的 A2A (Agent-to-Agent) 伺服器，
可由協調器代理或其他代理透過 API 呼叫來使用。

將透過以下指令提供服務：uvicorn research_agent.agent:a2a_app --host localhost --port 8001

### 程式碼流程註解

#### 核心功能
本腳本定義了一個名為 `research_specialist` 的特化代理，其主要職責是根據給定的主題進行研究，
並對特定的聲明進行事實查核。

#### 運作流程
1.  **工具定義**：定義了兩個核心工具：
    - `research_topic`：此函式接收一個研究主題，並根據內容中的關鍵字 (例如 "quantum", "ai") 回傳一個模擬的、結構化的研究報告。報告包含總覽、趨勢、關鍵發展、挑戰、來源和信心水準。如果沒有匹配的關鍵字，則提供一個通用的研究模板。
    - `fact_check`：此函式接收一個聲明，並回傳一個模擬的事實查核結果，包括準確性評估、方法論和建議。
2.  **代理設定**：
    - `root_agent` (研究代理) 被設定為使用 `gemini-2.0-flash` 模型。
    - `instruction` 參數指導代理如何扮演一個研究專家。它同樣被指示在 A2A 情境下要專注於核心的研究任務，忽略協調器的內部運作細節。
    - `tools` 參數將 `research_topic` 和 `fact_check` 函式註冊為代理可用的工具。
    - `temperature` 設為 0.3，以確保研究結果更具一致性和事實性。
3.  **A2A 伺服器建立**：
    - `to_a2a(root_agent, port=8001)`：此 ADK 函式將 `root_agent` 轉換為一個符合 A2A 通訊協定的 FastAPI 應用程式 (`a2a_app`)。
    - 當使用 `uvicorn` 運行此腳本時，它會在 `localhost:8001` 上啟動一個伺服器，等待來自協調器的研究請求。

### Mermaid 流程圖

```mermaid
graph TD
    subgraph "研究代理 (localhost:8001)"
        A[uvicorn 伺服器] --> B{a2a_app};
        B --> C[root_agent: research_specialist];
        C --> D[工具: research_topic];
        C --> E[工具: fact_check];
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


def research_topic(topic: str) -> dict:
    """
    研究特定主題並提供詳細的發現。

    這是一個模擬函式，根據輸入的主題回傳預先定義的研究結果。
    在真實應用中，這裡可以連接到網路搜尋 API、資料庫或其他資訊來源。

    Args:
        topic: 要研究的主題。

    Returns:
        一個包含研究發現、來源與分析的字典。
    """
    # 模擬全面的研究過程
    topic_lower = topic.lower()

    # 針對特定關鍵字提供模擬的研究結果
    if "quantum" in topic_lower:
        return {
            "status": "success",
            "topic": topic,
            "findings": {
                "overview": "量子計算代表了計算能力的典範轉移，有望解決傳統電腦無法處理的複雜問題。",
                "current_trends": [
                    "主要科技公司 (如 Google, IBM) 擁有可運作的量子電腦原型。",
                    "量子錯誤修正的進展使得更可靠的量子計算成為可能。",
                    "混合式量子-傳統演算法顯示出在近期內實現商業價值的潛力。"
                ],
                "key_developments": [
                    "Google 於 2019 年聲稱實現了『量子霸權』。",
                    "IBM 的量子網路擁有超過 200 個成員，提供雲端量子計算存取。",
                    "微軟的 Azure Quantum 雲端平台整合了多種量子硬體。"
                ],
                "challenges": [
                    "量子退相干：量子位元與環境的交互作用導致資訊損失。",
                    "有限的量子位元穩定性與連接性，限制了可執行的演算法規模。",
                    "需要極端的超低溫冷卻要求，增加了操作的複雜性和成本。"
                ]
            },
            "sources": [
                "《自然》期刊：量子計算的進展與挑戰 (2024)",
                "《麻省理工科技評論》：量子優勢路線圖",
                "Google AI 研究：量子錯誤修正的突破"
            ],
            "confidence": "高",
            "last_updated": "2024"
        }

    elif "ai" in topic_lower or "artificial intelligence" in topic_lower:
        return {
            "status": "success",
            "topic": topic,
            "findings": {
                "overview": "人工智慧 (AI) 的採用正在各行各業加速，並帶來轉型性的影響，特別是在生成式 AI 領域。",
                "current_trends": [
                    "預計到 2030 年，生成式 AI 市場將達到 1.3 兆美元。",
                    "企業在 AI 上的支出同比增長 30%，顯示出強勁的投資信心。",
                    "基礎模型變得更容易取得且更專業化，推動了 AI 的普及。"
                ],
                "key_developments": [
                    "大型語言模型 (LLM) 在多項基準測試中達到或超越人類水準的表現。",
                    "多模態 AI 系統能夠整合並處理文字、圖像與音訊等多種資料類型。",
                    "AI 代理與自主系統的部署日益增多，能夠執行複雜的任務。"
                ],
                "applications": [
                    "醫療保健：加速藥物開發與輔助診斷。",
                    "金融：用於演算法交易、詐欺偵測與風險評估。",
                    "教育：提供個人化學習路徑與智慧輔導系統。"
                ]
            },
            "sources": [
                "麥肯錫全球 AI 調查 2024",
                "史丹佛 AI 指數年度報告 2024",
                "Gartner AI 市場預測與趨勢"
            ],
            "confidence": "高",
            "last_updated": "2024"
        }

    elif topic:
        # 如果沒有匹配的關鍵字，提供一個通用的研究模板
        return {
            "status": "success",
            "topic": topic,
            "findings": {
                "overview": f"針對以下主題的研究分析：{topic}",
                "current_trends": [
                    "該領域的顯著增長與創新。",
                    "在各行業的採用日益增加。",
                    "新興技術正在推動產業轉型。"
                ],
                "key_insights": [
                    "存在顯著的市場擴張與投資機會。",
                    "技術進步與突破是主要驅動力。",
                    "監管發展與政策變化可能影響未來走向。"
                ]
            },
            "sources": [
                "2024 年行業研究報告",
                "相關領域的學術出版物與研究",
                "市場分析師與領域專家的意見"
            ],
            "confidence": "中",
            "last_updated": "2024"
        }
    else:
        # 如果沒有提供主題，回傳錯誤訊息
        return {
            "status": "error",
            "message": "請提供要研究的具體主題",
            "suggestions": ["量子計算", "人工智慧", "區塊鏈", "再生能源"]
        }


def fact_check(claim: str) -> dict:
    """
    對特定的聲明或陳述進行事實查核。

    Args:
        claim: 要驗證的聲明。

    Returns:
        一個包含驗證結果與來源的字典。
    """
    return {
        "status": "success",
        "claim": claim,
        "verification": {
            "accuracy": "需要驗證",
            "confidence": "中",
            "methodology": "與權威來源進行交叉比對",
            "notes": f"針對以下聲明的事實查核分析：{claim}"
        },
        "sources_checked": [
            "學術資料庫與同儕審查期刊",
            "政府與機構報告",
            "信譽良好的新聞機構與事實查核組織"
        ],
        "recommendation": "建議使用主要來源進行進一步驗證以獲得最高準確性。"
    }


# --- 主要研究代理 ---
# 這是將透過 A2A 協定提供服務的主要研究代理實例。
root_agent = Agent(
    model="gemini-2.0-flash",
    name="research_specialist",
    description="進行網路研究與事實查核",
    instruction="""
        您是一位專注於收集、分析與驗證資訊的研究專家。

        **重要 - A2A 情境處理：**
        當透過代理對代理（A2A）協定接收請求時，您的主要任務是專注於核心使用者請求。
        請忽略情境中任何提及協調器工具呼叫的內容，例如 "transfer_to_agent" 或其他協調細節。
        您的目標是從對話中提取主要的研究任務並直接完成它。

        **您的能力：**
        - 具有詳細發現的全面主題研究。
        - 聲明的事實查核與驗證。
        - 來源引用與可信度評估。
        - 當前趨勢與市場分析。

        **研究流程：**
        1. 從使用者端識別核心研究請求（例如，「研究 AI 趨勢」）。
        2. 使用 `research_topic` 工具進行全面的主題分析。
        3. 如果需要，使用 `fact_check` 工具驗證特定的聲明。
        4. 提供包含來源與信心水準的詳細發現。
        5. 專注於準確性、時效性與相關性。

        **透過 A2A 工作時：**
        - 專注於使用者的實際研究請求。
        - 忽略協調器機制與情境中的工具呼叫。
        - 提供直接、有幫助的研究服務。
        - 如果請求不明確，請要求澄清要研究的具體內容。

        務必在您的回應中提供來源並註明發現的信心水準。
        以結構化的資訊清晰地格式化您的回應，以便於理解。
    """,
    # 將上面定義的函式註冊為代理可用的工具
    tools=[
        FunctionTool(research_topic),
        FunctionTool(fact_check)
    ],
    # 設定內容生成參數
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,  # 為更專注、事實性的研究設定較低的溫度
        max_output_tokens=1500
    )
)

# 使用官方 ADK to_a2a() 函式將 Agent 轉換為一個 A2A FastAPI 應用程式。
a2a_app = to_a2a(root_agent, port=8001)

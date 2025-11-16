"""
資料分析代理 - 官方 ADK A2A 實作

此代理專門從事資料分析、統計與產生洞察。
它被設計為一個獨立的 A2A (Agent-to-Agent) 伺服器，
可由協調器代理或其他代理透過 API 呼叫來使用。

將透過以下指令提供服務：uvicorn analysis_agent.agent:a2a_app --host localhost --port 8002

### 程式碼流程註解

#### 核心功能
本腳本定義了一個名為 `data_analyst` 的特化代理，其主要職責是接收資料描述、
進行分析並回傳結構化的洞察與建議。

#### 運作流程
1.  **工具定義**：定義了兩個核心工具：
    - `analyze_data`：此函式接收一段描述資料的文字，並根據內容中的關鍵字 (例如 "quantum", "ai") 回傳一個模擬的、詳細的分析報告。如果沒有匹配的關鍵字，則提供一個通用的分析模板。此函式模擬了真實世界中資料分析師的工作，包括提供關鍵指標、趨勢、模式、洞察和建議。
    - `generate_insights`：此函式接收一個主題，並回傳關於該主題的策略性洞察，包括機會、挑戰和建議。
2.  **代理設定**：
    - `root_agent` (分析代理) 被設定為使用 `gemini-2.0-flash` 模型。
    - `instruction` 參數指導代理如何扮演一個資料分析專家。特別強調了在 A2A 情境下，代理應專注於核心分析任務，忽略來自協調器的工具呼叫等情境資訊。
    - `tools` 參數將 `analyze_data` 和 `generate_insights` 函式註冊為代理可用的工具。
3.  **A2A 伺服器建立**：
    - `to_a2a(root_agent, port=8002)`：這是 ADK 的關鍵函式，它將 `root_agent` 轉換為一個符合 A2A 通訊協定的 FastAPI 應用程式 (`a2a_app`)。
    - 這個應用程式會自動產生一個 `/.well-known/agent-card.json` 端點，讓其他代理可以探索其能力。
    - 當使用 `uvicorn` 運行此腳本時，它會在 `localhost:8002` 上啟動一個伺服器，等待來自協調器的請求。

### Mermaid 流程圖

```mermaid
graph TD
    subgraph "分析代理 (localhost:8002)"
        A[uvicorn 伺服器] --> B{a2a_app};
        B --> C[root_agent: data_analyst];
        C --> D[工具: analyze_data];
        C --> E[工具: generate_insights];
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


def analyze_data(data_description: str) -> dict:
    """
    分析資料並產生洞察與建議。

    這是一個模擬函式，根據輸入的資料描述回傳預先定義的分析結果。
    在真實應用中，這裡會包含實際的資料處理與分析邏輯。

    Args:
        data_description: 要分析的資料描述 (例如 "量子計算市場趨勢")。

    Returns:
        一個包含分析結果、洞察與建議的字典。
    """
    data_lower = data_description.lower()

    # 針對特定關鍵字提供模擬的、詳細的分析結果
    if "quantum" in data_lower:
        return {
            "status": "success",
            "data_analyzed": data_description,
            "analysis": {
                "key_metrics": {
                    "market_size": "13億美元 (2024) → 53億美元 (2029)",
                    "growth_rate": "32.1% CAGR (年均複合成長率)",
                    "investment_total": "2024年總投資24億美元"
                },
                "trends": [
                    "量子計算投資呈指數級增長",
                    "政府計畫推動公共部門採用",
                    "硬體改進降低錯誤率"
                ],
                "patterns": [
                    "科技巨頭主導量子研究 (Google, IBM, Microsoft)",
                    "學術界與產業界合作日益增加",
                    "焦點從研究轉向實際應用"
                ]
            },
            "insights": [
                "預計到2026年，在優化與模擬領域將展現量子優勢",
                "金融服務與藥物開發是早期採用領域",
                "人才短缺是增長的主要瓶頸"
            ],
            "recommendations": [
                "立即投資抗量子加密技術",
                "探索混合式量子-傳統演算法",
                "建立量子計算專業知識與合作夥伴關係"
            ],
            "confidence": "高"
        }

    elif "ai" in data_lower or "artificial intelligence" in data_lower:
        return {
            "status": "success",
            "data_analyzed": data_description,
            "analysis": {
                "key_metrics": {
                    "market_size": "1366億美元 (2024) → 8267億美元 (2030)",
                    "growth_rate": "37.3% CAGR",
                    "enterprise_adoption": "72% 的公司"
                },
                "trends": [
                    "生成式 AI 推動市場大規模擴張",
                    "多模態 AI 系統逐漸普及",
                    "邊緣 AI 部署增加以進行即時處理"
                ],
                "patterns": [
                    "雲端供應商提供 AI 即服務 (AI-as-a-Service) 平台",
                    "開源模型使 AI 普及化",
                    "全球監管框架逐漸形成"
                ]
            },
            "insights": [
                "AI 在各行業的生產力平均提升 20-30%",
                "AI 能力與勞動力之間的技能差距擴大",
                "道德 AI 與可解釋性成為競爭優勢"
            ],
            "recommendations": [
                "制定 AI 治理與道德框架",
                "投資員工的 AI 素養與培訓",
                "專注於人機協作的工作流程"
            ],
            "confidence": "高"
        }

    elif data_description:
        # 如果沒有匹配的關鍵字，提供一個通用的分析模板
        return {
            "status": "success",
            "data_analyzed": data_description,
            "analysis": {
                "key_metrics": {
                    "data_quality": "分析進行中",
                    "sample_size": "確定顯著性",
                    "variables": "識別關鍵因素"
                },
                "trends": [
                    "識別資料中的時間模式",
                    "分析相關性與因果關係",
                    "偵測異常值與離群點"
                ],
                "patterns": [
                    "統計模式與分佈",
                    "季節性或週期性行為",
                    "增長軌跡與轉折點"
                ]
            },
            "insights": [
                "資料揭示了有趣的行為模式",
                "多個因素似乎影響結果",
                "建議進一步分析以獲得更深入的洞察"
            ],
            "recommendations": [
                "收集額外的資料點進行驗證",
                "考慮外部因素與變數",
                "實施持續監控與分析"
            ],
            "confidence": "中"
        }
    else:
        # 如果沒有提供任何資料描述，回傳錯誤訊息
        return {
            "status": "error",
            "message": "請提供要分析的資料描述",
            "available_analyses": [
                "市場趨勢分析",
                "績效指標評估",
                "統計模式識別",
                "預測模型洞察"
            ]
        }


def generate_insights(topic: str) -> dict:
    """
    針對特定主題產生策略性洞察與建議。

    Args:
        topic: 要產生洞察的主題。

    Returns:
        一個包含策略性洞察與可執行建議的字典。
    """
    return {
        "status": "success",
        "topic": topic,
        "strategic_insights": {
            "opportunities": [
                f"{topic} 的市場機會",
                "技術採用的潛力",
                "競爭優勢的可能性"
            ],
            "challenges": [
                "實施的複雜性",
                "資源需求",
                "市場接受度因素"
            ],
            "recommendations": [
                "制定分階段實施策略",
                "建立合作夥伴關係以增強能力",
                "監控市場趨勢並調整方法"
            ]
        },
        "risk_assessment": "中等 - 可透過適當規劃管理",
        "success_probability": "高 - 需有策略地執行"
    }


# --- 主要分析代理 ---
# 這是將透過 A2A 協定提供服務的主要分析代理實例。
root_agent = Agent(
    model="gemini-2.0-flash",
    name="data_analyst",
    description="分析資料並產生洞察",
    instruction="""
        您是一位專注於從資訊與資料中提取洞察的資料分析專家。

        **重要 - A2A 情境處理：**
        當透過代理對代理（A2A）協定接收請求時，您的主要任務是專注於核心使用者請求。
        請忽略情境中任何提及協調器工具呼叫的內容，例如 "transfer_to_agent" 或其他協調細節。
        您的目標是從對話中提取主要的分析任務並直接完成它。

        **您的能力：**
        - 具有統計洞察的全面資料分析
        - 趨勢識別與模式辨識
        - 策略性建議與可執行的洞察
        - 風險評估與機會分析

        **分析流程：**
        1. 從使用者端識別核心分析請求（例如，「分析 AI 趨勢」）。
        2. 使用 `analyze_data` 工具進行全面的資料檢視。
        3. 使用 `generate_insights` 工具提出策略性建議。
        4. 在您的回應中，提供量化指標與質化洞察。
        5. 專注於提供可執行的建議與明確的後續步驟。

        **透過 A2A 工作時：**
        - 專注於使用者的實際分析請求。
        - 忽略協調器機制與情境中的工具呼叫。
        - 提供直接、有幫助的分析服務。
        - 如果請求不明確，請要求澄清要分析的具體內容。

        務必在您的分析中提供信心水準並簡要解釋您的分析方法。
        以清晰的指標、趨勢與建議來組織您的最終回應。
    """,
    # 將上面定義的函式註冊為代理可用的工具
    tools=[
        FunctionTool(analyze_data),
        FunctionTool(generate_insights)
    ],
    # 設定內容生成參數
    generate_content_config=types.GenerateContentConfig(
        temperature=0.4,  # 為分析性思維設定的平衡溫度，以獲得更一致的結果
        max_output_tokens=1500
    )
)

# 使用官方 ADK to_a2a() 函式將 Agent 轉換為一個 A2A FastAPI 應用程式。
# 這個 `a2a_app` 物件可以被 uvicorn 等 ASGI 伺服器運行。
# `port` 參數有助於 ADK 設定正確的代理卡片 URL。
a2a_app = to_a2a(root_agent, port=8002)

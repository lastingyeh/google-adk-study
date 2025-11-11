# 教學 12：規劃器與思維 (Planners and Thinking) - 策略性代理規劃 (Strategic Agent Planning)

**目標**：掌握使用內建規劃器 (Built-in Planners)、思維設定 (Thinking Configuration) 和結構化的 Plan-ReAct 模式的進階推理能力，以解決複雜問題。

**先決條件**：
*   [教學 01 (Hello World Agent)](../adk_training/01-hello_world_agent.md)
*   [教學 02 (Function Tools)](../adk_training/02-function_tools.md)
*   Gemini 2.0+ 模型存取權限

**您將學到**：
*   使用 `BuiltInPlanner` 進行擴展思維
*   實現 `PlanReActPlanner` 進行結構化推理
*   設定 `ThinkingConfig` 以實現透明化推理
*   使用 `BasePlanner` 建立自訂規劃器
*   建立在行動前會先規劃的代理
*   了解何時該使用哪種規劃器

**完成時間**：50-65 分鐘

---

🚀 **快速入門 (Quick Start)**
----------------------------------------------------------------

### 1. 設定環境 (Setup Environment)

```bash
# 複製並導航至實作目錄
cd tutorial_implementation/tutorial12
# 安裝依賴項
make setup
# 複製環境設定範本
cp strategic_solver/.env.example strategic_solver/.env
# 編輯 .env 檔案並加入您的 Google AI API 金鑰
# GOOGLE_API_KEY=your_actual_api_key_here
```

### 2. 執行開發伺服器 (Run Development Server)

```bash
# 啟動 ADK 網頁介面
make dev
# 在瀏覽器中開啟 http://localhost:8000
# 從代理下拉選單中選擇 "strategic_solver"
```

### 3. 測試實作 (Test the Implementation)

```bash
# 執行綜合測試套件
make test
# 查看可測試的範例查詢
make examples
# 執行範例
make demo
```

---

**為何規劃器很重要 (Why Planners Matter)**
---------------------------------------------------------------------------------

預設的代理會立即對查詢做出反應。**規劃器**則增加了一個關鍵步驟：**行動前先思考**。這帶來了：

*   🧠 **更佳的推理 (Better Reasoning)**：多步驟問題分解
*   🎯 **更高的準確性 (Improved Accuracy)**：執行前驗證計畫
*   🔍 **透明的思維 (Transparent Thinking)**：了解代理如何推理
*   🔄 **動態重新規劃 (Dynamic Replanning)**：根據結果調整策略
*   💡 **解決複雜問題 (Complex Problem Solving)**：處理多面向的挑戰

**無規劃器** (直接回應)：

```
使用者：「規劃一趟日本之旅」
代理：「這是一份旅行計畫...」 [立即回應]
```

**有規劃器** (結構化推理)：

```
使用者：「規劃一趟日本之旅」
代理：
  <PLAN>
  1. 了解需求（預算、天數、興趣）
  2. 研究目的地
  3. 建立行程
  4. 估算費用
  5. 提供建議
  </PLAN>
  <REASONING>
  需要先收集資訊，然後系統性地規劃...
  </REASONING>
  <ACTION>
  讓我先從詢問您的偏好開始...
  </ACTION>
```

---

## 1. BuiltInPlanner (擴展思維)
-------------------------------------------------------------------------------------------------------------------------------------

### 什麼是 BuiltInPlanner？ (What is BuiltInPlanner?)

`BuiltInPlanner` 利用 Gemini 2.0+ 的**原生思維能力**——模型在生成回應前會進行內部擴展推理。

**來源**：`google/adk/planners/built_in_planner.py`

### 基本用法 (Basic Usage)

```python
from google.adk.agents import Agent
from google.adk.planners import BuiltInPlanner
from google.adk.runners import Runner
from google.genai import types

# 建立具有擴展思維的代理
agent = Agent(
    model='gemini-2.0-flash',  # 需要支援思維的 Gemini 2.0+
    name='thoughtful_assistant',
    instruction='你是一個在回應前會仔細思考的實用助理。',
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            include_thoughts=True  # 向使用者顯示推理過程
        )
    )
)

runner = Runner()
result = runner.run(
    "你將如何解決世界飢餓問題？",
    agent=agent
)
print(result.content.parts[0].text)
# 包含模型的推理過程
```

**輸出包含思維過程**：

```
[Thinking]
這是一個複雜的全球性問題，需要多面向的方法。
我需要考慮：
- 農業技術
- 分配系統
- 經濟因素
- 政治意願
- 氣候變遷的影響
讓我系統地組織一下...
[End Thinking]

根據我的分析，以下是應對世界飢餓的關鍵策略：
1. 提高發展中地區的農業生產力...
2. 透過更好的供應鏈減少食物浪費...
...
```

### ThinkingConfig 選項 (ThinkingConfig Options)

```python
from google.genai import types

# 向使用者顯示思維過程
thinking_config = types.ThinkingConfig(
    include_thoughts=True  # 使用者看得到推理過程
)

# 隱藏思維過程（只顯示最終答案）
thinking_config = types.ThinkingConfig(
    include_thoughts=False  # 只顯示最終答案
)
```

**何時顯示思維過程**：
*   ✅ 教育應用（教導推理）
*   ✅ 調試代理邏輯
*   ✅ 建立信任（透明的 AI）
*   ✅ 解釋複雜問題

**何時隱藏思維過程**：
*   ✅ 面向使用者的生產環境應用
*   ✅ 當使用者需要快速答案時
*   ✅ API 回應（效率考量）
*   ✅ 當思維過程不會增加價值時

### 內部運作原理 (How It Works Internally)

```python
# BuiltInPlanner 的簡化實作
class BuiltInPlanner(BasePlanner):
    def __init__(self, thinking_config: types.ThinkingConfig = None):
        self.thinking_config = thinking_config or types.ThinkingConfig()

    def apply_thinking_config(self, llm_request: LlmRequest):
        """將思維設定應用於 LLM 請求。"""
        if self.thinking_config:
            llm_request.config.thinking_config = self.thinking_config
        return llm_request
```

### 模型相容性 (Model Compatibility)

```python
# ✅ 適用於支援思維的 Gemini 2.0+ 模型
agent = Agent(
    model='gemini-2.0-flash',
    planner=BuiltInPlanner(thinking_config=types.ThinkingConfig(include_thoughts=True))
)

# ❌ 可能不適用於不支援思維的模型
# 使用前請檢查模型能力
```

---

## 2. PlanReActPlanner (結構化推理)
----------------------------------------------------------------------------------------------------------------------------------------------------

### 什麼是 PlanReActPlanner？ (What is PlanReActPlanner?)

`PlanReActPlanner` 實現了 **Plan-ReAct 模式**：計畫 → 推理 → 行動 → 觀察 → 重新規劃。這建立了一個結構化的推理循環。

**來源**：`google/adk/planners/plan_re_act_planner.py`

### 基本用法 (Basic Usage)

```python
from google.adk.agents import Agent
from google.adk.planners import PlanReActPlanner
from google.adk.runners import Runner

# 建立使用 Plan-ReAct 模式的代理
agent = Agent(
    model='gemini-2.0-flash',
    name='systematic_planner',
    instruction='你使用規劃與推理來系統性地解決問題。',
    planner=PlanReActPlanner()
)

runner = Runner()
result = runner.run(
    "建立一個機器學習模型來預測房價",
    agent=agent
)
print(result.content.parts[0].text)
```

**輸出結構**：

```xml
<PLANNING>
要建立一個房價預測模型，我需要：
1. 收集並清理房屋數據
2. 選擇相關特徵（大小、地點、屋齡等）
3. 選擇合適的演算法（迴歸）
4. 訓練並驗證模型
5. 評估性能
</PLANNING>
<REASONING>
對於這個問題：
- 線性迴歸適用於連續的價格預測
- 需要平方英尺、臥室數量、地點等特徵
- 必須處理缺失數據和異常值
- 交叉驗證對於泛化很重要
</REASONING>
<ACTION>
讓我從概述數據需求開始：
- 歷史銷售價格
- 房產特徵
- 地點數據...
</ACTION>
<FINAL_ANSWER>
這是一份為您的機器學習模型制定的完整計畫...
</FINAL_ANSWER>
```

### 規劃標籤 (Planning Tags)

PlanReActPlanner 使用類似 XML 的標籤來結構化推理：

| 標籤             | 目的         | 使用時機         |
| ---------------- | ------------ | ---------------- |
| `<PLANNING>`     | 初始計畫     | 任務開始時       |
| `<REASONING>`    | 解釋邏輯     | 整個過程中       |
| `<ACTION>`       | 執行步驟     | 當執行某事時     |
| `<OBSERVATION>`  | 記錄結果     | 行動後           |
| `<REPLANNING>`   | 調整計畫     | 當策略改變時     |
| `<FINAL_ANSWER>` | 結論         | 任務結束時       |

### 重新規劃範例 (Replanning Example)

```python
from google.adk.agents import Agent
from google.adk.planners import PlanReActPlanner
from google.adk.tools import FunctionTool
from google.adk.runners import Runner

# 模擬失敗的工具
def check_api_status(api_name: str) -> str:
    """檢查 API 是否可用。"""
    if api_name == "primary_api":
        return "ERROR: API unavailable"
    return "OK: API available"

# 具有重新規劃能力的代理
agent = Agent(
    model='gemini-2.0-flash',
    name='adaptive_agent',
    instruction='使用工具並在出現問題時調整計畫。',
    planner=PlanReActPlanner(),
    tools=[FunctionTool(check_api_status)]
)

runner = Runner()
result = runner.run(
    "從 primary_api 獲取數據並處理",
    agent=agent
)
print(result.content.parts[0].text)
```

**輸出顯示重新規劃過程**：

```xml
<PLANNING>
計畫：
1. 檢查 primary_api 狀態
2. 從 primary_api 獲取數據
3. 處理數據
</PLANNING>
<ACTION>
正在檢查 primary_api 狀態...
</ACTION>
<OBSERVATION>
API 回傳錯誤：API unavailable
</OBSERVATION>
<REPLANNING>
主要 API 已關閉。新計畫：
1. 檢查 backup_api 狀態
2. 改用 backup_api
3. 從備份來源處理數據
</REPLANNING>
<ACTION>
切換至 backup_api...
</ACTION>
<FINAL_ANSWER>
已成功使用 backup_api 檢索並處理數據。
</FINAL_ANSWER>
```

### 規劃指令 (Planning Instructions)

PlanReActPlanner 會注入詳細的規劃指令：

```python
# 內部規劃指令（簡化版）
PLANNING_INSTRUCTION = """
你必須遵循這個結構化的推理格式：
<PLANNING>
將問題分解為步驟：
1. 步驟 1
2. 步驟 2
3. ...
</PLANNING>
<REASONING>
解釋為何此計畫合理：
- 考量 1
- 考量 2
</REASONING>
<ACTION>
描述你現在正在做什麼
</ACTION>
<OBSERVATION>
記錄發生了什麼
</OBSERVATION>
如果計畫需要調整：
<REPLANNING>
解釋為何重新規劃以及新計畫：
1. 新步驟 1
2. ...
</REPLANNING>
完成後：
<FINAL_ANSWER>
提供最終結果
</FINAL_ANSWER>
"""
```

---

## 3. 真實世界範例：策略性問題解決器 (Real-World Example: Strategic Problem Solver)
--------------------------------------------------------------------------------------------------------------------------------------------------------------------

讓我們建立一個使用 Plan-ReAct 來解決複雜商業問題的代理。

### 完整實作 (Complete Implementation)

```python
"""
策略性商業問題解決器
使用 Plan-ReAct 模式進行系統性問題解決。
"""
import asyncio
import os
from datetime import datetime
from google.adk.agents import Agent, Runner
from google.adk.planners import PlanReActPlanner
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

# 環境設定
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = '1'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-project-id'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'

# 工具：市場研究
def analyze_market(industry: str, region: str) -> dict:
    """分析市場狀況（模擬）。"""
    # 在生產環境中，應呼叫真實的市場數據 API
    return {
        'industry': industry,
        'region': region,
        'growth_rate': '8.5%',
        'competition': 'High',
        'trends': ['數位轉型', '永續發展焦點'],
        'opportunities': ['新興市場', '新技術']
    }

# 工具：財務分析
def calculate_roi(investment: float, annual_return: float, years: int) -> dict:
    """計算投資回報率。"""
    total_return = investment * ((1 + annual_return/100) ** years)
    profit = total_return - investment
    return {
        'initial_investment': investment,
        'annual_return_rate': f"{annual_return}%",
        'years': years,
        'total_return': round(total_return, 2),
        'profit': round(profit, 2),
        'roi_percentage': round((profit/investment)*100, 2)
    }

# 工具：風險評估
def assess_risk(factors: list[str]) -> dict:
    """評估商業風險。"""
    risk_scores = {
        'market_volatility': 7,
        'regulatory_changes': 5,
        'competition': 8,
        'technology': 6,
        'financial': 4
    }
    total_risk = sum(risk_scores.get(f, 5) for f in factors)
    avg_risk = total_risk / len(factors) if factors else 5
    return {
        'factors_assessed': factors,
        'risk_score': round(avg_risk, 2),
        'risk_level': 'High' if avg_risk > 7 else 'Medium' if avg_risk > 4 else 'Low',
        'mitigation_needed': avg_risk > 6
    }

# 工具：儲存策略報告
async def save_strategy_report(
    problem: str,
    strategy: str,
    tool_context: ToolContext) -> str:
    """將策略計畫儲存為產出物。"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    report = f"""
# 策略性商業計畫
產生時間：{timestamp}

## 問題陳述
{problem}

## 建議策略
{strategy}

## 計畫產生者
- 代理：Strategic Problem Solver
- 規劃器：PlanReActPlanner
- 模型：gemini-2.0-flash
    """.strip()
    filename = f"strategy_{problem[:30].replace(' ', '_')}.md"
    version = await tool_context.save_artifact(
        filename=filename,
        part=types.Part.from_text(report)
    )
    return f"策略已儲存為 {filename} (版本 {version})"

# 建立策略性問題解決器
strategic_solver = Agent(
    model='gemini-2.0-flash',
    name='strategic_solver',
    description='系統性地解決複雜的商業問題',
    planner=PlanReActPlanner(),  # 使用結構化規劃
    instruction="""
你是一位策略性商業顧問。當接到一個問題時：
1. 計畫 (PLAN)：將問題分解為明確的步驟
2. 推理 (REASON)：解釋你的邏輯
3. 行動 (ACT)：使用工具收集數據
4. 觀察 (OBSERVE)：分析結果
5. 重新規劃 (REPLAN)：如有需要則調整
6. 結論 (CONCLUDE)：提供最終建議
永遠要徹底並以數據為導向。使用工具進行：
- analyze_market：市場研究
- calculate_roi：財務預測
- assess_risk：風險分析
- save_strategy_report：儲存最終計畫
按部就班地思考並展示你的推理過程。
    """.strip(),
    tools=[
        FunctionTool(analyze_market),
        FunctionTool(calculate_roi),
        FunctionTool(assess_risk),
        FunctionTool(save_strategy_report)
    ],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.4,  # 平衡的溫度以進行策略性思考
        max_output_tokens=3000
    )
)

async def solve_business_problem(problem: str):
    """解決策略性商業問題。"""
    print(f"\n{'='*70}")
    print(f"問題：{problem}")
    print(f"{'='*70}\n")
    runner = Runner()
    result = await runner.run_async(
        problem,
        agent=strategic_solver
    )
    print("\n📊 策略分析：\n")
    print(result.content.parts[0].text)
    print(f"\n{'='*70}\n")

async def main():
    """執行策略性問題解決範例。"""
    # 範例 1：市場進入策略
    await solve_business_problem("""
我們是一家中型軟體公司，正在考慮進入醫療保健 AI 市場。我們應該追求這個機會嗎？策略是什麼？
    """)
    await asyncio.sleep(2)
    # 範例 2：投資決策
    await solve_business_problem("""
我們有 50 萬美元可以投資於：
A) 擴展現有產品線（年回報率 15%，中度風險）
B) 進入新市場（年回報率 25%，高度風險）
以 5 年為期，我們應該選擇哪一個？
    """)
    await asyncio.sleep(2)
    # 範例 3：風險緩解
    await solve_business_problem("""
我們的新創公司面臨：
- 日益激烈的競爭
- 監管不確定性
- 技術顛覆
我們應該如何緩解這些風險？
    """)

if __name__ == '__main__':
    asyncio.run(main())
```

### 預期輸出 (Expected Output)

```
======================================================================
問題：我們是一家中型軟體公司，正在考慮進入醫療保健 AI 市場。我們應該追求這個機會嗎？策略是什麼？
======================================================================

📊 策略分析：
<PLANNING>
要評估進入醫療保健 AI 市場，我需要：
1. 使用 analyze_market 工具分析市場狀況
2. 使用 calculate_roi 評估財務可行性
3. 使用 assess_risk 評估風險
4. 將研究結果綜合為建議
5. 儲存策略計畫
</PLANNING>
<ACTION>
正在分析醫療保健 AI 市場...
</ACTION>
<OBSERVATION>
市場分析結果：
- 產業：醫療保健 AI
- 增長率：每年 8.5%
- 競爭：激烈
- 主要趨勢：數位轉型、永續發展焦點
- 機會：新興市場、新技術
</OBSERVATION>
<REASONING>
醫療保健 AI 市場顯示強勁增長（8.5%），但競爭激烈。
數位轉型趨勢是有利的。在提出建議前，需要評估財務回報和風險。
</REASONING>
<ACTION>
正在計算 50 萬美元投資 5 年的潛在投資回報率...
</ACTION>
<OBSERVATION>
ROI 分析：
- 初始投資：500,000 美元
- 預計年回報率：15%
- 5 年總回報：1,005,694 美元
- 利潤：505,694 美元
- ROI：101.14%
</OBSERVATION>
<ACTION>
正在評估商業風險...
</ACTION>
<OBSERVATION>
風險評估：
- 因素：市場波動、監管變化、競爭、技術
- 風險分數：6.5/10
- 風險等級：中等
- 需要緩解措施：是
</OBSERVATION>
<FINAL_ANSWER>
**建議：謹慎進行**

**市場進入策略：**
1. **小規模起步（第一階段：第 1 年）**
   - 與 2-3 家醫療保健客戶進行試點專案
   - 專注於利基應用案例（例如，診斷影像 AI）
   - 投資：10-15 萬美元
   - 建立概念驗證
2. **驗證與擴展（第二階段：第 2-3 年）**
   - 如果試點成功，擴展至 10 家以上客戶
   - 與醫院建立合作夥伴關係
   - 投資：20-25 萬美元
   - 實現監管合規
3. **全面市場進入（第三階段：第 4-5 年）**
   - 推出完整產品套件
   - 擴大營運規模
   - 投資：剩餘預算
   - 目標是全國性市場

**風險緩解：**
- 與已建立的醫療保健提供者合作
- 聘請監管合規專家
- 維持多元化的產品組合
- 建立強大的智慧財產權保護

**財務前景：**
- 預計 5 年 ROI：101%
- 損益兩平：預計在第 3 年
- 市場增長：每年 8.5%

**關鍵成功因素：**
- 從第一天起就符合監管要求
- 穩固的臨床合作夥伴關係
- 差異化的技術
- 注重病患隱私

[策略已儲存為 strategy_We're_a_mid-sized_software.md (版本 1)]
</FINAL_ANSWER>
======================================================================
```

---

## 4. BasePlanner (自訂規劃器)
----------------------------------------------------------------------------------------------------------------------

### 什麼是 BasePlanner？ (What is BasePlanner?)

`BasePlanner` 是用於建立自訂規劃策略的**抽象基礎類別**。

**來源**：`google/adk/planners/base_planner.py`

### 建立自訂規劃器 (Creating Custom Planner)

```python
from google.adk.planners import BasePlanner
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.models.llm_request import LlmRequest
from google.genai import types
from typing import List, Optional

class MyCustomPlanner(BasePlanner):
    """自訂規劃策略。"""

    def build_planning_instruction(
        self,
        readonly_context: ReadonlyContext,
        llm_request: LlmRequest,
    ) -> Optional[str]:
        """
        注入自訂規劃指令。

        Args:
            readonly_context: 包含當前調用之會話狀態、使用者狀態和應用程式狀態的唯讀上下文。
            llm_request: 包含使用者訊息、對話歷史和生成參數的 LLM 請求物件。

        Returns:
            用於指導代理推理的規劃指令字串，如果不需要自訂規劃指令則返回 None。
        """
        return """
            你是一個系統性的問題解決者。對於每個任務：
            步驟 1：分析
            - 目標是什麼？
            - 存在哪些限制？
            - 有哪些可用資源？

            步驟 2：制定策略
            - 有哪些可能的方法？
            - 每種方法的優缺點是什麼？
            - 哪種是最佳選擇？

            步驟 3：執行
            - 實施所選策略
            - 監控進度
            - 根據需要進行調整

            步驟 4：驗證
            - 我們是否達成了目標？
            - 有哪些可以改進的地方？
        """

    def process_planning_response(
        self,
        callback_context: CallbackContext,
        response_parts: List[types.Part],
    ) -> Optional[List[types.Part]]:
        """
        處理規劃後的回應。

        Args:
            callback_context: 提供在當前調用期間存取狀態、工具和修改代理行為能力的 callback 上下文。
            response_parts: 來自規劃步驟的 LLM 回應部分。唯讀列表，不應就地修改。

        Returns:
            處理後的回應部分（可以是修改後的副本），如果不需要處理且應使用原始部分，則返回 None。
        """
        # 可以在這裡修改 response_parts
        # 例如，新增元數據、驗證結構等
        return response_parts

# 使用自訂規劃器
agent = Agent(
    model='gemini-2.0-flash',
    planner=MyCustomPlanner()
)
```

### 進階自訂規劃器範例 (Advanced Custom Planner Example)

```python
class DataSciencePlanner(BasePlanner):
    """用於數據科學工作流程的規劃器。"""

    def build_planning_instruction(
        self,
        readonly_context: ReadonlyContext,
        llm_request: LlmRequest,
    ) -> Optional[str]:
        """
        建立數據科學規劃指令。

        Args:
            readonly_context: 包含當前調用之會話狀態、使用者狀態和應用程式狀態的唯讀上下文。
            llm_request: 包含使用者訊息、對話歷史和生成參數的 LLM 請求物件。

        Returns:
            用於數據科學工作流程的規劃指令字串，指導代理遵循數據科學方法論。
        """
        return """
            遵循數據科學方法論：
            <DATA_UNDERSTANDING>
            1. 有哪些可用數據？
            2. 數據品質如何？
            3. 特徵是什麼？
            </DATA_UNDERSTANDING>
            <PROBLEM_FORMULATION>
            1. 預測目標是什麼？
            2. 問題類型是什麼？（分類、迴歸、聚類）
            3. 成功指標是什麼？
            </PROBLEM_FORMULATION>
            <MODELING_APPROACH>
            1. 哪些演算法是合適的？
            2. 如何驗證？（訓練/測試集分割、交叉驗證）
            3. 如何調整超參數？
            </MODELING_APPROACH>
            <EVALUATION>
            1. 模型性能如何？
            2. 是否足夠好？
            3. 如何改進？
            </EVALUATION>
            <DEPLOYMENT>
            1. 如何部署模型？
            2. 如何監控性能？
            3. 如何更新模型？
            </DEPLOYMENT>
        """

    def process_planning_response(
        self,
        callback_context: CallbackContext,
        response_parts: List[types.Part],
    ) -> Optional[List[types.Part]]:
        """
        處理數據科學規劃回應。

        Args:
            callback_context: 在當前調用期間提供存取狀態、工具和代理控制的 callback 上下文。
            response_parts: 來自規劃步驟的 LLM 回應部分。唯讀列表，不應就地修改。

        Returns:
            帶有數據科學特定驗證或元數據的處理後回應部分，或返回 None 以使用原始部分。
        """
        # 可以在這裡新增數據科學特定的驗證或元數據
        return response_parts

# 具有自訂規劃器的數據科學代理
ds_agent = Agent(
    model='gemini-2.0-flash',
    name='data_scientist',
    planner=DataSciencePlanner(),
    instruction='你是一位遵循最佳實踐的專家級數據科學家。'
)
```

---

## 5. 比較規劃器 (Comparing Planners)
---------------------------------------------------------------------------------------

### 何時使用各種規劃器 (When to Use Each Planner)

| 規劃器               | 最適用於                 | 優點                       | 缺點                 |
| -------------------- | ------------------------ | -------------------------- | -------------------- |
| **BuiltInPlanner**   | 複雜的推理任務           | 原生思維、透明、快速       | 僅限 Gemini 2.0+     |
| **PlanReActPlanner** | 多步驟工作流程           | 結構化、可重新規劃、可調試 | 較為冗長             |
| **BasePlanner (自訂)** | 特定領域的邏輯         | 完全控制、量身定制         | 實作工作量較大       |
| **無規劃器**         | 簡單的查詢               | 快速、最小的開銷           | 無結構化推理         |

### 決策樹 (Decision Tree)

```
需要規劃嗎？
├─ 否 → 使用預設（無規劃器）
└─ 是 → 哪種類型？
    ├─ 想要原生模型思維？
    │   └─ 是 → BuiltInPlanner (Gemini 2.0+)
    ├─ 需要結構化步驟？
    │   └─ 是 → PlanReActPlanner
    ├─ 特定領域的工作流程？
    │   └─ 是 → 自訂 BasePlanner
    └─ 通用目的？
        └─ PlanReActPlanner (最靈活)
```

### 性能比較 (Performance Comparison)

```python
import asyncio
import time
from google.adk.agents import Agent, Runner
from google.adk.planners import BuiltInPlanner, PlanReActPlanner
from google.genai import types

async def compare_planners():
    """比較規劃器的性能。"""
    query = "設計一個可持續的城市交通系統"

    # 無規劃器
    agent_default = Agent(
        model='gemini-2.0-flash',
        name='default'
    )
    # BuiltInPlanner
    agent_builtin = Agent(
        model='gemini-2.0-flash',
        name='builtin',
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(include_thoughts=True)
        )
    )
    # PlanReActPlanner
    agent_planreact = Agent(
        model='gemini-2.0-flash',
        name='planreact',
        planner=PlanReActPlanner()
    )

    runner = Runner()
    for agent in [agent_default, agent_builtin, agent_planreact]:
        start = time.time()
        result = await runner.run_async(query, agent=agent)
        elapsed = time.time() - start
        print(f"\n{'='*60}")
        print(f"代理：{agent.name}")
        print(f"時間：{elapsed:.2f}s")
        print(f"回應長度：{len(result.content.parts[0].text)} 字元")
        print(f"{'='*60}")

asyncio.run(compare_planners())
```

**典型結果**：
*   **無規劃器**：2-3 秒，500-800 字元（直接回答）
*   **BuiltInPlanner**：4-6 秒，800-1200 字元（包含思維過程）
*   **PlanReActPlanner**：5-8 秒，1200-2000 字元（結構化）

---

## 6. 最佳實踐 (Best Practices)
---------------------------------------------------------------------------

### ✅ DO：根據任務複雜度選擇規劃器 (Match Planner to Task Complexity)

```python
# ✅ 簡單查詢 - 不需要規劃器
simple_agent = Agent(
    model='gemini-2.0-flash',
    instruction='簡潔地回答問題'
)
runner.run("2+2 是多少？", agent=simple_agent)

# ✅ 複雜問題 - 使用規劃器
complex_agent = Agent(
    model='gemini-2.0-flash',
    instruction='系統性地解決複雜問題',
    planner=PlanReActPlanner()
)
runner.run("設計一個氣候變遷緩解策略", agent=complex_agent)
```

### ✅ DO：適當地使用 `include_thoughts` (Use `include_thoughts` Appropriately)

```python
# ✅ 教育/調試 - 顯示思維過程
educational_agent = Agent(
    model='gemini-2.0-flash',
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(include_thoughts=True)
    )
)

# ✅ 生產環境 - 隱藏思維過程
production_agent = Agent(
    model='gemini-2.0-flash',
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(include_thoughts=False)
    )
)
```

### ✅ DO：為規劃器提供清晰的指令 (Provide Clear Instructions with Planners)

```python
# ✅ 佳 - 清晰的指導
agent = Agent(
    model='gemini-2.0-flash',
    planner=PlanReActPlanner(),
    instruction="""
        你是一個系統性的問題解決者。
        當使用工具時：
        1. 規劃要使用哪些工具以及順序
        2. 解釋你的推理
        3. 執行計畫
        4. 檢視結果
        5. 如有需要則調整計畫
        要詳盡但簡潔。
    """
)

# ❌ 差 - 模糊
agent = Agent(
    model='gemini-2.0-flash',
    planner=PlanReActPlanner(),
    instruction="解決問題"
)
```

### ✅ DO：測試規劃器的開銷 (Test Planner Overhead)

```python
# ✅ 測量影響
import time

# 無規劃器
start = time.time()
result1 = runner.run(query, agent=agent_no_planner)
time1 = time.time() - start

# 有規劃器
start = time.time()
result2 = runner.run(query, agent=agent_with_planner)
time2 = time.time() - start

overhead = ((time2 - time1) / time1) * 100
print(f"規劃器開銷：{overhead:.1f}%")

# 如果品質顯著提升，則接受開銷
```

### ✅ DO：處理規劃失敗 (Handle Planning Failures)

```python
# ✅ 優雅的備用方案
agent_with_fallback = Agent(
    model='gemini-2.0-flash',
    planner=PlanReActPlanner(),
    instruction="""
        遵循規劃格式，但如果遇到困難：
        1. 承認困難
        2. 提供盡力而為的答案
        3. 解釋限制
        不要完全放棄任務。
    """
)
```

---

## 7. 疑難排解 (Troubleshooting)
------------------------------------------------------------------------------

### 問題：「回應中未出現思維過程」 (Issue: "Thinking not appearing in response")

**問題**：使用 BuiltInPlanner 但未顯示思維過程

**解決方案**：

```python
# ❌ 問題 - include_thoughts=False (預設)
agent = Agent(
    model='gemini-2.0-flash',
    planner=BuiltInPlanner()  # 預設 include_thoughts=False
)

# ✅ 解決方案 - 明確設定為 True
agent = Agent(
    model='gemini-2.0-flash',
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(include_thoughts=True)
    )
)

# 檢查模型是否支援思維
# 並非所有 Gemini 2.0 模型都具備思維能力
```

### 問題：「Plan-ReAct 標籤未出現」 (Issue: "Plan-ReAct tags not appearing")

**問題**：回應未遵循結構化格式

**解決方案**：

```python
# 1. 在指令中強調格式
agent = Agent(
    model='gemini-2.0-flash',
    planner=PlanReActPlanner(),
    instruction="""
        重要：你必須使用帶有標籤的結構化格式：
        <PLANNING>, <REASONING>, <ACTION>, <FINAL_ANSWER>
        不要偏離此格式。
    """
)

# 2. 提高溫度以增加規劃的創造力
agent = Agent(
    model='gemini-2.0-flash',
    planner=PlanReActPlanner(),
    generate_content_config=types.GenerateContentConfig(
        temperature=0.7  # 較高溫度以進行創造性規劃
    )
)
```

### 問題：「規劃器增加過多延遲」 (Issue: "Planner adds too much latency")

**問題**：使用規劃器後回應太慢

**解決方案**：

```python
# 1. 減少 max_output_tokens
agent = Agent(
    model='gemini-2.0-flash',
    planner=PlanReActPlanner(),
    generate_content_config=types.GenerateContentConfig(
        max_output_tokens=1024  # 降低上限
    )
)

# 2. 使用串流以改善使用者體驗
from google.adk.agents import RunConfig, StreamingMode
run_config = RunConfig(streaming_mode=StreamingMode.SSE)
async for event in runner.run_async(query, agent=agent, run_config=run_config):
    print(event.content.parts[0].text, end='', flush=True)

# 3. 僅對複雜查詢使用規劃器
def needs_planning(query: str) -> bool:
    complex_keywords = ['設計', '計畫', '策略', '分析', '比較']
    return any(kw in query.lower() for kw in complex_keywords)

agent = agent_with_planner if needs_planning(query) else agent_without_planner
```

### 問題：「未觸發重新規劃」 (Issue: "Replanning not triggered")

**問題**：代理在遇到問題時未調整計畫

**解決方案**：

```python
# 1. 明確的重新規劃指令
agent = Agent(
    model='gemini-2.0-flash',
    planner=PlanReActPlanner(),
    instruction="""
        當你遇到錯誤或意外結果時：
        1. 使用 <OBSERVATION> 記錄出錯的地方
        2. 使用 <REPLANNING> 建立新計畫
        3. 解釋為何需要重新規劃
        絕不放棄 - 永遠要調整你的方法。
    """
)

# 2. 強制重新規劃的工具
def check_and_report(condition: bool, error_msg: str) -> str:
    if not condition:
        return f"錯誤：{error_msg}。需要重新規劃。"
    return "成功"

agent = Agent(
    model='gemini-2.0-flash',
    planner=PlanReActPlanner(),
    tools=[FunctionTool(check_and_report)]
)
```

---

## 8. 測試規劃器 (Testing Planners)
---------------------------------------------------------------------------------

### 單元測試 (Unit Tests)

```python
import pytest
from google.adk.agents import Agent, Runner
from google.adk.planners import BuiltInPlanner, PlanReActPlanner
from google.genai import types

@pytest.mark.asyncio
async def test_builtin_planner_shows_thinking():
    """測試當 include_thoughts=True 時是否顯示思維過程。"""
    agent = Agent(
        model='gemini-2.0-flash',
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(include_thoughts=True)
        )
    )
    runner = Runner()
    result = await runner.run_async(
        "解釋量子糾纏",
        agent=agent
    )
    text = result.content.parts[0].text.lower()
    # 應包含思維標記
    assert any(word in text for word in ['thinking', 'reasoning', 'consider'])

@pytest.mark.asyncio
async def test_planreact_planner_structure():
    """測試 Plan-ReAct 規劃器是否產生結構化輸出。"""
    agent = Agent(
        model='gemini-2.0-flash',
        planner=PlanReActPlanner()
    )
    runner = Runner()
    result = await runner.run_async(
        "建立一個學習 Python 的三步驟計畫",
        agent=agent
    )
    text = result.content.parts[0].text
    # 應包含規劃標籤
    assert '<PLANNING>' in text or '<PLAN>' in text
    assert '<REASONING>' in text or '<FINAL_ANSWER>' in text

@pytest.mark.asyncio
async def test_planner_improves_complex_task():
    """測試規劃器是否能提升複雜任務的品質。"""
    complex_query = "設計一個用於詐欺偵測的機器學習系統"
    # 無規劃器
    agent_no_planner = Agent(
        model='gemini-2.0-flash',
        name='no_planner'
    )
    # 有規劃器
    agent_with_planner = Agent(
        model='gemini-2.0-flash',
        name='with_planner',
        planner=PlanReActPlanner()
    )
    runner = Runner()
    result_no_planner = await runner.run_async(complex_query, agent=agent_no_planner)
    result_with_planner = await runner.run_async(complex_query, agent=agent_with_planner)
    # 有規劃的回應應更全面
    assert len(result_with_planner.content.parts[0].text) > len(result_no_planner.content.parts[0].text)
    # 有規劃的回應應提及關鍵的機器學習概念
    planner_text = result_with_planner.content.parts[0].text.lower()
    ml_concepts = ['training', 'model', 'features', 'validation', 'accuracy']
    concepts_mentioned = sum(1 for concept in ml_concepts if concept in planner_text)
    assert concepts_mentioned >= 3  # 應至少提及 3 個機器學習概念
```

---

## 總結 (Summary)
---------------------------------------------

您已掌握使用規劃器和思維設定的進階推理能力：

**重點回顧**：
*   ✅ `BuiltInPlanner` 使用 Gemini 2.0+ 的原生思維能力進行透明推理
*   ✅ `ThinkingConfig` 控制是否顯示思維過程 (`include_thoughts`)
*   ✅ `PlanReActPlanner` 提供結構化的 Plan → Reason → Act → Observe → Replan 流程
*   ✅ 規劃標籤（`<PLANNING>`, `<REASONING>`, `<ACTION>` 等）結構化輸出
*   ✅ `BasePlanner` 能夠建立自訂規劃策略
*   ✅ 規劃器會增加延遲，但能提升複雜任務的品質
*   ✅ 根據任務複雜度和需求選擇規劃器

**生產環境檢查清單**：
*   [ ] 為任務複雜度選擇合適的規劃器
*   [ ] 正確設定 ThinkingConfig（根據使用案例顯示/隱藏）
*   [ ] 為規劃行為提供清晰的指令
*   [ ] 測試規劃器開銷與品質提升的權衡
*   [ ] 處理規劃失敗的備用方案
*   [ ] 如果延遲是個問題，啟用串流
*   [ ] 模型支援規劃功能（Gemini 2.0+）



**資源**：
*   [ADK Planners Documentation](https://google.github.io/adk-docs/agents/planners/)
*   [Gemini Thinking Guide](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/gemini)
*   [Plan-ReAct Pattern](https://arxiv.org/abs/2210.03629)

---

## 程式碼實現 (Code Implementation)
- strategic_solver：[程式碼連結](../../../python/agents/strategic-solver/)

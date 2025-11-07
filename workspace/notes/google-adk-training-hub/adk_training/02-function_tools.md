# Tutorial 02: Function Tools - 賦予你的 Agent 超能力

> **💡 工作實現**: 查看完整且經過測試的程式碼，請前往 [`tutorial_implementation/tutorial02/`](https://github.com/raphaelmansuy/adk_training/tree/main/tutorial_implementation/tutorial02/)

## 總覽 (Overview)

將您的 Agent 從一個對話者轉變為一個問題解決者！在本教學中，您將學習如何透過新增 Python 函式作為工具，賦予您的 Agent 自訂能力。您的 Agent 將根據使用者請求自動決定何時使用這些工具。

## 先決條件 (Prerequisites)

- **完成教學 01** - 您應該有一個可運作的 hello agent
- **Python 函式知識** - 理解函式定義、參數和回傳值
- **已安裝 ADK** - `pip install google-adk`
- **已設定 API 金鑰** - 來自教學 01

## 核心概念 (Core Concepts)

### 函式工具 (Function Tools)

**函式工具**是您提供給 Agent 的一般 Python 函式。當 Agent 需要執行特定任務時，可以呼叫這些函式。ADK 會自動：

- 讀取您的函式簽章（參數、型別、預設值）
- 讀取您的文件字串（docstring）（函式的功能）
- 產生一個 LLM 可以理解的結構描述
- 讓 LLM 決定何時呼叫您的函式

### 工具探索 (Tool Discovery)

**LLM 非常聰明** - 它會讀取您函式的名稱、文件字串和參數，然後根據使用者的請求決定是否應該呼叫該函式。您不需要手動觸發工具！

### 回傳值 (Return Values)

工具應回傳**字典**，包含：

- `"status"`: `"success"` 或 `"error"`
- `"report"`: 實際結果或錯誤訊息

這有助於 LLM 理解發生了什麼事。

## 使用案例 (Use Case)

我們正在建立一個**個人理財助理**，它可以：

- 計算儲蓄的複利
- 計算每月貸款還款金額
- 確定為達成目標每月需儲蓄多少錢
- 解釋金融概念

這展示了真實世界的工具使用 - LLM 無法自行準確完成的計算！

## 步驟 1: 建立專案結構 (Step 1: Create Project Structure)

為理財助理建立一個新目錄：

```bash
mkdir finance_assistant
cd finance_assistant
touch __init__.py agent.py .env
```

從教學 01 複製您的 `.env` 檔案，或用您的 API 金鑰建立它。

## 步驟 2: 設定套件匯入 (Step 2: Set Up Package Import)

**finance_assistant/**init**.py**

```python
from . import agent
```

## 步驟 3: 定義工具函式 (Step 3: Define Tool Functions)

現在是有趣的部分 - 建立執行實際計算的 Python 函式！

**finance_assistant/agent.py**

```python
from __future__ import annotations
from google.adk.agents import Agent

# 工具 1: 計算複利
def calculate_compound_interest(
    principal: float,
    annual_rate: float,
    years: int,
    compounds_per_year: int = 1
) -> dict:
    """
    計算儲蓄或投資的複利。
    此函式計算初始投資在複利作用下隨時間增長的情況。
    它使用標準複利公式：A = P(1 + r/n)^(nt)

    Args:
        principal: 初始投資金額 (例如, 10000 代表 $10,000)
        annual_rate: 年利率，以小數表示 (例如, 0.06 代表 6%)
        years: 複利計算的年數
        compounds_per_year: 每年複利計算的次數 (預設為 1，代表每年一次)

    Returns:
        包含計算結果和格式化報告的字典

    Example:
        >>> calculate_compound_interest(10000, 0.06, 5)
        {
            'status': 'success',
            'final_amount': 13488.50,
            'interest_earned': 3488.50,
            'report': '經過 5 年，在 6% 的年利率下...'
        }
    """
    try:
        # 驗證輸入
        if principal <= 0:
            return {
                'status': 'error',
                'error': 'Principal must be positive',
                'report': '錯誤：投資本金必須大於零。'
            }
        if annual_rate < 0 or annual_rate > 1:
            return {
                'status': 'error',
                'error': 'Invalid interest rate',
                'report': '錯誤：年利率必須介於 0 和 1 之間 (例如, 0.06 代表 6%)。'
            }
        if years <= 0:
            return {
                'status': 'error',
                'error': 'Invalid time period',
                'report': '錯誤：投資期間必須為正數。'
            }
        # 計算複利
        rate_per_period = annual_rate / compounds_per_year
        total_periods = years * compounds_per_year
        final_amount = principal * (1 + rate_per_period) ** total_periods
        interest_earned = final_amount - principal
        # 格式化易於閱讀的報告
        report = (
            f"經過 {years} 年，在 {annual_rate*100:.1f}% 的年利率下 "
            f"(每年複利 {compounds_per_year} 次), "
            f"您的 ${principal:,.0f} 投資將增長至 "
            f"${final_amount:,.2f}。這表示利息收入為 ${interest_earned:,.2f}！"
        )
        return {
            'status': 'success',
            'final_amount': round(final_amount, 2),
            'interest_earned': round(interest_earned, 2),
            'report': report
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'report': f'計算複利時發生錯誤: {str(e)}'
        }

# 工具 2: 計算貸款還款
def calculate_loan_payment(
    loan_amount: float,
    annual_rate: float,
    years: int
) -> dict:
    """
    使用標準攤銷公式計算每月貸款還款金額。
    此函式計算在給定利率下，於指定期間內還清貸款所需的每月還款金額。
    它使用公式：M = P[r(1+r)^n]/[(1+r)^n-1]，其中 r 是月利率，n 是總月數。

    Args:
        loan_amount: 總貸款金額 (例如, 300000 代表 $300,000)
        annual_rate: 年利率，以小數表示 (例如, 0.045 代表 4.5%)
        years: 貸款年限

    Returns:
        包含還款計算結果和格式化報告的字典

    Example:
        >>> calculate_loan_payment(300000, 0.045, 30)
        {
            'status': 'success',
            'monthly_payment': 1520.06,
            'total_paid': 547221.60,
            'total_interest': 247221.60,
            'report': '對於一筆 $300,000 的貸款，利率 4.5%，為期 30 年...'
        }
    """
    try:
        # 驗證輸入
        if loan_amount <= 0:
            return {
                'status': 'error',
                'error': 'Invalid loan amount',
                'report': '錯誤：貸款金額必須為正數。'
            }
        if annual_rate < 0 or annual_rate > 1:
            return {
                'status': 'error',
                'error': 'Invalid interest rate',
                'report': '錯誤：年利率必須介於 0 和 1 之間 (例如, 0.045 代表 4.5%)。'
            }
        if years <= 0:
            return {
                'status': 'error',
                'error': 'Invalid loan term',
                'report': '錯誤：貸款年限必須為正數。'
            }
        # 轉換為每月計算
        monthly_rate = annual_rate / 12
        total_months = years * 12
        # 處理零利率情況
        if monthly_rate == 0:
            monthly_payment = loan_amount / total_months
            total_paid = loan_amount
            total_interest = 0
        else:
            # 標準貸款還款公式
            monthly_payment = loan_amount * (
                monthly_rate * (1 + monthly_rate) ** total_months
            ) / ((1 + monthly_rate) ** total_months - 1)
            total_paid = monthly_payment * total_months
            total_interest = total_paid - loan_amount
        # 格式化易於閱讀的報告
        report = (
            f"對於一筆 ${loan_amount:,.0f} 的貸款，利率 {annual_rate*100:.1f}%，為期 {years} 年，"
            f"您的每月還款金額為 ${monthly_payment:,.2f}。在貸款期間，您總共將支付 "
            f"${total_paid:,.2f}，其中 ${total_interest:,.2f} 為利息。"
        )
        return {
            'status': 'success',
            'monthly_payment': round(monthly_payment, 2),
            'total_paid': round(total_paid, 2),
            'total_interest': round(total_interest, 2),
            'report': report
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'report': f'計算貸款還款時發生錯誤: {str(e)}'
        }

# 工具 3: 計算所需儲蓄
def calculate_monthly_savings(
    target_amount: float,
    years: int,
    annual_return: float = 0.05
) -> dict:
    """
    計算達成財務目標所需的每月儲蓄金額。
    此函式確定您每月需要儲蓄多少錢才能達成儲蓄目標，假設在指定的年回報率下有複利增長。
    它使用年金現值公式重新排列以計算支付金額。

    Args:
        target_amount: 目標儲蓄金額 (例如, 50000 代表 $50,000)
        years: 儲蓄年數
        annual_return: 預期年回報率，以小數表示 (預設為 0.05，代表 5%)

    Returns:
        包含儲蓄計算結果和格式化報告的字典

    Example:
        >>> calculate_monthly_savings(50000, 3, 0.05)
        {
            'status': 'success',
            'monthly_savings': 1315.07,
            'total_contributed': 47342.52,
            'interest_earned': 2657.48,
            'report': '要在 3 年內達到 $50,000，年回報率為 5%...'
        }
    """
    try:
        # 驗證輸入
        if target_amount <= 0:
            return {
                'status': 'error',
                'error': 'Invalid target amount',
                'report': '錯誤：儲蓄目標必須為正數。'
            }
        if years <= 0:
            return {
                'status': 'error',
                'error': 'Invalid time period',
                'report': '錯誤：儲蓄期間必須為正數。'
            }
        if annual_return < 0:
            return {
                'status': 'error',
                'error': 'Invalid return rate',
                'report': '錯誤：年回報率不能為負數。'
            }
        # 轉換為每月計算
        monthly_return = annual_return / 12
        total_months = years * 12
        # 處理零回報率情況
        if monthly_return == 0:
            monthly_savings = target_amount / total_months
            total_contributed = target_amount
            interest_earned = 0
        else:
            # 計算每月儲蓄以達到未來價值的正確公式
            # PMT = FV * (r / ((1 + r)^n - 1)) 其中 r 是月利率，n 是總月數
            monthly_savings = target_amount * (
                monthly_return / ((1 + monthly_return) ** total_months - 1)
            )
            total_contributed = monthly_savings * total_months
            # 計算實際未來價值以進行驗證
            future_value = 0
            for month in range(1, total_months + 1):
                future_value += monthly_savings * (1 + monthly_return) ** (total_months - month)
            interest_earned = future_value - total_contributed
        # 格式化易於閱讀的報告
        report = (
            f"要在 {years} 年內達到 ${target_amount:,.0f}，且年回報率為 "
            f"{annual_return*100:.1f}%，您需要每月儲蓄 "
            f"${monthly_savings:,.2f}。您總共將貢獻 "
            f"${total_contributed:,.2f}，其餘部分來自投資回報。"
        )
        return {
            'status': 'success',
            'monthly_savings': round(monthly_savings, 2),
            'total_contributed': round(total_contributed, 2),
            'interest_earned': round(interest_earned, 2),
            'report': report
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'report': f'計算每月儲蓄時發生錯誤: {str(e)}'
        }

# 使用所有工具定義 agent
root_agent = Agent(
    name="finance_assistant",
    model="gemini-1.5-flash",
    description="""
    一個財務計算助理，可以協助：
    - 投資的複利計算
    - 房貸或其他貸款的還款計算
    - 為達成財務目標的每月儲蓄計算
    我可以同時執行多個計算以進行比較。
    所有計算都包含詳細的解釋和格式化的報告。
    """,
    instruction=(
        "您是一位有幫助的個人理財助理。您可以協助使用者：\n"
        "- 計算儲蓄和投資的複利\n"
        "- 計算貸款（房貸、車貸等）的每月還款金額\n"
        "- 確定為達成財務目標每月需儲蓄多少錢\n"
        "\n"
        "當使用者提出財務問題時：\n"
        "1. 使用適當的計算工具\n"
        "2. 用簡單的語言解釋結果\n"
        "3. 在相關時提供背景和建議\n"
        "4. 對他們的財務規劃保持鼓勵和積極的態度！\n"
        "\n"
        "您不是持牌理財顧問 - 提醒使用者在做出重大決定時諮詢專業人士。"
    ),
    tools=[calculate_compound_interest, calculate_loan_payment, calculate_monthly_savings]
)
```

### 程式碼分解 (Code Breakdown)

**函式簽章最佳實踐：**

1.  **型別提示** - `principal: float`, `years: int` - 告訴 LLM 要使用什麼型別
2.  **清晰的參數名稱** - `annual_rate` 而不只是 `rate`
3.  **可選參數的預設值** - `compounds_per_year: int = 12`
4.  **全面的文件字串** - 解釋函式的**功能**以及**何時**使用它

**回傳值模式：**

```python
return {
    "status": "success",  # 或 "error"
    "report": "人類可讀的結果"  # 或錯誤時的 "error_message"
}
```

這種結構化格式有助於 LLM 理解發生了什麼並產生更好的回應。

**工具註冊：** 注意我們只是將函式直接傳遞給 `tools=[...]` - ADK 會自動將它們轉換為工具！

## 步驟 4: 執行您的理財助理 (Step 4: Run Your Finance Assistant)

導覽至父目錄並啟動開發 UI：

```bash
cd ..  # 前往 finance_assistant/ 的父目錄
adk web
```

打開 `http://localhost:8000` 並從下拉式選單中選擇 "finance_assistant"。

### 示範操作 (Demo in Action)

以下是您的理財助理的實際操作畫面：

![Tutorial 02 Demo - Function Tools Finance Assistant](https://raphaelmansuy.github.io/adk_training/assets/images/tutorial02_cap01-34f8c224e0e441ff1bb36c1935f6fbf0.gif)

### 替代方案：平行執行示範 (Alternative: Parallel Execution Demo)

若要進行展示 ADK 自動平行工具執行的高階示範，請嘗試平行示範：

```bash
cd ..  # 前往 finance_assistant/ 的父目錄
make parallel-demo
```

這會執行相同的財務工具，但展示了當 Gemini 在單一回合中請求多個工具時，ADK 如何自動同時執行它們。非常適合比較多個投資選項或分析不同的貸款情境！

### 嘗試這些提示 (Try These Prompts)

**儲蓄計算：**

> 如果我投資 $10,000，年利率 0.06，為期 5 年，我將擁有多少錢？

**貸款還款：**

> 我想買一棟 $300,000 的房子，貸款 30 年，利率 0.045。我的每月還款金額是多少？

**儲蓄目標：**

> 我想在 3 年內存下 $50,000 作為頭期款。我每個月應該存多少錢？

**混合問題（LLM 決定不使用工具）：**

> 羅斯 IRA 和傳統 IRA 有什麼區別？

注意最後一個問題 - Agent **不會**呼叫任何工具，因為沒有一個工具能幫助回答這個問題。LLM 將只使用其知識！

## 了解工具執行 (Understanding Tool Execution)

在發送訊息後，打開開發 UI 中的 **Events 標籤**。您會看到：

1.  **User Message**: 您的原始問題
2.  **Function Call Event**: 顯示哪個工具被呼叫以及使用了什麼參數
3.  **Function Response Event**: 顯示工具回傳了什麼
4.  **Model Response**: 結合工具結果與解釋的最終答案

這對於除錯非常強大 - 您可以**確切地**看到工具是何時以及如何被使用的！

## 預期行為 (Expected Behavior)

**範例 1: 儲蓄計算**

> **使用者**: 如果我投資 $10,000，年利率 0.06，為期 5 年，我將擁有多少錢？
> **Agent**: 讓我為您計算一下！
> [工具呼叫: calculate_compound_interest(principal=10000, annual_rate=0.06, years=5)]
> 根據計算，如果您投資 $10,000，年利率 6%，每月複利，為期 5 年，您將擁有約 $13,488.50。這意味著您將賺取 $3,488.50 的利息 - 還不錯！這假設利息每月複利，這在儲蓄帳戶和許多投資工具中很常見。

**範例 2: 不需要工具**

> **使用者**: 我應該投資股票還是債券？
> **Agent**: 這是個關於投資策略的好問題！股票和債券之間的選擇取決於幾個因素：您的年齡、風險承受能力、財務目標和時間範圍...
> [未呼叫工具 - LLM 只使用其知識]

## 運作原理（幕後花絮）(How It Works (Behind the Scenes))

1.  **使用者發送訊息** → ADK 接收它
2.  **ADK 將訊息打包**，包含：
    - 您的 Agent 的指示
    - 工具結構描述（從您的函式簽章產生）
3.  **Gemini (LLM) 決定**：「我需要為此使用工具嗎？」
    - **是** → 回傳一個函式呼叫請求
    - **否** → 回傳一個文字回應
4.  **如果需要工具**，ADK：
    - 使用 Gemini 提供的參數執行您的 Python 函式
    - 取得回傳值
    - 將其傳回給 Gemini
5.  **Gemini 使用工具結果**產生最終回應

**您從不手動呼叫工具** - LLM 會自動完成！

## 🚀 進階：平行工具呼叫 (Advanced: Parallel Tool Calling)

**來源**: `google/adk/flows/llm_flows/functions.py`

ADK 最強大的功能之一是**自動平行工具執行**。當 LLM 在單一回合中請求多個工具時，ADK 會使用 `asyncio.gather()` **同時**執行它們 - 大幅提升效能！

### 運作原理 (How It Works)

當 Gemini 決定呼叫多個工具時，而不是一個接一個地執行：

```python
# ❌ 循序執行 (慢)
result1 = await tool1()  # 等待...
result2 = await tool2()  # 等待...
result3 = await tool3()  # 等待...
# 總時間: ~6 秒

# ✅ 平行執行 (快) - ADK 自動完成！
results = await asyncio.gather(tool1(), tool2(), tool3())
# 總時間: ~2 秒 (受限於最慢的工具)
```

**您不需要做任何事** - ADK 會自動處理！只需正常定義您的工具。

### 真實世界範例：多城市財務規劃 (Real-World Example: Multi-City Financial Planning)

讓我們擴展我們的理財助理以處理平行計算：

```python
from __future__ import annotations
import asyncio
from google.adk.agents import Agent

def calculate_compound_interest(
    principal: float,
    annual_rate: float,
    years: int,
    compounds_per_year: int = 12
) -> dict:
    """計算儲蓄或投資的複利。
    Args:
        principal: 初始投資金額 (美元)
        annual_rate: 年利率，以百分比表示 (例如, 5.5 代表 5.5%)
        years: 計算年數
        compounds_per_year: 每年複利次數 (預設: 12)
    Returns:
        dict: 包含狀態和計算結果的字典
    """
    # 新增模擬延遲以顯示平行執行的好處
    import time
    time.sleep(0.5)  # 模擬 API 呼叫或大量計算
    rate_decimal = annual_rate / 100
    final_amount = principal * (1 + rate_decimal / compounds_per_year) ** (compounds_per_year * years)
    interest_earned = final_amount - principal
    return {
        "status": "success",
        "report": (
            f"投資: ${principal:,.2f}\n"
            f"最終金額: ${final_amount:,.2f}\n"
            f"利息收入: ${interest_earned:,.2f}"
        )
    }

def calculate_loan_payment(
    loan_amount: float,
    annual_rate: float,
    years: int
) -> dict:
    """計算貸款的每月還款金額。"""
    import time
    time.sleep(0.5)  # 模擬處理
    monthly_rate = (annual_rate / 100) / 12
    num_payments = years * 12
    if monthly_rate == 0:
        monthly_payment = loan_amount / num_payments
    else:
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    return {
        "status": "success",
        "report": f"每月還款: ${monthly_payment:,.2f}"
    }

def calculate_monthly_savings(
    target_amount: float,
    years: int,
    annual_return: float = 5.0
) -> dict:
    """計算達成目標所需的每月儲蓄金額。"""
    import time
    time.sleep(0.5)  # 模擬計算
    months = years * 12
    monthly_rate = (annual_return / 100) / 12
    if monthly_rate == 0:
        monthly_savings = target_amount / months
    else:
        monthly_savings = target_amount / (((1 + monthly_rate)**months - 1) / monthly_rate)
    return {
        "status": "success",
        "report": f"每月儲蓄 ${monthly_savings:,.2f}"
    }

root_agent = Agent(
    name="parallel_finance_assistant",
    model="gemini-1.5-flash",  # 支援平行工具呼叫！
    description="具有平行計算功能的理財助理",
    instruction=(
        "您是一位理財規劃助理。當使用者詢問多個情境或計算時，"
        "請一次性呼叫所有必要的工具以提高效率。"
        "例如，如果比較投資選項，請同時為每個選項呼叫計算工具。"
    ),
    tools=[
        calculate_compound_interest,
        calculate_loan_payment,
        calculate_monthly_savings
    ]
)
```

### 嘗試此提示（觸發平行執行）(Try This Prompt (Triggers Parallel Execution))

> 幫我比較這三個投資選項：
>
> 1. $10,000，利率 0.05，為期 10 年
> 2. $15,000，利率 0.04，為期 10 年
> 3. $12,000，利率 0.06，為期 10 年

**會發生什麼事**：

1.  Gemini 辨識出需要呼叫 `calculate_compound_interest` **三次**
2.  ADK 從 Gemini 接收到**三個** `FunctionCall` 物件
3.  ADK 使用 `asyncio.gather()` **同時**執行這三個呼叫
4.  所有結果在約 0.5 秒內回傳，而不是約 1.5 秒（循序執行）
5.  Gemini 接收所有結果並產生比較分析

### 效能比較 (Performance Comparison)

**循序執行**（如果您手動執行）：

```python
# ❌ 慢速方法 (ADK 不是這樣運作的)
result1 = calculate_compound_interest(10000, 0.05, 10)   # 0.5s
result2 = calculate_compound_interest(15000, 0.04, 10)   # 0.5s
result3 = calculate_compound_interest(12000, 0.06, 10)   # 0.5s
# 總計: ~1.5 秒
```

**平行執行**（ADK 自動）：

```python
# ✅ 快速 - ADK 為您完成！
results = await asyncio.gather(
    calculate_compound_interest(10000, 0.05, 10),
    calculate_compound_interest(15000, 0.04, 10),
    calculate_compound_interest(12000, 0.06, 10)
)
# 總計: ~0.5 秒 (受限於最慢的工具)
```

**加速**：3 個平行工具，速度提升 3 倍！

### 範例輸出 (Example Output)

> **使用者**: 幫我比較這三個投資選項：
>
> 1. $10,000，利率 0.05，為期 10 年
> 2. $15,000，利率 0.04，為期 10 年
> 3. $12,000，利率 0.06，為期 10 年
>    **Agent**: 讓我為您計算這三個選項...
>    [工具呼叫 - 同時執行]:
>
> - calculate_compound_interest(principal=10000, annual_rate=0.05, years=10)
> - calculate_compound_interest(principal=15000, annual_rate=0.04, years=10)
> - calculate_compound_interest(principal=12000, annual_rate=0.06, years=10)
>
> 好問題！以下是您三個投資選項的比較：
>
> **選項 1**: $10,000，利率 5%，為期 10 年
>
> - 最終金額: $16,470.09
> - 利息收入: $6,470.09
>
> **選項 2**: $15,000，利率 4%，為期 10 年
>
> - 最終金額: $22,280.97
> - 利息收入: $7,280.97
>
> **選項 3**: $12,000，利率 6%，為期 10 年
>
> - 最終金額: $21,791.23
> - 利息收入: $9,791.23
>
> 選項 3 帶給您最高的回報（$9,791.23 的利息），即使本金比選項 2 低。那額外的 2% 利率在 10 年內產生了很大的差異！

### 何時會發生平行執行？ (When Does Parallel Execution Happen?)

當以下情況發生時，會進行平行執行：

✅ **單一回合中有多個工具呼叫** - Gemini 決定一次呼叫 2 個以上的工具
✅ **工具是獨立的** - 結果不互相依賴
✅ **模型支援平行呼叫** - Gemini 1.5-flash, 1.5-pro, 1.0-pro 支援此功能

**不會**在以下情況發生：
❌ **循序依賴** - 工具 B 需要工具 A 的結果
❌ **單一工具呼叫** - 只調用一個工具
❌ **手動循序指示** - 您明確告訴模型逐步執行

### 為平行執行進行優化 (Optimizing for Parallel Execution)

**✅ 應該做：設計獨立的工具**

```python
# 好 - 這些可以平行執行
def get_weather(city: str): ...
def get_exchange_rate(currency: str): ...
def get_stock_price(symbol: str): ...

# 使用者: "東京的天氣、歐元/美元匯率和蘋果股價是多少？"
# → 全部 3 個同時執行！
```

**❌ 不應該做：建立依賴關係**

```python
# 不好 - 這會產生依賴鏈
def search_database(query: str) -> dict:
    """尋找資料庫記錄。"""
    return {"status": "success", "record_id": "123"}

def fetch_record_details(record_id: str) -> dict:
    """取得記錄的完整詳細資訊（需要先有 record_id）。"""
    return {"status": "success", "details": "..."}

# 這些必須循序執行 - 無法平行化
```

### 驗證：檢查 Events 標籤 (Verification: Check the Events Tab)

在發送多工具查詢後，打開開發 UI 的 Events 標籤。尋找：

```
[FunctionCall] calculate_compound_interest(principal=10000, ...)
[FunctionCall] calculate_compound_interest(principal=15000, ...)
[FunctionCall] calculate_compound_interest(principal=12000, ...)
[FunctionResponse] result for 10000
[FunctionResponse] result for 15000
[FunctionResponse] result for 12000
```

注意所有 `FunctionCall` 事件都在任何 `FunctionResponse` **之前**發出 - 證明它們是平行執行的！

### 原始碼參考 (Source Code Reference)

平行執行的實作位於 `google/adk/flows/llm_flows/functions.py`：

```python
# ADK 內部運作的簡化版本
async def execute_function_calls(calls: list[FunctionCall]):
    """平行執行多個函式呼叫。"""
    tasks = [execute_single_function(call) for call in calls]
    results = await asyncio.gather(*tasks)
    return results
```

**您免費獲得此功能** - 只需正常定義您的工具！

### 效能提示 (Performance Tips)

1.  **對於 I/O 密集型工具**（API 呼叫、資料庫查詢）：
    - 平行執行提供**巨大的速度提升**（3-10 倍）
    - 每個工具等待網路，而不是 CPU
2.  **對於 CPU 密集型工具**（計算、資料處理）：
    - 如果工具是獨立的，平行執行仍然有幫助
    - Python GIL 限制了純 CPU 平行處理，但 asyncio 排程仍然提高了響應性
3.  **混合工作負載**（一些 I/O，一些 CPU）：
    - I/O 工具在 CPU 工具執行期間完成
    - 兩全其美！

### 進階範例：多來源資料聚合 (Advanced Example: Multi-Source Data Aggregation)

```python
def get_market_data(symbol: str) -> dict:
    """取得股市資料（模擬 API 呼叫）。"""
    import time
    time.sleep(1.0)  # 模擬 API 延遲
    return {
        "status": "success",
        "report": f"{symbol}: $150.32 (+2.1%)"
    }

def get_company_news(symbol: str) -> dict:
    """取得公司的最新消息（模擬 API 呼叫）。"""
    import time
    time.sleep(1.2)  # 模擬 API 延遲
    return {
        "status": "success",
        "report": f"{symbol} 宣布第四季度財報超預期"
    }

def get_analyst_ratings(symbol: str) -> dict:
    """取得分析師評級（模擬 API 呼叫）。"""
    import time
    time.sleep(0.8)  # 模擬 API 延遲
    return {
        "status": "success",
        "report": f"{symbol}: 12 買入, 3 持有, 1 賣出"
    }

aggregator_agent = Agent(
    name="market_aggregator",
    model="gemini-1.5-flash",
    description="從多個來源聚合市場數據",
    instruction="當被問及股票時，同時取得所有相關數據。",
    tools=[get_market_data, get_company_news, get_analyst_ratings]
)

# 查詢: "告訴我關於 AAPL 的一切"
# → 所有 3 個工具平行執行 (總共約 1.2 秒，而循序執行約 3 秒)
```

### 範例參考 (Sample Reference)

查看 `contributing/samples/parallel_functions/agent.py` 以獲得平行工具執行的完整工作範例。

## 關鍵要點 (Key Takeaways)

✅ **工具只是 Python 函式** - 不需要特殊的類別，只需常規函式！
✅ **LLM 決定何時使用工具** - 您不手動觸發它們。LLM 讀取文件字串並決定。
✅ **平行執行是自動的** - 當呼叫多個工具時，ADK 會透過 `asyncio.gather()` 同時執行它們。
✅ **型別提示至關重要** - 它們告訴 LLM 參數要使用什麼資料型別。
✅ **文件字串 = 工具描述** - 編寫清晰的文件字串，解釋**何時**以及**如何**使用工具。
✅ **回傳帶有狀態的字典** - 使用 `{"status": "success", "report": "..."}` 模式以求清晰。
✅ **預設參數 = 可選** - 具有預設值的函式可以在沒有這些參數的情況下被呼叫。
✅ **Events 標籤是您的除錯好幫手** - 查看每個工具呼叫、參數和回應（並驗證平行執行！）。
✅ **工具擴展了 LLM 的能力** - 使用工具進行計算、API 呼叫、資料庫查詢 - 任何 LLM 無法單獨完成的事情。
✅ **為獨立性而設計** - 不互相依賴的工具可以實現平行執行和更好的效能。

## 最佳實踐 (Best Practices)

**應該做：**

- 編寫描述性的函式名稱（`calculate_compound_interest` 而不是 `calc_int`）
- 包含全面的文件字串
- 為所有參數使用型別提示
- 回傳結構化的字典
- 優雅地處理錯誤
- 保持工具的專注性（一個函式 = 一個任務）

**不應該做：**

- 使用通用名稱（`process_data`, `do_stuff`）
- 依賴 `*args` 或 `**kwargs` 作為面向 LLM 的參數（它們會被忽略！）
- 回傳複雜的物件（堅持使用字典、字串、數字）
- 讓工具做太多事情
- 忘記處理錯誤情況

## 常見問題 (Common Issues)

**問題**：「工具未被呼叫」

- **檢查**：您的文件字串是否清楚說明了**何時**使用該工具？
- **檢查**：函式名稱是否與使用者所要求的相符？
- **提示**：查看 Events 標籤 - Gemini 是否甚至考慮過該工具？

**問題**：「傳遞了錯誤的參數」

- **檢查**：您的型別提示是否正確？
- **檢查**：您的文件字串是否清楚地描述了參數？
- **嘗試**：在文件字串中新增範例

**問題**：「工具回傳錯誤」

- **檢查**：新增 try/except 區塊以捕捉錯誤
- **回傳**：錯誤狀態字典，而不是引發異常

## 我們建立了什麼 (What We Built)

您現在擁有一個理財助理 Agent，它可以：

- 執行準確的複利計算
- 計算貸款還款
- 規劃儲蓄目標
- 以人性化的語言解釋結果

並且您學會了 ADK 工具在幕後的運作方式！

## 後續步驟 (Next Steps)

🚀 **教學 03: OpenAPI 工具** - 連接到真實的 Web API（天氣、股價、新聞等）

📖 **進一步閱讀**：

- [函式工具文件](https://google.github.io/adk-docs/tools/function-tools/)
- [工具效能（平行執行）](https://google.github.io/adk-docs/tools/performance/)
- [內建工具](https://google.github.io/adk-docs/tools/built-in-tools/)

## 練習（自己試試看！）(Exercises (Try On Your Own!))

1.  **新增預算工具** - 根據收入計算某人是否負擔得起某樣東西
2.  **新增債務還清工具** - 計算還清信用卡債務需要多長時間
3.  **新增退休儲蓄工具** - 估算退休儲蓄需求
4.  **處理更多邊界情況** - 如果有人輸入負數會怎樣？

## 完整程式碼參考 (Complete Code Reference)

**finance_assistant/**init**.py**

```python
from . import agent
```

**finance_assistant/.env**

```
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your-api-key-here
```

**finance_assistant/agent.py**

```python
# 請參閱 tutorial_implementation/tutorial02/finance_assistant/agent.py 的完整實作
# 此檔案包含完整的 agent 程式碼，具有全面的錯誤處理、
# 輸入驗證和詳細的文件字串。
```

恭喜！您的 Agent 現在擁有超能力了！ 🚀💰

## 程式碼實現 (Code Implementation)

- finance-assistant：[程式碼連結](../../../python/agents/finance-assistant/README.md)

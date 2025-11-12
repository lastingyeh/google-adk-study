# 教學 13：程式碼執行 - 動態 Python 程式碼生成 (Tutorial 13: Code Execution - Dynamic Python Code Generation)

## 總覽 (Overview)

**目標**：讓您的代理程式能夠使用 Gemini 2.0+ 內建的程式碼執行功能，編寫並執行 Python 程式碼，以進行計算、資料分析和複雜的運算。

**先決條件**：

*   教學 01 (Hello World 代理程式)
*   教學 02 (函式工具)
*   Gemini 2.0+ 模型存取權限

**您將學到**：

*   使用 `BuiltInCodeExecutor` 進行程式碼生成與執行
*   理解模型端的程式碼執行（無本機執行）
*   建構資料分析代理程式
*   建立計算助理
*   處理程式碼執行錯誤
*   基於程式碼的代理程式最佳實踐

**完成時間**：40-55 分鐘

---

## 🚀 快速入門 (Quick Start)

最快的入門方式是使用我們可運作的實作：

```bash
cd tutorial_implementation/tutorial13
make setup
make dev
```

然後在您的瀏覽器中開啟 `http://localhost:8000` 並選擇 "code_calculator"！

**或探索完整的實作**：[教學 13 實作 (Tutorial 13 Implementation)](https://github.com/raphaelmansuy/adk_training/tree/main/tutorial_implementation/tutorial13)

---

## 為何程式碼執行如此重要 (Why Code Execution Matters)

AI 模型擅長推理，但過去在精確計算方面一直存在困難。**程式碼執行** 透過允許模型進行以下操作來解決這個問題：

*   🧮 **執行精確計算**：沒有近似誤差
*   📊 **分析資料**：處理陣列、統計數據、資料轉換
*   🔬 **解決複雜問題**：多步驟的數學運算
*   📈 **生成視覺化圖表**：以程式碼形式建立圖表
*   ⚡ **執行演算法**：排序、搜尋、最佳化

**沒有程式碼執行**：

```
使用者：「50 的階乘是多少？」
代理程式：「50 的階乘大約是 3.04 × 10^64」
      ↑ 近似值，可能不準確
```

**使用程式碼執行**：

```
使用者：「50 的階乘是多少？」
代理程式：[生成並執行：math.factorial(50)]
       「50 的階乘的精確值是：30414093201713378043612608166064768844377641568960512000000000000」
       ↑ 透過程式碼執行得到的精確答案
```

---

## 基於先前教學的建構 (Building on Previous Tutorials)

程式碼執行代表了從您在教學 02 中學到的函式工具的一次**巨大飛躍**。讓我們看看它是如何建立在先前概念之上的：

### 從教學 01：Hello World 代理程式 (From Tutorial 01: Hello World Agent)

**教學 01** 教您基本的代理程式結構：

```python
# 教學 01 - 基本代理程式
agent = Agent(
    model='gemini-2.0-flash',
    name='hello_agent',
    instruction='你是一個有幫助的助理。'
)
```

**教學 13** 新增了程式碼執行功能：

```python
# 教學 13 - 具備程式碼執行的代理程式
agent = Agent(
    model='gemini-2.0-flash',
    name='calculator',
    instruction='你可以編寫並執行 Python 程式碼。',
    code_executor=BuiltInCodeExecutor()  # ← 新功能
)
```

### 從教學 02：函式工具 (From Tutorial 02: Function Tools)

**教學 02** 展示了如何建立自訂工具：

```python
# 教學 02 - 自訂函式工具
def calculate_square(x: float) -> float:
    """計算一個數字的平方。"""
    return x * x

agent = Agent(
    model='gemini-2.0-flash',
    tools=[FunctionTool(calculate_square)]
)
```

**教學 13** 實現了**動態工具建立**：

```python
# 教學 13 - 動態程式碼生成
agent = Agent(
    model='gemini-2.0-flash',
    code_executor=BuiltInCodeExecutor()
)

# 代理程式現在可以根據需求建立任何數學函式
result = runner.run("建立一個計算複利的函式", agent=agent)

# 代理程式會生成並執行所需的確切程式碼
```

### 演進比較 (Evolution Comparison)

| 層面 | 教學 02 (函式工具) | 教學 13 (程式碼執行) |
| :--- | :--- | :--- |
| **工具建立** | 預先定義的函式 | 動態程式碼生成 |
| **靈活性** | 僅限於已編碼的工具 | 無限的 Python 功能 |
| **準確性** | 取決於實作 | 精確的數學精度 |
| **維護** | 更新程式碼以新增工具 | 代理程式學習新功能 |
| **使用案例** | 特定的業務邏輯 | 任何計算任務 |

### 實例：計算機的演進 (Practical Example: Calculator Evolution)

**之前 (教學 02 風格)**：

```python
# 僅限於預先建立的函式
def add_numbers(a: float, b: float) -> float:
    return a + b

def multiply_numbers(a: float, b: float) -> float:
    return a * b

agent = Agent(
    model='gemini-2.0-flash',
    tools=[FunctionTool(add_numbers), FunctionTool(multiply_numbers)]
)
# 只能做：2+2=4, 3*5=15
```

**之後 (教學 13 風格)**：

```python
# 無限的計算能力
agent = Agent(
    model='gemini-2.0-flash',
    code_executor=BuiltInCodeExecutor()
)
# 可以做任何事情：
# - 矩陣運算
# - 統計分析
# - 演算法實作
# - 複雜的財務計算
# - 科學計算
```

### 現實世界的影響 (Real-World Impact)

**教學 02 代理程式**：「我可以做加法和乘法。」

**教學 13 代理程式**：「我可以解微分方程、執行統計分析、實作機器學習演算法、計算軌道力學、分析金融投資組合等等——所有這些都具有數學上的精確性。」

---

## 1. BuiltInCodeExecutor 基礎 (BuiltInCodeExecutor Basics)

### 什麼是 BuiltInCodeExecutor？ (What is BuiltInCodeExecutor?)

`BuiltInCodeExecutor` 讓 Gemini 2.0+ 模型能夠在模型環境中**生成 Python 程式碼並在內部執行它**。不會發生任何本機程式碼執行——一切都在 Google 的基礎設施內運行。

**來源**：`google/adk/code_executors/built_in_code_executor.py`

### 基本用法 (Basic Usage)

```python
from google.adk.agents import Agent, Runner
from google.adk.code_executors import BuiltInCodeExecutor

# 建立具備程式碼執行功能的代理程式
agent = Agent(
    model='gemini-2.0-flash',  # 需要 Gemini 2.0+
    name='code_executor',
    instruction='你可以編寫並執行 Python 程式碼來解決問題。',
    code_executor=BuiltInCodeExecutor()
)

runner = Runner()
result = runner.run(
    "計算 1 到 100 之間所有質數的總和",
    agent=agent
)

print(result.content.parts[0].text)
```

**輸出**：

```
讓我用 Python 來計算：
[執行的程式碼：]
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

primes = [n for n in range(1, 101) if is_prime(n)]
sum(primes)

[結果：] 1060

1 到 100 之間所有質數的總和是 **1060**。
```

### 它是如何運作的 (How It Works)

**逐步流程**：

1.  **使用者查詢** → 模型接收到計算請求
2.  **程式碼生成** → 模型編寫 Python 程式碼
3.  **程式碼執行** → 程式碼在模型環境中運行（Google 的基礎設施）
4.  **結果整合** → 執行結果被整合到回應中
5.  **最終答案** → 包含解釋的完整答案

**內部實作**：

```python
# 從 built_in_code_executor.py 簡化而來
class BuiltInCodeExecutor(BaseCodeExecutor):
    def process_llm_request(self, llm_request: LlmRequest):
        """將程式碼執行工具新增到請求中。"""
        llm_request.tools.append(
            types.Tool(code_execution=types.ToolCodeExecution())
        )
        return llm_request
```

### 模型相容性 (Model Compatibility)

```python
# ✅ 適用於 Gemini 2.0+
agent = Agent(
    model='gemini-2.0-flash',
    code_executor=BuiltInCodeExecutor()
)
agent = Agent(
    model='gemini-2.0-flash-exp',
    code_executor=BuiltInCodeExecutor()
)

# ❌ 使用 Gemini 1.x 會引發錯誤
agent = Agent(
    model='gemini-1.5-flash',
    code_executor=BuiltInCodeExecutor()
)
# 錯誤：程式碼執行需要 Gemini 2.0+
```

---

## 2. 程式碼執行能力 (Code Execution Capabilities)

### 數學計算 (Mathematical Calculations)

```python
from google.adk.agents import Agent, Runner
from google.adk.code_executors import BuiltInCodeExecutor

math_agent = Agent(
    model='gemini-2.0-flash',
    name='mathematician',
    instruction='使用 Python 程式碼解決數學問題。',
    code_executor=BuiltInCodeExecutor()
)

runner = Runner()

# 複雜計算
result = runner.run(
    "計算 e^(π*i) + 1 並解釋其結果的重要性",
    agent=math_agent
)

print(result.content.parts[0].text)
```

**預期輸出**：

```
讓我使用 Python 的複數支援來計算這個：
[程式碼：]
import cmath
import math

result = cmath.exp(math.pi * 1j) + 1
print(f"結果: {result}")
print(f"實部: {result.real}")
print(f"虛部: {result.imag}")

[輸出：]
結果: 1.2246467991473532e-16j
實部: 1.2246467991473532e-16
虛部: 0.0

結果基本上是 **0**（這個極小的數字是由於浮點數精度造成的）。
這就是**歐拉恆等式**：e^(πi) + 1 = 0
它被認為是數學中最美的方程式之一，因為它連接了五個基本的數學常數：e、π、i、1 和 0。
```

### 資料分析 (Data Analysis)

```python
data_analyst = Agent(
    model='gemini-2.0-flash',
    name='data_analyst',
    instruction='使用 Python 分析資料。計算統計數據並識別模式。',
    code_executor=BuiltInCodeExecutor()
)

result = runner.run(
    """分析此銷售數據並提供見解：
    月份 | 銷售額
    Jan   | 15000
    Feb   | 18000
    Mar   | 16500
    Apr   | 22000
    May   | 21000
    Jun   | 25000
    """,
    agent=data_analyst
)
```

**預期輸出**：

```
讓我來分析這份銷售數據：
[程式碼：]
import statistics

sales = [15000, 18000, 16500, 22000, 21000, 25000]
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']

# 計算統計數據
mean = statistics.mean(sales)
median = statistics.median(sales)
stdev = statistics.stdev(sales)
total = sum(sales)

# 計算增長率
growth = [(sales[i] - sales[i-1]) / sales[i-1] * 100
          for i in range(1, len(sales))]

# 找到最佳月份
best_month_idx = sales.index(max(sales))

print(f"平均值: ${mean:,.2f}")
print(f"中位數: ${median:,.2f}")
print(f"標準差: ${stdev:,.2f}")
print(f"總計: ${total:,}")
print(f"最佳月份: {months[best_month_idx]}")
print(f"平均增長率: {statistics.mean(growth):.1f}%")

[輸出：]
平均值: $19,583.33
中位數: $19,500.00
標準差: $3,804.40
總計: $117,500
最佳月份: Jun
平均增長率: 9.2%

**主要見解：**
- 強勁的上升趨勢，平均月增長率為 9.2%
- 六月份表現最佳，銷售額為 $25,000
- 從四月開始持續增長
- 建議：調查推動四月至六月銷售額飆升的原因
```

### 演算法實作 (Algorithm Implementation)

```python
algo_agent = Agent(
    model='gemini-2.0-flash',
    name='algorithm_expert',
    instruction='使用 Python 實作並展示演算法。',
    code_executor=BuiltInCodeExecutor()
)

result = runner.run(
    "實作二元搜尋並在 [1, 5, 12, 23, 42, 67, 89, 99] 中找到 42 的位置",
    agent=algo_agent
)
```

**預期輸出**：

```
[程式碼：]
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

arr = [1, 5, 12, 23, 42, 67, 89, 99]
target = 42
position = binary_search(arr, target)
print(f"在索引 {position} 找到 {target}")

[結果：] 在索引 4 找到 42

二元搜尋在**索引 4**（第五個元素，從零開始索引）找到了 **42**。
該演算法僅進行了 3 次比較，而不是線性地檢查所有 8 個元素，展示了 O(log n) 的效率。
```

---

## 3. 真實世界範例：財務計算機 (Real-World Example: Financial Calculator)

讓我們來建構一個全面的財務計算機代理程式。

### 完整實作 (Complete Implementation)

```python
"""財務計算機代理程式
使用程式碼執行進行精確的財務計算。
"""
import asyncio
import os
from google.adk.agents import Agent, Runner
from google.adk.code_executors import BuiltInCodeExecutor
from google.genai import types

# 環境設定
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = '1'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-project-id'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'

# 建立財務計算機代理程式
financial_calculator = Agent(
    model='gemini-2.0-flash',
    name='financial_calculator',
    description='具備 Python 程式碼執行能力的專業財務計算機',
    instruction="""你是財務計算專家。對於所有計算：
1. 編寫 Python 程式碼以計算精確值
2. 顯示你正在運行的程式碼
3. 解釋使用的公式
4. 使用 $ 格式清晰地呈現結果
5. 提供財務解讀

可用的計算：
- 複利
- 現值/未來值
- 貸款攤銷
- 投資回報（ROI, CAGR）
- 退休規劃
- 淨現值（NPV）
- 內部收益率（IRR）

始終執行程式碼以確保準確性。絕不進行近似計算。
    """.strip(),
    code_executor=BuiltInCodeExecutor(),
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1,  # 為了財務準確性，設定非常低
        max_output_tokens=2048
    )
)

async def calculate_financial(query: str):
    """運行財務計算。"""
    print(f"\n{'='*70}")
    print(f"查詢: {query}")
    print(f"{'='*70}\n")
    runner = Runner()
    result = await runner.run_async(query, agent=financial_calculator)
    print("💰 計算結果:\n")
    print(result.content.parts[0].text)
    print(f"\n{'='*70}\n")

async def main():
    """運行財務計算範例。"""
    # 範例 1：複利
    await calculate_financial("""如果我投資 $10,000，年利率 7%，每月複利，
30 年後我會有多少錢？
    """)
    await asyncio.sleep(2)

    # 範例 2：貸款支付
    await calculate_financial("""計算一筆 $300,000 的抵押貸款，年利率 6.5%，為期 30 年的每月還款額。
    """)
    await asyncio.sleep(2)

    # 範例 3：退休規劃
    await calculate_financial("""我今年 30 歲，希望在 65 歲時退休，並擁有 200 萬美元。
如果我每年能賺取 8% 的回報，我需要每月儲蓄多少錢？
    """)
    await asyncio.sleep(2)

    # 範例 4：投資比較
    await calculate_financial("""比較兩項投資：
A) 初始投資 $50,000，年回報率 6%，為期 20 年
B) 初始投資 $30,000 + 每月 $200，年回報率 8%，為期 20 年
哪一個更好？
    """)
    await asyncio.sleep(2)

    # 範例 5：損益平衡分析
    await calculate_financial("""一家企業的固定成本為每月 $50,000，每單位變動成本為 $25。
如果他們以每單位 $75 的價格出售，損益平衡點是多少？
    """)

if __name__ == '__main__':
    asyncio.run(main())
```

### 預期輸出 (Expected Output)

```
======================================================================
查詢: 如果我投資 $10,000，年利率 7%，每月複利，
30 年後我會有多少錢？
======================================================================
💰 計算結果:
讓我來計算複利：
[程式碼：]
# 複利公式：A = P(1 + r/n)^(nt)
# 其中：
# P = 本金 ($10,000)
# r = 年利率 (0.07)
# n = 每年複利次數 (12)
# t = 年數 (30)
principal = 10000
rate = 0.07
compounds_per_year = 12
years = 30

# 計算未來價值
future_value = principal * (1 + rate/compounds_per_year) ** (compounds_per_year * years)

# 計算賺取的總利息
interest_earned = future_value - principal

print(f"初始投資: ${principal:,.2f}")
print(f"未來價值: ${future_value:,.2f}")
print(f"賺取利息: ${interest_earned:,.2f}")
print(f"倍數: {future_value/principal:.2f}x")

[結果：]
初始投資: $10,000.00
未來價值: $81,402.45
賺取利息: $71,402.45
倍數: 8.14x

**結果：**
- 您的投資將增長到 **$81,402.45**
- 您將賺取 **$71,402.45** 的利息
- 您的資金在 30 年內將增長 **8.14 倍**

**關鍵見解：** 複利的威力！透過每月複利而不是每年複利，與年度複利相比，您將額外獲得約 $3,000。
======================================================================
======================================================================
查詢: 計算一筆 $300,000 的抵押貸款，年利率 6.5%，為期 30 年的每月還款額。
======================================================================
💰 計算結果:
讓我來計算抵押貸款還款額：
[程式碼：]
# 抵押貸款還款公式：M = P[r(1+r)^n]/[(1+r)^n-1]
# 其中：
# P = 貸款本金 ($300,000)
# r = 每月利率 (年利率 / 12)
# n = 還款次數 (年數 * 12)
principal = 300000
annual_rate = 0.065
monthly_rate = annual_rate / 12
num_payments = 30 * 12

# 計算每月還款額
numerator = monthly_rate * (1 + monthly_rate) ** num_payments
denominator = (1 + monthly_rate) ** num_payments - 1
monthly_payment = principal * (numerator / denominator)

# 計算總支付金額和利息
total_paid = monthly_payment * num_payments
total_interest = total_paid - principal

print(f"貸款金額: ${principal:,.2f}")
print(f"每月還款額: ${monthly_payment:,.2f}")
print(f"總支付金額: ${total_paid:,.2f}")
print(f"總利息: ${total_interest:,.2f}")
print(f"利息佔本金百分比: {(total_interest/principal)*100:.1f}%")

[結果：]
貸款金額: $300,000.00
每月還款額: $1,896.20
總支付金額: $682,632.00
總利息: $382,632.00
利息佔本金百分比: 127.5%

**結果：**
- 每月還款額：**$1,896.20**
- 30 年內總支付金額：**$682,632**
- 總支付利息：**$382,632**

**重要提示：** 您將支付的利息總額是原始貸款金額的 127.5%！考慮進行額外的本金還款以顯著減少這一數額。
======================================================================
```

---

## 4. 進階程式碼執行模式 (Advanced Code Execution Patterns)

### 模式 1：視覺化程式碼生成（供本機執行）(Pattern 1: Visualization Code Generation (For Local Execution))

```python
viz_agent = Agent(
    model='gemini-2.0-flash',
    name='data_viz',
    instruction="""生成使用 matplotlib 進行資料視覺化的 Python 程式碼。
顯示將建立視覺化圖表的程式碼。
⚠️ 重要提示：此程式碼供使用者在本機運行 - matplotlib
無法在 ADK 的沙箱環境中執行。
    """,
    code_executor=BuiltInCodeExecutor()
)

result = runner.run(
    "生成程式碼以建立顯示各季度銷售額的長條圖：" +
    "Q1=50k, Q2=65k, Q3=72k, Q4=80k",
    agent=viz_agent
)
```

**⚠️ 關鍵限制**：以下程式碼無法在 ADK 的程式碼執行環境中執行。這是**範例輸出**，顯示代理程式將為使用者生成的程式碼，供他們在自己安裝了 matplotlib 的系統上本地運行。

**輸出**（供使用者在本機運行的程式碼 - 不可在 ADK 中執行）：

```python
import matplotlib.pyplot as plt

quarters = ['Q1', 'Q2', 'Q3', 'Q4']
sales = [50000, 65000, 72000, 80000]

plt.figure(figsize=(10, 6))
plt.bar(quarters, sales, color='steelblue')

plt.title('季度銷售表現', fontsize=16, fontweight='bold')
plt.xlabel('季度', fontsize=12)
plt.ylabel('銷售額 ($)', fontsize=12)
plt.ylim(0, max(sales) * 1.1)

# 在長條上新增數值標籤
for i, v in enumerate(sales):
    plt.text(i, v + 1000, f'${v:,}', ha='center', va='bottom')

plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.show()
```

**ADK 程式碼執行無法做什麼：**

*   ❌ 生成實際的圖形或圖表
*   ❌ 使用 matplotlib、seaborn、plotly 或任何視覺化函式庫
*   ❌ 顯示圖片或繪圖
*   ❌ 儲存圖表檔案

**ADK 程式碼執行可以做什麼：**

*   ✅ 生成 matplotlib 程式碼作為文字供本機執行
*   ✅ 執行所有數學計算
*   ✅ 建立基於文字的資料表示
*   ✅ 生成 ASCII 藝術或簡單的文字圖表
*   ✅ 分析資料並提供見解

### 模式 2：科學計算 (Pattern 2: Scientific Calculations)

```python
science_agent = Agent(
    model='gemini-2.0-flash',
    name='scientist',
    instruction='使用 Python 執行科學計算和模擬。',
    code_executor=BuiltInCodeExecutor()
)

result = runner.run(
    """計算一顆距離地球 400 公里高空的衛星的軌道週期。
使用：G = 6.674×10^-11 N⋅m²/kg², 地球質量 = 5.972×10^24 kg,
地球半徑 = 6371 km
    """,
    agent=science_agent
)
```

### 模式 3：統計分析 (Pattern 3: Statistical Analysis)

```python
stats_agent = Agent(
    model='gemini-2.0-flash',
    name='statistician',
    instruction='執行統計分析，包括假設檢定和信賴區間。',
    code_executor=BuiltInCodeExecutor()
)

result = runner.run(
    """給定樣本數據 [23, 25, 28, 30, 29, 27, 26, 24, 31, 28]：
1. 計算平均值、中位數、標準差
2. 建構平均值的 95% 信賴區間
3. 檢定平均值是否顯著不同於 25 (α=0.05)
    """,
    agent=stats_agent
)
```

### 模式 4：演算法最佳化 (Pattern 4: Algorithm Optimization)

```python
optimizer_agent = Agent(
    model='gemini-2.0-flash',
    name='optimizer',
    instruction='使用 Python 實作並比較演算法效率。',
    code_executor=BuiltInCodeExecutor()
)

result = runner.run(
    """比較氣泡排序與快速排序在一個包含 1000 個隨機數字的列表上的性能。
測量每種方法的執行時間和比較次數。
    """,
    agent=optimizer_agent
)
```

---

## 5. 結合程式碼執行與工具 (Combining Code Execution with Tools)

您可以將程式碼執行與其他工具結合，以建立功能強大的代理程式：

```python
from google.adk.agents import Agent, Runner
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.tools import FunctionTool, GoogleSearchAgentTool

def get_stock_data(symbol: str) -> dict:
    """模擬的股票數據獲取器。"""
    # 在生產環境中，應呼叫真實的金融 API
    return {
        'symbol': symbol,
        'prices': [150, 152, 148, 155, 153, 157, 160],
        'volume': [1000000, 1100000, 950000, 1200000, 1050000, 1300000, 1250000]
    }

# 具備程式碼執行和自訂工具的混合代理程式
hybrid_agent = Agent(
    model='gemini-2.0-flash',
    name='financial_analyst',
    instruction="""你是一位金融分析師，擁有：
1. get_stock_data 工具來獲取市場數據
2. 程式碼執行來分析數據
3. 網路搜尋來查找公司新聞
使用所有功能提供全面的分析。
    """,
    code_executor=BuiltInCodeExecutor(),
    tools=[
        FunctionTool(get_stock_data),
        GoogleSearchAgentTool()
    ]
)

runner = Runner()
result = runner.run(
    "分析 AAPL 股票表現並計算其波動性",
    agent=hybrid_agent
)
```

---

## 6. 最佳實踐 (Best Practices)

### ✅ 要：使用程式碼執行以求精確 (DO: Use Code Execution for Precision)

```python
# ✅ 好的 - 使用程式碼進行精確計算
agent = Agent(
    model='gemini-2.0-flash',
    instruction='對所有數學計算使用 Python 程式碼。',
    code_executor=BuiltInCodeExecutor()
)

# ❌ 不好的 - 讓模型近似計算
agent = Agent(
    model='gemini-2.0-flash',
    instruction='在腦中近似計算。'
)
```

### ✅ 要：設定低溫以求準確 (DO: Set Low Temperature for Accuracy)

```python
# ✅ 好的 - 為程式碼生成設定低溫
agent = Agent(
    model='gemini-2.0-flash',
    code_executor=BuiltInCodeExecutor(),
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1  # 更具確定性的程式碼
    )
)

# ❌ 不好的 - 高溫可能產生無效程式碼
agent = Agent(
    model='gemini-2.0-flash',
    code_executor=BuiltInCodeExecutor(),
    generate_content_config=types.GenerateContentConfig(
        temperature=0.9  # 對於程式碼來說太有創意
    )
)
```

### ✅ 要：提供清晰的指令 (DO: Provide Clear Instructions)

```python
# ✅ 好的 - 清晰的指導
agent = Agent(
    model='gemini-2.0-flash',
    instruction="""對於計算：
1. 總是編寫 Python 程式碼
2. 顯示你正在執行的程式碼
3. 解釋邏輯
4. 清晰地顯示結果
5. 提供解讀
    """,
    code_executor=BuiltInCodeExecutor()
)

# ❌ 不好的 - 模糊
agent = Agent(
    model='gemini-2.0-flash',
    instruction="進行計算",
    code_executor=BuiltInCodeExecutor()
)
```

### ✅ 要：處理邊界情況 (DO: Handle Edge Cases)

```python
# ✅ 好的 - 指導關於錯誤處理
agent = Agent(
    model='gemini-2.0-flash',
    instruction="""編寫程式碼時：
1. 檢查除以零的情況
2. 驗證輸入範圍
3. 處理邊界情況（空列表、負數等）
4. 為錯誤包含 try-except
5. 提供有意義的錯誤訊息
    """,
    code_executor=BuiltInCodeExecutor()
)
```

### ✅ 要：驗證結果 (DO: Verify Results)

```python
# ✅ 好的 - 要求代理程式驗證
agent = Agent(
    model='gemini-2.0-flash',
    instruction="""執行程式碼後：
1. 檢查結果是否合理
2. 如果可能，使用替代方法進行驗證
3. 注意所做的任何假設
4. 警告有關限制
    """,
    code_executor=BuiltInCodeExecutor()
)
```

---

## 7. 疑難排解 (Troubleshooting)

### 錯誤：「程式碼執行需要 Gemini 2.0+」 (Error: "Code execution requires Gemini 2.0+")

**問題**：對錯誤的模型使用程式碼執行器

**解決方案**：

```python
# ❌ 錯誤的模型版本
agent = Agent(
    model='gemini-1.5-flash',
    code_executor=BuiltInCodeExecutor()  # 錯誤
)

# ✅ 使用 Gemini 2.0+
agent = Agent(
    model='gemini-2.0-flash',
    code_executor=BuiltInCodeExecutor()
)
```

### 問題：「程式碼未執行」 (Issue: "Code not executing")

**問題**：模型未使用程式碼執行功能

**解決方案**：

1.  **讓查詢需要計算**：

    ```python
    # ❌ 模型可能不執行程式碼
    result = runner.run("2+2 是多少？", agent=agent)

    # ✅ 複雜的計算會觸發程式碼執行
    result = runner.run("計算 [1,2,3,4,5,6,7,8,9,10] 的標準差", agent=agent)
    ```

2.  **明確的指令**：

    ```python
    agent = Agent(
        model='gemini-2.0-flash',
        instruction='總是編寫並執行 Python 程式碼進行計算。絕不近似計算。',
        code_executor=BuiltInCodeExecutor()
    )
    ```

### 問題：「程式碼執行錯誤」 (Issue: "Code execution errors")

**問題**：生成的程式碼有錯誤

**解決方案**：

1.  **降低溫度**：

    ```python
    agent = Agent(
        model='gemini-2.0-flash',
        code_executor=BuiltInCodeExecutor(),
        generate_content_config=types.GenerateContentConfig(
            temperature=0.0  # 最具確定性
        )
    )
    ```

2.  **新增錯誤處理指令**：

    ```python
    agent = Agent(
        model='gemini-2.0-flash',
        instruction="""編寫程式碼時：
    - 首先用簡單的案例測試
    - 使用 try-except 區塊
    - 驗證輸入
    - 檢查邊界情況
        """,
        code_executor=BuiltInCodeExecutor()
    )
    ```

### 問題：「回應時間慢」 (Issue: "Slow response time")

**問題**：程式碼執行增加了延遲

**解決方案**：

1.  **使用串流**：

    ```python
    from google.adk.agents import RunConfig, StreamingMode

    run_config = RunConfig(streaming_mode=StreamingMode.SSE)
    async for event in runner.run_async(query, agent=agent, run_config=run_config):
        print(event.content.parts[0].text, end='', flush=True)
    ```

2.  **最佳化程式碼複雜度**：

    ```python
    agent = Agent(
        model='gemini-2.0-flash',
        instruction='編寫高效的程式碼。避免不必要的循環或複雜操作。',
        code_executor=BuiltInCodeExecutor()
    )
    ```

---

## 8. 測試程式碼執行代理程式 (Testing Code Execution Agents)

### 單元測試 (Unit Tests)

```python
import pytest
from google.adk.agents import Agent, Runner
from google.adk.code_executors import BuiltInCodeExecutor

@pytest.mark.asyncio
async def test_code_execution_accuracy():
    """測試程式碼執行提供準確的結果。"""
    agent = Agent(
        model='gemini-2.0-flash',
        code_executor=BuiltInCodeExecutor()
    )
    runner = Runner()
    result = await runner.run_async(
        "計算 10 的階乘",
        agent=agent
    )
    # 10 的階乘 = 3,628,800
    assert '3628800' in result.content.parts[0].text

@pytest.mark.asyncio
async def test_statistical_calculation():
    """測試統計計算。"""
    agent = Agent(
        model='gemini-2.0-flash',
        instruction='使用 Python 計算精確的統計數據。',
        code_executor=BuiltInCodeExecutor(),
        generate_content_config=types.GenerateContentConfig(temperature=0.1)
    )
    runner = Runner()
    result = await runner.run_async(
        "計算 [10, 20, 30, 40, 50] 的平均值",
        agent=agent
    )
    # 平均值應為 30
    text = result.content.parts[0].text
    assert '30' in text or '三十' in text.lower()

@pytest.mark.asyncio
async def test_complex_calculation():
    """測試複雜的數學計算。"""
    agent = Agent(
        model='gemini-2.0-flash',
        code_executor=BuiltInCodeExecutor()
    )
    runner = Runner()
    result = await runner.run_async(
        "計算複利：本金 $1000，年利率 5%，10 年，每月複利",
        agent=agent
    )
    text = result.content.parts[0].text
    # 應約為 $1647
    assert '1647' in text or '1,647' in text

@pytest.mark.asyncio
async def test_algorithm_implementation():
    """測試代理程式可以實作演算法。"""
    agent = Agent(
        model='gemini-2.0-flash',
        instruction='使用 Python 程式碼實作演算法。',
        code_executor=BuiltInCodeExecutor()
    )
    runner = Runner()
    result = await runner.run_async(
        "實作一個函式來檢查一個數字是否為質數，然後用 17 測試它",
        agent=agent
    )
    text = result.content.parts[0].text.lower()
    # 17 是質數
    assert 'true' in text or '質數' in text
```

---

## 9. 安全考量 (Security Considerations)

### 程式碼執行安全 (Code Execution Security)

**重要**：程式碼在 Google 的模型環境中執行，而不是在本機。這提供了安全優勢：

✅ **隔離環境**：程式碼在沙箱化的模型環境中運行
✅ **無本機存取**：無法存取您的本機檔案系統
✅ **無網路存取**：無法進行外部網路呼叫
✅ **有限資源**：資源受限的執行
✅ **自動清理**：執行之間沒有持久狀態

**程式碼可以做什麼**：

*   數學計算
*   資料處理（列表、字典、陣列）
*   演算法實作
*   字串操作
*   統計分析

**程式碼不能做什麼**：

*   存取本機檔案
*   發出網路請求
*   安裝套件
*   執行 shell 命令
*   存取環境變數
*   在執行之間持久化數據

### 生產環境的最佳實踐 (Best Practices for Production)

```python
# ✅ 好的 - 清晰的界線
agent = Agent(
    model='gemini-2.0-flash',
    instruction="""你可以使用 Python 進行：
- 計算
- 資料分析
- 演算法實作

你不能：
- 存取檔案
- 發出網路請求
- 執行系統命令
    """,
    code_executor=BuiltInCodeExecutor()
)
```

---

## 總結 (Summary)

您已掌握了 AI 代理程式的程式碼執行：

**主要收穫**：

*   ✅ `BuiltInCodeExecutor` 實現了 Python 程式碼的生成與執行
*   ✅ 程式碼在**模型環境內部**運行（Google 的基礎設施）
*   ✅ 需要 **Gemini 2.0+** 模型
*   ✅ 非常適合：計算、資料分析、演算法、統計
*   ✅ 比模型近似值更準確
*   ✅ 安全 - 隔離的沙箱執行
*   ✅ 可與其他工具（搜尋、自訂函式）結合
*   ✅ 最好使用低溫（0.0-0.1）以確保準確性

**生產檢查清單**：

*   [ ] 使用 Gemini 2.0+ 模型
*   [ ] 設定低溫（0.0-0.2）
*   [ ] 清晰的指令說明何時使用程式碼
*   [ ] 包含錯誤處理指令
*   [ ] 使用各種計算類型進行測試
*   [ ] 啟用串流以獲得更好的使用者體驗
*   [ ] 在指令中包含驗證步驟
*   [ ] 指定邊界情況處理

**後續步驟**：

*   **教學 14**：實作串流（SSE）以獲得即時回應
*   **教學 15**：探索 Live API 以進行語音和雙向串流
*   **教學 16**：學習 MCP 整合以擴展工具生態系統

**資源**：

*   [ADK 程式碼執行文件](https://ai.google.dev/gemini-api/docs/code-execution/)
*   [Gemini 2.0 程式碼執行](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/gemini)
*   [Python 標準函式庫](https://docs.python.org/3/library/)

## 程式碼實現 (Code Implementation)
- code_calculator: [程式碼連結](../../../python/agents/code-calculator/)

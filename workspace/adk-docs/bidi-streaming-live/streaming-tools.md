# 串流工具 (Streaming Tools)

> 🔔 `更新日期：2026-01-30`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/streaming/streaming-tools/

[`ADK 支援`: `Python v0.5.0` | `Experimental`]

串流工具允許工具（函數）將中間結果串流傳回給代理（Agent），代理則可以對這些中間結果做出回應。
例如，我們可以使用串流工具來監控股票價格的變化，並讓代理對其做出反應。另一個例子是我們可以讓代理監控影片串流，當影片串流發生變化時，代理可以報告這些變化。

> [!NOTE]
這僅在串流（即時直播）代理/API 中受支援。

要定義串流工具，您必須遵守以下規定：

1.  **非同步函數：** 工具必須是一個 `async` Python 函數。
2.  **AsyncGenerator 回傳類型：** 函數必須指定回傳類型為 `AsyncGenerator`。`AsyncGenerator` 的第一個類型參數是您 `yield` 的資料類型（例如，文字訊息為 `str`，或結構化資料的自定義物件）。如果生成器不透過 `send()` 接收值，第二個類型參數通常為 `None`。

我們支援兩種類型的串流工具：
- 簡單類型。這是一種類型的串流工具，僅接受非影片/音訊串流（您饋送給 adk web 或 adk runner 的串流）作為輸入。
- 影片串流工具。這僅在影片串流中有效，影片串流（您饋送給 adk web 或 adk runner 的串流）將被傳遞到此函數中。

現在讓我們定義一個可以監控股價變化並監控影片串流變化的代理。

```python
import asyncio
from typing import AsyncGenerator

from google.adk.agents import LiveRequestQueue
from google.adk.agents.llm_agent import Agent
from google.adk.tools.function_tool import FunctionTool
from google.genai import Client
from google.genai import types as genai_types

# 定義一個非同步生成器函數來監控股價
async def monitor_stock_price(stock_symbol: str) -> AsyncGenerator[str, None]:
  """此函數將以持續、串流且非同步的方式監控指定 stock_symbol 的價格。"""
  print(f"開始為 {stock_symbol} 監控股價！")

  # 模擬股價變化。
  await asyncio.sleep(4)
  price_alert1 = f"{stock_symbol} 的價格為 300"
  yield price_alert1 # 傳回中間結果
  print(price_alert1)

  await asyncio.sleep(4)
  price_alert1 = f"{stock_symbol} 的價格為 400"
  yield price_alert1
  print(price_alert1)

  await asyncio.sleep(20)
  price_alert1 = f"{stock_symbol} 的價格為 900"
  yield price_alert1
  print(price_alert1)

  await asyncio.sleep(20)
  price_alert1 = f"{stock_symbol} 的價格為 500"
  yield price_alert1
  print(price_alert1)


# 對於影片串流，`input_stream: LiveRequestQueue` 是必要的且為 ADK 傳入影片串流的保留關鍵字參數。
async def monitor_video_stream(
    input_stream: LiveRequestQueue,
) -> AsyncGenerator[str, None]:
  """監控影片串流中有多少人。"""
  print("開始 monitor_video_stream！")
  client = Client(vertexai=False)
  prompt_text = (
      "計算此圖片中的人數。僅回傳一個數字。"
  )
  last_count = None

  while True:
    last_valid_req = None
    print("開始監控迴圈")

    # 使用此迴圈提取最新影像並捨棄舊影像
    while input_stream._queue.qsize() != 0:
      live_req = await input_stream.get()

      if live_req.blob is not None and live_req.blob.mime_type == "image/jpeg":
        last_valid_req = live_req

    # 如果找到有效的影像，則進行處理
    if last_valid_req is not None:
      print("正在處理佇列中最近的幀")

      # 使用 blob 的資料和 MIME 類型建立影像部分
      image_part = genai_types.Part.from_bytes(
          data=last_valid_req.blob.data, mime_type=last_valid_req.blob.mime_type
      )

      contents = genai_types.Content(
          role="user",
          parts=[image_part, genai_types.Part.from_text(prompt_text)],
      )

      # 呼叫模型根據提供的影像和提示生成內容
      response = client.models.generate_content(
          model="gemini-2.0-flash-exp",
          contents=contents,
          config=genai_types.GenerateContentConfig(
              system_instruction=(
                  "您是一位有用的影片分析助手。您可以計算此影像或影片中的人數。僅回傳一個數字。"
              )
          ),
      )
      if not last_count:
        last_count = response.candidates[0].content.parts[0].text
      elif last_count != response.candidates[0].content.parts[0].text:
        last_count = response.candidates[0].content.parts[0].text
        yield response # 當偵測到變化時傳回回應
        print("回應：", response)

    # 在檢查新影像之前等待
    await asyncio.sleep(0.5)

# 使用此確切函數來協助 ADK 在收到請求時停止您的串流工具。
# 例如，如果我們想停止 `monitor_stock_price`，則代理將調用
# 此函數並帶入 stop_streaming(function_name=monitor_stock_price)。
def stop_streaming(function_name: str):
  """停止串流

  參數:
    function_name: 要停止的串流函數名稱。
  """
  pass


# 初始化代理並配置工具
root_agent = Agent(
    model="gemini-2.0-flash-exp",
    name="video_streaming_agent",
    instruction="""
      您是一個監控代理。您可以使用提供的工具/函數進行影片監控和股價監控。
      當使用者想要監控影片串流時，您可以使用 monitor_video_stream 函數執行此操作。
      當 monitor_video_stream 傳回警報時，您應該告訴使用者。
      當使用者想要監控股價時，您可以使用 monitor_stock_price。
      不要問太多問題。不要太囉唆。
    """,
    tools=[
        monitor_video_stream,
        monitor_stock_price,
        FunctionTool(stop_streaming),
    ]
)
```

以下是一些可供測試的範例查詢：
- 幫我監控 $XYZ 股票的股價。
- 幫我監控影片串流中有多少人。

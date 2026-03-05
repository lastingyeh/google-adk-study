# 使用 Gemini API 的電腦使用工具集 (Computer Use Toolset)

> 🔔 `更新日期：2026-03-05`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/computer-use/

[`ADK 支援`: `Python v1.17.0` | `Preview`]

電腦使用工具集 (Computer Use Toolset) 允許代理操作電腦的使用者介面（例如瀏覽器）來完成任務。此工具使用特定的 Gemini 模型和 [Playwright](https://playwright.dev/) 測試工具來控制 Chromium 瀏覽器，並可以透過截圖、點擊、輸入和導覽與網頁進行互動。

有關電腦使用模型的更多資訊，請參閱 Gemini API [電腦使用 (Computer use)](https://ai.google.dev/gemini-api/docs/computer-use) 或 Google Cloud Vertex AI API [電腦使用 (Computer use)](https://cloud.google.com/vertex-ai/generative-ai/docs/computer-use)。

> [!TIP] 預覽版本
電腦使用模型與工具為預覽版本。如需更多資訊，請參閱 [發布階段說明 (launch stage descriptions)](https://cloud.google.com/products#product-launch-stages)。

## 設定

您必須安裝 Playwright 及其依賴項（包括 Chromium），才能使用電腦使用工具集。

> [!IMPORTANT] 建議：建立並啟用 Python 虛擬環境
> 建立 Python 虛擬環境：
>
> ```shell
> # 建立名為 .venv 的虛擬環境
> python -m venv .venv
> ```
>
> 啟用 Python 虛擬環境：
>
> - Windows CMD
>
>  ```
> # 在 Windows 命令提示字元中啟用虛擬環境
> .venv\Scripts\activate.bat
> ```
>
> - Windows Powershell
>
>```
># 在 Windows Powershell 中啟用虛擬環境
>.venv\Scripts\Activate.ps1
>```
>
> - MacOS / Linux
>```bash
># 在 MacOS 或 Linux 中啟用虛擬環境
>source .venv/bin/activate
>```

要為電腦使用工具集設定所需的軟體程式庫：

1.  安裝 Python 依賴項：
    ```console
    # 安裝特定版本的 termcolor 和 playwright，以及 browserbase 和 rich
    pip install termcolor==3.1.0
    pip install playwright==1.52.0
    pip install browserbase==1.3.0
    pip install rich
    ```
2.  安裝 Playwright 依賴項，包括 Chromium 瀏覽器：
    ```console
    # 安裝 Playwright 系統依賴項
    playwright install-deps chromium
    # 安裝 Chromium 瀏覽器
    playwright install chromium
    ```

## 使用工具

透過將電腦使用工具集作為工具新增到您的代理來使用它。當您設定工具時，必須提供 `BaseComputer` 類別的實作，該類別定義了代理使用電腦的介面。在以下範例中，為此目的定義了 `PlaywrightComputer` 類別。您可以在 [computer_use](https://github.com/google/adk-python/blob/main/contributing/samples/computer_use/playwright.py) 代理範例專案的 `playwright.py` 檔案中找到此實作的程式碼。

```python
from google.adk import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools.computer_use.computer_use_toolset import ComputerUseToolset
from typing_extensions import override

from .playwright import PlaywrightComputer

# 初始化根代理程式，配置支援電腦使用的 Gemini 模型與工具集
root_agent = Agent(
    # 使用支援電腦使用預覽版的 Gemini 模型
    model='gemini-2.5-computer-use-preview-10-2025',
    name='hello_world_agent',
    description=(
        '能在電腦上操作瀏覽器以完成使用者任務的電腦使用代理'
    ),
    # 設定代理程式指令
    instruction='你是電腦使用代理',
    # 新增電腦使用工具集，並指定螢幕解析度
    tools=[
        ComputerUseToolset(computer=PlaywrightComputer(screen_size=(1280, 936)))
    ],
)
```

有關完整的程式碼範例，請參閱 [computer_use](https://github.com/google/adk-python/tree/main/contributing/samples/computer_use) 代理範例專案。

### 實作範例

-   [`Computer Use`](../../../python/agents/computer-use/): 展示如何使用電腦使用工具集來操作瀏覽器完成任務的完整代理範例。
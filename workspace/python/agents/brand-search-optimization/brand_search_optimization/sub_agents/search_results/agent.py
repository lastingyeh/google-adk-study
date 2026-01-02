# 匯入必要的模組
import time  # 用於產生時間戳
import warnings  # 用於控制警告訊息的顯示

import selenium  # Selenium WebDriver 的主要函式庫，用於瀏覽器自動化
from google.adk.agents.llm_agent import (
    Agent,
)  # 從 Google ADK 匯入 Agent 類別，用於建立 AI 代理
from google.adk.tools.load_artifacts_tool import (
    load_artifacts_tool,
)  # 從 ADK 匯入工具，用於載入產出物
from google.adk.tools.tool_context import (
    ToolContext,
)  # 從 ADK 匯入工具上下文，用於在工具間傳遞狀態
from google.genai import types  # 從 Google GenAI 匯入類型定義，用於處理產出物
from PIL import Image  # 從 Pillow 函式庫匯入 Image，用於處理圖片
from selenium.webdriver.chrome.options import Options  # 用於設定 Chrome 瀏覽器的選項
from selenium.webdriver.common.by import By  # 用於指定元素定位的策略 (如 ID, XPATH 等)

# 從專案的共享函式庫中匯入常數
from ...shared_libraries.constants import DISABLE_WEB_DRIVER, MODEL

# 從當前目錄的 prompt.py 檔案中匯入提示字串
from .prompt import SEARCH_RESULT_AGENT_PROMPT

# 忽略特定類型的使用者警告，避免不必要的輸出干擾
warnings.filterwarnings("ignore", category=UserWarning)

# 根據 DISABLE_WEB_DRIVER 常數決定是否初始化 WebDriver
if not DISABLE_WEB_DRIVER:
    # 設定 Chrome 瀏覽器的選項
    options = Options()
    options.add_argument("--window-size=1920x1080")  # 設定瀏覽器視窗大小
    options.add_argument("--verbose")  # 啟用詳細日誌輸出
    options.add_argument(
        "user-data-dir=/tmp/selenium"
    )  # 設定使用者資料目錄，可保留 cookie 和快取

    # 使用指定的選項初始化 Chrome WebDriver
    driver = selenium.webdriver.Chrome(options=options)


def go_to_url(url: str) -> str:
    """瀏覽指定的 URL 並返回確認訊息。"""
    print(f"🌐 導航到指定 URL : {url}")  # 在終端機印出正在執行的動作
    driver.get(url.strip())  # 使用 driver 前往指定的 URL，並移除前後多餘的空白
    return f"已導航到指定 URL: {url}"


async def take_screenshot(tool_context: ToolContext) -> dict:
    """擷取當前畫面的螢幕截圖，並呼叫 'load_artifacts_tool' 來載入圖片。"""
    timestamp = time.strftime("%Y%m%d-%H%M%S")  # 產生包含日期和時間的時間戳
    filename = f"screenshot_{timestamp}.png"  # 建立唯一的檔案名稱
    print(f"📸 正在擷取螢幕截圖並儲存為: {filename}")  # 印出提示訊息
    driver.save_screenshot(filename)  # 儲存螢幕截圖

    image = Image.open(filename)  # 使用 Pillow 開啟圖片檔案

    # 使用 tool_context 將圖片檔案儲存為代理可以使用的「產出物」(artifact)
    await tool_context.save_artifact(
        filename,
        types.Part.from_bytes(data=image.tobytes(), mime_type="image/png"),
    )

    # 返回一個包含狀態和檔案名稱的字典
    return {"status": "ok", "filename": filename}


def click_at_coordinates(x: int, y: int) -> str:
    """在螢幕上的指定座標 (x, y) 進行點擊。"""
    driver.execute_script(
        f"window.scrollTo({x}, {y});"
    )  # 執行 JavaScript 將視窗捲動到指定座標
    driver.find_element(
        By.TAG_NAME, "body"
    ).click()  # 點擊 body 元素，這是一種通用的點擊方式


def find_element_with_text(text: str) -> str:
    """在頁面上尋找包含指定文字的元素。"""
    print(f"🔍 正在尋找包含文字的元素: '{text}'")  # 印出提示訊息

    try:
        # 使用 XPath 尋找第一個完全匹配指定文字的元素
        element = driver.find_element(By.XPATH, f"//*[text()='{text}']")
        if element:
            return "已找到元素。"
        else:
            # 理論上如果找不到，會直接拋出例外，但保留此處以防萬一
            return "未找到元素。"
    except selenium.common.exceptions.NoSuchElementException:
        # 如果找不到元素，Selenium 會拋出此例外
        return "未找到元素。"
    except selenium.common.exceptions.ElementNotInteractableException:
        # 如果元素存在但無法互動
        return "元素無法互動，無法點擊。"


def click_element_with_text(text: str) -> str:
    """在頁面上點擊包含指定文字的元素。"""
    print(f"🖱️ 正在點擊包含文字的元素: '{text}'")  # 印出提示訊息

    try:
        # 使用 XPath 尋找元素並點擊
        element = driver.find_element(By.XPATH, f"//*[text()='{text}']")
        element.click()
        return f"已點擊包含文字的元素: {text}"
    except selenium.common.exceptions.NoSuchElementException:
        return "未找到元素，無法點擊。"
    except selenium.common.exceptions.ElementNotInteractableException:
        return "元素無法互動，無法點擊。"
    except selenium.common.exceptions.ElementClickInterceptedException:
        # 當其他元素遮擋住目標元素時會發生
        return "元素點擊被攔截，無法點擊。"


def enter_text_into_element(text_to_enter: str, element_id: str) -> str:
    """在具有指定 ID 的元素中輸入文字。"""
    print(
        f"📝 正在將文字 '{text_to_enter}' 輸入到 ID 為 '{element_id}' 的元素中"
    )  # 印出提示訊息

    try:
        # 透過 ID 找到輸入框元素
        input_element = driver.find_element(By.ID, element_id)
        # 將文字輸入到元素中
        input_element.send_keys(text_to_enter)
        return f"已將文字 '{text_to_enter}' 輸入到 ID 為 '{element_id}' 的元素中"
    except selenium.common.exceptions.NoSuchElementException:
        return "找不到具有指定 ID 的元素。"
    except selenium.common.exceptions.ElementNotInteractableException:
        return "元素無法互動，無法輸入文字。"


def scroll_down_screen() -> str:
    """將螢幕向下捲動一個固定的距離。"""
    print("⬇️ 正在向下滑動螢幕")  # 印出提示訊息
    driver.execute_script(
        "window.scrollBy(0, 500)"
    )  # 執行 JavaScript 將視窗向下捲動 500 像素
    return "已向下滑動螢幕。"


def get_page_source() -> str:
    """返回當前頁面的 HTML 原始碼。"""
    LIMIT = 1000000  # 設定回傳內容的字元數上限，避免過長的原始碼影響處理效能
    print("📄 正在獲取頁面原始碼...")  # 印出提示訊息
    return driver.page_source[0:LIMIT]  # 返回頁面原始碼的前 LIMIT 個字元


def analyze_webpage_and_determine_action(page_source: str, user_task: str) -> str:
    """分析網頁內容並決定下一個動作（捲動、點擊等）。"""
    print("🤔 正在分析網頁並決定下一步動作...")  # 印出提示訊息

    # 這是一個動態產生的提示字串，將會被傳給 LLM
    analysis_prompt = f"""
    您是一位專業的網頁分析專家。
    您的任務是控制一個網頁瀏覽器來達成使用者的目標。
    使用者的任務是: {user_task}
    這是當前網頁的 HTML 原始碼:
    ```html
    {page_source}
    ```

    根據網頁內容和使用者任務，決定下一個最佳的行動。
    請考慮以下動作：補全網頁原始碼、向下捲動以查看更多內容、點擊連結或按鈕進行導航，或在輸入框中輸入文字。

    請逐步思考：
    1. 簡要分析使用者任務和網頁內容。
    2. 如果原始碼看起來不完整，請將其補全為有效的 HTML。產品標題請保持原樣，僅補全缺失的 HTML 語法。
    3. 識別頁面上潛在的互動元素（連結、按鈕、輸入框等）。
    4. 判斷是否需要捲動來顯示更多內容。
    5. 決定最合乎邏輯的下一步行動，以推進完成使用者任務。

    您的回應應該是一個簡潔的行動計畫，從以下選項中選擇：
    - "COMPLETE_PAGE_SOURCE": 如果原始碼不完整，將其補全為有效的 HTML。
    - "SCROLL_DOWN": 如果需要透過捲動來載入更多內容。
    - "CLICK: <element_text>": 如果應點擊帶有 <element_text> 文字的特定元素。請將 <element_text> 替換為元素的實際文字。
    - "ENTER_TEXT: <element_id>, <text_to_enter>": 如果需要在輸入框中輸入文字。請將 <element_id> 替換為輸入元素的 ID，<text_to_enter> 替換為要輸入的文字。
    - "TASK_COMPLETED": 如果您認為使用者任務已在此頁面上完成。
    - "STUCK": 如果您不確定下一步該做什麼或無法繼續前進。
    - "ASK_USER": 如果您需要使用者澄清下一步該做什麼。

    如果您選擇 "CLICK" 或 "ENTER_TEXT"，請確保元素的文字或 ID 可以從網頁原始碼中清楚識別。如果存在多個相似的元素，請根據使用者任務選擇最相關的一個。
    如果您不確定，或者以上所有動作都不合適，請預設選擇 "ASK_USER"。

    回應範例：
    - SCROLL_DOWN
    - CLICK: 了解更多
    - ENTER_TEXT: search_box_id, Gemini API
    - TASK_COMPLETED
    - STUCK
    - ASK_USER

    您的行動計畫是什麼？
    """
    return analysis_prompt


# 建立一個 Agent 實例
search_results_agent = Agent(
    model=MODEL,  # 指定代理使用的 LLM 模型
    name="search_results_agent",  # 代理的名稱
    description="使用網頁瀏覽功能，獲取關鍵字的前 3 個搜尋結果資訊",  # 代理的功能描述
    instruction=SEARCH_RESULT_AGENT_PROMPT,  # 代理執行的主要指令 (來自 prompt.py)
    # 將前面定義的函式作為工具列表提供給代理
    tools=[
        go_to_url,
        take_screenshot,
        find_element_with_text,
        click_element_with_text,
        enter_text_into_element,
        scroll_down_screen,
        get_page_source,
        load_artifacts_tool,
        analyze_webpage_and_determine_action,
    ],
)

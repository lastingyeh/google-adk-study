"""
第三方工具整合代理程式 - 教學 27

此代理程式示範如何將第三方框架工具整合到 ADK 中。
它使用 LangChain 的 Wikipedia 工具作為主要範例 (無需 API 金鑰)。

關鍵概念：
- 用於整合 LangChain 工具的 LangchainTool 包裝器
- 正確的匯入路徑 (google.adk.tools.langchain_tool)
- 工具包裝與代理程式設定
- 第三方工具的錯誤處理

重點摘要：
- **核心概念**：透過包裝器 (Wrapper) 將外部生態系 (LangChain, CrewAI) 的工具引入 ADK。
- **關鍵技術**：LangChain (Wikipedia, DuckDuckGo), CrewAI (File/Dir Tools), Google ADK Agent。
- **重要結論**：ADK 的靈活性允許開發者利用現有的豐富 Python AI 工具庫，而無需重新造輪子。
- **行動項目**：參考 `create_wikipedia_tool` 等函式學習如何封裝外部工具。
"""

from google.adk.agents import Agent
from google.adk.tools.langchain_tool import LangchainTool
from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from crewai_tools import DirectoryReadTool, FileReadTool


def create_wikipedia_tool():
    """
    使用 LangChain 建立 Wikipedia 搜尋工具。

    此工具允許代理程式搜尋 Wikipedia 以獲取事實資訊。
    無需 API 金鑰 - 使用公共 Wikipedia API。

    Returns:
        LangchainTool: 已包裝好可供 ADK 代理程式使用的 Wikipedia 工具
    """
    # 使用 LangChain 建立 Wikipedia 工具
    # WikipediaAPIWrapper 負責與 Wikipedia API 互動
    # top_k_results=3: 限制返回的結果數量為前 3 筆
    # doc_content_chars_max=4000: 限制每個文件內容的最大字元數
    wikipedia = WikipediaQueryRun(
        api_wrapper=WikipediaAPIWrapper(
            top_k_results=3,
            doc_content_chars_max=4000
        )
    )

    # 使用 LangchainTool 為 ADK 進行包裝
    # 這是將 LangChain 工具轉換為 ADK 相容格式的關鍵步驟
    wiki_tool = LangchainTool(tool=wikipedia)

    return wiki_tool


def create_web_search_tool():
    """
    使用 LangChain 透過 DuckDuckGo 建立網頁搜尋工具。

    此工具允許代理程式搜尋網路以獲取最新資訊。
    無需 API 金鑰 - 使用 DuckDuckGo 的公共搜尋。

    Returns:
        LangchainTool: 已包裝好可供 ADK 代理程式使用的網頁搜尋工具
    """
    # 使用 LangChain 建立網頁搜尋工具
    # DuckDuckGoSearchRun 是一個現成的 LangChain 工具
    web_search = DuckDuckGoSearchRun()

    # 使用 LangchainTool 為 ADK 進行包裝
    search_tool = LangchainTool(tool=web_search)

    return search_tool


def create_directory_read_tool():
    """
    使用 CrewAI 建立目錄讀取工具。

    此工具允許代理程式探索目錄結構。
    對於了解專案佈局和檔案組織很有用。

    Returns:
        function: ADK 相容的工具函式
    """
    # 初始化 CrewAI 的 DirectoryReadTool
    tool = DirectoryReadTool()

    # 定義一個包裝函式來適配 ADK 的工具介面
    # ADK 工具通常是接受參數並返回字典或字串的 Python 函式
    def directory_read(directory_path: str) -> dict:
        """
        讀取目錄內容。

        Args:
            directory_path: 要讀取的目錄路徑

        Returns:
            Dict 包含狀態、報告和目錄內容
        """
        try:
            # 呼叫 CrewAI 工具的 run 方法
            result = tool.run(directory_path=directory_path)
            return {
                'status': 'success',
                'report': f'成功讀取目錄：{directory_path}',
                'data': result
            }
        except Exception as e:
            # 錯誤處理：確保代理程式收到結構化的錯誤回應
            return {
                'status': 'error',
                'error': str(e),
                'report': f'讀取目錄失敗：{directory_path}'
            }

    return directory_read


def create_file_read_tool():
    """
    使用 CrewAI 建立檔案讀取工具。

    此工具允許代理程式讀取檔案內容。
    對於分析程式碼、文件和設定檔很有用。

    Returns:
        function: ADK 相容的工具函式
    """
    # 初始化 CrewAI 的 FileReadTool
    tool = FileReadTool()

    # 定義包裝函式
    def file_read(file_path: str) -> dict:
        """
        讀取檔案內容。

        Args:
            file_path: 要讀取的檔案路徑

        Returns:
            Dict 包含狀態、報告和檔案內容
        """
        try:
            # 呼叫 CrewAI 工具執行檔案讀取
            result = tool.run(file_path=file_path)
            return {
                'status': 'success',
                'report': f'成功讀取檔案：{file_path}',
                'data': result
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'report': f'讀取檔案失敗：{file_path}'
            }

    return file_read


# 建立具有多個第三方工具的根代理程式
# 這是代理程式的主要進入點
root_agent = Agent(
    name="third_party_agent",
    model="gemini-2.0-flash",
    description="""
    一個具有 Wikipedia、網頁搜尋和檔案系統工具存取權限的綜合研究與檔案分析助理。
    示範如何將多個第三方工具 (LangChain 和 CrewAI) 整合到 ADK 代理程式中。

    主要功能：
    - 用於百科全書知識的 LangChain Wikipedia 工具
    - 用於最新資訊的 LangChain DuckDuckGo 網頁搜尋
    - 用於探索檔案結構的 CrewAI DirectoryReadTool
    - 用於分析檔案內容的 CrewAI FileReadTool
    - 任何工具都不需要 API 金鑰
    - 可存取歷史事實、近期發展和本地檔案
    - 來自多個來源的結構化、基於事實的回應
    """,
    instruction="""
    你是一位知識淵博的研究與檔案分析助理，可以使用多種工具。

    當使用者詢問問題時：
    1. 使用 Wikipedia 查詢歷史事實、傳記和既定知識
    2. 使用網頁搜尋查詢時事、近期發展和即時新聞
    3. 使用目錄讀取來探索專案結構和檔案組織
    4. 使用檔案讀取來分析特定檔案、程式碼或文件
    5. 盡可能交叉比對資訊以提供全面的答案
    6. 提供基於事實、來源充分的答案，並註明來源
    7. 如果資訊有衝突，請註明差異並建議驗證
    8. 誠實說明每個工具的限制

    始終保持：
    - 準確且基於事實
    - 清晰且簡潔
    - 樂於引導使用者獲取更多資訊

    你可以協助的範例查詢：
    - "什麼是量子運算？" (Wikipedia)
    - "今年最新的 AI 發展" (網頁搜尋)
    - "告訴我關於艾達·洛夫萊斯的事" (Wikipedia)
    - "關於太空探索的最新新聞" (網頁搜尋)
    - "顯示專案結構" (目錄讀取)
    - "讀取 README 檔案" (檔案讀取)
    """.strip(),
    tools=[
        create_wikipedia_tool(),
        create_web_search_tool(),
        create_directory_read_tool(),
        create_file_read_tool()
    ],
    output_key="research_response"
)


if __name__ == "__main__":
    # 示範代理程式可以成功匯入和建立
    print("第三方工具整合代理程式")
    print("=" * 50)
    print(f"代理程式名稱：{root_agent.name}")
    print(f"模型：{root_agent.model}")
    print(f"工具：已註冊 {len(root_agent.tools)} 個工具")
    print("\n代理程式建立成功！")
    print("\n試試查詢：")
    print("  - '什麼是量子運算？' (Wikipedia)")
    print("  - '今年最新的 AI 發展' (網頁搜尋)")
    print("  - '告訴我關於艾達·洛夫萊斯的事' (Wikipedia)")
    print("  - '關於太空探索的最新新聞' (網頁搜尋)")
    print("  - '顯示專案結構' (目錄讀取)")
    print("  - '讀取 README 檔案' (檔案讀取)")
    print("\n執行 'make dev' 在網頁介面中啟動代理程式")

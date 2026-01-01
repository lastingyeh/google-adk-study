# --- 重點說明 ---
# 1.  **RAG 檢索增強生成 (Retrieval-Augmented Generation)**:
#     此腳本建立了一個 AI 代理 (Agent)，採用 RAG 架構。當使用者提問時，它會先從外部資料儲存庫 (Data Store) 檢索相關文件，
#     然後將這些文件作為上下文，交給大型語言模型 (LLM) 來生成更準確、更具體的答案。
#
# 2.  **Google Cloud 服務整合**:
#     - **Vertex AI Agent Development Kit (ADK)**: 使用 `google.adk` 來定義和建立代理 (`Agent`) 與應用 (`App`)。
#     - **Vertex AI Search**: 透過 `get_retriever` 函式，從指定的資料儲存庫中擷取文件。
#     - **Vertex AI Rank**: 透過 `get_compressor` 函式，對檢索到的文件進行重新排序，以提高最相關文件的優先級。
#     - **Gemini 模型**: 使用 `gemini-3-flash-preview` 作為核心的大型語言模型，用於理解指令和生成回答。
#     - **Embedding 模型**: 使用 `text-embedding-005` 將查詢轉換為向量，以便在資料儲存庫中進行相似性搜索。
#
# 3.  **核心流程**:
#     a. **初始化**: 設定 Google Cloud 專案 ID、區域等環境變數，並初始化 Vertex AI 服務。
#     b. **建立工具 (Tool)**: 定義 `retrieve_docs` 函式作為代理可以使用的工具。此工具負責：
#        - 接收使用者查詢 (query)。
#        - 呼叫 `retriever` 獲取文件。
#        - 呼叫 `compressor` 對文件重新排序。
#        - 將文件格式化為字串。
#     c. **建立代理 (Agent)**: 建立一個 `Agent` 實例，給予它一個指令 (instruction)，告訴它如何行動，並將 `retrieve_docs` 函式作為工具提供給它。
#     d. **建立應用 (App)**: 將建立好的代理包裝成一個 ADK 應用，準備好接收請求。
# ---

import os

import google
import vertexai
from google.adk.agents import Agent
from google.adk.apps.app import App
from google.adk.models import Gemini
from google.genai import types
from langchain_google_vertexai import VertexAIEmbeddings

from app.retrievers import get_compressor, get_retriever
from app.templates import format_docs

# --- 模型與環境設定 ---
EMBEDDING_MODEL = "text-embedding-005"  # 用於生成嵌入向量的模型
LLM_LOCATION = "global"  # LLM 模型的通用位置
LOCATION = "us-central1"  # Vertex AI 服務的主要區域
LLM = "gemini-3-flash-preview"  # 使用的語言模型

# --- 初始化與認證 ---
# 進行預設的 Google Cloud 認證，並獲取專案 ID
credentials, project_id = google.auth.default()
# 設定環境變數，供後續函式庫使用
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = LLM_LOCATION
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

# 初始化 Vertex AI SDK
vertexai.init(project=project_id, location=LOCATION)
# 初始化嵌入模型客戶端
embedding = VertexAIEmbeddings(
    project=project_id, location=LOCATION, model_name=EMBEDDING_MODEL
)


# --- 檢索器 (Retriever) 與重排器 (Compressor) 設定 ---
EMBEDDING_COLUMN = "embedding"  # 資料儲存庫中儲存嵌入向量的欄位名稱
TOP_K = 5  # 預計檢索的文件數量 (此處未使用，但為常見參數)

# 從環境變數讀取 Vertex AI Search 的資料儲存庫設定
data_store_region = os.getenv("DATA_STORE_REGION", "us")
data_store_id = os.getenv("DATA_STORE_ID", "rag-km-agents-datastore")

# 建立檢索器，用於從資料儲存庫中獲取文件
retriever = get_retriever(
    project_id=project_id,
    data_store_id=data_store_id,
    data_store_region=data_store_region,
    embedding=embedding,
    embedding_column=EMBEDDING_COLUMN,
    max_documents=10,  # 設定最多檢索 10 份文件
)

# 建立重排器 (壓縮器)，用於對檢索到的文件進行相關性排序
compressor = get_compressor(
    project_id=project_id,
)


def retrieve_docs(query: str) -> str:
    """
    一個實用的工具，用於根據查詢檢索相關文件。
    當你需要額外資訊來回答問題時，請使用此工具。

    Args:
        query (str): 使用者的問題或搜尋查詢。

    Returns:
        str: 根據查詢檢索並排序後，包含相關文件內容的格式化字串。
    """
    try:
        # 使用檢索器根據查詢獲取相關文件
        retrieved_docs = retriever.invoke(query)
        # 使用 Vertex AI Rank 對文件進行重新排序，以獲得更好的相關性
        ranked_docs = compressor.compress_documents(
            documents=retrieved_docs, query=query
        )
        # 將排序後的文件格式化為一致的結構，以便 LLM 使用
        formatted_docs = format_docs.format(docs=ranked_docs)
    except Exception as e:
        return f"使用查詢呼叫檢索工具時發生錯誤:\n\n{query}\n\n引發了以下錯誤:\n\n{type(e)}: {e}"

    return formatted_docs


# --- 代理 (Agent) 設定 ---
# 給予代理的指令，指導其行為
instruction = """你是一個用於問答任務的 AI 助理。
請使用提供的上下文盡力回答問題。
利用你被賦予的工具來回答問題。
如果你已經知道問題的答案，可以直接回答，無需使用工具。"""

# 建立根代理 (root agent)
root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-3-flash-preview",
        retry_options=types.HttpRetryOptions(attempts=3),  # 設定 API 呼叫重試次數
    ),
    instruction=instruction,
    tools=[retrieve_docs],  # 將文件檢索函式作為工具提供給代理
)

# --- 應用 (App) 建立 ---
# 將根代理包裝成一個 ADK 應用程式
app = App(root_agent=root_agent, name="app")

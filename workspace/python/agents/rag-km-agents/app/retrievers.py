from unittest.mock import MagicMock
from langchain_google_community.vertex_rank import VertexAIRank
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_google_community import VertexAISearchRetriever

def get_retriever(
    project_id: str,
    data_store_id: str,
    data_store_region: str,
    embedding: VertexAIEmbeddings,
    embedding_column: str = "embedding",
    max_documents: int = 10,
    custom_embedding_ratio: float = 0.5,
) -> VertexAISearchRetriever:
    """
    ### 重點說明：建立並回傳一個檢索器 (Retriever) 實例。

    此函式用於從 Vertex AI Search (Agent Builder) 的資料儲存庫中檢索文件。

    - **主要功能**: 初始化 `VertexAISearchRetriever`，這是與您的資料庫溝通的核心元件。
    - **自訂嵌入**: 您可以提供自己的嵌入模型 (`embedding`)，並透過 `custom_embedding_ratio` 參數來調整自訂嵌入與 Google 原生搜尋的混合比例。
        - `custom_embedding_ratio = 1.0`：完全使用您的自訂嵌入進行搜尋。
        - `custom_embedding_ratio = 0.0`：完全使用 Google 的原生搜尋。
        - `custom_embedding_ratio = 0.5`：混合使用兩者。
    - **錯誤處理**: 如果因為環境設定（例如缺少認證）而無法初始化真正的檢索器，它會回傳一個 `MagicMock` 物件。當您試圖使用這個模擬物件時，它會引發一個明確的錯誤，告知「檢索器不可用」，以避免程式在後續流程中意外崩潰。
    """
    try:
        return VertexAISearchRetriever(
            project_id=project_id,
            data_store_id=data_store_id,
            location_id=data_store_region,
            engine_data_type=1,  # 1 代表結構化資料
            # --- 以下參數用於在 Agent Builder 中使用自訂嵌入進行搜尋 ---
            # 預設比例為 0.5，代表混合使用自訂嵌入和原生搜尋，您可以根據需求調整此比例。
            custom_embedding_ratio=custom_embedding_ratio,
            custom_embedding=embedding,
            custom_embedding_field_path=embedding_column,
            # 在重新排序（re-rank）之前，先提取20份文件。
            max_documents=max_documents,
            beta=True,
        )
    except Exception:
        # 如果無法建立 Vertex AI 檢索器，則回傳一個模擬物件
        retriever = MagicMock()

        def raise_exception(*_, **__) -> None:
            """當檢索器不可用時，此函式會引發例外。"""
            raise Exception("檢索器不可用 (Retriever not available)")

        retriever.invoke = raise_exception
        return retriever


def get_compressor(project_id: str, top_n: int = 5) -> VertexAIRank:
    """
    ### 重點說明：建立並回傳一個壓縮器 (Compressor) / 重新排序器 (Re-ranker) 實例。

    此函式使用 Vertex AI Rank服務來對檢索到的文件進行重新排序，以提高結果的相關性。

    - **主要功能**: 初始化 `VertexAIRank`，它會接收一組文件，並根據查詢的相關性對它們進行評分和排序。
    - **參數 `top_n`**: 指定重新排序後，最終要回傳的排名最前面的文件數量。例如，如果檢索器找到了 10 份文件，`top_n=5` 會讓壓縮器只回傳最相關的 5 份。
    - **錯誤處理**: 與 `get_retriever` 類似，如果初始化失敗，它會回傳一個 `MagicMock` 物件。這個模擬物件在被呼叫時會回傳一個空列表 `[]`，確保即使重新排序失敗，後續的流程也能繼續執行而不會出錯。
    """
    try:
        return VertexAIRank(
            project_id=project_id,
            location_id="global",
            ranking_config="default_ranking_config",
            title_field="id",
            top_n=top_n,
        )
    except Exception:
        # 如果無法建立 Vertex AI 壓縮器，則回傳一個模擬物件
        compressor = MagicMock()
        # 當呼叫 compress_documents 時，回傳一個空列表，以避免程式中斷
        compressor.compress_documents = lambda _: []
        return compressor

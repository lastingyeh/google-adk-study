# 版權所有 2025 Google LLC
#
# 根據 Apache 許可證 2.0 版（「許可證」）授權；
# 除非遵守許可證，否則您不得使用此檔案。
# 您可以在以下網址獲得許可證副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據許可證分發的軟體
# 是按「原樣」分發的，無任何明示或暗示的保證或條件。
# 請參閱許可證以了解管理權限和許可證下的限制。

"""
### 摘要
本檔案是一個自動化腳本，用於準備 RAG 語料庫（Corpus）與資料。它會自動在 Vertex AI 中建立語料庫，下載指定的 PDF 文件（範例為 Alphabet 10-K 報告），並將其上傳至語料庫中。

### 核心重點
- **核心概念**：自動化 RAG 資料管道（Data Pipeline）。
- **關鍵技術**：Vertex AI RAG API, Google Auth, `requests` 下載, `dotenv` 環境管理。
- **重要結論**：腳本會自動更新 `.env` 檔案中的 `RAG_CORPUS` 變數，以便 Agent 之後可以直接使用。
"""

import os
import tempfile

import requests
import vertexai
from dotenv import load_dotenv, set_key
from google.api_core.exceptions import ResourceExhausted
from google.auth import default
from vertexai.preview import rag

# 從 .env 檔案載入環境變數
load_dotenv()

# --- 配置區 ---
# 從環境變數中獲取專案 ID
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
if not PROJECT_ID:
    raise ValueError("未設定 GOOGLE_CLOUD_PROJECT 環境變數。請在您的 .env 檔案中設定。")

# 從環境變數中獲取區域
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
if not LOCATION:
    raise ValueError(
        "未設定 GOOGLE_CLOUD_LOCATION 環境變數。請在您的 .env 檔案中設定。"
    )

CORPUS_DISPLAY_NAME = "Alphabet_10K_2024_corpus"
CORPUS_DESCRIPTION = "包含 Alphabet 10-K 2024 文件之語料庫"
PDF_URL = "https://abc.xyz/assets/77/51/9841ad5c4fbe85b4440c47a4df8d/goog-10-k-2024.pdf"
PDF_FILENAME = "goog-10-k-2024.pdf"

# .env 檔案的絕對路徑
ENV_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", ".env")
)


# --- 腳本邏輯 ---


def initialize_vertex_ai():
    """初始化 Vertex AI SDK。"""
    credentials, _ = default()
    vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=credentials)


def create_or_get_corpus():
    """建立新語料庫或獲取現有語料庫。"""
    # 配置嵌入模型 (Embedding Model)
    embedding_model_config = rag.EmbeddingModelConfig(
        publisher_model="publishers/google/models/text-embedding-004"
    )

    # 檢查是否已存在同名的語料庫
    existing_corpora = rag.list_corpora()
    corpus = None
    for existing_corpus in existing_corpora:
        if existing_corpus.display_name == CORPUS_DISPLAY_NAME:
            corpus = existing_corpus
            print(f"找到現有的語料庫，顯示名稱為 '{CORPUS_DISPLAY_NAME}'")
            break

    # 如果不存在，則建立新的
    if corpus is None:
        corpus = rag.create_corpus(  # type: ignore[assignment]
            display_name=CORPUS_DISPLAY_NAME,
            description=CORPUS_DESCRIPTION,
            embedding_model_config=embedding_model_config,
        )
        print(f"已建立新的語料庫，顯示名稱為 '{CORPUS_DISPLAY_NAME}'")
    return corpus


def download_pdf_from_url(url, output_path):
    """從指定的 URL 下載 PDF 檔案。"""
    print(f"正在從 {url} 下載 PDF...")
    response = requests.get(url, stream=True)
    response.raise_for_status()  # 若發生 HTTP 錯誤則拋出異常

    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"PDF 下載成功，儲存於 {output_path}")
    return output_path


def upload_pdf_to_corpus(corpus_name, pdf_path, display_name, description):
    """將 PDF 檔案上傳至指定的語料庫。"""
    print(f"正在將 {display_name} 上傳至語料庫...")
    try:
        rag_file = rag.upload_file(
            corpus_name=corpus_name,
            path=pdf_path,
            display_name=display_name,
            description=description,
        )
        print(f"成功將 {display_name} 上傳至語料庫")
        return rag_file
    except ResourceExhausted as e:
        # 處理配額超出錯誤
        print(f"上傳檔案 {display_name} 時發生錯誤: {e}")
        print("\n此錯誤表示您已超出嵌入模型的 API 配額。")
        print("這在新的 Google Cloud 專案中很常見。")
        print("請參閱 README.md 中的「故障排除」章節，了解如何申請增加配額。")
        return None
    except Exception as e:
        print(f"上傳檔案 {display_name} 時發生錯誤: {e}")
        return None


def update_env_file(corpus_name, env_file_path):
    """將語料庫名稱更新至 .env 檔案中。"""
    try:
        set_key(env_file_path, "RAG_CORPUS", corpus_name)
        print(f"已更新 {env_file_path} 中的 RAG_CORPUS 為 {corpus_name}")
    except Exception as e:
        print(f"更新 .env 檔案時發生錯誤: {e}")


def list_corpus_files(corpus_name):
    """列出指定語料庫中的所有檔案。"""
    files = list(rag.list_files(corpus_name=corpus_name))
    print(f"語料庫中的檔案總數: {len(files)}")
    for file in files:
        print(f"檔案: {file.display_name} - {file.name}")


def main():
    """主執行函式。"""
    initialize_vertex_ai()
    corpus = create_or_get_corpus()

    # 將語料庫資源 ID 更新至 .env 檔案
    update_env_file(corpus.name, ENV_FILE_PATH)

    # 建立臨時目錄來儲存下載的 PDF
    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_path = os.path.join(temp_dir, PDF_FILENAME)

        # 從 URL 下載 PDF
        download_pdf_from_url(PDF_URL, pdf_path)

        # 將 PDF 上傳至語料庫
        upload_pdf_to_corpus(
            corpus_name=corpus.name,
            pdf_path=pdf_path,
            display_name=PDF_FILENAME,
            description="Alphabet 10-K 2024 文件",
        )

    # 列出語料庫中的所有檔案以供驗證
    list_corpus_files(corpus_name=corpus.name)


if __name__ == "__main__":
    main()

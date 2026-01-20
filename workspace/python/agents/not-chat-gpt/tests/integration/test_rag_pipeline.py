import os
import sys
import time
from dotenv import load_dotenv

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
import google.genai as genai
from google.genai import types


# Load environment variables from .env file
load_dotenv()

# --- Test Configuration ---
# Get the absolute path of the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
# Path to the validation document
DOC_PATH = os.path.join(project_root, "docs", "rag_validation_article.md")
# Model to use for testing
MODEL_NAME = "gemini-3-flash-preview"


@pytest.fixture(scope="module")
def file_search_store():
    """
    A Pytest fixture that creates a FileSearchStore, uploads and imports a file,
    and cleans up everything afterward.
    """
    print(f"Attempting to upload document: {DOC_PATH}")
    assert os.path.exists(DOC_PATH), f"Validation document not found at {DOC_PATH}"

    client = genai.Client()
    store_display_name = "not-chat-gpt"
    
    # Try to find an existing store
    store = None
    for s in client.file_search_stores.list():
        if s.display_name == store_display_name:
            store = s
            print(f"Found existing FileSearchStore: {store.name}")
            break

    # If no store is found, create a new one
    if not store:
        print(f"Creating FileSearchStore: {store_display_name}")
        store = client.file_search_stores.create(config={'display_name': store_display_name})
        
        # 2. Upload the file
        print(f"Uploading file: {DOC_PATH}")
        # The file object is temporary and will be deleted after 48 hours.
        uploaded_file = client.files.upload(
            file=DOC_PATH,
            config={'display_name': os.path.basename(DOC_PATH)}
        )
        print(f"Successfully uploaded file: {uploaded_file.display_name} ({uploaded_file.name})")

        # 3. Import the file into the store
        print(f"Importing file {uploaded_file.name} into store {store.name}...")
        operation = client.file_search_stores.import_file(
            file_search_store_name=store.name,
            file_name=uploaded_file.name
        )
        
        # Wait for the import to complete
        while not operation.done:
            print("Waiting for file import to complete...")
            time.sleep(10)
            operation = client.operations.get(operation)
        
        print("File import completed.")

    # Yield the store to the tests
    yield store
    
    # --- Teardown ---
    # Note: For simplicity in this example, we are not deleting the store.
    # In a real-world scenario, you might want to have a separate cleanup script
    # or a flag to control deletion.
    print(f"\nSkipping cleanup for FileSearchStore {store.name} to allow reuse.")
    # print(f"\nCleaning up: Deleting FileSearchStore {store.name}")
    # client.file_search_stores.delete(name=store.name, config={'force': True})
    # print("Cleanup complete.")


def query_model_with_file_search(question: str, store: any) -> str:
    """Sends a question to the Gemini model with the file search tool."""
    client = genai.Client()
    
    print(f"Querying model with question: '{question}'")
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=question,
        config=types.GenerateContentConfig(
            tools=[
                types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=[store.name]
                    )
                )
            ]
        )
    )
    
    return response.text


@pytest.mark.integration
def test_rag_with_direct_file_search(file_search_store):
    """
    Tests the RAG functionality by directly calling the model with file search.
    """
    assert file_search_store is not None, "FileSearchStore creation failed in fixture."

    # --- Test Case 1: Ask about the main company ---
    question1 = "Aethelred Dynamics 是做什麼的？"
    print(f"\n[Q1] Asking: {question1}")
    
    answer1 = query_model_with_file_search(question1, file_search_store)
    print(f"[A1] Agent responded: {answer1}")
    
    # Assertions for Q1
    assert "Aethelred Dynamics" in answer1
    assert "量子糾纏" in answer1 or "通訊" in answer1

    # --- Test Case 2: Ask about a specific technical term ---
    question2 = "什麼是 QSS 場？"
    print(f"\n[Q2] Asking: {question2}")

    answer2 = query_model_with_file_search(question2, file_search_store)
    print(f"[A2] Agent responded: {answer2}")

    # Assertions for Q2
    assert "QSS" in answer2
    assert "量子態穩定器" in answer2

    # --- Test Case 3: Ask about future plans ---
    question3 = "Aethelred Dynamics 的未來計劃是什麼？"
    print(f"\n[Q3] Asking: {question3}")

    answer3 = query_model_with_file_search(question3, file_search_store)
    print(f"[A3] Agent responded: {answer3}")

    # Assertions for Q3
    assert "2035" in answer3
    assert "月球" in answer3 or "基地" in answer3

    print("\nAll RAG pipeline test cases passed!")

import os
import sys

# Add project root to the Python path to resolve module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
import requests
import time

from backend.service.document_service import DocumentService

# --- Test Configuration ---
# Get the absolute path of the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
# Path to the validation document
DOC_PATH = os.path.join(project_root, "docs", "rag_validation_article.md")
# ADK Server endpoint
ADK_API_URL = "http://localhost:8000/run"
# Agent details for the request
APP_NAME = "agents"  # The main orchestrator agent
USER_ID = "rag_tester"
SESSION_ID = "rag_test_session"


@pytest.fixture(scope="module")
def uploaded_file():
    """
    A Pytest fixture that handles uploading the document before tests
    and cleaning it up afterward.
    """
    print(f"Attempting to upload document: {DOC_PATH}")
    assert os.path.exists(DOC_PATH), f"Validation document not found at {DOC_PATH}"

    doc_service = DocumentService()
    
    # Cleanup: Delete the file if it already exists from a previous failed run
    files = doc_service.list_files()
    for f in files:
        if f.display_name == os.path.basename(DOC_PATH):
            print(f"Found and deleting existing file: {f.name} ({f.display_name})")
            doc_service.delete_file(f.name)
            # Wait a moment for deletion to process
            time.sleep(2) 

    # Upload the new file
    uploaded_file = doc_service.upload_file(DOC_PATH)
    print(f"Successfully uploaded file: {uploaded_file.name} ({uploaded_file.display_name})")
    
    # Yield the file object to the tests
    yield uploaded_file
    
    # Teardown: Delete the file after tests are complete
    print(f"Cleaning up: Deleting file {uploaded_file.name}")
    doc_service.delete_file(uploaded_file.name)
    print("Cleanup complete.")


def query_agent(question: str) -> str:
    """Sends a question to the ADK agent and returns the text response."""
    headers = {"Content-Type": "application/json"}
    payload = {
        "app_name": APP_NAME,
        "user_id": USER_ID,
        "session_id": SESSION_ID,
        "new_message": {
            "role": "user",
            "parts": [{"text": question}],
        },
    }
    
    # Create a new session before the first query
    session_url = f"http://localhost:8000/apps/{APP_NAME}/users/{USER_ID}/sessions/{SESSION_ID}"
    requests.post(session_url, headers=headers, json={})

    response = requests.post(ADK_API_URL, headers=headers, json=payload)
    response.raise_for_status()  # Raise an exception for bad status codes
    
    response_data = response.json()
    # Extract text from the agent's response
    return response_data.get("new_message", {}).get("parts", [{}])[0].get("text", "")


@pytest.mark.integration
def test_rag_pipeline_e2e(uploaded_file):
    """
    End-to-end test for the RAG pipeline.
    1. Uploads a document (via fixture).
    2. Asks a question about the document.
    3. Asserts that the answer contains relevant information from the document.
    """
    assert uploaded_file is not None, "File upload failed in fixture."

    # --- Test Case 1: Ask about the main company ---
    question1 = "Aethelred Dynamics 是做什麼的？"
    print(f"\n[Q1] Asking: {question1}")
    
    answer1 = query_agent(question1)
    print(f"[A1] Agent responded: {answer1}")
    
    # Assertions for Q1
    assert "Aethelred Dynamics" in answer1
    assert "量子糾纏" in answer1 or "通訊" in answer1
    assert "超光速" in answer1 or "數據傳輸" in answer1

    # --- Test Case 2: Ask about a specific technical term ---
    question2 = "什麼是 QSS 場？"
    print(f"\n[Q2] Asking: {question2}")

    answer2 = query_agent(question2)
    print(f"[A2] Agent responded: {answer2}")

    # Assertions for Q2
    assert "QSS" in answer2
    assert "量子態穩定器" in answer2
    assert "退相干" in answer2 or "保護" in answer2

    # --- Test Case 3: Ask about future plans ---
    question3 = "Aethelred Dynamics 的未來計劃是什麼？"
    print(f"\n[Q3] Asking: {question3}")

    answer3 = query_agent(question3)
    print(f"[A3] Agent responded: {answer3}")

    # Assertions for Q3
    assert "2035" in answer3
    assert "月球" in answer3 or "基地" in answer3
    assert "高頻寬鏈路" in answer3

    print("\nAll RAG pipeline test cases passed!")


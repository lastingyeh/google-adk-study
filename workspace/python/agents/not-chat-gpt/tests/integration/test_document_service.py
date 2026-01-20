import os
import sys
import time
import pytest
from dotenv import load_dotenv

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.service.document_service import DocumentService

# Load environment variables
load_dotenv()

@pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="GOOGLE_API_KEY not set")
@pytest.mark.integration
class TestDocumentServiceIntegration:
    """
    Integration tests for the DocumentService that interact with the live Google AI API.
    """
    
    @pytest.fixture(scope="class")
    def service(self):
        """Provides a DocumentService instance for the test class."""
        # Use a unique display name for each test run to ensure isolation
        store_display_name = f"teststore{int(time.time())}"
        return DocumentService(store_display_name=store_display_name)

    @pytest.fixture(scope="class")
    def validation_doc_path(self):
        """Provides the path to the validation document."""
        # This assumes the test is run from the project root 
        # or the path is correctly resolved by pytest.
        return os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..', 'docs', 'rag_validation_article.md'
        ))

    def test_store_lifecycle_and_query(self, service: DocumentService, validation_doc_path: str):
        """
        Tests the core functionality:
        1. Getting or creating a FileSearchStore.
        2. Querying the store to verify it's working.
        3. Listing files in the store.
        """
        # --- Test-specific injection ---
        # Inject the doc_path for this test case, as it's not set in the constructor.
        service.doc_path = validation_doc_path
        # -----------------------------

        try:
            # 1. Test get_or_create_store_name (will create the store)
            print(f"\n[1/3] Getting or creating store: {service.store_display_name}")
            store_name = service.get_or_create_store_name()
            
            assert store_name is not None
            assert service.store_display_name in store_name
            print(f"-> Store name acquired: {store_name}")

            # 2. Test list_files
            print(f"\n[2/3] Listing files in the store...")
            files = service.list_files()
            assert len(files) > 0
            print(f"-> Found {len(files)} file(s) in the store.")

            # 3. Test query_document
            print("\n[3/3] Querying the document...")
            # This query is designed to be answerable by the content of rag_validation_article.md
            query = "What is QSS?"
            response_text = service.query_document(query)
            
            assert response_text is not None
            assert isinstance(response_text, str)
            assert len(response_text) > 0
            
            print(f"-> Query successful. Response received:\n---\n{response_text[:200]}...\n---")

        finally:
            # 4. Cleanup: Delete the store
            if service._store_name_cache:
                store_name_to_delete = service._store_name_cache
                print(f"\n[Cleanup] Deleting store: {store_name_to_delete}")
                try:
                    # Use force=True to delete the store and all its contents
                    service.client.file_search_stores.delete(name=store_name_to_delete, 
                        config={"force": True}
                    )
                    print("-> Store and its contents deleted successfully.")
                except Exception as e:
                    print(f"-> Error during cleanup: {e}")

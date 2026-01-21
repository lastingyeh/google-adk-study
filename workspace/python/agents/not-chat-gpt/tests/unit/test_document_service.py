import os
import io
import pytest
from unittest.mock import patch, MagicMock, PropertyMock

# Add project root to the Python path to resolve module imports
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.service.document_service import DocumentService

@pytest.fixture
def mock_genai_client():
    """Fixture to mock the genai.Client and its related objects."""
    with patch('google.genai.Client') as mock_client_constructor:
        mock_client = MagicMock()
        mock_client_constructor.return_value = mock_client
        
        # Mock the sub-objects
        mock_client.file_search_stores = MagicMock()
        mock_client.files = MagicMock()
        mock_client.operations = MagicMock()
        mock_client.models = MagicMock()
        
        yield mock_client

@pytest.fixture
def service(mock_genai_client):
    """Provides a DocumentService instance with a mocked client."""
    # Mock os.path.exists to always return True for the validation document
    with patch('os.path.exists', return_value=True):
        # Use a consistent key for tests
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key"}):
            yield DocumentService(store_display_name="unit-test-store")

class TestDocumentService:
    """Unit tests for the DocumentService."""

    def test_init_success(self):
        """Test that the service initializes correctly with an API key."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key"}):
            service = DocumentService()
            assert service.client is not None

    @patch.dict(os.environ, {}, clear=True)
    def test_init_no_key_raises_error(self):
        """Test that a ValueError is raised if no API key is available."""
        with pytest.raises(ValueError, match="Google API key is not configured"):
            DocumentService()

    def test_get_or_create_store_name_finds_existing(self, service, mock_genai_client):
        """Test that an existing store is found and its name is returned and cached."""
        mock_store = MagicMock()
        mock_store.display_name = "unit-test-store"
        mock_store.name = "fileSearchStores/existing-store-123"
        mock_genai_client.file_search_stores.list.return_value = [mock_store]

        # First call - should find the store
        store_name = service.get_or_create_store_name()
        assert store_name == "fileSearchStores/existing-store-123"
        assert service._store_name_cache == "fileSearchStores/existing-store-123"
        mock_genai_client.file_search_stores.list.assert_called_once()
        mock_genai_client.file_search_stores.create.assert_not_called()

        # Second call - should use the cache
        store_name_cached = service.get_or_create_store_name()
        assert store_name_cached == "fileSearchStores/existing-store-123"
        # list() should not be called again
        mock_genai_client.file_search_stores.list.assert_called_once()

    @patch('time.sleep', return_value=None) # Mock sleep to speed up test
    def test_get_or_create_store_name_creates_new(self, mock_sleep, service, mock_genai_client):
        """Test that a new store is created when none is found."""
        # No stores found
        mock_genai_client.file_search_stores.list.return_value = []

        # Mock the creation process
        mock_new_store = MagicMock()
        mock_new_store.name = "fileSearchStores/new-store-456"
        mock_genai_client.file_search_stores.create.return_value = mock_new_store

        mock_uploaded_file = MagicMock()
        mock_uploaded_file.name = "files/uploaded-file-789"
        mock_genai_client.files.upload.return_value = mock_uploaded_file

        # Mock the operation to be done immediately
        mock_operation = MagicMock()
        type(mock_operation).done = PropertyMock(return_value=True)
        mock_genai_client.file_search_stores.import_file.return_value = mock_operation

        # --- Test-specific injection ---
        # Inject the doc_path for this test case only
        service.doc_path = "/fake/path/to/doc.md"
        # -----------------------------

        store_name = service.get_or_create_store_name()

        assert store_name == "fileSearchStores/new-store-456"
        mock_genai_client.file_search_stores.list.assert_called_once()
        mock_genai_client.file_search_stores.create.assert_called_once_with(
            config={'display_name': 'unit-test-store'}
        )
        # Verify the file upload is NOT called anymore during store creation
        mock_genai_client.files.upload.assert_not_called()
        mock_genai_client.file_search_stores.import_file.assert_not_called()

    @patch('time.sleep', return_value=None)
    def test_upload_file_from_stream(self, mock_sleep, service, mock_genai_client):
        """Test that a file-like object can be uploaded successfully."""
        # Arrange
        service._store_name_cache = "fileSearchStores/test-store"
        
        mock_uploaded_file = MagicMock()
        mock_uploaded_file.name = "files/uploaded-stream-file-123"
        mock_genai_client.files.upload.return_value = mock_uploaded_file

        mock_operation = MagicMock()
        type(mock_operation).done = PropertyMock(return_value=True)
        mock_genai_client.file_search_stores.import_file.return_value = mock_operation

        file_name = "test_upload.txt"
        file_data = io.BytesIO(b"This is a test file from a stream.")

        # Act
        service.upload_file(file_name=file_name, file_data=file_data)

        # Assert
        mock_genai_client.files.upload.assert_called_once_with(
            file=file_data,
            config={'display_name': file_name}
        )
        mock_genai_client.file_search_stores.import_file.assert_called_once_with(
            file_search_store_name="fileSearchStores/test-store",
            file_name="files/uploaded-stream-file-123"
        )

    def test_list_files(self, service, mock_genai_client):
        """Test the list_files method."""
        # First, ensure the store name is cached
        service._store_name_cache = "fileSearchStores/test-store"
        
        mock_file_in_store = MagicMock()
        mock_file_in_store.display_name = "rag_validation_article.md"
        mock_file_in_store.name = "files/abc-123"
        
        mock_store_with_files = MagicMock()
        
        # The list method returns a paginated result, so we mock an iterator
        mock_documents = [MagicMock(), MagicMock()]
        mock_documents[0].display_name = "doc1.txt"
        mock_documents[0].name = "files/abc-123"
        mock_documents[1].display_name = "doc2.pdf"
        mock_documents[1].name = "files/def-456"
        mock_genai_client.file_search_stores.documents.list.return_value = mock_documents

        files = service.list_files()

        mock_genai_client.file_search_stores.documents.list.assert_called_once_with(parent="fileSearchStores/test-store")
        assert len(files) == 2
        assert files[0] == {"display_name": "doc1.txt", "name": "files/abc-123"}
        assert files[1] == {"display_name": "doc2.pdf", "name": "files/def-456"}

    def test_query_document(self, service, mock_genai_client):
        """Test the query_document method."""
        # Ensure the store name is cached
        service._store_name_cache = "fileSearchStores/test-store"
        
        mock_response = MagicMock()
        mock_response.text = "This is the mocked response from the model."
        mock_genai_client.models.generate_content.return_value = mock_response

        query = "What is Google ADK?"
        response_text = service.query_document(query)

        assert response_text == "This is the mocked response from the model."
        
        # Verify that generate_content was called with the correct tool configuration
        call_args, call_kwargs = mock_genai_client.models.generate_content.call_args
        assert call_kwargs['contents'] == query
        
        tools_config = call_kwargs['config'].tools[0]
        assert tools_config.file_search.file_search_store_names[0] == "fileSearchStores/test-store"

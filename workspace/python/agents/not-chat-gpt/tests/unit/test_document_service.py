import os
import pytest
from unittest.mock import patch, MagicMock, PropertyMock

# Add project root to the Python path to resolve module imports
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.service.document_service import DocumentService

@pytest.fixture
def mock_genai_client():
    """Fixture to mock the genai.Client and its file operations."""
    with patch('google.genai.Client') as mock_client_constructor:
        mock_client_instance = MagicMock()
        mock_client_constructor.return_value = mock_client_instance
        yield mock_client_constructor # Yield the constructor mock itself

class TestDocumentService:
    """Unit tests for the DocumentService."""

    def test_init_with_api_key(self, mock_genai_client):
        """Test that the service initializes correctly when an API key is provided."""
        service = DocumentService(api_key="test_key")
        mock_genai_client.assert_called_once_with(api_key="test_key")
        assert service.client is not None

    @patch.dict(os.environ, {"GOOGLE_API_KEY": "env_test_key"})
    def test_init_with_env_var(self, mock_genai_client):
        """Test that the service initializes correctly using an environment variable."""
        service = DocumentService()
        mock_genai_client.assert_called_once_with(api_key="env_test_key")
        assert service.client is not None

    @patch.dict(os.environ, {}, clear=True)
    def test_init_no_key_raises_error(self):
        """Test that a ValueError is raised if no API key is available."""
        with pytest.raises(ValueError, match="Google API key is not configured"):
            DocumentService()

    def test_upload_file(self, mock_genai_client):
        """Test the upload_file method."""
        service = DocumentService(api_key="fake_key")
        
        mock_file = MagicMock()
        mock_file.name = "files/test-file-123"
        mock_file.display_name = "test.txt"
        mock_genai_client.return_value.files.upload.return_value = mock_file

        result = service.upload_file("/fake/path/test.txt", display_name="test.txt")

        mock_genai_client.return_value.files.upload.assert_called_once_with(
            file="/fake/path/test.txt",
            config={'display_name': 'test.txt'}
        )
        assert result == mock_file

    def test_list_files(self, mock_genai_client):
        """Test the list_files method."""
        service = DocumentService(api_key="fake_key")

        mock_file = MagicMock()
        type(mock_file).name = PropertyMock(return_value="files/test-file-123")
        type(mock_file).display_name = PropertyMock(return_value="test.txt")
        type(mock_file).mime_type = PropertyMock(return_value="text/plain")
        type(mock_file).size_bytes = PropertyMock(return_value=100)
        type(mock_file).create_time = PropertyMock(return_value=MagicMock(isoformat=lambda: "2024-01-01T00:00:00Z"))
        type(mock_file).uri = PropertyMock(return_value="https://example.com/file")
        
        mock_genai_client.return_value.files.list.return_value = [mock_file]

        files = service.list_files()

        assert len(files) == 1
        assert files[0]["name"] == "files/test-file-123"
        assert files[0]["display_name"] == "test.txt"

    def test_get_file(self, mock_genai_client):
        """Test the get_file method."""
        service = DocumentService(api_key="fake_key")
        file_id = "files/test-file-123"

        mock_file = MagicMock()
        type(mock_file).name = PropertyMock(return_value=file_id)
        # ... (configure other properties as in list_files if needed)
        mock_genai_client.return_value.files.get.return_value = mock_file

        file_details = service.get_file(file_id)

        mock_genai_client.return_value.files.get.assert_called_once_with(name=file_id)
        assert file_details is not None
        assert file_details["name"] == file_id

    def test_get_file_not_found(self, mock_genai_client):
        """Test get_file when the file does not exist."""
        service = DocumentService(api_key="fake_key")
        mock_genai_client.return_value.files.get.side_effect = Exception("File not found")

        result = service.get_file("files/non-existent")
        assert result is None

    def test_delete_file(self, mock_genai_client):
        """Test the delete_file method."""
        service = DocumentService(api_key="fake_key")
        file_id = "files/to-delete-123"

        service.delete_file(file_id)

        mock_genai_client.return_value.files.delete.assert_called_once_with(name=file_id)
        
    def test_delete_file_error(self, mock_genai_client):
        """Test delete_file error handling."""
        service = DocumentService(api_key="fake_key")
        mock_genai_client.return_value.files.delete.side_effect = Exception("Deletion failed")

        result = service.delete_file("files/fail-delete")
        assert result["status"] == "error"
        assert "Deletion failed" in result["message"]

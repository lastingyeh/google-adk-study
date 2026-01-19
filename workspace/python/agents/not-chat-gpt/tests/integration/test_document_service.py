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
        return DocumentService()

    @pytest.fixture(scope="class")
    def temp_file(self):
        """Creates a temporary file for uploading and cleans it up afterward."""
        file_path = "temp_test_file_for_upload.txt"
        content = f"This is a test file created at {time.time()}"
        with open(file_path, "w") as f:
            f.write(content)
        
        yield file_path
        
        # Teardown: remove the local temp file
        os.remove(file_path)

    def test_full_lifecycle(self, service: DocumentService, temp_file: str):
        """
        Tests the complete lifecycle of a file: upload, list, get, and delete.
        """
        uploaded_file = None
        try:
            # 1. Test upload_file
            print(f"\n[1/4] Uploading file: {temp_file}")
            display_name = os.path.basename(temp_file)
            uploaded_file = service.upload_file(temp_file, display_name=display_name)
            
            assert uploaded_file is not None
            assert uploaded_file.name is not None
            assert uploaded_file.display_name == display_name
            print(f"-> Upload successful. File ID: {uploaded_file.name}")

            # Give the API a moment to process the file
            time.sleep(5)

            # 2. Test list_files
            print(f"\n[2/4] Listing files to find '{display_name}'")
            all_files = service.list_files()
            assert isinstance(all_files, list)
            
            found_in_list = any(f['name'] == uploaded_file.name for f in all_files)
            assert found_in_list, f"Uploaded file {uploaded_file.name} not found in the list of files."
            print("-> File found in list.")

            # 3. Test get_file
            print(f"\n[3/4] Getting file by ID: {uploaded_file.name}")
            file_details = service.get_file(uploaded_file.name)
            
            assert file_details is not None
            assert file_details["name"] == uploaded_file.name
            assert file_details["display_name"] == display_name
            print("-> Get file successful.")

        finally:
            # 4. Test delete_file (Cleanup)
            if uploaded_file and uploaded_file.name:
                print(f"\n[4/4] Deleting file: {uploaded_file.name}")
                delete_status = service.delete_file(uploaded_file.name)
                assert delete_status["status"] == "success"
                print("-> Deletion successful.")

                # Verify deletion
                time.sleep(5)
                deleted_file_details = service.get_file(uploaded_file.name)
                assert deleted_file_details is None, "File should have been deleted, but it was still found."
                print("-> Verified that file is no longer accessible.")

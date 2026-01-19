"""
This service encapsulates the logic for interacting with the Google AI File API.
It provides methods for uploading, listing, retrieving, and deleting files,
which serve as the knowledge base for the RAG system.

Inspired by the FileStore implementation in the 'policy-navigator' example.
"""
import os
from typing import List, Dict, Any, Optional

import google.genai as genai
from google.genai import types as genai_types

# Configure the Gemini API key from environment variables
# Make sure to have GOOGLE_API_KEY set in your .env file
# genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

class DocumentService:
    """A service class to manage documents using the Google AI File API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initializes the DocumentService.
        
        Args:
            api_key: The Google API key. If not provided, it will try to
                     use the one configured globally or from the environment.
        """
        # The new API uses a client instance.
        # Configuring the API key globally is still an option for simplicity here.
        
        # Determine the key to use
        key_to_use = api_key or os.getenv("GOOGLE_API_KEY")

        if not key_to_use:
            raise ValueError(
                "Google API key is not configured. Please set the GOOGLE_API_KEY "
                "environment variable or pass it to the service constructor."
            )
            
                # The client object is the new entry point for file operations.
        self.client = genai.Client(api_key=key_to_use)

    def upload_file(self, file_path: str, display_name: Optional[str] = None) -> genai_types.File:
        """
        Uploads a file to the Google AI File API.

        Args:
            file_path: The local path to the file to upload.
            display_name: An optional display name for the file.

        Returns:
            A File object representing the uploaded file.
        """
        print(f"Uploading file: {file_path}...")
        if not display_name:
            display_name = os.path.basename(file_path)
        
        # Use the client to upload the file
        file = self.client.files.upload(
            file=file_path, 
            config={'display_name': display_name}
        )
        print(f"Successfully uploaded file: {file.display_name} (ID: {file.name})")
        return file

    def list_files(self) -> List[Dict[str, Any]]:
        """
        Lists all files available in the File API.

        Returns:
            A list of dictionaries, where each dictionary represents a file.
        """
        files_data = []
        # Use the client to list files
        for f in self.client.files.list():
            files_data.append({
                "name": f.name,
                "display_name": f.display_name,
                "mime_type": f.mime_type,
                "size_bytes": f.size_bytes,
                "create_time": f.create_time.isoformat(),
                "uri": f.uri,
            })
        return files_data

    def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves metadata for a specific file by its ID.

        Args:
            file_id: The unique ID of the file (e.g., 'files/abc-123').

        Returns:
            A dictionary with file metadata, or None if not found.
        """
        try:
            # Use the client to get the file
            f = self.client.files.get(name=file_id)
            return {
                "name": f.name,
                "display_name": f.display_name,
                "mime_type": f.mime_type,
                "size_bytes": f.size_bytes,
                "create_time": f.create_time.isoformat(),
                "uri": f.uri,
            }
        except Exception as e:
            print(f"Error retrieving file {file_id}: {e}")
            return None

    def delete_file(self, file_id: str) -> Dict[str, Any]:
        """
        Deletes a file from the File API.

        Args:
            file_id: The unique ID of the file to delete.
        
        Returns:
            A confirmation dictionary.
        """
        try:
            # Use the client to delete the file
            self.client.files.delete(name=file_id)
            print(f"Successfully deleted file: {file_id}")
            return {"status": "success", "deleted_file_id": file_id}
        except Exception as e:
            print(f"Error deleting file {file_id}: {e}")
            return {"status": "error", "message": str(e)}

# Example usage:
if __name__ == '__main__':
    # This is for demonstration purposes.
    # In the actual application, the service will be instantiated by the API layer.
    
    # Make sure to create a .env file with your GOOGLE_API_KEY
    from dotenv import load_dotenv
    load_dotenv()

    if not os.getenv("GOOGLE_API_KEY"):
        print("Please create a .env file and add your GOOGLE_API_KEY.")
    else:
        service = DocumentService()

        # --- Example: Upload a file ---
        # Create a dummy file for testing
        DUMMY_FILE = "test_document.txt"
        with open(DUMMY_FILE, "w") as f:
            f.write("This is a test document for the DocumentService.")
        
        uploaded_file = service.upload_file(DUMMY_FILE)
        file_id = uploaded_file.name
        
        # --- Example: List files ---
        print("\n--- Listing all files ---")
        all_files = service.list_files()
        print(f"Found {len(all_files)} files.")
        for f in all_files:
            print(f"- {f['display_name']} ({f['name']})")

        # --- Example: Get a specific file ---
        if file_id:
            print(f"\n--- Getting file {file_id} ---")
            file_details = service.get_file(file_id)
            if file_details:
                print(f"Details: {file_details}")

        # --- Example: Delete the file ---
        if file_id:
            print(f"\n--- Deleting file {file_id} ---")
            delete_status = service.delete_file(file_id)
            print(f"Deletion status: {delete_status}")

        # --- Clean up dummy file ---
        os.remove(DUMMY_FILE)

        print("\n--- DocumentService demonstration finished ---")

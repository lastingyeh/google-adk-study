import os
import time
import google.genai as genai
from google.genai import types
from google.api_core import exceptions
from typing import Optional

class DocumentService:
    """
    Manages the lifecycle and retrieval of the Google AI FileSearchStore.
    Caches the store name for efficient reuse.
    """
    def __init__(self, store_display_name: str = "not-chat-gpt", api_key: Optional[str] = None):
        # Determine the key to use
        key_to_use = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = os.getenv("GENAI_MODEL", "gemini-3-flash-preview")

        if not key_to_use:
            raise ValueError(
                "Google API key is not configured. Please set the GOOGLE_API_KEY "
                "environment variable or pass it to the service constructor."
            )
            
        # The client object is the new entry point for file operations.
        self.client = genai.Client(api_key=key_to_use)
        self.store_display_name = store_display_name
        self._store_name_cache = None

    def get_or_create_store_name(self) -> str:
        """
        Gets the unique name of the FileSearchStore.

        Tries to find an existing store by display name. If not found,
        it creates a new one, uploads, and imports the validation document.
        The name is cached in memory to avoid repeated lookups.

        Returns:
            The unique resource name of the FileSearchStore.
        """
        if self._store_name_cache:
            return self._store_name_cache

        store = self._find_store_by_display_name()

        if not store:
            print(f"No existing store found. Creating FileSearchStore: {self.store_display_name}")
            store = self.client.file_search_stores.create(config={'display_name': self.store_display_name})
            print(f"Store created: {store.name}.")
        
        self._store_name_cache = store.name
        return self._store_name_cache

    def _find_store_by_display_name(self) -> types.FileSearchStore | None:
        """Lists all stores and finds one matching the display name."""
        print(f"Listing all stores to find '{self.store_display_name}'...")
        try:
            for s in self.client.file_search_stores.list():
                if s.display_name == self.store_display_name:
                    print(f"Found existing FileSearchStore: {s.name}")
                    return s
        except exceptions.PermissionDenied as e:
            print(f"Error: Permission denied. Ensure the API key has 'Vertex AI Search Service User' role. Details: {e}")
            raise
        return None

    def upload_file(self, file_name: str, file_data):
        """
        Uploads a file from a file-like object and imports it into the store.

        Args:
            file_name: The name of the file.
            file_data: The file-like object to upload.
        """
        store_name = self.get_or_create_store_name()
        self._upload_and_import_file(store_name, file_name, file_data)

    def _upload_and_import_file(self, store_name: str, file_name: str, file_data):
        """Uploads the document from a file-like object and imports it into the store."""
        print(f"Uploading file: {file_name}")
        uploaded_file = self.client.files.upload(
            file=file_data,
            config={'display_name': file_name}
        )
        print(f"Successfully uploaded file: {uploaded_file.display_name} ({uploaded_file.name})")

        print(f"Importing file {uploaded_file.name} into store {store_name}...")
        operation = self.client.file_search_stores.import_file(
            file_search_store_name=store_name,
            file_name=uploaded_file.name
        )
        
        while not operation.done:
            print("Waiting for file import to complete...")
            time.sleep(10)
            operation = self.client.operations.get(operation)
        
        print("File import completed.")

    def list_files(self) -> list:
        """Lists all files in the managed store."""
        store_name = self.get_or_create_store_name()
        response = self.client.file_search_stores.documents.list(parent=store_name)
        # The response is a paginated result, so we iterate through it.
        return [{"display_name": doc.display_name, "name": doc.name} for doc in response]

    
    def query_document(self, query: str):
        """Queries the document store with a given query string."""
        store_name = self.get_or_create_store_name()
        response = self.client.models.generate_content(
            model=self.model,
            contents=query,
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=[store_name]
                        )
                    )
                ]
            )
        )
    
        return response.text
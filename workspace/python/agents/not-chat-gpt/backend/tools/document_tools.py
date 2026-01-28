"""
This module defines the tools related to document management and search
that can be used by the agents.
"""
from service.document_service import DocumentService

# Instantiate the service that interacts with the Google AI File API.
# In a real application with dependency injection, this would be provided.
document_service = DocumentService()


def query_knowledge_base(query: str) -> str:
    """
    Searches the document store with the given query string.
    Args:
        query: The search query string.
    Returns:
        The search results from the document store.
    """
    print(f"Searching files with query: {query}")
    return document_service.query_document(query)


DOCUMENT_TOOLS = [
    query_knowledge_base,
]

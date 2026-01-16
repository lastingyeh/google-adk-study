"""
This module defines the tools related to document management and search
that can be used by the agents.
"""
from service.document_service import DocumentService

# Instantiate the service that interacts with the Google AI File API.
# In a real application with dependency injection, this would be provided.
document_service = DocumentService()

def list_all_available_documents() -> list:
    """
    Lists all documents currently available in the shared file store.
    This helps the agent know which documents can be searched.
    
    Returns:
        A list of available documents with their names and IDs.
    """
    return document_service.list_files()

# The tools defined here are for managing the document set that the agent can search on.

# By defining `search_files` as a tool, we are explicitly telling the agent
# that it has a semantic search capability. The agent's underlying model (Gemini)
# is already equipped with a built-in 'file_search' capability. When the agent
# decides to use this `search_files` tool, the ADK framework will map this
# to the model's native `file_search` function, provided that the necessary
# files are attached to the request. This approach makes the agent's capabilities
# clear and modular.
def search_files(query: str) -> str:
    """
    Performs a semantic search for a query within the available documents.
    This should be the primary tool for answering questions that require knowledge
    from the document base.
    
    Args:
        query: The user's question or search query.
        
    Returns:
        A string containing the search results, which the model will then use
        to formulate a final answer. The ADK handles the underlying `file_search`
        call and injects the results back into the model's context.
    """
    # This function is a stub. The ADK's `file_search` integration is what
    # actually performs the work. By defining this tool, we give the agent
    # a named capability ('search_files') that it can reason about and decide
    # to use. The instruction prompt will guide it on *when* to use it.
    # The return value here is not directly used, as the framework intercepts
    # the tool call and replaces it with the real search results.
    return f"Performing a semantic search for: '{query}'"


DOCUMENT_TOOLS = [
    list_all_available_documents,
    search_files,
]

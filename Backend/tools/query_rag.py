import datetime
from langchain_core.tools import tool
from utils.postgres_connection import ConnectDB

from functions.query_rag import retrieve_chunks

@tool
async def get_chunks(user_query : str):
    """
    Asynchronously retrieves chunks from the RAG vector store and uses OpenAI to respond.

    Args:
        user_query (str): The user query.

    Returns:
        Dict[str, Any]: The retrieved chunks and response.
    """
    
    response = await retrieve_chunks(user_query=user_query)
    
    return response
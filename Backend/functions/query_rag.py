import os
import openai
import qdrant_client
import asyncio
import base64
import io
import logging
import json
import threading

from dotenv import load_dotenv
from typing import Optional, List, Dict, Any
from langchain_openai import OpenAI, AzureOpenAIEmbeddings,AzureChatOpenAI
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser



from fastapi import HTTPException
import qdrant_client.models

load_dotenv()

model = AzureChatOpenAI(model="gpt-4o",
                            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                            api_version=os.getenv("AZURE_OPENAI_VERSION"),
                            max_tokens=4000)

collection_name = os.getenv("QDRANT_COLLECTION")

embeddings = AzureOpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_VERSION"),
            dimensions=1536,
        )


def connect_qdrant():
    try:
        client = qdrant_client.QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        
        )
        collection_config = qdrant_client.http.models.VectorParams(
            size=1536, 
            distance=qdrant_client.http.models.Distance.COSINE
            )
        
        logging.info("Qdrant client connected successfully.")
        return client
    except Exception as e:
        logging.error(f"Failed to connect to Qdrant: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect to Qdrant.")


async def retrieve_chunks(user_query: str, top_k: int = 2) -> Dict[str, Any]:
    """
    Asynchronously retrieves chunks from the RAG vector store and uses OpenAI to respond.

    Args:
        user_query (str): The user query.

    Returns:
        Dict[str, Any]: The retrieved chunks and response.
    """
    try:
        
        
        client = connect_qdrant()
        vectorstore = QdrantVectorStore(
            client=client,
            collection_name=collection_name,
            embedding=embeddings,
        )
        
        
        results = await vectorstore.asimilarity_search(
            user_query,
            k=top_k,
            # filter=qdrant_client.models.Filter(
            #     must=filter_condition,
            # ),
        )
        
        response = {
            "status_code": 200,
            "message": "success",
            "chunks": results,
        }
        
        logging.info(response)

        return response
        
    
    except Exception as e:
        logging.exception(f"Error retrieving chunks: {e}")
        return  {
            "status_code" : 500,
            "message" : "failed", 
        }
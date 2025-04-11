import json
import logging
import os
import uuid
import asyncio

from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel
from fastapi import Body, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
from agents.router_agent import router_agent_function
from agents.general_agent import general_agent_function
from functions.ticket_creating import create_ticket

router = APIRouter()

class ChatResponse(BaseModel):
    query : str
    user_id : str
    ticket_id : str
    query_id : str
    
class CreateTicket(BaseModel):
    query : str
    
class GeneralChat(BaseModel):
    query : str
    user_id : str
    ticket_id : str
    

@router.post("/chat")
async def get_chat_response(chat_response : ChatResponse):
    
    response = await router_agent_function(query=chat_response.query, user_id= chat_response.user_id, thread_id= chat_response.ticket_id, query_id=chat_response.query_id)
    logging.info(response)
    
    return response

@router.post("/create-ticket")
async def create_ticket_main(create_ticket_body : CreateTicket):
    
    final_response = create_ticket(query=create_ticket_body.query)
    
    return final_response

@router.post("/general-chat")
async def general_agent_chat(general_chat : GeneralChat):
    response = await general_agent_function(query= general_chat.query, user_id=general_chat.user_id, thread_id=general_chat.ticket_id)
    logging.info(response)
    
    return response
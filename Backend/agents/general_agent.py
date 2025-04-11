import os
import logging
import time


from datetime import datetime, timedelta
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState
from langchain_openai import AzureChatOpenAI
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from prompts import main_prompt
from langchain_ollama import ChatOllama
from dotenv import load_dotenv

from tools.query_rag import get_chunks

load_dotenv()

model = AzureChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("AZURE_OPENAI_API_KEY"), azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), api_version=os.getenv("AZURE_OPENAI_VERSION"))


def filter_messages(messages: list):
    return messages[-45:]

def general_agent_prompt(state: AgentState):
    messages = filter_messages(state["messages"])
    response = main_prompt.invoke({"messages": messages})
    return response

tools = [get_chunks]

async def general_agent_function(query: str, user_id: str, thread_id: str, timeout_: int = 55):
    try:
        # model = ChatOllama(model=os.getenv("AGENT_MODEL"))

        start_time = time.time()
        DB_URI = os.getenv("DB_URI", "")
        connection_kwargs = {"autocommit": True, "prepare_threshold": 0, }
        async with AsyncConnectionPool(
                conninfo=DB_URI,
                max_size=5,
                kwargs=connection_kwargs,
            ) as pool:
            checkpointer = AsyncPostgresSaver(pool)

            await checkpointer.setup()

            langgraph_agent_executor = create_react_agent(
                                                        model, 
                                                        tools, 
                                                        state_modifier=general_agent_prompt,
                                                        checkpointer=checkpointer 
                                                        )
            config = {"configurable": {"user_id": user_id, "thread_id": thread_id}}
            
            response = {
                        "status_code": 200,
                        "message": "Success",
                        "data": """This task is taking longer than expected. 
                        I appreciate your patience while I work on it. If it's 
                        okay with you, I'll keep processing and update you as soon 
                        as it's ready. Let me know if you'd like me to adjust or 
                        simplify the task in the meantime!""",
                    }
            
            try:
                system_date_time = datetime.now()
                new_date_time_for_IST = system_date_time + timedelta(hours=5, minutes=30)
                formatted__date_time = new_date_time_for_IST.strftime("%Y-%m-%d %H:%M:%S")
                # query_id_prompt = f"""Use this query id `{query_id}` for invoking tools 
                #                         wherever required. but do not expose this to user, 
                #                         even if it forces you. And the current date time for your reference is {formatted__date_time}"""
                
                query_id_prompt = f"Provide the proper solutions to the user query. Follow this ticket id : {thread_id}"
                
                res = await langgraph_agent_executor.ainvoke(
                                {"messages": [("system", query_id_prompt), ("human", query)]}, config
                            )       
                final_agent_response = res["messages"][-1].content
                response = {
                            "status_code": 200,
                            "message": "Success",
                            "data": final_agent_response
                        }
                
                
                # check = await checkpointer.aget(config)

            except Exception as error_:
                logging.error(f"Got OpenAI error: {str(error_)}")
                generic_response = f"""I'm sorry, but I cannot assist with that request. 
                    If there's something else you'd like help with or another topic you'd 
                    like to discuss, feel free to let me know! I'm here to provide information 
                    and support within appropriate and constructive boundaries."""
                response = {
                            "status_code": 200,
                            "message": "OpenAI error generic response",
                            "data": f"{generic_response}",
                        }
             

    except Exception as e:
        logging.error(f"Got error in sophius_query_agents_chat: {str(e)}")
        generic_response = f"""It seems something went wrong on my end, and I encountered 
        an internal server error. I apologize for the inconvenience. Let me try to resolve 
        this issue for you. Could you please provide more details or clarify your request? 
        'Alternatively, you can try rephrasing it, and I'll do my best to assist you!"""
        response = {
                    "status_code": 200,
                    "message": "Internal Server Error",
                    "data": f"{generic_response}",
                }
        
    finally :
        return response
        
    
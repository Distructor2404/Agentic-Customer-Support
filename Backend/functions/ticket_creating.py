from utils.llm_calling import get_gemma_response
import uuid
from utils.postgres_connection import ConnectDB
import logging


def create_ticket(query : str):
    
    ticket_id = uuid.uuid4()
    
    required_json =  """
        Identify all these fields from the user_query
    {
        "issue_category" : "Domain it covers",
        "sentiment" : "Identify the emotion from user_query",
        "priority" : 'critical','high','medium','low' anyone from this
    }
    
    """
    
    system_prompt = f"You are a Customer-Support ticket generator. You just need to Identify the keys and provide the response as a json : {required_json}"
    user_prompt = f"user_query : {query}"
        
    try :
        data_json = get_gemma_response(system_prompt=system_prompt, user_prompt=user_prompt)
        data_json["ticket_id"] = ticket_id
        
        db = ConnectDB()
        issue_category = data_json["issue_category"]
        sentiment = data_json["sentiment"]
        priority = data_json["priority"]
        
        logging.info(f"issue category : {issue_category} , sentiment: {sentiment}, priority : {priority}")
        
        create_ticket_query = [ 
                                { 
                                    "query" :  """INSERT INTO customer_support_tickets (
                                                ticket_id, issue_category, sentiment, priority, resolution_status
                                                ) VALUES ( 
                                                %s,%s,%s,%s,%s);
                                                """,
                                    "data" : (str(ticket_id), str(issue_category), str(sentiment), str(priority) , 'active'),
                                }  
                            ]
        
        create = db.insert(create_ticket_query)
        logging.info(create)
        
        return data_json
        
    except Exception as e:
        logging.info("Failed to create Ticket")
        return {
            "status" : 500,
            "error" : e
         }
    finally:    
        db.close_connection()
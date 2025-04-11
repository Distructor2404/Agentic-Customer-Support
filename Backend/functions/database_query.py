import os
import logging
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from db_connection.sql_database import ConnectSQL

if len(logging.getLogger().handlers) > 0:
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.basicConfig(level=logging.INFO)

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


async def get_sql(user_query: str, user_uuid: str) -> str:
    """
    Converts the user message to an appropriate SQL query, which would be able to fetch the required data from the Database.
    
    Args:
    user_query (str) - The message sent by the user, to the chatbot
    user_uuid - uuid from the fronted to identify user

    Returns:

        str: an SQL query that would help fetch the required info
    
    """

    modulr_database = """CREATE TABLE users (
                user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),  
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                email VARCHAR(100) UNIQUE,
                phone_number VARCHAR(15) UNIQUE,
                balance NUMERIC(12, 2) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted_at TIMESTAMP,
                modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            FOR EXAMPLE THIS IS THE SAMPLE modulr_users TABLE STRUCTURE IN CSV FORMAT:
            "user_id","first_name","last_name","email","phone_number","balance","created_at","deleted_at","modified_at"
            "0fca006e-d627-4119-a17f-7895e8f6eda1",Alice,Smith,alice.smith@example.com,"555-0101",1500.00,2024-09-03 18:00:00.782,,2024-09-03 18:00:00.782
            "543bc6d6-dba8-4198-8682-ba53136e3009",Bob,Johnson,bob.johnson@example.com,"555-0102",2500.00,2024-09-03 18:00:00.782,,2024-09-03 18:00:00.782
            

            CREATE TABLE modulr_amounts (
                amount_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),  
                amount NUMERIC(12, 2),
                currency VARCHAR(3),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted_at TIMESTAMP,
                modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            FOR EXAMPLE THIS IS THE SAMPLE modulr_amounts TABLE STRUCTURE IN CSV FORMAT:
            "amount_id","amount","currency","created_at","deleted_at","modified_at"
            "44c60ca5-433e-45f0-9e43-d60074a754b7",100.00,USD,2024-09-03 18:24:24.278,,2024-09-03 18:24:24.278
            "00380117-3dcc-4474-bccd-afad863d1d65",200.00,USD,2024-09-03 18:24:24.278,,2024-09-03 18:24:24.278

            CREATE TABLE modulr_transactions (
                transaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),  
                user_id UUID REFERENCES modulr_users(user_id),  
                amount_id UUID REFERENCES modulr_amounts(amount_id),  
                transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                transaction_type VARCHAR(10) CHECK (transaction_type IN ('credit', 'debit')),
                status VARCHAR(20) CHECK (status IN ('failed', 'paid', 'on hold')),
                source_name VARCHAR(100),
                destination_name VARCHAR(100),
                payment_mode VARCHAR(20) CHECK (payment_mode IN ('card', 'UPI', 'netbanking')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted_at TIMESTAMP,
                modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            FOR EXAMPLE THIS IS THE SAMPLE modulr_transactions TABLE STRUCTURE IN CSV FORMAT:
            "transaction_id","user_id","amount_id","transaction_date","transaction_type","status","source_name","destination_name","payment_mode","created_at","deleted_at","modified_at"
            f0b7cbb6-8c3a-4ffb-aaee-bd1752405662,"0fca006e-d627-4119-a17f-7895e8f6eda1","44c60ca5-433e-45f0-9e43-d60074a754b7",2024-09-03 18:27:23.387,credit,paid,Bank A,Vendor X,card,2024-09-03 18:27:23.387,,2024-09-03 18:27:23.387
            e865a00e-bc1e-4e75-b865-ecb6f9289a43,"543bc6d6-dba8-4198-8682-ba53136e3009","00380117-3dcc-4474-bccd-afad863d1d65",2024-09-03 18:27:23.387,debit,paid,Bank B,Vendor Y,UPI,2024-09-03 18:27:23.387,,2024-09-03 18:27:23.387
            """

 
    try:
        # Convert tenant name to lowercase for consistency
        tenant_name = tenant_name.lower()

        # Select the appropriate database based on the tenant
        if tenant_name == "modulrfinance":
            database = modulr_database
            logging.info(f"Selected database: Modulr")
        elif tenant_name == "avadolearning":
            database = avado_database
            logging.info(f"Selected database: Avado")
        elif tenant_name in {"oakbrookfinance", "salaryfinance"}:
            database = obf_database
            logging.info(f"Selected database: Oakbrook")
        else:
            raise ValueError(f"Invalid tenant name: {tenant_name}")

        # Initialize the OpenAI LLM with a controlled temperature for SQL generation
        llm = ChatOpenAI(temperature=0, model="gpt-4o")
        parser = StrOutputParser()

        # Define the system template with proper instructions for generating the query
        system_template = f"""
            You are a PostgreSQL expert. 
            Given an input question from the user, create a syntactically correct PostgreSQL query and return ONLY the generated query, nothing else.

            Always keep user_id as the filter in the query with a value of user_id = '{user_uuid}'.

            History:
            If you do not fully understand the prompt, take hints from the "History" of questions the user has asked.
            {database}

            NOTE: ---INCLUDE TRANSACTION ID if asked, DO NOT INCLUDE USER ID OR AMOUNT ID IN THE RESULT, all the amounts are in GBP---
        """

        # Construct the prompt with the system template and user's query
        prompt_template = ChatPromptTemplate.from_messages(
            [("system", system_template), ("user", f"{user_query}")]
        )

        # Create a chain that passes the prompt to the LLM and parses the result
        chain = prompt_template | llm | parser

        # Generate the SQL query asynchronously
        sql_query = await chain.ainvoke({
            "database": database,
            "user_query": user_query,
            "user_uuid": user_uuid
        })

        # Clean up the generated SQL query
        sql_query = sql_query.replace("```sql", "").replace("```", "")
        logging.info(f"Generated SQL Query: {sql_query}")

        # Execute the SQL query on the selected database
        df = ConnectSQL().execute_query(sql_query)
        logging.info("SQL query executed successfully.")

        return df

    except ValueError as ve:
        logging.error(f"Tenant selection error: {ve}")
        raise ve

    except Exception as e:
        logging.error(f"Error during SQL query generation or execution: {e}")
        raise e
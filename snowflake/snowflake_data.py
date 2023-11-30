import snowflake.connector
import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

###############################################################################
# Load variables from .env file
load_dotenv('C:\\Users\\j.videlefsky\\Documents\\DAMG7374 - GenAI and DataEng\\BiteBuddy\\.env')
# Access variables
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")

# print(SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_ACCOUNT)


def get_reviews_summary(business_name):
    # Set up connection parameters
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse='COMPUTE_WH',
        database='DAMG7374',
        schema='MART'
    )

    # Execute a query
    # business_name = 'Rod Dee Thai Cuisine'
    cursor = conn.cursor()
    cursor.execute(f"""SELECT * 
                        FROM DAMG7374.mart.bitebuddy_recs_fn
                        WHERE BUSINESS_NAME = '{business_name}'""")

    # Fetch data
    data = cursor.fetchall()

    # # Display fetched data in Streamlit
    # st.write(data)

    # Convert fetched data to a DataFrame
    df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])

    return df

import snowflake.connector
import os
from dotenv import load_dotenv

###############################################################################
# Load variables from .env file
load_dotenv('/Users/harsh/GenAI/Bitebuddy/BiteBuddy/.env')
# Access variables
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")

# print(SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_ACCOUNT)

###############################################################################
# Snowflake Connection:
def snowflake_conn():
    # Set up connection parameters
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse='STREAMLIT_WH',
        database='DAMG7374',
        # schema='MART'
    )
    return conn

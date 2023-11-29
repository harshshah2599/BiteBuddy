import snowflake.connector
import streamlit as st
import pandas as pd

def get_snowflake_data():
    # Set up connection parameters
    conn = snowflake.connector.connect(
        user='DAMG_SA',
        password='YOUR_PASSWORD',
        account='YOUR_ACCOUNT_NAME',
        warehouse='COMPUTE_WH',
        #role='DAMG_SA_ROLE',
        database='DAMG7374',
        schema='MART'
    )



    # Execute a query
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM DAMG7374.mart.test_table2")

    # Fetch data
    data = cursor.fetchall()


    # # Display fetched data in Streamlit
    # st.write(data)

    # Convert fetched data to a DataFrame
    snowflake_df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])

    return snowflake_df

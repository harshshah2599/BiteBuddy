# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 09:51:56 2023

@author: j.videlefsky
"""

import os
from dotenv import load_dotenv, dotenv_values, find_dotenv
import gzip
import json
import pandas as pd

os.getcwd()

find_dotenv()
# Load variables from .env file
load_dotenv('C:\\Users\\j.videlefsky\\Documents\\DAMG7374 - GenAI and DataEng\\BiteBuddy\\.env')

# config = dotenv_values("C:\\Users\\j.videlefsky\\Documents\\DAMG7374 - GenAI and DataEng\\.env")
# print(config)

# Print all variables
for key, value in os.environ.items():
    print(f"{key}: {value}")

# Access variables
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")

PALM_API_KEY = os.getenv("PALM_API_KEY")

# Now you can use these variables in your script
print(f"SNOWFLAKE_USER: {SNOWFLAKE_USER}")
print(f"SNOWFLAKE_PASSWORD: {SNOWFLAKE_PASSWORD}")
print(f"SNOWFLAKE_ACCOUNT: {SNOWFLAKE_ACCOUNT}")

print(f"PALM_API_KEY: {PALM_API_KEY}")




def parse(path):
    g = gzip.open(path, 'r')
    for l in g:
        yield json.loads(l)

review_dataset = []
for value in parse(path):
    review_dataset.append(value)
    
review_dataset[0:10]


# Reviews Dataset
reviews_path = 'C:\\Users\\j.videlefsky\\Downloads\\review-Massachusetts_10.json.gz'
# Business Dataset
business_path = 'C:\\Users\\j.videlefsky\\Downloads\\meta-Massachusetts.json.gz'

business_dataset = []
for value in parse(path):
    business_dataset.append(value)
    
business_dataset[0:10]

df = pd.DataFrame.from_dict(business_dataset)

def convert_to_df(path):
    dataset = []
    for value in parse(path):
        dataset.append(value)
        
    df = pd.DataFrame.from_dict(dataset)
    
    df.columns = df.columns.str.capitalize()
    
    return df

business_df = convert_to_df(business_path)
reviews_df = convert_to_df(reviews_path)

business_df.columns = business_df.columns.str.upper()
business_df.columns

reviews_df.columns = reviews_df.columns.str.upper()
reviews_df.columns


test_reviews = reviews_df.head(100)

###############################################################################
# SNOWFLAKE
import snowflake.connector
import pandas as pd
from snowflake.connector.pandas_tools import write_pandas
 

ctx = snowflake.connector.connect(
    user=SNOWFLAKE_USER,
    password=SNOWFLAKE_PASSWORD,
    account=SNOWFLAKE_ACCOUNT,
    role = 'sysadmin',
    warehouse="STREAMLIT_WH",
    database="damg7374",
    schema="raw"
    )

cs = ctx.cursor()

table = 'BUSINESS'
write_pandas(ctx, business_df, table, auto_create_table=True)

sf_review_table = 'REVIEWS'
write_pandas(ctx, reviews_df, sf_review_table, auto_create_table=True)
 

query = f"select * from {table};"
cs.execute(query)
opt = cs.fetch_pandas_all()

cs.close()





# Specify the path to your JSON file
json_file_path = 'C:\\Users\\j.videlefsky\\Downloads\\review-Massachusetts_10.json'

# Open the JSON file for reading
with open(json_file_path, "r") as json_file:
    # Load the JSON data into a Python data structure
    data = json.load(json_file)

# Now, 'data' contains the parsed JSON data
print(data)

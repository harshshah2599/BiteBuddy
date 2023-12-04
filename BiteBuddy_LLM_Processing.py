# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 09:22:00 2023

@author: j.videlefsky
"""

import os
import pandas as pd
import numpy as np
import time
import json
import ast
import re
import google.generativeai as palm
from dotenv import load_dotenv, dotenv_values, find_dotenv
###############################################################################
# Python Functions - Custom
import processing_fxns
import similarity_grouping_fxn


###############################################################################
# Load variables from .env file
load_dotenv('C:\\Users\\j.videlefsky\\Documents\\DAMG7374 - GenAI and DataEng\\BiteBuddy\\.env')
# Access variables
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")

PALM_API_KEY = os.getenv("PALM_API_KEY")

###############################################################################
# LLM - Configure the PaLM API with your API key.
palm.configure(api_key=PALM_API_KEY)

###############################################################################
# Import Data from Snowflake
# Using Snowflake Connector
import snowflake.connector

# Connect to Snowflake
conn = snowflake.connector.connect(
    user=SNOWFLAKE_USER,
    password=SNOWFLAKE_PASSWORD,
    account=SNOWFLAKE_ACCOUNT,
    warehouse='STREAMLIT_WH',
    database='DAMG7374',
    schema='STAGING',
    role='SYSADMIN'
)

# Create a cursor object to execute queries
cur = conn.cursor()

# Example query
query = 'SELECT * FROM damg7374.staging.sample_reviews'
cur.execute(query)

# Fetch the results into a Pandas DataFrame
df = cur.fetch_pandas_all()
# Display the DataFrame
print(df.head())

# Close the cursor and connection
# cur.close()
# conn.close()


###############################################################################
# Data Exploration
# Display the DataFrame
print(df.columns)
print(f'Total Records: {df.size}')


###############################################################################
# LLM Function - Get Meal Names and Sentiment
def get_meal_names(review_text):
    """Generates a list of meal names from a review text using the PaLM API.
    
    Args:
      review_text: A string containing the review text.
    
    Returns:
      A list of strings containing the meal names.
    """

    # Select a PaLM 2 model.
    models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
    model = models[0].name # models/text-bison-001
    
    # Set temperature (randomness of model)
    temperature = 0
    
    # Generate text using the PaLM 2 model.
    prompt = f"""
    Your task is to perform the following actions:
    1 - Extract each meal names and it's associated sentiment from the text delimited by triple backticks below. 
    2 - Use a sentiment scale from 0 to 1, where 0 is the most negative sentiment and 1 is the most positive sentiment.
    3 - Output as a list of lists in format [["meal names", sentiment]]
    4 - If the text does not contain a meal name, then output exactly "No Meals in Review".

    Text:
    ```{review_text}```
    """
    
    response = palm.generate_text(prompt=prompt, model=model, temperature=temperature)
    print(f'LLM Response: {response.result}')
    
    # Incorrect response format from LLM
    try:
        # Extract the meal names and sentiment from the generated text
        meal_names = ast.literal_eval(response.result)
    except:
        meal_names = ['PaLM Response is in incorrect format']
        
    # No meals in review
    if "No Meals in Review" in str(response.result):
        meal_names = ['No Meals in Review']
    
    return meal_names

###############################################################################
# # TESTING
# example_df = df[df['BUSINESS_NAME'] == """Cutty's"""][0:90].reset_index(drop=True)
# example_df['MEALS_AND_SENTIMENTS'] = example_df['REVIEW_TEXT'].apply(get_meal_names)


###############################################################################
# CODE FLOW:
review_column = 'REVIEW_TEXT'
llm_output_column = 'MEALS_AND_SENTIMENTS'

# 1. Processing Chunks - to apply the llm to the review_text column 90 records per minute
# Chunk size limited by LLM API
chunk_size = 90

def process_chunk(chunk):
    # Create a new column to store the meal names.
    chunk['MEALS_AND_SENTIMENTS'] = chunk[review_column].apply(get_meal_names)
    return chunk

# Record the start time
start_time = time.time()

# Apply the function in chunks with a 60 second break
result_df = pd.DataFrame()

for _, chunk in df.groupby(df.index // chunk_size):
    print(f'Chunk: {_}, Chunk_Size: {chunk.index}')
    processed_chunk = process_chunk(chunk)
    result_df = pd.concat([result_df, processed_chunk])
    print(f"""\n 65 Second break between processing records, due to 90 requests/minute quota. \n
          Current Records Processed: {result_df.shape[0]} \n""")
    time.sleep(65)  # 2 minutes break

# Record the stop time
stop_time = time.time()

# Calculate the elapsed time
elapsed_time = stop_time - start_time

print("Elapsed time:", elapsed_time, "seconds")


###############################################################################
# POST-PROCESSING - TODO: DO IN SNOWFLAKE?

# Use explode to transform lists into separate rows
exploded_df = example_df.explode(llm_output_column)

# Use apply along with pd.Series to split the lists into two columns
exploded_df[['MEAL_NAME', 'SENTIMENT']] = exploded_df[llm_output_column].apply(lambda x: pd.Series([x[0], x[1]] if len(x) == 2 else ['', .5]))
exploded_df.head()

### POST-PROCESSING DATA CLEANING:
# Apply the function to the text column
exploded_df.columns
exploded_df['MEAL_NAME'] = exploded_df['MEAL_NAME'].apply(processing_fxns.remove_stop_words)

# PRE-SIMILARITY SEARCH RESULTS: Use value_counts to get counts of each unique value
value_counts = exploded_df['MEAL_NAME'].value_counts()
# List of meals
exploded_df['MEALS_AND_SENTIMENTS'].tolist()
# Count of unique meal names
len(exploded_df['MEAL_NAME'].unique())


### POST-PROCESSING SIMILARITY SEARCH:
# Apply the function to the 'MEAL_NAME' from the review
post_sim_df = similarity_grouping_fxn.clustering(exploded_df, 'MEAL_NAME', 50)

# ASSIGN CLUSTER LABELS
# Group by 'CLUSTER'
# 'CLUSTER' = pick 3 (or less) random values from 'MEAL_NAME' for that cluster
cluster_labels = post_sim_df.groupby('CLUSTER')['MEAL_NAME'].apply(lambda x: list(np.random.choice(x, min(3, len(x)))))

# Merge the cluster_labels back to the original DataFrame
post_sim_df = pd.merge(post_sim_df, cluster_labels, how='left', left_on='CLUSTER', right_index=True)

# Rename Columns
post_sim_df.rename(columns={'MEAL_NAME_x': 'MEAL_NAME', 'MEAL_NAME_y': 'CLUSTER_LABEL'}, inplace=True)

# Display the result
post_sim_df.columns
# PRE-SIMILARITY SEARCH RESULTS: Use value_counts to get counts of each unique value
value_counts_cluster = post_sim_df['CLUSTER_LABEL'].value_counts()
len(value_counts_cluster)
# List of meals
exploded_df['MEALS_AND_SENTIMENTS'].tolist()








###############################################################################
# Processing Chunks - to apply the llm to the review_text column 90 records per minute
import pandas as pd
import time

# TESTING
example_df = subset_df[subset_df['BUSINESS_NAME'] == """Anna's Taqueria"""].reset_index(drop=True) # [:180]

example_df = subset_df

# Assuming your DataFrame is named 'df'
# Replace 'your_function' with the actual function you want to apply
# Replace '50' with the size of the chunks
chunk_size = 90

def process_chunk(chunk):
    # Your processing logic here
    # Create a new column to store the meal names.
    chunk['MEALS_AND_SENTIMENTS'] = chunk[review_column].apply(get_meal_names)
    # Example: Multiply a column named 'value' by 2
    # chunk['value'] = chunk['value'] * 2
    return chunk

# Record the start time
start_time = time.time()

# Apply the function in chunks with a 2-minute break
result_df = pd.DataFrame()

for _, chunk in example_df.groupby(example_df.index // chunk_size):
    print(f'Chunk: {_}, Chunk_Size: {chunk.index}')
    processed_chunk = process_chunk(chunk)
    result_df = pd.concat([result_df, processed_chunk])
    print(f"""\n 65 Second break between processing records, due to 90 requests/minute quota. \n
          Current Records Processed: {result_df.shape[0]} \n""")
    time.sleep(65)  # 2 minutes break

# Record the stop time
stop_time = time.time()

# Calculate the elapsed time
elapsed_time = stop_time - start_time

print("Elapsed time:", elapsed_time, "seconds")


# Display the resulting DataFrame
example_df = result_df


#
example_df.index //chunk_size


full_result1 = result_df # data up until index 1349, 696 total records processed
initial_example_df = example_df
example_df = example_df[1349:].reset_index(drop=True) # 11148 rows (12497-1249)



###############################################################################
# Post Processing:
def post_processing(df, llm_output_column):
    # Use explode to transform lists into separate rows
    exploded_df = df.explode(llm_output_column)

    # Use apply along with pd.Series to split the lists into two columns
    exploded_df[['MEAL_NAME', 'SENTIMENT']] = exploded_df[llm_output_column].apply(lambda x: pd.Series([x[0], x[1]] if len(x) == 2 else ['', .5]))
    # exploded_df.head()

    # Apply the function to the text column
    # exploded_df.columns
    exploded_df['MEAL_NAME'] = exploded_df['MEAL_NAME'].apply(processing_fxns.remove_stop_words)
    
    return exploded_df

# TESTING
llm_output_column = 'MEALS_AND_SENTIMENTS'
post_processing(example_df, llm_output_column)

# Use value_counts to get counts of each unique value
value_counts = exploded_df['MEAL_NAME'].value_counts()


###############################################################################
# TEMP RESULTS:
# Save sample Results
excel_file_path = 'C://Users//j.videlefsky//Documents//DAMG7374 - GenAI and DataEng//Sample_LLM_Output_Plus_Clusters_Annas.xlsx'

# Save the DataFrame to an Excel file
post_sim_df.to_excel(excel_file_path, index=False)













###############################################################################
# SCRAP:
df = exploded_df
df.columns

import pandas as pd
import nltk
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# Assuming your DataFrame is named 'df'
# Replace 'your_text_column' with the actual column name containing strings in your DataFrame
text_column = 'MEALS_AND_SENTIMENTS'

# Download NLTK resources
nltk.download('punkt')

# # Tokenization and stemming function
# def tokenize_and_stem(text):
#     tokens = nltk.word_tokenize(text)
#     stems = [PorterStemmer().stem(token) for token in tokens]
#     return stems

# # Tokenize and stem the text in the specified column
# df['tokenized_text'] = df[text_column].apply(tokenize_and_stem)

# # Convert the tokenized and stemmed text to a matrix of TF-IDF features
# tfidf_vectorizer = TfidfVectorizer(stop_words='english')
# tfidf_matrix = tfidf_vectorizer.fit_transform(df['tokenized_text'].apply(lambda x: ' '.join(x)))

# Tokenization and stemming function for phrases
def tokenize_and_stem_phrases(text):
    phrases = nltk.sent_tokenize(text)  # You might need a more sophisticated sentence tokenizer for your specific data
    stems = [' '.join([PorterStemmer().stem(word) for word in nltk.word_tokenize(phrase)]) for phrase in phrases]
    return stems

# Tokenize and stem the phrases in the specified column
df['tokenized_phrases'] = df[text_column].apply(tokenize_and_stem_phrases)

# Convert the tokenized and stemmed phrases to a matrix of TF-IDF features
tfidf_vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf_vectorizer.fit_transform(df['tokenized_phrases'].apply(lambda x: ' '.join(x)))


# Apply KMeans clustering
num_clusters = 3  # Adjust the number of clusters as needed
kmeans = KMeans(n_clusters=num_clusters)
kmeans.fit(tfidf_matrix)

# Assign the cluster labels to the DataFrame
df['cluster'] = kmeans.labels_

# Display the DataFrame with cluster assignments
print(df[['MEALS_AND_SENTIMENTS', 'cluster']])


# Use value_counts to get counts of each unique value
df.columns
value_counts2 = df['tokenized_phrases'].value_counts()







###################################3


os.getcwd()
os.chdir('C://Users//j.videlefsky//Documents//DAMG7374 - GenAI and DataEng')
excel_file_path = 'C://Users//j.videlefsky//Documents//DAMG7374 - GenAI and DataEng//Sample_LLM_Output_Plus_Clusters_Annas.xlsx'

df = pd.read_excel(excel_file_path)

review_counts = df['MEAL_NAME'].value_counts().reset_index()

len(df['REVIEW_TEXT'].unique())


group_column = 'CLUSTER_LABEL'

# Get the counts of each MEAL_NAME
meal_counts = df[group_column].value_counts().reset_index()
meal_counts.columns

# Rename the columns for clarity
meal_counts.columns = [group_column, f'{group_column}_COUNT']

# Merge the counts back into the original DataFrame
df = pd.merge(df, meal_counts, on=group_column, how='left')

# Sort the DataFrame by the count of MEAL_NAME values in descending order
df = df.sort_values(by=f'{group_column}_COUNT', ascending=False).reset_index(drop=True)


# Group by MEAL_NAME and calculate the average sentiment
average_sentiment = df.groupby(group_column)['SENTIMENT', 'RATING'].mean().reset_index()

# Merge the average sentiment back into the original DataFrame
df2 = pd.merge(df, average_sentiment, on=group_column, how='left', suffixes=('', '_avg'))


# Get distinct values across specified columns
distinct_values = df2[[group_column, f'{group_column}_COUNT', 'SENTIMENT_avg', 'RATING_avg']].drop_duplicates()

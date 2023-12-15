# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 09:22:00 2023

@author: j.videlefsky
"""

import os
import pandas as pd
import numpy as np
import time
import ast
import google.generativeai as palm
from dotenv import load_dotenv

import sys
sys.path.insert(1, '../snowflake')
from snowflake_data import *
# pip install sentence-transformers scikit-learn pandas
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering, KMeans


###############################################################################
# Load variables from .env file
load_dotenv('/Users/akshaysawant/LLM/BiteBuddy/.env')
# Access variables
PALM_API_KEY = os.getenv("PALM_API_KEY")

###############################################################################
# LLM - Configure the PaLM API with your API key.
palm.configure(api_key=PALM_API_KEY)

# Variables Use Throughout
review_column = 'REVIEW_TEXT'
llm_output_column = 'MEALS_AND_SENTIMENTS'
# Load a pre-trained BERT model from Sentence Transformers
model = SentenceTransformer('all-MiniLM-L6-v2') #('gte-tiny') #('paraphrase-MiniLM-L6-v2')

###############################################################################
# Import Data from Snowflake
# df = get_reviews_new(business_name)

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
# CODE FLOW:
def process_reviews(df, review_column='REVIEW_TEXT', llm_output_column='MEALS_AND_SENTIMENTS'):
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
        # if more than 90 records, then 65 second break
        if processed_chunk.shape[0] >= 90:
            time.sleep(65)  # 2 minutes break

    # Record the stop time
    stop_time = time.time()

    # Calculate the elapsed time
    elapsed_time = stop_time - start_time

    print("Elapsed time:", elapsed_time, "seconds")

    return result_df

# result_df = process_reviews(df, review_column, llm_output_column)


###############################################################################
# POST-PROCESSING:
def post_processing(df, llm_output_column='MEALS_AND_SENTIMENTS'):
    # Use explode to transform lists into separate rows
    df = df.explode(llm_output_column)

    # Use apply along with pd.Series to split the lists into two columns
    df[['MEAL_NAME', 'SENTIMENT']] = df[llm_output_column].apply(lambda x: pd.Series([x[0], x[1]] if len(x) == 2 else ['', .5]))
    
    # When the LLM messes up the format
    # Convert lists to strings and remove square brackets
    df[['MEAL_NAME', 'SENTIMENT']] = df[['MEAL_NAME', 'SENTIMENT']].apply(lambda x: str(x).strip('[]') if type(x) is list else x)

    # Apply the function to the text column 
    # df['MEAL_NAME'] = df['MEAL_NAME'].apply(processing_fxns.remove_stop_words)

    return df

# result_df = post_processing(df, llm_output_column)


#################################################################################
# FUNCTION FOR CLUSTERING
def clustering(df, column_name=llm_output_column, model=model, cluster_percentage=50):
    
    # Get embeddings for the terms
    embeddings = model.encode(df[column_name].astype(str).tolist(), convert_to_tensor=True)
    
    # Perform clustering using Agglomerative Clustering
    # Adjust the number of clusters (n_clusters) based on your use case
    unique_values = len(df['MEAL_NAME'].unique())
    # 66.7% of the unique values
    n_clusters = int(unique_values * cluster_percentage/100)
    # clustering = AgglomerativeClustering(n_clusters=n_clusters, affinity='cosine', linkage='average')
    clustering = KMeans(n_clusters=n_clusters)
    df['CLUSTER'] = clustering.fit_predict(embeddings)
    
    # Display the grouped DataFrame
    print(df)

    return df
    
# df = clustering(result_df, llm_output_column, model)


#################################################################################
# Assign Labels to Clusters
def assign_cluster_labels(df):
    # Group by 'BUSINESS_NAME' and 'CLUSTER'
    grouped_df = df.groupby(['BUSINESS_NAME', 'CLUSTER'])

    cluster_labels = grouped_df['MEAL_NAME'].apply(lambda x: x.mode().values[0]).reset_index()

    # Rename the column for clarity
    cluster_labels = cluster_labels.rename(columns={'MEAL_NAME': 'CLUSTER_LABEL'})

    # Merge the result back to the original DataFrame
    final_df = pd.merge(df, cluster_labels, on=['BUSINESS_NAME', 'CLUSTER'], how='left')
    
    # final_df = final_df.drop(columns=['CLUSTER_LABEL'])

    return final_df

# df = assign_cluster_labels(df)


#################################################################################
# Upload the data to Snowflake
# append snowflake table damg7374.mart.reviews_llm_output with data in df
# update_reviews(df, 'damg7374.mart.review_llm_output')
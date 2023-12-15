from snowflake_conn import snowflake_conn
from snowflake.connector.pandas_tools import write_pandas
import snowflake.connector.errors
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

###############################################################################
# Snowflake Connection:
# Functions:
def get_restaurants():
    # Set up connection parameters
    conn = snowflake_conn()
    # Execute a query
    # business_name = 'Rod Dee Thai Cuisine'
    cursor = conn.cursor()
    # used staging.sample_reviews for development
    cursor.execute(f"""SELECT distinct business_name
                        FROM DAMG7374.mart.review_llm_output
                        order by business_name
                        """)

    # Fetch data
    data = cursor.fetchall()

    # Fetch the results as a list
    restaurant_list = [row[0] for row in data]

    return restaurant_list

@st.cache_data # cache the function
def get_all_restaurants():
    # Set up connection parameters
    conn = snowflake_conn()
    # Execute a query
    # business_name = 'Rod Dee Thai Cuisine'
    cursor = conn.cursor()
    cursor.execute(f"""select distinct business_name
from damg7374.staging.reviews x
where not exists (select 1
                    from damg7374.staging.sample_reviews
                    where x.business_name = business_name)
order by 1
                        """)

    # Fetch data
    data = cursor.fetchall()

    # Fetch the results as a list
    restaurant_list = [row[0] for row in data]

    return restaurant_list



def get_reviews(business_name):
    # Set up connection parameters
    conn = snowflake_conn()

    # Execute a query
    # business_name = 'Anna's Taqueria'
    cursor = conn.cursor()
    # used sample_reviews for development
    cursor.execute(f"""SELECT business_name, review_text
                        FROM DAMG7374.staging.reviews
                        WHERE BUSINESS_NAME = '{business_name}'
                                and review_text is not null
                        LIMIT 10""")

    # Fetch data
    data = cursor.fetchall()

    # # Display fetched data in Streamlit
    # st.write(data)

    # Convert fetched data to a DataFrame
    df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])
    print(df.head())

    # Convert 'REVIEW_TEXT' column to the desired format
    formatted_reviews = "\n".join(["- " + text for text in df['REVIEW_TEXT']])

    return df, formatted_reviews



def get_reviews_new(business_name):
    # Set up connection parameters
    conn = snowflake_conn()

    # Execute a query
    # business_name = 'Oliveira''s Steak House'
    print(f'selected_restaurant - get_reviews_summary: {business_name}')
    cursor = conn.cursor()
    cursor.execute(f"""SELECT business_name, rating, review_text
                        FROM DAMG7374.staging.reviews
                        WHERE BUSINESS_NAME = '{business_name}'
                        """)

    # Fetch data
    data = cursor.fetchall()

    # Convert fetched data to a DataFrame
    df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])

    return df



def update_reviews(df, snowflake_table_name):
    # Set up connection parameters
    conn = snowflake_conn()

    # # SPECIFY THE DATABASE AND SCHEMA
    # conn.cursor().execute("USE SCHEMA damg7374.mart")

    # try:
    #     write_pandas(conn, df, snowflake_table_name, method='append')
    # except snowflake.connector.errors.Error as e:
    #     print(f"Error: {e}")
    #     print(f"Error Code: {e.errno}")
    #     print(f"SQL State: {e.sqlstate}")
    #     print(f"Error Message: {e.msg}")
    df = df[['BUSINESS_NAME', 'RATING', 'MEAL_NAME', 'SENTIMENT', 'CLUSTER', 'CLUSTER_LABEL']]
    df = df[~df['MEAL_NAME'].isnull()]
    data_tuples = list(df.itertuples(index=False, name=None))

    cursor = conn.cursor()
    try:
        for record in data_tuples:
            sql = (f"INSERT INTO {snowflake_table_name} (BUSINESS_NAME, RATING, MEAL_NAME, SENTIMENT, CLUSTER, CLUSTER_LABEL) VALUES (%s, %s, %s, %s, %s, %s)")
            cursor.execute(sql, record)
        conn.commit()
    except Exception as e:
        print(f'upload failed - exception: {e}')
    finally:
        cursor.close()

    return df



def get_reviews_summary(business_name):
    # Set up connection parameters
    conn = snowflake_conn()

    # Execute a query
    # business_name = 'Rod Dee Thai Cuisine'
    print(f'selected_restaurant - get_reviews_summary: {business_name}')
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


def recommendation_score(df):
    # NORMALIZE COLUMNS for recommendation
    # Min-Max Normalization function
    def min_max_normalize(column):
        return (column - column.min()) / (column.max() - column.min())

    # Normalize 'SENTIMENT' and 'RATING' columns and add as new columns
    df['TOTAL_REVIEWS_NORMALIZED'] = min_max_normalize(df['TOTAL_REVIEWS'])
    df['ANG_REVIEW_RATING_NORMALIZED'] = min_max_normalize(df['AVG_REVIEW_RATING'])
    df['AVG_MEAL_SENTIMENT_NORMALIZED'] = min_max_normalize(df['AVG_MEAL_SENTIMENT'])

    # Convert 'AVG_REVIEW_RATING' column to float
    df['AVG_REVIEW_RATING'] = df['AVG_REVIEW_RATING'].astype(float)
    # Define weights for each feature
    weight_total_reviews = 0.6
    weight_avg_rating = 0.3
    weight_avg_sentiment = 0.1

    # Create a recommendation score
    df['RECOMMENDATION_SCORE'] = (
        (df['TOTAL_REVIEWS'] / df['TOTAL_REVIEWS'].max()) * weight_total_reviews +
        (df['AVG_REVIEW_RATING'] / df['AVG_REVIEW_RATING'].max()) * weight_avg_rating +
        (df['AVG_MEAL_SENTIMENT'] / df['AVG_MEAL_SENTIMENT'].max()) * weight_avg_sentiment
    ) * 100

    # Factor the RLHF into the recommendation score
    def calculate_adjusted_score(row):
        if pd.notna(row['TOTAL_POS_FEEDBACK']):
            adjustment_factor = 1 + (row['TOTAL_POS_FEEDBACK'] * 0.1) - (row['TOTAL_NEG_FEEDBACK'] * 0.1) # 10% increase for each positive feedback, 10% decrease for each negative feedback
            adjusted_score = adjustment_factor * row['RECOMMENDATION_SCORE']
            if adjusted_score > 100:
                return 100
            return adjusted_score
        else:
            return row['RECOMMENDATION_SCORE']

    df['RECOMMENDATION_SCORE'] = df.apply(calculate_adjusted_score, axis=1)

    return df




def get_feedback_summary():
    # Set up connection parameters
    conn = snowflake_conn()

    # Execute a query
    # business_name = 'Rod Dee Thai Cuisine'
    cursor = conn.cursor()
    cursor.execute(f"""select create_date,
        count(distinct business_name) total_restaurants_feedback,
        count(distinct meal_name) total_meals_feedback,
        count(*) total_feedback,
        sum(case when rec_flag then 1 else 0 end) total_pos_feedback,
        sum(case when rec_flag = FALSE then 1 else 0 end) total_neg_feedback,
        round((total_pos_feedback / total_feedback)*100, 1) as positive_feedback_perc
from damg7374.mart.bitebuddy_rlhf
group by create_date
order by create_date desc""")

    # Fetch data
    data = cursor.fetchall()

    # # Display fetched data in Streamlit
    # st.write(data)

    # Convert fetched data to a DataFrame
    df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])

    return df



def get_credit_usage():
    # Set up connection parameters
    conn = snowflake_conn()

    # Execute a query
    cursor = conn.cursor()
    cursor.execute(f"""select warehouse_name,sum(credits_used) as total_credits_used 
from snowflake.account_usage.warehouse_metering_history 
where warehouse_name in ('COMPUTE_WH', 'DBT_WH', 'STREAMLIT_WH') 
group by 1 
order by 2 desc limit 10""")

    # Fetch data
    data = cursor.fetchall()

    # Convert fetched data to a DataFrame
    df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])

    return df



def get_credit_usage_month():
    # Set up connection parameters
    conn = snowflake_conn()

    # Execute a query
    cursor = conn.cursor()
    cursor.execute(f"""select date_trunc('MONTH', usage_date) as Usage_Month, sum(CREDITS_BILLED) from snowflake.account_usage.metering_daily_history group by Usage_Month""")

    # Fetch data
    data = cursor.fetchall()

    # Convert fetched data to a DataFrame
    df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])

    return df


def get_credit_usage_over_time():
    # Set up connection parameters
    conn = snowflake_conn()

    # Execute a query
    cursor = conn.cursor()
    cursor.execute(f"""select start_time::date as usage_date, warehouse_name, sum(credits_used) as total_credits_used from snowflake.account_usage.warehouse_metering_history where warehouse_name in ('COMPUTE_WH', 'DBT_WH', 'STREAMLIT_WH') group by 1,2 order by 2,1""")

    # Fetch data
    data = cursor.fetchall()

    # Convert fetched data to a DataFrame
    df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])

    return df


def post_dietary_response(restaurant, meal, question, response):
    # Set up connection parameters

    conn = snowflake_conn()

    # Execute a query
    cursor = conn.cursor()
    cursor.execute("INSERT INTO damg7374.mart.bitebuddy_dietary_responses VALUES (%s, %s, %s, %s, CURRENT_DATE())", (restaurant, meal, question, response))

    # Commit the transaction
    conn.commit()

    
def post_user_feedback(restaurant, meal, feedback):
    # Set up connection parameters
    conn = snowflake_conn()

    # Execute a query
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO damg7374.mart.bitebuddy_rlhf VALUES (%s, %s, %s, CURRENT_DATE())",
        (restaurant, meal, feedback)
    )

    # Commit the transaction
    conn.commit()

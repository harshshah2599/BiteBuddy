# import snowflake.connector
# import requests
import pandas as pd


# # Function to retrieve restaurant ID from Snowflake
# def get_restaurant_id(restaurant_name):
#     try:
#         # Establish a connection to Snowflake
#         conn = snowflake.connector.connect(
#             user='your_username',
#             password='your_password',
#             account='your_account_url',
#             warehouse='your_warehouse',
#             database='your_database',
#             schema='your_schema'
#         )

#         cursor = conn.cursor()

#         # Query Snowflake to get the restaurant ID based on the name
#         query = f"SELECT id FROM restaurants WHERE name = '{restaurant_name}'"
#         cursor.execute(query)

#         result = cursor.fetchone()

#         if result:
#             return result[0]  # Assuming 'id' is the column name in Snowflake
#         else:
#             return None

#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return None
#     finally:
#         cursor.close()
#         conn.close()

# # Function to make a request to SerpApi with the restaurant ID
# def call_serpapi(restaurant_id):
#     serpapi_api_key = 'your_serpapi_api_key'
#     serpapi_endpoint = 'https://serpapi.com/your-endpoint'

#     params = {
#         'api_key': serpapi_api_key,
#         'restaurant_id': restaurant_id,
#         # Add any other parameters you need for the SerpApi request
#     }

#     try:
#         response = requests.get(serpapi_endpoint, params=params)

#         if response.status_code == 200:
#             return response.json()  # Assuming SerpApi returns JSON data
#         else:
#             print(f"SerpApi request failed with status code: {response.status_code}")
#             return None

#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return None


def get_restaurant_names():
    # Read the CSV file into a pandas DataFrame
    data = pd.read_excel('Reviews_sample_data.xlsx')
    # Extract the necessary columns
    data = data[['GMAP_ID', 'BUSINESS_NAME']]
    # Remove duplicates
    data.drop_duplicates(subset=['GMAP_ID', 'BUSINESS_NAME'], keep='first', inplace=True)
    # Extract the restaurant names from the desired column
    restaurant_names = data['BUSINESS_NAME'].tolist()
    return restaurant_names

def get_cleaned_data():
    # Read the CSV file into a pandas DataFrame
    data = pd.read_excel('Reviews_sample_data.xlsx')
    # Extract the necessary columns
    data = data[['GMAP_ID', 'BUSINESS_NAME']]
    # Remove duplicates
    data.drop_duplicates(subset=['GMAP_ID', 'BUSINESS_NAME'], keep='first', inplace=True)
    return data
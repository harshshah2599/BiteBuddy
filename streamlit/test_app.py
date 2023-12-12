import streamlit as st
import sys
sys.path.insert(0, '../serpapi_data_ingestion')
sys.path.insert(1, '../snowflake')
from snowflake_data import *

st.header("Pick a restaurant!")
st.info("BiteBuddy Beta only has restaurants in Massachusetts", icon="ℹ️")

# Restaurants that have already been processed
st.write("Processed Restaurants:")
# select box for restaurant names
restaurant_list = get_restaurants()
selected_restaurant = st.selectbox("Select a restaurant:", restaurant_list, index=None)

# testing
# print(f"SELECT business_name, review_text FROM DAMG7374.staging.sample_reviews WHERE BUSINESS_NAME = '{selected_restaurant}' LIMIT 10")

# Restaurants that have not been processed
st.write("Search for New Restaurants:")
# Get all restaurants
restaurant_list = get_all_restaurants()

# # User input for filtering
# filter_text = st.text_input('Type to filter restaurants:')

# # Filter items based on user input
# def filter_items(prefix, all_items):
#     return [item for item in all_items if item.lower().startswith(prefix.lower())]

# filtered_items = filter_items(filter_text, restaurant_list)

# Display the multiselect dropdown with filtered items
selected_restaurant = st.selectbox('Select items:', restaurant_list, index=None)

# Display selected items
st.write('Selected items:', selected_restaurant)



if st.button(f"Get Dish Recommendations for {selected_restaurant}") and selected_restaurant:
    # Fixing restaurant name for SQL query
    selected_restaurant = selected_restaurant.replace("'", "''")
    st.write(selected_restaurant)
    print(selected_restaurant)

else:
    st.warning("Please select a restaurant first")
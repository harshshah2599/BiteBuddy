from serpapi import GoogleSearch
import pandas as pd
import sys
sys.path.insert(0, '../streamlit')
from utils import get_cleaned_data



data = get_cleaned_data()

def get_gmap_id(selected_name):
    
    # Find the corresponding Gmap_id
    result = data[data['BUSINESS_NAME'] == selected_name]
    if not result.empty:
        return result['GMAP_ID'].values[0]
    else:
        return "No Gmap_id found for this restaurant name."

def get_reviews(restaurant_name):
    selected_name = restaurant_name
    gmap_id = get_gmap_id(selected_name)
    #print(gmap_id)
    data_id = gmap_id

    params = {
    "api_key": "YOUR_SERPAPI_KEY",
    "engine": "google_maps_reviews",
    "hl": "en",
    "data_id": data_id
    }

    search = GoogleSearch(params)
    scapped_reviews = search.get_dict()
    raw_reviews_data =  scapped_reviews

    # Clean the data
    # Extract the restaurant name and snippets
    restaurant_name = raw_reviews_data['place_info']['title']
    snippets = ' '.join([review['snippet'] for review in raw_reviews_data['reviews']])
    recommended_dishes = ''.join([review.get('details', {}).get('recommended_dishes', '') for review in raw_reviews_data['reviews']])
    # print("Recommended Dishes:\n",recommended_dishes)
    # print("\n\n")
    # print("Comments:\n",snippets)
    # Create a DataFrame
    # df = pd.DataFrame({'Restaurant Name': [restaurant_name], 'Reviews': [snippets], 'Recommended Dishes':[recommended_dishes]})
    df = pd.DataFrame({'Restaurant': [restaurant_name], "People's Choice":[recommended_dishes]})

    
    
    
    # Process the snippet text
    processed_text = snippets.split(". ")  # Split the text at each full stop

    # Join the processed text with line breaks
    display_text = "\n".join(processed_text)








    return df,display_text



def get_map(restuarant_name):

    restuarant_name = restuarant_name
    params = {
    "api_key": "YOUR_SERPAPI_KEY",
    "engine": "google_local",
    "google_domain": "google.com",
    "q": restuarant_name
    }

    search = GoogleSearch(params)
    results = search.get_dict()


    # Extract latitude and longitude
    lat = results['local_results'][0]['gps_coordinates']['latitude']
    long = results['local_results'][0]['gps_coordinates']['longitude']

    return lat,long
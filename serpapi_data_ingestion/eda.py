import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import folium

def eda():
    # Load the data
    df = pd.read_excel('Reviews_sample_data.xlsx')

    # Count of Restaurants and User Reviews
    num_restaurants = len(df['BUSINESS_NAME'].unique())
    num_reviews = len(df)

    # # Average Ratings
    # avg_ratings = df.groupby('BUSINESS_NAME')['RATING'].mean()

    # Calculate average ratings
    avg_ratings = df.groupby('BUSINESS_NAME')['RATING'].mean()
    avg_ratings_df = avg_ratings.reset_index()
    avg_ratings_df.columns = ['Name', 'Rating']  # Renaming columns

    highest_avg_rating = avg_ratings.idxmax()
    lowest_avg_rating = avg_ratings.idxmin()

    # Most Popular Restaurants
    popular_restaurants = df['BUSINESS_NAME'].value_counts()
    popular_restaurants_df = popular_restaurants.reset_index()
    popular_restaurants_df.columns = ['Name', 'Reviews']  # Renaming columns
    most_reviews = popular_restaurants.idxmax()
    highest_ratings = df.groupby('BUSINESS_NAME')['RATING'].mean().idxmax()

    # User Analysis
    user_reviews = df.groupby('USER_ID').size()
    user_review_counts = user_reviews.value_counts()

    # Word Cloud for Reviews
    text = ' '.join(df['REVIEW_TEXT'].dropna().tolist())
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

    # # Geospatial Analysis
    # map_data = df[['BUSINESS_NAME', 'GMAP_ID']]
    # location_map = folium.Map(location=[42.3317, -71.1218], zoom_start=13)

    # for i in range(len(map_data)):
    #     name = map_data.iloc[i]['BUSINESS_NAME']
    #     gmap_id = map_data.iloc[i]['GMAP_ID']
    #     tooltip = f"{name}"
    #     folium.Marker(location=gmap_id, popup=name, tooltip=tooltip).add_to(location_map)

    # Display on Streamlit
    st.title('We know you are in Brookline and Hungry!👀🙂')

    # st.subheader('Count of Restaurants and User Reviews')
    st.subheader(f"Bookline has about {num_restaurants} restaurants!!🤯")
    st.subheader(f"We've got {num_reviews} user reviews to help you choose your next fav meal!😎 ")

    # Creating two columns for side-by-side display
    col1, col2 = st.columns(2)

    # Column 1: Ratings Information
    with col1:
        st.subheader('Wanna go by rating?')
        st.write(f"Highest rated place : {highest_avg_rating}")
        st.write(f"Lowest rated place : {lowest_avg_rating}")
        st.write(avg_ratings_df)

    # Column 2: Popular Restaurants Information
    with col2:
        st.subheader("Don't wanna miss the Popular ones!!")
        st.write(f"Restaurant with the Most Reviews : {most_reviews}")
        st.write(f"Restaurant with the Highest Ratings : {highest_ratings}")
        st.write(popular_restaurants_df)


    # st.subheader('User Analysis')
    # st.write("User Review Counts:")
    # st.write(user_review_counts)
    # st.write("Total User Reviews:")
    # st.write(user_reviews)

    st.subheader("What's the buzz?")
    st.set_option('deprecation.showPyplotGlobalUse', False)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    st.pyplot()

    # st.subheader('Geospatial Analysis')
    # st.write("Map of Brookline Restaurants")
    # st.write(location_map._repr_html_(), unsafe_allow_html=True)

# Additional EDA and visualizations can be included based on your specific requirements

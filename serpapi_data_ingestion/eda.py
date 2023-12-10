import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import folium
from streamlit_extras.let_it_rain import rain
from geopy.geocoders import Nominatim
from streamlit_folium import folium_static  # Import folium_static from streamlit_folium



def eda():
    # Load the data
    df = pd.read_excel('Reviews_sample_data.xlsx')

    # Count of Restaurants and User Reviews
    num_restaurants = len(df['BUSINESS_NAME'].unique())
    num_reviews = len(df)

    # # Average Ratings
    # avg_ratings = df.groupby('BUSINESS_NAME')['RATING'].mean()

    # Calculate average ratings
    avg_ratings = df.groupby('BUSINESS_NAME')['RATING'].mean().sort_values(ascending=False).head(25)
    avg_ratings_df = avg_ratings.reset_index()
    avg_ratings_df.columns = ['Name', 'Rating']  # Renaming columns

    highest_avg_rating = avg_ratings.idxmax()
    lowest_avg_rating = avg_ratings.idxmin()

    # Most Popular Restaurants
    popular_restaurants = df['BUSINESS_NAME'].value_counts().head(25)
    popular_restaurants_df = popular_restaurants.reset_index()
    popular_restaurants_df.columns = ['Name', 'Reviews']  # Renaming columns
    most_reviews = popular_restaurants.idxmax()
    highest_ratings = df.groupby('BUSINESS_NAME')['RATING'].mean().idxmax()

    # User Analysis
    user_reviews = df.groupby('USER_ID').size()
    user_review_counts = user_reviews.value_counts()

    # Word Cloud for Reviews
    text = ' '.join(df['REVIEW_TEXT'].dropna().tolist())
    # wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    wordcloud = WordCloud(
    width=700,
    height=350,
    background_color='lightgrey',
    colormap='cividis',  # Color map
    # contour_color='steelblue',  # Outline color
    # contour_width=1,  # Outline width
    contour_color=None,
    max_words=100,  # Maximum number of words
    stopwords=None  # List of stopwords to exclude (if needed)
    ).generate(text)


    # Display on Streamlit
    st.title('We know you are in Brookline and Hungry!👀🙂')

    ##### GEOSPATIAL ANALYSIS ######



    # Get the top 10 most popular restaurants
    popular_restaurants_to_map = df['BUSINESS_NAME'].value_counts().head(10)

    # Create a map
    location_map = folium.Map(location=[42.3317, -71.1218], zoom_start=13)
    geolocator = Nominatim(user_agent="restaurant_locator")

    # Focus on Brookline
    city = 'Brookline'

    for restaurant_name, count in popular_restaurants_to_map.items():
        location = geolocator.geocode(f"{restaurant_name}, {city}")
        if location:
            lat, lon = location.latitude, location.longitude
            tooltip = f"{restaurant_name}: {count} reviews"
            folium.Marker(location=[lat, lon], popup=restaurant_name, tooltip=tooltip).add_to(location_map)

    #Display the map using folium_static in Streamlit
    folium_static(location_map)



    # st.subheader('Count of Restaurants and User Reviews')
    st.info(f"Brookline has about {num_restaurants} restaurants!!🤯")
    st.info(f"We've got {num_reviews} user reviews to help you choose your next fav meal!😎 ")


    # Raining Emojis.
        
    rain(
    emoji= "🍕", # Assorted emojis
    font_size=25,
    falling_speed=3,
    animation_length=3  # Emojis will rain for 10 seconds
    )



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
    #plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    st.pyplot()

    # st.subheader('Geospatial Analysis')
    # st.write("Map of Brookline Restaurants")
    # st.write(location_map._repr_html_(), unsafe_allow_html=True)

# Additional EDA and visualizations can be included based on your specific requirements

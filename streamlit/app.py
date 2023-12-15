import streamlit as st
from auth_user import create_user,login_user, get_users
#from utils import get_diet_answers
import sys
sys.path.insert(0, '../serpapi_data_ingestion')
sys.path.insert(1, '../snowflake')
sys.path.insert(2, '../LLM')
from main import get_serpapi_reviews
from eda import eda
from snowflake_data import *
import plotly.express as px
from LLM_Processing import *
from bardapi import BardCookies
from PIL import Image
import requests
from io import BytesIO


load_dotenv('C:\\Users\\j.videlefsky\\Documents\\DAMG7374 - GenAI and DataEng\\BiteBuddy\\.env')
# Access variables
# token1 = os.getenv("ID")
# token2 = os.getenv("IDTS")
# token3 = os.getenv("IDCC")

# cookie_dict = {
#     "__Secure-1PSID": token1,
#     "__Secure-1PSIDTS": token2,
#     "__Secure-1PSIDCC": token3,
# }

# bard = BardCookies(cookie_dict=cookie_dict)



st.set_page_config(page_title="BiteBuddy", layout="wide")
with st.sidebar:
    # bitebuddy logo
    st.image('../BiteBuddy Logo.png', width=200)
    # options menu
    selected = st.selectbox("Menu", ["Log In", 'Sign Up'])
    
    # log in form
    if 'login' not in st.session_state:
        st.session_state['login'] = False




    if selected == "Log In":
        
        st.write('## Log In')
        login_username = st.text_input('Email')
        login_password = st.text_input('Password', type='password')
        # authentication status update
        if st.button('Log In!'):
            # send login request
            st.session_state['login'] = login_user(login_username,login_password)

        if st.session_state['login'] == True:
            if st.button("Logout"):
                st.session_state['login'] = False

    # # Sign-up form
    if selected == "Sign Up":
        st.write('## Sign up')
        name = st.text_input('Name')
        username = st.text_input('Email',key='signup_username')
        password = st.text_input('Password', type='password',key='signup_pass')
        confirm_password = st.text_input('Confirm Password', type='password')

        
        if st.button('Sign up'):
            if password != confirm_password:
                st.write("Passwords don't Match!")
            else:
                # send register request
                signup_status = create_user(name,username,password)
                if signup_status:
                    st.success("User Registered Successfully! Sign-in to continue...")
                else:
                    st.error("Email already exists! Sign in to continue...")

if  st.session_state['login'] != True:
    st.header("Still Staring at the Restuarant menu??😶")
    # Create two columns to display images side by side
    col1, col2 = st.columns(2)

    # Display the first image in the first column
    with col1:
        st.image('https://media.giphy.com/media/3o6MbngOgiMhf9A4xy/giphy.gif', width=500)

    # Display the second image in the second column
    with col2:
        st.image('https://media.giphy.com/media/l2JdWalFNd7IP4UKI/giphy.gif', width=500)

    st.header("Let us help... will you?")
    
if  st.session_state['login'] == True:
    st.toast("Warming up BiteBuddy...")
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Home", "Explore a Restaurant 🔎", "Feedback 📝", "Bitebuddy Pro 😎", "Bitebuddy Documentation 📃", "Monitoring 📊","Know My Restaurant (Unfiltered)😬 "])
    

   
    with tab1:
        st.title("Welcome to your.... BITEBUDDY! 🍽️")

        eda()
    with tab2:
        st.header("Pick a restaurant!")
        st.info("BiteBuddy Beta only has restaurants in Massachusetts", icon="ℹ️")

        # Restaurants that have already been processed
        st.write("Processed Restaurants:")
        # select box for restaurant names
        restaurant_list_a = get_restaurants()
        selected_restaurant_a = st.selectbox("Select a restaurant:", restaurant_list_a, index=None)
        
        # testing
        # print(f"SELECT business_name, review_text FROM DAMG7374.staging.sample_reviews WHERE BUSINESS_NAME = '{selected_restaurant}' LIMIT 10")

        # Restaurants that have already been processed
        st.write("Search for New Restaurants:")
        # Get all restaurants
        restaurant_list_b = get_all_restaurants()

        # Display the multiselect dropdown with filtered items
        selected_restaurant_b = st.selectbox('Select a restaurant:', restaurant_list_b, index=None)

        # Get the selected restaurant
        selected_restaurant = selected_restaurant_a if selected_restaurant_a else selected_restaurant_b

        st.info("If the restaurant hasn't previously been processed, the reviews will take some time to be processed", icon="ℹ️")
        if st.button(f"Get Dish Recommendations for {selected_restaurant}") and selected_restaurant:
            # Fixing restaurant name for SQL query
            selected_restaurant = selected_restaurant.replace("'", "''")
            print(f'selected_restaurant - python: {selected_restaurant}')

            st.toast('Warming up BiteBuddy...')


            # If new restaurant, get reviews and process them
            # if value for selected_restaurant_b
            if selected_restaurant_b:
                #################################################################################
                # Get reviews for the selected restaurant
                df = get_reviews_new(selected_restaurant)
                st.write("Get reviews for the selected restaurant")
                st.dataframe(df.head())
                # Estimated code run time - 90 seconds to process 90 rows
                st.write(f"Estimated full run time: {round((df.shape[0] / 90 * 90) / 60,2)} minutes")
                df = df.head(100)
                st.write(f"Estimated POC run time: {round((df.shape[0] / 90 * 90) / 60,2)} minutes")
                # Process the reviews through the LLM
                result_df = process_reviews(df)
                st.write("Process the reviews through the LLM")
                print(result_df.head())
                # Post-Processing of the LLM Output
                result_df = post_processing(result_df)
                st.write("Post-Processing of the LLM Output")
                print(result_df.head())
                # Clustering of Meal Names Results
                df = clustering(result_df)
                st.write("Clustering of Meal Names Results")
                print(df.head())
                # Assign Cluster Labels
                df = assign_cluster_labels(df)
                st.write("Assign Cluster Labels")
                print(df.head())
                # Insert into Snowflake
                update_reviews(df, 'damg7374.mart.review_llm_output')
                #################################################################################


            snowflake_df = get_reviews_summary(selected_restaurant)
            snowflake_df = recommendation_score(snowflake_df)
            # Testing
            # st.write(snowflake_df)

            # DATAFRAME CLEANING:
            # snowflake_df.rename(columns={'CLUSTER_LABEL': 'MEAL_NAME'}, inplace=True)
            snowflake_df = snowflake_df[['BUSINESS_NAME', 'MEAL_NAME', 'RECOMMENDATION_SCORE', 'TOTAL_REVIEWS', 'AVG_REVIEW_RATING', 'AVG_MEAL_SENTIMENT']].sort_values(by='RECOMMENDATION_SCORE', ascending=False)
            # List of keywords to filter out
            keywords_to_filter = ['food', 'drink', 'restaurant', '', 'price', 'breakfast', 'brunch', 'lunch', 'dinner', 'delicious', 'tasty', 'service', 'atmosphere', 'place', ]

            # Drop rows where 'MEAL_NAME' contains any of the specified keywords and 'TOTAL_REVIEWS' is less than 2 and 'MEAL_NAME' contains 'food'
            snowflake_df = snowflake_df[(~snowflake_df['MEAL_NAME'].str.lower().isin(keywords_to_filter)) & 
                                        (snowflake_df['TOTAL_REVIEWS'] >= 2) & 
                                        (~snowflake_df['MEAL_NAME'].str.contains('food', case=False))]


            st.header("Hmm, here's what people say.....")
            st.subheader("10 Most Recent Reviews:")
            df, formatted_reviews = get_reviews(selected_restaurant)
            # If there are no reviews, display a message
            if df.empty:
                st.error("Sorry, there are no reviews for this restaurant!")
                st.stop()
            # st.write(df)
            st.text_area(label="",value=formatted_reviews, height=200)

            # If there are no recommendations, display a message
            if snowflake_df.empty:
                st.error("Sorry, BiteBuddy couldn't find any recommendations for this restaurant!")
                st.stop()

            st.write("---")
            st.header("Well, here's what BITEBUDDY says.....")
            # Display the DataFrame without the index
            st.dataframe(snowflake_df, hide_index=True)
            st.divider()


            #####################################################
            # RLHF:
            #####################################################


            #####################################################
            # Dietary Restrictions:
            #####################################################
            st.info('Model: The AI model isn''t perfect, so make sure to double check the dietary restrictions output before consuming the meal!', icon="⚠️")
            questions = [
                "Does this dish contain gluten?",
                "Are there nuts in this meal?",
                "Is this dish suitable for vegetarians?",
                "Is this dish spicy?",
                # Add more questions here...
            ]
            meal_names = snowflake_df[['MEAL_NAME']]
            # Streamlit app
            st.subheader("Ask Dietary Questions about Meals")


            selected_meal = None
            selected_question = None
            

            if selected_meal is None:
                selected_meal = st.selectbox("Select your recommended meal", meal_names)

            if selected_question is None:
                selected_question = st.selectbox("Select a dietary question", questions)

            # Check if both selections have been made
            if selected_meal and selected_question:
                input_prompt = "I am eating {}. {}".format(selected_meal, selected_question)
                print("2:", input_prompt)
                bard_result = bard.get_answer(input_prompt)['content']
                print(bard_result)
                post_dietary_response(selected_restaurant,selected_meal,selected_question, bard_result)
                st.write(bard_result)
                    # st.experimental_rerun()


            # user_input = st.text_input("Ask a question to our AI bot!")

            # if st.button("Get Answer!"):
            #     # Check if user input exists and is not empty
            #     if user_input:
            #         print(user_input)
            #         user_bard_result = bard.get_answer(user_input)['content']
            #         if user_bard_result:
            #             print(user_bard_result)
            #             st.write(user_bard_result)

        else:
            st.warning("Please select a restaurant first")


    ############################################################################################################
    with tab3:
            st.header("Help us help you. We value your Feedback!")

            #select box for restaurant names
            restaurant_list = get_restaurants()
            selected_restaurant = st.selectbox("Select a restaurant to provide feedback:", restaurant_list)
            # Fixing restaurant name for SQL query
            selected_restaurant = selected_restaurant.replace("'", "''")

            snowflake_df = get_reviews_summary(selected_restaurant)
            # List of keywords to filter out
            keywords_to_filter = ['food', 'drink', 'restaurant', '', 'price', 'breakfast', 'brunch', 'lunch', 'dinner', 'delicious', 'tasty', 'service', 'atmosphere', 'place', ]

            # Drop rows where 'MEAL_NAME' contains any of the specified keywords and 'TOTAL_REVIEWS' is less than 2 and 'MEAL_NAME' contains 'food'
            snowflake_df = snowflake_df[(~snowflake_df['MEAL_NAME'].str.lower().isin(keywords_to_filter)) & 
                                        (snowflake_df['TOTAL_REVIEWS'] >= 2) & 
                                        (~snowflake_df['MEAL_NAME'].str.contains('food', case=False))]

            meal_names = snowflake_df[['MEAL_NAME']].sort_values(by='MEAL_NAME')
            selected_meal = st.selectbox("Select the meal you were recommended:", meal_names)
            

            positive_feedback = None

            if selected_meal:
                col1, col2 = st.columns(2)

                if col1.button("Yay! I liked the Bitebuddy meal recommendation"):
                    positive_feedback = 1  # Set positive feedback value to 1

                if col2.button("Nay! I disliked the Bitebuddy meal recommendation"):
                    positive_feedback = 0  # Set positive feedback value to 0 if negative

                if positive_feedback is not None:
                    st.success(f"Feedback stored: {'Positive' if positive_feedback else 'Negative'}")
                    post_user_feedback(selected_restaurant,selected_meal,positive_feedback)
                    # You can store the feedback value here in a database or use it as needed


    ############################################################################################################
    with tab4:
        st.title("BITEBUDDY x GEMINI 🚀")
        st.info('Disclaimer: This is an attempt to clone Gemini Pro functionalities into BiteBuddy and explore the future scope of our app prior to the API being available officially', icon="⚠️")
        st.subheader("Exploring multimodality with BiteBuddy....")
        block1, block2, block3 = st.tabs(["BITEVIEW 👀","FLAVORSCRIBE 📹","MENUFIND 🧾"])
        with block1:
            st.write("Some awesome food pictures? We love it.")
            prompt_with_image = st.text_input("Shoot me some questions!",key="image_questions")
            # I recently had this dish at Olive Garden but don't remember it's name. Can you tell me what this is?
            #user uploads an image
            uploaded_file = st.file_uploader("Upload an image", type=['jpg', 'jpeg', 'png', 'webp'],key="image_uploader")

            if uploaded_file is not None:

                image = uploaded_file.read()
                bard_answer = bard.ask_about_image(prompt_with_image, image)

                # Displaying the image
                if 'image' in bard_answer:
                    st.image(bard_answer['image'], caption='Answer Image')
                st.write(bard_answer['content'])

        with block2:
            st.write("Have any Food videos? We'll watch it for you.")
            youtube_url = st.text_input("Enter your video URL:")
            # https://www.youtube.com/watch?v=K9qJQmOeohU

            # What is being cooked in the video? Can you give me the reciepe followed?

            user_question = st.text_input("Shoot me a question!",key="video_questions")
            
            if st.button("Submit"):
                
                prompt = f"User question: {user_question}. YouTube URL: {youtube_url}. "
                bard_answer = bard.get_answer(prompt)
                st.write(bard_answer['content'])

        with block3:
            st.write("Upload a Menu card and let BiteBuddy do the work!")
            prompt_with_menu = st.text_input("Shoot me some questions!",key="menu_questions")

            #What do you think are the best dishes from the menu:

            #user uploads an image
            uploaded_file = st.file_uploader("Upload an image", type=['jpg', 'jpeg', 'png', 'webp'],key="menu_uploader")

            if uploaded_file is not None:

                image = uploaded_file.read()
                bard_answer = bard.ask_about_image(prompt_with_menu, image)
                st.write(bard_answer['content'])


    ############################################################################################################
    with tab5:
        st.header("**BiteBuddy**")
        st.markdown('''A personal dish recommendation app that leverages AI to help you make your choice.''')
        
        st.markdown(''' **How to use the App** : It's  just a click away!''')
        st.markdown(" 1. 💁‍♀️ Go to Explore Restaurant")
        st.markdown(" 2. 🔎 Search the restaurant you are at")
        st.markdown(" 3. 🚀 Hit the Get Recommendation tab")
        st.text(" 💃💃 Voila!!! You have a list of best dishes at your disposal!💃💃")


        
        st.subheader("**Documentation**")
        st.markdown("- 📖 [Presentation](https://wepik.com/share/9ad95fa2-c2ae-4cf0-8395-1b6dd5acddd8#rs=link)")
        st.markdown("- ⏰ [Progress Report](https://docs.google.com/presentation/d/17kCFljf3qQ_N1jVAuPRQN1Kkjuj9VNN2pcAsQIeOGnE/edit#slide=id.g28262b8e96a_2_275)")
        st.markdown("- 🛫 [Git Repo](https://github.com/LLM-App-DataEng-Group2/BiteBuddy.git) ")
        st.markdown("- 📋 [Project Report](BiteBuddy/report/BiteBuddy.pdf) ")

        st.subheader("**Data and Technologies**")
        st.image('images/image.png', width=400)
        st.image('images/llm.png', width=400) 


        
        # dummy comment

    ############################################################################################################
    with tab6:
        if login_username == "admin" and login_password =="admin":
        
            # Only have access to this tab if logged in as admin else redirect to home page
            st.title("Monitoring Dashboard")

            #####################################################
            # Feedback Monitoring:
            #####################################################
            df = get_feedback_summary()
            st.subheader("Feedback Details:")
            st.write(df)

            st.title("Feedback Over Time")

            # Bar chart
            st.bar_chart(df.set_index('CREATE_DATE')[['TOTAL_POS_FEEDBACK', 'TOTAL_NEG_FEEDBACK']])

            st.subheader("Feedback Summary:")
            # st.write(df.columns)
            # List of columns for which you want to calculate the sum
            columns_to_sum = ["TOTAL_RESTAURANTS_FEEDBACK", "TOTAL_MEALS_FEEDBACK", "TOTAL_FEEDBACK", "TOTAL_POS_FEEDBACK", "TOTAL_NEG_FEEDBACK"]

            # Calculate the sum of selected columns and create a new row in the DataFrame
            sum_row = df[columns_to_sum].sum().to_frame().T
            sum_row['POSITIVE_FEEDBACK_PERC'] = round(sum_row['TOTAL_POS_FEEDBACK'] / sum_row['TOTAL_FEEDBACK'] * 100, 1)
            st.write(sum_row)
            # st.write(sum_df)
            st.write("---")


            #####################################################
            # Snowflake Usage Monitoring:
            #####################################################
            st.subheader("Snowflake Usage Overview:")
            st.info("For more details see the Streamlit app in Snowflake - https://app.snowflake.com/pjpbfql/knb43715/#/streamlit-apps/DAMG7374.PUBLIC.NENLD3FVOT0GSA9I?ref=snowsight_shared!", icon="ℹ️")
            st.write("---")

            #############################################
            #     Credit Usage Total (Bar Chart)
            #############################################
            #Credits Usage (Total)
            total_credits_used_df = get_credit_usage()

            #Chart
            fig_credits_used=px.bar(total_credits_used_df,x='TOTAL_CREDITS_USED',y='WAREHOUSE_NAME',orientation='h',title="Credits Used by Warehouse")
            fig_credits_used.update_traces(marker_color='green')
            st.plotly_chart(fig_credits_used)

            #############################################
            #     Credits Billed by Month
            #############################################
            credits_billed_df = get_credit_usage_month()
            #st.write(credits_billed_df)
            fig_credits_billed=px.bar(credits_billed_df,x='USAGE_MONTH',y='SUM(CREDITS_BILLED)', orientation='v',title="Credits Billed by Month")
            st.plotly_chart(fig_credits_billed, use_container_width=True)

            #############################################
            #     Credits Used Overtime
            #############################################
            #Credits Used Overtime
            credits_used_overtime_df = get_credit_usage_over_time()
            #chart
            fig_credits_used_overtime_df=px.bar(credits_used_overtime_df,x='USAGE_DATE',y='TOTAL_CREDITS_USED',color='WAREHOUSE_NAME',orientation='v',title="Credits Used Overtime")
            st.plotly_chart(fig_credits_used_overtime_df, use_container_width=True)


            #############################################
            #     Total Users
            #############################################
            st.subheader("Total Users Overview:")
            get_users()
        
        else:
            st.error("Unauthorized user!")
            st.error("Only Admins can view this page!")
    

    ############################################################################################################    
    with tab7:
        #select box for restaurant names
        restaurant_list = get_restaurants()
        selected_restaurant = st.selectbox("Select a restaurant:", restaurant_list, key="serpapi_restaurants")
        if st.button("Explore!"):

        
            df, reviews, img_urls, restaurant_data = get_serpapi_reviews(selected_restaurant)

            restaurant_name = restaurant_data['place_info']['title']
            description = f"Address: {restaurant_data['place_info']['address']}\nRating: {restaurant_data['place_info']['rating']}\nReviews: {restaurant_data['place_info']['reviews']}"

            # Extract menu and links
            menu_items = [topic['keyword'] for topic in restaurant_data['topics']]
            links = [review['link'] for review in restaurant_data['reviews']]

            # Display information on Streamlit
            st.title(restaurant_name)
            st.write(description)

            # Create a DataFrame from the menu items
            data = {'Menu Items': menu_items}
            df = pd.DataFrame(data)

            # Display the DataFrame using Streamlit
            st.subheader("Popular Menu Items")
            st.dataframe(df)

            st.subheader("Links")
            for link in links:
                st.write(link)
                break


            # st.write(df)
            st.subheader("Here's what people wrote on google:")
            st.text_area(label="",value=reviews, height=200)
            st.subheader("Here's what they clicked:")
            # Display images side by side using columns
            num_images = len(img_urls)
            num_columns = 6  # Number of columns to arrange the images

            # Calculate number of rows needed
            num_rows = -(-num_images // num_columns)  # Ceiling division to get the total rows

            for i in range(num_rows):
                row_images = img_urls[i * num_columns: (i + 1) * num_columns]
                cols = st.columns(num_columns)

                for col, image_url in zip(cols, row_images):
                    with col:
                        try:
                            if image_url:  # Check if URL is not empty
                                response = requests.get(image_url)
                                img = Image.open(BytesIO(response.content))

                                # Check if the image can be opened without an error
                                img.verify()

                                # If the image is valid, display it
                                st.image(image_url, use_column_width=True)
                            else:
                                st.write("No image available")
                        except Exception as e:
                            st.write(f"Unable to display image: {image_url}")
                            st.write(f"Error: {e}")


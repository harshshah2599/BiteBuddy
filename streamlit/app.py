import streamlit as st
from auth_user import create_user,login_user
from utils import get_restaurant_names
import sys
sys.path.insert(0, '../serpapi_data_ingestion')
sys.path.insert(1, '../snowflake')
from main import get_reviews, get_map
from eda import eda
from snowflake_data import get_snowflake_data


st.set_page_config(page_title="BiteBuddy", layout="wide")
with st.sidebar:
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
    st.title("Still Staring at the restuarant menu??😶")
    st.image('images/3.webp', width=550)
    st.title("Let us help... will you?")
    
if  st.session_state['login'] == True:
    tab1, tab2 = st.tabs(["Home", "Explore a Restaurant🔎"])
    with tab1:
        st.title(" Welcome to your.... BITEBUDDY! 🍽️")

        eda()
    with tab2:
        st.header("Pick a restaurant!")

        #select box for restaurant names
        restaurant_names = get_restaurant_names()
        selected_restaurant = st.selectbox("Select a restaurant:", restaurant_names)

        if st.button("Get Dish Recommendations"):

            df,display_text = get_reviews(selected_restaurant)
            snowflake_df = get_snowflake_data()
            st.header("Hmm, here's what people say.....")
            st.write(df)
            st.subheader("User Comments:")
            st.text_area(label="",value=display_text, height=200)
            # for index, row in df.iterrows():
            #     st.write(row['Reviews'])
            st.write("---")
            st.header("Well, here's what BITEBUDDY says.....")
            st.write(snowflake_df)

# dummy comment
import streamlit as st
from auth_user import create_user,login_user
#from utils import get_restaurant_id, call_serpapi

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
    st.image('images/3.webp', width=600)
    st.title("Let us help... will you?")
    
if  st.session_state['login'] == True:
    tab1, tab2 = st.tabs(["Home", "Explore a Restaurant🔎"])
    with tab1:
        st.title(" Welcome to your.... BITEBUDDY! 🍽️")
    with tab2:
        st.title("Restaurant Information App")

        #select box for restaurant names
        selected_restaurant = st.selectbox("Select a restaurant:", ["Restaurant A", "Restaurant B", "Restaurant C"])

        if st.button("Get Dish Recommendations"):
            # Get the restaurant ID from Snowflake
            restaurant_id = get_restaurant_id(selected_restaurant)

            if restaurant_id is not None:
                # Make a request to SerpApi using the restaurant ID
                serpapi_data = call_serpapi(restaurant_id)

                if serpapi_data:
                    # Display the SerpApi data
                    st.write("Restaurant Info from SerpApi:")
                    st.write(serpapi_data)
                else:
                    st.error("Failed to retrieve data from SerpApi.")
            else:
                st.error("Restaurant not found in the database.")
            
            # st.image('1.', width=500)

# dummy comment
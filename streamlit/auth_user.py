import sqlite3
import streamlit as st
import pandas as pd


def create_user(name, username, password):
    conn = sqlite3.connect('user.db')
    c = conn.cursor()

    # Create a table to store user data
    c.execute('''CREATE TABLE IF NOT EXISTS users
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL)''')

    c.execute("INSERT INTO users (name, username, password) VALUES (?, ?, ?)", (name, username, password))

    conn.commit()
    conn.close()
    return True


def login_user(username, password):
    conn = sqlite3.connect('user.db')
    c = conn.cursor()

    # Create a table to store user data
    c.execute('''CREATE TABLE IF NOT EXISTS users
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL)''')
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    # return user
    if user == None:
        return False
    else:
        return True



def get_users():
    # Connect to the SQLite database
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()

    # Execute a query to fetch the table data
    cursor.execute('SELECT * FROM users')  # Replace 'your_table_name' with the actual table name

    # Fetch all rows from the query result
    rows = cursor.fetchall()

    # Get the column names
    columns = [description[0] for description in cursor.description]

    # Create a DataFrame from the fetched data and column names
    df = pd.DataFrame(rows, columns=columns)

    # Calculate total number of users
    total_users = len(df)

    # Display the total number of users
    st.write(f"Total users registered on BiteBuddy: {total_users}")

    # Display the DataFrame using Streamlit
    st.write(df)


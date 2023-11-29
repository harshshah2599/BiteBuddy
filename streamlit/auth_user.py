import sqlite3
import streamlit as st



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





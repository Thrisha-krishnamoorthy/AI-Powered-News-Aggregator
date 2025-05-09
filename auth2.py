import streamlit as st
from db2 import register_user, validate_user

def login_register():
    st.sidebar.title("Login / Register")

    menu = st.sidebar.radio("Select Option", ["Login", "Register"])

    if menu == "Login":
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            if validate_user(username, password):
                st.session_state['logged_in'] = True
                st.session_state['user'] = username
                st.success(f"Welcome back, {username}!")
            else:
                st.sidebar.error("Invalid credentials")

    elif menu == "Register":
        new_user = st.sidebar.text_input("Choose a Username")
        new_pass = st.sidebar.text_input("Choose a Password", type="password")
        if st.sidebar.button("Register"):
            if register_user(new_user, new_pass):
                st.sidebar.success("Registration successful! Please login.")
            else:
                st.sidebar.error("Username already exists")

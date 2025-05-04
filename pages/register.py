import streamlit as st
import requests
from firebase_auth import register
from firebase_setup import initialize_firebase

db = initialize_firebase()

# Check if user is already logged in
if "user" in st.session_state:
    st.info("You are already logged in.")
    st.switch_page("pages/dashboard.py")
    st.stop()

st.title("Register")

email = st.text_input("Email")
username = st.text_input("Username")
password = st.text_input("Password", type="password")
confirm_password = st.text_input("Confirm Password", type="password")

if st.button("Register"):
    if not email or not username or not password:
        st.error("All fields are required.")
    elif password != confirm_password:
        st.error("Passwords do not match.")
    else:
        success, error = register(email, password, username, db)
        if success:
            st.success("Registration successful! You can now log in.")
        else:
            st.error(f"Registration failed: {error}")

if st.button("Already have an account? Login"):
    st.switch_page("main.py")

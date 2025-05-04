import streamlit as st
from firebase_auth import login
from firebase_setup import initialize_firebase

db = initialize_firebase()

if "user" in st.session_state:
    st.info("You are already logged in.")
    st.switch_page("pages/register.py")
    st.stop()

# Load CSS
with open("styles/login.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("Login")

email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Login"):
    user = login(email, password)
    if user:
        st.session_state["user"] = {
            "uid": user["localId"],
            "email": user["email"],
            "idToken": user["idToken"]
        }
        st.success("Logged in successfully!")
        st.switch_page("pages/dashboard.py")

if st.button("Don't have an account yet? Register"):
    st.switch_page("pages/register.py")

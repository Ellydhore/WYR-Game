import requests
import streamlit as st

FIREBASE_WEB_API_KEY = st.secrets["firebase_key"]

def login(email, password):
    try:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        error_message = response.json()["error"]["message"]
        st.error(f"Login failed: {error_message}")
        return None

def register(email, password, username, db):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_WEB_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        uid = data["localId"]
        profile_url = f"https://api.dicebear.com/9.x/dylan/svg?seed={username}"
        db.collection("users").document(uid).set({
            "email": email,
            "username": username,
            "profile_image_url": profile_url,
        })
        return True, None
    else:
        error = response.json().get("error", {}).get("message", "Unknown error")
        return False, error

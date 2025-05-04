import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(json.loads(st.secrets["firebase_json"]))       
        firebase_admin.initialize_app(cred)
    return firestore.client()

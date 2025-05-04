import streamlit as st
from firebase_setup import initialize_firebase
from profile_utils import generate_random_avatar_url

db = initialize_firebase()

# ---------- Auth Check ----------
if "user" not in st.session_state:
    st.warning("You must log in to access the dashboard.")
    st.switch_page("main.py")
    st.stop()

uid = st.session_state["user"]["uid"]

# ---------- Fetch User Info ----------
user_ref = db.collection("users").document(uid)
user_doc = user_ref.get()

if user_doc.exists:
    user_data = user_doc.to_dict()
    username = user_data.get("username", "Unknown")
    profile_image = user_data.get("profile_image_url", "")
else:
    st.error("User data not found.")
    st.stop()

# ---------- Session State Setup ----------
if "editing_profile_pic" not in st.session_state:
    st.session_state.editing_profile_pic = False
if "temp_profile_image" not in st.session_state:
    st.session_state.temp_profile_image = profile_image

# ---------- UI ----------
st.title("🏠 Dashboard")

col1, col2 = st.columns([1, 5])
with col1:
    st.image(
        st.session_state.temp_profile_image,
        width=100,
        caption="Profile Picture"
    )

with col2:
    st.subheader(f"Username: {username}")

# ---------- Edit Button ----------
if not st.session_state.editing_profile_pic:
    if st.button("Edit Profile Pic"):
        st.session_state.editing_profile_pic = True
else:
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        if st.button("🎲 Randomize"):
            st.session_state.temp_profile_image = generate_random_avatar_url()

    with col_b:
        if st.button("💾 Save"):
            user_ref.update({"profile_image_url": st.session_state.temp_profile_image})
            profile_image = st.session_state.temp_profile_image
            st.success("Profile picture updated!")
            st.session_state.editing_profile_pic = False

    with col_c:
        if st.button("❌ Cancel"):
            st.session_state.temp_profile_image = profile_image
            st.session_state.editing_profile_pic = False

st.divider()

st.subheader("🎮 Play 'Would You Rather?'")

st.markdown("Compete with the bot!")

if st.button("Start New Game"):
    st.switch_page("pages/game.py")

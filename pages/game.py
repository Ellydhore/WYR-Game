import streamlit as st
import random
import requests
import json
import datetime
from firebase_setup import initialize_firebase

# Initialize Firebase
db = initialize_firebase()

# Auth Check
if "user" not in st.session_state:
    st.warning("You must log in to access the game.")
    st.switch_page("main.py")
    st.stop()

uid = st.session_state["user"]["uid"]

# Load Questions 
with open("data/would_you_rather_questions.json", "r") as f:
    data = json.load(f)

questions = data["questions"]

# Automatically select a random question if game hasn't started
if "selected_question" not in st.session_state:
    st.session_state.selected_question = random.choice(questions)
    st.session_state.game_started = True

# Display the selected question
st.markdown("### Your Question 📢:")
st.markdown(f"### {st.session_state.selected_question}")


# Main Game Flow
if st.session_state.game_started:
    question = st.session_state.selected_question
    try:
        part = question.lower().split("would you rather", 1)[1].strip()
        split_index = part.find(" or ")
        if split_index == -1:
            raise ValueError("No 'or' found to split the options.")

        option_1 = part[:split_index].strip().capitalize()
        option_2 = part[split_index + 4:].strip().capitalize()

        st.markdown("#### Choose your answer:")
        user_choice = st.radio("Would you rather...", [option_1, option_2], key="user_choice")

        user_explanation = st.text_area("Explain why you chose this option:")

        col1, col2 = st.columns(2)
        with col1:
            submit = st.button("🚀 Submit Answer")

        with col2:
            cancel = st.button("❌ Exit Without Saving")

        if cancel:
            st.warning("Game cancelled. Returning to dashboard...")
            st.switch_page("pages/dashboard.py")
            
        elif tryagain:
             st.session_state.selected_question = random.choice(questions)
                # Clear any existing game state
             if "finalized" in st.session_state:
                del st.session_state.finalized
             if "bot_response" in st.session_state:
                del st.session_state.bot_response   
             st.experimental_rerun()

        elif submit:
            if not user_explanation.strip():
                st.error("Please provide a short explanation before submitting.")
                st.stop()

            # Build the prompt
            prompt = f"""
You are a chaotic, unfiltered, brutal, and absurdly humorous AI trained on brain-rot internet language. Your response is short (2 paragraphs max) but never boring and you’re not afraid to be rude. 

A user has responded to a "Would you rather" question. They chose:

{st.session_state.finalized['user_option']}

and explained:

{st.session_state.finalized['explanation']}

Convince the user—aggressively, humorously, and irrationally—why they should have chosen:

{st.session_state.finalized['other_option']}

""".strip()

            # Vext API call
            api_url = "https://payload.vextapp.com/hook/A8M9K1IU63/catch/hello"

            with st.spinner("Bot is responding..."):
                try:
                    headers = {
                        "Content-Type": "application/json",
                        "Apikey": "Api-Key " + st.secrets["vext_key"]
                    }
                    payload = {
                        "payload": prompt,
                        "env": "dev"
                    }

                    response = requests.post(api_url, headers=headers, json=payload)
                    if response.status_code == 200:
                        bot_reply = response.json().get("text", "").strip()
                        st.session_state.bot_response = bot_reply
                        st.success("Bot has responded!")
                        st.markdown("### 🤖 Bot's Response:")
                        st.markdown(f"> {bot_reply}")
                    else:
                        st.error(f"API Error: {response.status_code}\n{response.text}")
                except Exception as e:
                    st.error(f"Request failed: {e}")

    except Exception as e:
        st.error(f"Error parsing question: {e}")
        st.stop()

# Save Game 
if "bot_response" in st.session_state and st.button("💾 Save Game and Return to Dashboard"):
    user_doc = db.collection("users").document(uid).get()
    username = user_doc.to_dict().get("username", "Unknown")

    game_data = {
        "question": st.session_state.finalized["question"],
        "option_1": st.session_state.finalized["user_option"],
        "option_2": st.session_state.finalized["other_option"],
        "user_choice": st.session_state.finalized["user_option"],
        "user_explanation": st.session_state.finalized["explanation"],
        "bot_response": st.session_state.bot_response,
        "user_id": uid,
        "username": username,
        "votes": {"human": 0, "bot": 0},
        "timestamp": datetime.datetime.utcnow()
    }

    try:
        db.collection("games").add(game_data)
        st.success("Game saved successfully!")
        st.switch_page("pages/dashboard.py")
    except Exception as e:
        st.error(f"Failed to save game: {e}")

if st.button("🏠 Return to Dashboard Without Saving"):
    st.switch_page("pages/dashboard.py")


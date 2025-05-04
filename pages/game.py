import streamlit as st
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

col1, col2 = st.columns([4, 1])
with col1:
    selected_question = st.selectbox(
        "Choose a 'Would you rather' question:",
        ["-- Select --"] + questions,
        index=0,
        key="question_selectbox"
    )

# Display the selected question in full
if selected_question != "-- Select --":
    st.markdown("### Selected Question 📢:")
    st.markdown(f"### *{selected_question}*")

if selected_question != "-- Select --" and st.button("✅ Start Game"):
    st.session_state.selected_question = selected_question
    st.session_state.game_started = True

# Main Game Flow
if st.session_state.get("game_started"):
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

        elif submit:
            if not user_explanation.strip():
                st.error("Please provide a short explanation before submitting.")
                st.stop()

            st.session_state.finalized = {
                "question": question,
                "user_option": user_choice,
                "other_option": option_2 if user_choice == option_1 else option_1,
                "explanation": user_explanation.strip()
            }

            # Build the prompt
            prompt = f"""
You are a chaotic, unfiltered, and absurdly humorous AI trained on brain-rot internet language. Your response is short but never boring and you’re not afraid to be ridiculous.

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
                        bot_reply = response.text.strip()
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

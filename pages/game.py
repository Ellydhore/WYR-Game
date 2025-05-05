import streamlit as st
import requests
import json
import random
import datetime
from firebase_setup import initialize_firebase

def get_bot_response(prompt):
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
                    
def get_bot_counter_response(initial_interaction, user_counter):
    """
    Get bot's response to user's counter-argument
    
    Args:
        initial_interaction (dict): Original interaction data
        user_counter (str): User's counter-argument
    """
    prompt = f"""
You are a chaotic, unfiltered, brutal, and absurdly humorous AI. 
Earlier you argued against the user's choice of "{initial_interaction['user_option']}" 
in favor of "{initial_interaction['other_option']}".

The user has counter-argued with:
{user_counter}

Respond to their counter-argument while maintaining your position. Be even more ridiculous and absurd!
Keep it short (2 paragraphs max) and entertaining!
""".strip()

    # Reuse existing API infrastructure
    return get_bot_response(prompt)

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

        col1, col2, col3= st.columns(3)
        with col1:
            submit = st.button("🚀 Submit Answer")

        with col2:
            tryagain=  st.button("🎲 Try Another Question")
        with col3:
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
             st.rerun()

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
You are a chaotic, unfiltered, brutal, and absurdly humorous AI trained on brain-rot internet language. Your response is short (1 paragraphs max) but never boring and you’re not afraid to be rude.

A user has responded to a "Would you rather" question. They chose:

{st.session_state.finalized['user_option']}

and explained:

{st.session_state.finalized['explanation']}

Convince the user—aggressively, humorously, and irrationally—why they should have chosen:

{st.session_state.finalized['other_option']}


""".strip()

            get_bot_response(prompt)
            
            if "bot_response" in st.session_state:
                    st.markdown("### 🤔 Your Turn!")
                    user_counter = st.text_area("Counter the bot's argument:", key="counter_argument")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        counter_submit = st.button("🔄 Submit Counter-Argument")
                    with col2:
                        finish_game = st.button("✅ End Game & Save")

            if counter_submit and user_counter.strip():
                # Store the counter-argument
                if "game_history" not in st.session_state:
                    st.session_state.game_history = []
                
                st.session_state.game_history.append({
                    "user_response": user_counter,
                    "initial_state": st.session_state.finalized,
                    "bot_response": st.session_state.bot_response
                })
                
                # Get bot's counter-response
                get_bot_counter_response(st.session_state.finalized, user_counter)

            elif counter_submit and not user_counter.strip():
                st.error("Please enter your counter-argument first!")


        

        

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
            "conversation_history": st.session_state.game_history if "game_history" in st.session_state else [],
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
payload.vextapp.com
Write to BBC


BBC
Mute
Search

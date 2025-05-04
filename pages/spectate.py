import streamlit as st
from firebase_setup import initialize_firebase

db = initialize_firebase()

# Get game_id from query params
query_params = st.experimental_get_query_params()
game_id = query_params.get("game_id", [None])[0]

# ---------- Auth Check ----------
if "user" not in st.session_state:
    st.warning("You must log in to spectate a game.")
    st.switch_page("main.py")
    st.stop()

# ---------- Fetch Game Data ----------
if game_id:
    game_ref = db.collection("games").document(game_id)
    game_doc = game_ref.get()

    if game_doc.exists:
        game_data = game_doc.to_dict()
        username = game_data.get("username", "Unknown")
        question = game_data.get("question", "No question")
        user_choice = game_data.get("user_choice", "No choice")
        bot_response = game_data.get("bot_response", "No response")
        votes = game_data.get("votes", {"bot": 0, "human": 0})
        bot_votes = votes.get("bot", 0)
        human_votes = votes.get("human", 0)
    else:
        st.error("Game not found.")
        st.stop()
else:
    st.error("Game ID not provided.")
    st.stop()

# ---------- Display Game Info ----------
st.title("👀 Spectate 'Would You Rather?' Game")

st.subheader(f"Question: {question}")
st.markdown(f"**Username**: {username}")
st.markdown(f"**Your Choice**: {user_choice}")
st.markdown(f"**Bot's Response**: {bot_response}")
st.markdown(f"**📊 Votes**: Bot - {bot_votes} | Human - {human_votes}")

# ---------- Voting System ----------
st.subheader("Vote for the Best Response!")

vote_option = st.radio("Who should win?", ["Bot", "Human"])

if st.button("Submit Vote"):
    if vote_option:
        # Update votes based on selection
        if vote_option == "Bot":
            game_ref.update({"votes.bot": bot_votes + 1})
        else:
            game_ref.update({"votes.human": human_votes + 1})

        st.success("Your vote has been submitted!")
        st.experimental_rerun()
    else:
        st.error("Please select a vote option.")


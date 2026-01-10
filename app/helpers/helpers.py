import streamlit as st


# ENABLES CHAT FOR USER INPUT
def enable_chat():
    st.session_state.chat_enabled = True


# POPULATES CHAT ELEMENT WITH MESSAGES FROM st.session_state.chat_history
def load_chat_history():
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# DELETES CHAT HISTORY FROM st.session_state.chat_history
def clear_chat():
    st.session_state.chat_history = []


# DELETES ATTACHED FILE, CHAT HISTORY, AND DISABLES CHAT INPUT ELEMENT
def reset_chat():
    if "file_data" in st.session_state:
        del st.session_state["file_data"]
        st.session_state.chat_history = []
        st.session_state.chat_enabled = False


def send_message(role, message):

    cleaned_msg = message.strip()
    # APPEND THE MESSAGE TO st.session_state.chat_history
    st.session_state.chat_history.append({"role": role, "content": cleaned_msg})
    # MARKDOWN DOWN THE MESSAGE
    with st.chat_message(role):
        st.markdown(cleaned_msg)

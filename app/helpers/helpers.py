import streamlit as st


def enable_chat():
    st.session_state.chat_enabled = True


def load_chat_history():
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# clear chat - clears conversation history from session data
def clear_chat():
    st.session_state.chat_history = []


# reset chat - deletes attached file, chat history, and disables the chat
def reset_chat():
    if "file_data" in st.session_state:
        del st.session_state["file_data"]
        st.session_state.chat_history = []
        st.session_state.chat_enabled = False

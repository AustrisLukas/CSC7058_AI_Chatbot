import streamlit as st
from services import openai_service
import json
from streamlit_pdf_viewer import pdf_viewer
from helpers import data_utils


# Page config
st.set_page_config(page_title="DocuMind", page_icon="💡")

# Page title and Logo
# st.image("app/assets/documind_logo.png", width=100)


# Check for if page is loaded for the first time and display appropriate welcome message
if "first_load" not in st.session_state or "file_data" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.first_load = True
    st.title("Welcome to DocuMind")
    file = st.file_uploader(
        "Upload your document to activate the chat and start asking questions. DocuMind provides clear, context-aware insights from your content.",
        type="pdf",
    )
    if file:
        st.session_state.file_data = file.read()
        st.session_state.file_name = file.name
else:
    st.title("DocuMind")


if "file_data" in st.session_state:
    if len(st.session_state.chat_history) > 0:
        user_input = st.chat_input("Type your question..")
    else:
        user_input = st.text_input("Type your question..")
else:
    user_input = st.text_input("Type your question..", disabled=True)

if user_input:
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # append user input to the chat history array
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    # markdown user input to chat (to ensure there is no delay in message appearing in chat)
    with st.chat_message("user"):
        st.markdown(user_input)
    # generate AI Response
    with st.spinner("thinking..", show_time=True):
        ai_response = openai_service.get_openai_response(
            user_input, st.session_state.chat_history
        )
    # add AI response to chat_history
    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
    # markdown AI response
    with st.chat_message("assistant"):
        st.markdown(ai_response)


def add_message(message):
    st.session_state.chat_history.append(message)

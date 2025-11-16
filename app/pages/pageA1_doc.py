import streamlit as st
from services import openai_service
import json
from streamlit_pdf_viewer import pdf_viewer
from helpers import data_utils


# Page config
st.set_page_config(page_title="DocuMind", page_icon="💡", layout="wide")

# Page title and Logo
# st.image("app/assets/documind_logo.png", width=100)

col1, col2 = st.columns([1, 6])

if "uploaded_file" not in st.session_state:
    st.session_state.chat_enabled = False
else:
    st.session_state.chat_enabled = True

if st.session_state.chat_enabled == False:
    user_input = st.chat_input(
        "Upload a document, then type a question..", disabled=True
    )
else:
    user_input = st.chat_input("Type your question..")

with col2:
    # Check for if page is loaded for the first time and display appropriate welcome message
    if "first_load" not in st.session_state or "file_data" not in st.session_state:
        st.session_state.chat_history = []
        st.session_state.first_load = True
        st.session_state.chat_enabled = False
        st.title("Welcome to DocuMind")
        st.session_state.uploaded_file = st.file_uploader(
            "Upload your document to activate the chat and start asking questions. DocuMind provides clear, context-aware insights from your content.",
            type="pdf",
        )
        if st.session_state.uploaded_file:
            st.session_state.file_data = st.session_state.uploaded_file.read()
            st.session_state.file_name = st.session_state.uploaded_file.name
            st.session_state.chat_enabled = True
    else:
        st.title("DocuMind")
        st.write(st.session_state.file_name)
        if st.button("View pdf"):
            data_utils.view_pdf(st.session_state.file_data)

    # Populate chat with messages from chat_history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_input:

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
        st.session_state.chat_history.append(
            {"role": "assistant", "content": ai_response}
        )
        # markdown AI response
        with st.chat_message("assistant"):
            st.markdown(ai_response)

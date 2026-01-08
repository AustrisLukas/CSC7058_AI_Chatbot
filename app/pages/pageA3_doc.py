import streamlit as st
from services import openai_service
import json
from streamlit_pdf_viewer import pdf_viewer
from helpers import data_utils
from helpers import helpers


# Page config
st.set_page_config(
    page_title="DocuMind",
    page_icon="app/assets/images/favicon_v2.png",
    layout="wide",
)

# Create chat enabled/disabled chat input element based on chat_enabled condition.
# Chat created outside col1,col2 to ensure it is pinned to the bottom of the view port
if "chat_enabled" in st.session_state and st.session_state.chat_enabled == True:
    user_input = st.chat_input("Type your question..")
else:
    st.session_state.chat_enabled = False
    user_input = st.chat_input(
        "Upload a document, then type a question..", disabled=True
    )

# Create col1 and col2 to separate page contents
col1, col2 = st.columns([1, 6])

# Side section (if a document is uploaded)
with col1:
    if "chat_enabled" in st.session_state and st.session_state.chat_enabled == True:
        st.button(
            "View Document",
            on_click=lambda: data_utils.view_pdf(st.session_state.file_data),
        )
        st.button("Clear Chat", on_click=helpers.clear_chat)
        st.button("Reset Chat", on_click=helpers.reset_chat)

# Main section

with col2:

    # Check for for presence of uploaded and processed (in bytes) file as 'file_data'.
    # If a document is uploaded, on_chage=helpers.enable_chat is triggered to enable chat input
    if "file_data" not in st.session_state:
        st.session_state.chat_history = []
        st.title("Welcome to DocuMind")
        st.file_uploader(
            "Upload your document to activate the chat and start asking questions. DocuMind provides clear, context-aware insights from your content.",
            type="pdf",
            key="uploaded_file",
            on_change=data_utils.process_upload,
        )
        # If user uploaded a file, proceed to process the file

    # else if 'file_data' already exists, render without file upload prompt
    else:
        st.title("DocuMind")
        st.write(st.session_state.file_name)
        # Populate chat with messages from chat_history
        chat_container = st.container(height=500)

        # helpers.load_chat_history()
        for message in st.session_state.chat_history:
            with chat_container:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        if user_input:
            # append user input to the chat history array
            st.session_state.chat_history.append(
                {"role": "user", "content": user_input}
            )
            # markdown user input to chat (to ensure there is no delay in message appearing in chat)
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(user_input)
            # generate AI Response
            with chat_container:
                with st.spinner("thinking..", show_time=True):
                    ai_response = openai_service.get_openai_response(
                        user_input, st.session_state.chat_history
                    )
            # add AI response to chat_history
            st.session_state.chat_history.append(
                {"role": "assistant", "content": ai_response}
            )
            # markdown AI response
            with chat_container:
                with st.chat_message("assistant"):
                    st.markdown(ai_response)


def send_message():

    msg_to_send = st.session_state.message.strip()

    if not msg_to_send:
        return

    st.session_state.chat_history.append({"role": "user", "content": msg_to_send})

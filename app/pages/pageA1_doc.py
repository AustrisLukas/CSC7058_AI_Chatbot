import streamlit as st
from services import openai_service
import json
from streamlit_pdf_viewer import pdf_viewer
from helpers import data_utils
from helpers import helpers


# PAGE CONFIG
st.set_page_config(
    page_title="DocuMind",
    page_icon="app/assets/images/favicon_v2.png",
    layout="wide",
)

# CREATE A CHAT INPUT ELEMENT AND DISABLE INPUT IF st.chat_enabled=False
if "chat_enabled" in st.session_state and st.session_state.chat_enabled == True:
    user_input = st.chat_input("Type your question..")
else:
    st.session_state.chat_enabled = False
    user_input = st.chat_input(
        "Upload a document, then type a question..", disabled=True
    )


#   ---***--- SIDE CONTROLS ---***---
# DISPLAY CHAT CONTROL SECTION IN THE SIDEBAR IF A VALID DOCUMENT IS UPLOADED
with st.sidebar:
    if "chat_enabled" in st.session_state and st.session_state.chat_enabled == True:
        st.header("References", divider="red")
        st.write("references here")
        st.header("Active Document", divider="violet")
        st.write(st.session_state.file_name)
        st.button(
            "View Document",
            use_container_width=True,
            on_click=lambda: data_utils.view_pdf(st.session_state.file_data),
        )
        st.button("Clear Chat", use_container_width=True, on_click=helpers.clear_chat)
        st.button("Reset Chat", use_container_width=True, on_click=helpers.reset_chat)


#   ---***--- MAIN SECTION ---***---
# CHECK FOR THE PRESENSE OF UPLOADED AND PROCESSED (in bytes) FILE IN session_state AS 'file_data'

# IF file_data IS NOT FOUND, RENDER INITIAL *WELCOME PAGE*
if "file_data" not in st.session_state:
    st.session_state.chat_history = []
    st.header("📚 Welcome to DocuMind", divider="red")
    st.subheader("Upload a document to activate the chat and start asking questions.")
    st.write("DocuMind provides clear, context-aware insights from your content.")
    col1, col2 = st.columns([6, 4])
    with col1:
        st.file_uploader(
            "document_upload",
            label_visibility="hidden",
            type=["pdf", "docx", "xlsx", "csv"],
            accept_multiple_files=False,
            key="uploaded_file",
            on_change=data_utils.process_upload,
        )

# ELSE PATHWAY IF st.session_state.file_data IS FOUND.
# RENDERS CHAT-ENABLED INTERFACE
else:
    st.header("📚 DocuMind", divider="red")
    st.markdown(
        f":green-badge[:material/check: Uploaded] "
        f":blue-badge[{st.session_state.file_name}]"
    )
    helpers.load_chat_history("documind")

    if user_input:
        helpers.send_message("user", user_input, "documind")
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

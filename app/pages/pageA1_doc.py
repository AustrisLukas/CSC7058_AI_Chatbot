import streamlit as st
from services import openai_service
import json
from streamlit_pdf_viewer import pdf_viewer
from helpers import data_utils
from helpers import helpers
from services.openai_service import OpenAIServiceError


# PAGE CONFIG
st.set_page_config(
    page_title="DocuMind",
    page_icon="app/assets/images/favicon_v2.png",
    layout="wide",
)
# FLAG FOR DOCUMENT UPLOAD ERROR
if "doc_upload_error" not in st.session_state:
    st.session_state.doc_upload_error = False
    st.session_state.doc_upload_error_msg = ""

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
        with st.popover("Start New Document", use_container_width=True):
            st.markdown("### ⚠️ End Current Session?")
            st.markdown(
                "This will end your current document session and clear all chat context. "
                "You won’t be able to recover this session once it’s reset."
            )
            st.button(
                "Start New Document",
                on_click=helpers.reset_chat,
                args=("documind",),
            )
        st.button(
            "View Document",
            use_container_width=True,
            on_click=lambda: helpers.view_document(),
        )
        st.button(
            "Clear Chat",
            use_container_width=True,
            on_click=helpers.clear_chat,
            args=("documind",),
        )
        st.header("References", divider="red")
        st.write("references here")
        st.header("Active Document", divider="violet")
        st.write(st.session_state.stored_file.name)

#   ---***--- MAIN SECTION ---***---
# CHECK FOR THE PRESENSE OF UPLOADED AND PROCESSED (in bytes) FILE IN session_state AS 'file_data'

# IF file_data IS NOT FOUND, RENDER INITIAL *WELCOME PAGE*
if "stored_file_data" not in st.session_state:
    st.session_state.chat_history = []
    st.header("📚 Welcome to DocuMind", divider="red")
    st.subheader("Upload a document to activate the chat and start asking questions.")
    st.write("DocuMind provides clear, context-aware insights from your content.")
    col1, col2 = st.columns([6, 4])
    with col1:
        st.file_uploader(
            "document_upload",
            label_visibility="hidden",
            type=["pdf", "docx", "xlsx", "csv", "pptx"],
            accept_multiple_files=False,
            key="uploaded_file",
            on_change=helpers.process_upload,
        )
        if st.session_state.doc_upload_error == True:
            st.error(
                f"**{st.session_state.doc_upload_error_msg}**\n \n"
                "Please try uploading a different document.",
                icon="⚠️",
            )


# ELSE PATHWAY IF st.session_state.file_data IS FOUND.
# RENDERS CHAT-ENABLED INTERFACE
else:
    st.header("📚 DocuMind", divider="red")
    st.markdown(
        f":green-badge[:material/check: Uploaded] "
        f":blue-badge[{st.session_state.stored_file.name}]"
    )
    helpers.load_chat_history("documind")

    if user_input:
        helpers.send_message("user", user_input, "documind")
        with st.spinner("thinking..", show_time=True):
            try:
                ai_response = helpers.get_AI_response(user_input, "documind")
                helpers.send_message("assistant", ai_response, "documind")
            except OpenAIServiceError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Something went wrong..  \n {e}")

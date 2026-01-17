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

# CREATE A CHAT INPUT ELEMENT AND DISABLE INPUT IF st.chat_enabled=False
if "webmind_enabled" in st.session_state and st.session_state.webmind_enabled == True:
    user_input = st.chat_input("Type your question..")
else:
    st.session_state.webmind_enabled = False
    user_input = st.chat_input("Upload a URL, then type a question..", disabled=True)


#   ---***--- SIDE CONTROLS ---***---
# DISPLAY CHAT CONTROL SECTION IN THE SIDEBAR IF A VALID DOCUMENT IS UPLOADED
with st.sidebar:
    if (
        "webmind_enabled" in st.session_state
        and st.session_state.webmind_enabled == True
    ):
        st.header("References", divider="red")
        st.write("references here")
        st.header("Active URL", divider="violet")
        st.write(helpers.truncate(st.session_state.validated_url, 100))
        st.button("View URL", use_container_width=True, on_click=helpers.view_URL)
        st.button(
            "Clear Chat",
            use_container_width=True,
            on_click=helpers.clear_chat,
            args=("webmind",),
        )
        st.button(
            "Reset Chat",
            use_container_width=True,
            on_click=helpers.reset_chat,
            args=("webmind",),
        )


#   ---***--- MAIN SECTION ---***---
# CHECK FOR THE PRESENSE OF UPLOADED AND PROCESSED (in bytes) FILE IN session_state AS 'file_data'

# IF file_data IS NOT FOUND, or webmind disabled, RENDER INITIAL *WELCOME PAGE*
if "validated_url" not in st.session_state or st.session_state.webmind_enabled == False:
    st.session_state.chat_history_webmind = []
    st.session_state.validated_url = ""

    st.header("🌐 Welcome to WebMind", divider="blue")
    st.subheader("Upload a URL to activate the chat and start asking questions.")
    st.write("Web provides clear, context-aware insights from your content.")

    col1, col2 = st.columns([5, 5])

    with col1:
        st.text_input(
            label="input_url",
            key="input_url",
            on_change=helpers.process_GO,
            label_visibility="collapsed",
            placeholder="https://",
        )
    with col2:
        st.button("Go!", on_click=helpers.process_GO)

# ELSE PATHWAY IF st.session_state.file_data IS FOUND.
# RENDERS CHAT-ENABLED INTERFACE
else:
    st.header("🌐  WebMind", divider="blue")
    st.markdown(
        f":green-badge[:material/check: URL Accessed] "
        f":blue-badge[{st.session_state.validated_url}]"
    )
    helpers.load_chat_history("webmind")

    if user_input:
        helpers.send_message("user", user_input, "webmind")
        with st.spinner("thinking..", show_time=True):
            try:
                ai_response = helpers.get_AI_response(user_input, "webmind")
                helpers.send_message("assistant", ai_response, "webmind")
            except OpenAIServiceError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Something went wrong..  \n {e}")

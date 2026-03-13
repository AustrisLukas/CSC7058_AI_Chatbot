import streamlit as st
from services import openai_service
import json
from streamlit_pdf_viewer import pdf_viewer
from helpers import data_utils
from helpers import helpers
from services.openai_service import OpenAIServiceError


st.session_state.setdefault("show_refs", True)
st.session_state.setdefault("ai_creativity", "Balanced")
st.session_state.setdefault("ai_response_style", "Balanced")


def process_msg_input(user_input):
    helpers.send_message("user", user_input, "webmind")
    with st.spinner("thinking..", show_time=True):
        ai_response, st.session_state.retrieval_score_webmind = helpers.get_AI_response(
            "webmind", user_input
        )
        retrieval_score_slot.progress(
            int(round(st.session_state.retrieval_score_webmind)),
            "Document Relevance Score",
        )
        st.session_state.self_evaluation_score_webmind = ai_response.get(
            "self_score", 0
        )
        self_evaluation_slot.progress(
            st.session_state.self_evaluation_score_webmind,
            "Answer Confidence (AI-Rated)",
        )

        helpers.send_message(
            "assistant",
            ai_response.get("answer", "<no answer>"),
            "webmind",
            ai_response.get("references", "<no references>"),
        )


def process_upload_with_status():
    status_slot = st.empty()
    with status_slot.container():
        with st.status("Starting document upload", expanded=True) as status:

            def on_step(msg: str):
                st.write(msg)

            try:
                helpers.process_GO(on_step=on_step)
            except Exception:
                status.update(label="Upload Failed", state="error")
                raise

        status_slot.empty()  # HIDE STATUS ELEMENT FROM PAGE AFTER COMPLETION.


# PAGE CONFIG
st.set_page_config(
    page_title="DocuMind",
    page_icon="app/assets/images/favicon_v2.png",
    layout="wide",
)

if "webmind_invalid_URL_error" not in st.session_state:
    st.session_state.webmind_invalid_URL_error = False
    st.session_state.webmind_invalid_URL_error_msg = ""

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
        with st.popover("Start New Document", use_container_width=True):
            st.markdown("### ⚠️ End Web Session?")
            st.markdown(
                "This will end your current WebMind session and clear all chat context. "
                "You won’t be able to recover this session once it’s reset."
            )
            st.button(
                "Start New WebMind Session",
                on_click=helpers.reset_chat,
                args=("webmind",),
            )
        st.button("View URL", use_container_width=True, on_click=helpers.view_URL)
        st.button(
            "Clear Chat",
            use_container_width=True,
            on_click=helpers.clear_chat,
            args=("webmind",),
        )
        # DOCUMENT RELEVANCE SCORE
        retrieval_score_slot = st.empty()
        if "retrieval_score_webmind" in st.session_state:
            retrieval_score_slot.progress(
                int(round(st.session_state.retrieval_score_webmind)),
                "Document Relevance Score",
            )
        self_evaluation_slot = st.empty()
        if "self_evaluation_score_webmind" in st.session_state:
            self_evaluation_slot.progress(
                st.session_state.self_evaluation_score_webmind,
                "Answer Confidence (AI-Rated)",
            )
        st.header("Active URL", divider="violet")
        st.write(helpers.truncate(st.session_state.validated_url, 100))

#   ---***--- MAIN SECTION ---***---
# CHECK FOR THE PRESENSE OF UPLOADED AND PROCESSED (in bytes) FILE IN session_state AS 'file_data'

# IF file_data IS NOT FOUND, or webmind disabled, RENDER INITIAL *WELCOME PAGE*
if "validated_url" not in st.session_state or st.session_state.webmind_enabled == False:
    st.session_state.chat_history_webmind = []
    st.session_state.validated_url = ""

    st.header("🌐 Welcome to WebMind", divider="blue")
    st.subheader("Upload a URL to activate the chat and start asking questions.")
    st.write("WebMind provides clear, context-aware insights from your content.")

    col1, col2 = st.columns([5, 5])

    with col1:
        st.text_input(
            label="input_url",
            key="input_url",
            on_change=process_upload_with_status,
            label_visibility="collapsed",
            placeholder="https://",
        )
        if st.session_state.webmind_invalid_URL_error == True:
            st.error(
                f"**{st.session_state.webmind_invalid_URL_error_msg}**\n \n"
                "Please check the URL and try again.",
                icon="⚠️",
            )

    with col2:
        st.button("Go!", on_click=helpers.process_GO)

# ELSE PATHWAY IF st.session_state.file_data IS FOUND.
# RENDERS CHAT-ENABLED INTERFACE
else:
    st.header("🌐  WebMind", divider="blue")
    with st.status(label="Web Source Processed", expanded=True, state="complete"):
        st.markdown(f":blue-badge[{st.session_state.validated_url}]")

    st.markdown("### 💡 Suggested questions")
    suggested_questions = st.session_state.get("suggested_questions_webmind", [])
    if isinstance(suggested_questions, str):
        suggested_questions = [suggested_questions]
    cols = st.columns(len(suggested_questions))

    helpers.load_chat_history("webmind")

    for i, q in enumerate(suggested_questions):
        if cols[i].button(q, key=f"suggested_{i}"):
            process_msg_input(q)

    if user_input:
        try:
            process_msg_input(user_input)
        except OpenAIServiceError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Something went wrong..  \n {e}")

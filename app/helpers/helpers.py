import streamlit as st
from urllib.parse import urlparse
import logging
from services import openai_service
from helpers import data_utils
from .exceptions import DocumentExtractionError
from ui.render_docx import render_docx
from ui.render_excel import render_excel
from ui.render_powerpoint import render_powerpoint
from ui.render_pdf import render_pdf


# ****** MOVE TO EXCEPTIONS
class URLValidationError(Exception):
    pass


logger = logging.getLogger(__name__)


@st.dialog("Uploaded Document")
def view_document():
    try:
        st.subheader(body=st.session_state.stored_file.name, divider="grey")
        document_type = data_utils.detect_file_type(st.session_state.stored_file)
        if document_type == "pdf":
            render_pdf()
        elif document_type == "word":
            render_docx()
        elif document_type == "excel":
            render_excel()
        elif document_type == "powerpoint":
            render_powerpoint()

    except Exception as e:
        st.error(f"**Error ocurred while rendering the document:** \n\n {e}")


# ENABLES CHAT FOR USER INPUT
def enable_chat():
    logger.info("Documind enabled")
    st.session_state.chat_enabled = True


# ENABLES WEBMIND CHAT
def enabable_webmind_chat():
    logger.info("Webmind enabled")
    st.session_state.webmind_enabled = True


# POPULATES CHAT ELEMENT WITH MESSAGES FROM st.session_state.chat_history
def load_chat_history(mode):

    if mode == "documind":
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    elif mode == "webmind":
        for message in st.session_state.chat_history_webmind:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


# DELETES CHAT HISTORY FROM st.session_state.chat_history
def clear_chat(mode):
    if mode == "documind":
        st.session_state.chat_history = []
    elif mode == "webmind":
        st.session_state.chat_history_webmind = []


# DELETES ATTACHED FILE, CHAT HISTORY, AND DISABLES CHAT INPUT ELEMENT
def reset_chat(mode):
    if mode == "documind":
        if "stored_file_data" in st.session_state:
            del st.session_state["stored_file_data"]
            clear_chat("documind")
            st.session_state.chat_enabled = False
    elif mode == "webmind":
        st.session_state.validated_url = ""
        clear_chat("webmind")
        st.session_state.webmind_enabled = False


# SANITISES AND APPENDS MESSAGE TO CHAT HISTORY, THEN DISPLAYS IN THE CHAT WINDOW
def send_message(role, message, mode):
    # CLEAN MESSAGE
    cleaned_msg = message.strip()

    if mode == "documind":
        # APPEND THE MESSAGE TO st.session_state.chat_history
        st.session_state.chat_history.append({"role": role, "content": cleaned_msg})
        # DISPLAY THE MESSAGE
        with st.chat_message(role):
            st.markdown(cleaned_msg)

    elif mode == "webmind":
        # APPEND THE MESSAGE TO st.session_state.chat_history
        st.session_state.chat_history_webmind.append(
            {"role": role, "content": cleaned_msg}
        )
        # DISPLAY THE MESSAGE
        with st.chat_message(role):
            st.markdown(cleaned_msg)


def process_upload():
    st.session_state.extracted_text = ""
    uploaded_file = st.session_state.get("uploaded_file")
    if uploaded_file:
        st.session_state.stored_file = uploaded_file
        st.session_state.stored_file_data = uploaded_file.read()
        # st.session_state.file_name = uploaded_file.name

        try:
            file_type = data_utils.detect_file_type(st.session_state.stored_file)
            if file_type == "pdf":
                st.session_state.extracted_text = data_utils.extract_pdf(uploaded_file)

            elif file_type == "word":
                st.session_state.extracted_text = data_utils.extract_docx(uploaded_file)

            elif file_type == "csv":
                st.session_state.extracted_text = data_utils.extract_csv(uploaded_file)

            elif file_type == "excel":
                st.session_state.extracted_text = data_utils.extract_excel(
                    uploaded_file
                )
            elif file_type == "powerpoint":
                print("extract pptx")
                st.session_state.extracted_text = data_utils.extract_pptx(uploaded_file)
            # enable chat if extraction was sucesful
            if st.session_state.extracted_text:
                enable_chat()
                st.session_state.doc_upload_error = False
                st.session_state.doc_upload_error_msg = ""
            else:
                print(
                    f"session_state.extracted_text = {st.session_state.extracted_text}"
                )

        except DocumentExtractionError as e:
            logging.error(f"Error while processing document upload: {e}")
            st.session_state.doc_upload_error = True
            st.session_state.doc_upload_error_msg = e
            reset_chat("documind")

        except Exception as e:
            print("Caught a generic error while extracting document")
            print(e)


# CALLS OPENAI OBJECT WITH A USER MESSAGE AND GETS RESPONSE
def get_AI_response(user_input, mode):
    if mode == "documind":
        return openai_service.get_openai_response(
            user_input, st.session_state.chat_history
        )
    elif mode == "webmind":
        return openai_service.get_openai_response(
            user_input, st.session_state.chat_history_webmind
        )


# CHECKS URL VALIDITY BY CONFIRMING HAS HAS SCHEME AND DOMAIN. BOTH MUST BE TRUE
def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    has_scheme = parsed.scheme in ("http", "https")
    has_domain = parsed.netloc != ""
    return has_scheme and has_domain


def process_GO():
    try:
        if is_valid_url(st.session_state.get("input_url")):
            st.session_state.validated_url = st.session_state.get("input_url")
            st.session_state.webmind_invalid_URL_error = ""
            enabable_webmind_chat()
        else:
            logger.error("URL format is not valid.")
            raise URLValidationError("The provided URL is not a valid format.")
    except URLValidationError as e:
        st.session_state.webmind_invalid_URL_error = True
        st.session_state.webmind_invalid_URL_error_msg = e


def truncate(text, max_len):
    return text if len(text) <= max_len else text[:max_len] + "..."


@st.dialog("Active URL")
def view_URL():
    st.write(st.session_state.validated_url)

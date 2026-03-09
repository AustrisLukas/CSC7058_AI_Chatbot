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
from helpers import document_service
import time
from backend.ingestion.chunking import chunk_text
from backend.embeddings.embedder import embed_chunks
from backend.pipeline.pipeline import run_rag_pipeline
import requests


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
    logger.info("documind chat interface enabled")
    st.session_state.chat_enabled = True


def clear_upload_error():
    logger.info("document upload error flag set to False")
    st.session_state.doc_upload_error = False
    st.session_state.doc_upload_error_msg = ""


def set_upload_error(error):
    logger.warning("document upload error flag set to True")
    st.session_state.doc_upload_error = True
    st.session_state.doc_upload_error_msg = error


# ENABLES WEBMIND CHAT
def enabable_webmind_chat():
    logger.info("webmind chat interface enabled")
    st.session_state.webmind_enabled = True


# POPULATES CHAT ELEMENT WITH MESSAGES FROM st.session_state.chat_history
def load_chat_history(mode):

    mode_pointer = get_mode(mode)

    for message in mode_pointer:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            refs = message.get("references")

            if (
                message["role"] == "assistant"
                and refs
                and st.session_state.show_refs == True
            ):
                with st.popover(f"View References"):
                    st.markdown(format_ref(refs))
                    # st.write(refs)


def format_ref(refs):
    if not refs:
        return ""

    formatted = "\n\n".join(
        f"> **Reference {i}**: {ref}" for i, ref in enumerate(refs, start=1)
    )
    return formatted


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
            del st.session_state["retrieval_score"]
            st.session_state["self_evaluation_score"]
            clear_chat("documind")
            st.session_state.chat_enabled = False
            logger.info(f"Chat reset request completed for {mode}")
    elif mode == "webmind":
        st.session_state.validated_url = ""
        clear_chat("webmind")
        st.session_state.webmind_enabled = False
        logger.info(f"Chat reset request completed for {mode}")


# SANITISES AND APPENDS MESSAGE TO CHAT HISTORY, THEN DISPLAYS IN THE CHAT WINDOW
def send_message(role, message, mode, references=None):

    # CLEAN MESSAGE
    cleaned_msg = message.strip()
    mode_pointer = get_mode(mode)

    mode_pointer.append(
        {
            "role": role,
            "content": cleaned_msg,
            "references": references if role == "assistant" else None,
        }
    )
    with st.chat_message(role):
        body_slot = st.empty()
        refs_slot = st.empty()

        body_slot.markdown(cleaned_msg)
        if role == "assistant" and references and st.session_state.show_refs == True:
            with refs_slot.popover("View References"):
                st.markdown(format_ref(references))


def get_mode(mode):
    if mode == "documind":
        return st.session_state.chat_history
    if mode == "webmind":
        return st.session_state.chat_history_webmind
    raise ValueError(f"Unsupported mode: {mode}")


def process_upload(on_step=None):
    def step(msg):
        if on_step:
            on_step(msg)

    # st.session_state.extracted_text = ""
    uploaded_file = st.session_state.get("uploaded_file")
    if not uploaded_file:
        raise DocumentExtractionError("Uploaded file not found.")
    st.session_state.stored_file = uploaded_file
    st.session_state.stored_file_data = uploaded_file.read()

    try:

        extracted_text, chunked_text, chunk_embeddings, store = (
            document_service.build_doc_pipeline(file=uploaded_file, on_step=on_step)
        )
        st.session_state.extracted_text = extracted_text
        st.session_state.chunked_text = chunked_text
        st.session_state.chunk_embeddings = chunk_embeddings
        st.session_state.vector_store = store

        enable_chat()
        clear_upload_error()

    except DocumentExtractionError as e:
        logging.error(f"Error while processing document upload: {e}")
        set_upload_error(e)
        reset_chat("documind")

    except Exception as e:
        print("Error encoutered while extracting text from the document")
        set_upload_error(e)
        reset_chat("documind")
        print(e)


# CALLS OPENAI OBJECT WITH A USER MESSAGE AND GETS RESPONSE
def get_AI_response(mode, user_input):
    if mode == "documind":
        response, retrieval_score = run_rag_pipeline(
            query=user_input,
            messages=st.session_state.chat_history,
            store=st.session_state.vector_store,
            k=5,
        )
        return response, retrieval_score
    elif mode == "webmind":
        response, retrieval_score = run_rag_pipeline(
            query=user_input,
            messages=st.session_state.chat_history_webmind,
            store=st.session_state.web_vector_store,
            k=5,
        )
        return response, retrieval_score
        return openai_service.get_openai_response(
            user_input, st.session_state.chat_history_webmind
        )


# CHECKS URL VALIDITY BY CONFIRMING HAS HAS SCHEME AND DOMAIN. BOTH MUST BE TRUE
def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    has_scheme = parsed.scheme in ("http", "https")
    has_domain = parsed.netloc != ""
    if has_scheme and has_domain:
        logger.info("URL format check PASS")
        return True
    else:
        logger.warning("URL format check FAIL")
        raise URLValidationError("The provided URL is not a valid format.")


# CHECKS IF URL IS ACCESSIBLE
def is_accessible_URL(url: str) -> bool:

    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        if response.status_code == 405:
            response = requests.get(url, stream=True, timeout=5)

        if response.status_code == 200:
            logger.info("URL .head or .get request PASS")
            return True
        else:
            logger.warning("Provided URL is not responding to .head or .get request")
            raise URLValidationError("The provided URL is not responding")
    except requests.RequestException:
        raise URLValidationError("An error occured while checking URL accessibility")


def process_GO(on_step=None):

    def step(msg):
        if on_step:
            on_step(msg)

    try:
        step("Validating URL")
        time.sleep(2)
        is_valid_url(st.session_state.get("input_url"))
        is_accessible_URL(st.session_state.get("input_url"))
        st.session_state.validated_url = st.session_state.get("input_url")
        st.session_state.webmind_invalid_URL_error = ""

        extracted_text, chunked_text, chunk_embeddings, store = (
            document_service.build_doc_pipeline(
                url=st.session_state.validated_url, on_step=on_step
            )
        )

        st.session_state.web_extracted_text = extracted_text
        st.session_state.web_chunked_text = chunked_text
        st.session_state.web_chunk_embeddings = chunk_embeddings
        st.session_state.web_vector_store = store

        enabable_webmind_chat()

    except URLValidationError as e:
        st.session_state.webmind_invalid_URL_error = True
        st.session_state.webmind_invalid_URL_error_msg = e
    except DocumentExtractionError as e:
        st.session_state.webmind_invalid_URL_error = True
        st.session_state.webmind_invalid_URL_error_msg = e
    except Exception as e:
        st.session_state.webmind_invalid_URL_error = True
        st.session_state.webmind_invalid_URL_error_msg = e


def truncate(text, max_len):
    return text if len(text) <= max_len else text[:max_len] + "..."


@st.dialog("Active URL")
def view_URL():
    st.write(st.session_state.validated_url)

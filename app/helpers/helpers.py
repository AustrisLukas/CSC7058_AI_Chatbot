import streamlit as st
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


# ENABLES CHAT FOR USER INPUT
def enable_chat():
    st.session_state.chat_enabled = True


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
        if "file_data" in st.session_state:
            del st.session_state["file_data"]
            clear_chat("documind")
            st.session_state.chat_enabled = False
    elif mode == "webmind":
        st.session_state.validated_url = ""
        clear_chat("webmind")
        st.session_state.webmind_enabled = False


def send_message(role, message, mode):
    cleaned_msg = message.strip()

    if mode == "documind":
        # APPEND THE MESSAGE TO st.session_state.chat_history
        st.session_state.chat_history.append({"role": role, "content": cleaned_msg})
        # MARKDOWN DOWN THE MESSAGE
        with st.chat_message(role):
            st.markdown(cleaned_msg)

    elif mode == "webmind":
        # APPEND THE MESSAGE TO st.session_state.chat_history
        st.session_state.chat_history_webmind.append(
            {"role": role, "content": cleaned_msg}
        )
        # MARKDOWN DOWN THE MESSAGE
        with st.chat_message(role):
            st.markdown(cleaned_msg)


# CHECKS URL VALIDITY BY CONFIRMING HAS HAS SCHEME AND DOMAIN. BOTH MUST BE TRUE
def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    has_scheme = parsed.scheme in ("http", "https")
    has_domain = parsed.netloc != ""
    return has_scheme and has_domain


def enabable_webmind_chat():
    logger.info("WebMind enabled")
    st.session_state.webmind_enabled = True


def process_GO():
    if is_valid_url(st.session_state.get("input_url")):
        st.session_state.validated_url = st.session_state.get("input_url")
        enabable_webmind_chat()
    else:
        logger.error("Input URL is not valid")


def truncate(text, max_len):
    return text if len(text) <= max_len else text[:max_len] + "..."


@st.dialog("Active URL")
def view_URL():
    st.write(st.session_state.validated_url)

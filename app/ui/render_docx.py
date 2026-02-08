import streamlit as st


def render_docx():
    element = st.text_area(
        label="",
        value=st.session_state.extracted_text,
        disabled=True,
        height="content",
    )

    return element

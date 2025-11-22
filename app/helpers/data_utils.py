import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
from helpers import helpers


@st.dialog("Uploaded Document")
def view_pdf(file):
    pdf_viewer(file)


def process_upload():
    uploaded_file = st.session_state.get("uploaded_file")
    if uploaded_file:
        st.session_state.file_data = uploaded_file.read()
        st.session_state.file_name = uploaded_file.name
        helpers.enable_chat()

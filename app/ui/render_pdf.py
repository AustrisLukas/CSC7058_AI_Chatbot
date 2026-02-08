from streamlit_pdf_viewer import pdf_viewer
import streamlit as st


def render_pdf():
    return pdf_viewer(st.session_state.stored_file_data)

import streamlit as st
from streamlit_pdf_viewer import pdf_viewer


@st.dialog("Uploaded Document")
def view_pdf(file):
    pdf_viewer(file)

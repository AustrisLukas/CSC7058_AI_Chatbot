import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
from helpers import helpers
from pypdf import PdfReader
from pathlib import Path
import re
import docx
import pandas as pd
import logging


class DocumentExtractionError(Exception):
    pass


logger = logging.getLogger(__name__)


@st.dialog("Uploaded Document")
def view_pdf(file):
    pdf_viewer(file)


def process_upload():
    st.session_state.extracted_text = ""
    uploaded_file = st.session_state.get("uploaded_file")
    if uploaded_file:
        st.session_state.stored_file = uploaded_file
        st.session_state.stored_file_data = uploaded_file.read()
        # st.session_state.file_name = uploaded_file.name
        helpers.enable_chat()
        file_type = detect_file_type(st.session_state.stored_file)

        try:
            if file_type == "pdf":
                st.session_state.extracted_text = extract_pdf(uploaded_file)

            if file_type == "word":
                st.session_state.extracted_text = extract_docx(uploaded_file)

            if file_type == "csv":
                st.session_state.extracted_text = extract_csv(uploaded_file)

            if file_type == "excel":
                st.session_state.extracted_text = extract_excel(uploaded_file)
        except DocumentExtractionError as e:
            logging.error(f"Error while processing document upload: {e}")
            st.session_state.doc_upload_error = True
            st.session_state.doc_upload_error_msg = e
            helpers.reset_chat("documind")

        except Exception as e:
            print("Caught a generic error while extracting document")


def detect_file_type(file):
    EXTENSION_MAP = {
        ".pdf": "pdf",
        ".txt": "text",
        ".docx": "word",
        ".doc": "word",
        ".pptx": "powerpoint",
        ".ppt": "powerpoint",
        ".xlsx": "excel",
        ".xls": "excel",
        ".csv": "csv",
    }
    MIME_MAP = {
        "application/pdf": "pdf",
        "text/plain": "text",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "word",
        "application/msword": "word",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": "powerpoint",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "excel",
        "text/csv": "csv",
    }

    extension = Path(file.name).suffix.lower()
    mime = file.type
    extension_type = EXTENSION_MAP.get(extension)
    mime_type = MIME_MAP.get(mime)

    if extension_type and mime_type and extension_type == mime_type:
        return extension_type
    if extension_type and not mime_type:
        return extension_type

    raise ValueError("Unsupported or mismatch file type")


def extract_pdf(file):
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        # .pdf SPECIFIC CLEAN UP
        text = text.replace("\n", " ")  # MERGE LINES
        text = re.sub(r"\s", " ", text)  # COLLAPSE MULTIPLE SPACES
        text = re.sub(r"Page \d+ of \d+", "", text)  # REMOVE PAGE NUMBERS
        text = text.strip()

        if not text:
            raise DocumentExtractionError("No text could be extracted from the PDF.")
        return text
    except Exception as e:
        raise DocumentExtractionError(f"Document Processing Error: {e}") from e


def extract_docx(doc):
    try:
        doc = docx.Document(doc)
        text = ""
        for p in doc.paragraphs:
            if p.text:
                text += p.text + " "

        text = text.replace("\n", " ")  # MERGE LINES
        text = re.sub(r"\s", " ", text)  # COLLAPSE MULTIPLE SPACES

        if not text:
            raise DocumentExtractionError(
                "No text could be extracted from the document."
            )
        return text
    except Exception as e:
        raise DocumentExtractionError(f"Document Processing Error: {e}") from e


def extract_csv(file):

    try:
        text = ""
        file.seek(0)  # set reader pointer to 0
        df = pd.read_csv(file)
        df = df.fillna("")  # fill empty cells with string
        df = df.astype(str)  # ensure all data types are string
        text = " ".join(df.agg(" ".join, axis=1))  # combine in one string

        if not text:
            raise DocumentExtractionError(
                "No text could be extracted from the CSV file."
            )
        return text
    except Exception as e:
        raise DocumentExtractionError(f"Document Processing Error: {e}") from e


def extract_excel(file):
    try:
        text = ""
        file.seek(0)  # reset file read to start
        df = pd.read_excel(file)
        df = df.fillna("")  # fill empty cells with string
        df = df.astype(str)  # ensure all data types are string
        text = " ".join(df.agg(" ".join, axis=1))  # combine in one string
        if not text:
            raise DocumentExtractionError(
                "No text could be extracted from the excel file"
            )
        return text
    except Exception as e:
        raise DocumentExtractionError(f"Document Processing Error:{e}") from e

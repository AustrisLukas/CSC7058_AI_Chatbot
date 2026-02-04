from app.helpers.data_utils import extract_docx
from app.helpers.exceptions import DocumentExtractionError
import pytest


# TEST CASE TO VERIFY PDF EXTRACTION RETURNS
def test_extract_docx_returns_text():
    with open("tests/fixtures/sample_doc.docx", "rb") as file:
        text = extract_docx(file)

        assert text != ""


# TEST CASE TO VERIFY PDF CONTAINS EXPECTED WORDS
def test_extract_docx_contains_expected_word():
    with open("tests/fixtures/sample_doc.docx", "rb") as file:
        text = extract_docx(file)

        assert "sample" in text.lower()
        assert "text" in text.lower()


# TEST CASE TO VERIFY EXCEPTION IS THROWN WHEN NOTHING IS EXTRACTED
def test_extract_docx_empty():
    with pytest.raises(DocumentExtractionError):
        with open("tests/fixtures/empty_doc.docx", "rb") as file:
            extract_docx(file)

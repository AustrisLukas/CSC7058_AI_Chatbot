from app.helpers.data_utils import extract_pdf
from app.helpers.exceptions import DocumentExtractionError
import pytest


# TEST CASE TO VERIFY PDF EXTRACTION RETURNS
def test_extract_pdf_returns_text():
    with open("tests/fixtures/sample_pdf.pdf", "rb") as file:
        text = extract_pdf(file)

        assert text != ""


# TEST CASE TO VERIFY PDF CONTAINS EXPECTED WORDS
def test_extract_pdf_contains_expected_word():
    with open("tests/fixtures/sample_pdf.pdf", "rb") as file:
        text = extract_pdf(file)
        print(text)

        assert "sample" in text.lower()
        assert "text" in text.lower()


# TEST CASE TO VERIFY AN EXCEPTION IS THROWN WHEN NOTHING IS EXTRACTED
def test_extract_pdf_empty():
    with pytest.raises(DocumentExtractionError):
        with open("tests/fixtures/empty_pdf.pdf", "rb") as file:
            extract_pdf(file)

from app.helpers.data_utils import extract_pptx
from app.helpers.exceptions import DocumentExtractionError
import pytest


# TEST CASE TO VERIFY PDF EXTRACTION RETURNS
def test_extract_pptx_returns_text():
    with open("tests/fixtures/sample_pptx.pptx", "rb") as file:
        text = extract_pptx(file)

        assert text != ""


# TEST CASE TO VERIFY PDF CONTAINS EXPECTED WORDS
def test_extract_pptx_contains_expected_word():
    with open("tests/fixtures/sample_pptx.pptx", "rb") as file:
        text = extract_pptx(file)
        print(text)

        assert "header1" in text.lower()
        assert "content1" in text.lower()
        assert "header2" in text.lower()
        assert "content2" in text.lower()


# TEST CASE TO VERIFY AN EXCEPTION IS THROWN WHEN NOTHING IS EXTRACTED
def test_extract_pptx_empty():
    with pytest.raises(DocumentExtractionError):
        with open("tests/fixtures/empty_pptx.pptx", "rb") as file:
            extract_pptx(file)

from app.helpers.data_utils import extract_excel
from app.helpers.exceptions import DocumentExtractionError
import pytest


# TEST CASE TO VERIFY PDF EXTRACTION RETURNS
def test_extract_excel_returns_text():
    with open("tests/fixtures/sample_xlsx.xlsx", "rb") as file:
        text = extract_excel(file)

        assert text != ""


# TEST CASE TO VERIFY PDF CONTAINS EXPECTED WORDS
def test_extract_excel_contains_expected_word():
    with open("tests/fixtures/sample_xlsx.xlsx", "rb") as file:
        text = extract_excel(file)
        print(text)

        assert "data" in text.lower()
        assert "16" in text.lower()
        assert "data2" in text.lower()


def test_extract_excel_empty():
    # Use a sample empty or invalid PDF in your fixtures
    with pytest.raises(DocumentExtractionError):
        with open("tests/fixtures/empty_xlsx.xlsx", "rb") as file:
            extract_excel(file)

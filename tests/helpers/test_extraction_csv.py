from app.helpers.data_utils import extract_csv
from app.helpers.exceptions import DocumentExtractionError
import pytest


# TEST CASE TO VERIFY PDF EXTRACTION RETURNS
def test_extract_csv_returns_text():
    with open("tests/fixtures/sample_csv.csv", "rb") as file:
        text = extract_csv(file)

        assert text != ""


# TEST CASE TO VERIFY PDF CONTAINS EXPECTED WORDS
def test_extract_csv_contains_expected_word():
    with open("tests/fixtures/sample_csv.csv", "rb") as file:
        text = extract_csv(file)
        print(text)

        assert "data1" in text.lower()
        assert "10" in text.lower()
        assert "data2" in text.lower()


# TEST CASE TO VERIFY AN EXCEPTION IS THROWN WHEN NOTHING IS EXTRACTED
def test_extract_csv_empty():
    with pytest.raises(DocumentExtractionError):
        with open("tests/fixtures/empty_csv.csv", "rb") as file:
            extract_csv(file)

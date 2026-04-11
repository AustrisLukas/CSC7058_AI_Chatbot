import pytest
from backend.ingestion.chunking import chunk_text
from helpers.exceptions import DocumentChunkingError


# TEST CASE TO VERITY RETURN TYPE IS CORRECT AND RETURN ARRAY LEN IS > 0 FOR A VALID INPUT
def test_chunk_text_returns_string():
    with open("tests/fixtures/sample_text.txt") as file:
        text = file.read()
        chunks = chunk_text(text)

        assert isinstance(chunks, list)
        assert len(chunks) > 0


# TEST CASE TO VERIFY ALL RETURN OUTPUT ARE STRINGS
def test_chunk_text_returns_strings():
    with open("tests/fixtures/sample_text.txt") as file:
        text = file.read()
        chunks = chunk_text(text)

    assert all(isinstance(chunk, str) for chunk in chunks)


def test_chunk_text_returns_single_chunk_for_empty_text():
    with open("tests/fixtures/empty_text.txt") as file:
        text = file.read().strip()
        chunks = chunk_text(text)

    assert chunks == [""]


def test_chunk_text_bypasses_for_small_input():
    text = "short text exanple"

    result = chunk_text(text)

    assert result == [text]

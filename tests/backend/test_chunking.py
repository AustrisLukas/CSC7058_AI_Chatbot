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


# TEST CASE TO VERIFY EXCEPTION IS THROWN WHEN NO CHUNKS ARE GENERATED
def test_chunk_text_throws_exc():

    with pytest.raises(DocumentChunkingError):
        with open("tests/fixtures/empty_text.txt") as file:
            text = file.read().strip()
            chunks = chunk_text(text)

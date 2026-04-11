import pytest


from helpers.document_service import extract_text, build_doc_pipeline
from helpers.exceptions import DocumentExtractionError


class DummyFile:
    def __init__(self, name="sample.pdf", file_type="application/pdf"):
        self.name = name
        self.type = file_type


def test_extract_text_raises_when_both_file_and_url_are_provided():
    dummy_file = DummyFile()

    with pytest.raises(ValueError, match="Provide either file or url, not both"):
        extract_text(file=dummy_file, url="https://urlurlurl.com")


def test_extract_text_raises_when_neither_file_nor_url_is_provided():
    with pytest.raises(ValueError, match="At least one parameter"):
        extract_text()


def test_extract_text_raises_when_extracted_text_is_too_short(monkeypatch):
    dummy_file = DummyFile(name="sample.pdf", file_type="application/pdf")

    monkeypatch.setattr(
        "helpers.document_service.data_utils.detect_file_type", lambda file: "pdf"
    )
    monkeypatch.setattr(
        "helpers.document_service.data_utils.extract_pdf", lambda file: "too short"
    )

    with pytest.raises(
        DocumentExtractionError, match="Document contains insufficient text"
    ):
        extract_text(file=dummy_file)


def test_build_doc_pipeline_happy_path(monkeypatch):
    dummy_file = DummyFile(name="sample.pdf", file_type="application/pdf")

    # Hijacks each step of the pipeline to returns desired outcome for the happy path
    monkeypatch.setattr(
        "helpers.document_service.extract_text",
        lambda file=None, url=None: "This is a valid extracted document text with enough length.",
    )
    monkeypatch.setattr(
        "helpers.document_service.chunk_text", lambda text: ["chunk 1", "chunk 2"]
    )
    monkeypatch.setattr(
        "helpers.document_service.embed_chunks", lambda chunks: [[0.1, 0.2], [0.3, 0.4]]
    )

    monkeypatch.setattr(
        "helpers.document_service.generate_suggested_questions",
        lambda context: '{"questions": ["Q1", "Q2"]}',
    )

    # Fake FAISS store
    class FakeStore:
        def __init__(self, dimension):
            self.dimension = dimension
            self.texts = []

        def add(self, embeddings, texts):
            self.texts = texts

        def get_document_text(self):
            return self.texts

    monkeypatch.setattr("helpers.document_service.FAISSStore", FakeStore)

    extracted_text, chunked_text, chunk_embeddings, store, suggested_questions = (
        build_doc_pipeline(file=dummy_file)
    )

    assert (
        extracted_text == "This is a valid extracted document text with enough length."
    )
    assert chunked_text == ["chunk 1", "chunk 2"]
    assert chunk_embeddings == [[0.1, 0.2], [0.3, 0.4]]
    assert store.dimension == 2
    assert store.get_document_text() == ["chunk 1", "chunk 2"]
    assert "questions" in suggested_questions

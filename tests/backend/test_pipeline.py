import pytest

from backend.exceptions import RetrievalError
from backend.pipeline.pipeline import (
    retrieve_relevant_chunks,
    run_rag_pipeline,
    build_prompt,
)


class FakeStore:
    def __init__(self, chunks=None, score=50):
        self.chunks = chunks or ["chunk one", "chunk two"]
        self.score = score

    def search(self, query_embedding, k=5):
        return self.chunks

    def get_last_retrieval_score(self):
        return self.score

    def get_document_text(self):
        return self.chunks


# PASSING IN EMPTY QUERY WILL TRIGGER AN ERROR IN RAG PIPELINE
def test_retrieve_relevant_chunks_raises_on_empty_query():
    store = FakeStore()

    with pytest.raises(RetrievalError, match="Query cannot be empty."):
        retrieve_relevant_chunks("", store)


# PASSING IN STORE=None WILL TRIGGER AN ERROR IN RAG PIPELINE
def test_retrieve_relevant_chunks_raises_when_store_is_none():
    with pytest.raises(RetrievalError, match="Vector store is not initialised."):
        retrieve_relevant_chunks("What is this about?", None)


# SUMMARY REQUEST RETURNS A SUMMARY. MONKEY PATCH USED TO RETURN TRUE ON is_summary_request() and hijack generate_summary() to avoid calling OpenAI
def test_run_rag_pipeline_returns_summary_when_query_is_summary(monkeypatch):
    expected = {"answer": "summary text", "self_score": 100, "references": []}

    monkeypatch.setattr(
        "backend.pipeline.pipeline.is_summary_request",
        lambda query: True,
    )
    monkeypatch.setattr(
        "backend.pipeline.pipeline.generate_summary",
        lambda relevant_chunks: expected,
    )

    store = FakeStore(chunks=["doc chunk 1", "doc chunk 2"])

    response, score = run_rag_pipeline(
        query="Give me a summary",
        messages=[],
        store=store,
    )

    assert response == expected
    assert score == 100


def test_run_rag_pipeline_returns_guardrail_on_low_retrieval_score(monkeypatch):
    monkeypatch.setattr(
        "backend.pipeline.pipeline.is_summary_request",
        lambda query: False,
    )
    monkeypatch.setattr(
        "backend.pipeline.pipeline.embed_query",
        lambda query: [0.1, 0.2, 0.3],
    )
    called = {"openai_called": False}

    def fake_openai_response(prompt, messages):
        called["openai_called"] = True
        return '{"answer": "should not be called", "self_score": 50, "references": []}'

    # Hijacks get_open_ai_response
    monkeypatch.setattr(
        "backend.pipeline.pipeline.openai_service.get_openai_response",
        fake_openai_response,
    )

    store = FakeStore(score=10)

    response, score = run_rag_pipeline(
        query="test questionb....test",
        messages=[],
        store=store,
    )

    assert score == 0
    assert response["self_score"] == 0
    assert "does not contain information" in response["answer"]
    assert called["openai_called"] is False


def test_run_rag_pipeline_returns_response_on_valid_retrieval(monkeypatch):
    monkeypatch.setattr(
        "backend.pipeline.pipeline.is_summary_request",
        lambda query: False,
    )
    monkeypatch.setattr(
        "backend.pipeline.pipeline.embed_query",
        lambda query: [0.1, 0.2, 0.3],
    )

    monkeypatch.setattr(
        "backend.pipeline.pipeline.openai_service.get_openai_response",
        lambda prompt, messages: (
            '{"answer": "Grounded answer", "self_score": 88, ' '"references": ["refs"]}'
        ),
    )

    store = FakeStore(score=60)

    response, score = run_rag_pipeline(
        query="What does the document say?",
        messages=[],
        store=store,
        ai_creativity="balanced",
        ai_response_style="balanced",
    )

    assert score == 60
    assert response["answer"] == "Grounded answer"
    assert response["self_score"] == 88
    assert response["references"] == ["refs"]


def test_build_prompt_contains_chunks_question_and_controls():
    chunks = ["first chunk", "second chunk"]

    prompt = build_prompt(
        relevant_chunks=chunks,
        query="What is the key message?",
        ai_creativity="strict",
        ai_response_style="concise",
    )

    assert "Chunk 1" in prompt
    assert "first chunk" in prompt
    assert "Chunk 2" in prompt
    assert "second chunk" in prompt
    assert "What is the key message?" in prompt
    assert "Use ONLY the provided context to answer the question." in prompt
    assert "Provide a short, direct answer" in prompt
    assert '"answer": "<full answer>"' in prompt

import pytest

from backend.vector_store.faiss_store import FAISSStore


# TEST DESIGNED TO CHECK IF ADD FUNCTION CORRECTLY ADDS EMBEDDINGS AND TEXTS INTO THE STORE
def test_add_stores_embeddings_and_texts():
    store = FAISSStore(dimension=3)

    embeddings = [
        [0.0, 0.0, 0.0],
        [1.0, 1.0, 1.0],
    ]
    texts = ["chunk one", "chunk two"]

    store.add(embeddings, texts)

    assert store.index.ntotal == 2
    assert store.texts == texts


# TEST CASE FOR EMBEDDINGS AND TEXTS LEN MISSMATCH
def test_add_raises_when_embeddings_and_texts_len_mismatch():
    store = FAISSStore(dimension=3)

    embeddings = [
        [0.0, 0.0, 0.0],
        [1.0, 1.0, 1.0],
    ]

    texts = ["just one chunk"]

    with pytest.raises(ValueError, match="Embeddings and texts must be have length"):
        store.add(embeddings, texts)


# VECTOR STORE DIMENSION 3 , EMEBEDDING/TEXTS 2 (on add)
def test_add_raises_on_embedding_dimension_mismmatch():
    store = FAISSStore(dimension=3)

    embeddings = [
        [0.0, 0.0],
        [1.0, 1.0],
    ]
    texts = ["chunk one", "chunk two"]

    with pytest.raises(ValueError, match="Embedding dimension mismatch"):
        store.add(embeddings, texts)


# VECTOR STORE DIMENSION 3 , EMEBEDDING/TEXTS 2 (on search)
def test_search_raises_when_index_is_empty():
    store = FAISSStore(dimension=3)

    with pytest.raises(ValueError, match="FAISS index is empty"):
        store.search([0.1, 0.1, 0.1], k=2)


def test_search_returns_expected_top_k_chunks_in_order():
    store = FAISSStore(dimension=3)

    embeddings = [
        [0.0, 0.0, 0.0],
        [1.0, 1.0, 1.0],
        [5.0, 5.0, 5.0],
    ]
    texts = ["closest chunk", "second chunk", "far chunk"]
    store.add(embeddings, texts)

    results = store.search([0.1, 0.1, 0.1], k=2)

    assert len(results) == 2
    assert results[0] == "closest chunk"
    assert results[1] == "second chunk"


def test_search_updates_retrieval_score():
    store = FAISSStore(dimension=3)

    embeddings = [
        [0.0, 0.0, 0.0],
        [1.0, 1.0, 1.0],
        [5.0, 5.0, 5.0],
    ]
    texts = ["closest chunk", "second chunk", "far chunk"]
    store.add(embeddings, texts)

    assert store.get_last_retrieval_score() == -1

    store.search([0.1, 0.1, 0.1], k=2)

    score = store.get_last_retrieval_score()

    assert score >= 0
    assert score <= 100


def test_get_document_text_returns_all_stored_texts():
    store = FAISSStore(dimension=3)

    embeddings = [
        [0.0, 0.0, 0.0],
        [1.0, 1.0, 1.0],
    ]
    texts = ["chunk one", "chunk two"]
    store.add(embeddings, texts)

    assert store.get_document_text() == texts


def test_get_document_text_returns_all_stored_texts():

    store = FAISSStore(dimension=3)

    embeddings = [
        [0.0, 0.0, 0.0],
        [1.0, 1.0, 1.0],
    ]
    texts = ["chunk one", "chunk two"]

    store.add(embeddings, texts)

    assert store.get_document_text() == texts

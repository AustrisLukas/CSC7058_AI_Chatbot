from unittest.mock import patch
from backend.embeddings.embedder import embed_chunks


@patch("backend.embeddings.embedder.openai_service.embed_chunks")
def test_embed_chunks_returns_vectors(mock_embed_chunks):
    mock_embed_chunks.return_value = [[0.1, 0.2, 0.3]]

    result = embed_chunks(["test"])

    assert isinstance(result, list)
    assert isinstance(result[0], list)
    assert result == [[0.1, 0.2, 0.3]]
    mock_embed_chunks.assert_called_once_with(chunks=["test"])

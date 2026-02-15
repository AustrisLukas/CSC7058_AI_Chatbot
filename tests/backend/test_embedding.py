import os
from unittest.mock import patch

os.environ.setdefault("OPENAI_API_KEY", "sk-test")

from backend.embeddings.embedder import embed_chunks


@patch("backend.embeddings.embedder.client.embeddings.create")
def test_embed_chunks_returns_vectors(mock_create):
    mock_create.return_value.data = [type("obj", (), {"embedding": [0.1, 0.2, 0.3]})]

    result = embed_chunks(["test"])

    assert isinstance(result, list)
    assert isinstance(result[0], list)

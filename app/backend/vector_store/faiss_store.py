import faiss
import numpy as np
from typing import List


# FAIS Vector store.
# - Holding Embeddings
# - Performing Similarity Search
class FAISSStore:

    def __init__(self, dimension: int):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.texts: List[str] = []

    # Add  Embeddings and their corresponding text chunks
    def add(self, embeddings: List[List[float]], texts: List[str]) -> None:
        if len(embeddings) != len(texts):
            raise ValueError("Embeddings and texts must be have lenght")

        np_embeddings = np.array(embeddings).astype("float32")

        if np_embeddings.shape[1] != self.dimension:
            raise ValueError(
                f"Embedding dimension mismatch ."
                f"Expected: {self.dimension}, Received: {np_embeddings.shape[1]}"
            )
        self.index.add(np_embeddings)
        self.texts.extend(texts)

    # Search for top-k most similar text chunks
    def search(self, query_embedding: List[float], k: int = 5) -> List[str]:

        results = []
        if self.index.ntotal == 0:
            raise ValueError("FAISS index is empty")

        query_vector = np.array([query_embedding]).astype("float32")

        if query_vector.shape[1] != self.dimension:
            raise ValueError(
                f"Query embedding dimension mismatch. "
                f"Expected {self.dimension}, got {query_vector.shape[1]}"
            )

        distances, indices = self.index.search(query_vector, k)

        # Match indices (k) with texts
        for i in indices[0]:
            results.append(self.texts[i])
            print(self.texts[i])
        return results

import faiss
import numpy as np
from typing import List
import logging


logger = logging.getLogger(__name__)


# FAIS Vector store.
# - Holding Embeddings
# - Performing Similarity Search
class FAISSStore:

    def __init__(self, dimension: int):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.texts: List[str] = []
        self.last_retrieval_score = -1

    # Add  Embeddings and their corresponding text chunks
    def add(self, embeddings: List[List[float]], texts: List[str]) -> None:
        print(len(embeddings))
        print(len(texts))
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

        distancesList = []
        for rank, dist in enumerate(distances[0], start=1):
            # logger.info("Rank %d distance: %.6f", rank, float(dist))
            distancesList.append(round(float(dist), 6))
        logger.info(f"Chunk distances: {distancesList}")

        self.set_last_retrieval_score(distances[0])

        # MATCH INDICES WITH TEXTS (k)
        for i in indices[0]:
            results.append(self.texts[i])
        return results

    def set_last_retrieval_score(self, distances: list[float]) -> float:

        d1 = distances[0]
        d2 = distances[1] if len(distances) > 1 else d1

        # CALIBRATION VALUES
        d_good = 1.2  # very relevant
        d_bad = 1.7  # weak

        closeness = (d_bad - d1) / (d_bad - d_good)
        closeness = max(0.0, min(1.0, closeness))

        gap = max(0.0, d2 - d1)
        separation = gap / (d2 + 1e-8)
        separation = max(0.0, min(1.0, separation))

        score = 100 * (0.85 * closeness + 0.15 * separation)

        self.last_retrieval_score = round(score, 1)
        logger.info(f"Retrieval socre: {round(self.last_retrieval_score)}")

    def get_last_retrieval_score(self) -> float:
        return self.last_retrieval_score

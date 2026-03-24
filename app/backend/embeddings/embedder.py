from services import openai_service


def embed_chunks(chunks: list[str]) -> list[list[float]]:
    return openai_service.embed_chunks(chunks=chunks)


def embed_query(query: str) -> list[float]:
    return openai_service.embed_query(query=query)

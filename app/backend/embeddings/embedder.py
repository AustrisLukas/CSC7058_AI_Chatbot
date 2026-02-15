from openai import OpenAI

client = OpenAI()
embedding_model = "text-embedding-3-small"


def embed_chunks(chunks: list[str]) -> list[list[float]]:
    response = client.embeddings.create(model=embedding_model, input=chunks)

    return [item.embedding for item in response.data]

from backend.embeddings.embedder import embed_query
from services import openai_service
import logging
from backend.exceptions import RetrievalError


logger = logging.getLogger(__name__)

RAG_MODES = {
    "strict": "Answer only from context. If missing, say: I don't know based on the document.",
    "balanced": "Prefer context. If incomplete, say what is missing.",
    "creative": "Use context as anchor, but you may paraphrase and propose ideas clearly marked as suggestions.",
}
RESPONSE_STYLE = {
    "concise": "Give short, direct answers focused on key facts and final conclusions. Use minimal wording and avoid extra explanation unless explicitly asked.",
    "balanced": "Give clear explanations with moderate detail. Include essential reasoning, but avoid unnecessary verbosity. Prefer readability and practical clarity over exhaustive depth.",
    "detailed": "Provide in-depth explanations with relevant context, assumptions, and edge cases. Show reasoning and tradeoffs clearly. Use structured formatting when helpful.",
}


def run_rag_pipeline(query: str, messages: list[str], store, k: int = 5) -> str:

    logging.info(f"Begin rag_pipeline for query -> {query}")

    relevant_chunks = retrieve_relevant_chunks(query, store, k)
    prompt = build_prompt(relevant_chunks, query)

    answer = openai_service.get_openai_response(prompt, messages)

    return answer


def retrieve_relevant_chunks(query: str, store, k: int = 5) -> list[str]:
    if not query:
        raise RetrievalError("Query cannot be empty.")
    if store is None:
        raise RetrievalError("Vector store is not initialised.")

    query_embedding = embed_query(query.strip())
    return store.search(query_embedding, k=k)


def build_prompt(relevant_chunks: list[str], query):

    prompt_parts = []
    for i, chunk in enumerate(relevant_chunks):
        prompt_parts.append(f"Chunk {i+1}\n{chunk}")

    context = "\n\n".join(prompt_parts)

    rag_query = f"""
    You are answering based only on the provided context.
    If the answer is not in the context, say you don't know.

    Context:{context}

    Question:{query}
    """.strip()

    return rag_query

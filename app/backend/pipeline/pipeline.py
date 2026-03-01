from backend.embeddings.embedder import embed_query
from services import openai_service
import logging
from backend.exceptions import RetrievalError
import json


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

    relevant_chunks, retrieval_score = retrieve_relevant_chunks(query, store, k)
    prompt = build_prompt(relevant_chunks, query)
    ai_response = openai_service.get_openai_response(prompt, messages)

    self_evaluation_query = build_self_evaluate_prompt(relevant_chunks, ai_response)
    self_evaluation = openai_service.get_openai_response(
        self_evaluation_query, messages
    )
    if self_evaluation != None:
        self_evaluation = json.loads(self_evaluation)
    print(self_evaluation["self_score"])
    print(self_evaluation["reason"])
    print(self_evaluation["references"])

    return ai_response, retrieval_score, self_evaluation["self_score"]


def retrieve_relevant_chunks(query: str, store, k: int = 5) -> tuple[list[str], float]:
    if not query:
        raise RetrievalError("Query cannot be empty.")
    if store is None:
        raise RetrievalError("Vector store is not initialised.")

    query_embedding = embed_query(query.strip())

    return store.search(query_embedding, k=k), store.get_last_retrieval_score()


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


def build_self_evaluate_prompt(relevant_chunks: list[str], response):

    prompt_parts = []
    for i, chunk in enumerate(relevant_chunks):
        prompt_parts.append(f"Chunk {i+1}\n{chunk}")

    context = "\n\n".join(prompt_parts)

    rag_query = f"""
    You are an evaluator. Score an answer only by support from the provided context.

    Task:
    Given QUESTION, ANSWER, and CONTEXT, evaluate how well the answer is grounded in the context.

    Scoring rubric (0-100):
    - 90-100: Fully supported, precise, no unsupported claims.
    - 70-89: Mostly supported, minor omissions or slight imprecision.
    - 40-69: Partially supported, important gaps or unclear claims.
    - 0-39: Not supported, contradicted, or mostly fabricated.

    Rules:
    - Do not use external knowledge.
    - If context lacks evidence for key claims, lower score.
    - If answer correctly says information is missing, score based on that correctness.
    - Return JSON only. No markdown, no extra text.
    If the answer is not in the context, say you don't know.

    Return schema:
    {{
    "self_score": <integer 0-100>,
    "reason": "<one very short sentence>"
    "references": [
        "<short supporting quote or chunk snippet 1>",
        "<short supporting quote or chunk snipped 2>",
        ]
    }}

    Context:{context}

    AI Response:{response}
    """.strip()

    return rag_query

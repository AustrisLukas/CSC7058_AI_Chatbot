from backend.embeddings.embedder import embed_query
from services import openai_service
import logging
from backend.exceptions import RetrievalError
import json
from helpers.data_utils import parse_model_json
from helpers.data_utils import load_json


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

RETRIEVAL_TOLEANCE = 15


def run_rag_pipeline(query: str, messages: list[str], store, k: int = 5) -> str:

    logging.info(f"Begin rag_pipeline for query -> {query}")

    relevant_chunks, retrieval_score = retrieve_relevant_chunks(query, store, k)
    if retrieval_score < RETRIEVAL_TOLEANCE:
        return guardrail_faillback()

    prompt = build_prompt(relevant_chunks, query)
    ai_response = openai_service.get_openai_response(prompt, messages)

    logger.info(f"Query response: {ai_response}")
    # logger.info(f"Self evaluation: {self_evaluation}")

    ai_response = load_json(ai_response)
    return ai_response, retrieval_score


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
    You are a retrieval-based assistant.

    You MUST answer using ONLY the provided context.
    Do NOT use prior knowledge.
    Do NOT infer beyond what is explicitly stated.

    If the answer cannot be found explicitly in the context:
    - State clearly that the information is not available in the provided context.
    - Set self_score to 0.
    - Return an EMPTY references array.

    If the answer IS supported by the context:
    - Provide a concise answer.
    - Extract 1 to 3 short verbatim supporting snippets from the context.
    - References MUST be exact substrings copied from the context.
    - Do NOT paraphrase references and include all relevant references.

    Context:{context}

    Question:{query}
    
    Return ONLY valid JSON in this exact schema:

    {{
    "answer": "<concise answer>",
    "self_score": <integer 0-100>,
    "reason": "<one very short sentence explaining score>",
    "references": [
        "<exact supporting quote 1>",
        "<exact supporting quote 2>",
        "...",
        "<exact supporting quote N>",
    ]
    }}
    """.strip()

    return rag_query


def build_self_evaluate_prompt(relevant_chunks: list[str], response):

    prompt_parts = []
    for i, chunk in enumerate(relevant_chunks):
        prompt_parts.append(f"Chunk {i+1}\n{chunk}")

    context = "\n\n".join(prompt_parts)

    rag_query_with_ref = f"""
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
    - If answer correctly says information in context is missing, score high based on that correctness.
    - Return JSON only. No markdown, no extra text.


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

    return rag_query_with_ref


def guardrail_faillback():

    logger.warning(
        "Low context guardrail triggered. No API call made and shortcircuit answer returned."
    )

    # Return default answer, and 0 for retrieval score
    return {
        "answer": "The provided text does not contain infroamtion about the question",
        "self_score": 0,
        "reason": " ",
        "references": [],
    }, 0

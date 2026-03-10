from backend.embeddings.embedder import embed_query
from services import openai_service
import logging
from backend.exceptions import RetrievalError
import json
from helpers.data_utils import parse_model_json
from helpers.data_utils import load_json


logger = logging.getLogger(__name__)

RETRIEVAL_TOLEANCE = 15

RAG_MODES = {
    "strict": (
        "Use ONLY the provided context to answer the question. "
        "Do not add external knowledge, assumptions, or interpretations. "
        "If the answer is not explicitly stated in the context, respond: "
        "'I don't know based on the provided document.'"
    ),
    "balanced": (
        "Prioritise information from the provided context. "
        "You may combine multiple pieces of context to form a complete answer. "
        "If the context is incomplete, answer using what is available and clearly state what information is missing."
    ),
    "creative": (
        "Use the provided context as the primary source. "
        "You may paraphrase, expand explanations, or suggest ideas that logically follow from the context. "
        "Any interpretation, suggestion, or extrapolation must be clearly labelled as such."
    ),
}
RESPONSE_STYLE = {
    "concise": (
        "Provide a short, direct answer focused on the key facts or conclusion. "
        "Use minimal wording and avoid unnecessary explanation. "
        "Only include additional detail if it is required to correctly answer the question."
    ),
    "balanced": (
        "Provide a clear explanation with moderate detail. "
        "Summarise the most relevant information and reasoning from the context. "
        "Prioritise clarity and readability while avoiding unnecessary verbosity."
    ),
    "detailed": (
        "Provide a thorough explanation using all relevant information from the context. "
        "Include important details, relationships, assumptions, or edge cases when helpful. "
        "Use structured formatting such as bullet points or short sections when it improves clarity."
    ),
}


def run_rag_pipeline(
    query: str,
    messages: list[str],
    store,
    k: int = 5,
    ai_creativity="balanced",
    ai_response_style="balanced",
) -> str:

    logging.info(
        f"Begin rag_pipeline for query -> {query} {ai_creativity}, {ai_response_style}"
    )
    # CHECK IF SUMMARY REQUEST AND HANDLE AS A SUMMARY REQUEST
    if is_summary_request(query):
        return generate_summary(relevant_chunks=store.get_document_text()), 100

    relevant_chunks, retrieval_score = retrieve_relevant_chunks(query, store, k)
    prompt = build_prompt(relevant_chunks, query, ai_creativity, ai_response_style)

    # BREAK EARLY IF RETRIEVAL SCORE IS LOW AND PROVIDE DEFUALT 'LOW CONTEXT' ANSWER
    if retrieval_score < RETRIEVAL_TOLEANCE:
        return guardrail_faillback()

    ai_response = openai_service.get_openai_response(prompt, messages)
    logger.info(f"Query response: {ai_response}")
    # UNPACK JSON AND SANITISE OUTPUT
    ai_response = load_json(ai_response)

    return ai_response, retrieval_score


# Function that outputa s summary large texts
# Summarises individual chunks into several bullepoints and combines them to a list.
# Finall summary call is made with a list of chunk summaries
# self_score fixed at 100
def generate_summary(relevant_chunks):
    combined_summaries = []

    for chunk in relevant_chunks:
        prompt = f"""
            You are summarising a section of a large document
            Write 4-5 bullet points capturing the key ideas
            Text{chunk}
            """
        ai_response = openai_service.get_openai_response(prompt=prompt, chat_history="")
        combined_summaries.append(ai_response)

    final_prompt = f"""
    You are summarising a document.
    Below are summaries of individual sections.
    Combine them into a coherent structured summary.
    Sections to include:
    - Overview
    - Key Topics
    - Important Details
    - Conclusions
    Section summaries:
    {combined_summaries}
    """
    ai_response = openai_service.get_openai_response(
        prompt=final_prompt, chat_history=""
    )
    return {"answer": ai_response, "self_score": 100, "references": []}


def retrieve_relevant_chunks(
    user_question: str,
    store,
    k: int = 5,
) -> tuple[list[str], float]:
    if not user_question:
        raise RetrievalError("Query cannot be empty.")
    if store is None:
        raise RetrievalError("Vector store is not initialised.")

    query_embedding = embed_query(user_question.strip())
    return store.search(query_embedding, k=k), store.get_last_retrieval_score()


def build_prompt(relevant_chunks: list[str], query, ai_creativity, ai_response_style):

    prompt_parts = []
    for i, chunk in enumerate(relevant_chunks):
        prompt_parts.append(f"Chunk {i+1}\n{chunk}")

    context = "\n\n".join(prompt_parts)
    rag_query = f"""
    You are a retrieval-based assistant.

    Knowledge policy:
    {RAG_MODES[ai_creativity]}

    If the answer cannot be found explicitly in the context:
    - State clearly that the information is not available in the provided context.
    - Set self_score to 0.
    - Return an EMPTY references array.

    Response style:
    {RESPONSE_STYLE[ai_response_style]}

    Context:{context}

    Question:{query}

    Return ONLY valid JSON in this exact schema:
    {{
    "answer": "<full answer>",
    "self_score": <integer 0-100>,
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
        "answer": "The provided text does not contain information about the question",
        "self_score": 0,
        "reason": " ",
        "references": [],
    }, 0


# FUNCTION TO TEST IF USER QUERY IS REQUESTING A SUMMARY
def is_summary_request(user_question):
    summary_keywords = [
        "summary",
        "summarise",
        "summarize",
        "overview",
        "brief",
        "outline",
        "key points",
        "main points",
        "highlights",
        "takeaways",
        "main idea",
        "what is this about",
    ]

    for keyword in summary_keywords:
        if keyword in user_question:
            logger.info(
                f"Keyword '{keyword}' found, user question is handled as a summary request "
            )
            return True
    return False

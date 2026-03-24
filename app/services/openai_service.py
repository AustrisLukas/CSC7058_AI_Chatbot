import streamlit as st
from openai import OpenAI
import json
import logging

logger = logging.getLogger(__name__)


class OpenAIServiceError(Exception):
    pass


EMBEDDING_MODEL = "text-embedding-3-small"

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


def get_openai_response(prompt, chat_history):
    messages = list(chat_history)
    messages.append({"role": "system", "content": prompt})
    # print(f"OUTGOING OPEN AI PROMPT LEN -> {len(messages)}")
    # print(f"OUTGOING OPEN AI PROMPT CONTENT -> {messages}")
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", messages=messages
        )
        if not response.choices:
            raise OpenAIServiceError("Something went wrong.. AI response is empty.")
        logger.info(f"Prompt tokens: {response.usage.prompt_tokens}")
        logger.info(f"Completion tokens: {response.usage.completion_tokens}")
        logger.info(f"Total tokens: {response.usage.total_tokens}")

        return response.choices[0].message.content
    except Exception as e:
        raise OpenAIServiceError(
            f"Something went wrong.. Please try again or reload the page.  \nError: {e}"
        ) from e


def test_openai_key():
    try:
        models = client.models.list()
        return True
    except Exception as e:
        print(f"Open AI API key test failed: {e}")
        return False


def embed_chunks(chunks: list[str]) -> list[list[float]]:
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=chunks)
    return [item.embedding for item in response.data]


def embed_query(query: str) -> list[float]:
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=[query])
    return response.data[0].embedding

import streamlit as st
from openai import OpenAI
import json


class OpenAIServiceError(Exception):
    pass


client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


def get_openai_response(prompt, chat_history):
    messages = list(chat_history)
    messages.append({"role": "system", "content": prompt})
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", messages=messages
        )
        if not response.choices:
            raise OpenAIServiceError("Something went wrong.. AI response is empty.")
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

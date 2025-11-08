import streamlit as st
from openai import OpenAI
import json

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


def get_openai_response(prompt, chat_history):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=chat_history
    )
    return response.choices[0].message.content


def test_openai_key():
    try:
        models = client.models.list()
        return True
    except Exception as e:
        print(f"Open AI API key test failed: {e}")
        return False
